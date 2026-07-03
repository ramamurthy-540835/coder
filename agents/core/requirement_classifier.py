#!/usr/bin/env python3
"""Deterministic requirement classification for prompt catalog entries."""

from __future__ import annotations

from dataclasses import dataclass, asdict

CATEGORY_KEYWORDS = {
    "business_requirement": ["business", "stakeholder", "workflow", "process", "customer", "user story", "acceptance"],
    "technical_requirement": ["api", "service", "database", "schema", "architecture", "integration", "code", "backend", "frontend"],
    "data_requirement": ["bigquery", "table", "dataset", "pipeline", "etl", "gcs", "csv", "json", "data"],
    "security_compliance": ["security", "iam", "secret", "token", "credential", "compliance", "audit", "permission"],
    "deployment_operational": ["deploy", "cloud run", "gcp", "terraform", "release", "environment", "monitoring", "logging"],
    "testing_acceptance": ["test", "qa", "validation", "verify", "acceptance criteria", "unit test", "integration test"],
}

GAP_KEYWORDS = {
    "missing_acceptance_criteria": ["acceptance", "done when", "success criteria"],
    "missing_security_requirements": ["security", "iam", "permission", "secret", "compliance"],
    "missing_test_requirements": ["test", "validation", "verify", "qa"],
    "missing_deployment_requirements": ["deploy", "release", "environment", "cloud run", "gcp"],
}


@dataclass(frozen=True)
class RequirementClassification:
    categories: list[str]
    confidence: float
    missing_requirement_signals: list[str]
    evidence: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def classify_requirement_text(text: str) -> RequirementClassification:
    """Classify prompt text with explainable keyword evidence.

    This is intentionally deterministic for v1. Model-based classification can be
    layered later after the team accepts the categories and evidence contract.
    """
    normalized = text.lower()
    categories: list[str] = []
    evidence: list[str] = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [keyword for keyword in keywords if keyword in normalized]
        if matched:
            categories.append(category)
            evidence.append(f"{category}: {', '.join(matched[:4])}")

    missing = []
    for gap, keywords in GAP_KEYWORDS.items():
        if not any(keyword in normalized for keyword in keywords):
            missing.append(gap)

    if not categories:
        categories = ["unknown_or_needs_triage"]
        confidence = 0.35
        evidence.append("No strong deterministic category keywords found.")
    else:
        confidence = min(0.9, 0.45 + (0.1 * len(categories)))

    return RequirementClassification(
        categories=categories,
        confidence=round(confidence, 2),
        missing_requirement_signals=missing,
        evidence=evidence,
    )
