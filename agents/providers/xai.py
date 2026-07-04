#!/usr/bin/env python3
"""xAI model routing metadata for Vertex MaaS."""

from __future__ import annotations

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


def is_xai_model(model_id: str) -> bool:
    """Return True when an identifier is scoped under xAI."""
    return model_id.startswith("xai/")
