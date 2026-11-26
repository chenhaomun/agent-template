# Project Context

## Purpose

Reusable agent-configuration template for projects that use Claude and Codex.

## Architecture

- `.agents/` is the source of truth for shared instructions, skills, subagents, tools, and checks.
- `.claude/` and `.codex/` are adapters generated or linked from that shared source.
- `.agents/Makefile` exposes portable sync and verification commands; the root Makefile only includes it for this template repository.
- `AGENTS.md` holds required behavior; `SECURITY.md` is installed as a managed block. Optional Codex/Claude memory stays small and non-duplicative.

## Ownership

- Source: `.agents/skills/` and `.agents/subagents/`. Adapters: `.claude/` and `.codex/`.
- Enforcement and maintenance: `.agents/tools/` with tests in `.agents/tests/`. Tooling uses Python 3.11+ without third-party packages.
- Command and SDK selection: `.agents/tools/run_checks.py`, with optional project-owned `.agents/project-commands.json`; hooks share this resolver.
- Install lifecycle: `.agents/tests/smoke_install.py`; Windows/Linux CI in `.github/workflows/verify.yml`.
- Provenance, adaptations, and content hashes for every skill: `skills-lock.json` (hashes written by sync, checked by `check-template`). Flutter skills follow each project's SDK, architecture, and tooling.
- Reviews: `production-code-review` is the only review skill.

## Feature Map

- Install/upgrade: `.agents/tools/install_template.py`
- Adapter sync: `.agents/tools/sync_shared.py`
- Credential, generated-file, and format hooks: `.agents/tools/hook_*.py`
- Independent-review gate (UserPromptSubmit/Stop hooks and record CLI): `.agents/tools/review_gate.py`
- Project context: `.agents/tools/generate_project_context.py`, `check_project_context.py`
- Dart/Flutter MCP server: `.mcp.json` (Claude) runs `.agents/tools/dart_mcp.py` with the project SDK; Codex entry in `.codex/config.example.toml`
- Device preferences: `.codex/install.py`, `.claude/device-setup/install.py`
- Story/task drafting, HTML visuals, and ClickUp creation: `draft-user-stories`; RCA: `root-cause-analyze` (shares the mobile sizing guide); app-flow tests: `flutter-add-integration-test`

## Commands

- `make -f .agents/Makefile verify` (or `python .agents/tools/run_checks.py verify`) checks template integrity, context freshness, and project checks.
- `python .agents/tests/smoke_install.py` checks preview, installation, sync, upgrades, and preservation using temporary projects.
- `make -f .agents/Makefile sync` refreshes adapters; `make -f .agents/Makefile context` updates the generated structure.

## Structural Map

<!-- BEGIN GENERATED STRUCTURE -->
### Generated Structure

- agent-runtime
  - folders: .agents/skills, .agents/subagents, .claude, .codex
- agent-tooling
  - folders: .agents/tests, .agents/tools

<!-- END GENERATED STRUCTURE -->
