#!/usr/bin/env python3
"""PostToolUse: auto-format and analyze edited Dart files.

Reads a Claude Code or Codex hook payload from stdin. For edited `.dart` files
inside a Dart/Flutter project, runs `dart format` then `dart analyze` on each
file. If the analyzer reports issues, prints them to stderr and exits 2.

Deterministic and cheap: the agent never has to run/parse these itself.
Safe no-op when `dart` is unavailable, the file is not Dart, or there is no
surrounding `pubspec.yaml` (non-Flutter projects).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from hook_payload import extract_file_paths

OUTPUT_CAP = 4000  # keep analyzer output within the AGENTS.md cap


def find_pubspec(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        if (parent / "pubspec.yaml").exists():
            return parent
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    dart = shutil.which("dart")
    if not dart:
        return 0  # not a Dart environment; nothing to enforce

    failed = False
    for path in extract_file_paths(payload):
        if path.suffix != ".dart" or not path.exists():
            continue
        if find_pubspec(path.resolve().parent) is None:
            continue

        target = str(path)
        subprocess.run([dart, "format", target], capture_output=True, text=True)
        result = subprocess.run(
            [dart, "analyze", target], capture_output=True, text=True
        )
        if result.returncode == 0:
            continue

        out = (result.stdout or result.stderr or "").strip()
        if len(out) > OUTPUT_CAP:
            out = out[:OUTPUT_CAP] + "\n... (truncated)"
        sys.stderr.write(f"dart analyze found issues in {path.name}:\n{out}\n")
        failed = True
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
