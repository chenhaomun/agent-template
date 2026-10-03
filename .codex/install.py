from __future__ import annotations

import argparse
import shutil
import tomllib
from datetime import datetime
from pathlib import Path


ROOT_KEYS = {"personality", "model", "model_reasoning_effort", "model_context_window"}
SECTIONS = {
    "windows",
    "desktop",
    "desktop.appearanceDarkChromeTheme",
    "desktop.appearanceDarkChromeTheme.fonts",
    "desktop.appearanceDarkChromeTheme.semanticColors",
    "desktop.appearanceLightChromeTheme",
    "desktop.appearanceLightChromeTheme.fonts",
    "desktop.appearanceLightChromeTheme.semanticColors",
    "features",
}


def statements(text: str) -> list[str]:
    """Keep complete TOML values together, including multiline strings/arrays."""
    tomllib.loads(text)
    result: list[str] = []
    pending = ""
    for line in text.splitlines():
        pending += line + "\n"
        try:
            tomllib.loads(pending)
        except tomllib.TOMLDecodeError:
            continue
        result.append(pending.rstrip("\n"))
        pending = ""
    if pending:
        raise ValueError("cannot safely split TOML configuration")
    return result


def split_sections(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    root: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current = root
    for statement in statements(text):
        if statement.lstrip().startswith("["):
            current = []
            sections.append((statement, current))
        else:
            current.append(statement)
    return root, sections


def section_name(header: str) -> tuple[str, ...] | None:
    if header.lstrip().startswith("[["):
        return None
    value = tomllib.loads(header)
    parts: list[str] = []
    while isinstance(value, dict) and len(value) == 1:
        key, value = next(iter(value.items()))
        parts.append(key)
    return tuple(parts)


def key_of(statement: str) -> str | None:
    return next(iter(tomllib.loads(statement)), None)


def merge_values(existing: list[str], example: list[str], allowed: set[str] | None = None) -> list[str]:
    replacements = {
        key: statement for statement in example
        if (key := key_of(statement)) and (allowed is None or key in allowed)
    }
    output: list[str] = []
    for statement in existing:
        output.append(replacements.pop(key_of(statement), statement))
    output.extend(replacements.values())
    return trim_blank_edges(output)


def trim_blank_edges(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def render(root: list[str], sections: list[tuple[str, list[str]]]) -> str:
    lines: list[str] = []
    lines.extend(trim_blank_edges(root.copy()))

    for header, body in sections:
        if lines:
            lines.append("")
        lines.append(header)
        lines.extend(trim_blank_edges(body.copy()))

    return "\n".join(lines).rstrip() + "\n"


def merge_config(current: str, example: str) -> tuple[str, list[str]]:
    cur_root, cur_sections = split_sections(current)
    ex_root, ex_sections = split_sections(example)
    actions: list[str] = []

    merged_root = merge_values(cur_root, ex_root, ROOT_KEYS)
    merged_sections = list(cur_sections)
    allowed = {tuple(name.split(".")) for name in SECTIONS}
    for header, body in ex_sections:
        name = section_name(header)
        if name not in allowed:
            continue
        index = next((i for i, (old, _) in enumerate(merged_sections) if section_name(old) == name), None)
        if index is not None:
            old_header, old_body = merged_sections[index]
            merged_sections[index] = (old_header, merge_values(old_body, body))
            actions.append(f"update {header}")
        else:
            merged_sections.append((header, body))
            actions.append(f"add {header}")

    merged = render(merged_root, merged_sections)
    tomllib.loads(merged)
    return merged, actions


def copy_pet(repo_root: Path, codex_home: Path, force: bool) -> str:
    src = repo_root / ".codex" / "pets" / "codehound"
    dst = codex_home / "pets" / "codehound"
    if not src.exists():
        return "skip pet: .codex/pets/codehound missing"
    if (dst.exists() or dst.is_symlink()) and not force:
        return "skip pet: already installed; pass --force-pet to overwrite"
    if dst.exists() or dst.is_symlink():
        stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        dst.rename(dst.with_name(f"{dst.name}.bak-{stamp}"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    return f"install pet: {dst}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply shared Codex template settings.")
    parser.add_argument("--dry-run", action="store_true", help="preview changes without writing")
    parser.add_argument("--write", action="store_true", help="write changes to ~/.codex/config.toml")
    parser.add_argument("--install-pet", action="store_true", help="install .codex/pets/codehound")
    parser.add_argument("--force-pet", action="store_true", help="back up and replace existing Codehound pet")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    example_path = repo_root / ".codex" / "config.example.toml"
    codex_home = Path.home() / ".codex"
    target = codex_home / "config.toml"

    example = example_path.read_text(encoding="utf-8")
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    try:
        merged, actions = merge_config(current, example)
    except ValueError as error:
        parser.error(f"configuration was not changed: {error}")

    print(f"target: {target}")
    print("mode: write" if args.write else "mode: dry-run")
    for action in actions:
        print(f"- {action}")

    if args.install_pet:
        pet_action = "pending pet install"
        print(f"- {pet_action}")

    if not args.write:
        print("no files changed")
        return 0

    codex_home.mkdir(parents=True, exist_ok=True)
    if target.exists():
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup = target.with_name(f"config.toml.bak-{stamp}")
        shutil.copy2(target, backup)
        print(f"backup: {backup}")

    target.write_text(merged, encoding="utf-8")
    print("config written")

    if args.install_pet:
        print(copy_pet(repo_root, codex_home, args.force_pet))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
