# Agent Rules

Shared Claude Code and Codex rules. Flutter/Dart is primary, but project conventions win.

## Commands / Verify

- Prefer project scripts. Run template checks with `make -f .agents/Makefile verify`; use root `make verify` only when the project defines it.
- Do not hand-edit generated/vendored files (`*.g.dart`, `*.freezed.dart`, `build/`, `.dart_tool/`, etc.); edit the source and re-run the generator.
- Cap large command output at 4,000 chars (pipe through `head` or limit explicitly).
- Final response: outcome, changes, verification, and blockers/API/env impact only. Expand for safety or when asked.

> Hooks in `.claude/settings.json` and `.codex/hooks.json` enforce these via shared `.agents/tools/` scripts; follow the rules even when hooks are unavailable.

## Work Rules

- Read nearby code first; follow existing architecture, naming, and tests.
- Read `.agents/project-context.md` before broad search. Update its generated block when structure or verification entrypoints change; update curated notes when architecture or ownership changes.
- Use relevant `.agents/skills/<skill>/SKILL.md`.
- Use `grill-requirements` when requirements are unclear or broad, or when acceptance criteria, scope, target flow/state, or contradictions may cause rework.
- Keep changes scoped. Preserve user changes. Never reset unrelated work.
- Prefer simple, scoped design. Ask before dependencies, architecture, state-management, or generator changes.
- Keep secrets out. Stop and report suspicious or unexpectedly long commands.
- Add/update tests when requested, required by TDD, or expected by project practice; verify narrowly first.
- Default `caveman lite` responses (Codex: `$caveman`, Claude: `/caveman`); expand only for safety warnings, blockers, or explicit user request.
- Do not comment obvious code. Use short comments or doc comments only for non-obvious rationale, contracts, invariants, or hazards.

## Filesystem Safety

- Default writes to the active project and task-specific temporary directories. A project task does not authorize changes to system files, other projects, user configuration, credentials, or agent/tool homes.
- Never delete, overwrite, move, `chmod`, or `chown` files outside the project unless the user explicitly names the exact path and action.
- Before destructive actions, resolve exact targets with read-only checks. Reject broad roots, unresolved variables, globs, external symlinks, and ambiguous recursive operations; prefer recoverable actions and backups.
- Preserve untracked files, local edits, and unrelated user data. Use elevated permissions only for an exact user-authorized target; stop and ask when scope or recovery is unclear.

## Flutter

- Verify with `flutter analyze`, `flutter test`, `flutter run --dart-define-from-file=.env.dev.json`, `flutter build <target> --dart-define-from-file=.env.prod.json`.
- Check `analysis_options.yaml`; prefer existing packages and Dart/Flutter tooling.
- Prefer composition, immutable/`const` widgets, fast `build()`, lazy lists, and off-UI-thread expensive work.
- Preserve null safety, project logging/theme/l10n, responsiveness/a11y, platform parity, permissions, and loading/success/empty/error/disabled states.
- Use configured flavors and `--dart-define-from-file`.
- Native/FFI/binary downloads require explicit user approval and hash/offline fallback review.

## Screenshot UI

- When the user provides screenshot paths, inspect those exact files and implement the UI accordingly. Reuse project tokens/components/assets, cover responsive and interaction states, and ask only when behavior cannot be inferred. Do not require a fixed folder or Figma.

## Memory

- Keep required rules and stable project facts in checked-in instructions or `.agents/project-context.md`; auto-memory is recall only.
- Store no secrets or duplicated repository facts. Keep only durable preferences, corrections, and decisions; prune stale entries.

## Subagents

For medium/large/risky/unclear work, use `.agents/skills/subagent-workflow`. It chooses planner strength by complexity, then the cheapest capable executor. Skip for small work. Do not silently change public APIs; update consumers and verification together.

## Git

- Never commit, push, tag, publish, create a pull request, or change remote Git state unless the user explicitly requests that exact action.

Branch: `<type>/<ticket-title-summary>`, e.g. `feature/add-auth`, `fix/login-crash`.

For commit messages from staged changes, use `git-staged-commit-message`.

Commit with ticket:

```text
<ticket> - <summary>

- <point A>
- <point B>
```

Without ticket, omit `<ticket> - `.
