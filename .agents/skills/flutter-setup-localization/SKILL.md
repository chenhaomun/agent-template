---
name: flutter-setup-localization
stack: flutter
description: Set up or extend Flutter localization with `flutter_localizations`, `intl`, ARB files, and generated `AppLocalizations`. Use when adding l10n to a project or adding/changing localized strings.
---

# Flutter Localization

Inspect `pubspec.yaml`, `l10n.yaml`, existing ARB files, and how the app reads strings. Extend the existing setup; follow its key naming, file locations, and generated import path.

## Setup (only when the project has none)

1. Add `flutter_localizations` (`sdk: flutter`) and `intl` at the version the Flutter SDK pins; set `flutter: generate: true`.
2. Create `l10n.yaml` with `arb-dir`, `template-arb-file`, and `output-localization-file`. Use the output location the SDK version supports; recent SDKs generate into the source tree rather than the deprecated `flutter_gen` synthetic package.
3. Add `AppLocalizations.delegate` and the Global Material/Widgets/Cupertino delegates plus `supportedLocales` to the app root.

Adding localization packages is a new dependency setup; confirm it is in scope.

## Strings

- Add every new key to the template ARB with an `@key` description. Add other locales only from provided translations; otherwise leave them missing (gen-l10n falls back and lists untranslated keys) and report the gap. Never hard-code user-facing text that the project localizes.
- Use typed placeholders, `plural` (with `other`), and `select` instead of string concatenation. Keep exact approved copy.
- Read strings with `AppLocalizations.of(context)` below the app root; do not hand-edit generated localization files.

## Verify

Regenerate (`flutter gen-l10n` or `flutter pub get` per project setup), fix ARB errors, run analysis and affected widget tests, and check long translations for overflow and text scaling.
