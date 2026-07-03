@AGENTS.md

Claude-only additions follow (shared rules are imported above).

## Memory

- User memory: `~/.claude/CLAUDE.md`. Project memory: this file.
- Read memory files only if they exist; never infer or fabricate memory from missing paths. If none exist, proceed without them.
- Surface a remembered preference only when it's relevant to the current task.
- Write to `~/.claude/projects/<project>/memory/` (create it if absent) when asked to remember, or when you learn a durable preference.

## Thinking

- Prefer extended thinking before complex, multi-step, or risky tasks.
- Surface key assumptions and risks before irreversible changes.

## Tool Use

- Prefer built-in tools (Read, Edit, Write, Glob, Grep, Bash) over shell one-liners for file ops.
- Track non-trivial multi-step work with `TaskCreate`/`TaskUpdate` so progress survives compaction.
- MCP servers are configured in `.claude/settings.json`.

## Skills & Subagents

`.claude/skills` and `.claude/agents` are copies of `.agents/skills` and `.agents/subagents`, refreshed by `make sync` (and at SessionStart). Edit only under `.agents/`, never the copies; `make check-template` fails on drift. Skills invoke as `/<name>`; subagents are Agent-tool targets.

## Review Mode

Subagents via the Agent tool:
- Read-only (BA, TL, Security, QA, UX): tool allowlist without Write/Edit.
- Write-capable (Developer, Flutter, Backend API, DevOps): edit only within explicit ownership.
