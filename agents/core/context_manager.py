#!/usr/bin/env python3
"""Context loading utilities for PRISM coding agents."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


DEFAULT_ALLOWED_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".sql",
    ".sh",
    ".ts",
    ".tsx",
    ".js",
    ".mjs",
}

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".next",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "logs",
    ".pytest_cache",
}


@dataclass(frozen=True)
class LoadedFile:
    """A file included in the model context."""

    path: str
    chars: int
    content: str


@dataclass(frozen=True)
class ProjectContext:
    """Aggregated context used by the orchestrator."""

    task: str
    prompt_file: str | None
    prompt_text: str
    project_files: list[LoadedFile] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    def render(self) -> str:
        """Render context into a single prompt for a coding model."""
        sections = [
            "# PRISM CODING AGENT TASK",
            self.task.strip(),
            "",
            "# SAVED PROMPT CONTEXT",
            self.prompt_text.strip() or "(none provided)",
            "",
            "# PROJECT FILE CONTEXT",
        ]
        if not self.project_files:
            sections.append("(no project files loaded)")
        for loaded in self.project_files:
            sections.extend(
                [
                    f"\n## FILE: {loaded.path}",
                    "```",
                    loaded.content,
                    "```",
                ]
            )
        sections.extend(
            [
                "",
                "# OUTPUT REQUIREMENTS",
                "Return a practical engineering response. Include file-level changes, commands to run, and risks or assumptions.",
            ]
        )
        return "\n".join(sections).strip() + "\n"


def read_text_file(path: Path, max_chars: int) -> str:
    """Read a text file with a hard cap to control model cost."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[TRUNCATED: file exceeded per-file character limit]\n"


def iter_context_files(
    roots: Iterable[Path],
    allowed_suffixes: set[str],
    ignore_dirs: set[str],
) -> Iterable[Path]:
    """Yield context files from root paths in stable order."""
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            if root.suffix in allowed_suffixes:
                yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in ignore_dirs]
            base = Path(dirpath)
            for filename in sorted(filenames):
                path = base / filename
                if path.suffix in allowed_suffixes and not filename.startswith("."):
                    yield path


def load_project_files(
    roots: list[str],
    *,
    repo_root: Path,
    max_files: int,
    max_file_chars: int,
    allowed_suffixes: set[str] | None = None,
    ignore_dirs: set[str] | None = None,
) -> list[LoadedFile]:
    """Load selected project files with count and character limits."""
    suffixes = allowed_suffixes or DEFAULT_ALLOWED_SUFFIXES
    ignored = ignore_dirs or DEFAULT_IGNORE_DIRS
    loaded: list[LoadedFile] = []
    root_paths = [(repo_root / root).resolve() for root in roots]

    for path in iter_context_files(root_paths, suffixes, ignored):
        if len(loaded) >= max_files:
            break
        try:
            content = read_text_file(path, max_file_chars)
            rel_path = str(path.resolve().relative_to(repo_root.resolve()))
        except Exception:
            continue
        loaded.append(LoadedFile(path=rel_path, chars=len(content), content=content))
    return loaded


def load_prompt_text(prompt_file: str | None, max_chars: int) -> str:
    """Load saved prompt text if provided."""
    if not prompt_file:
        return ""
    path = Path(prompt_file)
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    return read_text_file(path, max_chars)



