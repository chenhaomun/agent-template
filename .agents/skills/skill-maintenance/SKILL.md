---
name: skill-maintenance
description: Check project-local vendored skills for upstream drift and refresh selected changes.
---

# Skill Maintenance

Run only when explicitly requested. `skills-lock.json` holds provenance for every skill. Edit sources, notes, and review fields by hand; In the template repository, `make -f .agents/Makefile sync` writes each `computedHash` (SHA-256 of the local skill folder) and `check-template` fails when one is stale or a skill has no entry; installed projects keep the installer-owned lock unchanged. Never commit automatically.

## Drift check

Clone each public source once into a task temporary directory, keeping history so `lastReviewedCommit` can be diffed. Skip local entries. Use an explicit pinned revision when supplied; otherwise inspect HEAD and record its exact commit and review date. Resolve local files using `localPath`, or `skillPath` under `.agents/`.

```sh
tmp=$(mktemp -d)
git clone --filter=blob:none https://github.com/flutter/agent-plugins "$tmp/flutter"
git clone --filter=blob:none https://github.com/dart-lang/skills "$tmp/dart"
git clone --filter=blob:none https://github.com/JuliusBrussee/caveman "$tmp/caveman"
```

- If a source repository was renamed or moved, update its lock `source` and the clone URL above.
- Diff each `skillPath` from `lastReviewedCommit` to the reviewed revision; review every changed `SKILL.md` and apply changes file by file.
- Preserve lock-documented local adaptations; do not restore upstream tutorials or mandatory architecture/packages merely to eliminate drift. Flutter/Dart entries keep local `stack:` and shortened descriptions; compare bodies and reapply local frontmatter after refresh. `caveman` keeps its shortened description and lock-documented body edits.
- Record `lastReviewedCommit`, `lastReviewedAt`, and intentional adaptations in the lock. Report unavailable sources without implying a completed comparison. Update matching UI descriptions when skill descriptions change.

All upstream Flutter/Dart skills are vendored. When upstream adds one, adapt it the same way (local `stack:`, short description, project-conventions-first body, approval gates) and add its lock entry.

After changes, run `make -f .agents/Makefile sync` and `make -f .agents/Makefile verify`. If make is unavailable, run the equivalent Python scripts and applicable project checks; report the substitution. Restart active agents if skill metadata remains stale.
