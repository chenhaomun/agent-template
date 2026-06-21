#!/usr/bin/env python3
"""Check folder entries in .agents/project-map.md."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path.cwd()
MAP = ROOT / ".agents" / "project-map.md"
FOLDERS_RE = re.compile(r"^\s*-\s*folders:\s*(.+?)\s*$", re.IGNORECASE)


def parse_folders(text: str) -> list[str]:
    folders: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = FOLDERS_RE.match(line)
        if not match:
            continue
        for item in match.group(1).split(","):
            folder = item.strip().strip("`").strip()
            if folder:
                folders.append(folder)
    return folders


def main() -> int:
    if not MAP.exists():
        print("FAIL project-map missing: .agents/project-map.md")
        return 1

    folders = parse_folders(MAP.read_text(encoding="utf-8", errors="ignore"))
    if not folders:
        print("OK project-map has no mapped folders yet")
        return 0

    missing = [folder for folder in folders if not (ROOT / folder).exists()]
    if missing:
        print(f"FAIL missing mapped folders: {len(missing)}")
        for folder in missing[:20]:
            print(f"- {folder}")
        if len(missing) > 20:
            print(f"- ... {len(missing) - 20} more")
        return 1

    print(f"OK project-map folders exist: {len(folders)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
