@AGENTS.md

Claude-only additions; shared rules are imported above.

## Working Style

- Use extended thinking when complexity or risk warrants it; use built-in file tools for edits.
- Track non-trivial work so it survives compaction.

## Response Length

- Default to a direct answer in 1–3 short sentences, or at most 3 short bullets for parallel findings. For completed work, state the result and verification; mention blockers only when present.
- Do not restate the request, narrate routine tool calls, explain obvious edits, or add unsolicited tutorials, recommendations, recaps, or offers to continue.
- Keep progress updates to one sentence when a meaningful finding, delay, or blocker warrants it. Keep internal plans and checklists out of the response unless requested.
- Expand only when the user asks or essential correctness, safety, tradeoffs, or actionable review findings need more detail. Brevity limits presentation, not investigation or verification; never omit distinct defects to meet the default length.

## Skills & Subagents

`.claude/skills` and `.claude/agents` resolve to `.agents/`. Edit sources only; run `make sync` and `make check-template`.
