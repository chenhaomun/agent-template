---
name: dart-collect-coverage
stack: dart
description: Collect Dart/Flutter test coverage and produce an LCOV report. Use when coverage is requested or a coverage gate exists.
---

# Collect Coverage

Use the project's existing coverage script or CI job first. Report coverage as evidence, not as proof of correct behavior.

- Flutter: `flutter test --coverage` writes `coverage/lcov.info`.
- Dart: if `package:coverage` is already a dev dependency, run `dart run coverage:test_with_coverage` (pass explicit test directories in a workspace). Adding it is a new dev dependency and needs approval.
- Manual VM collection (`--enable-vm-service`, `coverage:collect_coverage`, `coverage:format_coverage --check-ignore`) only when branch or function coverage is required.

Rules:

- Keep `coverage/` output out of version control unless the project tracks it.
- Use `// coverage:ignore-line`, `ignore-start`/`ignore-end`, or `ignore-file` only for generated or genuinely untestable code, never to meet a threshold.
- When a file shows no coverage, check whether tests import and execute it before adding tests.

Report the command, overall and changed-file coverage, and any gaps in changed behavior.
