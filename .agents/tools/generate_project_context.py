#!/usr/bin/env python3
"""Preview or update the generated structure in .agents/project-context.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTEXT_PATH = ROOT / ".agents" / "project-context.md"
BEGIN = "<!-- BEGIN GENERATED STRUCTURE -->"
END = "<!-- END GENERATED STRUCTURE -->"
MAX_AREAS = 40
IGNORED = {"build", ".dart_tool", "node_modules", "__pycache__", ".git", "dist", ".next", "target"}


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def directory(root: Path, *parts: str) -> Path | None:
    path = root.joinpath(*parts)
    return path if path.is_dir() else None


def child_dirs(path: Path) -> list[Path]:
    return sorted(child for child in path.iterdir() if child.is_dir() and child.name not in IGNORED)


def add_area(areas: dict[str, set[str]], root: Path, name: str, *folders: Path | None) -> None:
    valid = {relative(root, folder) for folder in folders if folder is not None and folder.is_dir()}
    if valid:
        areas.setdefault(name.replace("_", "-").lower(), set()).update(valid)


def detect_areas(root: Path) -> dict[str, set[str]]:
    areas: dict[str, set[str]] = {}
    add_area(
        areas,
        root,
        "agent-runtime",
        directory(root, ".agents", "skills"),
        directory(root, ".agents", "subagents"),
        directory(root, ".claude"),
        directory(root, ".codex"),
    )
    add_area(
        areas,
        root,
        "agent-tooling",
        directory(root, ".agents", "tools"),
        directory(root, ".agents", "tests"),
    )
    for base in (directory(root, "lib", "features"), directory(root, "test", "features")):
        if base is None:
            continue
        for feature in child_dirs(base):
            add_area(areas, root, feature.name, feature, root / "test" / "features" / feature.name)

    for name in ("app", "core", "shared", "common", "services", "data", "domain", "presentation"):
        add_area(areas, root, name, directory(root, "lib", name), directory(root, "test", name))
    for name in ("src", "app", "server", "client", "api", "tests", "test", "lib", "pkg", "internal"):
        add_area(areas, root, name, directory(root, name))
    for base in (directory(root, "packages"), directory(root, "apps")):
        if base is not None:
            for package in child_dirs(base):
                add_area(areas, root, package.name, package)
    return dict(list(areas.items())[:MAX_AREAS])


def render_structure(areas: dict[str, set[str]]) -> str:
    lines = [BEGIN, "### Generated Structure", ""]
    if not areas:
        lines.append("No detected folders yet.")
    else:
        for name, folders in sorted(areas.items()):
            lines += [f"- {name}", f"  - folders: {', '.join(sorted(folders))}"]
    lines += ["", END]
    return "\n".join(lines)


def starter_document(structure: str) -> str:
    return """# Project Context

## Purpose

Reusable agent-configuration template for projects that use Claude and Codex.

## Architecture

- `.agents/` is the source of truth for shared instructions, skills, subagents, tools, and checks.
- `.claude/` and `.codex/` are adapters generated or linked from that shared source.
- `.agents/Makefile` exposes portable sync and verification commands; a project root Makefile remains project-owned.

## Ownership

- Source: `.agents/skills/` and `.agents/subagents/`.
- Adapters: `.claude/` and `.codex/`.
- Enforcement and maintenance: `.agents/tools/` with tests in `.agents/tests/`.

## Commands

- `make -f .agents/Makefile verify` checks template integrity, context freshness, and project checks.
- `make -f .agents/Makefile sync` refreshes adapters after shared source changes.
- `make -f .agents/Makefile context` updates the generated structure.

## Structural Map

""" + structure + "\n"


def replace_structure(document: str, structure: str) -> str:
    pattern = re.compile(rf"{re.escape(BEGIN)}.*?{re.escape(END)}", re.DOTALL)
    if not pattern.search(document):
        raise ValueError("project-context is missing generated structure markers")
    return pattern.sub(structure, document, count=1)


def render_document(root: Path) -> str:
    structure = render_structure(detect_areas(root))
    path = root / ".agents" / "project-context.md"
    if not path.exists():
        return starter_document(structure)
    return replace_structure(path.read_text(encoding="utf-8"), structure)


def write_document(root: Path) -> bool:
    path = root / ".agents" / "project-context.md"
    content = render_document(root)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Update generated project-context structure.")
    parser.add_argument("--write", action="store_true", help="Write only the generated structure block.")
    args = parser.parse_args()
    if args.write:
        changed = write_document(ROOT)
        print(f"{'updated' if changed else 'current'}: .agents/project-context.md")
    else:
        print(render_document(ROOT), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
