#!/usr/bin/env python3
"""Check that .agents/project-context.md reflects the current structure."""

from __future__ import annotations

import re
from pathlib import Path

from generate_project_context import BEGIN, END, detect_areas


ROOT = Path(__file__).resolve().parents[2]
FOLDERS = re.compile(r"^\s*-\s*folders:\s*(.+?)\s*$", re.IGNORECASE)


def generated_block(text: str) -> str | None:
    match = re.search(rf"{re.escape(BEGIN)}(.*?){re.escape(END)}", text, re.DOTALL)
    return match.group(1) if match else None


def mapped_folders(block: str) -> set[str]:
    folders: set[str] = set()
    for line in block.splitlines():
        match = FOLDERS.match(line)
        if match:
            folders.update(item.strip().strip("`") for item in match.group(1).split(",") if item.strip())
    return folders


def check_context(root: Path) -> list[str]:
    path = root / ".agents" / "project-context.md"
    if not path.exists():
        return ["project-context missing: .agents/project-context.md"]
    block = generated_block(path.read_text(encoding="utf-8", errors="ignore"))
    if block is None:
        return ["project-context generated structure markers are missing"]
    mapped = mapped_folders(block)
    detected = {folder for folders in detect_areas(root).values() for folder in folders}
    errors = [f"missing mapped folder: {folder}" for folder in sorted(mapped) if not (root / folder).is_dir()]
    errors += [f"unmapped detected folder: {folder}" for folder in sorted(detected - mapped)]
    errors += [f"stale generated folder: {folder}" for folder in sorted(mapped - detected) if (root / folder).is_dir()]
    return errors


def main() -> int:
    errors = check_context(ROOT)
    if not errors:
        print("OK project-context is current")
        return 0
    print(f"FAIL project-context is stale: {len(errors)} issue(s)")
    for error in errors[:20]:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
