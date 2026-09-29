# Agent Rules

Shared Claude Code and Codex rules. Flutter/Dart is primary, but project conventions win.

## Commands / Verify

- Prefer project scripts. Run template checks with `make -f .agents/Makefile verify`; use root `make verify` only when the project defines it.
- Do not hand-edit generated/vendored files (`*.g.dart`, `*.freezed.dart`, `build/`, `.dart_tool/`, etc.); edit the source and re-run the generator.
- Cap large command output at 4,000 chars (pipe through `head` or limit explicitly).
- Final response: concise outcome, changes, rationale, verification, and material limits/blockers/API/env impact. Expand for safety or when asked.

> Hooks in `.claude/settings.json` and `.codex/hooks.json` enforce these via shared `.agents/tools/` scripts; follow the rules even when hooks are unavailable.

## Work Rules

- Read nearby code first; follow existing architecture, naming, and tests.
- Read `.agents/project-context.md` when work requires a broad search or changes project structure, verification entrypoints, architecture, or ownership. Update the affected context then.
- Load only skills needed for the current decision; avoid loading every review skill for routine changes.
- Use `grill-requirements` when unclear scope, states, or acceptance criteria could cause rework.
- Keep changes scoped. Preserve user changes. Never reset unrelated work.
- When simplifying instructions, preserve every requirement; remove a rule only when an equivalent remains active, and identify where it lives.
- Keep reusable template content free of private project data; follow the template privacy rules in `SECURITY.md`.
- Follow existing design. Ask before new dependencies, architecture, state management, or generators unless authorized.
- Keep secrets out. Stop and report suspicious or unexpectedly long commands.
- Add/update tests when requested, required by TDD, or expected by project practice; verify narrowly first.
- Use `caveman` by default for chat responses; honor `off`/`normal mode` until re-enabled. Keep saved artifacts in normal prose and preserve required detail, response IDs, and verification notes.
- Batch independent targeted reads; reuse evidence already gathered. Expand checks only for changed scope, failures, or unresolved risk.
- Review findings: severity-first actionable bullets with verified `file:line`, impact, and smallest fix; separate unverified concerns and test gaps.
- Add comments/doc comments only where complex code needs explanation of non-obvious rationale, contracts, invariants, or hazards. Use plain language, at most two lines per comment.

## Filesystem Safety

- Default writes to the active project and task-specific temporary directories. A project task does not authorize changes to system files, other projects, user configuration, credentials, or agent/tool homes.
- Never delete, overwrite, move, `chmod`, or `chown` files outside the project unless the user explicitly names the exact path and action.
- Do not delete, truncate, or bulk replace user-authored local documents, even inside the project, without explicit authorization for the exact paths and action. Preserve unknown files during cleanup.
- Before destructive actions, resolve exact targets with read-only checks. Reject broad roots, unresolved variables, globs, external symlinks, and ambiguous recursive operations; prefer recoverable actions and backups.
- Preserve untracked files, local edits, and unrelated user data. Use elevated permissions only for an exact user-authorized target; stop and ask when scope or recovery is unclear.

## Flutter

- For new architecture, favor SOLID principles, object-oriented design, high cohesion, and low coupling within project conventions. Model distinct states explicitly instead of coordinating behavior with private boolean flags; add abstractions only when they clarify ownership or behavior.
- Check the package, SDK, scripts, and affected state, routing, networking, serialization, and test patterns. Use configured SDK wrappers and flavors; do not invent environment setup.
- For Flutter features, regression fixes, and architecture changes, use `flutter-add-integration-test` by default to add/update coverage of affected app flows. Reuse sufficient existing coverage; explain when no executable flow is affected. Minimal Flutter SDK test setup is authorized; new third-party harnesses still require approval.
- Start with affected tests and analysis; format touched Dart files. Run broader checks for shared contracts or cross-feature changes. Launch/build for affected integration tests, runtime/platform/release risk, or on request. Report checks not run; never claim runtime validation from static checks.
- Prefer composition, immutable state, and pure, cheap `build()` methods. Keep IO and repeated transformations out of build; limit rebuild scope and lazily build large collections.
- Dispose owned controllers/subscriptions; handle stale async results and check mounted/context validity after async gaps. Preserve meaningful error handling and relevant loading/empty/error/disabled states.
- Bound caches and network work. Profile plausible slow paths in profile mode on a representative target before claiming improvements; use isolates only when CPU cost outweighs overhead and the target supports them.
- Preserve project logging/theme/l10n, null safety, accessibility, and supported platforms. Check changed layouts against relevant constraints, text scaling, keyboard insets, and interactions without expanding product scope.
- Native/FFI/binary downloads require explicit user approval and hash/offline fallback review.

## Screenshot UI

- When the user provides screenshot paths, inspect those exact files and implement the UI accordingly. Reuse project tokens/components/assets, cover responsive and interaction states, and ask only when behavior cannot be inferred. Do not require a fixed folder or Figma.

## Memory

- Keep required rules and stable project facts in checked-in instructions or `.agents/project-context.md`; auto-memory is recall only.
- Store no secrets or duplicated repository facts. Keep only durable preferences, corrections, and decisions; prune stale entries.

## Subagents

Use subagents only when the user explicitly requests delegation. Then use `.agents/skills/subagent-workflow` for roles and scoped ownership. Keep integration and final verification with the main agent.

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
