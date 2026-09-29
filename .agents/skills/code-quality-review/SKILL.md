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

Use the shared [findings format](../production-code-review/references/findings.md) for short, plain-language issue bullets.
