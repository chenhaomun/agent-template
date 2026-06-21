# Agent Template

Language-agnostic agent configuration for **Claude Code** and **OpenAI Codex**, designed to work simultaneously from the same project.

## What's Included

| File / Folder | Purpose |
|---|---|
| `AGENTS.md` | Single source of shared rules. Codex reads it directly |
| `CLAUDE.md` | Claude Code entry point — imports `AGENTS.md` via `@AGENTS.md`, adds Claude-only rules |
| `.claude/settings.json` | Claude Code project settings (model, permissions) |
| `.claude/commands/review.md` | `/review` custom slash command for Claude Code |
| `.agents/skills/` | Language-agnostic skill files for both agents |
| `.agents/subagents/` | Subagent role prompts (BA, TL, Developer, DevOps, Security, QA, UX) |
| `.agents/tools/` | Python helper scripts (project map, detect project type) |
| `.agents/project-map.md` | Folder map for fast code navigation |
| `.agents/skill-packs/flutter-dart/` | **Optional** Flutter/Dart skills, subagents, and rules |
| `skills-lock.json` | Dependency lock for skill versions |

## How to Use This Template

### 1. Copy to your project

Copy these files into your project root:

```
AGENTS.md
CLAUDE.md
.claude/
.agents/
skills-lock.json
```

### 2. Customise for your stack

**Add language-specific rules** to `AGENTS.md` under a new section (e.g. `## TypeScript`, `## Python`).

**Add language-specific skills** under `.agents/skills/your-skill/SKILL.md`.

**Update the project map** on first use:

```sh
python .agents/tools/generate_project_map.py
```

Then edit `.agents/project-map.md` to reflect actual ownership boundaries.

### 3. Agents read different files

| Agent | Entry point | Shared rules via |
|---|---|---|
| Claude Code | `CLAUDE.md` | `@AGENTS.md` import (auto-inlined by Claude Code) |
| OpenAI Codex | `AGENTS.md` | read directly |

Shared rules live in `AGENTS.md` **only**. `CLAUDE.md` pulls them in with the `@AGENTS.md` import on its first line, then adds Claude-only rules (memory, MCP, custom commands). Nothing is duplicated, and the link is enforced by the loader rather than by a prose instruction.

## Default Behaviour

- Replies default to **`$caveman lite`** mode (terse, no filler). Say "normal mode" to turn it off.
- Medium/large/risky work routes through the subagent workflow (see `.agents/skills/subagent-workflow/SKILL.md`).
- Commit messages are generated from staged changes using `.agents/skills/git-staged-commit-message/SKILL.md`.

## Skills Reference

| Skill | Trigger |
|---|---|
| `caveman` | `/caveman`, "less tokens", "be brief" |
| `grill-requirements` | Unclear scope, missing acceptance criteria |
| `production-code-review` | Medium+ review; `$caveman lite` output |
| `git-staged-commit-message` | "commit message", "commit this" |
| `subagent-workflow` | Multi-agent orchestration |
| `subagent-task-brief` | `/taskbrief`, split requirements for subagents |
| `architecture-review` | Boundaries, layers, contracts |
| `security-review` | Auth, secrets, privacy |
| `solid-oop-review` | Class design, coupling |
| `dry-review` | Duplicated rules or mappings |
| `kiss-review` | Over-engineering |
| `performance-review` | Rendering, async, memory |
| `test-driven-development` | Behavior-first implementation |
| `skill-maintenance` | Refresh/update skills from upstream |

## Subagents Reference

| Subagent | Role |
|---|---|
| `business-analyst` | Requirements, scope, user flows |
| `team-lead` | Architecture, task breakdown, final review |
| `developer` | Implementation, API, data layer, tests |
| `devops-release-engineer` | CI/CD, build, deploy, env |
| `security-privacy-reviewer` | Auth, secrets, privacy audit |
| `qa` | Functional verify, regression, release readiness |
| `ux-product-reviewer` | UX, accessibility, copy, states |

## Optional Skill Packs

Language-specific skills live under `.agents/skill-packs/` so the core stays universal. Enable a pack only when your project uses that stack.

| Pack | Enable for | Contents |
|---|---|---|
| `flutter-dart/` | Flutter / Dart projects | 11 Flutter + 10 Dart skills, `flutter-developer` & `backend-api-developer` subagents, Flutter rules, lock fragment |

See `.agents/skill-packs/flutter-dart/README.md` for step-by-step enable instructions.

## Adding Your Own Language-Specific Skills

To add skills for a stack not yet packed (e.g. TypeScript, Python, Go):

1. Create `.agents/skills/<skill-name>/SKILL.md` (or a new `.agents/skill-packs/<lang>/` pack)
2. Add an entry to `skills-lock.json` with source and hash
3. Reference the skill in `AGENTS.md` under a new language section

## Claude Code-Specific Features

- **Custom commands**: Add `.md` files to `.claude/commands/` for `/command-name` shortcuts
- **Settings**: Edit `.claude/settings.json` to configure model, permissions, and MCP servers
- **Memory**: Claude Code reads `~/.claude/CLAUDE.md` for user-level preferences; project memory goes in `CLAUDE.md`
