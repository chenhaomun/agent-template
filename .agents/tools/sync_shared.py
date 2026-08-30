#!/usr/bin/env python3
"""Generate tool adapters from canonical sources under `.agents/`.

Subagents and skills are authored once under `.agents/`; the per-tool adapters
are derived here, so nothing is hand-maintained twice:

- `.claude/skills`  -> `.agents/skills`
- `.claude/agents`  -> `.agents/subagents`
- `.codex/agents/*.toml` <- generated from `.agents/subagents/*.md` frontmatter

Committed relative symlinks remove duplicate content. When Git cannot create
symlinks (commonly Windows), this tool replaces the dead placeholder with a
stack-gated copy. Codex TOML re-encodes each canonical subagent definition.

Idempotent. A correctly-resolving symlink is left untouched. Run with
`make -f .agents/Makefile sync`; `check_template.py` reports adapter drift.
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
    """Copy canonical entries into dst without deleting project-owned files.

    Top-level entries named in `exclude_top` are skipped (and pruned from dst
    if already present), which is how stack-gated skills stay out of the copy.
    """
    changed = False
    dst.mkdir(parents=True, exist_ok=True)

    for path in src.rglob("*"):
        if not relevant(path):
            continue
        rel = path.relative_to(src)
        if rel.parts[0] in exclude_top:
            continue
        out = dst / rel
        if path.is_dir():
            if not out.is_dir():
                out.mkdir(parents=True, exist_ok=True)
                changed = True
        elif not out.exists() or not filecmp.cmp(path, out, shallow=False):
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out)
            changed = True

    return changed


# Claude capability tier (subagent frontmatter `model:`) -> Codex model + effort.
# The source of truth stays the vendor-neutral tier; this table is the only place
# the concrete Codex model strings live, so a model rename is a one-line change.
# Mirrors the Claude tiers: opus=strongest (planning), sonnet=standard, haiku=economy.
CODEX_TIER: dict[str, tuple[str, str]] = {
    "opus": ("gpt-5.6-sol", "high"),
    "sonnet": ("gpt-5.6-terra", "medium"),
    "haiku": ("gpt-5.6-luna", "low"),
}
GENERATED_HEADER = "# Generated from .agents/subagents; edit the source Markdown."


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


def render_codex_toml(
    name: str,
    description: str,
    body: str,
    model: str | None = None,
    effort: str | None = None,
) -> str:
    lines = [
        GENERATED_HEADER,
        f"name = {toml_basic(name)}",
        f"description = {toml_basic(description)}",
    ]
    if model:
        lines.append(f"model = {toml_basic(model)}")
    if effort:
        lines.append(f"model_reasoning_effort = {toml_basic(effort)}")
    lines.append(f"developer_instructions = {toml_body(body)}")
    return "\n".join(lines) + "\n"


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
        # Map the vendor-neutral Claude tier to a Codex model + effort; unknown
        # or absent tiers emit nothing and inherit the session default.
        model, effort = CODEX_TIER.get(front.get("model", ""), (None, None))
        out = CODEX_AGENTS / f"{name}.toml"
        wanted.add(out.name)
        content = render_codex_toml(name, description, body, model, effort)
        if not out.exists() or out.read_text(encoding="utf-8") != content:
            out.write_text(content, encoding="utf-8")
            actions.append(f"generated .codex/agents/{out.name}")
    for toml in CODEX_AGENTS.glob("*.toml"):
        if toml.name not in wanted and toml.read_text(encoding="utf-8").startswith(GENERATED_HEADER):
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
