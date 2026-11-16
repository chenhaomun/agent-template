---
name: resolving-merge-conflicts
description: Resolve git merge/rebase/cherry-pick conflicts safely — understand both sides, preserve intent, regenerate generated files, verify. Use when conflict markers or a halted merge/rebase appear.
---

# Resolving Merge Conflicts

Resolve conflicts by understanding intent, not by blind-picking a side. Preserve everyone's work.

## Scope

Trigger: `<<<<<<<`/`=======`/`>>>>>>>` markers, or a halted `git merge`/`rebase`/`cherry-pick`/`stash pop`. First run `git status` and `git diff --name-only --diff-filter=U` to list conflicted files.

## Steps

1. Know the operation: `git status` says merge vs rebase (in a rebase, "ours"/"theirs" are swapped — ours = the branch you're replaying onto). State which before resolving.
2. Per safe source file, understand both sides and why each changed using scoped history and diffs. Apply SECURITY.md before reading content; credential-bearing conflicts require sanitized evidence. Do not resolve a hunk you don't understand.
3. Resolve preserving both intents. Combine changes when both are wanted; drop a side only when it is genuinely superseded — never to make markers disappear. Remove every conflict marker.
4. Do NOT hand-merge generated/vendored files (`*.g.dart`, `*.freezed.dart`, `build/`, etc. — see AGENTS.md). Take one side or `--theirs`/`--ours` to unblock, then regenerate from source. Same for lockfiles: resolve `pubspec.yaml`/`package.json` by hand, then regenerate `pubspec.lock`/lockfiles.
5. Verify with the project's relevant commands; use `make -f .agents/Makefile verify` for template checks. Cleanly merged code can still fail to compile or behave incorrectly.
6. Stage only resolved files when the requested conflict workflow calls for it. Continuing a rebase/cherry-pick or committing a merge creates commits: do so only with explicit authorization under AGENTS.md. Otherwise leave the verified resolution ready for the user. Never continue with unresolved markers.

## Guardrails

- Never `git checkout --ours`/`--theirs` on a whole file to skip understanding it, and never `git merge --abort`/`reset --hard` without asking — that discards work.
- Preserve unrelated local changes; keep the resolution scoped to the conflict.
- If either side's intent is unclear or the sides truly contradict, stop and ask rather than guessing.
- Re-run any codegen (`build_runner`) and format after resolving; remove leftover debug/churn.
