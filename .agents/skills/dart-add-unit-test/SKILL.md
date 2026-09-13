---
name: dart-add-unit-test
stack: dart
description: Write unit tests with `package:test`. Use when adding new logic or fixing bugs.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Fri, 24 Apr 2026 15:07:58 GMT
---

# Dart Unit Tests

Use existing test packages, naming, helpers, and fake/mock conventions; Flutter projects may use flutter_test. Do not introduce a new library just for this skill.

1. Identify the observable contract and relevant success, boundary, and failure cases.
2. For changed behavior, add the smallest regression test and confirm it fails for the intended reason before fixing.
3. Implement and run the affected test file through the project SDK wrapper; broaden for shared behavior.

- Test behavior rather than private methods, incidental call order, or mirrored implementation.
- Reuse controllable dependencies; avoid real network, wall-clock delays, and shared mutable fixtures.
- Await asynchronous expectations and exercise errors, stale responses, and state transitions where relevant.
- Use simple fakes when sufficient. Generate mocks only when already used or authorized.
- Keep fixtures small and release resources in teardown. Report checks and material gaps briefly.
