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
2. Per file, understand BOTH sides and WHY each changed: `git log --merge -p <file>`, `git blame`. Do not resolve a hunk you don't understand.
3. Resolve preserving both intents. Combine changes when both are wanted; drop a side only when it is genuinely superseded — never to make markers disappear. Remove every conflict marker.
4. Do NOT hand-merge generated/vendored files (`*.g.dart`, `*.freezed.dart`, `build/`, etc. — see AGENTS.md). Take one side or `--theirs`/`--ours` to unblock, then regenerate from source. Same for lockfiles: resolve `pubspec.yaml`/`package.json` by hand, then regenerate `pubspec.lock`/lockfiles.
5. Verify before continuing: `make verify` (or narrow `flutter analyze`/`flutter test` on touched areas). Conflicts often produce code that merges cleanly but doesn't compile.
6. `git add` each resolved file, then continue (`git rebase --continue` / `git cherry-pick --continue` / commit the merge). Never `git commit` with unresolved markers.

## Guardrails

- Never `git checkout --ours`/`--theirs` on a whole file to skip understanding it, and never `git merge --abort`/`reset --hard` without asking — that discards work.
- Preserve unrelated local changes; keep the resolution scoped to the conflict.
- If either side's intent is unclear or the sides truly contradict, stop and ask rather than guessing.
- Re-run any codegen (`build_runner`) and format after resolving; remove leftover debug/churn.
