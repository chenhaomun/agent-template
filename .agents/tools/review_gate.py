#!/usr/bin/env python3
"""Independent-review gate: keep the main agent working until its file changes are reviewed.

Hook modes read a Claude Code or Codex payload on stdin:
  turn-start  (UserPromptSubmit) snapshot the working tree before the agent acts
  stop        (Stop) block finishing while the agent changed files that have no
              recorded review; at most MAX_BLOCKS per turn so a turn is never trapped
Agents run `record clean|accepted|skip|pending --note ...` after or during review.
Fingerprints use paths, sizes, and mtimes only, so no file contents are read.
State lives under the Git directory, so the working tree stays clean.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

MAX_BLOCKS = 3
PENDING_SECONDS = 3600
STALE_SECONDS = 7 * 24 * 3600
REASON = (
    "Independent review required: you changed files that have no recorded review. "
    "Run the `reviewer` subagent in a fresh context with only the request, acceptance criteria or ticket, "
    "changed paths, and checks run. If it runs in the background, first run "
    "`python3 .agents/tools/review_gate.py record pending`. Fix valid findings, re-verify, and re-review after "
    "substantive fixes (two rounds max). Then run `python3 .agents/tools/review_gate.py record clean`, "
    '`record accepted --note "<unfixed finding and why>"`, or, for trivial edits only, '
    '`record skip --note "<why>"`. Keep the review exchange out of your reply.'
)


def git(cwd: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout if result.returncode == 0 else None


def state_dir(cwd: Path) -> Path | None:
    git_dir = git(cwd, "rev-parse", "--absolute-git-dir")
    return Path(git_dir.strip()) / "agent-review" if git_dir else None


def fingerprint(cwd: Path) -> str | None:
    """Fingerprint changed paths by status and file metadata; 'clean' when nothing differs from HEAD."""
    top = git(cwd, "rev-parse", "--show-toplevel")
    status = git(cwd, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if top is None or status is None:
        return None
    root = Path(top.strip())
    entries: list[tuple[str, str]] = []
    items = iter(status.split("\0"))
    for item in items:
        if len(item) < 4:
            continue
        code, path = item[:2], item[3:]
        if "R" in code or "C" in code:
            next(items, None)
        entries.append((code, path))
    if not entries:
        return "clean"
    digest = hashlib.sha256()
    for code, path in sorted(entries):
        try:
            info = (root / path).lstat()
            meta = f"{info.st_size}:{info.st_mtime_ns}"
        except OSError:
            meta = "-"
        digest.update(f"{code}\0{path}\0{meta}\n".encode())
    return digest.hexdigest()


def session_file(directory: Path, payload: dict) -> Path:
    session = re.sub(r"[^A-Za-z0-9_-]", "", str(payload.get("session_id") or "default"))[:80]
    return directory / f"session-{session or 'default'}.json"


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def read_payload() -> dict:
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def payload_cwd(payload: dict) -> Path:
    cwd = payload.get("cwd")
    return Path(cwd) if isinstance(cwd, str) and Path(cwd).is_dir() else Path.cwd()


def turn_start(payload: dict) -> int:
    cwd = payload_cwd(payload)
    directory, current = state_dir(cwd), fingerprint(cwd)
    if directory is None or current is None:
        return 0
    if directory.is_dir():
        cutoff = time.time() - STALE_SECONDS
        for old in directory.glob("session-*.json"):
            if old.stat().st_mtime < cutoff:
                old.unlink(missing_ok=True)
    path = session_file(directory, payload)
    state = load(path)
    if state.get("open") and current != state.get("turn_start"):
        state["needs_review"] = True
    state.update(turn_start=current, open=True, blocks=0)
    save(path, state)
    return 0


def is_reviewed(directory: Path, current: str) -> bool:
    review = load(directory / "reviewed.json")
    if review.get("fingerprint") != current:
        return False
    if review.get("result") == "pending":
        return time.time() - review.get("at", 0) < PENDING_SECONDS
    return True


def stop(payload: dict) -> int:
    cwd = payload_cwd(payload)
    directory, current = state_dir(cwd), fingerprint(cwd)
    if directory is None or current is None:
        return 0
    path = session_file(directory, payload)
    state = load(path)
    if "turn_start" not in state:
        save(path, {"turn_start": current})
        return 0
    if current != state["turn_start"]:
        state["needs_review"] = True
    if not state.get("needs_review") or current == "clean" or is_reviewed(directory, current):
        save(path, {"turn_start": current})
        return 0
    blocks = state.get("blocks", 0) if isinstance(state.get("blocks"), int) else 0
    if blocks >= MAX_BLOCKS:
        state["open"] = False
        save(path, state)
        print(json.dumps({"systemMessage": "Review gate stopped blocking; these changes are unreviewed."}))
        return 0
    state["blocks"] = blocks + 1
    save(path, state)
    print(json.dumps({"decision": "block", "reason": REASON}))
    return 0


def record(result: str, note: str) -> int:
    cwd = Path.cwd()
    directory, current = state_dir(cwd), fingerprint(cwd)
    if directory is None or current is None:
        print("not a Git repository; nothing recorded", file=sys.stderr)
        return 1
    if result in {"accepted", "skip"} and not note.strip():
        print(f"`record {result}` needs --note", file=sys.stderr)
        return 1
    try:
        save(directory / "reviewed.json", {"fingerprint": current, "result": result, "note": note, "at": int(time.time())})
    except OSError as error:
        print(f"cannot write review state under {directory} ({error.strerror}); report the review outcome in your reply", file=sys.stderr)
        return 1
    print(f"recorded {result} review for the current working tree")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Independent-review gate for agent turns.")
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("turn-start")
    sub.add_parser("stop")
    rec = sub.add_parser("record")
    rec.add_argument("result", choices=("clean", "accepted", "skip", "pending"))
    rec.add_argument("--note", default="")
    args = parser.parse_args(argv)
    if args.mode == "record":
        return record(args.result, args.note)
    payload = read_payload()
    return turn_start(payload) if args.mode == "turn-start" else stop(payload)


if __name__ == "__main__":
    raise SystemExit(main())
