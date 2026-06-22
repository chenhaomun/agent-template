---
name: solid-oop-review
description: Review SOLID/OOP: class design, service boundaries, dependency direction, responsibility splits, abstractions, coupling.
---

# SOLID OOP Review

Use project architecture first. Do not force textbook patterns where local style is simpler.

## Check

| Principle | Reject when |
|---|---|
| Single responsibility | One class/service mixes orchestration, mapping, IO, policy, and state |
| Open/closed | New variant requires editing many switch/if blocks across unrelated layers |
| Liskov | Subtype/implementation weakens expected behavior or throws unsupported surprises |
| Interface segregation | Callers depend on methods/data they do not need |
| Dependency inversion | High-level policy depends directly on low-level IO/framework details |
| Encapsulation | Mutable state, construction rules, or invariants leak outside owner |

## Output

Return only critical items:

| Decision | Design issue | Direction |
|---|---|---|
| accepted / needs revision / rejected | Concrete smell | Smallest project-compatible fix |

Do not recommend new packages, state managers, or architectures unless required.

## Examples

| Principle | Signal | Direction |
|---|---|---|
| SRP | Service handles HTTP, parsing, caching, and business policy | Split data/policy/transport concerns |
| OCP | New type requires switches in multiple unrelated layers | Add strategy/mapper at the boundary |
| LSP | Implementation returns partial model or throws for supported contract method | Preserve contract or narrow the interface |
| ISP | Class depends on large interface only to call one method | Depend on smaller existing interface/callback |
| DIP | Domain/use-case imports framework/IO implementation | Depend on project abstraction and inject implementation |
| Encapsulation | Callers patch mutable fields directly | Encapsulate mutation behind owner method or immutable value |
