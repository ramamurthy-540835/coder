#!/usr/bin/env python3
"""Deterministic model selection for PRISM coding agents."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.core.metrics import SelectionMetrics, ScoreItem, score_task
from agents.providers.vertex_maas import extract_text, vertex_generate_content


LOGICAL_ROUTES: dict[str, str] = {
    "fast_code": "Fast code generation, simple CRUD/scaffolding, straightforward refactors.",
    "balanced_code": "General coding, review, and architecture work with balanced capability.",
    "hard_reasoning": "Security, architecture, hard debugging, production risk, and tradeoff analysis.",
    "large_context": "Very large context tasks that need a high context window.",
    "data_report": "Data, SQL, BigQuery, ETL, reporting, summarization, and broad drafting.",
    "local_edit": "Direct local code editing through Codex; not auto-selected until execution is wired.",
}

LOGICAL_ROUTE_MODELS: dict[str, str] = {
    "fast_code": "xai/grok-4.3-fast",
    "balanced_code": "xai/grok-4.3",
    "hard_reasoning": "xai/grok-4.3",
    "large_context": "gemini-3.5-flash",
    "data_report": "gemini-3.5-flash",
    "local_edit": "gpt-5.3-codex",
}

ROUTE_ORDER = ["data_report", "fast_code", "balanced_code", "hard_reasoning"]
LIVE_AUTO_ROUTES = {"fast_code", "balanced_code", "hard_reasoning", "large_context", "data_report"}


@dataclass(frozen=True)
class ModelConfig:
    """A configured physical model from models.json."""

    id: str
    name: str
    provider: str
    max_tokens: int
    input_cost_per_million_tokens: float
    output_cost_per_million_tokens: float
    enabled: bool
    raw: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "max_tokens": self.max_tokens,
            "input_cost_per_million_tokens": self.input_cost_per_million_tokens,
            "output_cost_per_million_tokens": self.output_cost_per_million_tokens,
            "enabled": self.enabled,
        }


def load_model_registry(path: Path | None = None) -> dict[str, ModelConfig]:
    """Load enabled model metadata from models.json."""
    registry_path = path or Path("models.json")
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    models: dict[str, ModelConfig] = {}
    for item in data.get("models", []):
        model = ModelConfig(
            id=str(item["id"]),
            name=str(item.get("name", item["id"])),
            provider=str(item.get("provider", "unknown")),
            max_tokens=int(item.get("max_tokens", 0) or 0),
            input_cost_per_million_tokens=float(item.get("input_cost_per_million_tokens", 0.0) or 0.0),
            output_cost_per_million_tokens=float(item.get("output_cost_per_million_tokens", 0.0) or 0.0),
            enabled=bool(item.get("enabled", True)),
            raw=item,
        )
        if model.enabled:
            models[model.id] = model
    return models




@dataclass(frozen=True)
class ModelSelection:
    """A model-route decision and its explanation."""

    logical_route: str
    physical_model: str
    reason: str
    confidence: float
    mode: str
    metrics: SelectionMetrics
    alternative_considered: str | None = None
    rejected_reason: str | None = None
    feasibility_excluded: list[dict[str, Any]] = field(default_factory=list)
    estimated_cost_usd: dict[str, float] = field(default_factory=dict)
    raw_response: dict[str, Any] | None = None

    @property
    def route(self) -> str:
        """Backward-compatible alias used by the orchestrator."""
        return self.logical_route

    def to_dict(self) -> dict[str, Any]:
        return {
            "logical_route": self.logical_route,
            "physical_model": self.physical_model,
            "route": self.logical_route,
            "reason": self.reason,
            "confidence": self.confidence,
            "mode": self.mode,
            "metrics": self.metrics.to_dict(),
            "alternative_considered": self.alternative_considered,
            "rejected_reason": self.rejected_reason,
            "feasibility_excluded": self.feasibility_excluded,
            "estimated_cost_usd": self.estimated_cost_usd,
            "raw_response": self.raw_response,
        }




def route_for_metrics(metrics: SelectionMetrics) -> tuple[str, str]:
    """Choose a base logical route from score metrics before feasibility/cost bias."""
    if metrics.estimated_tokens > 220000:
        return "large_context", "Estimated tokens exceed the Grok comfort threshold, so large-context routing is preferred."
    if "data_report" in metrics.intent and metrics.risk_score < 6:
        return "data_report", "Data/report task with risk below the hard-reasoning threshold."
    if metrics.risk_score >= 6 or metrics.complexity_score >= 7:
        return "hard_reasoning", "High complexity or high risk requires the reasoning route."
    if metrics.complexity_score <= 3 and metrics.risk_score <= 3:
        return "fast_code", "Low complexity and low risk fit the fast-code route."
    return "balanced_code", "Moderate complexity/risk fits the balanced-code route."


def apply_cost_mode(route: str, metrics: SelectionMetrics) -> tuple[str, str | None]:
    """Apply cost-mode bias after safety and base route selection."""
    if route == "large_context" or metrics.risk_score >= 6:
        return route, "Cost-mode bias ignored because risk floor or context gate has priority."
    if route not in ROUTE_ORDER:
        return route, None
    idx = ROUTE_ORDER.index(route)
    if metrics.cost_mode == "low" and idx > 0:
        return ROUTE_ORDER[idx - 1], "Cost mode low biased the route down one tier."
    if metrics.cost_mode == "best" and idx < len(ROUTE_ORDER) - 1:
        return ROUTE_ORDER[idx + 1], "Cost mode best biased the route up one tier."
    return route, None


def estimate_cost(model: ModelConfig, metrics: SelectionMetrics, output_tokens: int = 2048) -> float:
    """Estimate one call cost using configured token prices."""
    input_cost = metrics.estimated_tokens / 1_000_000 * model.input_cost_per_million_tokens
    output_cost = output_tokens / 1_000_000 * model.output_cost_per_million_tokens
    return round(input_cost + output_cost, 6)


def feasibility_exclusions(registry: dict[str, ModelConfig], metrics: SelectionMetrics) -> list[dict[str, Any]]:
    """Return models excluded because the estimated prompt is too large."""
    excluded = []
    for route, model_id in LOGICAL_ROUTE_MODELS.items():
        model = registry.get(model_id)
        if not model:
            excluded.append({"logical_route": route, "physical_model": model_id, "reason": "model_not_enabled_or_missing"})
        elif model.max_tokens and metrics.estimated_tokens > model.max_tokens:
            excluded.append({
                "logical_route": route,
                "physical_model": model_id,
                "reason": "estimated_tokens_exceed_model_limit",
                "estimated_tokens": metrics.estimated_tokens,
                "max_tokens": model.max_tokens,
            })
    return excluded


def ensure_feasible_route(route: str, registry: dict[str, ModelConfig], metrics: SelectionMetrics) -> tuple[str, str | None]:
    """Move to a feasible route if the selected model cannot fit the prompt."""
    model_id = LOGICAL_ROUTE_MODELS[route]
    model = registry.get(model_id)
    if model and (not model.max_tokens or metrics.estimated_tokens <= model.max_tokens):
        return route, None
    for fallback in ["large_context", "balanced_code", "data_report", "fast_code"]:
        fallback_model = registry.get(LOGICAL_ROUTE_MODELS[fallback])
        if fallback_model and (not fallback_model.max_tokens or metrics.estimated_tokens <= fallback_model.max_tokens):
            return fallback, f"Route {route} was infeasible for estimated token count; fell back to {fallback}."
    return route, "No feasible fallback model found; selected route may fail."


def confidence_for_route(route: str, metrics: SelectionMetrics) -> float:
    """Compute confidence from distance to routing boundaries."""
    if route == "large_context":
        margin = max(0, metrics.estimated_tokens - 220000) / 220000
        return round(min(0.95, 0.72 + margin), 2)
    if route == "hard_reasoning":
        margin = max(metrics.complexity_score - 7, metrics.risk_score - 6, 0)
        return round(min(0.95, 0.72 + margin * 0.06), 2)
    if route == "fast_code":
        margin = max(3 - metrics.complexity_score, 3 - metrics.risk_score, 0)
        return round(min(0.90, 0.64 + margin * 0.06), 2)
    if route == "data_report":
        return 0.70 if "data_report" in metrics.intent else 0.58
    return 0.66


def alternative_for(route: str, metrics: SelectionMetrics) -> tuple[str | None, str | None]:
    """Pick one rejected alternative and explain why."""
    if route == "hard_reasoning":
        return "gemini-3.5-flash", "Lower reasoning fit for high-risk or high-complexity work."
    if route == "large_context":
        return "xai/grok-4.3", "Estimated tokens may exceed or approach the smaller context window."
    if route == "fast_code":
        return "xai/grok-4.3", "Balanced route is more capable but unnecessary for low-risk/simple work."
    if route == "data_report":
        return "xai/grok-4.3", "Data/report task favors larger context and lower cost."
    return "xai/grok-4.3-fast", "Fast route may be cheaper but less robust for moderate complexity."


def heuristic_select(task: str, prompt: str, context_metadata: dict[str, Any] | None, cost_mode: str) -> ModelSelection:
    """Deterministic scorecard route selection."""
    registry = load_model_registry()
    metrics = score_task(task=task, prompt=prompt, context_metadata=context_metadata, cost_mode=cost_mode)
    base_route, base_reason = route_for_metrics(metrics)
    feasible_route, feasibility_reason = ensure_feasible_route(base_route, registry, metrics)
    biased_route, cost_reason = apply_cost_mode(feasible_route, metrics)
    final_route, final_feasibility_reason = ensure_feasible_route(biased_route, registry, metrics)
    model_id = LOGICAL_ROUTE_MODELS[final_route]
    model = registry.get(model_id)
    alternative, rejected_reason = alternative_for(final_route, metrics)
    reasons = [base_reason]
    for item in [feasibility_reason, cost_reason, final_feasibility_reason]:
        if item:
            reasons.append(item)
    costs = {}
    if model:
        costs[model_id] = estimate_cost(model, metrics)
    if alternative and alternative in registry:
        costs[alternative] = estimate_cost(registry[alternative], metrics)
    return ModelSelection(
        logical_route=final_route,
        physical_model=model_id,
        reason=" ".join(reasons),
        confidence=confidence_for_route(final_route, metrics),
        mode="heuristic",
        metrics=metrics,
        alternative_considered=alternative,
        rejected_reason=rejected_reason,
        feasibility_excluded=feasibility_exclusions(registry, metrics),
        estimated_cost_usd=costs,
    )


def summarize_task_text(task: str, prompt: str, metrics: SelectionMetrics, max_chars: int = 12000) -> str:
    """Limit selector input to keep cost bounded."""
    text = (
        f"TASK:\n{task.strip()}\n\n"
        f"METRICS:\n{json.dumps(metrics.to_dict(), indent=2)}\n\n"
        f"PROMPT/CONTEXT SUMMARY:\n{prompt.strip()}"
    )
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[TRUNCATED FOR MODEL SELECTION]"


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
    context_metadata: dict[str, Any] | None,
    cost_mode: str,
    project_id: str,
    location: str,
    selector_model: str,
    timeout_seconds: int,
) -> ModelSelection:
    """Use Gemini to choose among deterministic feasible logical routes."""
    registry = load_model_registry()
    metrics = score_task(task=task, prompt=prompt, context_metadata=context_metadata, cost_mode=cost_mode)
    excluded = feasibility_exclusions(registry, metrics)
    excluded_routes = {item["logical_route"] for item in excluded if item["reason"] != "model_not_enabled_or_missing"}
    feasible_routes = sorted(route for route in LIVE_AUTO_ROUTES if route not in excluded_routes)
    selector_prompt = f"""You are selecting the best logical model route for a coding-agent task.

