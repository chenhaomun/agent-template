from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".agents" / "tools"


def load_tool(name: str):
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProjectContextTest(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = load_tool("generate_project_context")
        self.checker = load_tool("check_project_context")

    def test_write_is_idempotent_and_preserves_curated_notes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agents" / "skills").mkdir(parents=True)
            context = root / ".agents" / "project-context.md"
            context.write_text(
                "# Project Context\n\n## Purpose\n\nCurated note.\n\n"
                "<!-- BEGIN GENERATED STRUCTURE -->\nold\n<!-- END GENERATED STRUCTURE -->\n",
                encoding="utf-8",
            )

            self.assertTrue(self.generator.write_document(root))
            first = context.read_text(encoding="utf-8")
            self.assertFalse(self.generator.write_document(root))

            self.assertIn("Curated note.", first)
            self.assertEqual(first, context.read_text(encoding="utf-8"))

    def test_checker_reports_structural_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agents" / "skills").mkdir(parents=True)
            self.generator.write_document(root)
            (root / "src").mkdir()

            errors = self.checker.check_context(root)

            self.assertIn("unmapped detected folder: src", errors)

    def test_checker_reports_missing_mapped_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agents" / "skills").mkdir(parents=True)
            self.generator.write_document(root)
            (root / ".agents" / "skills").rmdir()

            errors = self.checker.check_context(root)

            self.assertIn("missing mapped folder: .agents/skills", errors)

    def test_feature_without_test_peer_maps_only_existing_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "lib" / "features" / "auth").mkdir(parents=True)

            areas = self.generator.detect_areas(root)

            self.assertEqual(areas["auth"], {"lib/features/auth"})

    def test_session_start_does_not_write_context(self) -> None:
        session = load_tool("session_start")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agents" / "skills").mkdir(parents=True)
            self.generator.write_document(root)
            context = root / ".agents" / "project-context.md"
            before = context.read_bytes()
            original_root = session.check_project_context.ROOT
            try:
                session.check_project_context.ROOT = root
                self.assertEqual(session.main(), 0)
            finally:
                session.check_project_context.ROOT = original_root

            self.assertEqual(before, context.read_bytes())


if __name__ == "__main__":
    unittest.main()
