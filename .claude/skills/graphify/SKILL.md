---
name: graphify
description: Query graphify-out for repo structure, relationships, and impact analysis before broad searches.
---

# Graphify

Knowledge-graph view of the repo via the `graphify` CLI (PyPI package
`graphifyy`). Code extraction is local tree-sitter AST — no LLM, no API key,
nothing leaves the machine. Same commands for Claude Code and Codex.

## Requirement

CLI must exist: `graphify --help`. If missing, ask the user before installing
(AGENTS.md package rule): `pip install graphifyy`.

## Build / update the graph

```sh
graphify update .          # local, code files only, no API key
```

- Run once per project, then after big changes. After refactors that delete
  code, add `--force` (rebuild guard trips when node count drops).
- Output lands in `graphify-out/` (graph.json + graph.html +
  GRAPH_REPORT.md). Ensure `graphify-out/` is gitignored.
- Docs/PDF/image ingestion (`/graphify .` full flow) needs an LLM backend key
  (e.g. `GEMINI_API_KEY`) — optional; never required for code.

## Query (prefer over repo-wide grep/read when the graph exists)

```sh
graphify explain "<node>"        # node + neighbors in plain language
graphify path "A" "B"            # shortest path between two nodes
```

- `GRAPH_REPORT.md` = key concepts and suggested queries; read it first.
- Node names are files, classes, functions. Start from `explain` on the file
  or symbol in question; follow edges instead of opening whole files.
- Graph stale or node missing → `graphify update .`, retry once, then fall
  back to Grep/Read.

## Traps

- Dart extraction is UNVERIFIED in this setup (no tree-sitter-dart wheel
  shipped as of v0.9.12) — on first Flutter project, confirm .dart nodes
  appear before relying on the graph; otherwise fall back to project-map +
  Grep.
- Never install with `--project` for Claude in template-derived repos: it
  writes `.claude/skills/graphify/`, which fails `check_template` (drift vs
  `.agents/skills/`). This vendored skill replaces any global install.
- Keep graph artifacts out of commits and subagent reports; reference node
  names instead.
