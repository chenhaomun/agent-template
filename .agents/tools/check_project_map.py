#!/usr/bin/env python3
"""Check folder entries in .agents/project-map.md."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FOLDERS_RE = re.compile(r"^\s*-\s*folders:\s*(.+?)\s*$", re.IGNORECASE)
COMMON_DIRS = ("src", "app", "server", "client", "api", "tests", "test", "lib", "pkg", "internal")


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


def detected_folders(root: Path) -> set[str]:
    detected = {name for name in COMMON_DIRS if (root / name).is_dir()}
    for base_name in ("lib/features", "test/features", "packages", "apps"):
        base = root / base_name
        if not base.is_dir():
            continue
        detected.update(
            child.relative_to(root).as_posix()
            for child in base.iterdir()
            if child.is_dir()
            and child.name not in {"build", ".dart_tool", "node_modules", "__pycache__"}
        )
    return detected


def check_map(root: Path) -> list[str]:
    map_path = root / ".agents" / "project-map.md"
    if not map_path.exists():
        return ["project-map missing: .agents/project-map.md"]

    folders = parse_folders(map_path.read_text(encoding="utf-8", errors="ignore"))
    errors = [f"missing mapped folder: {folder}" for folder in folders if not (root / folder).exists()]
    mapped = set(folders)
    for folder in sorted(detected_folders(root)):
        if folder not in mapped:
            errors.append(f"unmapped detected folder: {folder}")
    return errors


def main() -> int:
    errors = check_map(ROOT)
    if not errors:
        map_path = ROOT / ".agents" / "project-map.md"
        count = len(parse_folders(map_path.read_text(encoding="utf-8", errors="ignore")))
        print(f"OK project-map is current: {count} mapped folder(s)")
        return 0

    print(f"FAIL project-map is stale: {len(errors)} issue(s)")
    for error in errors[:20]:
        print(f"- {error}")
    if len(errors) > 20:
        print(f"- ... {len(errors) - 20} more")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
