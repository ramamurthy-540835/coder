#!/usr/bin/env python3
"""PRISM semantic memory utilities.

V1 uses a deterministic hash embedding so the retrieval layer is testable without
live model cost. The table schema is intentionally compatible with replacing the
embedding source with Vertex/BigQuery ML embeddings later.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

try:
    from google.cloud import bigquery
except Exception:  # pragma: no cover - optional runtime dependency
    bigquery = None  # type: ignore[assignment]

DATASET = "prism_prompt_catalog"
TABLE = "prompt_semantic_memory"
EMBEDDING_DIMENSIONS = 128


@dataclass(frozen=True)
class SemanticSearchResult:
    memory_id: str
    source_type: str
    prompt_uid: str
    title: str | None
    text_preview: str
    categories: list[str]
    protection_level: str | None
    status: str | None
    similarity: float

    def to_dict(self) -> dict[str, object]:
        return {
            "memory_id": self.memory_id,
            "source_type": self.source_type,
            "prompt_uid": self.prompt_uid,
            "title": self.title,
            "text_preview": self.text_preview,
            "categories": self.categories,
            "protection_level": self.protection_level,
            "status": self.status,
            "similarity": round(self.similarity, 6),
        }


def stable_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def deterministic_embedding(text: str, dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
    """Create a stable bag-of-tokens hash embedding.

    This is not a replacement for Gemini/Vertex embeddings. It is a zero-cost,
    deterministic fallback that makes the semantic memory pipeline operational
    and testable before a managed embedding model is configured.
    """
    vector = [0.0] * dimensions
    tokens = [token for token in text.lower().replace("_", " ").split() if token]
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if not norm:
        return vector
    return [round(value / norm, 8) for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))


class PrismSemanticMemory:
    def __init__(self, project_id: str = "ctoteam") -> None:
        if bigquery is None:
            raise RuntimeError("google-cloud-bigquery is required for semantic memory")
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)

    @property
    def table_ref(self) -> str:
        return f"{self.project_id}.{DATASET}.{TABLE}"

    def ensure_table(self) -> None:
        dataset = self.client.dataset(DATASET)
        table = dataset.table(TABLE)
        try:
            self.client.get_table(table)
            return
        except Exception:
            pass

        schema = [
            bigquery.SchemaField("memory_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("prompt_uid", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("version_number", "INT64"),
            bigquery.SchemaField("run_id", "STRING"),
            bigquery.SchemaField("chunk_order", "INT64"),
            bigquery.SchemaField("title", "STRING"),
            bigquery.SchemaField("text", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("text_hash", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
            bigquery.SchemaField("embedding_model", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("categories", "STRING", mode="REPEATED"),
            bigquery.SchemaField("protection_level", "STRING"),
            bigquery.SchemaField("status", "STRING"),
            bigquery.SchemaField("gcs_uri", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        table_obj = bigquery.Table(table, schema=schema)
        table_obj.time_partitioning = bigquery.TimePartitioning(field="created_at")
        table_obj.clustering_fields = ["source_type", "prompt_uid", "status"]
        self.client.create_table(table_obj)

    def index_prompt_submissions(self, limit: int = 100) -> int:
        self.ensure_table()
        sql = f"""
        SELECT
          submission_id,
          prompt_uid,
          title,
          prompt_text,
          categories,
          protection_level,
          status,
          created_at,
          updated_at
        FROM `{self.project_id}.{DATASET}.prompt_submissions`
        WHERE prompt_text IS NOT NULL AND prompt_text != ''
        ORDER BY created_at DESC
        LIMIT @limit
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("limit", "INT64", max(1, min(1000, int(limit))))]
        )
        rows = list(self.client.query(sql, job_config=job_config).result())
        if not rows:
            return 0

        existing_hashes = self._existing_hashes("prompt_submission")
        now = datetime.now(timezone.utc).isoformat()
        to_insert: list[dict[str, Any]] = []
        for row in rows:
            data = dict(row)
            text = data.get("prompt_text") or ""
            text_hash = stable_text_hash(text)
            if text_hash in existing_hashes:
                continue
            to_insert.append({
                "memory_id": str(uuid.uuid4()),
                "source_type": "prompt_submission",
                "source_id": data["submission_id"],
                "prompt_uid": data["prompt_uid"],
                "version_number": None,
                "run_id": None,
                "chunk_order": None,
                "title": data.get("title"),
                "text": text,
                "text_hash": text_hash,
                "embedding": deterministic_embedding(text),
                "embedding_model": "local-hash-embedding-v1",
                "categories": list(data.get("categories") or []),
                "protection_level": data.get("protection_level"),
                "status": data.get("status"),
                "gcs_uri": None,
                "created_at": now,
                "updated_at": now,
            })

        if not to_insert:
            return 0
        errors = self.client.insert_rows_json(self.table_ref, to_insert)
        if errors:
            raise RuntimeError(f"Failed to insert semantic memory rows: {errors}")
        return len(to_insert)

    def search(self, query: str, limit: int = 8) -> list[SemanticSearchResult]:
        self.ensure_table()
        query_vector = deterministic_embedding(query)
        sql = f"""
        SELECT memory_id, source_type, prompt_uid, title, text, categories, protection_level, status, embedding
        FROM `{self.table_ref}`
        WHERE ARRAY_LENGTH(embedding) = @dimensions
        ORDER BY updated_at DESC
        LIMIT 1000
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("dimensions", "INT64", EMBEDDING_DIMENSIONS)]
        )
        scored: list[SemanticSearchResult] = []
        for row in self.client.query(sql, job_config=job_config).result():
            data = dict(row)
            similarity = cosine_similarity(query_vector, list(data.get("embedding") or []))
            text = data.get("text") or ""
            scored.append(SemanticSearchResult(
                memory_id=data["memory_id"],
                source_type=data["source_type"],
                prompt_uid=data["prompt_uid"],
                title=data.get("title"),
                text_preview=text[:500],
                categories=list(data.get("categories") or []),
                protection_level=data.get("protection_level"),
                status=data.get("status"),
                similarity=similarity,
            ))
        scored.sort(key=lambda item: item.similarity, reverse=True)
        return scored[: max(1, min(50, int(limit)))]

    def _existing_hashes(self, source_type: str) -> set[str]:
        self.ensure_table()
        sql = f"SELECT text_hash FROM `{self.table_ref}` WHERE source_type = @source_type"
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("source_type", "STRING", source_type)]
        )
        return {row.text_hash for row in self.client.query(sql, job_config=job_config).result()}


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISM semantic memory indexing/search")
    parser.add_argument("--project-id", default="ctoteam")
    parser.add_argument("--index-submissions", action="store_true")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--query", help="Optional semantic search query")
    args = parser.parse_args()

    memory = PrismSemanticMemory(project_id=args.project_id)
    result: dict[str, object] = {"project_id": args.project_id}
    if args.index_submissions:
        result["indexed_submission_rows"] = memory.index_prompt_submissions(limit=args.limit)
    if args.query:
        result["results"] = [item.to_dict() for item in memory.search(args.query, limit=args.limit)]
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
