# Project Map

Use this map before broad searches. Start with mapped folders and nearby tests.

## Areas

- agent-configuration
  - folders: .agents/skills, .agents/subagents, .claude, .codex
  - terms: skills, subagents, hooks, project map, device setup
  - notes: shared agent configuration plus Claude/Codex-specific adapters
- agent-tools
  - folders: .agents/tools, .agents/tests
  - terms: hooks, integrity, freshness, enforcement
  - notes: deterministic tests for agent tooling
- agent-ops
  - folders: .agents/ops
  - terms: harness diagnosis, Windows shell, make fallback
  - notes: deferred troubleshooting; routing lives in the subagent workflow skill

## Rules

- Keep area names stable and lowercase.
- Store folders, not exact file paths, unless one file is the whole area.
- Prefer nearest stable parent folders.
- Include test folders beside source folders when known.
- If a folder is missing or stale, fall back to `rg` and update the map.
