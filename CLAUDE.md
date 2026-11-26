@AGENTS.md

Claude-only additions; shared rules are imported above.

- Use extended thinking when complexity or risk warrants it; use built-in file tools for edits.
- Track non-trivial work so it survives compaction.
- `.claude/skills` and `.claude/agents` resolve to `.agents/`. Edit sources only, then run `make -f .agents/Makefile sync` and `make -f .agents/Makefile verify`.
