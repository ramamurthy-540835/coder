#!/usr/bin/env python3
"""Scoring and metric helpers for model routing decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def clamp(value: int, low: int = 1, high: int = 10) -> int:
    """Clamp a score to a bounded range."""
    return max(low, min(high, value))


@dataclass(frozen=True)
class ScoreItem:
    """One scorecard contribution."""

    category: str
    signal: str
    points: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "signal": self.signal,
            "points": self.points,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class SelectionMetrics:
    """Measured task complexity and routing inputs."""

    complexity_score: int
    risk_score: int
    estimated_tokens: int
    prompt_chars: int
    context_file_count: int
    project_context_chars: int
    cost_mode: str
    intent: list[str]
    scorecard: list[ScoreItem] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "complexity_score": self.complexity_score,
            "risk_score": self.risk_score,
            "estimated_tokens": self.estimated_tokens,
            "prompt_chars": self.prompt_chars,
            "context_file_count": self.context_file_count,
            "project_context_chars": self.project_context_chars,
            "cost_mode": self.cost_mode,
            "intent": self.intent,
            "signals": self.signals,
            "scorecard": [item.to_dict() for item in self.scorecard],
        }


def add_score(items: list[ScoreItem], category: str, signal: str, points: int, reason: str) -> None:
    """Append a score item if points are positive."""
    if points > 0:
        items.append(ScoreItem(category, signal, points, reason))


def detect_intent(text: str) -> list[str]:
    """Detect broad task intent labels."""
    rules = {
        "security_review": ["security", "iam", "secret", "credential", "vulnerability", "compliance", "owasp"],
        "architecture": ["architecture", "design", "tradeoff", "scalable", "resilience", "orchestration"],
        "debugging": ["debug", "root cause", "failing", "error", "fix", "incident", "race condition"],
        "code_generation": ["generate code", "write code", "implement", "scaffold", "crud"],
        "code_review": ["review", "audit", "quality", "risks"],
        "testing": ["test", "pytest", "unit test", "integration test", "coverage"],
        "deployment": ["deploy", "cloud run", "workflow", "gcp", "terraform", "iam", "cloudbuild"],
        "data_report": ["bigquery", "sql", "etl", "data", "pipeline", "report", "summarize"],
        "local_edit": ["apply patch", "edit files", "modify files", "commit", "push"],
    }
    return [name for name, terms in rules.items() if any(term in text for term in terms)] or ["general_coding"]


def score_task(
    *,
    task: str,
    prompt: str,
    context_metadata: dict[str, Any] | None,
    cost_mode: str,
) -> SelectionMetrics:
    """Score task complexity and risk with explicit point evidence."""
    metadata = context_metadata or {}
    context_file_count = int(metadata.get("project_file_count", 0) or 0)
    project_context_chars = int(metadata.get("project_context_chars", 0) or 0)
    prompt_chars = int(metadata.get("prompt_chars", len(prompt)) or len(prompt))
    total_chars = len(task) + prompt_chars + project_context_chars
    estimated_tokens = max(1, total_chars // 4)

    task_text = task.lower()
    support_text = prompt.lower()
    task_intent = detect_intent(task_text)
    support_intent = [] if not support_text.strip() else detect_intent(support_text)
    support_intent_signals = [
        f"support_{item}"
        for item in support_intent
        if item != "general_coding"
    ]
    intent = list(dict.fromkeys([*task_intent, *support_intent_signals]))

    complexity_items: list[ScoreItem] = []
    risk_items: list[ScoreItem] = []

    if 1 <= context_file_count <= 2:
        add_score(complexity_items, "complexity", "context_files_1_to_2", 1, "Small multi-file context.")
    elif 3 <= context_file_count <= 6:
        add_score(complexity_items, "complexity", "context_files_3_to_6", 2, "Moderate multi-file context.")
    elif context_file_count >= 7:
        add_score(complexity_items, "complexity", "context_files_7_plus", 3, "Large multi-file context.")

    if 5000 <= project_context_chars < 20000:
        add_score(complexity_items, "complexity", "context_size_5k_to_20k", 1, "Moderate context size.")
    elif 20000 <= project_context_chars < 50000:
        add_score(complexity_items, "complexity", "context_size_20k_to_50k", 2, "Large context size.")
    elif project_context_chars >= 50000:
        add_score(complexity_items, "complexity", "context_size_50k_plus", 3, "Very large context size.")

    task_signals = {
        "code_generation": ("code_generation", 1, "Code generation or implementation requested in task."),
        "code_review": ("code_review", 1, "Review or audit requested in task."),
        "testing": ("tests_required", 1, "Tests or validation mentioned in task."),
        "deployment": ("deployment_required", 1, "Deployment or cloud workflow mentioned in task."),
        "architecture": ("architecture_design", 2, "Architecture/design reasoning requested in task."),
        "debugging": ("debug_root_cause", 2, "Debugging or root cause reasoning requested in task."),
        "security_review": ("security_compliance", 2, "Security/compliance reasoning requested in task."),
    }
    for label, (signal, points, reason) in task_signals.items():
        if label in task_intent:
            add_score(complexity_items, "complexity", signal, points, reason)
    if any(term in task_text for term in ["multi-step", "multi agent", "multi-agent", "orchestrate", "workflow"]):
        add_score(complexity_items, "complexity", "multi_step_reasoning", 2, "Multi-step or orchestration language present in task.")

    supporting_complexity_labels = {
        "architecture",
        "debugging",
        "security_review",
        "deployment",
        "testing",
        "code_review",
        "code_generation",
        "data_report",
    }
    if any(label in support_intent for label in supporting_complexity_labels):
        add_score(
            complexity_items,
            "complexity",
            "supporting_context_complexity",
            1,
            "Saved prompt/supporting context contains complexity signals; capped at +1.",
        )

    # Risk floor signals are intentionally task-only.
    if "security_review" in task_intent:
        add_score(risk_items, "risk", "security_compliance_wording", 3, "Security/compliance requested in task.")
    if any(term in task_text for term in ["production", "prod", "critical", "incident", "customer", "release"]):
        add_score(risk_items, "risk", "production_critical_wording", 2, "Production or critical system mentioned in task.")
    if any(term in task_text for term in ["gcp", "iam", "deploy", "cloud run", "cloudbuild", "workflow"]):
        add_score(risk_items, "risk", "gcp_iam_deployment", 2, "Cloud/IAM/deployment changes mentioned in task.")
    if any(term in task_text for term in ["bigquery write", "gcs write", "insert_rows", "load_table", "write to bigquery", "upload to gcs"]):
        add_score(risk_items, "risk", "bigquery_gcs_write", 2, "Cloud data writes mentioned in the task.")
    if any(term in task_text for term in ["execute generated", "run generated", "subprocess", "shell", "eval", "exec("]):
        add_score(risk_items, "risk", "generated_code_execution", 3, "Generated or shell code execution mentioned in task.")
    if context_file_count >= 3 or any(term in task_text for term in ["multi-file", "multiple files", "across files"]):
        add_score(risk_items, "risk", "multi_file_change", 1, "Multi-file context/change increases regression risk.")
    if any(term in task_text for term in ["api key", "auth", "token", "credential", "secret", "external api"]):
        add_score(risk_items, "risk", "external_api_secret_auth", 2, "Auth/secrets/external APIs mentioned in task.")

    support_risk_terms = [
        "security",
        "iam",
        "secret",
        "credential",
        "production",
        "deploy",
        "gcp",
        "bigquery write",
        "gcs write",
    ]
    if support_text and any(term in support_text for term in support_risk_terms):
        add_score(
            risk_items,
            "risk",
            "supporting_context_risk",
            1,
            "Saved prompt/supporting context contains risk signals; capped at +1 and cannot trigger risk floor.",
        )

    complexity_score = clamp(1 + sum(item.points for item in complexity_items))
    risk_score = clamp(1 + sum(item.points for item in risk_items))
    scorecard = [*complexity_items, *risk_items]
    signals = [item.signal for item in scorecard]
    return SelectionMetrics(
        complexity_score=complexity_score,
        risk_score=risk_score,
        estimated_tokens=estimated_tokens,
        prompt_chars=prompt_chars,
        context_file_count=context_file_count,
        project_context_chars=project_context_chars,
        cost_mode=cost_mode,
        intent=intent,
        scorecard=scorecard,
        signals=signals,
    )
