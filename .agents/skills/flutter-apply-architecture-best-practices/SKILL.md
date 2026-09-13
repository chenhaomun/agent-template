---
name: flutter-apply-architecture-best-practices
stack: flutter
description: Plan or refine Flutter feature boundaries while preserving the project's established architecture. Use for new features or targeted refactors.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 21 Apr 2026 20:11:20 GMT
---

# Structure Flutter Features

Start with the feature's nearby code, state-management approach, dependency wiring, and tests. Extend existing conventions unless a refactor is explicitly requested.

## Design Guidance

- Keep widgets focused on rendering, input, and short-lived UI behavior. Put reusable business decisions and external I/O behind the boundaries the project already uses.
- Create a new layer, repository, use case, controller, or provider only when it has a clear owner, reuse case, or testability benefit. Do not impose MVVM, `ChangeNotifier`, dependency injection, or a directory layout.
- Model asynchronous states explicitly where the UI can observe them: loading, data, empty, error, and disabled or permission-limited states when relevant.
- Keep state immutable where practical. Avoid side effects in `build`, repeated requests on rebuild, and UI updates after a widget or controller is disposed.
- Give streams, controllers, subscriptions, focus nodes, and clients one clear owner and dispose or cancel them at the matching lifecycle boundary.

## Refactoring

1. Identify a concrete coupling, duplication, or lifecycle problem and its callers.
2. Make the smallest change that preserves public behavior and platform accessibility, localization, theming, and responsive layout.
3. Update affected consumers and focused tests together; avoid speculative abstractions or broad reorganizations.
4. Verify the feature's relevant success, loading, empty, and error paths.
