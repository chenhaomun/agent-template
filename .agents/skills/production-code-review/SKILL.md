---
name: production-code-review
description: Review a branch, diff, or plan against its ticket for correctness, architecture, code quality, performance, and security. Report only problems with fix direction; estimate sprint points when the ticket has none.
---

# Production Code Review

Review only: no fixes, commits, ticket edits, or posted comments unless asked. Apply `SECURITY.md` before reading diffs or logs; redact sensitive evidence.

## Scope

Accept `Review {branch}; ticket: {ticket URL}.`

- Read the ticket, acceptance criteria, sprint points, and comments/replies. If inaccessible, say so and review the code; never invent requirements or treat suggestions as approved.
- Compare the branch from its merge base with the PR target or established base, without switching branches or touching local edits. Ask only when the base cannot be inferred.
- Review the diff plus affected callers, contracts, and tests. Separate introduced defects from pre-existing ones; flag unrelated churn only when it adds risk.

## Checks

Check only what the change touches.

- **Correctness:** requirement fit, nullability, async races, lifecycle ownership, failure paths, and consumers of changed APIs, models, routes, permissions, or persistence.
- **Tests:** protect observable behavior and edge cases, not private implementation.
- **Architecture:** ownership, layering, dependency flow, and compatible contracts or migrations. Prefer boundaries visible in folders and enforced by import checks. Direct UI/data access is not automatically wrong; follow project conventions.
- **Quality:** mixed responsibilities that cause coupling or poor testability; duplicated business rules that can drift; speculative abstraction; risky APIs used outside one owning wrapper; workarounds that copy anti-patterns or rely on comments. Small feature-local duplication is fine. Never prescribe packages or DI just to satisfy a pattern.
- **Performance:** IO or repeated parsing/sorting in build, broad rebuilds, eager large lists, oversized images, missing pagination, repeated or unbounded requests, stale results, leaked controllers/subscriptions, unbounded caches, blocked startup. Use isolates only when CPU cost justifies them. Speed claims need profile-mode evidence; mark suspected issues as suspected.
- **Security:** trace untrusted input to sensitive operations: server-side authorization, session expiry/refresh, validation, payment replay. Trace sensitive data through storage, logs, URLs, analytics, crash reports, and backups. For Flutter/mobile, use [mobile security checks](references/security-flutter.md) for affected surfaces. Validate advisories and scanner output against pinned versions and reachable code.

## CI

- Inspect CI config and included jobs first (triggers, path filters, commands). Do not rerun checks CI already covers for this commit; pending, skipped, stale, or inaccessible results are not passes.
- Run a focused local check only for uncovered risk, a finding needing reproduction, a CI failure, changed CI config, or on request. Without CI, run the narrowest relevant checks.
- Do not repeat CI's mechanical findings unless explaining cause or impact. Passing CI does not prove correctness.

## Sprint Points

If the ticket has no sprint points, estimate its mobile work with the [sizing guide](../draft-user-stories/references/sprint-points.md): one Fibonacci value for complexity, effort, and uncertainty, not hours. Do not edit the ticket.

## Output

Problems only, most severe first, one bullet per cause:

`[P1] file:line — What breaks and when. Fix: smallest change.`

- P0 critical, P1 high, P2 medium, P3 low. Aim for 30 words or fewer after the location, in everyday words.
- Example: `[P1] checkout.dart:42 — Tapping Pay twice sends two charges. Fix: disable Pay while the request runs.`
- Report only verified, actionable issues; no style preferences or unmeasured suspicions. Link `file:line` on changed lines; name the reviewed ref if local lines differ.
- For a defect likely to recur, the fix names the check that blocks it (type, lint, test, import boundary).
- No praise, summaries, or tables. With no problems, write `No actionable findings.`
- Then, only if material: `Not verified:` bullets (unrun checks, inaccessible ticket, unknown trust assumptions).
- Last, when the ticket had no points: `Sprint Point: n (estimated)`.
