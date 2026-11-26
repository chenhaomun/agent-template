---
name: flutter-add-widget-preview
stack: flutter
description: Add Flutter Widget Previewer `@Preview` entries for UI components. Use when the project's Flutter SDK supports `package:flutter/widget_previews.dart` and previews are requested or already used.
---

# Flutter Widget Previews

Check the pinned Flutter SDK supports `package:flutter/widget_previews.dart` and follow existing preview files, naming, and folders. Do not add previews to a project that does not use them unless asked.

## Write

- Annotate a top-level function, static method, or public constructor with no required arguments that returns a `Widget` or `WidgetBuilder`.
- Set only needed parameters: `name`, `group`, `size`, `textScaleFactor`, `wrapper`, `theme`, `brightness`, `localizations`. Give unconstrained widgets an explicit `size`.
- Reuse the app's theme, localization, and state wrappers instead of inventing new ones. Extract repeated setup into one custom `Preview` or `MultiPreview` subclass; override `transform()` only for runtime-derived values.
- Cover the states that matter (loading, empty, error, disabled, long text, dark mode) without one preview per trivial variant.

## Limits

- The previewer runs on web: no `dart:io`, `dart:ffi`, or native plugins in the preview path. Isolate them behind existing seams or fakes rather than changing production architecture.
- Use package-based asset paths for `dart:ui` `fromAsset` APIs. Annotation callbacks must be public and constant.
- Keep the `.widget_preview/` cache out of version control.

## Verify

Run `flutter widget-preview start` (or the IDE previewer) through the project SDK wrapper, confirm each preview renders, and fix console errors. If the previewer cannot run here, say so; analysis alone does not prove rendering.
