from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


ROOT_KEYS = {"personality", "model", "model_reasoning_effort"}
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


def split_sections(text: str) -> tuple[list[str], dict[str, list[str]], list[str]]:
    root: list[str] = []
    sections: dict[str, list[str]] = {}
    order: list[str] = []
    current: str | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped.strip("[]")
            sections.setdefault(current, [])
            order.append(current)
            continue

        if current is None:
            root.append(line)
        else:
            sections[current].append(line)

    return root, sections, order


def key_of(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    return stripped.split("=", 1)[0].strip()


def section_keys(lines: list[str]) -> set[str]:
    return {key for line in lines if (key := key_of(line))}


def remove_keys(lines: list[str], keys: set[str]) -> list[str]:
    output: list[str] = []
    skip_multiline = False

    for line in lines:
        if skip_multiline:
            if '"""' in line:
                skip_multiline = False
            continue

        key = key_of(line)
        if key in keys:
            if '"""' in line and line.count('"""') == 1:
                skip_multiline = True
            continue

        output.append(line)

    return output


def merge_root(existing: list[str], example: list[str]) -> list[str]:
    example_by_key = {key_of(line): line for line in example if key_of(line) in ROOT_KEYS}
    output: list[str] = []
    used: set[str] = set()

    for line in existing:
        key = key_of(line)
        if key in example_by_key:
            output.append(example_by_key[key])
            used.add(key)
        else:
            output.append(line)

    for key in ROOT_KEYS - used:
        if key in example_by_key:
            output.append(example_by_key[key])

    return trim_blank_edges(output)


def trim_blank_edges(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def render(root: list[str], sections: dict[str, list[str]], order: list[str]) -> str:
    lines: list[str] = []
    lines.extend(trim_blank_edges(root.copy()))

    for name in order:
        body = trim_blank_edges(sections.get(name, []).copy())
        if lines:
            lines.append("")
        lines.append(f"[{name}]")
        lines.extend(body)

    return "\n".join(lines).rstrip() + "\n"


def merge_config(current: str, example: str) -> tuple[str, list[str]]:
    cur_root, cur_sections, cur_order = split_sections(current)
    ex_root, ex_sections, ex_order = split_sections(example)
    actions: list[str] = []

    merged_root = merge_root(cur_root, ex_root)
    merged_sections = dict(cur_sections)
    merged_order = list(cur_order)

    for name in ex_order:
        if name not in SECTIONS:
            continue
        ex_body = ex_sections.get(name, [])
        if not ex_body and name not in cur_sections:
            continue
        if name in merged_sections:
            existing_keys = section_keys(merged_sections[name])
            example_keys = section_keys(ex_body)
            merged_sections[name] = remove_keys(merged_sections[name], example_keys)
            merged_sections[name] = trim_blank_edges(ex_body.copy()) + merged_sections[name]
            changed = ", ".join(sorted(example_keys & existing_keys))
            actions.append(f"update [{name}]" + (f": {changed}" if changed else ""))
        else:
            merged_sections[name] = trim_blank_edges(ex_body.copy())
            merged_order.append(name)
            actions.append(f"add [{name}]")

    return render(merged_root, merged_sections, merged_order), actions


def copy_pet(repo_root: Path, codex_home: Path, force: bool) -> str:
    src = repo_root / ".codex" / "pets" / "codehound"
    dst = codex_home / "pets" / "codehound"
    if not src.exists():
        return "skip pet: .codex/pets/codehound missing"
    if dst.exists() and not force:
        return "skip pet: already installed; pass --force-pet to overwrite"
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    return f"install pet: {dst}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply shared Codex template settings.")
    parser.add_argument("--dry-run", action="store_true", help="preview changes without writing")
    parser.add_argument("--write", action="store_true", help="write changes to ~/.codex/config.toml")
    parser.add_argument("--install-pet", action="store_true", help="install .codex/pets/codehound")
    parser.add_argument("--force-pet", action="store_true", help="overwrite existing Codehound pet")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    example_path = repo_root / ".codex" / "config.example.toml"
    codex_home = Path.home() / ".codex"
    target = codex_home / "config.toml"

    example = example_path.read_text(encoding="utf-8")
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    merged, actions = merge_config(current, example)

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
