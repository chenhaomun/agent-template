---
name: resolving-merge-conflicts
description: Resolve git merge, rebase, cherry-pick, or stash conflicts by working out the latest intended behavior from code, tickets, and commit history. Use when conflict markers or a halted operation appear.
---

# Resolving Merge Conflicts

Decide each conflict from evidence of what the code should do now. No side wins by default.

## Gather evidence

- Run `git status` and `git diff --name-only --diff-filter=U` to see the operation and conflicted files. In a rebase, "ours" is the branch being replayed onto.
- For each conflict, read the base and both sides (`git show :1:<path>`, `:2:<path>`, `:3:<path>`), the commits that changed it on each side with their messages, linked tickets or PRs, and current callers and tests.
- Establish the latest intended behavior: which change reflects the current requirement, and whether one side already includes, moves, renames, reverts, or replaces the other.

## Resolve

- Write the code that delivers that behavior and fits current callers. It may be one side, both, or a new combination.
- For generated files and lockfiles, resolve their sources, then regenerate.
- Remove every conflict marker. Keep unrelated local changes.
- If the evidence conflicts or intent stays unclear, stop and ask, citing the hunk and the evidence.

## Verify and report

- Build or analyze, then run tests that cover the conflicted code; a clean merge can still break.
- Report per file what was chosen and why (commit, ticket, or caller).
- Do not continue the operation, commit, abort, or reset without an explicit request.
