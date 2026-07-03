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


def build_context(
    *,
    task: str,
    prompt_file: str | None,
    context_roots: list[str],
    repo_root: Path,
    max_files: int = 40,
    max_file_chars: int = 12000,
    max_prompt_chars: int = 80000,
) -> ProjectContext:
    """Build an orchestrator-ready project context."""
    prompt_text = load_prompt_text(prompt_file, max_prompt_chars)
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
