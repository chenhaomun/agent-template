---
name: grill-requirements
description: Automatically ask concise blocking clarification questions before planning or implementation when requirements are unclear, risky, broad, contradictory, missing acceptance criteria, missing target flow/state, or likely to cause rework, even if the user did not explicitly request clarification.
---

# Grill Requirements

Use automatically when missing information blocks a good plan. Do not question obvious or discoverable facts.

## Rules

- Ask max 3 blocking questions by default.
- If no blocking question exists, proceed and state safe assumptions.
- Ask business/product questions first; route technical questions to TL.
- Prefer one clear default assumption when safe.
- Do not ask about implementation if the user only gave business requirements.
- If repo inspection can answer it, inspect instead of asking.

## Question Types

| Need | Ask |
|---|---|
| Outcome | What should be true when this is done? |
| Scope | What is explicitly out of scope? |
| User flow | Which user/path/state must work first? |
| Edge state | What should happen for empty/error/permission/offline? |
| Acceptance | What check proves this is accepted? |

## Output

```text
Blocking questions:
1. <question>
2. <question>

Safe assumption:
- <assumption, or None>
```
