---
name: flutter-implement-json-serialization
stack: flutter
description: Implement manual JSON mapping with the project's existing model conventions. Use when manual `fromJson`/`toJson` mapping is requested or already established.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 21 Apr 2026 21:44:50 GMT
---

# Implement Manual JSON Mapping

Inspect neighbouring models, API contracts, and serialization tooling first. Use this skill only for manual mapping; preserve generated serializers or another established mapper when the project uses one.

## Mapping Rules

- Keep wire-format models separate from UI-only state when the project makes that distinction. Preserve field names, nullability, defaults, dates, enums, and nested structures from the contract.
- Decode into checked map/list shapes before reading values. Validate required fields and incompatible types with a useful `FormatException` or the project's typed parse failure.
- Treat optional and nullable API fields deliberately; do not coerce missing or invalid data into misleading defaults.
- Serialize only fields accepted by the endpoint and omit nulls only when the API contract calls for it.
- Keep conversion free of network and UI concerns. Use a top-level or static parser off the UI isolate only for demonstrated large parsing work.

## Verification

Add focused mapping tests when models have non-trivial fields, validation, defaults, nesting, or enum/date conversion. Cover a valid payload and the most meaningful malformed or missing-field case, then run the affected tests.

Do not introduce code generation, packages, or broad model rewrites solely for this task.
