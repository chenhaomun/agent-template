---
name: production-code-review
description: Review diffs for production readiness: correctness, maintainability, edge cases, verification, regressions, ship-readiness.
---

# Production Code Review

Review actual code or diff, not only reports.

## Check

| Area | Reject when |
|---|---|
| Requirement fit | Behavior misses requirement, overbuilds scope, or changes unrelated behavior |
| Correctness | Edge case, null, async, lifecycle, race, stale state, or error path is unsafe |
| Maintainability | Names, structure, duplication, unnecessary abstraction, or file size makes future change harder |
| Integration | API, model, route, permission, env, migration, or platform contract changed silently |
| Verification | No meaningful check was run and no blocker explains why |
| Cleanliness | Debug code, TODO without owner, dead code, generated-file edits, or unrelated churn remains |
| Simplicity | Implementation is more complex than the requirement or project pattern needs |

## Output

Return concise table rows:

| Decision | Reason | Required action |
|---|---|---|
| accepted / needs revision / rejected | Critical reason only | Exact next change or verification |

Prefer `needs revision` over `accepted` when production risk is unclear.

## Examples

| Signal | Review response |
|---|---|
| Feature works but empty/error state missing | `needs revision`: add missing state or document why unreachable |
| Diff modifies unrelated files | `needs revision`: remove unrelated churn |
| Tests not run because dependency missing | `needs revision` only if blocker is real and stated |
