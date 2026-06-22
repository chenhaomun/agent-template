#!/usr/bin/env python3
"""PreToolUse guard: block edits to generated/vendored files.

Reads a Claude Code or Codex hook payload from stdin. If any target file looks
generated, exit 2 to block the edit and tell the agent why.
Exit 0 otherwise. Safe no-op on any parse error (never blocks real work).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from hook_payload import extract_file_paths

# Suffix patterns for code-generated Dart/Flutter files.
GENERATED_SUFFIXES = (
    ".g.dart",
    ".freezed.dart",
    ".gr.dart",
    ".config.dart",
    ".mocks.dart",
    ".pb.dart",
    ".pbenum.dart",
    ".pbjson.dart",
    ".pbserver.dart",
    ".gen.dart",
)
GENERATED_NAMES = {
    "generated_plugin_registrant.dart",
    "firebase_options.dart",
}
# Directory segments that should never be hand-edited.
GENERATED_DIRS = {".dart_tool", "build", ".git", "node_modules"}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    for path in extract_file_paths(payload):
        name = path.name
        if name in GENERATED_NAMES or name.endswith(GENERATED_SUFFIXES):
            reason = "generated file"
        elif GENERATED_DIRS.intersection(path.parts):
            seg = next(p for p in path.parts if p in GENERATED_DIRS)
            reason = f"inside generated/vendored dir '{seg}/'"
        else:
            continue

        sys.stderr.write(
            f"Blocked: '{name}' is a {reason}. "
            "Edit the source (annotations, schema, or generator config) and "
            "re-run the generator instead.\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
