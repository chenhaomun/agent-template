---
name: dart-use-ffigen
stack: dart
description: Generate Dart FFI bindings with `package:ffigen` instead of hand-writing them. Use with approval when adding or extending C/Objective-C/Swift bindings.
---

# Generate FFI Bindings

Native/FFI work needs explicit approval (AGENTS.md). Follow an existing generator config if the package has one.

## Rules

- Never hand-write `DynamicLibrary.lookup`, `@Native` externals, or struct classes when headers exist; generate them.
- Keep the generator at `tool/ffigen.dart` (or the project's existing config). Resolve paths from `Platform.script.resolve('../')`.
- Keep third-party headers under `third_party/` and generated bindings under `lib/src/third_party/` with a `.g.dart` suffix.
- Include only the symbols needed (`Functions.includeSet({...})` or `include` filters); everything else stays excluded.
- Set an `Output.preamble` carrying the native library's license, a generated-file warning, and any `ignore_for_file` needed for generated lints. Do not change global lint rules.
- When native assets tree-shake, set `recordUse: (_) => true` and a `recordUseMapping` `.g.dart` output.

## Verify

Run the generator, keep regenerated output only when it changed (do not commit), and run analysis. Never edit generated bindings by hand; report generator errors with the failing header and options.
