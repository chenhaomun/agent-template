---
name: architecture-review
description: Review architecture and system boundaries. Use for feature placement, layering, module ownership, dependency flow, public contracts, cross-platform behavior, refactors, and integration risk.
---

# Architecture Review

Prefer existing project architecture over generic patterns.

## Check

| Area | Reject when |
|---|---|
| Placement | Code lives in the wrong layer, feature, module, or ownership boundary |
| Dependency flow | UI owns data policy, domain depends on framework/IO, or lower layer calls upward |
| Contracts | Public API/model/event/route/env behavior changes without matching consumers |
| Scope | Refactor touches unrelated modules or combines multiple goals |
| Extensibility | New behavior hard-codes variants that project already models elsewhere |
| Platform | Platform-specific behavior is inconsistent without reason |
| Migration | Data, cache, permission, or release impact is missing when contract changes |

## Output

| Decision | Architectural risk | Better direction |
|---|---|---|
| accepted / needs revision / rejected | Specific boundary or contract issue | Smallest aligned design |

Avoid broad redesign unless the current design blocks the requirement.

## Examples

| Signal | Better direction |
|---|---|
| UI imports data layer directly | Route through existing service/repository layer |
| Public DTO shape changed without updating callers | Update contract consumers, fixtures, and verification together |
| One feature edit rewrites shared module | Split shared change or keep feature scoped |
