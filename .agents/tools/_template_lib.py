#!/usr/bin/env python3
"""Shared helpers for the template sync/integrity tools.

Single source for the adapter map, frontmatter parsing, and the copy-relevance
filter used by both `sync_shared.py` and `check_template.py`, so the rules that
keep `.claude/` adapters in step with `.agents/` are defined exactly once.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Claude adapter (destination) -> canonical source under .agents/.
LINKS = {
    ".claude/skills": ".agents/skills",
    ".claude/agents": ".agents/subagents",
}

IGNORED_PARTS = {"__pycache__"}


def relevant(path: Path) -> bool:
    """True if path should participate in mirroring/comparison."""
    return not (set(path.parts) & IGNORED_PARTS) and path.suffix != ".pyc"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return ({name, description, ...}, body) from a `---` frontmatter doc.

    Only top-level scalar keys are captured; indented keys (e.g. under
    `metadata:`) and value-less keys are skipped.
    """
    if not text.startswith("---"):
        return {}, text.strip()
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text.strip()
    front_block = text[3:end]
    body = text[end + 4:].lstrip("\n").rstrip()
    front: dict[str, str] = {}
    for match in re.finditer(r"^([A-Za-z_]+):[ \t]*(.+?)[ \t]*$", front_block, re.MULTILINE):
        front[match.group(1)] = _unquote(match.group(2))
    return front, body


def _unquote(value: str) -> str:
    """Strip one matching pair of surrounding quotes from a scalar value.

    Frontmatter values are usually bare, but a quoted `name:`/`description:`
    would otherwise leak its quotes into the generated Codex TOML.
    """
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


# A detected stack also pulls in the stacks it builds on (Flutter ships Dart).
STACK_IMPLIES = {
    "flutter": {"dart"},
}


def expand_stacks(detected: set[str]) -> set[str]:
    """Add implied stacks (e.g. flutter -> dart) to a detected set."""
    stacks = set(detected)
    for stack in list(stacks):
        stacks |= STACK_IMPLIES.get(stack, set())
    return stacks


def skill_stack(skill_md: Path) -> str | None:
    """The `stack:` a skill is scoped to, or None if it is stack-agnostic."""
    front, _ = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="ignore"))
    return front.get("stack")


def gated_skill_names(skills_src: Path, detected: set[str]) -> set[str]:
    """Top-level skill dirs to exclude when syncing for the detected stacks.

    A skill is excluded only when it declares a `stack:` absent from the
    (expanded) detected set. Returns an empty set when nothing is detected or
    the stack is unknown, so the full skill set is always the safe default.
    Shared by sync and the integrity check so both gate identically.
    """
    if not detected or "unknown" in detected:
        return set()
    effective = expand_stacks(detected)
    excluded: set[str] = set()
    for skill_md in sorted(skills_src.glob("*/SKILL.md")):
        stack = skill_stack(skill_md)
        if stack is not None and stack not in effective:
            excluded.add(skill_md.parent.name)
    return excluded
