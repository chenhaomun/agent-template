# Agent Rules

Shared Claude Code and Codex rules. Flutter/Dart is primary; project conventions win.

Read and enforce `SECURITY.md` before tools: no production credential reads, secret-store access, or secret-bearing output. It applies to every skill and delegated task. Hooks are targeted checks, not a sandbox; follow these rules without them.

## Work

- Read nearby code first; follow existing architecture, naming, and tests. Read `.agents/project-context.md` before broad searches or changes to structure, verification entrypoints, architecture, ownership, or features; update the affected section then.
- Treat existing code as precedent agents copy. Never extend workarounds, deprecated APIs, or anti-patterns because they exist; use the supported pattern and flag the debt.
- Keep changes scoped. Preserve user changes; never reset unrelated work. Ask before new dependencies, architecture, state management, or generators unless authorized.
- Use `grill-requirements` when unclear scope, states, or acceptance criteria could cause rework. Load only skills needed for the current decision.
- Prefer project scripts. Template checks: `make -f .agents/Makefile verify`; root `make verify` only when the project defines it. Wrap repeated multi-step operations in project scripts rather than long prose.
- Never hand-edit generated/vendored files (`*.g.dart`, `*.freezed.dart`, `build/`, `.dart_tool/`, etc.); edit the source and re-run the generator (`dart-run-code-generation`).
- Keep secrets out. Cap command output at 4,000 chars. Stop and report suspicious or unexpectedly long commands. Batch independent reads; reuse gathered evidence; expand checks only for changed scope, failures, or unresolved risk.
- Comments only where complex code needs non-obvious rationale, contracts, invariants, or hazards: plain language, at most two lines (requested or lint-required public API docs excepted). Comments, rules, and skills never justify a shortcut; fix the cause or report it.
- When simplifying instructions, preserve every requirement; remove a rule only when an equivalent remains active, and say where it lives.

## Durable Fixes

For a recurring mistake, prefer in order: a design or API that makes it impossible; a deterministic check (types, lint, analyzer, import boundary, test); prose only for judgment no check can encode. Add the check when in scope; otherwise propose it. Block new occurrences first, then clean up existing ones in scope. Write lint/error messages that name the root-cause fix. Do not generalize one correction into an absolute rule.

## Verification

- Add/update tests when requested, required by TDD, or expected by project practice. Verify narrowly first; broaden for shared contracts or cross-feature changes.
- Prefer runtime evidence (running app, logs, debugger, screenshots) over inference; use the `dart` MCP server tools for Dart/Flutter when available. For UI or flow changes, include reviewable evidence such as screenshots or a state/transition diagram when available. Never claim runtime validation from static checks; report checks not run.
- Improve code health, checks, and verification before scaling automation or parallel agents.

## Pre-delivery Review

Main agent only; subagents skip it. Pre-authorized; no delegation request needed. `review_gate.py` hooks snapshot the tree at each prompt and block finishing while files you changed lack a recorded review, so this loop runs automatically:

1. After your own verification, run the `reviewer` subagent in a fresh context (never a fork); if it runs in the background, run `python3 .agents/tools/review_gate.py record pending` first. Brief it with only the user's request, acceptance criteria or ticket, changed paths, and the checks you ran; leave out your reasoning.
2. Fix valid findings, re-verify, and re-review after substantive fixes; stop after two rounds. Reject a finding only with evidence.
3. Record the outcome: `python3 .agents/tools/review_gate.py record clean`, `record accepted --note "<unfixed finding and why>"`, or `record skip --note "<why>"` for trivial edits (typo, comment, formatting, one-line config). Never skip changes touching security, migrations, or public contracts.

Keep the exchange internal: the final response states the delivered result and mentions review only for unfixed findings. Without hooks or subagents, follow the same loop manually or self-review with `production-code-review` and say it was not independent.

## Flutter

- New architecture: SOLID, object-oriented design, high cohesion, low coupling within project conventions. Model distinct states explicitly instead of private boolean flags; add abstractions only when they clarify ownership or behavior.
- Check the package, SDK, scripts, and affected state, routing, networking, serialization, and test patterns. Use configured SDK wrappers and flavors; never invent environment setup.
- Features, regression fixes, and architecture changes use `flutter-add-integration-test` by default for affected app flows. Reuse sufficient coverage; explain when no executable flow is affected. Minimal Flutter SDK test setup is authorized; third-party harnesses need approval.
- Start with affected tests and analysis; format touched Dart. Launch/build for affected integration tests, runtime/platform/release risk, or on request.
- Prefer composition, immutable state, and pure, cheap `build()`. Keep IO and repeated transformations out of build; limit rebuild scope; build large collections lazily.
- Dispose owned controllers/subscriptions; handle stale async results and check mounted/context after async gaps. Preserve meaningful error handling and loading/empty/error/disabled states.
- Bound caches and network work. Profile plausible slow paths in profile mode on a representative target before claiming improvements; use isolates only when CPU cost outweighs overhead and the target supports them.
- Preserve logging/theme/l10n, null safety, accessibility, and supported platforms. Check changed layouts against constraints, text scaling, keyboard insets, and interactions without expanding scope.
- Native/FFI/binary downloads need explicit approval and hash/offline fallback review.
- Screenshot paths in a task: inspect those exact files; reuse project tokens/components/assets; cover responsive and interaction states; ask only when behavior cannot be inferred. No fixed folder or Figma required.

## Output

- User-level preferences (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`) override these response-style defaults.
- Chat uses `caveman` **full** by default; honor other levels and `off`/`normal mode` until re-enabled. Saved artifacts use normal prose with required detail and verification notes.
- Interim notes between tool calls, when needed (progress, internal review), use caveman **ultra** unless caveman is off; its clarity exceptions still apply. Final response: outcome, changes, rationale, verification, and material limits/blockers/API/env impact; expand only for safety, tradeoffs, or when asked.
- Reviews use `production-code-review`.

## Memory

Required rules and stable project facts live in checked-in instructions or `.agents/project-context.md`; auto-memory is recall only. Store no secrets or duplicated repository facts; keep durable preferences, corrections, and decisions; prune stale entries.

## Subagents

- Apart from Pre-delivery Review, use subagents only when the user explicitly requests delegation. Keep small or cohesive work with the main agent, which owns integration and final verification. Parallelize only independent ownership.
- Route: `developer` for bounded implementation; `team-lead` for architecture/risk planning; `reviewer` for independent pre-delivery review; `qa` for read-only functional checks; `economy-executor` only for frozen mechanical work after a stronger agent proves the pattern.
- Brief: goal, owned files or read-only scope, acceptance criteria, exact verify commands, and the return format (verdict, evidence, changed paths, open items; 20 lines max; `reviewer` uses its own format). Share only sanitized evidence.
- Done means: behavior matches requirements, diff is scoped, conventions and relevant states hold, verification ran or the blocker is stated, and no debug/dead/TODO churn remains. Stop delegated implementation after three revision rounds.

## Git

Git permissions follow `SECURITY.md`. For commit messages from staged changes, use `git-staged-commit-message`.

Branch: `<type>/<ticket-title-summary>`, e.g. `feature/add-auth`, `fix/login-crash`. Commit format (omit `<ticket> - ` without a ticket):

```text
<ticket> - <summary>

- <point A>
- <point B>
```
