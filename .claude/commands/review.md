Run a production code review on the current staged changes or the specified file/directory.

Use `.agents/skills/production-code-review/SKILL.md` as the review guide.

If no argument is given, review staged changes via `git diff --cached`.
If an argument is given, review the specified path.

Report findings grouped by severity: blocking, warning, suggestion.
