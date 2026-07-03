#!/usr/bin/env python3
"""PRISM coding agent orchestrator CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.core.context_manager import build_context, write_context_manifest
from agents.core.model_router import run_model
from agents.core.model_selector import select_model, write_selection


DEFAULT_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ctoteam")
DEFAULT_LOCATION = os.getenv("VERTEX_LOCATION", "global")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a structured PRISM coding-agent task.")
    parser.add_argument("--task", required=True, help="Coding/review/report task to run")
    parser.add_argument("--model-route", default="auto", help="auto, glm5, grok43, grok420_reasoning, grok420_non_reasoning, codex")
    parser.add_argument("--prompt-file", help="Optional saved prompt file, for example prompts/prompt-0")
    parser.add_argument(
        "--context-root",
        action="append",
        default=[],
        help="File or directory to load into context. Can be repeated.",
    )
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--location", default=DEFAULT_LOCATION)
    parser.add_argument("--output-dir", help="Override route output directory")
    parser.add_argument("--max-files", type=int, default=40)
    parser.add_argument("--max-file-chars", type=int, default=12000)
    parser.add_argument("--max-prompt-chars", type=int, default=80000)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-output-tokens", type=int, default=8192)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--selector-mode", choices=["heuristic", "gemini"], default="heuristic")
    parser.add_argument("--selector-model", default="gemini-3.5-flash")
    parser.add_argument("--cost-mode", choices=["low", "balanced", "best"], default="balanced")
    parser.add_argument("--dry-run", action="store_true", help="Build context and manifest but do not call a model")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    context_roots = args.context_root or ["agents", "scripts", "README.md"]

    try:
        context = build_context(
            task=args.task,
            prompt_file=args.prompt_file,
            context_roots=context_roots,
            repo_root=repo_root,
            max_files=args.max_files,
            max_file_chars=args.max_file_chars,
            max_prompt_chars=args.max_prompt_chars,
        )
        evidence_dir = Path(args.output_dir or "reports/orchestrator")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        manifest_path = evidence_dir / f"context_manifest_{timestamp}.json"
        write_context_manifest(context, manifest_path)

        prompt = context.render()
        prompt_path = evidence_dir / f"composed_prompt_{timestamp}.md"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(prompt, encoding="utf-8")

        selected_route = args.model_route
        selection_path = None
        selection = None
        if args.model_route == "auto":
            selection = select_model(
                task=args.task,
                prompt=context.prompt_text,
                mode=args.selector_mode,
                project_id=args.project_id,
                location=args.location,
                selector_model=args.selector_model,
                timeout_seconds=args.timeout,
                context_metadata=context.metadata,
                cost_mode=args.cost_mode,
            )
            selected_route = selection.route
            selection_path = write_selection(selection, evidence_dir)

        if args.dry_run:
            print(json.dumps({
                "status": "dry_run",
                "selected_route": selected_route,
                "selection": selection.to_dict() if selection else None,
                "selection_evidence": str(selection_path) if selection_path else None,
                "manifest": str(manifest_path),
                "composed_prompt": str(prompt_path),
                "metadata": context.metadata,
            }, indent=2))
            return 0

        result = run_model(
            route_name=selected_route,
            prompt=prompt,
            source_name="orchestrator_task",
            project_id=args.project_id,
            location=args.location,
            output_dir=args.output_dir,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            timeout_seconds=args.timeout,
        )
        print(json.dumps({
            "status": "success",
            "route": result.route.__dict__,
            "selection": selection.to_dict() if selection else None,
            "selection_evidence": str(selection_path) if selection_path else None,
            "manifest": str(manifest_path),
            "composed_prompt": str(prompt_path),
            "markdown": str(result.markdown_path),
            "json": str(result.json_path),
        }, indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
