#!/usr/bin/env python3
"""Generate a starter .agents/project-map.md from common folder layouts."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path.cwd()
MAP = ROOT / ".agents" / "project-map.md"
MAX_AREAS = 40


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def existing(*parts: str) -> Path | None:
    path = ROOT.joinpath(*parts)
    return path if path.exists() and path.is_dir() else None


def child_dirs(path: Path) -> list[Path]:
    ignored = {"build", ".dart_tool", "node_modules", "__pycache__", ".git", "dist", ".next", "target"}
    return sorted(p for p in path.iterdir() if p.is_dir() and p.name not in ignored)


def add_area(areas: dict[str, set[str]], name: str, *folders: Path | None) -> None:
    valid = [rel(folder) for folder in folders if folder and folder.exists()]
    if valid:
        areas.setdefault(name.replace("_", "-").lower(), set()).update(valid)


def detect_areas() -> dict[str, set[str]]:
    areas: dict[str, set[str]] = {}

    # Flutter/Dart common layouts.
    for base in (existing("lib", "features"), existing("test", "features")):
        if not base:
            continue
        for feature in child_dirs(base):
            test_peer = ROOT / "test" / "features" / feature.name
            add_area(areas, feature.name, feature, test_peer)

    for name in ("app", "core", "shared", "common", "services", "data", "domain", "presentation"):
        add_area(areas, name, existing("lib", name), existing("test", name))

    # Node/Python/general layouts.
    for name in ("src", "app", "server", "client", "api", "tests", "test", "lib", "pkg", "internal"):
        add_area(areas, name, existing(name))

    # Monorepo layouts.
    for base in (existing("packages"), existing("apps")):
        if not base:
            continue
        for pkg in child_dirs(base):
            add_area(areas, pkg.name, pkg)

    return dict(list(areas.items())[:MAX_AREAS])


def render(areas: dict[str, set[str]]) -> str:
    lines = [
        "# Project Map",
        "",
        "Use this map before broad searches. Start with mapped folders and nearby tests.",
        "",
        "## Areas",
        "",
    ]
    if not areas:
        lines.append("No areas mapped yet.")
    else:
        for name, folders in sorted(areas.items()):
            folder_list = ", ".join(sorted(folders))
            terms = name.replace("-", ", ")
            lines += [
                f"- {name}",
                f"  - folders: {folder_list}",
                f"  - terms: {terms}",
                "  - notes: inferred; refine after first real task",
            ]
    lines += [
        "",
        "## Rules",
        "",
        "- Keep area names stable and lowercase.",
        "- Store folders, not exact file paths, unless one file is the whole area.",
        "- Prefer nearest stable parent folders.",
        "- Include test folders beside source folders when known.",
        "- If a folder is missing or stale, fall back to `rg` and update the map.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate starter project map.")
    parser.add_argument("--write", action="store_true", help="Write .agents/project-map.md. Default prints preview.")
    args = parser.parse_args()

    areas = detect_areas()
    content = render(areas)
    if args.write:
        try:
            MAP.parent.mkdir(parents=True, exist_ok=True)
            MAP.write_text(content, encoding="utf-8")
            print(f"updated: .agents/project-map.md areas={len(areas)}")
        except OSError:
            print("write blocked; apply this preview with apply_patch:")
            print(content[:4000])
            return 1
    else:
        print(f"preview: areas={len(areas)}")
        print(content[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
