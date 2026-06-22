---
name: kiss-review
description: Review KISS/simplicity: over-engineering, needless abstraction, indirection, clever code, complexity beyond the requirement.
---

# KISS Review

Use project architecture first. Prefer the simplest implementation that satisfies the requirement, preserves correctness, and fits existing conventions.

## Check

| Principle | Reject when |
|---|---|
| Minimal abstraction | New layer, helper, base class, mixin, service, package, or pattern adds no clear current value |
| Straight control flow | Async flow, state transitions, or branching are harder to follow than the requirement needs |
| Locality | Reader must jump through unrelated files to understand simple behavior |
| Clear syntax | Clever syntax hides business behavior, lifecycle constraints, or error handling |
| Scope discipline | Implementation solves future/general cases not required by the task |
| Operational simplicity | Added config, generated code, tooling, or setup increases maintenance without need |

## Output

Return only critical items:

| Decision | Complexity issue | Direction |
|---|---|---|
| accepted / needs revision / rejected | Concrete over-complexity risk | Smallest project-compatible simplification |

Do not flatten necessary architecture, safety checks, or platform handling just to reduce lines.

## Examples

| Principle | Signal | Direction |
|---|---|---|
| Minimal abstraction | One-off helper class wraps a single function with no state | Inline or use a small function in the owner file |
| Straight control flow | Nested callbacks/promises obscure loading/error transitions | Use existing state-management pattern with explicit states |
| Locality | Simple action routes through unrelated service registry | Call existing nearby owner/callback |
| Scope discipline | Feature adds generic plugin system for one current variant | Implement current variant; add extension point only if needed |
