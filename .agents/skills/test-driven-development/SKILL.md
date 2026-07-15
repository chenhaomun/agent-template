---
name: test-driven-development
description: Use focused failing tests for clear behavior changes: bugs, validation, business logic, mappers, services, or state.
---

# Test Driven Development

Use TDD automatically when expected behavior is clear enough to test. Do not wait for the user to say "TDD" or invoke this skill explicitly.

Do not use strict TDD for trivial UI styling, copy/config edits, generated files, exploratory refactors, or ambiguous requirements.

Project conventions win over examples. Use existing test libraries, helpers, mocks, fixtures, naming, and folder layout.

## Loop

| Step | Action |
|---|---|
| 1. Behavior | State the exact behavior under test in one sentence |
| 2. Red | Add/update the smallest failing test that proves the behavior is missing or broken |
| 3. Run narrow | Run only the new/changed test first |
| 4. Green | Implement the smallest project-compatible change to pass |
| 5. Refactor | Clean duplication or naming only after the test passes |
| 6. Verify | Re-run the focused test, then the narrow relevant linter/test command |

If the test cannot be written because requirements are unclear, stop and ask BA/TL for clarification instead of guessing.

## Test Choice

| Behavior | Prefer |
|---|---|
| Pure logic, mappers, validators, use cases | Unit test |
| Service/state events and state transitions | Unit test using existing project pattern |
| Repository behavior with dependency | Unit test with existing mock/fake style |
| Component rendering or interaction | Component/widget test |
| Full navigation/user flow | Integration/E2E test only when existing or requested |

Do not introduce a new testing package, mocking library, or integration harness without approval.

## Report

When done, report:

| Field | Content |
|---|---|
| TDD | used / skipped with reason |
| Red test | file and behavior |
| Verification | focused test and final narrow check |
| Gaps | untested risk or blocker |
