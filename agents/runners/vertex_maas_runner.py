#!/usr/bin/env python3
"""
Run local prompt files through Vertex AI Model-as-a-Service models.

Examples:
  python3 agents/runners/vertex_maas_runner.py --preset glm5 --all
  python3 agents/runners/vertex_maas_runner.py --preset grok43 --prompt-file prompts/prompt-0
  python3 agents/runners/vertex_maas_runner.py --publisher xai --model grok-4.3 --question "Write a FastAPI CSV CRUD app"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.providers.xai import MODEL_PRESETS
from agents.providers.vertex_maas import extract_text, safe_stem, vertex_generate_content

DEFAULT_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ctoteam")
DEFAULT_LOCATION = os.getenv("VERTEX_LOCATION", "global")
DEFAULT_PRESET = "grok43"

def write_outputs(
    *,
    output_dir: Path,
    source_name: str,
    prompt: str,
    response_json: dict[str, Any],
    response_text: str,
    project_id: str,
    location: str,
    publisher: str,
    model: str,
) -> Path:
    """Save markdown output and metadata JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"{safe_stem(source_name)}_{timestamp}"

    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    md_path.write_text(response_text + "\n", encoding="utf-8")
    metadata = {
        "source": source_name,
        "project_id": project_id,
        "location": location,
        "publisher": publisher,
        "model": model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt_chars": len(prompt),
        "response_chars": len(response_text),
        "usageMetadata": response_json.get("usageMetadata", {}),
        "response": response_json,
    }
    json_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return md_path


def run_prompt(
    *,
    source_name: str,
    prompt: str,
    args: argparse.Namespace,
) -> Path:
    response_json = vertex_generate_content(
        project_id=args.project_id,
        location=args.location,
        publisher=args.publisher,
        model=args.model,
        prompt=prompt,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        timeout_seconds=args.timeout,
    )
    response_text = extract_text(response_json)
    if not response_text:
        raise RuntimeError(f"No text returned for {source_name}")

    return write_outputs(
        output_dir=Path(args.output_dir),
        source_name=source_name,
        prompt=prompt,
        response_json=response_json,
        response_text=response_text,
        project_id=args.project_id,
        location=args.location,
        publisher=args.publisher,
        model=args.model,
    )


def apply_model_preset(args: argparse.Namespace) -> argparse.Namespace:
    """Apply preset defaults, while allowing explicit CLI overrides."""
    preset = MODEL_PRESETS.get(args.preset)
    if not preset:
        choices = ", ".join(sorted(MODEL_PRESETS))
        raise ValueError(f"Unknown preset '{args.preset}'. Available presets: {choices}")

    if args.publisher is None:
        args.publisher = preset["publisher"]
    if args.model is None:
        args.model = preset["model"]
    if args.output_dir is None:
        args.output_dir = preset["output_dir"]
    return args


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call Vertex AI MaaS generateContent models for local prompt files."
    )
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--location", default=DEFAULT_LOCATION)
    parser.add_argument(
        "--preset",
        default=DEFAULT_PRESET,
        choices=sorted(MODEL_PRESETS),
        help="Named model defaults. Explicit --publisher/--model/--output-dir override it.",
    )
    parser.add_argument("--publisher", help="Vertex publisher, for example xai or zai-org")
    parser.add_argument("--model", help="Vertex MaaS model ID, for example grok-4.3 or glm-5-maas")
    parser.add_argument("--prompt-file", default="prompts/prompt-0")
    parser.add_argument("--prompts-dir", default="prompts")
    parser.add_argument("--all", action="store_true", help="Run every file in --prompts-dir")
    parser.add_argument("--question", help="Inline prompt text instead of reading a file")
    parser.add_argument("--output-dir", help="Directory for markdown and JSON response artifacts")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-output-tokens", type=int, default=8192)
    parser.add_argument("--timeout", type=int, default=180)
    return apply_model_preset(parser.parse_args())


def main() -> int:
    args = parse_args()

    try:
        if args.question:
            output_path = run_prompt(
                source_name="inline_question",
                prompt=args.question,
                args=args,
            )
            print(f"Saved Vertex MaaS response: {output_path}")
            return 0

        if args.all:
            prompt_files = sorted(
                path for path in Path(args.prompts_dir).iterdir() if path.is_file()
            )
            if not prompt_files:
                raise FileNotFoundError(f"No prompt files found in {args.prompts_dir}")

            for prompt_file in prompt_files:
                prompt = prompt_file.read_text(encoding="utf-8")
                output_path = run_prompt(
                    source_name=str(prompt_file),
                    prompt=prompt,
                    args=args,
                )
                print(f"Saved Vertex MaaS response: {output_path}")
            return 0

        prompt_file = Path(args.prompt_file)
        prompt = prompt_file.read_text(encoding="utf-8")
        output_path = run_prompt(
            source_name=str(prompt_file),
            prompt=prompt,
            args=args,
        )
        print(f"Saved Vertex MaaS response: {output_path}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
