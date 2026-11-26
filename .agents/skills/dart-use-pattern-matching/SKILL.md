---
name: dart-use-pattern-matching
stack: dart
description: Use Dart 3 patterns, switch expressions, and destructuring where they simplify validation, sealed-type handling, and list/record/map decomposition. Use when refactoring branching or parsing code; not for simple boolean checks.
---

# Dart Patterns

Requires a Dart 3 SDK constraint. Use patterns only where they make code shorter and clearer than the existing style.

## Choose

- Switch expression to produce a value; switch statement for side effects. Rely on exhaustiveness for `sealed` classes and enums instead of a catch-all `_` arm.
- Map/List/Object patterns to validate and extract decoded JSON in one step, with a final `_ => throw FormatException(...)` arm. Map patterns require the key to exist; read optional keys separately.
- List patterns with rest elements for path segments and `split` tokens instead of `.first`, `.skip`, and index arithmetic.
- Record patterns for multiple return values; Object patterns to unpack three or more fields used repeatedly or to promote nullable fields.
- `when` guards for conditions patterns cannot express; `||` for arms sharing a body (both sides bind the same variables).

## Avoid

- `if-case` where an `is` check promotes the variable in place.
- Single-arm or boolean switches; use `if` or a ternary.
- `if-case` filters that silently drop malformed data; fail fast instead.
- Destructuring one or two fields, or fields passed straight into a single call.
- Relational patterns for one standalone comparison.

Verify with analysis (exhaustiveness, unreachable arms) and tests for malformed and missing-key input.
