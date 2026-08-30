# Agent Template

Lean shared configuration for Claude Code and OpenAI Codex. Flutter/Dart support is included, while project-specific rules and existing files remain intact.

## Structure

- `AGENTS.md`: shared runtime rules.
- `CLAUDE.md`: imports shared rules and adds Claude-only behavior.
- `.agents/project-context.md`: project purpose, architecture, ownership, commands, and generated structure.
- `.agents/skills/`: canonical skills.
- `.agents/subagents/`: canonical planner, developer, economy, and QA roles.
- `.agents/tools/`: safe installer, adapter sync, hooks, context checks, and integrity checks.
- `.agents/tests/`: deterministic tooling tests.
- `.agents/Makefile`: portable verification targets without owning a project's root Makefile.
- `.claude/skills` and `.claude/agents`: relative symlinks to canonical sources.
- `.codex/agents/`: generated TOML adapters.
- `skills-lock.json`: upstream skill provenance.

Rare setup skills are not vendored. Install them only when a project needs them.

## Install into an existing project

Do not broadly copy this repository over another project. Preview the managed installation:

```sh
python .agents/tools/install_template.py /path/to/project
python .agents/tools/install_template.py /path/to/project --write
```

The installer:

- appends or refreshes marked template blocks in existing `AGENTS.md` and `CLAUDE.md`;
- preserves existing instructions outside those blocks;
- merges only missing template hooks into Claude/Codex JSON settings;
- leaves an existing `Makefile` untouched;
- backs up changed instruction and settings files;
- records installed hashes so unchanged template-owned files can be upgraded safely;
- aborts when a user-modified owned file or same-name unowned path would be overwritten;
- creates relative Claude adapter symlinks on Unix/macOS.

Use `--copy-adapters` on filesystems without symlink support. Windows selects copy mode automatically.

Template rules cannot outrank system instructions. Codex also lets instructions closer to the working directory override root guidance. The managed root block is placed after existing root text for consistent repository-wide defaults without hiding project rules.

## New projects

This repository itself uses:

```sh
make sync
make context
make verify
```

For another project, keep its existing build commands and Makefile. The installer intentionally does not replace them. Run portable checks directly or call them from the project's workflow:

```sh
make -f .agents/Makefile sync
make -f .agents/Makefile verify
```

## Project context

Agents read `.agents/project-context.md` before broad searches. Curated purpose, architecture, ownership, and command sections stay hand-maintained. Only the marked structural block is generated:

```sh
python .agents/tools/generate_project_context.py
python .agents/tools/generate_project_context.py --write
```

`check_project_context.py` fails when detected folders and the generated block differ. Session start checks freshness but never writes, avoiding unexpected dirty worktrees.

## Shared skills and subagents

Edit only `.agents/skills/` and `.agents/subagents/`. Run `make sync` after changes.

Active roles:

- `team-lead`: read-only planning, architecture, and final review.
- `developer`: Flutter, backend/API, application, data, platform, and tests.
- `economy-executor`: frozen mechanical work only.
- `qa`: read-only functional and regression verification.

`subagent-workflow` contains routing and the complete delegation brief format. Requirements clarification uses `grill-requirements`; separate BA/backend/Flutter prompt files are unnecessary.

## UI from screenshots

Provide screenshot file paths in the task. Agents inspect the referenced files, reuse project tokens/components/assets, implement responsive and interaction states, and compare the result with those screenshots. No fixed folder or Figma-specific workflow is required.

## Comments

Obvious code needs no comment or doc comment. Keep comments short and use them only for non-obvious rationale, contracts, invariants, or hazards.

## Codex context

`.codex/config.example.toml` selects `gpt-5.6-sol` and sets:

```toml
model_context_window = 1050000
```

Apply device preferences with a preview first:

```sh
python .codex/install.py --dry-run
python .codex/install.py --write
```

The device installer merges allowlisted keys and backs up existing `~/.codex/config.toml`; it does not copy auth, sessions, trust, or local provider paths.

## Agent memory

Required behavior stays in checked-in instructions. Auto-memory is optional recall and must not become the only copy of a rule or project fact.

Codex local memory is off by default and controlled through `/memories` or user config. Claude Code auto-memory is per repository and managed through `/memory`. Neither generated memory store should contain secrets.

## Security

See `SECURITY.md` for filesystem boundaries, destructive-action safeguards, safe installation, and secret handling.

## Skill maintenance

Run `skill-maintenance` only when requested. It compares vendored bodies with pinned upstream repositories, preserves local frontmatter, and never invents unavailable hashes. Restart active agents if changed skill metadata does not refresh.
