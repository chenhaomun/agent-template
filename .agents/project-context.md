# Project Context

## Purpose

Reusable agent-configuration template for projects that use Claude and Codex.

## Architecture

- `.agents/` is the source of truth for shared instructions, skills, subagents, tools, and checks.
- `.claude/` and `.codex/` are adapters generated or linked from that shared source.
- `.agents/Makefile` exposes portable sync and verification commands; the root Makefile only includes it for this template repository.
- `AGENTS.md` holds required behavior; optional Codex/Claude memory stays small and non-duplicative.

## Ownership

Flutter skills follow project-specific SDK, architecture, and tooling. Local adaptations and reviewed upstream revisions are recorded in `skills-lock.json`.

- Source: `.agents/skills/` and `.agents/subagents/`.
- Adapters: `.claude/` and `.codex/`.
- Enforcement and maintenance: `.agents/tools/` with tests in `.agents/tests/`.
- Project command and SDK selection: `.agents/tools/run_checks.py`; optional project-owned overrides in `.agents/project-commands.json`. Hooks share this resolver and report missing pinned SDKs.
- Installation lifecycle coverage: `.agents/tests/smoke_install.py`; Windows/Linux verification in `.github/workflows/verify.yml`. Tooling uses Python 3.11+ without third-party packages.
- Security policy: `SECURITY.md`.
- Story drafting/approved ClickUp creation: `draft-user-stories`; scoped HTML infographics: `visual-explainer`. Both are project-local skills.
- Review skills share the concise output contract in `.agents/skills/production-code-review/references/findings.md`.
- Flutter app-flow test authoring: `flutter-add-integration-test`; default triggers and setup authorization live in `AGENTS.md`.

## Commands

- `make -f .agents/Makefile verify` checks template integrity, context freshness, and project checks.
- `python .agents/tools/run_checks.py verify` runs equivalent checks without make.
- `python .agents/tests/smoke_install.py` checks preview, installation, sync, upgrades, and preservation using temporary projects.
- `make -f .agents/Makefile sync` refreshes adapters after shared source changes.
- `make -f .agents/Makefile context` updates the generated structure.

## Structural Map

<!-- BEGIN GENERATED STRUCTURE -->
### Generated Structure

- agent-runtime
  - folders: .agents/skills, .agents/subagents, .claude, .codex
- agent-tooling
  - folders: .agents/tests, .agents/tools

<!-- END GENERATED STRUCTURE -->
