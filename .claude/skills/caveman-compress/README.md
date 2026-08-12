# caveman-compress

Local-only compressor for Codex instruction and memory files.

## Usage

```text
/caveman-compress <filepath>
```

## Behavior

- Compresses natural-language prose with deterministic local rules.
- Preserves code blocks, inline code, URLs, commands, paths, headings, and structure.
- Writes `<filename>.original.md` backup beside the source file.
- Restores original and removes backup if validation fails.
- No external model API, external agent CLI, network, or shell execution.

## Files

| Type | Compress? |
|---|---|
| `.md`, `.txt`, `.rst`, `.typ`, `.typst`, `.tex` | Yes |
| Extensionless natural-language files | Yes |
| code/config/env/lock files | No |
| `*.original.md` | No |

See [SECURITY.md](./SECURITY.md).
