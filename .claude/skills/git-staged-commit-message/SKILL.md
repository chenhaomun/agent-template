---
name: git-staged-commit-message
description: Generate a commit message from staged git changes and copy to clipboard. Use for commit message/title/body or staged-change summary.
---

# Git Staged Commit Message

Generate commit message from staged changes only, copy it to clipboard, and return it in chat. Do not include unstaged or untracked changes unless user explicitly asks.

## Inspect

Run:

```sh
git status --short
git diff --cached --name-status
git diff --cached --stat
git diff --cached
```

If staged diff is large, inspect `--name-status`, `--stat`, then sample the staged diff by file. Do not exceed useful context.

## Rules

- Base message only on staged changes.
- If no staged changes exist, say no staged changes.
- Follow `AGENTS.md` Git format.
- If ticket is obvious from branch name, issue key, or user message, use ticket format.
- If ticket is not obvious, omit ticket.
- Keep summary imperative and under 72 chars when practical.
- Body bullets should describe outcomes, not every file.
- Mention risk-impacting items when staged: dependency, API, env, permission, migration, generated files.
- Do not run `git commit`.
- Copy the generated message to clipboard by default.

## Output

Return one ready-to-use commit message in the `AGENTS.md § Git` format (ticket or no-ticket variant).

If staged changes are mixed/unrelated, say so and provide either:
- one best broad message, or
- grouped message options when splitting commits is clearly better.

## Quality Bar

Good message answers:

- What changed?
- Why does it matter?
- What notable risk or follow-up is included?

## Clipboard

Windows PowerShell:

```powershell
@'
<commit message>
'@ | Set-Clipboard
```

macOS:

```sh
cat <<'EOF' | pbcopy
<commit message>
EOF
```

Linux:

```sh
cat <<'EOF' | xclip -selection clipboard
<commit message>
EOF
```

If clipboard command is unavailable or blocked, return the message normally and say clipboard copy failed.
