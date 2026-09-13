---
name: flutter-add-widget-test
stack: flutter
description: Write `WidgetTester` tests verifying widget rendering and interactions (tap, scroll, text entry).
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 21 Apr 2026 21:15:41 GMT
---

# Flutter Widget Tests

Use the project's existing flutter_test setup, harness, fixtures, and state overrides. Add dependencies only when authorized.

1. Identify observable behavior and the changed state/interaction; reproduce regressions before fixing.
2. Build with required theme, localization, routing, and dependencies from the existing harness. Keep network and time deterministic.
3. Assert initial state, perform the action, pump the expected frame/duration, and assert visible results or callbacks.
4. Run the affected test file through the project SDK wrapper; broaden for shared widget changes.

- Prefer bounded pumps; pumpAndSettle can time out on perpetual animations and hide extra frames. Use it only when completion is expected.
- Test relevant loading/error/empty/disabled transitions and disposal/stale async behavior when changed.
- Check changed layouts at relevant constraints and text scales; restore view overrides and dispose test-owned resources.
- Scroll lazy items into view before interaction. Prefer stable semantic finders over incidental widget nesting.
- Reuse existing golden workflows when visual regression matters; do not introduce one for every styling change.
