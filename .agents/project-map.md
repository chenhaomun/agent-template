# Project Map

Use this map before broad searches. Start with mapped folders and nearby tests.

## Areas

No areas mapped yet. Run `python .agents/tools/generate_project_map.py` to generate a starter map, then refine after the first real task.

## Rules

- Keep area names stable and lowercase.
- Store folders, not exact file paths, unless one file is the whole area.
- Prefer nearest stable parent folders.
- Include test folders beside source folders when known.
- If a folder is missing or stale, fall back to `rg` and update the map.
