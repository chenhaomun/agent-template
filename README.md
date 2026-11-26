# Agent Template

Lean shared configuration for Claude Code and OpenAI Codex. Flutter/Dart support is included; project-specific rules and existing files remain intact. Requires Python 3.11+ and no third-party packages.

## Structure

- `AGENTS.md`: shared runtime rules. `CLAUDE.md` imports them and adds Claude-only behavior. `SECURITY.md`: mandatory security policy.
- `.agents/project-context.md`: purpose, architecture, ownership, feature map, commands, and generated structure.
- `.agents/skills/` and `.agents/subagents/`: canonical skills and roles (`team-lead`, `developer`, `economy-executor`, `qa`, `reviewer`).
- `.agents/tools/` and `.agents/tests/`: installer, adapter sync, hooks, context and integrity checks, and their tests.
- `.agents/Makefile`: portable targets that never own a project's root Makefile.
- `.claude/skills`, `.claude/agents`: relative symlinks to canonical sources. `.codex/agents/`: generated TOML.
- `skills-lock.json`: provenance and content hashes for every skill (hashes written by sync, checked in the template repository).

All upstream Flutter and Dart skills are vendored in adapted form and stack-gated, so they install only into matching projects.

## Install into an existing project

Never copy this repository over another project. Preview, then write:

```sh
python .agents/tools/install_template.py /path/to/project
python .agents/tools/install_template.py /path/to/project --write
```

The installer appends or refreshes marked blocks in existing `AGENTS.md`, `CLAUDE.md`, and `SECURITY.md`; merges missing hooks (and, for Claude, the review-gate `record` allow rules) into Claude/Codex settings; leaves an existing `Makefile` untouched; backs up changed instruction and settings files; records hashes so unchanged template-owned files upgrade safely; and aborts when a user-modified owned file or unowned same-name path would be overwritten.

It rejects symlinks in copied sources and adapter destinations and excludes caches, backups, private `.env` files, and `settings.local.json` (`.env.example` stays). New project context is generated from the destination structure with placeholders; existing context stays project-owned. Use `--copy-adapters` without symlink support; Windows selects copy mode automatically.

Template rules cannot outrank system instructions, and Codex lets instructions closer to the working directory override root guidance. The managed block is placed after existing root text.

## Commands

This repository uses `make sync`, `make context`, and `make verify`. Other projects keep their own Makefile and call:

```sh
make -f .agents/Makefile sync
make -f .agents/Makefile verify
python .agents/tools/run_checks.py verify   # without make
```

The Makefile uses `python`; set `PYTHON=python3` if needed. CI verifies Windows and Linux, plus install/upgrade smoke checks for copied and symlinked adapters.

Configure project commands in the project-owned `.agents/project-commands.json`. Values are argument arrays, never shell strings; set only needed keys:

```json
{
  "dart": ["fvm", "dart"],
  "flutter": ["fvm", "flutter"],
  "analyze": ["python", "scripts/check.py", "analyze"],
  "test": ["python", "scripts/check.py", "test"]
}
```

`format` and `format-check` also accept full overrides. SDK overrides apply to hooks and verification. Otherwise checks use a cached `.fvm/flutter_sdk`, then global Dart/Flutter when no FVM pin exists. A missing pinned SDK is reported, never downloaded or replaced by a global version. Nested packages inherit the nearest configuration and run from their own directory.

## Dart and Flutter tool server

`.mcp.json` registers the Dart and Flutter MCP server (`dart mcp-server`, bundled with the Dart SDK) for Claude Code. `.agents/tools/dart_mcp.py` starts it with the same SDK verification uses: `project-commands.json`, then the cached FVM SDK, then `dart` on PATH. It uses the repository-root pin; for a pin that lives only in a nested package, set `dart` in `project-commands.json`. Claude asks once to approve project MCP servers. The launcher runs `python3`, which Windows machines must provide. The installer adds the `dart` server to an existing `.mcp.json`, refreshes it on upgrade only while unchanged, and never replaces a project-edited same-name server.

Codex reads MCP servers from user config; `python .codex/install.py --write` adds `[mcp_servers.dart]` only when missing. It uses `dart` on PATH rather than a project's pinned SDK. On SDKs without `mcp-server` the server does not start, and agents fall back to normal commands.

## Project context

Purpose, architecture, ownership, feature map, and commands are hand-maintained. The feature map gives agents shared names for user-facing features and where they live. Only the marked structure block is generated:

```sh
python .agents/tools/generate_project_context.py          # preview
python .agents/tools/generate_project_context.py --write
```

`check_project_context.py` fails when detected folders drift. Session start checks freshness but never writes.

## Skills and subagents

Edit only `.agents/skills/` and `.agents/subagents/`, then run `make -f .agents/Makefile sync`. Sync rejects same-name custom Codex roles instead of overwriting them and migrates legacy skill display fields under `interface`.

Before delivering file changes, agents get an independent review from the read-only `reviewer` subagent and fix findings internally; `review_gate.py` hooks (UserPromptSubmit and Stop) keep the turn going until that review is recorded. The installer also adds the `review_gate.py record` allow rules to installed projects' Claude settings, so recording never prompts. The gate is a strong nudge, not proof: an agent can record a review it did not run, and sessions sharing one worktree see each other's edits. Other subagents run only when requested; routing, the delegation brief, and done criteria live in `AGENTS.md`. Chat uses `caveman` at **full** by default, with **ultra** for interim progress notes (`normal mode` or `off` opts out); saved artifacts keep normal prose. Personal response-format preferences belong in user-level files (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`), not in this shared template.

Notable project-local skills:

- `draft-user-stories`: one Markdown file of user stories under an Epic, or tasks under an Enhancement (never stories), from FRS and screenshots; creates ClickUp items only after approval, and builds an HTML visual only on request.
- `root-cause-analyze`: brief RCA with category, sprint points, and verified introducing commit.
- `production-code-review`: the single review skill, covering correctness, architecture, quality, performance, and security. `Review {branch name}; ticket: {ticket URL}.` returns severity-ranked problems with `file:line` and fix direction, plus a sprint-point estimate when the ticket has none.

`skill-maintenance` (on request only) compares upstream changes, preserves local adaptations, and records reviewed commits in `skills-lock.json`. Restart active agents if changed skill metadata does not refresh.

## Device setup

Optional user-level preferences, never auto-loaded. Preview first:

```sh
python .codex/install.py --dry-run
python .claude/device-setup/install.py --dry-run
```

See `.codex/README.md` and `.claude/device-setup/README.md`. Installers merge allowlisted keys, validate the result, and back up existing config; they never copy auth, sessions, trust, or local provider paths.

## Memory and security

Required behavior stays in checked-in instructions; Claude/Codex auto-memory is optional recall and must hold no secrets. Read `SECURITY.md` before tools. Hooks block recognizable credential access without reading contents, but they are not a sandbox: keep production credentials outside agent access and enforce host restrictions.
