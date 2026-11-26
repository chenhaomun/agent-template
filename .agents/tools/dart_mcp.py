#!/usr/bin/env python3
"""Start the Dart and Flutter MCP server with the project's pinned SDK.

Resolves `dart` the same way verification does from the repository root
(project-commands.json, then a cached FVM SDK, then PATH) and runs
`dart mcp-server` over stdio. A pin that exists only in a nested package is
not used here; configure `dart` in project-commands.json for that layout.
"""

from __future__ import annotations

import os
import subprocess
import sys

from run_checks import ROOT, sdk_command


def server_command(argv: list[str]) -> list[str]:
    return [*sdk_command(ROOT, "dart"), "mcp-server", *argv]


def main(argv: list[str]) -> int:
    try:
        command = server_command(argv)
    except (FileNotFoundError, ValueError) as error:
        print(f"dart mcp-server unavailable: {error}", file=sys.stderr)
        return 1
    print(
        f"starting {command[0]} mcp-server; if it reports no 'mcp-server' command, this SDK predates the bundled MCP server",
        file=sys.stderr,
    )
    os.chdir(ROOT)
    if os.name != "nt":
        os.execv(command[0], command)
    try:
        return subprocess.call(command)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
