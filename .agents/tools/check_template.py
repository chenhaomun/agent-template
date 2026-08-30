#!/usr/bin/env python3
"""Template integrity check.

Verifies the two pieces that silently break when the template is copied to a
new project (especially on Windows, where symlinks need extra setup):

1. `.claude/skills`  mirrors `.agents/skills`    (resolving symlink, or in-sync copy)
2. `.claude/agents`  mirrors `.agents/subagents` (resolving symlink, or in-sync copy)
3. every `.agents/subagents/*.md` has YAML frontmatter with name + description

A copy that has drifted from its source fails the check; run `make sync`.

Exit 0 = healthy, 1 = problem. Run via `make check-template`.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from _template_lib import LINKS, ROOT, gated_skill_names, parse_frontmatter, relevant
from detect_project import detect
from sync_shared import CODEX_TIER, GENERATED_HEADER, render_codex_toml

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 fallback; template already requires 3.10 syntax.
    tomllib = None


def directory_snapshot(root: Path, exclude_top: set[str] = frozenset()) -> dict[Path, str]:
    """Map each relevant file to a content hash for cheap tree comparison.

    Top-level entries named in `exclude_top` are omitted, matching the
    stack-gated skills that sync deliberately leaves out of the copy.
    """
    snapshot: dict[Path, str] = {}
    for path in root.rglob("*"):
        if not (path.is_file() and relevant(path)):
            continue
        rel = path.relative_to(root)
        if rel.parts[0] in exclude_top:
            continue
        snapshot[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def check_shared_directories(errors: list[str]) -> None:
    detected = set(detect())
    for link, expected_target in LINKS.items():
        link_path = ROOT / link
        target = (ROOT / expected_target).resolve()
        if link_path.is_symlink():
            if not link_path.resolve().exists():
                errors.append(f"{link} -> {link_path.readlink()} does not resolve")
            elif link_path.resolve() != target:
                errors.append(f"{link} points to {link_path.resolve()}, expected {target}")
            continue
        if not link_path.is_dir():
            errors.append(f"{link} is missing")
            continue
        # Copies may also contain project-owned entries; canonical entries must match.
        exclude = gated_skill_names(target, detected) if expected_target == ".agents/skills" else frozenset()
        actual = directory_snapshot(link_path)
        expected = directory_snapshot(target, exclude)
        if any(actual.get(relative) != digest for relative, digest in expected.items()):
            errors.append(f"{link} copy has drifted from {expected_target}")


def check_subagents(errors: list[str]) -> int:
    subagents_dir = ROOT / ".agents" / "subagents"
    if not subagents_dir.is_dir():
        errors.append(".agents/subagents/ is missing")
        return 0

    files = sorted(subagents_dir.glob("*.md"))
    for md in files:
        text = md.read_text(encoding="utf-8", errors="ignore")
        if not text.startswith("---"):
            errors.append(f"{md.name}: missing YAML frontmatter")
            continue
        front, _ = parse_frontmatter(text)
        if not front.get("name"):
            errors.append(f"{md.name}: frontmatter missing 'name:'")
        if not front.get("description"):
            errors.append(f"{md.name}: frontmatter missing 'description:'")
    return len(files)


def check_skills(errors: list[str]) -> int:
    """Validate active skill frontmatter plus Codex adapters.

    A SKILL.md with a missing/mismatched name or missing description silently
    fails to load (Claude) or mis-surfaces (Codex), so fail loudly here.
    """
    count = 0
    active = ROOT / ".agents" / "skills"
    for skill_dir in sorted(p for p in active.iterdir() if p.is_dir()):
        md = skill_dir / "SKILL.md"
        rel = f".agents/skills/{skill_dir.name}"
        if not md.is_file():
            if any(path.is_file() for path in skill_dir.rglob("*")):
                errors.append(f"{rel}: missing SKILL.md")
            continue
        count += 1
        front, _ = parse_frontmatter(md.read_text(encoding="utf-8", errors="ignore"))
        if front.get("name") != skill_dir.name:
            errors.append(f"{rel}: frontmatter name {front.get('name')!r} != directory name")
        if not front.get("description"):
            errors.append(f"{rel}: frontmatter missing 'description:'")
        if not (skill_dir / "agents" / "openai.yaml").is_file():
            errors.append(f"{rel}: missing agents/openai.yaml (run make sync)")
    return count


def check_skills_lock(errors: list[str]) -> None:
    """Lock entries must point at real files."""
    lock_path = ROOT / "skills-lock.json"
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))["skills"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(f"skills-lock.json is invalid: {error}")
        return
    for name, entry in lock.items():
        local = entry.get("localPath", ".agents/" + entry.get("skillPath", ""))
        if not (ROOT / local).is_file():
            errors.append(f"skills-lock.json: {name} points at missing file {local}")


def parse_agent_toml(text: str) -> dict[str, object]:
    if tomllib is not None:
        return tomllib.loads(text)
    data: dict[str, object] = {}
    for field in ("name", "description"):
        if match := re.search(rf'^\s*{field}\s*=\s*"([^"]*)"', text, re.MULTILINE):
            data[field] = match.group(1)
    if match := re.search(
        r'^\s*developer_instructions\s*=\s*"""(.*?)"""',
        text,
        re.MULTILINE | re.DOTALL,
    ):
        data["developer_instructions"] = match.group(1)
    elif match := re.search(
        r'^\s*developer_instructions\s*=\s*"((?:[^"\\]|\\.)*)"',
        text,
        re.MULTILINE,
    ):
        data["developer_instructions"] = match.group(1)
    return data


def check_codex(errors: list[str], expected_agents: int) -> None:
    hooks_path = ROOT / ".codex" / "hooks.json"
    try:
        hooks_text = hooks_path.read_text(encoding="utf-8")
        hooks = json.loads(hooks_text)["hooks"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(f".codex/hooks.json is invalid: {error}")
        hooks_text = ""
        hooks = {}

    for event in ("PreToolUse", "PostToolUse", "SessionStart"):
        if event not in hooks:
            errors.append(f".codex/hooks.json missing {event}")
    if "CLAUDE_PROJECT_DIR" in hooks_text:
        errors.append(".codex/hooks.json uses Claude-only CLAUDE_PROJECT_DIR")

    codex_agents = sorted((ROOT / ".codex" / "agents").glob("*.toml"))
    shared_names = {path.stem for path in (ROOT / ".agents" / "subagents").glob("*.md")}
    codex_names: set[str] = set()
    generated_count = 0
    for path in codex_agents:
        try:
            text = path.read_text(encoding="utf-8")
            if not text.startswith(GENERATED_HEADER):
                continue
            generated_count += 1
            data = parse_agent_toml(text)
        except (OSError, ValueError) as error:
            errors.append(f"{path.name}: invalid TOML: {error}")
            continue
        for field in ("name", "description", "developer_instructions"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                errors.append(f"{path.name}: missing '{field}'")
        if isinstance(data.get("name"), str):
            codex_names.add(data["name"])
    if codex_names != shared_names or generated_count != expected_agents:
        errors.append(".codex/agents does not match .agents/subagents")
    for source in sorted((ROOT / ".agents" / "subagents").glob("*.md")):
        front, body = parse_frontmatter(source.read_text(encoding="utf-8"))
        model, effort = CODEX_TIER.get(front.get("model", ""), (None, None))
        expected = render_codex_toml(front["name"], front["description"], body, model, effort)
        adapter = ROOT / ".codex" / "agents" / f"{front['name']}.toml"
        if adapter.is_file() and adapter.read_text(encoding="utf-8") != expected:
            errors.append(f"{adapter.name} has drifted from .agents/subagents/{source.name}")


def check_claude(errors: list[str]) -> None:
    settings_path = ROOT / ".claude" / "settings.json"
    try:
        hooks = json.loads(settings_path.read_text(encoding="utf-8"))["hooks"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(f".claude/settings.json hooks are invalid: {error}")
        return
    for event in ("PreToolUse", "PostToolUse", "SessionStart"):
        if event not in hooks:
            errors.append(f".claude/settings.json missing {event}")


def check_makefile(errors: list[str]) -> None:
    try:
        makefile = (ROOT / ".agents" / "Makefile").read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f".agents/Makefile is missing: {error}")
        return
    verify_line = next((line for line in makefile.splitlines() if line.startswith("verify:")), "")
    for target in ("check-template", "check-context", "analyze", "test", "format-check", "tool-tests"):
        if target not in verify_line:
            errors.append(f"Makefile verify target missing dependency: {target}")


def main() -> int:
    errors: list[str] = []
    check_shared_directories(errors)
    count = check_subagents(errors)
    skill_count = check_skills(errors)
    check_skills_lock(errors)
    check_codex(errors, count)
    check_claude(errors)
    check_makefile(errors)

    if errors:
        print(f"FAIL template integrity ({len(errors)} issue(s)):")
        for err in errors:
            print(f"- {err}")
        return 1

    print(
        f"OK template integrity: shared directories resolve, "
        f"{count} Claude/Codex agents and {skill_count} skills valid"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
