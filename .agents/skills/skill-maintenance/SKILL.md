---
name: skill-maintenance
description: Check project-local vendored skills for upstream drift and refresh selected changes.
---

# Skill Maintenance

Run only when explicitly requested. `skills-lock.json` is hand-maintained provenance: never fabricate `computedHash` values.

## Drift check

Clone each public source once into a task temporary directory. Skip local entries. Use an explicit pinned revision when supplied; otherwise inspect HEAD and record its exact commit and review date. Resolve local files using `localPath`, or `skillPath` under `.agents/`.

```sh
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/flutter/skills "$tmp/flutter"
git clone --depth 1 https://github.com/dart-lang/skills "$tmp/dart"
git clone --depth 1 https://github.com/JuliusBrussee/caveman "$tmp/caveman"
```

- Review every changed `SKILL.md`; apply changes file by file.
- Use `lastReviewedCommit` to compare upstream changes since the previous review when available. Preserve lock-documented local adaptations; do not restore upstream tutorials or mandatory architecture/packages merely to eliminate drift.
- Flutter/Dart entries keep local `stack:` and shortened descriptions. Compare bodies when judging drift and reapply local frontmatter after refresh.
- `caveman` keeps its shortened description and any lock-documented local body edits.
- If content changes, report its stored hash as stale. External tooling required to regenerate it.
- Record `lastReviewedCommit`, `lastReviewedAt`, and intentional adaptations in the lock. Report unavailable sources without implying a completed comparison. Update matching UI descriptions when skill descriptions change.
- Never commit automatically.

Rare skills are intentionally not vendored. Install one only when a project needs it, then add explicit provenance to the lock.

After changes, run `make -f .agents/Makefile sync` and `make -f .agents/Makefile verify`. If make is unavailable, run the equivalent Python scripts and applicable project checks; report the substitution. Restart active agents if skill metadata remains stale.
