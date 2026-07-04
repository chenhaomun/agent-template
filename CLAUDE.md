@AGENTS.md

Claude-only additions follow (shared rules are imported above).

## Memory

- Read memory files only if they exist; never fabricate memory from missing paths. Surface a remembered preference only when relevant.
- Write durable preferences to `~/.claude/projects/<project>/memory/` (create if absent).

## Working Style

- Prefer extended thinking before complex, multi-step, or risky tasks; surface assumptions and risks before irreversible changes.
- Prefer built-in tools (Read, Edit, Write, Glob, Grep, Bash) over shell one-liners for file ops.
- Track non-trivial multi-step work with `TaskCreate`/`TaskUpdate` so progress survives compaction.

## Skills & Subagents

`.claude/skills` and `.claude/agents` are copies of `.agents/skills` and `.agents/subagents`, refreshed by `make sync` (and at SessionStart). Edit only under `.agents/`, never the copies; `make check-template` fails on drift. Skills invoke as `/<name>`; subagents are Agent-tool targets with tool access declared in their frontmatter (read-only reviewers get no Write/Edit).
