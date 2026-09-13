---
name: dart-run-static-analysis
stack: dart
description: Analyze Dart code and resolve relevant diagnostics without changing project lint policy. Use when analysis is requested or needed after Dart changes.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Fri, 24 Apr 2026 15:09:34 GMT
---
# Analyze Dart Code

Inspect the nearest `analysis_options.yaml`, project commands, and changed code first. Preserve the project's analyzer, formatter, and generated-file conventions.

## Workflow

1. Run the narrowest applicable analyzer command; use the project verification command when it defines one.
2. Fix correctness and type-safety issues first, then relevant lint issues in touched code.
3. Read the surrounding API and call sites before changing behavior. Do not hide failures with broad exclusions or suppressions.
4. Format only changed Dart files unless project tooling owns broader formatting.
5. Re-run analysis for the affected scope and report unresolved diagnostics with their cause.

## Boundaries

- Do not alter lint configuration, SDK constraints, generated files, or dependency versions unless the task explicitly requires it.
- Use `dart fix --dry-run` only when useful; review its proposals before applying any fix. Never run blanket `dart fix --apply` or format the whole repository by default.
- Prefer a narrow documented ignore only for a confirmed false positive or required compatibility constraint; place it at the smallest scope and explain why.
- Treat warnings from generated or vendored code according to existing project configuration rather than editing those files.
