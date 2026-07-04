#!/usr/bin/env python3
"""Codex provider adapter placeholder."""

from __future__ import annotations


def build_local_edit_route():
    """Return metadata for the local Codex execution plan.

    Local Codex execution is not currently wired to a runtime adapter.
    Keep this module for future extension and for routing completeness.
    """
    return {
        "provider": "local",
        "publisher": None,
        "model": "codex-cli",
        "output_dir": "reports/codex",
    }
