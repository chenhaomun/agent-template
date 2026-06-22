@AGENTS.md

<!-- Claude-only rules below; shared rules live in AGENTS.md (imported above). -->

## Memory

- User-level memory lives in `~/.claude/CLAUDE.md`. Project memory lives here.
- Use the memory system to remember user preferences, decisions, and recurring patterns. Surface relevant memories at the start of new sessions.
- Write to memory files under `~/.claude/projects/<project>/memory/` when the user asks you to remember something or when you learn a persistent preference.

## Thinking

- For complex, multi-step, or risky tasks, prefer extended thinking before acting.
- Surface key assumptions and risks before making irreversible changes.

## Tool Use

- Prefer built-in Claude Code tools (Read, Edit, Write, Glob, Grep, Bash) over shell one-liners for file operations.
- Use `TaskCreate`/`TaskUpdate` to track non-trivial multi-step work so progress survives context compaction.
- MCP tools are available for project-specific integrations. Check `.claude/settings.json` for configured servers.

## Skills & Subagents

Shared with Codex via symlinks: `.claude/skills` → `.agents/skills`, `.claude/agents` → `.agents/subagents`. Every skill is invocable as `/<skill-name>`; subagents are available to the Agent tool. Add new ones under `.agents/` so both tools get them.

## Review Mode

When using subagents via the Agent tool:
- Read-only subagents (BA, TL, Security, QA, UX) declare a tool allowlist without Write/Edit.
- Write-capable subagents (Developer, Flutter, Backend API, DevOps) edit only within explicit ownership.
- Subagent definitions live in `.agents/subagents/` (read via `.claude/agents`).
