---
name: dart-build-cli-app
stack: dart
description: Build or change Dart command-line tools - entrypoints, `package:args` parsing, exit codes, stdout/stderr, subprocesses, signals, and tests. Use for CLI tools and scripts; not for Flutter UI or HTTP servers.
---

# Dart CLI Apps

Follow the package's existing layout, argument library, and test helpers. New packages (`io`, `cli_util`, `test_process`, and similar) need approval.

## Structure

- Keep `bin/*.dart` a thin entrypoint (`exitCode = await runCli(args);`); put commands and logic in `lib/src/` so they unit-test in memory.
- Declare commands under `executables:` in `pubspec.yaml`.
- Use `ArgParser` for simple tools and `CommandRunner<int>` with `Command<int>` for subcommands. Read options with `results.flag/option/multiOption`.

## Exit and output

- Set `exitCode` or return it from the runner; avoid `exit(n)`, which skips `finally`, drops buffered output, and breaks coverage. Use standard codes: 0 success, 64 usage, 65 data, 70 software, 78 config.
- Results to `stdout`; errors, warnings, and logs to `stderr`. On a usage error write the message and usage to `stderr` and return 64; print usage to `stdout` only for `--help`.
- Emit ANSI codes only when `stdout.hasTerminal`, `supportsAnsiEscapes`, and no `NO_COLOR`. With `--json`/`--machine`, keep `stdout` machine-readable.
- Keep caches under `.dart_tool/<package>/`.

## Processes and signals

- Do not assume `Platform.resolvedExecutable` is `dart`; AOT binaries point to themselves. Use the project's SDK resolution (for example `cli_util`).
- Guard `ProcessSignal.sigterm` on Windows. Restore terminal echo/line mode and cursor visibility, and close servers, on exit or interrupt.

## Verify

Unit-test commands in memory; add subprocess tests for exit codes and stream routing where the project already has them. Run analysis and report any platform not exercised.
