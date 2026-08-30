#!/usr/bin/env python3
"""Safely apply this agent template to another repository.

Preview is the default.  ``--write`` only adds canonical entries that are
absent, appends managed instruction blocks, and adds missing template hooks.
It never removes target files or replaces an unowned path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[2]
MANAGED_NAME = "agent-template"
INSTRUCTION_FILES = {
    "AGENTS.md": SOURCE_ROOT / "AGENTS.md",
    "CLAUDE.md": SOURCE_ROOT / "CLAUDE.md",
}
COPY_ENTRIES = (
    ".agents/Makefile",
    ".agents/skills",
    ".agents/subagents",
    ".agents/tests",
    ".agents/tools",
    ".claude/device-setup",
    ".codex/README.md",
    ".codex/agents",
    ".codex/config.example.toml",
    ".codex/install.py",
    "skills-lock.json",
)
SEED_IF_ABSENT = (".agents/project-context.md",)
MANIFEST_RELATIVE = ".agents/.template-manifest.json"
ADAPTERS = {
    ".claude/agents": ".agents/subagents",
    ".claude/skills": ".agents/skills",
}
HOOK_FILES = {
    ".claude/settings.json": SOURCE_ROOT / ".claude/settings.json",
    ".codex/hooks.json": SOURCE_ROOT / ".codex/hooks.json",
}


class InstallConflict(RuntimeError):
    """The target contains a path that this installer does not own."""


HASH = re.compile(r"^[0-9a-f]{64}$")
OWNED_PREFIXES = (".agents/", ".claude/device-setup/", ".codex/agents/")
OWNED_EXACT = {
    ".codex/README.md",
    ".codex/config.example.toml",
    ".codex/install.py",
    "skills-lock.json",
}


def safe_relative(value: object, *, adapter: bool = False) -> str:
    if not isinstance(value, str) or not value:
        raise InstallConflict("invalid manifest path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise InstallConflict(f"unsafe manifest path: {value}")
    allowed = value.startswith((".claude/agents/", ".claude/skills/")) if adapter else (
        value in OWNED_EXACT or value.startswith(OWNED_PREFIXES)
    )
    if not allowed or value == MANIFEST_RELATIVE:
        raise InstallConflict(f"unowned manifest path: {value}")
    return value


def safe_target(root: Path, relative: str) -> Path:
    target = root / relative
    if not target.resolve(strict=False).is_relative_to(root):
        raise InstallConflict(f"target path escapes project: {relative}")
    return target


def marker(name: str, end: bool = False) -> str:
    side = "END" if end else "BEGIN"
    return f"<!-- {side} {MANAGED_NAME}:{name} -->"


def managed_block(name: str, source: Path) -> str:
    body = source.read_text(encoding="utf-8").strip()
    return f"{marker(name)}\n{body}\n{marker(name, end=True)}\n"


def replace_block(current: str, name: str, block: str) -> str:
    """Append or replace one clearly-owned block without touching other text."""
    start, end = marker(name), marker(name, end=True)
    start_at, end_at = current.find(start), current.find(end)
    if (start_at == -1) != (end_at == -1) or (start_at != -1 and end_at < start_at):
        raise InstallConflict(f"malformed managed block in {name}")
    if start_at == -1:
        prefix = "" if not current.strip() else current.rstrip() + "\n\n"
        return prefix + block
    outside = current[:start_at] + current[end_at + len(end) :]
    prefix = "" if not outside.strip() else outside.rstrip() + "\n\n"
    return prefix + block


def load_object(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise InstallConflict(f"invalid JSON: {path}: {error}") from error
    if not isinstance(data, dict):
        raise InstallConflict(f"JSON root must be an object: {path}")
    return data


def merge_hooks(current: dict, template: dict, previous: list[dict]) -> tuple[dict, list[dict]]:
    """Replace prior template hooks while retaining unknown target hooks."""
    result = dict(current)
    target_hooks = current.get("hooks", {})
    template_hooks = template.get("hooks", {})
    if not isinstance(target_hooks, dict) or not isinstance(template_hooks, dict):
        raise InstallConflict("hooks must be a JSON object")
    merged_hooks = dict(target_hooks)
    for entry in previous:
        event, hook = entry.get("event"), entry.get("hook")
        hooks = merged_hooks.get(event, [])
        if isinstance(event, str) and isinstance(hooks, list) and hook in hooks:
            hooks = list(hooks)
            hooks.remove(hook)
            merged_hooks[event] = hooks
    next_entries: list[dict] = []
    for event, additions in template_hooks.items():
        if not isinstance(additions, list):
            raise InstallConflict(f"template hooks.{event} must be a list")
        existing = list(merged_hooks.get(event, []))
        if not isinstance(existing, list):
            raise InstallConflict(f"hooks.{event} must be a list")
        for item in additions:
            if item not in existing:
                existing.append(item)
            next_entries.append({"event": event, "hook": item})
        merged_hooks[event] = existing
    result["hooks"] = merged_hooks
    return result, next_entries


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def template_files(source_root: Path) -> dict[str, Path]:
    """Return canonical template files, excluding caches and directories."""
    files: dict[str, Path] = {}
    for relative in COPY_ENTRIES:
        source = source_root / relative
        if not source.exists():
            continue
        if source.is_file():
            files[relative] = source
            continue
        for child in source.rglob("*"):
            if child.is_file() and "__pycache__" not in child.parts and child.suffix != ".pyc":
                files[child.relative_to(source_root).as_posix()] = child
    return files


def source_version(files: dict[str, Path]) -> str:
    digest = hashlib.sha256()
    for relative, path in sorted(files.items()):
        digest.update(relative.encode())
        digest.update(file_hash(path).encode())
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"files": {}, "adapters": {}}
    data = load_object(path)
    files, adapters, hooks = data.get("files", {}), data.get("adapters", {}), data.get("hooks", {})
    if not isinstance(files, dict) or not isinstance(adapters, dict) or not isinstance(hooks, dict):
        raise InstallConflict(f"invalid manifest: {path}")
    for relative, digest in files.items():
        safe_relative(relative)
        if not isinstance(digest, str) or not HASH.fullmatch(digest):
            raise InstallConflict("invalid manifest file hash")
    for relative, digest in adapters.items():
        safe_relative(relative, adapter=True)
        if not isinstance(digest, str) or not HASH.fullmatch(digest):
            raise InstallConflict("invalid manifest adapter hash")
    if any(relative not in HOOK_FILES for relative in hooks):
        raise InstallConflict("invalid manifest hook path")
    return data


def plan_canonical_files(
    source_files: dict[str, Path], target_root: Path, manifest: dict[str, object]
) -> list[tuple[Path, Path]]:
    """Plan safe creates/upgrades; only prior manifest hashes authorize overwrites."""
    planned: list[tuple[Path, Path]] = []
    old_files = manifest.get("files", {})
    assert isinstance(old_files, dict)
    for relative, source in source_files.items():
        target = safe_target(target_root, relative)
        new_hash = file_hash(source)
        if not target.exists():
            planned.append((source, target))
            continue
        if not target.is_file():
            raise InstallConflict(f"unowned conflict: {relative}")
        current_hash = file_hash(target)
        if current_hash == new_hash:
            continue
        previous_hash = old_files.get(relative)
        if previous_hash == current_hash:
            planned.append((source, target))
            continue
        raise InstallConflict(f"unowned conflict: {relative}")
    return planned


def plan_stale_files(old_files: dict, source_files: dict[str, Path], target_root: Path) -> list[Path]:
    """Plan removal of template files deleted upstream, never project edits."""
    stale: list[Path] = []
    for relative, previous_hash in old_files.items():
        if relative in source_files:
            continue
        if not isinstance(relative, str) or not isinstance(previous_hash, str):
            raise InstallConflict("invalid manifest file entry")
        relative = safe_relative(relative)
        target = safe_target(target_root, relative)
        if not target.exists():
            continue
        if not target.is_file() or file_hash(target) != previous_hash:
            raise InstallConflict(f"unowned conflict: {relative}")
        stale.append(target)
    return stale


def effective_files(
    root: Path, updates: list[tuple[Path, Path]], deletes: list[Path]
) -> dict[Path, Path]:
    """Files a target directory will contain after planned canonical updates."""
    files = {path.relative_to(root): path for path in root.rglob("*") if path.is_file()} if root.is_dir() else {}
    for source, target in updates:
        try:
            relative = target.relative_to(root)
        except ValueError:
            continue
        files[relative] = source
    for target in deletes:
        try:
            files.pop(target.relative_to(root))
        except ValueError:
            continue
    return files


def remove_owned_file(path: Path, root: Path) -> None:
    path.unlink()
    parent = path.parent
    while parent != root and parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()
        parent = parent.parent


def backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    result = path.with_name(f"{path.name}.bak-{stamp}")
    shutil.copy2(path, result)
    return result


def install(source_root: Path, target_root: Path, *, write: bool, copy_adapters: bool) -> list[str]:
    """Install into ``target_root`` and return a human-readable action list."""
    source_root, target_root = source_root.resolve(), target_root.resolve()
    if source_root == target_root:
        raise InstallConflict("target must not be the template source directory")
    if not target_root.is_dir():
        raise InstallConflict(f"target directory does not exist: {target_root}")
    manifest_path = target_root / MANIFEST_RELATIVE
    manifest = load_manifest(manifest_path)
    source_files = template_files(source_root)
    canonical_updates = plan_canonical_files(source_files, target_root, manifest)
    old_files = manifest.get("files", {})
    assert isinstance(old_files, dict)
    canonical_deletes = plan_stale_files(old_files, source_files, target_root)
    old_adapters = manifest.get("adapters", {})
    assert isinstance(old_adapters, dict)

    changes: list[str] = []
    instruction_updates: dict[Path, str] = {}
    for name, source in INSTRUCTION_FILES.items():
        source = source_root / source.relative_to(SOURCE_ROOT)
        target = target_root / name
        before = target.read_text(encoding="utf-8") if target.exists() else ""
        after = replace_block(before, name.lower(), managed_block(name.lower(), source))
        if after != before:
            instruction_updates[target] = after
            changes.append(f"merge managed block: {name}")

    hook_updates: dict[Path, dict] = {}
    next_hook_entries: dict[str, list[dict]] = {}
    old_hooks = manifest.get("hooks", {})
    if not isinstance(old_hooks, dict):
        raise InstallConflict("invalid manifest hooks")
    for relative, source in HOOK_FILES.items():
        source = source_root / source.relative_to(SOURCE_ROOT)
        target = target_root / relative
        before = load_object(target) if target.exists() else {}
        previous = old_hooks.get(relative, [])
        if not isinstance(previous, list) or not all(isinstance(entry, dict) for entry in previous):
            raise InstallConflict(f"invalid manifest hooks: {relative}")
        after, next_entries = merge_hooks(before, load_object(source), previous)
        next_hook_entries[relative] = next_entries
        if after != before:
            hook_updates[target] = after
            changes.append(f"merge template hooks: {relative}")

    for source, target in canonical_updates:
        relative = target.relative_to(target_root).as_posix()
        changes.append(f"install: {relative}" if not target.exists() else f"upgrade: {relative}")
    for target in canonical_deletes:
        changes.append(f"remove stale: {target.relative_to(target_root).as_posix()}")
    adapter_updates: list[tuple[Path, Path]] = []
    adapter_deletes: list[Path] = []
    adapter_files: dict[str, dict[Path, Path]] = {}
    adapter_symlinks: set[str] = set()
    for adapter, target_rel in ADAPTERS.items():
        adapter_path, adapter_source = target_root / adapter, target_root / target_rel
        expected = effective_files(adapter_source, canonical_updates, canonical_deletes)
        adapter_files[adapter] = expected
        if not adapter_path.exists() and not adapter_path.is_symlink():
            mode = "copy" if copy_adapters else "symlink"
            changes.append(f"{mode} adapter: {adapter} -> {target_rel}")
            if copy_adapters:
                adapter_updates.extend((source, adapter_path / relative) for relative, source in expected.items())
            else:
                adapter_symlinks.add(adapter)
        elif adapter_path.is_symlink() and adapter_path.resolve() != adapter_source.resolve():
            raise InstallConflict(f"unowned conflict: {adapter}")
        elif adapter_path.is_symlink():
            adapter_symlinks.add(adapter)
        elif not adapter_path.is_symlink() and not adapter_path.is_dir():
            raise InstallConflict(f"unowned conflict: {adapter}")
        elif not adapter_path.is_symlink():
            for relative, source in expected.items():
                destination = adapter_path / relative
                if not destination.exists():
                    adapter_updates.append((source, destination))
                    continue
                if not destination.is_file():
                    raise InstallConflict(f"unowned conflict: {adapter}/{relative}")
                if file_hash(destination) == file_hash(source):
                    continue
                previous_hash = old_adapters.get(f"{adapter}/{relative.as_posix()}")
                if previous_hash == file_hash(destination):
                    adapter_updates.append((source, destination))
                    continue
                raise InstallConflict(f"unowned conflict: {adapter}/{relative}")
            prefix = f"{adapter}/"
            expected_keys = {prefix + relative.as_posix() for relative in expected}
            for key, previous_hash in old_adapters.items():
                if not isinstance(key, str) or not key.startswith(prefix) or key in expected_keys:
                    continue
                if not isinstance(previous_hash, str):
                    raise InstallConflict("invalid manifest adapter entry")
                safe_relative(key, adapter=True)
                stale = safe_target(target_root, key)
                if not stale.exists():
                    continue
                if not stale.is_file() or file_hash(stale) != previous_hash:
                    raise InstallConflict(f"unowned conflict: {key}")
                adapter_deletes.append(stale)

    next_adapter_hashes = {
        f"{adapter}/{relative.as_posix()}": file_hash(source)
        for adapter, files in adapter_files.items()
        if adapter not in adapter_symlinks
        for relative, source in files.items()
    }
    next_manifest = {
        "format": 1,
        "source_version": source_version(source_files),
        "files": {relative: file_hash(path) for relative, path in sorted(source_files.items())},
        "adapters": dict(sorted(next_adapter_hashes.items())),
        "hooks": next_hook_entries,
    }
    if manifest != next_manifest:
        changes.append(f"update manifest: {MANIFEST_RELATIVE}")

    seeds = [
        (source_root / relative, safe_target(target_root, relative))
        for relative in SEED_IF_ABSENT
        if (source_root / relative).is_file() and not (target_root / relative).exists()
    ]
    changes.extend(f"seed: {target.relative_to(target_root).as_posix()}" for _, target in seeds)

    if not write:
        return changes

    for target, content in instruction_updates.items():
        if target.exists():
            backup_path = backup(target)
            changes.append(f"backup: {backup_path.relative_to(target_root)}")
        target.write_text(content, encoding="utf-8")
    for target, data in hook_updates.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup_path = backup(target)
            changes.append(f"backup: {backup_path.relative_to(target_root)}")
        target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    for source, target in canonical_updates:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for source, target in seeds:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for target in canonical_deletes:
        remove_owned_file(target, target_root)
    for adapter, target_rel in ADAPTERS.items():
        path, destination = target_root / adapter, target_root / target_rel
        if path.exists() or path.is_symlink():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if copy_adapters:
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.symlink_to(os.path.relpath(destination, path.parent), target_is_directory=True)
    for source, destination in adapter_updates:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    for destination in adapter_deletes:
        remove_owned_file(destination, target_root)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(next_manifest, indent=2) + "\n", encoding="utf-8")
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preview or safely install this agent template.")
    parser.add_argument("target", type=Path, help="existing project directory")
    parser.add_argument("--write", action="store_true", help="apply the previewed changes")
    parser.add_argument("--copy-adapters", action="store_true", help="copy Claude adapters instead of symlinking")
    args = parser.parse_args(argv)
    copy_adapters = args.copy_adapters or sys.platform.startswith("win")
    try:
        actions = install(SOURCE_ROOT, args.target, write=args.write, copy_adapters=copy_adapters)
    except InstallConflict as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("mode: write" if args.write else "mode: preview")
    for action in actions or ["already installed"]:
        print(f"- {action}")
    if not args.write:
        print("no files changed; rerun with --write to apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
