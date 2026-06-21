---
name: skill-maintenance
description: >
  Refresh and review project-local agent skills. Use when the user asks to update,
  refresh, install, or keep skills current, or asks to run skill maintenance for this template.
---

# Skill Maintenance

Keep skills current like vendored dependencies. Run only when the user invokes this skill.

## Refresh

Invocation is the command. Run the refresh batch immediately when this skill is loaded or mentioned. Do not reply "loaded", "awaiting command", or ask conversational confirmation first. Rely only on system approval prompts for network/install commands.

macOS/Linux:

```sh
npx skills add JuliusBrussee/caveman --skill caveman --agent universal
npx skills add JuliusBrussee/caveman --skill caveman-compress --agent universal
```

Windows PowerShell:

```powershell
npx.cmd skills add JuliusBrussee/caveman --skill caveman --agent universal
npx.cmd skills add JuliusBrussee/caveman --skill caveman-compress --agent universal
```

## Review

- Review `git diff -- .agents/skills skills-lock.json`.
- Review every changed `SKILL.md`.
- Investigate installer high-risk flags before use.
- Check unexpected lock-hash-only churn against actual skill diffs.
- Re-check `caveman-compress` stays local-only: no external model API, external agent CLI, or network path.
- Do not commit automatically.
- Tell user to restart the agent after skill changes if metadata does not refresh.
