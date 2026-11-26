---
name: dart-migrate-to-checks-package
stack: dart
description: Migrate Dart tests from `package:matcher` `expect` to `package:checks`. Use only when the migration is requested or the project already uses `checks`.
---

# Migrate to package:checks

Adding `checks` is a new dev dependency and a test-style change; do it only on request and only for the files in scope.

## Workflow

1. Add `checks` as a dev dependency if missing.
2. Per file, replace `import 'package:test/test.dart';` with `package:test/scaffolding.dart` and `package:checks/checks.dart`. For an incremental migration also import `package:test/expect.dart`; remove it at the end so leftover `expect` calls fail to compile.
3. Translate assertions, then run analysis and the affected tests. A changed failure means a wrong translation until proven otherwise.

## Pitfalls

- Collections: `expect(list, [..])` compared deeply; use `.deepEquals`, not `.equals`. Cast `dynamic` JSON values to `List`/`Map` first.
- `reason:` becomes `check(because: '...', actual)`.
- `matches(r'..')` becomes `.matchesPattern(RegExp(r'..'))`; a `String` is literal.
- `isA<T>().having(f, 'n', m)` becomes `.isA<T>().has(f, 'n')` followed by a chained check.
- Sync `.throws<E>()` returns a subject to chain; async `await check(future).throws<E>((it) => ...)` needs a callback.
- `.isTrue()`/`.isFalse()` need non-nullable `bool`; use `.equals(true)` for `bool?`.
- Map keys use `.containsKey`. Extension types may need `check<int>(value)`.
- Every async check (`completes`, `throws`, `emits`) must be awaited.

## Common mappings

`same` to `identicalTo`; `hasLength(n)` to `.length.equals(n)`; `isNot(m)` to `.not((it) => ...)`; `anyElement`/`everyElement` to `.any`/`.every`; `isPositive` to `isGreaterThan(0)`; ranges to cascaded bounds; specific `throwsXError` to `.throws<XError>()`. Replace custom `Matcher` classes with `extension` methods on `Subject<T>` using `package:checks/context.dart`.
