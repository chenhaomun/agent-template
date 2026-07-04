# Deferred Flutter/Dart skills (opt-in)

These skills are vendored but kept **out of the always-loaded set** to save context tokens. Claude loads every skill description in `.claude/skills` on each session; the skills below are rarely needed, one-time setup, or heavy (e.g. `dart-setup-ffi-assets` is ~650 chars on its own), so they live here instead.

Their guidance is unchanged — only their *availability* is deferred. Nothing about code quality changes; you just enable one when a task actually needs it. (Everyday skills — tests, mocks, layout, architecture, JSON, HTTP, analysis — stay always-on in `.agents/skills/`.)

| Skill | Enable when you are |
|---|---|
| `dart-setup-ffi-assets` | compiling/packaging C/C++ as Dart native assets |
| `dart-use-ffigen` | generating FFI bindings |
| `dart-build-cli-app` | building a Dart command-line app |
| `dart-migrate-to-checks-package` | migrating tests from `matcher` to `checks` |
| `flutter-add-widget-preview` | adding interactive widget previews |
| `flutter-add-integration-test` | adding integration/driver tests |
| `dart-use-pattern-matching` | refactoring toward switch expressions/patterns |
| `dart-collect-coverage` | producing an LCOV coverage report |
| `dart-resolve-package-conflicts` | fixing a failing `pub get` version conflict |
| `flutter-setup-localization` | wiring l10n for the first time |
| `flutter-setup-declarative-routing` | introducing `go_router`/URL routing |

## Enable one for a task

```sh
mv .agents/skill-packs/flutter-dart/skills/<name> .agents/skills/<name>
make sync          # copies it into .claude/skills so Claude can load it
```

Move it back here when done to keep the always-on set lean (then `make sync` again).

## After an upstream refresh

`skill-maintenance` with `--skill '*'` reinstalls **all** flutter/dart skills into `.agents/skills/`. After refreshing, move the skills in the table above back into this folder so they stay deferred (their `localPath` in `skills-lock.json` points here), then `make sync`. The drift check should diff deferred skills against this path, not `.agents/skills/`.
