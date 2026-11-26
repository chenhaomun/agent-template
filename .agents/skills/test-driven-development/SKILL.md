---
name: test-driven-development
description: Use focused failing tests for clear behavior changes: bugs, validation, business logic, mappers, services, or state.
---

# Test Driven Development

Apply automatically when expected behavior is testable. Skip strict TDD for trivial styling/copy/config, generated files, exploratory refactors, or unclear requirements. Inspect contracts before asking about a genuine blocker.

1. State observable behavior; add the smallest test demonstrating it is missing/broken.
2. Run that test and verify the intended assertion fails, not setup.
3. Make the smallest compatible fix; refactor only after it passes.
4. Re-run focused tests and relevant analysis, expanding for shared risk.

Use existing libraries, helpers, fixtures, and conventions. Prefer unit tests for logic/mappers/services/state, widget/component tests for rendering/interactions, and integration tests for full flows. Use property-based tests for invariants over wide input ranges when the project already has a library. Flutter flow coverage follows `flutter-add-integration-test` and AGENTS.md's default triggers/setup authorization; other new harnesses require approval.

Report behavior covered, actual checks, and material gaps without repeating this workflow.
