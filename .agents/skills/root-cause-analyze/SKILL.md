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
4. Read the ticket's root-cause category and applicable field options when available. Preserve an existing category's exact label as the ticket's value; if it conflicts with the findings, briefly note that in RCA. If unset but options exist, select a supported exact label and mark it proposed. Never invent categories or update the ticket automatically.
5. Estimate the corrective mobile work using the shared [sprint-point guide](../draft-user-stories/references/sprint-points.md). Include implementation and regression validation complexity, effort, and uncertainty—not investigation time, hours, or line count. Use a Fibonacci value; 21 signals work needing breakdown, not permission to create tickets.

## Return

Return rendered Markdown with every label and its colon bolded; do not wrap the response in a code block. No hyperlinks or investigation recap. Omit Root Cause Category when neither a ticket value nor a supported choice from its options is available:

```markdown
**RCA:** <Brief explanation of the trigger, faulty logic in the relevant file/method, and user impact.>

**Root Cause Category:** <Exact ticket label, or proposed label from its options>

**Sprint Point:** <n>

**Caused By:** `<commit>` - <author name>
```

Keep the RCA brief and clear, without a fixed sentence limit. Include the relevant filename and method when verified, plus the condition or state that caused the failure. Connect that logic to the user impact. Use inline backticks for filenames/paths, classes, widgets, methods/functions, variables, properties, enum values, and code expressions; keep ordinary prose and author names unformatted. Omit code dumps, unnecessary call chains, and detailed history. Do not add fix direction, uncertainty, or evidence sections.

Always include the estimate as `**Sprint Point:** n`, replacing `n` with the chosen number. Keep sizing rationale internal unless requested; do not change the ticket's stored points.

Use a verified, unambiguous short commit SHA and its recorded Git author name. Omit the commit subject, author email, and proof narrative. Verification remains required internally; never attribute the bug to the assignee, committer, merger, or last editor without causal proof. If attribution cannot be verified, use `**Caused By:** Unconfirmed` rather than guessing; qualify an unverified cause briefly within RCA. External updates still require approval of the exact text and fields.
