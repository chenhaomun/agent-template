#!/usr/bin/env python3
"""Generate the agent adapters from the single source under `.agents/`.

Subagents and skills are authored once under `.agents/`; the per-tool adapters
are derived here, so nothing is hand-maintained twice:

- `.claude/skills`  <- copy of `.agents/skills`     (Claude loads skills here)
- `.claude/agents`  <- copy of `.agents/subagents`  (Claude loads subagents here)
- `.codex/agents/*.toml` <- generated from `.agents/subagents/*.md` frontmatter

Copies exist because Claude needs real directories at those paths; on Windows
(`core.symlinks=false`) git checks symlinks out as dead text files. The Codex
TOML is just the `.md` name/description plus its body, re-encoded.

Idempotent. A correctly-resolving symlink is left untouched. Run via
`make sync`; also runs at SessionStart so adapters self-heal. Pair with
`check_template.py`, which fails if any adapter has drifted from its source.
"""

from __future__ import annotations

import filecmp
import shutil
from pathlib import Path

from _template_lib import LINKS, ROOT, gated_skill_names, parse_frontmatter, relevant
from detect_project import detect

SUBAGENTS = ROOT / ".agents" / "subagents"
CODEX_AGENTS = ROOT / ".codex" / "agents"
SKILLS = ROOT / ".agents" / "skills"


def is_good_symlink(link: Path, target: Path) -> bool:
    return link.is_symlink() and link.exists() and link.resolve() == target.resolve()


def mirror(src: Path, dst: Path, exclude_top: set[str] = frozenset()) -> bool:
    """Copy src tree into dst, removing stale entries. Return True if changed.

    Top-level entries named in `exclude_top` are skipped (and pruned from dst
    if already present), which is how stack-gated skills stay out of the copy.
    """
    changed = False
    dst.mkdir(parents=True, exist_ok=True)

    wanted: set[Path] = set()
    for path in src.rglob("*"):
        if not relevant(path):
            continue
        rel = path.relative_to(src)
        if rel.parts[0] in exclude_top:
            continue
        wanted.add(rel)
        out = dst / rel
        if path.is_dir():
            if not out.is_dir():
                out.mkdir(parents=True, exist_ok=True)
                changed = True
        elif not out.exists() or not filecmp.cmp(path, out, shallow=False):
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out)
            changed = True

    # Remove anything in dst that no longer exists in src (deepest first).
    for path in sorted(dst.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if not relevant(path):
            continue
        if path.relative_to(dst) in wanted:
            continue
        if path.is_dir():
            if not any(path.iterdir()):
                path.rmdir()
                changed = True
        else:
            path.unlink()
            changed = True

    return changed


def toml_basic(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def toml_body(value: str) -> str:
    """Render an arbitrary subagent body as a TOML string.

    Prefer a readable multiline basic string; fall back to an escaped
    single-line basic string when the body contains the `\"\"\"` delimiter
    (which a multiline basic string cannot represent), so a body is never
    silently dropped from the generated adapter.
    """
    if '"""' not in value:
        return f'"""\n{value}"""'
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\t", "\\t")
        .replace("\n", "\\n")
    )
    return f'"{escaped}"'


def render_codex_toml(name: str, description: str, body: str) -> str:
    return (
        f"name = {toml_basic(name)}\n"
        f"description = {toml_basic(description)}\n"
        f"developer_instructions = {toml_body(body)}\n"
    )


def generate_codex_agents(actions: list[str]) -> None:
    """Regenerate .codex/agents/*.toml from .agents/subagents/*.md."""
    if not SUBAGENTS.is_dir():
        return
    CODEX_AGENTS.mkdir(parents=True, exist_ok=True)
    wanted: set[str] = set()
    for md in sorted(SUBAGENTS.glob("*.md")):
        front, body = parse_frontmatter(md.read_text(encoding="utf-8"))
        name, description = front.get("name"), front.get("description")
        if not name or not description:
            actions.append(f"skip {md.name}: missing name/description")
            continue
        out = CODEX_AGENTS / f"{name}.toml"
        wanted.add(out.name)
        content = render_codex_toml(name, description, body)
        if not out.exists() or out.read_text(encoding="utf-8") != content:
            out.write_text(content, encoding="utf-8")
            actions.append(f"generated .codex/agents/{out.name}")
    for toml in CODEX_AGENTS.glob("*.toml"):
        if toml.name not in wanted:
            toml.unlink()
            actions.append(f"removed stale .codex/agents/{toml.name}")


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def short_description(description: str, limit: int = 140) -> str:
    """First sentence of a skill description, capped for the $-command list."""
    text = " ".join(description.split())
    cut = text.find(". ")
    if cut != -1:
        text = text[: cut + 1]
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def generate_openai_adapters(actions: list[str]) -> None:
    """Create a default agents/openai.yaml for any skill that lacks one.

    Codex only surfaces a skill as a `$`-command when this adapter exists;
    generating missing ones keeps the Codex and Claude skill sets identical
    without hand-maintaining a second description. Curated adapters are never
    overwritten — only absent ones are filled in.
    """
    if not SKILLS.is_dir():
        return
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        out = skill_md.parent / "agents" / "openai.yaml"
        if out.exists():
            continue
        front, _ = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="ignore"))
        name = front.get("name") or skill_md.parent.name
        description = front.get("description")
        if not description:
            actions.append(f"skip openai.yaml for {name}: missing description")
            continue
        content = (
            f"display_name: {yaml_quote(name.replace('-', ' ').title())}\n"
            f"short_description: {yaml_quote(short_description(description))}\n"
            f"default_prompt: {yaml_quote(f'Use {name} for this task.')}\n"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        actions.append(f"generated .agents/skills/{skill_md.parent.name}/agents/openai.yaml")


def main() -> int:
    actions: list[str] = []
    generate_codex_agents(actions)
    generate_openai_adapters(actions)
    detected = set(detect())
    for link, target in LINKS.items():
        link_path = ROOT / link
        target_path = ROOT / target
        if not target_path.is_dir():
            print(f"skip {link}: source {target} is missing")
            continue
        if is_good_symlink(link_path, target_path):
            continue
        # Clear a dead symlink or a placeholder file occupying the path.
        if link_path.is_symlink() or (link_path.exists() and not link_path.is_dir()):
            link_path.unlink()
        # Only the skills adapter is stack-gated; subagents always mirror whole.
        exclude = gated_skill_names(target_path, detected) if target == ".agents/skills" else frozenset()
        if mirror(target_path, link_path, exclude):
            actions.append(f"synced {link} <- {target}")

    for action in actions:
        print(action)
    if not actions:
        print("shared directories already in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
