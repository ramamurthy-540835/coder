#!/usr/bin/env python3
"""Vertex AI MaaS provider utilities."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _run_access_token_command(command: list[str]) -> str:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )
    token = result.stdout.strip()
    if token:
        return token
    return ""


def get_access_token() -> str:
    """Return a Google Cloud access token from active gcloud auth."""
    commands = [
        ["gcloud", "auth", "print-access-token"],
        ["gcloud", "auth", "application-default", "print-access-token"],
    ]

    for command in commands:
        try:
            token = _run_access_token_command(command)
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
    """Call Vertex AI generateContent and return raw JSON response."""
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

    import requests

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
