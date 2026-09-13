---
name: production-code-review
description: Review a branch or diff against ticket requirements; report only actionable problems in short bullets with file and line references.
---

# Production Code Review

Review the diff and affected callers/tests. Prioritize correctness and regressions over cosmetic cleanup.

## Branch and Ticket

Accept: `Review {branch}; ticket: {ticket URL}.`

- Read the ticket and acceptance criteria when provided. If inaccessible, disclose the gap and review available code; never invent requirements.
- Resolve the requested branch and its PR target or established base. Compare from their merge base; ask only when the base cannot be inferred safely. Inspect refs without switching branches or disturbing local edits.
- Review changes against the ticket and affected consumers. Review-only requests do not authorize fixes, commits, or posting comments.

- Check requirement fit, nullability, async races, lifecycle ownership, and failure paths.
- Trace changed APIs, routes, models, permissions, and persistence through consumers.
- Check tests protect observable behavior and relevant edge cases, not private implementation.
- Identify concrete maintainability/performance risks; use specialist review only when warranted.
- Distinguish introduced defects from pre-existing issues; flag unrelated churn when it creates risk.

## Findings

Inspect actual code and affected callers. Report actionable issues supported by a concrete trigger and impact; do not turn style preferences or missing measurements into defects.

- `[P1] path/to/file.dart:42 — Trigger and impact; smallest fix.`

Report only what is wrong: no strengths, positive summaries, or generic praise. Use one short bullet per issue, ordered by severity (P0 critical, P1 high, P2 medium, P3 low). Use clickable file links with verified line numbers when supported; anchor to changed lines for diff reviews and identify the reviewed ref when local lines differ. Merge duplicate causes. No tables.
If none, say “No actionable findings.” Mention material verification gaps separately; do not imply unrun checks passed.
