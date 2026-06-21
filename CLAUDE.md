# CLAUDE.md

Claude Code reads this file. Shared rules are imported below; Claude-specific additions follow.

@AGENTS.md

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

## Custom Commands

Custom slash commands live in `.claude/commands/`. Add project-specific commands there as `.md` files.

## Review Mode

When using subagents via the Agent tool:
- Read-only subagents: research, BA, security, QA.
- Write-capable subagents: only those with explicit file ownership.
- Match subagent roles to `.agents/subagents/` prompts.
