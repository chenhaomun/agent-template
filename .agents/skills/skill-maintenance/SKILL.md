---
name: skill-maintenance
description: >
  Refresh and review project-local agent skills. Use when the user asks to update,
  refresh, install, or keep skills current, or asks to run skill maintenance for this template.
---

# Skill Maintenance

Keep skills current like vendored dependencies. Run only when the user invokes this skill.

## How the lock works (read first)

`skills-lock.json` is **hand-maintained**. The `skills` CLI does not read or write it, and `computedHash` is **not** a plain `sha256` of `SKILL.md` — it is produced by external tooling not present in this repo, so it cannot be regenerated here. Do **not** fabricate hashes. Treat the lock as a version pin + provenance record; verify drift by content diff, not by recomputing hashes.

`sourceType: github-adapted` entries (e.g. `caveman-compress`) are local-only and intentionally diverge from upstream — **exclude them from any refresh.**

## Refresh (drift check — canonical, no mutation)

Invocation is the command. Run this immediately when the skill is mentioned; rely on system approval prompts for the network clone. Clone each upstream source to a temp dir and diff against the vendored `SKILL.md` files — this is reliable regardless of `skills` CLI version:

```sh
TMP=$(mktemp -d)
git clone --depth 1 https://github.com/flutter/skills      "$TMP/flutter"
git clone --depth 1 https://github.com/dart-lang/skills     "$TMP/dart"
git clone --depth 1 https://github.com/JuliusBrussee/caveman "$TMP/caveman"
# For each non-"github-adapted" skill in skills-lock.json, diff:
#   diff -u .agents/<skillPath>  "$TMP/<repo>/<skillPath>"
```

Apply only the diffs you want, file by file. Leave `caveman-compress` untouched.

## Refresh (optional, via skills CLI)

If you instead use the `skills` CLI (v1.5.x), the correct flags are `--skill`/`-s` and `--agent '*'` (there is **no** `universal` agent), with `--copy` so files land as copies, not symlinks:

```sh
npx skills add flutter/skills      --skill '*' --agent '*' --copy -y
npx skills add dart-lang/skills    --skill '*' --agent '*' --copy -y
npx skills add JuliusBrussee/caveman --skill caveman --agent '*' --copy -y
# Do NOT add caveman-compress — it is local-only/github-adapted.
```

Verify the install target afterward (the CLI may write to a different layout) and reconcile into `.agents/skills/` if needed.

## Review

- Diff vendored vs upstream per the canonical drift check above; review every changed `SKILL.md`.
- Investigate installer high-risk flags before use.
- Re-check `caveman-compress` stays local-only: no external model API, external agent CLI, or network path.
- After a Flutter/Dart refresh, merge only portable guardrails from https://docs.flutter.dev/ai/ai-rules into the `## Flutter` section of `AGENTS.md`.
- If a skill's content changes, its `computedHash` becomes stale and cannot be regenerated here — flag it for the user rather than inventing a value.
- Do not commit automatically.
- Tell user to restart the agent after skill changes if metadata does not refresh.
