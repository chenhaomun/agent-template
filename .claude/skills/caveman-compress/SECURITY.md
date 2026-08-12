# Security

This project-local `caveman-compress` copy is local-only.

## Behavior

- No external model API.
- No external agent CLI.
- No network calls.
- No shell execution.
- Reads only the user-provided file.
- Writes only the compressed file and sibling `.original.md` backup.
- Refuses secret-looking filenames and private config paths.

## Limits

Files larger than 500KB are rejected before processing.
