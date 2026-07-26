#!/usr/bin/env python3
"""Local-only caveman compression for natural-language memory files."""

from __future__ import annotations

import re
from pathlib import Path

from .detect import should_compress
from .validate import validate

MAX_FILE_SIZE = 500_000

FENCE_REGEX = re.compile(r"^(\s{0,3})(`{3,}|~{3,})")
FRONTMATTER_REGEX = re.compile(r"\A(---\r?\n.*?\r?\n---\r?\n)(.*)", re.DOTALL)
INLINE_OR_URL_REGEX = re.compile(r"`[^`]+`|https?://[^\s)]+")

SENSITIVE_BASENAME_REGEX = re.compile(
    r"(?ix)^("
    r"\.env(\..+)?"
    r"|\.netrc"
    r"|credentials(\..+)?"
    r"|secrets?(\..+)?"
    r"|passwords?(\..+)?"
    r"|id_(rsa|dsa|ecdsa|ed25519)(\.pub)?"
    r"|authorized_keys"
    r"|known_hosts"
    r"|.*\.(pem|key|p12|pfx|crt|cer|jks|keystore|asc|gpg)"
    r")$"
)
SENSITIVE_PATH_COMPONENTS = frozenset({".ssh", ".aws", ".gnupg", ".kube", ".docker"})
SENSITIVE_NAME_TOKENS = (
    "secret",
    "credential",
    "password",
    "passwd",
    "apikey",
    "accesskey",
    "token",
    "privatekey",
)

PHRASE_REPLACEMENTS = (
    ("in order to", "to"),
    ("make sure to", "ensure"),
    ("the reason is because", "because"),
    ("it might be worth", ""),
    ("you could consider", ""),
    ("it would be good to", ""),
    ("you should always", ""),
    ("you should", ""),
    ("remember to", ""),
    ("happy to", ""),
    ("of course", ""),
    ("certainly", ""),
    ("basically", ""),
    ("actually", ""),
    ("essentially", ""),
    ("generally", ""),
    ("simply", ""),
    ("really", ""),
    ("just", ""),
    ("however", ""),
    ("furthermore", ""),
    ("additionally", ""),
    ("in addition", ""),
    ("utilize", "use"),
    ("utilizing", "using"),
    ("implementation", "impl"),
    ("approximately", "about"),
    ("extensive", "big"),
)


def split_frontmatter(text: str) -> tuple[str, str]:
    match = FRONTMATTER_REGEX.match(text)
    if match:
        return match.group(1), match.group(2)
    return "", text


def is_sensitive_path(filepath: Path) -> bool:
    name = filepath.name
    if SENSITIVE_BASENAME_REGEX.match(name):
        return True
    lowered_parts = {p.lower() for p in filepath.parts}
    if lowered_parts & SENSITIVE_PATH_COMPONENTS:
        return True
    lowered_name = re.sub(r"[_\-\s.]", "", name.lower())
    return any(token in lowered_name for token in SENSITIVE_NAME_TOKENS)


def _protect(text: str) -> tuple[str, list[str]]:
    protected: list[str] = []

    def replace(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"@@P{len(protected) - 1}@@"

    return INLINE_OR_URL_REGEX.sub(replace, text), protected


def _restore(text: str, protected: list[str]) -> str:
    for index, value in enumerate(protected):
        text = text.replace(f"@@P{index}@@", value)
    return text


def compress_line(line: str) -> str:
    if not line.strip() or line.lstrip().startswith("#"):
        return line

    prefix = line[: len(line) - len(line.lstrip())]
    body = line.lstrip()
    protected_body, protected = _protect(body)

    for old, new in PHRASE_REPLACEMENTS:
        protected_body = re.sub(rf"\b{re.escape(old)}\b", new, protected_body, flags=re.IGNORECASE)

    protected_body = re.sub(r"\b(a|an|the)\s+", "", protected_body, flags=re.IGNORECASE)
    protected_body = re.sub(r"\s+", " ", protected_body).strip()
    protected_body = re.sub(r"\s+([,.;:!?])", r"\1", protected_body)
    protected_body = _restore(protected_body, protected)

    return prefix + protected_body if protected_body else line


def compress_text(text: str) -> str:
    frontmatter, body = split_frontmatter(text)
    output: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in body.splitlines():
        fence = FENCE_REGEX.match(line)
        if fence:
            marker = fence.group(2)
            char = marker[0]
            length = len(marker)
            if not in_fence:
                in_fence = True
                fence_char = char
                fence_len = length
            elif char == fence_char and length >= fence_len:
                in_fence = False
            output.append(line)
            continue

        output.append(line if in_fence else compress_line(line))

    suffix = "\n" if text.endswith("\n") else ""
    return frontmatter + "\n".join(output) + suffix


def compress_file(filepath: Path) -> bool:
    filepath = filepath.resolve()
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if filepath.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large to compress safely (max 500KB): {filepath}")
    if is_sensitive_path(filepath):
        raise ValueError(f"Refusing to compress sensitive-looking file: {filepath}")

    print(f"Processing: {filepath}")
    if not should_compress(filepath):
        print("Skipping (not natural language)")
        return False

    original_text = filepath.read_text(encoding="utf-8", errors="ignore")
    if not original_text.strip():
        print("Refusing to compress: file is empty or whitespace-only.")
        return False

    backup_path = filepath.with_name(filepath.stem + ".original.md")
    if backup_path.exists():
        print(f"Backup file already exists: {backup_path}")
        print("Aborting to prevent data loss.")
        return False

    compressed = compress_text(original_text)
    if compressed.strip() == original_text.strip():
        print("Compression produced no change. Original file untouched.")
        return False

    backup_path.write_text(original_text, encoding="utf-8")
    if backup_path.read_text(encoding="utf-8", errors="ignore") != original_text:
        backup_path.unlink(missing_ok=True)
        print("Backup verification failed. Original file untouched.")
        return False

    filepath.write_text(compressed, encoding="utf-8")
    result = validate(backup_path, filepath)
    if result.is_valid:
        print("Validation passed")
        return True

    filepath.write_text(original_text, encoding="utf-8")
    backup_path.unlink(missing_ok=True)
    print("Validation failed; original restored")
    for error in result.errors:
        print(f"  - {error}")
    return False
