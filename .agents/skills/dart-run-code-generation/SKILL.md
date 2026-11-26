---
name: dart-run-code-generation
stack: dart
description: Regenerate Dart/Flutter generated files (`build_runner`, `gen-l10n`, ffigen, and similar) after editing their sources. Use when annotations, models, routes, mocks, ARB files, or generator config change, or generated output is stale.
---

# Run Code Generation

Generated files (`*.g.dart`, `*.freezed.dart`, `*.gr.dart`, `*.mocks.dart`, generated l10n) are never edited by hand. Change the source or generator config, then regenerate.

## Find the generator

- Check project scripts, `Makefile`, CI, and `build.yaml` first; use their command and the configured SDK wrapper (for example `fvm dart run build_runner build`).
- Match the output to its generator: `part '*.g.dart'` and `*.freezed.dart` come from `build_runner`; l10n from `flutter gen-l10n` or `flutter pub get`; FFI bindings from the project's ffigen script.
- Adding a generator package is a new dependency and needs approval.

## Run

- Prefer a single scoped build (`dart run build_runner build`, with `--build-filter` or a package directory in monorepos) over `watch`.
- On conflicting outputs, rerun with `--delete-conflicting-outputs` only after confirming the conflicts are generated files, never hand-written ones.
- Regenerate after merges or rebases that touched generated files, instead of hand-merging them.
- Keep generated output in version control only if the project already tracks it.

## Verify

Confirm the expected files changed and nothing unrelated was rewritten, then run analysis and affected tests. Report generator errors with the failing source file; do not silence them by editing output.
