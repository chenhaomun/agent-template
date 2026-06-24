---
name: subagent-workflow
description: Subagent workflow rules. Use to route subagents (BA/TL/dev/QA), choose models, write reports, manage multi-agent work.
---

Use only for medium, large, risky, or unclear work. Use `grill-requirements` first when requirements are unclear, missing acceptance criteria, missing target flow/state, contradictory, or likely to cause rework.

## Routing

BA: business scope. TL: architecture/refactor/ownership/risk. Developer: implementation, API, data, tests. DevOps: CI/build/release/env/deploy. Security: privacy/auth/permissions/secrets/payments. UX: accessibility/copy/states. QA: functional verify/manual QA/regression/risk.

## Model Choice

Use these default overrides:

| Role | Model |
|---|---|
| BA | `claude-haiku-4-5` |
| TL | `claude-opus-4-8` |
| Developer | `claude-sonnet-4-6` |
| DevOps | `claude-sonnet-4-6` |
| Security | `claude-sonnet-4-6` |
| UX | `claude-haiku-4-5` |
| QA | `claude-sonnet-4-6` |

Use stronger model only when complexity clearly needs it. If unavailable, use nearest capable model and record fallback in report.

## Permissions

- Read-only by default: BA, TL, QA, security, UX.
- Write-capable only with explicit ownership: Developer, DevOps.
- QA must not add test files unless the user asks for tests.
- Developers must not edit outside ownership without reporting why.
- Developers may add/update scoped tests when behavior is clear and regression risk justifies TDD.

## Execution

- Use one stable kebab-case `task-slug` for `reports/subagents/<task-slug>/` during the whole task.
- Flow: choose tier first. Medium single-owner may use TL -> developer -> quick TL review. Large/risky uses BA -> TL -> developer -> developer self-check -> TL review -> developer revision -> QA.
- TL review: spec compliance first, code quality/architecture second.
- Repeat TL loop until accepted; stop after 3 rounds.
- Each subagent starts with goal, scope, max 3 steps, verification.
- Parallelize only independent, non-overlapping work.

## Production Bar

Developer cannot report `done` unless behavior matches requirements, diff is scoped, project conventions hold, relevant states are handled, verification ran or blocker is stated, and no debug/dead/TODO/generated-file churn remains.

For large/risky or multi-agent work, TL runs final review before acceptance: accumulated changes, unresolved assumptions, verification, and relevant review-skill findings.

Gates: `USER_DECISION` ask; `CLARIFICATION` route BA/TL; `REVIEW_CHANGES` revise; `PRODUCTION_GAP` reject; `BLOCKED` report; `ACCEPTED` continue.

## Task Breakdown

For larger work, TL creates task rows with task, dependency, owner, requirement, verification. Prefer vertical slices; parallelize only non-overlapping ownership.

Generic slice order: data/model contracts → service/repository layer → business logic → presentation/UI → tests.

## Quality Tiers

| Tier | Use |
|---|---|
| Trivial | No subagent, no TDD/review skill |
| Small | Direct work + quick self-check |
| Medium single-owner | One developer, `production-code-review` only, max one specialist skill |
| Medium behavior risk | Add TDD only when focused test fits existing project |
| Large/risky/multi-agent | Full TL/dev/TL/QA loop and relevant specialist skills |

## Review Skills

| Skill | Use for |
|---|---|
| `production-code-review` | medium+ review |
| `grill-requirements` | unclear scope, missing acceptance, likely rework |
| `test-driven-development` | clear behavior changes with meaningful regression risk |
| `architecture-review` | boundaries, contracts, ownership, integration risk |
| `solid-oop-review` | class/refactor design, responsibility, coupling |
| `dry-review` | duplicated rules, mappings, setup, or drift-prone copy/paste |
| `kiss-review` | over-engineering, avoidable indirection, unnecessary abstraction |
| `security-review` | auth, privacy, permissions, secrets, network, dependency risk |
| `performance-review` | rendering, async work, memory, data processing, scaling |

Developer owns one bounded module or concern, reads nearby code/tests, states intended files before editing, and runs narrow verification after each slice. TL reviews actual diff, not reports only. Integrate after tier-matched review passes.

## Harness Tools

Use `.agents/tools/` at checkpoints, not every turn. Use the available Python command for the local OS (`python`, `python3`, or bundled runtime).

| Checkpoint | Tool |
|---|---|
| Task start, project type unclear | `<python> .agents/tools/detect_project.py` |
| Project map missing/empty/stale | Preview with `<python> .agents/tools/generate_project_map.py`; update via `apply_patch` |
| Before broad search or after map edits | `<python> .agents/tools/check_project_map.py` |

Keep output short. No install/network/destructive action without approval.

## Reports

Write reports under `reports/subagents/<task-slug>/`.

- `timeline.md`: time/order, role, action, decision, outcome.
- `<role>.md`; append `## Run N - <short reason>` for repeats.
- Table-based, under 80 lines.
- Omit files read unless essential evidence.
- Use `$caveman lite`.

Report fields: run heading, `Field/Report`, `Decision/Reason/Outcome`, `Step/Critical thinking/Outcome`.

## QA Without Tests

If tests do not exist or are not requested, QA uses static checks, app/manual scenarios, state checks, and nearby regression checks.

## Compact Timing

Compact before context gets heavy, before more than 2 subagents, after TL/dev review loops, and before QA. Update `timeline.md` first.
