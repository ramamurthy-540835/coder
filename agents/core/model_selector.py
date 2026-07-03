#!/usr/bin/env python3
"""Model selection helpers for PRISM coding agents."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.runners.vertex_maas_runner import extract_text, vertex_generate_content


AVAILABLE_ROUTES = {
    "glm5": "General implementation, broad generation, and cost-conscious drafting.",
    "grok43": "Strong coding, architecture, and review work with balanced reasoning.",
    "grok420_reasoning": "Hard debugging, multi-step design, security review, and tradeoff analysis.",
    "grok420_non_reasoning": "Fast code generation, refactors, and simpler implementation tasks.",
    "codex": "Local CLI-assisted code editing placeholder; not selected automatically yet.",
}


@dataclass(frozen=True)
class ModelSelection:
    """A model-route decision and its explanation."""

    route: str
    reason: str
    confidence: float
    mode: str
    raw_response: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "reason": self.reason,
            "confidence": self.confidence,
            "mode": self.mode,
            "raw_response": self.raw_response,
        }


def summarize_task_text(task: str, prompt: str, max_chars: int = 12000) -> str:
    """Limit selector input to keep cost bounded."""
    text = f"TASK:\n{task.strip()}\n\nPROMPT/CONTEXT SUMMARY:\n{prompt.strip()}"
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[TRUNCATED FOR MODEL SELECTION]"


def heuristic_select(task: str, prompt: str) -> ModelSelection:
    """Cheap deterministic route selection."""
    text = f"{task}\n{prompt}".lower()
    hard_reasoning = [
        "debug",
        "root cause",
        "security",
        "architecture",
        "tradeoff",
        "complex",
        "multi-step",
        "race condition",
        "production incident",
    ]
    fast_code = [
        "generate code",
        "write code",
        "simple",
        "boilerplate",
        "crud",
        "scaffold",
        "refactor",
    ]
    data_or_general = ["sql", "bigquery", "data", "etl", "pipeline", "report", "summarize"]
    if any(term in text for term in hard_reasoning):
        return ModelSelection("grok420_reasoning", "Task suggests deeper reasoning, architecture, debugging, or security analysis.", 0.78, "heuristic")
    if any(term in text for term in fast_code):
        return ModelSelection("grok420_non_reasoning", "Task looks like straightforward code generation or refactoring.", 0.70, "heuristic")
    if any(term in text for term in data_or_general):
        return ModelSelection("glm5", "Task looks data/report oriented or broad generation where GLM is a reasonable cost-conscious default.", 0.66, "heuristic")
    return ModelSelection("grok43", "Balanced default for mixed coding-agent work.", 0.60, "heuristic")


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract a JSON object from model text."""
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return json.loads(stripped)
    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if not match:
        raise ValueError("Selector response did not contain a JSON object")
    return json.loads(match.group(0))


def gemini_select(
    *,
    task: str,
    prompt: str,
    project_id: str,
    location: str,
    selector_model: str,
    timeout_seconds: int,
) -> ModelSelection:
    """Use a Gemini model on Vertex to choose a route and return JSON."""
    selector_prompt = f"""You are selecting the best model route for a coding-agent task.

Available routes:
{json.dumps(AVAILABLE_ROUTES, indent=2)}

Selection rules:
- Return JSON only.
- Pick exactly one route from the available routes.
- Use grok420_reasoning for hard reasoning, security, architecture, and difficult debugging.
- Use grok420_non_reasoning for faster straightforward coding and simple refactors.
- Use grok43 for balanced coding/review work.
- Use glm5 for broad drafting, data/report tasks, or cost-conscious generation.
- Do not choose codex in auto mode; it is a registered placeholder until local CLI execution is wired.

Input:
{summarize_task_text(task, prompt)}

Return this JSON shape:
{{"route":"grok43","reason":"short reason","confidence":0.0}}
"""
    response_json = vertex_generate_content(
        project_id=project_id,
        location=location,
        publisher="google",
        model=selector_model,
        prompt=selector_prompt,
        temperature=0.0,
        max_output_tokens=1024,
        timeout_seconds=timeout_seconds,
    )
    text = extract_text(response_json)
    parsed = extract_json_object(text)
    route = str(parsed.get("route", "grok43"))
    if route not in AVAILABLE_ROUTES:
        route = "grok43"
    confidence = parsed.get("confidence", 0.5)
    try:
        confidence_float = float(confidence)
    except (TypeError, ValueError):
        confidence_float = 0.5
    return ModelSelection(
        route=route,
        reason=str(parsed.get("reason", "Gemini selector chose a balanced default.")),
        confidence=max(0.0, min(1.0, confidence_float)),
        mode="gemini",
        raw_response=response_json,
    )


def select_model(
    *,
    task: str,
    prompt: str,
    mode: str,
    project_id: str,
    location: str,
    selector_model: str,
    timeout_seconds: int,
) -> ModelSelection:
    """Select a model route using the configured selector mode."""
    if mode == "heuristic":
        return heuristic_select(task, prompt)
    if mode == "gemini":
        try:
            return gemini_select(
                task=task,
                prompt=prompt,
                project_id=project_id,
                location=location,
                selector_model=selector_model,
                timeout_seconds=timeout_seconds,
            )
        except Exception as exc:
            fallback = heuristic_select(task, prompt)
            return ModelSelection(
                fallback.route,
                f"Gemini selector failed ({exc}); fallback used. {fallback.reason}",
                min(fallback.confidence, 0.55),
                "gemini_fallback",
            )
    raise ValueError("selector mode must be heuristic or gemini")


def write_selection(selection: ModelSelection, output_dir: Path) -> Path:
    """Write model selection evidence."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"model_selection_{timestamp}.json"
    path.write_text(json.dumps(selection.to_dict(), indent=2), encoding="utf-8")
    return path
