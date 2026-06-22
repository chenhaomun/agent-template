# Agent Template

Shared agent configuration for **Claude Code** and **OpenAI Codex**, designed to work simultaneously from the same project. **Flutter/Dart is the primary stack**; the core rules and workflow are language-agnostic. One copy of every skill and subagent lives in `.agents/`, and Claude reads the same files through symlinks — so both tools always have an identical set.

## What's Included

| File / Folder | Purpose |
|---|---|
| `AGENTS.md` | Single source of shared rules. Codex reads it directly |
| `CLAUDE.md` | Claude Code entry point — imports `AGENTS.md` via `@AGENTS.md`, adds Claude-only rules |
| `.claude/settings.json` | Claude Code project settings (model, permissions, **hooks**) |
| `.codex/hooks.json` | Codex project hooks using the shared enforcement scripts |
| `.codex/agents/` | Codex-native custom agent definitions matching shared subagent roles |
| `Makefile` | Canonical verify entrypoints — `make verify` / `make help` |
| `.claude/skills` → `.agents/skills` | Symlink so Claude sees every skill as `/<skill-name>` |
| `.claude/agents` → `.agents/subagents` | Symlink so Claude sees every subagent natively |
| `.claude/device-setup/` | Portable Claude **user** prefs (theme/model/behaviour) — `settings.example.json`, `install.py`. Not auto-loaded; applied per machine |
| `.codex/` | Portable Codex **device** setup — `config.example.toml`, `install.py`, optional pet. Not auto-loaded; applied per machine |
| `.agents/skills/` | **The** skill files (core + Flutter/Dart), read by both tools. Review/workflow skills also carry an `agents/openai.yaml` so Codex surfaces them as `$`-commands |
| `.agents/subagents/` | Subagent definitions with Claude frontmatter (BA, TL, Developer, DevOps, Security, QA, UX, Flutter, Backend API) |
| `.agents/flutter-dependencies.md` | Default Flutter package choices (bloc, go_router, dio) |
| `.agents/tools/` | Python helpers — project map, project detection, hook scripts, template integrity check |
| `.agents/project-map.md` | Folder map for fast code navigation |
| `skills-lock.json` | Dependency lock for all skill versions (core + Flutter/Dart) |
| `.gitignore` | Ignores `reports/`, `.DS_Store`, `.env.*.json` |

## How to Use This Template

### 1. Copy to your project

Copy these files into your project root:

```
AGENTS.md
CLAUDE.md
Makefile
.claude/
.codex/
.agents/
skills-lock.json
```

Copy `.claude/` and `.agents/` **together** — `.claude/skills` and `.claude/agents` are relative symlinks into `.agents/`. `git` and `cp -R` preserve them on macOS/Linux. (On Windows, enable Developer Mode or `git config core.symlinks true`, or replace the two links with copies.)

### 2. Stacks

**Flutter/Dart is the primary stack** — wired in by default (`## Flutter` rules in `AGENTS.md`, `flutter-*`/`dart-*` skills, `flutter-developer`/`backend-api-developer` subagents). For a Flutter project you're ready to go.

**TypeScript, Python, and other stacks are secondary** — the core rules, review skills, and subagent workflow are language-agnostic and work for them out of the box. When a secondary stack needs its own conventions, add a section to `AGENTS.md` (e.g. `## TypeScript`, `## Python`) and drop any stack-specific skills under `.agents/skills/your-skill/SKILL.md` — both tools pick them up automatically (Claude via the symlink, Codex directly).

**Update the project map** on first use:

```sh
python .agents/tools/generate_project_map.py
```

Then edit `.agents/project-map.md` to reflect actual ownership boundaries.

### 3. Agents read different files

| Agent | Entry point | Shared rules via |
|---|---|---|
| Claude Code | `CLAUDE.md` | `@AGENTS.md` import (auto-inlined by Claude Code) |
| OpenAI Codex | `AGENTS.md` | read directly |

