---
name: subagent-workflow
description: Route planner/executor/reviewer roles and model tiers for non-trivial work.
---

Use for medium/large/risky/unclear work. Grill unclear requirements first.

## Route once

Use capability tiers, not vendor names. The live runtime decides the mapping (typically Claude: haiku/sonnet/opus; Codex: low/medium/high effort). If per-agent overrides are unavailable, use the closest available tier and say so.

| Task | Planner | Executor | Acceptance |
|---|---|---|---|
| Small, clear, ≤2 files | current/low | direct | self-check |
| Medium, bounded | standard; strong for architecture/ambiguity | economy for a frozen mechanical slice, otherwise standard | main reviews diff; add fresh review for behavior/contracts |
| Large/risky/multi-owner | strongest | standard; economy only for proven repetition | TL review + independent QA |

The planner owns scope, decisions, slice order, and checkable acceptance criteria. After one pattern is proven, hand each slice to the cheapest capable executor. Escalate economy→standard after one capability failure; standard→strongest after two, including failure evidence. Missing information is clarification, not model failure.

Roles: BA—business scope; TL—plan/architecture/review; developer—implementation/tests; DevOps—CI/release; security—auth/privacy; UX—states/a11y; QA—acceptance/regression.

## Permissions

- BA, TL, QA, security, and UX are read-only. Developer/DevOps write only inside assigned ownership.
- QA never creates or edits test files; automated-test authoring belongs to developers. QA may run existing suites as a check.

## Handoff

Every delegation contains: goal/why (≤3 sentences), owned files or read-only scope, ≤3 steps, numbered acceptance criteria, verification, and return format. Return only verdict, decisive `file:line`/test evidence, changed paths, and open items (≤20 lines). Put longer evidence in `reports/subagents/<task-slug>/` only for large work or output that cannot fit.

Parallelize independent ownership only. A developer reads nearby code, keeps the diff scoped, handles relevant states, runs narrow checks, and removes debug/dead/generated churn. TL reviews the actual diff, requirement fit first. Stop after three revision rounds.

Use at most one specialist review skill for medium work; use all directly relevant skills for large/risky work. TDD is for focused behavior risk. Security/data migrations/public APIs require fresh review. Figma work always follows `figma-design-to-code`.

No install, network, destructive action, or scope expansion without authority. Use project scripts and `.agents/tools/` only at relevant checkpoints.
