---
name: subagent-workflow
description: Route planner/executor/reviewer roles and model tiers for non-trivial work.
---

Use for medium/large/risky/unclear work. Grill unclear requirements first.

## Route once

Use capability tiers, not vendor names. The live runtime decides the mapping (typically Claude: haiku/sonnet/opus; Codex: low/medium/high effort). If per-agent overrides are unavailable, use the closest available tier and say so. A user's explicit model choice overrides this routing.

The main loop runs a standard model and orchestrates; escalate to the strongest model only inside a bounded planning burst (`team-lead`). The economy tier is the `economy-executor` agent (haiku / low effort) — use it only for a frozen mechanical slice after the pattern is proven, and escalate it to a standard executor on one capability failure.

| Task | Planner | Executor | Acceptance |
|---|---|---|---|
| Small, clear, ≤2 files | current/low | direct | self-check |
| Medium, bounded | standard; strong for architecture/ambiguity | `economy-executor` for a frozen mechanical slice, otherwise standard | main reviews diff; add fresh review for behavior/contracts |
| Large/risky/multi-owner | strongest | standard; `economy-executor` only for proven repetition | TL review + independent QA |

For large/risky/unclear work, the planner presents its plan — scope, slice order, acceptance criteria — for user approval before any code is written; small, clear work proceeds directly. The planner owns scope, decisions, slice order, and checkable acceptance criteria. After one pattern is proven, hand each slice to the cheapest capable executor. Escalate economy→standard after one capability failure; standard→strongest after two, including failure evidence. Missing information is clarification, not model failure.

Roles: BA—business scope; TL—plan/architecture/review; developer—implementation/tests; economy-executor—frozen mechanical slices only; QA—acceptance/regression. For security/privacy, UX/a11y, and CI/release, the owning developer or TL runs the matching review skill (e.g. `security-review`) — there is no dedicated subagent.

Production Bar (the `done` criteria every executor self-checks before reporting): behavior matches the requirement, diff scoped, project conventions and relevant states handled, verification ran or blocker stated, no debug/dead/TODO/churn.

## Permissions

- BA, TL, and QA are read-only. Developers write only inside assigned ownership.
- QA never creates or edits test files; automated-test authoring belongs to developers. QA may run existing suites as a check.

## Handoff

Every delegation contains: goal/why (≤3 sentences), owned files or read-only scope, ≤3 steps, numbered acceptance criteria, verification, and return format. For large or fan-out work also pass anchor context — the concrete relevant paths and the matching `.agents/project-map.md` area — so the executor starts from the planner's exploration instead of rediscovering it. Return only verdict, decisive `file:line`/test evidence, changed paths, and open items (≤20 lines). Put longer evidence in `reports/subagents/<task-slug>/` only for large work or output that cannot fit.

Every subagent orients from the brief's anchor context first, then `.agents/project-map.md`; run broad grep/glob only when those miss, and report the gap so the planner can fix the brief. Parallelize independent ownership only. A developer reads nearby code, keeps the diff scoped, handles relevant states, runs narrow checks, and removes debug/dead/generated churn. TL reviews the actual diff, requirement fit first. Stop after three revision rounds.

Use at most one specialist review skill for medium work; use all directly relevant skills for large/risky work. TDD is for focused behavior risk. Security/data migrations/public APIs require fresh review. Figma work always follows `figma-design-to-code`.

No install, network, destructive action, or scope expansion without authority. Use project scripts and `.agents/tools/` only at relevant checkpoints.
