#!/usr/bin/env python3
"""Detect common project types with short output."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path.cwd()


def exists(*parts: str) -> bool:
    return (ROOT.joinpath(*parts)).exists()


def detect() -> list[str]:
    found: list[str] = []
    if exists("pubspec.yaml"):
        pubspec = ROOT.joinpath("pubspec.yaml").read_text(encoding="utf-8", errors="ignore")
        found.append("flutter" if "sdk: flutter" in pubspec or exists("lib") else "dart")
    if exists("package.json"):
        found.append("node")
    if any(exists(name) for name in ("pyproject.toml", "requirements.txt", "setup.py")):
        found.append("python")
    if exists("Cargo.toml"):
        found.append("rust")
    if exists("go.mod"):
        found.append("go")
    if exists("pom.xml") or exists("build.gradle") or exists("build.gradle.kts"):
        found.append("jvm")
    return found or ["unknown"]


def main() -> int:
    project_types = detect()
    markers = {
        "pubspec.yaml": exists("pubspec.yaml"),
        "package.json": exists("package.json"),
        "pyproject.toml": exists("pyproject.toml"),
        "requirements.txt": exists("requirements.txt"),
        "Cargo.toml": exists("Cargo.toml"),
        "go.mod": exists("go.mod"),
    }
    print(json.dumps({"project_types": project_types, "markers": markers}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