def load_bigquery_prompt_context(*, prompt_uid: str, project_id: str, max_chars: int) -> str:
    """Load prompt catalog context from BigQuery.

    The current catalog stores version and chunk metadata. Some deployments store
    chunk text elsewhere, so this function intentionally returns a concise
    metadata context rather than assuming chunk content is present in BigQuery.
    """
    if not prompt_uid:
        return ""
    try:
        from google.cloud import bigquery
    except Exception as exc:
        raise RuntimeError("google-cloud-bigquery is required for BigQuery context retrieval") from exc

    client = bigquery.Client(project=project_id)
    version_query = f"""
    SELECT
      prompt_uid,
      source_prompt_id,
      run_id,
      version_number,
      repeat_mode,
      status,
      chunk_count,
      system_present,
      user_message_count,
      model_message_count,
      raw_size_bytes,
      extracted_chars,
      bronze_gcs_uri,
      silver_gcs_uri,
      gold_gcs_uri
    FROM `{project_id}.prism_prompt_catalog.prompt_versions`
    WHERE prompt_uid = @prompt_uid AND is_current = TRUE
    LIMIT 1
    """
    chunk_query = f"""
    SELECT chunk_order, chunk_file, gcs_uri, char_count, estimated_tokens, role, artifact_type
    FROM `{project_id}.prism_prompt_catalog.prompt_chunks`
    WHERE prompt_uid = @prompt_uid
    ORDER BY chunk_order ASC
    LIMIT 50
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("prompt_uid", "STRING", prompt_uid)]
    )
    version_rows = list(client.query(version_query, job_config=job_config).result())
    chunk_rows = list(client.query(chunk_query, job_config=job_config).result())

    lines = [
        "# BIGQUERY PROMPT CATALOG CONTEXT",
        f"Prompt UID: {prompt_uid}",
        "",
    ]
    if version_rows:
        row = dict(version_rows[0])
        lines.append("## Current Version")
        for key, value in row.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("No current prompt_versions row found.")

    lines.append("\n## Registered Chunks")
    if chunk_rows:
        for row in chunk_rows:
            data = dict(row)
            lines.append(
                "- "
                f"order={data.get('chunk_order')} "
                f"file={data.get('chunk_file')} "
                f"chars={data.get('char_count')} "
                f"tokens={data.get('estimated_tokens')} "
                f"gcs={data.get('gcs_uri')}"
            )
    else:
        lines.append("No prompt_chunks rows found.")

    rendered = "\n".join(lines).strip() + "\n"
    if len(rendered) <= max_chars:
        return rendered
    return rendered[:max_chars] + "\n\n[TRUNCATED: BigQuery context exceeded character limit]\n"

def build_context(
    *,
    task: str,
    prompt_file: str | None,
    context_roots: list[str],
    repo_root: Path,
    max_files: int = 40,
    max_file_chars: int = 12000,
    max_prompt_chars: int = 80000,
    bigquery_prompt_uid: str | None = None,
    gcp_project_id: str | None = None,
) -> ProjectContext:
    """Build an orchestrator-ready project context."""
    prompt_text = load_prompt_text(prompt_file, max_prompt_chars)
    bigquery_context_status = None
    if bigquery_prompt_uid:
        project_id = gcp_project_id or 'ctoteam'
        try:
            bq_text = load_bigquery_prompt_context(
                prompt_uid=bigquery_prompt_uid,
                project_id=project_id,
                max_chars=max_prompt_chars,
            )
            prompt_text = (prompt_text + '\n\n' + bq_text).strip() if prompt_text else bq_text
            bigquery_context_status = "loaded"
        except Exception as exc:
            bigquery_context_status = f"unavailable: {exc}"
            warning = (
                "# BIGQUERY PROMPT CATALOG CONTEXT\n"
                f"Prompt UID: {bigquery_prompt_uid}\n"
                f"Status: {bigquery_context_status}\n"
            )
            prompt_text = (prompt_text + '\n\n' + warning).strip() if prompt_text else warning
    project_files = load_project_files(
        context_roots,
        repo_root=repo_root,
        max_files=max_files,
        max_file_chars=max_file_chars,
    )
    metadata = {
        "context_roots": context_roots,
        "project_file_count": len(project_files),
        "project_context_chars": sum(item.chars for item in project_files),
        "prompt_chars": len(prompt_text),
        "bigquery_prompt_uid": bigquery_prompt_uid,
        "bigquery_context_status": bigquery_context_status,
    }
    return ProjectContext(
        task=task,
        prompt_file=prompt_file,
        prompt_text=prompt_text,
        project_files=project_files,
        metadata=metadata,
    )


def write_context_manifest(context: ProjectContext, output_path: Path) -> None:
    """Write a lightweight manifest for audit/evidence."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "task": context.task,
        "prompt_file": context.prompt_file,
        "metadata": context.metadata,
        "files": [{"path": item.path, "chars": item.chars} for item in context.project_files],
    }
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
