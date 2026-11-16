---
name: git-staged-commit-message
description: Generate a commit message from staged git changes and copy to clipboard. Use for commit message/title/body or staged-change summary.
---

# Git Staged Commit Message

1. Inspect `git status --short`, `git diff --cached --name-status`, and `--stat` first. Apply SECURITY.md before reading selected staged file diffs; never dump credential-bearing content. If nothing is staged, say so and stop.
2. Base the message only on staged changes unless asked otherwise. Follow AGENTS.md's Git format; infer a ticket from explicit context or branch, otherwise omit it. Use an imperative summary (under 72 characters when practical) and outcome/why bullets. Include material dependency, API, environment, permission, migration, or generated-file effects.
3. Return one ready-to-use message. For clearly unrelated changes, note the mix and give a broad message or useful split options. Do not stage or commit.
4. Copy the exact message using the platform clipboard (`pbcopy`, `Set-Clipboard`, or available Linux clipboard tool). Pass text through stdin or safe literal quoting; never interpolate it as executable shell code. If unavailable or blocked, return the message and state that copying failed.
