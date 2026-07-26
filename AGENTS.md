# AGENTS.md

Shared rules for Codex and Claude Code; Flutter/Dart is the primary stack.

## Commands / Verify

- Prefer project scripts. Use `make verify`; if `make` is unavailable, use `.agents/ops/diagnosis.md` § Make fallback. For other stacks, check `package.json` or `scripts/`.
- Do not hand-edit generated/vendored files (`*.g.dart`, `*.freezed.dart`, `build/`, `.dart_tool/`, etc.); edit the source and re-run the generator.
- Cap large command output at 4,000 chars (pipe through `head` or limit explicitly).
- Final response: outcome, changes, verification, and blockers/API/env impact only. Expand for safety or when asked.

> Hooks in `.claude/settings.json` and `.codex/hooks.json` enforce these via shared `.agents/tools/` scripts; follow the rules even when hooks are unavailable.

## Work Rules

- Read nearby code first; follow existing architecture, naming, and tests.
- Check `.agents/project-map.md` before broad search; if missing or stale, preview `<python> .agents/tools/generate_project_map.py`, then update via `apply_patch`.
- Use relevant `.agents/skills/<skill>/SKILL.md`; project conventions win. Deferred skills live in `.agents/skill-packs/`.
- Use `grill-requirements` when requirements are unclear or broad, or when acceptance criteria, scope, target flow/state, or contradictions may cause rework.
- Keep changes scoped. Preserve user changes. Never reset unrelated work.
- Prefer simple, scoped design. Ask before dependencies, architecture, state-management, or generator changes.
- Keep secrets out. Stop and report suspicious or unexpectedly long commands.
- Add/update tests when requested, required by TDD, or expected by project practice; verify narrowly first.
- Default `caveman lite` responses (Codex: `$caveman`, Claude: `/caveman`); expand only for safety warnings, blockers, or explicit user request.

## Flutter

- Verify with `flutter analyze`, `flutter test`, `flutter run --dart-define-from-file=.env.dev.json`, `flutter build <target> --dart-define-from-file=.env.prod.json`.
- Check `analysis_options.yaml` and `.agents/flutter-dependencies.md`; prefer Dart/Flutter tooling.
- Prefer composition, immutable/`const` widgets, fast `build()`, lazy lists, and off-UI-thread expensive work.
- Preserve null safety, project logging/theme/l10n, responsiveness/a11y, platform parity, permissions, and loading/success/empty/error/disabled states.
- Use configured flavors and `--dart-define-from-file`.
- Native/FFI/binary downloads require explicit user approval and hash/offline fallback review.

## Design-to-Code (Figma)

- Any UI built from a Figma design (MCP/connector, URL, or node ID) MUST follow `.agents/skills/figma-design-to-code/SKILL.md` — not optional, applies to subagents. Take exact values per node from the Figma MCP; never estimate from screenshots. The skill holds the rest (token mapping, asset export, component reuse, `pixel_diff.py`-gated compare loop).

## Subagents

For medium/large/risky/unclear work, use `.agents/skills/subagent-workflow`. It chooses planner strength by complexity, then the cheapest capable executor. Skip for small work. Do not silently change public APIs; update consumers and verification together.

## Git

Branch: `<type>/<ticket-title-summary>`, e.g. `feature/add-auth`, `fix/login-crash`.

For commit messages from staged changes, use `git-staged-commit-message`.

Commit with ticket:

```text
<ticket> - <summary>

- <point A>
- <point B>
```

Without ticket, omit `<ticket> - `.
