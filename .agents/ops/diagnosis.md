# Harness Diagnosis

Read only after a tooling, shell, sync, or context-cost problem.

## Fast path

- Use `.agents/project-map.md`, then `rg`, then a narrow file read.
- Cap output at 4,000 characters; return conclusions and decisive errors, not logs.
- Delegate bulk scans or repeated edits only after scope and acceptance are fixed.
- Prefer project tools, then shell; use MCP/connectors only when the task requires them.

## Known traps

- Windows Python output: use `encoding="utf-8", errors="replace"`. If `python`/`python3` is absent or a Store stub, use the agent runtime's bundled Python.
- PowerShell 5.1 has no `&&`/`||`; `Out-File` needs `-Encoding utf8`.
- CRLF vs LF drift: normalize line endings or use `diff --strip-trailing-cr`.
- Edit `.agents/` sources only. `.claude/skills`, `.claude/agents`, and `.codex/agents` are generated.
- Never fabricate `skills-lock.json` hashes.
- This repo is under OneDrive; retry one transient lock, then report it.

## Make fallback

When `make` is unavailable:

```text
<python> .agents/tools/sync_shared.py
<python> .agents/tools/check_template.py
<python> .agents/tools/check_project_map.py
<python> -m unittest discover -s .agents/tests -p "test_*.py"
```

For Flutter/Dart projects also run the analyzer, tests, and format check represented by the Makefile.
