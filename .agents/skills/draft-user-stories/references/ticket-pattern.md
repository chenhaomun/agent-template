# User-story pattern

- Title: `FE - Apps - [Feature] - Action`; adapt the prefix to the supplied project convention.
- Body: a short user story and testable behavior bullets. Include API when backend effort is required; otherwise omit it by default. No Screenshots/Flow section.
- Resolve destination, epic relationship, required fields, tags, and assignee from the active request or private target-project configuration. No real project details belong in this reference.

Use this shape, replacing placeholders with evidence and removing drafting notes before creation:

```markdown
# FE - Apps - [Feature] - Action

- Epic: [Supplied epic reference]
- Tags: Pending user input
- Assignee: [Requested member or team]
- Priority: Normal

## User Story
As a customer, I can [action] so I can [outcome].

## Acceptance Criteria
- [Action or condition] → [visible result].

## API
- `METHOD /confirmed/path` — [inputs, outputs, and when called].

```

Remove the API section when no backend work or requested API documentation is needed. Keep missing decisions in the generated README, not in story files. Never include destination lists or draft versions.

Deliver the folder under Downloads using the sanitized epic ticket name. Generate a short `README.md` alongside the stories:

```markdown
# [Epic title]

## Stories
- [Story title](story-name.md)

## Open Questions
- [Story title](story-name.md): [Short question?]
- Shared: [Question affecting several stories?]
```

Omit empty question groups; say “None” when there are no open questions. Add source/access gaps only when material. After creation, append ticket links to the story index. Never upload README or send its questions to tickets; publish only the approved story body sections.
