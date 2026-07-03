#!/usr/bin/env python3
"""Reusable BigQuery retrieval helpers for PRISM prompt catalog data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PromptCatalogRow:
    prompt_uid: str
    source_prompt_id: str
    version_number: int
    run_id: str
    status: str
    repeat_mode: str
    chunk_count: int
    actual_chunks: int
    extracted_chars: int
    valid_from: str | None

    @property
    def missing_chunks(self) -> int:
        return max(0, self.chunk_count - self.actual_chunks)

    @property
    def has_gap(self) -> bool:
        return self.missing_chunks > 0 or self.extracted_chars == 0 or self.status != "success"


def _client(project_id: str):
    try:
        from google.cloud import bigquery
    except Exception as exc:  # pragma: no cover - dependency varies by runtime
        raise RuntimeError("google-cloud-bigquery is required for prompt catalog retrieval") from exc
    return bigquery.Client(project=project_id), bigquery


class BigQueryPromptRetriever:
    """Read prompt lakehouse metadata through parameterized BigQuery queries."""

    def __init__(self, project_id: str = "ctoteam") -> None:
        self.project_id = project_id
        self.client, self.bigquery = _client(project_id)

    def search_prompts(self, query: str = "", status: str = "", limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(200, int(limit)))
        sql = f"""
        WITH current_versions AS (
          SELECT *
          FROM `{self.project_id}.prism_prompt_catalog.prompt_versions`
          WHERE is_current = TRUE
            AND (@status = '' OR status = @status)
            AND (@query = '' OR LOWER(prompt_uid) LIKE CONCAT('%', LOWER(@query), '%')
              OR LOWER(source_prompt_id) LIKE CONCAT('%', LOWER(@query), '%'))
        ), chunk_counts AS (
          SELECT prompt_uid, run_id, version_number, COUNT(*) AS actual_chunks
          FROM `{self.project_id}.prism_prompt_catalog.prompt_chunks`
          GROUP BY prompt_uid, run_id, version_number
        )
        SELECT
          v.prompt_uid, v.source_prompt_id, v.version_number, v.run_id, v.status,
          v.repeat_mode, v.chunk_count, COALESCE(c.actual_chunks, 0) AS actual_chunks,
          v.extracted_chars, CAST(v.valid_from AS STRING) AS valid_from
        FROM current_versions v
        LEFT JOIN chunk_counts c USING (prompt_uid, run_id, version_number)
        ORDER BY v.valid_from DESC
        LIMIT @limit
        """
        job_config = self.bigquery.QueryJobConfig(
            query_parameters=[
                self.bigquery.ScalarQueryParameter("query", "STRING", query),
                self.bigquery.ScalarQueryParameter("status", "STRING", status),
                self.bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )
        return [dict(row) for row in self.client.query(sql, job_config=job_config).result()]

    def get_prompt_detail(self, prompt_uid: str) -> dict[str, Any]:
        version_sql = f"""
        SELECT *
        FROM `{self.project_id}.prism_prompt_catalog.prompt_versions`
        WHERE prompt_uid = @prompt_uid AND is_current = TRUE
        LIMIT 1
        """
        chunk_sql = f"""
        SELECT chunk_order, chunk_file, gcs_uri, char_count, estimated_tokens, role, artifact_type
        FROM `{self.project_id}.prism_prompt_catalog.prompt_chunks`
        WHERE prompt_uid = @prompt_uid
        ORDER BY version_number DESC, chunk_order ASC
        LIMIT 100
        """
        event_sql = f"""
        SELECT event_type, lifecycle_status, repeat_mode, severity, message, CAST(created_at AS STRING) AS created_at
        FROM `{self.project_id}.prism_prompt_catalog.prompt_events`
        WHERE prompt_uid = @prompt_uid
        ORDER BY created_at DESC
        LIMIT 50
        """
        attachment_sql = f"""
        SELECT attachment_id, mime_type, attachment_type, gcs_uri, size_bytes, decoded, CAST(created_at AS STRING) AS created_at
        FROM `{self.project_id}.prism_prompt_catalog.prompt_attachments`
        WHERE prompt_uid = @prompt_uid
        ORDER BY created_at DESC
        LIMIT 50
        """
        config = self.bigquery.QueryJobConfig(
            query_parameters=[self.bigquery.ScalarQueryParameter("prompt_uid", "STRING", prompt_uid)]
        )
        version_rows = [dict(row) for row in self.client.query(version_sql, job_config=config).result()]
        return {
            "prompt_uid": prompt_uid,
            "version": version_rows[0] if version_rows else None,
            "chunks": [dict(row) for row in self.client.query(chunk_sql, job_config=config).result()],
            "events": [dict(row) for row in self.client.query(event_sql, job_config=config).result()],
            "attachments": [dict(row) for row in self.client.query(attachment_sql, job_config=config).result()],
        }
