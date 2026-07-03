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
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


DEFAULT_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ctoteam")
DEFAULT_LOCATION = os.getenv("VERTEX_LOCATION", "global")
DEFAULT_PRESET = "grok43"

MODEL_PRESETS: dict[str, dict[str, str]] = {
    "glm5": {
        "publisher": "zai-org",
        "model": "glm-5-maas",
        "output_dir": "reports/glm5",
    },
    "grok43": {
        "publisher": "xai",
        "model": "grok-4.3",
        "output_dir": "reports/grok43",
    },
    "grok420_reasoning": {
        "publisher": "xai",
        "model": "grok-4.20-reasoning",
        "output_dir": "reports/grok420_reasoning",
    },
    "grok420_non_reasoning": {
        "publisher": "xai",
        "model": "grok-4.20-non-reasoning",
        "output_dir": "reports/grok420_non_reasoning",
    },
}


def get_access_token() -> str:
    """Return a Google Cloud access token from active gcloud auth."""
    commands = [
        ["gcloud", "auth", "print-access-token"],
        ["gcloud", "auth", "application-default", "print-access-token"],
    ]

    for command in commands:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
            token = result.stdout.strip()
            if token:
                return token
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    raise RuntimeError(
        "Could not get a GCP access token. Run: "
        "gcloud auth login --no-launch-browser"
    )


def vertex_generate_content(
    *,
    project_id: str,
    location: str,
    publisher: str,
    model: str,
    prompt: str,
    temperature: float,
    max_output_tokens: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    """Call Vertex AI generateContent and return the raw JSON response."""
    token = get_access_token()
    url = (
        f"https://aiplatform.googleapis.com/v1/projects/{project_id}"
        f"/locations/{location}/publishers/{publisher}/models/{model}:generateContent"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-goog-user-project": project_id,
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        },
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return response.json()


def extract_text(response_json: dict[str, Any]) -> str:
    """Extract generated text from a Vertex generateContent response."""
    parts: list[str] = []
    for candidate in response_json.get("candidates", []):
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            text = part.get("text")
            if text:
                parts.append(text)
    return "\n\n".join(parts).strip()


def safe_stem(value: str) -> str:
    """Create a stable filesystem-friendly output stem."""
    stem = Path(value).stem or "prompt"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    return stem or "prompt"


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
