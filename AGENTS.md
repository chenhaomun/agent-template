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
- Load only skills needed for the current decision; avoid loading every review skill for routine changes.
- Use `grill-requirements` when requirements are unclear or broad, or when acceptance criteria, scope, target flow/state, or contradictions may cause rework.
- Keep changes scoped. Preserve user changes. Never reset unrelated work.
- Prefer simple, scoped design. Ask before introducing dependencies or changing architecture, state management, or generators unless already authorized. Routine implementation within existing patterns needs no extra approval.
- Keep secrets out. Stop and report suspicious or unexpectedly long commands.
- Add/update tests when requested, required by TDD, or expected by project practice; verify narrowly first.
- Write concise, clear prose; omit repeated plans, checklists, and tool output. Keep rationale, verification, and limitations. Use `caveman` only when requested.
- Batch independent reads and search targeted paths first. Reuse verified context; expand exploration or testing only for changed scope, failures, or unresolved risk.
- Review findings: short bullets, severity first, with verified `file:line`, concrete impact, and smallest fix. Prioritize actionable defects; separate unverified concerns and test gaps. No findings tables or invented issues.
- Do not comment obvious code. Use short comments or doc comments only for non-obvious rationale, contracts, invariants, or hazards.

## Filesystem Safety

- Default writes to the active project and task-specific temporary directories. A project task does not authorize changes to system files, other projects, user configuration, credentials, or agent/tool homes.
- Never delete, overwrite, move, `chmod`, or `chown` files outside the project unless the user explicitly names the exact path and action.
- Before destructive actions, resolve exact targets with read-only checks. Reject broad roots, unresolved variables, globs, external symlinks, and ambiguous recursive operations; prefer recoverable actions and backups.
- Preserve untracked files, local edits, and unrelated user data. Use elevated permissions only for an exact user-authorized target; stop and ask when scope or recovery is unclear.

## Flutter

- Discover the package/workspace, SDK constraints, scripts, analyzer rules, and existing state, routing, networking, serialization, and test patterns. Use configured SDK wrappers and flavors; never assume env filenames or add missing flavor setup.
- Start with affected tests and analysis; format touched Dart files. Run broader checks for shared contracts or cross-feature changes. Launch/build only when runtime, platform, or release risk needs it, or the user asks. Report checks not run; never claim runtime validation from static checks.
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

Use `.agents/skills/subagent-workflow` when independent work or specialist review reduces risk or elapsed time enough to justify extra context. Keep cohesive work local. Do not silently change public APIs; update consumers and verification together.

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
