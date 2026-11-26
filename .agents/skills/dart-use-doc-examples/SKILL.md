---
name: dart-use-doc-examples
stack: dart
description: Inject analyzable example files into Dartdoc with `{@example}`, `#region`, and `#hide`. Use when public API docs need multi-line code samples.
---

# Dartdoc Examples

Prefer an existing `example/` file the analyzer already checks over inline `///` code blocks for multi-line samples.

- Put the directive on its own `///` line: `{@example <path>[#region] [lang=...] [indent=keep|strip]}`. A leading `/` resolves from the package root; otherwise the path is relative to the current file. Use forward slashes; local files only.
- Wrap the shown code in `// #region name` and `// #endregion name`, and mark required-but-distracting lines with `// #hide`. Markers are stripped only when the directive targets a region.
- Keep example files small, compiling, and free of secrets or real endpoints.

Verify with analysis on the example files and, when available, `dart doc` without "Failed to read file" or missing-region warnings.
