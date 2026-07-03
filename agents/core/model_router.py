#!/usr/bin/env python3
"""Model routing for PRISM coding agents."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.runners.vertex_maas_runner import (
    MODEL_PRESETS,
    extract_text,
    safe_stem,
    vertex_generate_content,
)


@dataclass(frozen=True)
class ModelRoute:
    """Resolved model route."""

    name: str
    provider: str
    publisher: str | None
    model: str
    output_dir: str


@dataclass(frozen=True)
class ModelResult:
    """Result from a model invocation."""

    route: ModelRoute
    text: str
    raw_response: dict[str, Any]
    markdown_path: Path
    json_path: Path


LOCAL_ROUTES: dict[str, ModelRoute] = {
    "codex": ModelRoute(
        name="codex",
        provider="local",
        publisher=None,
        model="codex-cli",
        output_dir="reports/codex",
    )
}


def resolve_route(name: str, output_dir: str | None = None) -> ModelRoute:
    """Resolve a named route from built-in presets."""
    if name in MODEL_PRESETS:
        preset = MODEL_PRESETS[name]
        return ModelRoute(
            name=name,
            provider="vertex_maas",
            publisher=preset["publisher"],
            model=preset["model"],
            output_dir=output_dir or preset["output_dir"],
        )
    if name in LOCAL_ROUTES:
        route = LOCAL_ROUTES[name]
        if output_dir:
            return ModelRoute(route.name, route.provider, route.publisher, route.model, output_dir)
        return route
    choices = sorted([*MODEL_PRESETS.keys(), *LOCAL_ROUTES.keys()])
    raise ValueError(f"Unknown model route '{name}'. Available routes: {', '.join(choices)}")


def write_model_outputs(
    *,
    route: ModelRoute,
    source_name: str,
    prompt: str,
    response_json: dict[str, Any],
    response_text: str,
    project_id: str,
    location: str,
) -> tuple[Path, Path]:
    """Write model output and raw metadata."""
    output_dir = Path(route.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"{safe_stem(source_name)}_{route.name}_{timestamp}"
    md_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"
    md_path.write_text(response_text + "\n", encoding="utf-8")
    metadata = {
        "route": route.__dict__,
        "source": source_name,
        "project_id": project_id,
        "location": location,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt_chars": len(prompt),
        "response_chars": len(response_text),
        "usageMetadata": response_json.get("usageMetadata", {}),
        "response": response_json,
    }
    json_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return md_path, json_path


def run_vertex_route(
    *,
    route: ModelRoute,
    prompt: str,
    source_name: str,
    project_id: str,
    location: str,
    temperature: float,
    max_output_tokens: int,
    timeout_seconds: int,
) -> ModelResult:
    """Run a Vertex MaaS model route."""
    if not route.publisher:
        raise ValueError(f"Route {route.name} is missing a Vertex publisher")
    response_json = vertex_generate_content(
        project_id=project_id,
        location=location,
        publisher=route.publisher,
        model=route.model,
        prompt=prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        timeout_seconds=timeout_seconds,
    )
    response_text = extract_text(response_json)
    if not response_text:
        raise RuntimeError(f"No text returned by route {route.name}")
    md_path, json_path = write_model_outputs(
        route=route,
        source_name=source_name,
        prompt=prompt,
        response_json=response_json,
        response_text=response_text,
        project_id=project_id,
        location=location,
    )
    return ModelResult(route, response_text, response_json, md_path, json_path)


def run_model(
    *,
    route_name: str,
    prompt: str,
    source_name: str,
    project_id: str,
    location: str,
    output_dir: str | None = None,
    temperature: float = 0.2,
    max_output_tokens: int = 8192,
    timeout_seconds: int = 180,
) -> ModelResult:
    """Run a configured model route."""
    route = resolve_route(route_name, output_dir=output_dir)
    if route.provider == "vertex_maas":
        return run_vertex_route(
            route=route,
            prompt=prompt,
            source_name=source_name,
            project_id=project_id,
            location=location,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            timeout_seconds=timeout_seconds,
        )
    raise NotImplementedError(
        "The codex route is registered for planning, but local Codex execution is not wired yet. "
        "Use the Codex CLI directly for now."
    )
