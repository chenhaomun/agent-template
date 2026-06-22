# Shared Claude Code Device Setup

Portable, safe Claude Code **user-level** preferences for this template — the Claude counterpart to `.codex/`. Carry your appearance and behaviour across machines instead of reconfiguring each one.

It is **not** auto-loaded by Claude Code (only `settings.json` / `settings.local.json` are). Apply it explicitly:

```sh
python .claude/device-setup/install.py --dry-run          # preview
python .claude/device-setup/install.py --write            # apply to ~/.claude/settings.json
```

To snapshot the current machine's prefs back into the template (e.g. after you set your theme with `/theme`):

```sh
python .claude/device-setup/install.py --capture          # writes settings.example.json
```

Typical flow: configure one device → `--capture` → commit → `--write` on every other device.

## What it syncs

Only an allowlist of portable user keys from `settings.example.json`, merged into `~/.claude/settings.json` (existing unrelated keys are preserved):

- **Appearance:** `theme` (`auto` / `dark` / `light` / `*-daltonized` / `*-ansi`, or `custom:<slug>`), `prefersReducedMotion`, `axScreenReader`
- **Model / effort:** `model`, `advisorModel`, `effortLevel`, `outputStyle`, `editorMode`, `language`
- **Behaviour:** `autoUpdatesChannel`, `autoCompactEnabled`, `autoMemoryEnabled`, `includeCoAuthoredBy`, `cleanupPeriodDays`, `fileCheckpointingEnabled`, `awaySummaryEnabled`, `autoScrollEnabled`, `fastModePerSessionOptIn`, `spinnerTips`, `verbose`
- **Notifications:** `preferredNotifChannel`, `agentPushNotifEnabled`, `inputNeededNotifEnabled`, `remoteControlAtStartup`

**Custom themes:** drop the theme file in `.claude/device-setup/themes/<slug>.json` and set `"theme": "custom:<slug>"`. The installer copies it to `~/.claude/themes/`. `--capture` copies an active custom theme back.

## What it does NOT sync

Machine- or account-specific keys are never read or written: `env`, `permissions`, `hooks`, `statusLine`, `apiKeyHelper`, `*AuthRefresh`, `awsCredentialExport`, `autoMemoryDirectory`, `fileSuggestion`, `otelHeadersHelper`, `defaultShell`, and any MCP/provider paths. Auth, sessions, and project trust stay local.

The installer backs up `~/.claude/settings.json` (timestamped `.bak-*`) before writing.

> Note: project-scoped settings (model/permissions for *this repo*) live in `.claude/settings.json`. This folder is for *your* cross-device user preferences — a different scope.
