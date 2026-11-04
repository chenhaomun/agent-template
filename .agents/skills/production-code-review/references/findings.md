# Review Checks and Findings

## CI coverage

- Before running checks, inspect existing CI configuration (such as `.gitlab-ci.yml`, `.github/workflows/`, or equivalent) and relevant included jobs/scripts. Check triggers, path filters, commands, and targets; a config file alone does not prove a check covers this change.
- Avoid rerunning equivalent formatting, lint, analysis, test, build, or scan jobs covered by applicable CI. When available, use results for the reviewed commit; pending, skipped, stale, or inaccessible results are not passes. Report only material verification gaps.
- Run a focused local check only for uncovered risk, a concrete finding needing reproduction, CI failure diagnosis, changed CI configuration, or an explicit user request. With no applicable CI, use the narrowest relevant checks.
- Continue reviewing logic, requirements, architecture, and test quality. Do not repeat mechanical findings already reported by CI unless explaining their cause or impact adds useful review evidence; passing CI does not prove correctness.

## Findings

- Report proven, actionable problems only. Verify the trigger and impact in code and affected callers; style preferences and unmeasured suspicions are not defects.
- Use one bullet per cause, highest severity first: P0 critical, P1 high, P2 medium, P3 low.
- Write `[P1] file:line — What breaks and when. Smallest fix.` Aim for 30 words or fewer after the location; keep necessary conditions even if longer. Use everyday words and concrete outcomes, not abstract labels.
- Example: `[P1] checkout.dart:42 — Tapping Pay twice sends two charges. Disable Pay while the first request runs.`
- Link verified file/line locations. Anchor diff findings to changed lines; identify the reviewed ref if local lines differ.
- No praise, tables, or repeated summaries. If none, say “No actionable findings.” List material verification gaps separately; never imply unrun checks passed.
