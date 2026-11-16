#!/usr/bin/env python3
"""Block recognizable credential access before tool execution; not a sandbox."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from hook_payload import extract_file_paths


PATH_KEYS = {'file_path', 'path', 'paths', 'file_paths', 'filename', 'target_file', 'uri', 'url'}
COMMAND_KEYS = {'command', 'cmd', 'code', 'script'}
PRIVATE_DIRS = {'.ssh', '.aws', '.gnupg', '.azure', '.kube', 'keychains', 'secrets', 'credentials'}
PRIVATE_SUFFIXES = {'.pem', '.key', '.p8', '.p12', '.pfx', '.jks', '.keystore', '.mobileprovision'}
PRIVATE_NAMES = {'key.properties', 'credentials', 'credentials.json', 'auth.json',
                 '.netrc', '.npmrc', '.pypirc', '.git-credentials', 'id_rsa', 'id_ed25519'}
SECRET_COMMAND = re.compile(
    r'\b(printenv|secretsmanager|secretmanager)\b|'
    r'\bsecurity\s+(find|dump|export)|\b(?:vault|op)\s+(read|get|item)|'
    r'\bgcloud\s+(?:secrets|auth\s+print-)\b|\baz\s+keyvault\b|'
    r'\baws\s+ssm\s+get-parameter|\bgh\s+auth\s+token\b|'
    r'\$\{?\w*(?:TOKEN|SECRET|PASSWORD|PRIVATE_KEY)\w*|'
    r'\bos\.environ\b|\bprocess\.env\b|\bGet-ChildItem\s+Env:|'
    r'(?:^|[;&|]\s*)(?:env|set|export\s+-p)\s*(?:$|[;&|])', re.I,
)
TOKEN = re.compile(r"[^\s\"'`(){}\[\],;|<>]+")


def private_path(value: str, cwd: Path) -> bool:
    if value.startswith(('https://', 'http://')):
        return False
    if value.startswith('file://'):
        from urllib.parse import unquote, urlsplit
        value = unquote(urlsplit(value).path)
    value = value.replace('\\', '/')
    path = Path(value).expanduser()
    candidates = [path]
    try:
        candidates.append((cwd / path).resolve())
    except (OSError, RuntimeError):
        return True
    for candidate in candidates:
        parts = [part.lower() for part in candidate.parts]
        if PRIVATE_DIRS.intersection(parts):
            return True
        for name in parts:
            if name.startswith('.env') and name not in {'.env.example', '.env.sample', '.env.template'}:
                return True
            if name in PRIVATE_NAMES or Path(name).suffix in PRIVATE_SUFFIXES:
                return True
            if re.search(r'^(service[-_]?account|credentials?|secrets?)[-_.]', name):
                return True
    return False


def blocked_input(value, cwd: Path, key: str = '') -> bool:
    if isinstance(value, dict):
        workdir = value.get('workdir') or value.get('cwd')
        if isinstance(workdir, str):
            cwd = cwd / workdir
        return any(blocked_input(item, cwd, name) for name, item in value.items())
    if isinstance(value, list):
        return any(blocked_input(item, cwd, key) for item in value)
    if not isinstance(value, str):
        return False
    if key in PATH_KEYS:
        return private_path(value, cwd)
    if key not in COMMAND_KEYS:
        return False
    if value.startswith('*** Begin Patch'):
        return any(private_path(str(path), cwd) for path in extract_file_paths({'tool_input': value}))
    if SECRET_COMMAND.search(value):
        return True
    # Inspect literal paths only; never open a target or echo command contents.
    for token in TOKEN.findall(value):
        if token.startswith('!'):
            continue
        token = token.split('=', 1)[-1]
        if private_path(token, cwd):
            return True
        if ':' in token and private_path(token.rsplit(':', 1)[-1], cwd):
            return True
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict) or 'tool_input' not in payload:
            raise ValueError('invalid payload')
        cwd = Path(payload.get('cwd') or Path.cwd())
        value = payload['tool_input']
        if isinstance(value, str):
            value = {'command': value}
        if not isinstance(value, dict) or blocked_input(value, cwd):
            raise ValueError('protected input')
    except (ValueError, TypeError, OSError, RuntimeError):
        sys.stderr.write('Blocked by SECURITY.md: credential access or unreadable guard input. '
                         'Use source code, example schemas, or sanitized evidence.\n')
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
