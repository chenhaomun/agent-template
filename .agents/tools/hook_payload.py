#!/usr/bin/env python3
"""Extract edited paths from Claude Code and Codex hook payloads."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Delete|Update) File: (.+)$", re.MULTILINE)


def extract_file_paths(payload: dict[str, Any]) -> list[Path]:
    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, str):
        patch_text = tool_input
        tool_input = {}
    elif isinstance(tool_input, dict):
        patch_text = next(
            (
                value
                for key in ("command", "patch", "input")
                if isinstance((value := tool_input.get(key)), str)
            ),
            "",
        )
    else:
        return []

    candidates: list[str] = []
    file_path = tool_input.get("file_path")
    if isinstance(file_path, str):
        candidates.append(file_path)
    candidates.extend(PATCH_PATH_RE.findall(patch_text))

    paths: list[Path] = []
    for candidate in candidates:
        path = Path(candidate.strip())
        if path not in paths:
            paths.append(path)
    return paths
