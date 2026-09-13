---
name: dart-generate-test-mocks
stack: dart
description: Generate Mockito mocks for existing build-runner test setups. Use only when Mockito and generated mocks are already used or explicitly requested.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Fri, 24 Apr 2026 15:13:58 GMT
---

# Generate Mockito Mocks

Inspect the target test, neighbouring tests, `pubspec.yaml`, and generator configuration first. Follow the project's test framework and mock style.

## Workflow

1. Mock only a boundary the test needs to control, such as an API, clock, storage adapter, or platform service. Prefer a real value object or small fake when it states the behavior more clearly.
2. Inject the dependency through the existing seam; do not change production architecture solely to satisfy a mock generator.
3. Add or update the existing Mockito annotation and generated import following nearby tests. Do not hand-edit `.mocks.dart` files.
4. Stub every asynchronous method with an asynchronous answer and test both the meaningful result and failure behavior.
5. Verify interactions only when they are part of the contract; assert observable output and state first.
6. Run the project's generator for the narrowest target supported, then run the affected test.

## Boundaries

- Do not add Mockito, build_runner, or other dependencies unless the user explicitly requests that setup.
- Do not generate mocks when the project uses another mock library, handwritten fakes, or integration tests instead.
- Keep generated output in source control only if the repository already tracks it.
