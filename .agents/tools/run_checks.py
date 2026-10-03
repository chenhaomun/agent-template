#!/usr/bin/env python3
"""Portable verification and project SDK selection without shell command strings."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT_TASKS = ("analyze", "test", "format", "format-check")
VERIFY_TASKS = ("check-template", "check-context", "analyze", "test", "format-check", "tool-tests")
OUTPUT_CAP = 4000


def project_roots(root: Path):
    for parent in (root, *root.parents):
        yield parent
        if (parent / ".git").exists():
            break


def configuration(root: Path) -> tuple[dict[str, list[str]], Path]:
    for parent in project_roots(root):
        path = parent / ".agents/project-commands.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or set(data) - {*PROJECT_TASKS, "dart", "flutter"}:
            raise ValueError(f"invalid project command keys: {path}")
        for key, command in data.items():
            if not isinstance(command, list) or not command or not all(
                isinstance(argument, str) and argument for argument in command
            ):
                raise ValueError(f"{path}: {key} must be a nonempty array of command arguments")
        return data, parent
    return {}, root


def resolve_command(command: list[str], root: Path) -> list[str]:
    local = root / command[0]
    executable = str(local) if local.is_file() else shutil.which(command[0])
    if not executable:
        raise FileNotFoundError(f"required command is unavailable: {command[0]}")
    return [executable, *command[1:]]


def sdk_command(root: Path, tool: str) -> list[str]:
    config, config_root = configuration(root)
    if tool in config:
        return resolve_command(config[tool], config_root)
    for parent in project_roots(root):
        executable = parent / ".fvm/flutter_sdk/bin" / (tool + (".bat" if os.name == "nt" else ""))
        if executable.is_file():
            return [str(executable)]
        if (parent / ".fvmrc").exists() or (parent / ".fvm/fvm_config.json").exists():
            raise FileNotFoundError(
                f"FVM SDK missing at {executable}; complete the project's pinned SDK setup"
            )
    return resolve_command([tool], root)


def project_command(root: Path, task: str) -> list[str] | None:
    config, config_root = configuration(root)
    if task in config:
        return resolve_command(config[task], config_root)
    pubspec = root / "pubspec.yaml"
    if not pubspec.is_file():
        return None
    flutter = re.search(r"(?m)^\s*sdk:\s*['\"]?flutter['\"]?\s*(?:#.*)?$", pubspec.read_text(encoding="utf-8"))
    if task in {"analyze", "test"}:
        return [*sdk_command(root, "flutter" if flutter else "dart"), task]
    arguments = ["format"]
    if task == "format-check":
        arguments += ["--output=none", "--set-exit-if-changed"]
    return [*sdk_command(root, "dart"), *arguments, "."]


def run_task(root: Path, task: str) -> int:
    if task in PROJECT_TASKS:
        command = project_command(root, task)
        if command is None:
            print(f"SKIP {task}: no pubspec.yaml or configured project command")
            return 0
    elif task == "tool-tests":
        command = [sys.executable, "-m", "unittest", "discover", "-s", ".agents/tests", "-p", "test_*.py"]
    else:
        script = {"check-template": "check_template.py", "check-context": "check_project_context.py"}[task]
        command = [sys.executable, str(root / ".agents/tools" / script)]
    result = subprocess.run(
        command, cwd=root, capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output[:OUTPUT_CAP] + ("\n... (truncated)" if len(output) > OUTPUT_CAP else ""))
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=("verify", *VERIFY_TASKS, "format"), nargs="?", default="verify")
    args = parser.parse_args()
    try:
        for task in VERIFY_TASKS if args.task == "verify" else (args.task,):
            result = run_task(ROOT, task)
            if result:
                return result
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
