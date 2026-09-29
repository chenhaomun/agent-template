# Review Findings

- Report proven, actionable problems only. Verify the trigger and impact in code and affected callers; style preferences and unmeasured suspicions are not defects.
- Use one bullet per cause, highest severity first: P0 critical, P1 high, P2 medium, P3 low.
- Write `[P1] file:line — What breaks and when. Smallest fix.` Aim for 30 words or fewer after the location; keep necessary conditions even if longer. Use everyday words and concrete outcomes, not abstract labels.
- Example: `[P1] checkout.dart:42 — Tapping Pay twice sends two charges. Disable Pay while the first request runs.`
- Link verified file/line locations. Anchor diff findings to changed lines; identify the reviewed ref if local lines differ.
- No praise, tables, or repeated summaries. If none, say “No actionable findings.” List material verification gaps separately; never imply unrun checks passed.
