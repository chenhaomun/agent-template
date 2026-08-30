# Agent Security Policy

## Filesystem Safety

- Default writes to the active project and task-specific temporary directories.
- A project task does not authorize changes to operating-system files, other projects, user configuration, credentials, or agent/tool homes.
- Never delete, overwrite, move, `chmod`, or `chown` files outside the project unless the user explicitly names the exact path and action.
- Treat `/`, system directories, the user home, shell profiles, SSH/GPG stores, keychains, and `~/.codex` or `~/.claude` as protected.
- Before a destructive action, resolve and inspect every target with read-only checks. Reject broad roots, unresolved variables, globs, external symlinks, and recursive operations with ambiguous scope.
- Prefer recoverable actions and backups. Preserve untracked files, local edits, and unrelated user data.
- Use elevated permissions only for an exact user-authorized target; never to bypass an unexpected protection failure. Stop and ask when the target or recovery path is unclear.

## Security Scope

Security issues include:

- installer path traversal, unsafe overwrite, or manifest ownership bypass;
- hooks, skills, or subagents executing commands beyond their stated scope;
- secrets entering source, backups, logs, reports, prompts, or memory;
- symlinks escaping the target project;
- unsafe merging of existing Claude, Codex, or project settings.

## Safe Use

- Treat this repository, its hooks, and vendored skills as executable code. Review changes before installation or refresh.
- Preview installation first; the installer must preserve unknown project content and stop on unowned conflicts.
- Keep `.agents/.template-manifest.json` tracked in installed projects. It contains ownership hashes used for safe upgrades, not credentials.
- Never commit `.env*`, local settings, generated logs, or timestamped `.bak-*` files.
- Do not store tokens, credentials, personal data, or private source excerpts in agent memory.
- Run `make -f .agents/Makefile verify` after changing hooks, installers, skills, subagents, or adapters.

## Git Operations

- The user owns commits and remote repository changes.
- Agents must not commit, push, tag, publish, create a pull request, or otherwise change remote Git state unless the user explicitly requests that exact action.
- Read-only Git inspection and preparing a requested commit message are allowed. Never rewrite history or discard user changes without explicit approval.

If a real secret was exposed, remove it from active use and rotate it immediately; deleting it from the latest commit is not sufficient.
