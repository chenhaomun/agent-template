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

Use the shared [findings format](references/findings.md) for short, plain-language issue bullets.
