---
name: skill-maintenance
description: Check project-local vendored skills for upstream drift and refresh selected changes.
---

# Skill Maintenance

Run only when explicitly requested. `skills-lock.json` is hand-maintained provenance: never fabricate `computedHash` values.

## Drift check

Clone pinned public sources into a temporary directory, then diff each lock entry against its `skillPath`. Use `localPath` when present.

```sh
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/flutter/skills "$tmp/flutter"
git clone --depth 1 https://github.com/dart-lang/skills "$tmp/dart"
git clone --depth 1 https://github.com/JuliusBrussee/caveman "$tmp/caveman"
```

- Review every changed `SKILL.md`; apply changes file by file.
- Flutter/Dart entries keep local `stack:` and shortened descriptions. Compare bodies when judging drift and reapply local frontmatter after refresh.
- `caveman` keeps its shortened description and any lock-documented local body edits.
- If content changes, report its stored hash as stale. External tooling required to regenerate it.
- Never commit automatically.

Rare skills are intentionally not vendored. Install one only when a project needs it, then add explicit provenance to the lock.

After changes, run `make sync`, `make check-template`, and tell the user to restart active agents if skill metadata remains stale.
