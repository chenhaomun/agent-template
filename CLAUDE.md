@AGENTS.md

Claude-only additions; shared rules are imported above.

## Memory

- Read memory only when relevant. Store Claude-only preferences there; shared rules and facts belong in `.agents/` or `AGENTS.md`.

## Working Style

- Prefer extended thinking for complex/risky planning and built-in file tools for edits.
- Track non-trivial work so it survives compaction. For harness errors, read `.agents/ops/diagnosis.md`.

## Skills & Subagents

`.claude/skills` and `.claude/agents` are generated from `.agents/`. Edit sources only; run `make sync` and `make check-template`.
