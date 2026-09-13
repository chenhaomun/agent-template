---
name: architecture-review
description: Review architecture/boundaries: feature placement, layering, ownership, dependency flow, public contracts, refactors, integration risk.
---

# Architecture Review

Review affected ownership boundaries using the project's established architecture.

- Trace dependencies and state/data ownership; name the consequence of a misplaced responsibility.
- Check API/model/event/route changes update consumers and preserve compatibility or define migration.
- Assess persistence, platform, permission, and release effects where relevant.
- Keep refactors scoped. Add boundaries only for current complexity or demonstrated coupling.
- Direct UI/data access is not automatically a defect; assess project conventions and behavior.

## Findings

Inspect actual code and affected callers. Report actionable issues supported by a concrete trigger and impact; do not turn style preferences or missing measurements into defects.

- `[P1] path/to/file.dart:42 — Trigger and impact; smallest fix.`

Use one short bullet per issue, ordered by severity (P0 critical, P1 high, P2 medium, P3 low). Use clickable file links with verified line numbers when supported; anchor to changed lines for diff reviews. Merge duplicate causes. No tables or generic praise.
If none, say “No actionable findings.” Mention material verification gaps separately; do not imply unrun checks passed.
