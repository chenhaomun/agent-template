# User-story pattern

Use an outcome-based title. Draft metadata stays outside the published body.

```markdown
# FE - Apps - [Feature] - Outcome

- Epic: [Supplied reference]
- Tags: [Approved or proposed tags]
- Assignee: [Approved or proposed member/team]
- Priority: Normal

**As a [role],**
**I want to** [user action],
**So that** [useful outcome].

### Acceptance Criteria

**Scenario 1: [Short outcome title]**
**Given** [relevant starting state],
**When** [action or event],
**Then** [observable result].

**Scenario 2: [Short outcome title]**
**Given** [relevant starting state],
**When** [action or event],
**Then** [observable result].
```

Use only as many scenarios as needed; one concise sentence per Given, When, and Then. Do not pad a simple story or drop essential conditions to shorten it.

Append an **API** section only when needed, with short endpoint bullets. Never add Scope notes or Screenshots/Flow.

Generate a separate local README:

```markdown
# [Epic title]

## Stories
- [Story title](story-name.md)

## Open Questions
- [Story title](story-name.md): [Unresolved material question?]
```

Deduplicate shared questions; write “None” when resolved. Add only material gaps/coverage notes. Append created ticket links to the index; never publish README or its questions.