Available logical routes:
{json.dumps(LOGICAL_ROUTES, indent=2)}

Physical model map:
{json.dumps(LOGICAL_ROUTE_MODELS, indent=2)}

Feasible logical routes for this task:
{json.dumps(feasible_routes, indent=2)}

Selection rules:
- Return JSON only.
- Pick exactly one logical_route from feasible logical routes.
- Respect this safety order: risk floor > token feasibility > cost-mode bias > base complexity route.
- Do not choose local_edit/codex in auto mode.
- Use hard_reasoning for risk >= 6 or complexity >= 7.
- Use large_context when estimated tokens are high.
- Use data_report for data/report work when risk < 6.

Input:
{summarize_task_text(task, prompt, metrics)}

Return this JSON shape:
{{"logical_route":"balanced_code","reason":"short reason","confidence":0.0}}
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
    parsed = extract_json_object(extract_text(response_json))
    route = str(parsed.get("logical_route", parsed.get("route", "balanced_code")))
    if route not in feasible_routes:
        route = heuristic_select(task, prompt, context_metadata, cost_mode).logical_route
    model_id = LOGICAL_ROUTE_MODELS[route]
    alternative, rejected_reason = alternative_for(route, metrics)
    confidence = parsed.get("confidence", confidence_for_route(route, metrics))
    try:
        confidence_float = float(confidence)
    except (TypeError, ValueError):
        confidence_float = confidence_for_route(route, metrics)
    costs = {}
    if model_id in registry:
        costs[model_id] = estimate_cost(registry[model_id], metrics)
    if alternative and alternative in registry:
        costs[alternative] = estimate_cost(registry[alternative], metrics)
    return ModelSelection(
        logical_route=route,
        physical_model=model_id,
        reason=str(parsed.get("reason", "Gemini selector chose from deterministic metrics.")),
        confidence=max(0.0, min(1.0, confidence_float)),
        mode="gemini",
        metrics=metrics,
        alternative_considered=alternative,
        rejected_reason=rejected_reason,
        feasibility_excluded=excluded,
        estimated_cost_usd=costs,
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
    context_metadata: dict[str, Any] | None = None,
    cost_mode: str = "balanced",
) -> ModelSelection:
    """Select a logical model route using deterministic metrics."""
    if cost_mode not in {"low", "balanced", "best"}:
        raise ValueError("cost_mode must be low, balanced, or best")
    if mode == "heuristic":
        return heuristic_select(task, prompt, context_metadata, cost_mode)
    if mode == "gemini":
        try:
            return gemini_select(
                task=task,
                prompt=prompt,
                context_metadata=context_metadata,
                cost_mode=cost_mode,
                project_id=project_id,
                location=location,
                selector_model=selector_model,
                timeout_seconds=timeout_seconds,
            )
        except Exception as exc:
            fallback = heuristic_select(task, prompt, context_metadata, cost_mode)
            return ModelSelection(
                logical_route=fallback.logical_route,
                physical_model=fallback.physical_model,
                reason=f"Gemini selector failed ({exc}); fallback used. {fallback.reason}",
                confidence=min(fallback.confidence, 0.55),
                mode="gemini_fallback",
                metrics=fallback.metrics,
                alternative_considered=fallback.alternative_considered,
                rejected_reason=fallback.rejected_reason,
                feasibility_excluded=fallback.feasibility_excluded,
                estimated_cost_usd=fallback.estimated_cost_usd,
            )
    raise ValueError("selector mode must be heuristic or gemini")


def write_selection(selection: ModelSelection, output_dir: Path) -> Path:
    """Write model selection evidence."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"model_selection_{timestamp}.json"
    path.write_text(json.dumps(selection.to_dict(), indent=2), encoding="utf-8")
    return path
