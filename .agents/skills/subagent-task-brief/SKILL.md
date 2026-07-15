---
name: subagent-task-brief
description: Turn requirements into a subagent-ready Task/Requirements/Verify brief.
---

Create a concise subagent task brief from raw requirements.

Rules:
- Keep business requirements separate from technical direction.
- Auto-use `grill-requirements` first when requirements risk rework (trigger conditions: AGENTS.md Work Rules).
- Include the handoff fields required by `subagent-workflow`.
- Make `Task` one clear outcome.
- Make `Requirements` business/product-focused bullets.
- Make `Verify` include useful commands and manual checks.
- Add `Suggested subagents` based on AGENTS.md routing.
- Add `Clarifying questions` only when blocked; max 3 by default.
- Do not invent technical implementation details.
- Use `$caveman lite`.

Output:

```text
Use subagents: <roles>.

Task:
<one clear outcome>

Requirements:
- <business/product requirement>
- <business/product requirement>

Verify:
- <command or manual check>
- <command or manual check>

Clarifying questions:
- <blocking question, or None>

Assumptions:
- <safe assumption, or None>
```
