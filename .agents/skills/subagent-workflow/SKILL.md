---
name: subagent-workflow
description: Route planner, executor, and reviewer roles for non-trivial work.
---

# Subagent Workflow

Use when independent work or specialist review justifies delegation overhead. Keep small or cohesive work with the current agent.

## Route

- Delegate bounded independent implementation to `developer` when it reduces latency or context load; avoid duplicating its investigation.
- For significant architecture or risk, use `team-lead` for bounded planning/review and `qa` for relevant functional checks. Seek approval only for unresolved scope or actions not already authorized.
- Repetitive frozen work: `economy-executor` only after a stronger agent proves the pattern. Escalate on the first decision or unexpected failure.
- Resolve business ambiguity with `grill-requirements` before delegation.

Choose capability by difficulty and failure cost, not price alone. Parallelize independent ownership only; use compact briefs and reuse results. The main agent owns integration and final verification.

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
