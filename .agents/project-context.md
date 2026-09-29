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
- Security policy: `SECURITY.md`.
- Story drafting/approved ClickUp creation: `draft-user-stories`; scoped HTML infographics: `visual-explainer`. Both are project-local skills.
- Review skills share the concise output contract in `.agents/skills/production-code-review/references/findings.md`.
- Flutter app-flow test authoring: `flutter-add-integration-test`; default triggers and setup authorization live in `AGENTS.md`.

## Commands

- `make -f .agents/Makefile verify` checks template integrity, context freshness, and project checks.
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
