# User-story pattern

Save one file in the target repository. Use an epic heading and repeat the story section below for each outcome. Draft metadata stays outside the published body.

```markdown
# [Epic title]

## FE - Apps - [Feature] - Outcome

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

After the last story, append the shared questions section in the same file:

```markdown
## Open Questions
- [Story title]: [Unresolved material question?]
```

Deduplicate shared questions; write “None” when resolved. Add only material gaps/coverage notes. Record created ticket links beside the corresponding story metadata. No separate README or per-story files; never publish the combined draft or its questions.
