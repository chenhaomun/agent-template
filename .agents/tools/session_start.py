#!/usr/bin/env python3
"""SessionStart hook: adapter sync + project-map freshness in one process.

One interpreter spawn instead of two keeps session startup fast (process
creation is the slow path, especially on Windows). Behavior is identical to
running `sync_shared.py` then `check_project_map.py` back to back; both stay
independently runnable via `make sync` / `make check-map`.
"""

from __future__ import annotations

import check_project_map
import sync_shared


def main() -> int:
    sync_rc = sync_shared.main()
    map_rc = check_project_map.main()
    return sync_rc or map_rc


if __name__ == "__main__":
    raise SystemExit(main())
