#!/usr/bin/env python3
"""PostToolUse: auto-format and analyze edited Dart files.

Resolve the project's Dart SDK, format edited files, then analyze each file.
Non-Dart edits are ignored; missing SDKs and failed checks are reported.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hook_payload import extract_file_paths
from run_checks import sdk_command

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

    cwd = Path(payload.get("cwd") or Path.cwd())
    packages: dict[Path, list[str]] = {}
    for path in extract_file_paths(payload):
        path = (cwd / path).resolve()
        if path.suffix == ".dart" and path.is_file():
            package = find_pubspec(path.parent)
            if package is not None:
                packages.setdefault(package, []).append(str(path))
    try:
        for package, paths in packages.items():
            dart = sdk_command(package, "dart")
            commands = [[*dart, "format", *paths]]
            # One target per analysis call also supports older pinned Dart SDKs.
            commands += [[*dart, "analyze", path] for path in paths]
            for command in commands:
                result = subprocess.run(command, cwd=package, capture_output=True, text=True)
                if result.returncode:
                    output = (result.stdout + result.stderr).strip()
                    sys.stderr.write(f"Dart check failed:\n{output[:OUTPUT_CAP]}\n")
                    return 2
    except (OSError, ValueError) as error:
        sys.stderr.write(f"Dart checks could not run: {error}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
