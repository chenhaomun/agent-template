# AGENTS.md

Shared agent rules for Codex and Claude Code. Core rules are language-agnostic; Flutter/Dart is the primary stack (see `## Flutter`). For other stacks, add a section here.

## Commands / Verify

- Prefer project scripts over raw commands. This template ships a `Makefile` — use `make verify` (integrity + map freshness + analysis + tests + format check) as the canonical gate; `make help` lists targets. Check `package.json` scripts or `scripts/` for non-Flutter stacks.
- Do not hand-edit generated/vendored files (`*.g.dart`, `*.freezed.dart`, `build/`, `.dart_tool/`, etc.); edit the source and re-run the generator.
- Cap potentially large command output at 4,000 chars (pipe through `head` or limit explicitly).
- Final response states: changes made, verification ran, blockers/gaps, and API/env/permission impact if relevant.

> Claude Code and Codex enforce these rules via project hooks in `.claude/settings.json` and `.codex/hooks.json`. Both run shared scripts from `.agents/tools/`; agents must still follow the rules when hooks are unavailable or untrusted.

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
