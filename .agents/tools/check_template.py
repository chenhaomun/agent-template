#!/usr/bin/env python3
"""Template integrity check.

Verifies the two pieces that silently break when the template is copied to a
new project (especially on Windows, where symlinks need extra setup):

1. `.claude/skills`  -> `.agents/skills`   (symlink, resolves)
2. `.claude/agents`  -> `.agents/subagents` (symlink, resolves)
3. every `.agents/subagents/*.md` has YAML frontmatter with name + description

Exit 0 = healthy, 1 = problem. Run via `make check-template`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 fallback; template already requires 3.10 syntax.
    tomllib = None

ROOT = Path(__file__).resolve().parents[2]

LINKS = {
    ".claude/skills": ".agents/skills",
    ".claude/agents": ".agents/subagents",
}


def directory_snapshot(root: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def check_shared_directories(errors: list[str]) -> None:
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
        if directory_snapshot(link_path) != directory_snapshot(target):
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
        end = text.find("\n---", 3)
        front = text[3:end] if end != -1 else ""
        if not re.search(r"^name:\s*\S+", front, re.MULTILINE):
            errors.append(f"{md.name}: frontmatter missing 'name:'")
        if not re.search(r"^description:\s*\S+", front, re.MULTILINE):
            errors.append(f"{md.name}: frontmatter missing 'description:'")
    return len(files)


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
    for path in codex_agents:
        try:
            text = path.read_text(encoding="utf-8")
            data = parse_agent_toml(text)
        except (OSError, ValueError) as error:
            errors.append(f"{path.name}: invalid TOML: {error}")
            continue
        for field in ("name", "description", "developer_instructions"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                errors.append(f"{path.name}: missing '{field}'")
        if isinstance(data.get("name"), str):
            codex_names.add(data["name"])
    if codex_names != shared_names or len(codex_agents) != expected_agents:
        errors.append(".codex/agents does not match .agents/subagents")


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
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"Makefile is missing: {error}")
        return
    verify_line = next((line for line in makefile.splitlines() if line.startswith("verify:")), "")
    for target in ("check-template", "check-map", "analyze", "test", "format-check", "tool-tests"):
        if target not in verify_line:
            errors.append(f"Makefile verify target missing dependency: {target}")


def main() -> int:
    errors: list[str] = []
    check_shared_directories(errors)
    count = check_subagents(errors)
    check_codex(errors, count)
    check_claude(errors)
    check_makefile(errors)

    if errors:
        print(f"FAIL template integrity ({len(errors)} issue(s)):")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"OK template integrity: shared directories resolve, {count} Claude/Codex agents valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
