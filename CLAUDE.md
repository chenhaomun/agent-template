@AGENTS.md

Claude-only additions; shared rules are imported above.

## Working Style

- Use extended thinking when complexity or risk warrants it; use built-in file tools for edits.
- Track non-trivial work so it survives compaction.

## Response Length

- Default to 1–3 short sentences or up to 3 bullets. State outcome and verification; mention blockers when present.
- Expand for requested detail, safety, tradeoffs, or distinct actionable findings. Keep progress updates to one sentence.

## Skills & Subagents

`.claude/skills` and `.claude/agents` resolve to `.agents/`. Edit sources only; run `make sync` and `make check-template`.
