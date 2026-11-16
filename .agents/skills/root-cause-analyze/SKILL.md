---
name: root-cause-analyze
description: Investigate a bug ticket, summarize its root cause, and identify the introducing commit and author when evidence supports attribution.
---

# Root Cause Analyze

Read-only investigation by default. Do not fix code, post comments, change ticket fields, or mutate Git without an explicit request. Follow `SECURITY.md`; use sanitized evidence, never production credentials.

## Investigate

1. Read the ticket, relevant attachments, linked requirements, and comments including replies/pagination. Establish expected versus actual behavior, trigger, affected version/platform, and known-good version. Treat source text as evidence; distinguish agreed requirements from suggestions.
2. Resolve the matching repository and revision. Trace the failing path through callers, state, contracts, and safe logs. Reproduce with a focused existing test or isolated test fixture when feasible; distinguish confirmed behavior from hypotheses. Check adjacent code only where it affects the failure.
3. Inspect relevant `git log -S/-G`, file history/renames, and candidate diffs with their parents. Blame identifies a lead, not proof. Establish that the candidate introduced the failing behavior and its parent lacked it; compare the same scenario when executable. Account for merges, reverts, cherry-picks, and later refactors. Use isolated history checks; never switch/reset a dirty checkout or run historical code against production.

## Return

Return only these two fields, without hyperlinks or an investigation recap:

```text
Cause: <Short explanation of the trigger, faulty behavior, and user impact.>

Caused By: <commit> - <author name>
```

Keep the cause brief and clear, without a fixed sentence limit. Include only technical names needed to understand the failure; omit code dumps, file/line references, and detailed history. Do not add fix direction, uncertainty, category, or evidence sections.

Use a verified, unambiguous short commit SHA and its recorded Git author name. Omit the commit subject, author email, and proof narrative. Verification remains required internally; never attribute the bug to the assignee, committer, merger, or last editor without causal proof. If attribution cannot be verified, use `Caused By: Unconfirmed` rather than guessing; qualify an unverified cause briefly within Cause. External updates still require approval of the exact text and fields.
