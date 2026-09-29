# User-story pattern

- Title: `FE - Apps - [Feature] - Action`; adapt the prefix to the supplied project convention.
- Body: a short user story, testable behavior bullets, conditional API calls, and Screenshots/Flow.
- Resolve destination, epic relationship, required fields, tags, and assignee from the active request or private target-project configuration. No real project details belong in this reference.

Use this shape, replacing placeholders with evidence and removing drafting notes before creation:

```markdown
# FE - Apps - [Feature] - Action

- Epic: [Supplied epic reference]
- List: [Verified destination]
- Tags: Pending user input
- Assignee: [Requested member or team]
- Priority: Normal

## User Story
As a customer, I can [action] so I can [outcome].

## Acceptance Criteria
- [Action or condition] → [visible result].

## API
- `METHOD /confirmed/path` — [inputs, outputs, and when called].

## Screenshots/Flow
- [Screen name](source)
- [Entry] → [action] → [result].

<!-- Local draft only: never send this section to the ticket. -->
## Open Questions
- [Short question needed to finish this story?]
```

Keep the four body sections in the draft even when evidence is missing; use “Not provided” and a focused local question. Build the ticket description from those four sections only; never send Open Questions or the full draft file.
