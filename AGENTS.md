# AGENTS.md

Shared agent rules for Codex and Claude Code. Core rules are language-agnostic; Flutter/Dart is the primary stack (see `## Flutter`). For other stacks, add a section here.

## Commands / Verify

- Prefer project scripts over raw commands. Use `make verify` as the canonical gate (integrity + map + analysis + tests + format); `make help` lists targets. Non-Flutter stacks: check `package.json` scripts or `scripts/`.
- Do not hand-edit generated/vendored files (`*.g.dart`, `*.freezed.dart`, `build/`, `.dart_tool/`, etc.); edit the source and re-run the generator.
- Cap large command output at 4,000 chars (pipe through `head` or limit explicitly).
- Final response: short and precise. Lead with the outcome, then only changes made, verification run, and any blocker/API/env impact. No preamble, no restating the request, no step-by-step recap. Prose or a short list — not both. Expand only when asked or when safety requires it.

> Hooks in `.claude/settings.json` and `.codex/hooks.json` enforce these via shared `.agents/tools/` scripts; follow the rules even when hooks are unavailable.

## Work Rules

- Read nearby code before editing; follow existing architecture, naming, patterns, and test conventions.
- Check `.agents/project-map.md` before broad search; if missing or stale, preview `<python> .agents/tools/generate_project_map.py`, then update via `apply_patch`.
- Use relevant `.agents/skills/<skill>/SKILL.md`; project conventions beat generic examples.
- Use `grill-requirements` when acceptance criteria, scope, target flow/state, or contradictions may cause rework.
- Keep changes scoped. Preserve user changes. Never reset unrelated work or modify generated/vendored files.
- Follow SOLID/DRY/KISS. Ask before adding packages, tools, or global dependencies. Ask before architecture, state-management, or generator changes.
- Keep secrets out. Stop suspicious or unexpectedly long commands; report the command and elapsed time.
- Add/update tests when requested, when following TDD, or when matching project practice. Run narrow verification.
- Tiered review: small = self-check; medium single-owner = `production-code-review` + max one specialist skill; large/risky/multi-agent = full review.
- Default `$caveman lite`; expand only for safety warnings, blockers, or explicit user request.
- Default to low reasoning effort for small, well-scoped edits. Raise effort for risky, multi-step, architectural, or ambiguous work (Codex: `/reasoning high` or `model_reasoning_effort`).

## Flutter

- Verify with `flutter analyze`, `flutter test`, `flutter run --dart-define-from-file=.env.dev.json`, `flutter build <target> --dart-define-from-file=.env.prod.json`.
- Prefer Dart/Flutter MCP for analyzer, symbols, fixes, format, tests, pub.dev, dependencies, and running-app/widget inspection.
- Check `analysis_options.yaml` and `.agents/flutter-dependencies.md`.
- Prefer composition, immutable widgets, `const`, pure/fast `build()`, lazy lists, and off-UI-thread expensive work.
- Keep null safety; avoid `!` unless guaranteed. Use project logging, theme/assets/tokens, l10n, responsive/a11y, platform parity, permissions, and fallbacks.
- Cover loading, success, empty, error, disabled, and permission states. Keep errors actionable.
- Use configured flavors and `--dart-define-from-file`.
- Native/FFI/binary downloads require explicit user approval and hash/offline fallback review.

## Contracts

- Do not silently change public APIs. Update consumers, mocks/fixtures, migrations, and verification together.
- Keep PRs single-goal.

## Subagents

For medium/large/risky/unclear work, use `.agents/skills/subagent-workflow`. Skip for trivial edits.

## Git

Branch: `<type>/<ticket-title-summary>`, e.g. `feature/add-auth`, `fix/login-crash`.

For commit messages from staged changes, use `git-staged-commit-message`.

Commit with ticket:

```text
<ticket> - <summary>

- <point A>
- <point B>
```

Without ticket, omit `<ticket> - `.
