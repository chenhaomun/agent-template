---
name: dry-review
description: Review code for DRY maintainability. Use for duplicated business rules, mappings, validation, queries, routing, UI state, fixtures, test setup, and copy/paste drift risks.
---

# DRY Review

Use project architecture first. Do not remove duplication when shared code would make ownership, readability, or change isolation worse.

## Check

| Principle | Reject when |
|---|---|
| Single source of truth | Same business rule, permission, validation, route, query, or mapping can drift across files |
| Data over copy/paste | Repeated blocks differ only by literals that belong in params, data, enum values, or config |
| Boundary reuse | DTO/domain/UI conversions are duplicated instead of using the project mapper/factory pattern |
| Test reuse | Fixtures or setup are copied enough that future behavior changes require many edits |
| Intent clarity | Duplication hides which owner is authoritative for behavior |

## Output

Return only critical items:

| Decision | Duplication issue | Direction |
|---|---|---|
| accepted / needs revision / rejected | Concrete drift risk | Smallest project-compatible dedupe |

Accept small local duplication when it keeps features independent or avoids premature abstraction.

## Examples

| Principle | Signal | Direction |
|---|---|---|
| Single source of truth | Same status mapping exists in service and in view | Move mapping to existing mapper/state owner |
| Data over copy/paste | Three handlers repeat identical logic with only labels changed | Use data list + existing component/helper |
| Boundary reuse | API response parsing duplicated in two services | Reuse project DTO/mapper path |
| Test reuse | Same setup copied across many tests | Extract local test helper/fixture where project style supports it |
