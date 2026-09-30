# User-story pattern

- Title: `FE - Apps - [Feature] - Action`; adapt the prefix to the supplied project convention.
- Body: a short user story and testable behavior bullets. Include API when backend effort is required; otherwise omit it by default. No Screenshots/Flow section.
- Creation fields: **Task Type = User Story**, **Target Platform(s) = Mobile App**. Link the standalone story to the epic through **Related tasks**, never as a subtask. Keep these operational fields out of the story body.
- Use explicit instructions or private project configuration first; infer missing metadata from the epic, comments, and related conventions. Show inferred values as proposed for review. No real project details belong in this reference.

Use this shape, replacing placeholders with evidence and removing drafting notes before creation:

```markdown
# FE - Apps - [Feature] - Action

- Epic: [Supplied epic reference]
- Tags: [Specified tags or inferred tags marked proposed]
- Assignee: [Specified member/team or inferred identity marked proposed]
- Priority: Normal

## User Story
As a customer, I can [action] so I can [outcome].

## Acceptance Criteria
- [Action or condition] → [visible result].

## API
- `METHOD /confirmed/path` — [inputs, outputs, and when called].

```

Remove the API section when no backend work or requested API documentation is needed. Preserve inspected codebase conventions for behavior the requirements leave unspecified. Keep only unresolved material decisions in README; do not ask routine metadata or existing-behavior questions. Never include destination lists or draft versions.

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
