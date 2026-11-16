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

Prioritize clarity over a fixed sentence count. Use concise paragraphs or bullets with enough technical context to explain the failure. Omit category and evidence sections; verification still supports the conclusions.

- **Cause:** explain the trigger, failed rule/state/contract, and user impact. Include relevant uncertainty naturally in the explanation.
- **Fix direction:** smallest corrective change and regression check; label it proposed.
- **Introducing commit / author:** SHA, subject, and recorded Git author name, with the parent comparison supporting attribution. This identifies a code change, not personal fault. If evidence is incomplete, say “Unconfirmed” and label candidates as suspects. Missing/shallow history or a configuration/backend cause may prevent commit attribution.

Keep the commit/author conclusion last. Do not expose author email addresses or claim the ticket assignee, committer, merger, or last line editor caused the bug. Separate the technical cause from how it escaped tests when both are requested. External updates require approval of the exact summary and fields.
