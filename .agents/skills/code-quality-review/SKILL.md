---
name: code-quality-review
description: Review SOLID/DRY/KISS, coupling, duplication, needless abstraction, and excess complexity.
---

# Code Quality Review (SOLID + DRY + KISS)

Use project architecture first. Do not force textbook patterns where local style is simpler, do not remove duplication when shared code would make ownership or change isolation worse, and do not flatten necessary architecture just to reduce lines.

## Check: SOLID / OOP

| Principle | Reject when |
|---|---|
| Single responsibility | One class/service mixes orchestration, mapping, IO, policy, and state |
| Open/closed | New variant requires editing many switch/if blocks across unrelated layers |
| Liskov | Subtype/implementation weakens expected behavior or throws unsupported surprises |
| Interface segregation | Callers depend on methods/data they do not need |
| Dependency inversion | High-level policy depends directly on low-level IO/framework details |
| Encapsulation | Mutable state, construction rules, or invariants leak outside owner |

## Check: DRY

| Principle | Reject when |
|---|---|
| Single source of truth | Same business rule, permission, validation, route, query, or mapping can drift across files |
| Data over copy/paste | Repeated blocks differ only by literals that belong in params, data, enum values, or config |
| Boundary reuse | DTO/domain/UI conversions are duplicated instead of using the project mapper/factory pattern |
| Test reuse | Fixtures or setup are copied enough that future behavior changes require many edits |

Accept small local duplication when it keeps features independent or avoids premature abstraction.

## Check: KISS

| Principle | Reject when |
|---|---|
| Minimal abstraction | New layer, helper, base class, mixin, service, or pattern adds no clear current value |
| Straight control flow | Async flow, state transitions, or branching are harder to follow than the requirement needs |
| Locality | Reader must jump through unrelated files to understand simple behavior |
| Scope discipline | Implementation solves future/general cases not required by the task |
| Operational simplicity | Added config, generated code, tooling, or setup increases maintenance without need |

## Output

Return only critical items:

| Decision | Issue (SOLID/DRY/KISS) | Direction |
|---|---|---|
| accepted / needs revision / rejected | Concrete smell or drift risk | Smallest project-compatible fix |

Do not recommend new packages, state managers, or architectures unless required.

## Examples

| Dimension | Signal | Direction |
|---|---|---|
| SRP | Service handles HTTP, parsing, caching, and business policy | Split data/policy/transport concerns |
| DIP | Domain/use-case imports framework/IO implementation | Depend on project abstraction and inject implementation |
| DRY | Same status mapping exists in service and in view | Move mapping to existing mapper/state owner |
| DRY | Three handlers repeat identical logic with only labels changed | Use data list + existing component/helper |
| KISS | One-off helper class wraps a single function with no state | Inline or use a small function in the owner file |
| KISS | Feature adds generic plugin system for one current variant | Implement current variant; add extension point only if needed |
