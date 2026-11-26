---
name: dart-write-documentation
stack: dart
description: Write Dart `///` API doc comments following Effective Dart. Use when documenting public declarations or when doc comments are requested.
---

# Dart API Documentation

Document public APIs when requested or when the project requires it. Requested or lint-required public API docs are exempt from the AGENTS.md two-line comment cap; keep them as short as the contract allows and never restate what the code plainly says.

- Use `///`, never `/** */`. Start with a one-sentence summary ending in a period, then a `///` blank line before details.
- Openers: noun phrase for properties ("The radius..."), "Whether" for booleans, third-person verb for methods ("Initializes..."). Do not restate the name or signature.
- Describe parameters, return values, and thrown exceptions in prose; never `@param`, `@return`, or `@throws`.
- Place doc comments before annotations. Do not repeat inherited docs on unchanged overrides. Document a getter/setter pair on the getter only.
- Link in-scope symbols with `[name]` (no parentheses; `[Class.new]` for the unnamed constructor). Use backticks for keywords and literals. For out-of-scope symbols use `/// @docImport` on `library;` instead of a runtime import.
- Label fenced code blocks (`dart`, `sh`); use `dart-use-doc-examples` for longer samples.

Verify with analysis (`comment_references` clean) and, when available, `dart doc`.
