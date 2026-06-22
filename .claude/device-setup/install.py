from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

# Allowlist of portable, device-safe user-level keys. Anything not listed here is
# never written to or captured from ~/.claude/settings.json by this script.
# Deliberately excludes machine/account-specific keys: env, permissions, hooks,
# statusLine, apiKeyHelper, *AuthRefresh, awsCredentialExport, autoMemoryDirectory,
# fileSuggestion, otelHeadersHelper, defaultShell, and any MCP/provider paths.
PORTABLE_KEYS = {
    "theme",
    "model",
    "advisorModel",
    "editorMode",
    "outputStyle",
    "effortLevel",
    "autoUpdatesChannel",
    "language",
    "autoCompactEnabled",
    "autoMemoryEnabled",
    "prefersReducedMotion",
    "axScreenReader",
    "awaySummaryEnabled",
    "fileCheckpointingEnabled",
    "autoScrollEnabled",
    "agentPushNotifEnabled",
    "inputNeededNotifEnabled",
    "preferredNotifChannel",
    "remoteControlAtStartup",
    "includeCoAuthoredBy",
    "cleanupPeriodDays",
    "fastModePerSessionOptIn",
    "spinnerTips",
    "verbose",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc})")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def filtered(example: dict) -> tuple[dict, list[str]]:
    """Keep only allowlisted keys; report any that were dropped."""
    keep = {k: v for k, v in example.items() if k in PORTABLE_KEYS}
    dropped = sorted(k for k in example if k not in PORTABLE_KEYS)
    return keep, dropped


def copy_custom_themes(src_dir: Path, theme: str | None, dst_dir: Path) -> list[str]:
    """Copy a custom:<slug> theme file into ~/.claude/themes/ if present."""
    actions: list[str] = []
    if not theme or not theme.startswith("custom:"):
        return actions
    slug = theme.split(":", 1)[1]
    src = src_dir / f"{slug}.json"
    if not src.exists():
        actions.append(f"warn: theme '{theme}' set but {src} is missing")
        return actions
    dst = dst_dir / f"{slug}.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    actions.append(f"install theme: {dst}")
    return actions


def cmd_apply(args, here: Path, target: Path, themes_dst: Path) -> int:
    example = load_json(here / "settings.example.json")
    keep, dropped = filtered(example)
    current = load_json(target)

    merged = dict(current)
    changes: list[str] = []
    for k, v in keep.items():
        if current.get(k) != v:
            changes.append(f"{'update' if k in current else 'add'} {k} = {json.dumps(v)}")
        merged[k] = v

    print(f"target: {target}")
    print("mode: write" if args.write else "mode: dry-run")
    for c in changes or ["(no changes — already in sync)"]:
        print(f"- {c}")
    if dropped:
        print(f"- skipped non-portable keys in example: {', '.join(dropped)}")

    theme_actions = copy_custom_themes(here / "themes", keep.get("theme"), themes_dst)
    for a in theme_actions:
        print(f"- {a}" if not args.write else f"- (pending) {a}")

    if not args.write:
        print("no files changed")
        return 0

    if target.exists():
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup = target.with_name(f"settings.json.bak-{stamp}")
        shutil.copy2(target, backup)
        print(f"backup: {backup}")

    write_json(target, merged)
    print("settings written")
    # Re-run theme copy for real on write.
    for a in copy_custom_themes(here / "themes", keep.get("theme"), themes_dst):
        print(f"- {a}")
    return 0


def cmd_capture(here: Path, target: Path, themes_src: Path) -> int:
    """Snapshot the current device's portable settings back into the template."""
    current = load_json(target)
    if not current:
        raise SystemExit(f"error: {target} not found — configure Claude first (e.g. /theme, /config)")
    keep, _ = filtered(current)
    out = here / "settings.example.json"
    write_json(out, keep)
    print(f"captured {len(keep)} portable keys -> {out}")
    for k in sorted(keep):
        print(f"- {k} = {json.dumps(keep[k])}")

    # If a custom theme is active, copy its file into the template for portability.
    theme = keep.get("theme")
    if theme and theme.startswith("custom:"):
        slug = theme.split(":", 1)[1]
        src = themes_src / f"{slug}.json"
        if src.exists():
            dst = here / "themes" / f"{slug}.json"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"- captured theme: {dst}")
        else:
            print(f"- warn: theme '{theme}' active but {src} missing")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync portable Claude Code user settings between this template and ~/.claude."
    )
    parser.add_argument("--dry-run", action="store_true", help="preview the merge (default)")
    parser.add_argument("--write", action="store_true", help="write merged settings to ~/.claude/settings.json")
    parser.add_argument(
        "--capture",
        action="store_true",
        help="snapshot this device's portable settings INTO settings.example.json",
    )
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    claude_home = Path.home() / ".claude"
    target = claude_home / "settings.json"
    themes_dir = claude_home / "themes"

    if args.capture:
        return cmd_capture(here, target, themes_dir)
    return cmd_apply(args, here, target, themes_dir)


if __name__ == "__main__":
    raise SystemExit(main())
