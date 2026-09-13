---
name: code-quality-review
description: Review SOLID/DRY/KISS, coupling, duplication, needless abstraction, and excess complexity.
---

# Code Quality Review

Follow project conventions. SOLID, DRY, and KISS guide decisions; they do not require extra layers.

- Flag mixed responsibilities when they cause coupling, conflicting changes, or poor testability.
- Check implementations preserve contracts and encapsulate mutable state.
- Flag duplicated business rules that can drift; accept small duplication that keeps features independent.
- Prefer direct control flow and local ownership over speculative generalization.
- Recommend the smallest compatible fix; do not prescribe packages, repositories, or dependency injection merely to satisfy a pattern.

## Findings

Inspect actual code and affected callers. Report actionable issues supported by a concrete trigger and impact; do not turn style preferences or missing measurements into defects.

- `[P1] path/to/file.dart:42 — Trigger and impact; smallest fix.`

Use one short bullet per issue, ordered by severity (P0 critical, P1 high, P2 medium, P3 low). Use clickable file links with verified line numbers when supported; anchor to changed lines for diff reviews. Merge duplicate causes. No tables or generic praise.
If none, say “No actionable findings.” Mention material verification gaps separately; do not imply unrun checks passed.
