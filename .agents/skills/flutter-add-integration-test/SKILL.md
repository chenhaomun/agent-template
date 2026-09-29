---
name: flutter-add-integration-test
stack: flutter
description: Write Flutter app-flow integration tests by default for features, regression fixes, and architecture changes; run focused coverage using project tooling.
---

# Flutter Integration Tests

Use automatically for Flutter feature implementation, regression fixes, and architecture changes. Add or update tests for affected app flows; reuse existing coverage when it already proves the required behavior. Documentation-only work and changes with no executable flow need no artificial integration test; state the reason briefly.

## Setup

- Inspect `pubspec.yaml`, SDK wrappers, flavors, app bootstrap, `integration_test/`, fixtures, and test/CI scripts. Reuse the existing harness and dependency overrides; do not replace established tooling.
- If no harness exists, add minimal `integration_test` and `flutter_test` dev dependencies from `sdk: flutter`, using the configured SDK. Keep tests in `integration_test/`. This setup is authorized by the template; ask before third-party packages, native tooling/downloads, or new services.
- For SDK integration tests, initialize `IntegrationTestWidgetsFlutterBinding.ensureInitialized()` before tests and launch the real app through its existing test entrypoint/bootstrap. Preserve required async initialization, routing, localization, and state wiring. Do not create a fake app that bypasses the changed path.

## Write

1. Identify an observable journey and acceptance criteria. For a regression, reproduce the failing journey before fixing; distinguish the intended assertion failure from setup failure. For architecture changes, establish passing behavior coverage before refactoring and keep it passing afterward.
2. Exercise the actual UI and connections between affected layers. Assert meaningful results after actions: navigation, visible state, persisted/reloaded data, or recovery. Prefer stable keys/semantics; avoid assertions tied to widget nesting or private methods.
3. Cover the main success path and changed failure/boundary paths. Add relevant loading, empty, permission, disabled, back-navigation, or retry behavior without duplicating every unit/widget case.
4. Use isolated fixtures and controllable network/time at external boundaries. Keep affected internal layers real; disclose fake service boundaries so coverage is not mistaken for live backend/native verification. Never use production accounts, payments, or shared mutable data. Clean up only test-owned state and resources.
5. Await interactions and use bounded, condition-based waits. Avoid arbitrary sleeps or unlimited retries; use `pumpAndSettle` only when animations can finish. Native permission dialogs need existing platform automation; report unsupported interactions instead of pretending widget finders cover them.

## Verify

- Run the affected file first through project scripts, SDK wrapper, flavor, and configured test environment. For a standard native SDK setup, adapt `flutter test integration_test/<flow>_test.dart -d <device-id>` to verified project settings. Web and custom harnesses use their established runners.
- Format touched Dart, analyze affected code, and run relevant unit/widget tests. Broaden integration coverage for changed shared routes, bootstrap, persistence, or contracts.
- If a required device, credential, or environment is unavailable, still complete the test code and available checks; report the exact blocker and pending command. Never call a skipped test passing or substitute static analysis for a device run.
- Report the journey covered, target/environment, results, and material gaps. Do not modify unrelated CI or add a full test matrix for a scoped change.

SDK reference when setup details are needed: [Flutter integration testing](https://docs.flutter.dev/testing/integration-tests). Prefer the project's pinned SDK conventions over newer examples.
