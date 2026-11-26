---
name: dart-use-path-package
stack: dart
description: Manipulate file paths with `package:path` (and `package:file` contexts) instead of string operations. Use when joining, splitting, comparing, or converting file paths or extensions; not for URLs or non-path strings.
---

# Cross-Platform Paths

Use `package:path` when the project already depends on it; adding it is a new dependency and needs approval.

## Replace string operations

| Avoid | Use |
|---|---|
| `'$dir/$file'` | `p.join(dir, file)` |
| `path.contains('foo/')` | `p.split(path).contains('foo')` |
| `path.startsWith('foo/')` | `p.split(path)` with a list pattern (`case ['foo', ...final rest]`) or `p.isWithin('foo', path)` |
| `path.endsWith('.ext')`, `lastIndexOf('.')` | `p.extension(path)`, `p.withoutExtension(path)`, `p.extension(path, 2)` for known compound suffixes |
| `path.replaceAll(r'\', '/')` | `p.posix.joinAll(p.split(p.relative(path, from: root)))` or `p.url.joinAll(...)` |
| `Uri.parse(path)`, `uri.path` | `p.toUri(path)`, `p.fromUri(uri)` |

## Rules

- Strip `:line[-col]` suffixes before treating a string as a path.
- `p.normalize` and `p.canonicalize` are lexical. To compare real files across symlinks, use `resolveSymbolicLinksSync()` and handle `FileSystemException` for paths that may not exist.
- Git paths, `.gitignore` entries, and manifests always use POSIX separators.
- With `package:file`, use the file system's own context (`file.fileSystem.path`), not global `p.*`, so Windows-style memory file systems test correctly.
- In POSIX-only tools, joining a dynamic base to one static subpath (`p.join(root, 'build/web/index.html')`) is fine and keeps paths searchable.

Verify with tests on both path styles where the code is cross-platform, then analysis.
