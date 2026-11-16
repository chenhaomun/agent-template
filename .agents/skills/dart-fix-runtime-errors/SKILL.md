---
name: dart-fix-runtime-errors
stack: dart
description: Diagnose Dart runtime exceptions from a stack trace, fix the cause, and reproduce the affected flow.
---

# Fix Dart Runtime Errors

1. Capture the first relevant exception and stack from available runtime tools or sanitized user logs. Resolve the matching source/version; distinguish the original failure from cascading errors. Use `dart-run-static-analysis` for analyzer-only diagnostics.
2. Trace the failing value through callers, initialization, parsing, and async/lifecycle ownership. Correct the violated contract; do not silence failures with `!`, unchecked casts, `late`, broad catches, or meaningless defaults.
3. Add a focused regression check when behavior is reproducible. Preserve sound override/generic contracts, nullability, and meaningful error handling.
4. Reproduce the original action after the fix. Hot reload only when it can apply the change; restart for initialization/state changes and rebuild native changes. Report unavailable runtime validation separately from passing tests/analysis.

Use the project's SDK, test harness, and lint policy. Do not enable stricter lints, apply blanket fixes, or change unrelated code as part of crash diagnosis.
