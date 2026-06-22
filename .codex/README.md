# Shared Codex Device Setup

This folder stores safe, portable Codex preferences for this template.

It is not auto-loaded by Codex. On a new device, ask Codex to read `.codex/README.md` and apply the setup, or run:

```sh
python .codex/install.py --dry-run
python .codex/install.py --write --install-pet
```

What it syncs:

- Model/personality defaults.
- Desktop appearance, terminal location, review display, and commit message template.
- Optional Codehound pet from `.codex/pets/codehound`.

What it does not sync:

- Account auth, sessions, logs, cache, or local runtime paths.
- Project trust paths.
- MCP server binary paths or local marketplace cache paths.

The installer backs up `~/.codex/config.toml` before writing.