Shared rules live in `AGENTS.md` only; `CLAUDE.md` imports them via `@AGENTS.md` and adds the Claude-only delta. (The files can't be merged: Claude Code reads only `CLAUDE.md`, Codex only `AGENTS.md`.)

**Skills and subagents have a single source** in `.agents/skills/` and `.agents/subagents/`. Codex reads them directly; Claude reads the same files through `.claude/skills` and `.claude/agents` symlinks. Add or edit once and both tools get it — no duplication, no sync step.

## Default Behaviour

- Replies default to **`$caveman lite`** mode (terse, no filler). Say "normal mode" to turn it off.
- Medium/large/risky work routes through the subagent workflow (see `.agents/skills/subagent-workflow/SKILL.md`).
- Commit messages are generated from staged changes using `.agents/skills/git-staged-commit-message/SKILL.md`.

## Verification & Hooks

Run `make verify` as the canonical gate. It checks template integrity and project-map freshness, runs shared tool tests, then analyzes/tests/format-checks Dart or Flutter when `pubspec.yaml` exists. `make help` lists all targets. Both agents prefer these over raw commands.

Claude Code and Codex enforce quality with deterministic project hooks. Claude configuration lives in `.claude/settings.json`; Codex configuration lives in `.codex/hooks.json`. Both call the same scripts:

| Hook | Script | Effect |
|---|---|---|
| PostToolUse | `hook_format_analyze.py` | Auto-formats + analyzes each edited `.dart` file; surfaces analyzer issues to the agent |
| PreToolUse | `hook_guard_generated.py` | Blocks edits to generated/vendored files (`*.g.dart`, `build/`, …) |
| SessionStart | `check_project_map.py` | Flags missing mapped folders and newly detected unmapped areas |

Format/analyze no-ops safely outside a Dart/Flutter project. Codex requires a trusted project and one-time review of new or changed hooks through `/hooks`; untrusted hooks are skipped. `AGENTS.md` remains the fallback contract when either client cannot run hooks.

## Skills Reference

| Skill | Trigger |
|---|---|
| `caveman` | `/caveman`, "less tokens", "be brief" |
| `caveman-compress` | Deterministic local text compression (scripted) |
| `grill-requirements` | Unclear scope, missing acceptance criteria |
| `production-code-review` | Medium+ review; `$caveman lite` output |
| `git-staged-commit-message` | "commit message", "commit this" |
| `subagent-workflow` | Multi-agent orchestration |
| `subagent-task-brief` | `/taskbrief`, split requirements for subagents |
| `architecture-review` | Boundaries, layers, contracts |
| `security-review` | Auth, secrets, privacy |
| `solid-oop-review` | Class design, coupling |
| `dry-review` | Duplicated rules or mappings |
| `kiss-review` | Over-engineering |
| `performance-review` | Rendering, async, memory |
| `test-driven-development` | Behavior-first implementation |
| `skill-maintenance` | Refresh/update skills from upstream |

Plus the bundled **Flutter/Dart** skills (11 `flutter-*` + 10 `dart-*`): widgets, tests, routing, l10n, responsive layout, JSON serialization, HTTP, coverage, mocks, static analysis, FFI, pattern matching. All tracked in `skills-lock.json` and refreshed by `skill-maintenance`.

## Subagents Reference

| Subagent | Role |
|---|---|
| `business-analyst` | Requirements, scope, user flows |
| `team-lead` | Architecture, task breakdown, final review |
| `developer` | Implementation, API, data layer, tests |
| `devops-release-engineer` | CI/CD, build, deploy, env |
| `security-privacy-reviewer` | Auth, secrets, privacy audit |
| `qa` | Functional verify, regression, release readiness |
| `ux-product-reviewer` | UX, accessibility, copy, states |
| `flutter-developer` | Flutter UI/state/routing/platform implementation |
| `backend-api-developer` | API/DTO/migration/contract implementation |

## Claude Code-Specific Features

- **Skills & subagents**: every skill in `.agents/skills/` is invocable as `/<skill-name>` (via the `.claude/skills` symlink); every subagent in `.agents/subagents/` is available to the Agent tool (via `.claude/agents`). No per-skill command files needed
- **Settings**: Edit `.claude/settings.json` to configure model, permissions, and MCP servers
- **Memory**: Claude Code reads `~/.claude/CLAUDE.md` for user-level preferences; project memory goes in `CLAUDE.md`
- **Device setup**: `.claude/device-setup/` carries portable *user* prefs (theme, model, behaviour, custom themes) across machines — the Claude counterpart to `.codex/`. Configure one device, then:

  ```sh
  python .claude/device-setup/install.py --capture   # snapshot this device's prefs into the template
  python .claude/device-setup/install.py --write      # apply them on another machine
  ```

  Merges only an allowlist of safe keys into `~/.claude/settings.json` (backed up first); never touches auth, env, permissions, or MCP paths. See `.claude/device-setup/README.md`.

## Codex-Specific Features

- **Skill commands**: Review/workflow skills include an `agents/openai.yaml` (`display_name`, `short_description`, `default_prompt`) so Codex surfaces them as `$`-commands. Add one to any skill you want Codex to expose.
- **Device setup**: `.codex/` holds portable, safe Codex preferences (model/personality, desktop theme, commit template, optional pet). It is **not** auto-loaded. On a new machine, preview then apply:

  ```sh
  python .codex/install.py --dry-run
  python .codex/install.py --write --install-pet
  ```

  The installer backs up `~/.codex/config.toml` before writing. It never syncs auth, sessions, logs, or local runtime paths. See `.codex/README.md`.
