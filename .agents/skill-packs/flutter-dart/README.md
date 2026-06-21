# Flutter/Dart Skill Pack

Optional. Enable only for Flutter or Dart projects. The template core stays language-agnostic; this pack adds Flutter/Dart-specific skills, subagents, and rules.

## Contents

| Item | What it is |
|---|---|
| `skills/flutter-*` (11) | Flutter skills: widgets, tests, routing, l10n, responsive layout, JSON serialization, HTTP |
| `skills/dart-*` (10) | Dart skills: unit tests, coverage, mocks, static analysis, FFI, pattern matching |
| `subagents/flutter-developer.md` | Flutter UI/state/routing/platform developer role |
| `subagents/backend-api-developer.md` | API/DTO/migration/contract developer role |
| `flutter-dependencies.md` | Default package choices (bloc, go_router, dio) |
| `AGENTS-flutter.md` | Flutter rules to append to your `AGENTS.md` |
| `skills-lock.fragment.json` | Lock entries to merge into root `skills-lock.json` |

## Enable

From the project root:

```sh
# 1. Move skills into the active skills folder
mv .agents/skill-packs/flutter-dart/skills/* .agents/skills/

# 2. Move the Flutter/Dart subagents into the active subagents folder
mv .agents/skill-packs/flutter-dart/subagents/* .agents/subagents/

# 3. Move the dependencies reference up one level
mv .agents/skill-packs/flutter-dart/flutter-dependencies.md .agents/flutter-dependencies.md
```

PowerShell equivalent:

```powershell
Move-Item .agents\skill-packs\flutter-dart\skills\* .agents\skills\
Move-Item .agents\skill-packs\flutter-dart\subagents\* .agents\subagents\
Move-Item .agents\skill-packs\flutter-dart\flutter-dependencies.md .agents\flutter-dependencies.md
```

Then, by hand:

4. **Append** the sections in `AGENTS-flutter.md` to your project `AGENTS.md`.
5. **Merge** the `skills` entries from `skills-lock.fragment.json` into the root `skills-lock.json`.
6. Update `.agents/skills/subagent-workflow/SKILL.md` routing/model rows to include `flutter-developer` and `backend-api-developer` if you use the subagent flow.

Once moved, you can delete the empty `.agents/skill-packs/flutter-dart/` folder.

## Keeping current

Refresh upstream skills with:

```sh
npx skills add flutter/skills --skill '*' --agent universal
npx skills add dart-lang/skills --skill '*' --agent universal
```

Review `git diff -- .agents/skills skills-lock.json` and merge only portable guardrails from https://docs.flutter.dev/ai/ai-rules into `AGENTS.md`.
