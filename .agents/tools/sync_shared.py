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
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# destination (Claude adapter) -> source (canonical)
LINKS = {
    ".claude/skills": ".agents/skills",
    ".claude/agents": ".agents/subagents",
}

SUBAGENTS = ROOT / ".agents" / "subagents"
CODEX_AGENTS = ROOT / ".codex" / "agents"

IGNORED_PARTS = {"__pycache__"}


def relevant(path: Path) -> bool:
    return not (set(path.parts) & IGNORED_PARTS) and path.suffix != ".pyc"


def is_good_symlink(link: Path, target: Path) -> bool:
    return link.is_symlink() and link.exists() and link.resolve() == target.resolve()


def mirror(src: Path, dst: Path) -> bool:
    """Copy src tree into dst, removing stale entries. Return True if changed."""
    changed = False
    dst.mkdir(parents=True, exist_ok=True)

    wanted: set[Path] = set()
    for path in src.rglob("*"):
        if not relevant(path):
            continue
        rel = path.relative_to(src)
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


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return ({name, description, ...}, body) from a `---` frontmatter doc."""
    if not text.startswith("---"):
        return {}, text.strip()
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text.strip()
    front_block = text[3:end]
    body = text[end + 4:].lstrip("\n").rstrip()
    front: dict[str, str] = {}
    for match in re.finditer(r"^([A-Za-z_]+):[ \t]*(.+?)[ \t]*$", front_block, re.MULTILINE):
        front[match.group(1)] = match.group(2)
    return front, body


def toml_basic(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_codex_toml(name: str, description: str, body: str) -> str:
    return (
        f"name = {toml_basic(name)}\n"
        f"description = {toml_basic(description)}\n"
        f'developer_instructions = """\n{body}"""\n'
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
        if not name or not description or '"""' in body:
            actions.append(f"skip {md.name}: missing name/description or unsafe body")
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


def main() -> int:
    actions: list[str] = []
    generate_codex_agents(actions)
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
        if mirror(target_path, link_path):
            actions.append(f"synced {link} <- {target}")

    for action in actions:
        print(action)
    if not actions:
        print("shared directories already in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
