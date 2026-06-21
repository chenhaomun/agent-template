# Flutter rules (append to AGENTS.md when the pack is enabled)

Paste the sections below into your project's `AGENTS.md` after the shared rules.

## Commands / Verify (Flutter)

- Common: `flutter analyze`, `flutter test`, `flutter run --dart-define-from-file=.env.dev.json`, `flutter build <target> --dart-define-from-file=.env.prod.json`.
- Prefer Dart/Flutter MCP for analyzer, symbols, fixes, format, tests, pub.dev, dependencies, and running-app/widget inspection.

## Flutter

- Check `analysis_options.yaml` and `.agents/flutter-dependencies.md`.
- Prefer composition, immutable widgets, `const`, pure/fast `build()`, lazy lists, and off-UI-thread expensive work.
- Keep null safety; avoid `!` unless guaranteed. Use project logging, theme/assets/tokens, l10n, responsive/a11y, platform parity, permissions, and fallbacks.
- Cover loading, success, empty, error, disabled, and permission states. Keep errors actionable.
- Use configured flavors and `--dart-define-from-file`.
- Native/FFI/binary downloads require explicit user approval and hash/offline fallback review.
