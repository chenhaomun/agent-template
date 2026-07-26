---
name: find-skills
description: Recommend skills that fit this project — scan the stack, installed skills, and gaps, then propose skills to add or enable. Use to discover or expand the skill set.
---

# Find Skills

Find skills that fit this project and propose them. This skill discovers and recommends; it does not install silently — installation goes through `skill-maintenance`.

## Steps

1. Detect the stack: `python .agents/tools/detect_project.py` (Flutter/Dart, Node, Python, …), and skim `.agents/project-map.md` for the shape of the code.
2. Inventory what already exists: active skills in `.agents/skills/`, deferred ones in `.agents/skill-packs/*/skills/`, and their `skills-lock.json` entries. Do not re-propose these.
3. Find gaps: recurring tasks or stack areas with no matching skill (e.g. testing, CI/release, localization, state management, data/serialization, review lenses). Weigh gaps against the work actually happening in this repo, not a generic checklist.
4. Source candidates for each gap from known upstreams and note provenance:
   - `dart-lang/skills`, `flutter/skills` (Flutter/Dart, already the primary stack)
   - `JuliusBrussee/caveman` (response/memory compression)
   - Anthropic and other reputable skill repos for cross-stack needs
5. Propose a shortlist: skill name, source, one-line why, and active vs. deferred (default rare/setup skills to a skill-pack to keep the always-loaded listing lean). Present it — do not install yet.

## Install (only after the user approves)

Hand chosen skills to `skill-maintenance` (its vendoring flow): add via the `skills` CLI or vendor manually, add a `skills-lock.json` entry (never fabricate `computedHash`), place under `.agents/skills/` or the right `.agents/skill-packs/`, then `make sync` and `make check-template`. Adding an installer/CLI dependency needs explicit user approval per AGENTS.md.

## Guardrails

- Recommend, then wait — no installs, dependencies, or network fetches without approval.
- Prefer a few high-fit skills over a long list; respect the template's lean-context discipline.
- Stack-specific skills should carry a `stack:` key so `sync_shared.py` gates them correctly.
