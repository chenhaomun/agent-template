#!/usr/bin/env python3
"""SessionStart hook: report project-context drift without writing files."""

from __future__ import annotations

import check_project_context


def main() -> int:
    return check_project_context.main()


if __name__ == "__main__":
    raise SystemExit(main())
