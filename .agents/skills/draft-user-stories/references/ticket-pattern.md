# User-story pattern

Repeat the story section for each outcome. Group each story statement and scenario into a compact block. Use Markdown hard line breaks (`\` at line end) within blocks; blank lines separate sections and scenarios only. Preserve visible line breaks in ClickUp and verify they neither collapse nor display literal escape characters.

```markdown
# [Epic/topic title]

## FE - Apps - [Feature] - Outcome

- Epic: [Supplied reference]
- Tags: [Approved or proposed tags]
- Assignee: [Approved or proposed member/team]
- Priority: Normal

**As a [role],**\
**I want to** [user action],\
**So that** [useful outcome].

### Acceptance Criteria

**Scenario 1: [Short outcome title]**\
**Given** [starting condition],\
**When** [action or event],\
**Then** [observable result].
```

Use one short sentence per clause, without an arbitrary word cap. Prefer “Then I see matching records” to “Then the system displays a list containing all records matching my search.”

Append optional API endpoint bullets within the relevant story. After the final story, add:

```markdown
## Open Questions

- [Story title]: [Unresolved material question?]
```
