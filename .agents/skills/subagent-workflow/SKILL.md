---
name: subagent-workflow
description: Route planner, executor, and reviewer roles for non-trivial work.
---

# Subagent Workflow

Use for medium, large, risky, or unclear work. Small clear work stays with the current agent.

## Route

- Medium: current agent plans; `developer` executes bounded behavior; main agent reviews.
- Large/risky: `team-lead` produces a read-only plan for user approval; `developer` owns implementation slices; `qa` verifies behavior.
- Repetitive frozen work: `economy-executor` only after a stronger agent proves the pattern. Escalate on the first decision or unexpected failure.
- Resolve business ambiguity with `grill-requirements` before delegation.

Use the strongest tier only for bounded planning/review. Prefer the cheapest capable executor after scope and pattern are fixed. Parallelize independent ownership only.

## Brief

Every delegation includes:

```text
Task: goal and why
Ownership: exact files or read-only scope
Requirements: observable behavior, states, constraints, non-goals
Steps: no more than three
Acceptance: numbered, checkable outcomes
Verify: exact narrow commands or scenarios
Return: verdict, decisive file/test evidence, changed paths, open items (20 lines max)
```

Anchor the brief to relevant paths and `.agents/project-context.md`. Agents read nearby code first, preserve other work, avoid scope expansion, and write only inside assigned ownership.

## Production Bar

Done means behavior matches requirements, diff stays scoped, project conventions and relevant states hold, verification ran or blocker is explicit, and no debug/dead/TODO churn remains.

Read-only roles never edit. QA may run existing tests but never writes automated tests. Developers own test changes. Security, migrations, and public contracts require fresh review. Stop after three revision rounds.
