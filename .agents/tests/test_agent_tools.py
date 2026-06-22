from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".agents" / "tools"


def load_tool(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HookPayloadTest(unittest.TestCase):
    def test_extracts_claude_file_path(self) -> None:
        hooks = load_tool("hook_payload")

        paths = hooks.extract_file_paths({"tool_input": {"file_path": "lib/app.dart"}})

        self.assertEqual(paths, [Path("lib/app.dart")])

    def test_extracts_codex_apply_patch_paths(self) -> None:
        hooks = load_tool("hook_payload")
        patch = """*** Begin Patch
*** Update File: lib/app.dart
@@
-old
+new
*** Add File: lib/generated.g.dart
+generated
*** End Patch
"""

        paths = hooks.extract_file_paths({"tool_input": {"command": patch}})

        self.assertEqual(paths, [Path("lib/app.dart"), Path("lib/generated.g.dart")])


class GeneratedGuardTest(unittest.TestCase):
    def test_blocks_generated_path_in_codex_patch(self) -> None:
        payload = {
            "tool_input": {
                "command": "*** Begin Patch\n*** Update File: lib/model.g.dart\n*** End Patch\n"
            }
        }

        result = subprocess.run(
            [sys.executable, str(TOOLS / "hook_guard_generated.py")],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("model.g.dart", result.stderr)


class ProjectMapFreshnessTest(unittest.TestCase):
    def test_fails_when_detected_source_folder_is_unmapped(self) -> None:
        checker = load_tool("check_project_map")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agents").mkdir()
            (root / "lib" / "features" / "auth").mkdir(parents=True)
            (root / ".agents" / "project-map.md").write_text(
                "# Project Map\n\n## Areas\n\nNo areas mapped yet.\n",
                encoding="utf-8",
            )

            errors = checker.check_map(root)

        self.assertIn("lib/features/auth", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
