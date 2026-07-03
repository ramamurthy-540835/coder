#!/usr/bin/env python3
"""Business logic for prompt catalog search, detail, gaps, and classification."""

from __future__ import annotations

from typing import Any

from agents.core.requirement_classifier import classify_requirement_text
from agents.tools.bigquery_retriever import BigQueryPromptRetriever
from agents.tools.semantic_memory import PrismSemanticMemory


def detect_prompt_gaps(version: dict[str, Any] | None, chunks: list[dict[str, Any]], events: list[dict[str, Any]]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    if not version:
        return [{"code": "missing_current_version", "severity": "high", "message": "No current prompt_versions row found."}]

    expected_chunks = int(version.get("chunk_count") or 0)
    actual_chunks = len(chunks)
    if expected_chunks != actual_chunks:
        gaps.append({
            "code": "chunk_count_mismatch",
            "severity": "high" if expected_chunks > actual_chunks else "medium",
            "message": f"prompt_versions expects {expected_chunks} chunks, but prompt_chunks has {actual_chunks} rows.",
        })
    if int(version.get("extracted_chars") or 0) == 0:
        gaps.append({"code": "empty_extraction", "severity": "high", "message": "Current version has zero extracted characters."})
    if version.get("status") != "success":
        gaps.append({"code": "non_success_status", "severity": "high", "message": f"Current version status is {version.get('status')}."})
    if not version.get("gold_gcs_uri"):
        gaps.append({"code": "missing_gold_uri", "severity": "medium", "message": "No gold artifact URI is registered."})
    if not any(event.get("event_type") == "completed" for event in events):
        gaps.append({"code": "missing_completed_event", "severity": "medium", "message": "No completed lifecycle event found."})
    return gaps


class PromptCatalogService:
    def __init__(self, project_id: str = "ctoteam") -> None:
        self.project_id = project_id
        self.retriever = BigQueryPromptRetriever(project_id=project_id)

    def search(self, query: str = "", status: str = "", limit: int = 50) -> list[dict[str, Any]]:
        rows = self.retriever.search_prompts(query=query, status=status, limit=limit)
        for row in rows:
            row["missing_chunks"] = max(0, int(row.get("chunk_count") or 0) - int(row.get("actual_chunks") or 0))
            row["has_gap"] = row["missing_chunks"] > 0 or int(row.get("extracted_chars") or 0) == 0 or row.get("status") != "success"
        return rows

    def detail(self, prompt_uid: str) -> dict[str, Any]:
        detail = self.retriever.get_prompt_detail(prompt_uid)
        chunks = detail.get("chunks", [])
        classification_text = "\n".join(str(chunk.get("chunk_file") or "") for chunk in chunks)
        if detail.get("version"):
            classification_text += "\n" + "\n".join(str(value) for value in detail["version"].values() if value is not None)
        detail["gaps"] = detect_prompt_gaps(detail.get("version"), chunks, detail.get("events", []))
        detail["classification"] = classify_requirement_text(classification_text).to_dict()
        return detail


    def semantic_search(self, query: str, limit: int = 8, *, index_submissions: bool = True) -> list[dict[str, object]]:
        memory = PrismSemanticMemory(project_id=self.project_id)
        if index_submissions:
            memory.index_prompt_submissions(limit=200)
        return [item.to_dict() for item in memory.search(query, limit=limit)]
