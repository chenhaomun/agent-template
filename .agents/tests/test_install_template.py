from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".agents" / "tools"


def load_installer():
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location("install_template_test", TOOLS / "install_template.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load installer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstallTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.installer = load_installer()

    def _source(self, root: Path) -> Path:
        (root / ".agents" / "tools").mkdir(parents=True)
        (root / ".agents" / "skills" / "core").mkdir(parents=True)
        (root / ".agents" / "subagents").mkdir(parents=True)
        (root / ".agents" / "tools" / "tool.py").write_text("tool\n", encoding="utf-8")
        (root / ".agents" / "Makefile").write_text("verify:\n\t@true\n", encoding="utf-8")
        (root / ".agents" / "skills" / "core" / "SKILL.md").write_text("skill\n", encoding="utf-8")
        (root / ".agents" / "subagents" / "dev.md").write_text("agent\n", encoding="utf-8")
        (root / ".agents" / "project-context.md").write_text("context\n", encoding="utf-8")
        (root / "AGENTS.md").write_text("template rules\n", encoding="utf-8")
        (root / "CLAUDE.md").write_text("template claude\n", encoding="utf-8")
        (root / ".claude").mkdir()
        (root / ".codex").mkdir()
        (root / ".codex" / "agents").mkdir()
        (root / ".codex" / "agents" / "dev.toml").write_text("name = \"dev\"\n", encoding="utf-8")
        (root / ".claude" / "settings.json").write_text(
            json.dumps({"hooks": {"SessionStart": [{"command": "template"}]} }), encoding="utf-8"
        )
        (root / ".codex" / "hooks.json").write_text(
            json.dumps({"hooks": {"PreToolUse": [{"command": "guard"}]} }), encoding="utf-8"
        )
        return root

    def _target(self, root: Path) -> Path:
        target = root / "target"
        target.mkdir()
        return target

    def test_preview_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)

            actions = self.installer.install(source, target, write=False, copy_adapters=True)

            self.assertTrue(actions)
            self.assertEqual(list(target.iterdir()), [])

    def test_refreshed_instruction_block_moves_to_file_end(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            begin = self.installer.marker("agents.md")
            end = self.installer.marker("agents.md", end=True)
            (target / "AGENTS.md").write_text(
                f"before\n\n{begin}\nold\n{end}\n\nafter\n", encoding="utf-8"
            )

            self.installer.install(source, target, write=True, copy_adapters=False)

            text = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("before", text)
            self.assertIn("after", text)
            self.assertTrue(text.rstrip().endswith(end))

    def test_rejects_the_template_source_as_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = self._source(Path(temp) / "source")

            with self.assertRaisesRegex(self.installer.InstallConflict, "must not be the template source"):
                self.installer.install(source, source, write=False, copy_adapters=False)

    def test_preserves_unknown_content_and_backs_up_mutated_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            (target / "AGENTS.md").write_text("local rules\n", encoding="utf-8")
            (target / "CLAUDE.md").write_text("local claude\n", encoding="utf-8")
            (target / "Makefile").write_text("project-target:\n\t@true\n", encoding="utf-8")
            (target / ".claude").mkdir()
            (target / ".codex").mkdir()
            (target / ".claude" / "settings.json").write_text(
                json.dumps({"custom": True, "hooks": {"SessionStart": [{"command": "local"}]}}), encoding="utf-8"
            )
            (target / ".codex" / "hooks.json").write_text(
                json.dumps({"custom": True, "hooks": {"PreToolUse": [{"command": "local"}]}}), encoding="utf-8"
            )

            self.installer.install(source, target, write=True, copy_adapters=True)

            self.assertIn("local rules", (target / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertIn("BEGIN agent-template:agents.md", (target / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertTrue(list(target.glob("AGENTS.md.bak-*")))
            self.assertTrue(list(target.glob("CLAUDE.md.bak-*")))
            settings = json.loads((target / ".claude" / "settings.json").read_text(encoding="utf-8"))
            self.assertTrue(settings["custom"])
            self.assertEqual(len(settings["hooks"]["SessionStart"]), 2)
            self.assertTrue(list((target / ".claude").glob("settings.json.bak-*")))
            self.assertTrue(list((target / ".codex").glob("hooks.json.bak-*")))
            self.assertEqual(
                (target / "Makefile").read_text(encoding="utf-8"), "project-target:\n\t@true\n"
            )

    def test_second_install_is_stable_and_user_skill_survives(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            (target / ".agents" / "skills" / "user").mkdir(parents=True)
            (target / ".agents" / "skills" / "user" / "SKILL.md").write_text("user skill\n", encoding="utf-8")

            self.installer.install(source, target, write=True, copy_adapters=True)
            self.assertEqual(self.installer.install(source, target, write=True, copy_adapters=True), [])
            self.assertTrue((target / ".agents" / "skills" / "user" / "SKILL.md").exists())

    def test_unowned_same_name_conflict_aborts_without_partial_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            (target / ".agents" / "tools").mkdir(parents=True)
            (target / ".agents" / "tools" / "tool.py").write_text("different\n", encoding="utf-8")

            with self.assertRaisesRegex(self.installer.InstallConflict, "unowned conflict: .agents/tools"):
                self.installer.install(source, target, write=True, copy_adapters=True)

            self.assertFalse((target / "AGENTS.md").exists())

    def test_upgrade_replaces_an_unmodified_canonical_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=False)
            (source / ".agents" / "tools" / "tool.py").write_text("upgraded\n", encoding="utf-8")

            actions = self.installer.install(source, target, write=True, copy_adapters=False)

            self.assertIn("upgrade: .agents/tools/tool.py", actions)
            self.assertEqual((target / ".agents" / "tools" / "tool.py").read_text(encoding="utf-8"), "upgraded\n")
            manifest = json.loads((target / ".agents" / ".template-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["files"][".agents/tools/tool.py"], self.installer.file_hash(source / ".agents" / "tools" / "tool.py"))

    def test_upgrade_stops_when_project_modified_a_canonical_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=False)
            (target / ".agents" / "tools" / "tool.py").write_text("project edit\n", encoding="utf-8")
            (source / ".agents" / "tools" / "tool.py").write_text("upgraded\n", encoding="utf-8")

            with self.assertRaisesRegex(self.installer.InstallConflict, "unowned conflict: .agents/tools/tool.py"):
                self.installer.install(source, target, write=True, copy_adapters=False)

            self.assertEqual((target / ".agents" / "tools" / "tool.py").read_text(encoding="utf-8"), "project edit\n")

    def test_removes_stale_unmodified_canonical_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=False)
            (source / ".agents" / "tools" / "tool.py").unlink()

            actions = self.installer.install(source, target, write=True, copy_adapters=False)

            self.assertIn("remove stale: .agents/tools/tool.py", actions)
            self.assertFalse((target / ".agents" / "tools" / "tool.py").exists())

    def test_stale_project_modified_file_blocks_removal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=False)
            (target / ".agents" / "tools" / "tool.py").write_text("project edit\n", encoding="utf-8")
            (source / ".agents" / "tools" / "tool.py").unlink()

            with self.assertRaisesRegex(self.installer.InstallConflict, "unowned conflict: .agents/tools/tool.py"):
                self.installer.install(source, target, write=True, copy_adapters=False)

            self.assertTrue((target / ".agents" / "tools" / "tool.py").exists())

    def test_hook_upgrade_replaces_template_hook_and_preserves_unknown_hook(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=False)
            settings_path = target / ".claude" / "settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings["hooks"]["SessionStart"].append({"command": "local"})
            settings_path.write_text(json.dumps(settings), encoding="utf-8")
            (source / ".claude" / "settings.json").write_text(
                json.dumps({"hooks": {"SessionStart": [{"command": "template-v2"}]}}), encoding="utf-8"
            )

            self.installer.install(source, target, write=True, copy_adapters=False)

            hooks = json.loads(settings_path.read_text(encoding="utf-8"))["hooks"]["SessionStart"]
            self.assertEqual(hooks, [{"command": "local"}, {"command": "template-v2"}])

    def test_copy_adapter_upgrades_when_its_prior_copy_is_unmodified(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=True)
            (source / ".agents" / "skills" / "core" / "SKILL.md").write_text("upgraded skill\n", encoding="utf-8")

            self.installer.install(source, target, write=True, copy_adapters=True)

            self.assertEqual(
                (target / ".claude" / "skills" / "core" / "SKILL.md").read_text(encoding="utf-8"),
                "upgraded skill\n",
            )

    def test_copy_adapter_prunes_a_stale_owned_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=True)
            (source / ".agents" / "skills" / "core" / "SKILL.md").unlink()

            self.installer.install(source, target, write=True, copy_adapters=True)

            self.assertFalse((target / ".claude" / "skills" / "core" / "SKILL.md").exists())

    def test_symlink_and_copy_adapter_modes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=False)
            self.assertTrue((target / ".claude" / "skills").is_symlink())
            self.assertTrue((target / ".claude" / "agents").is_symlink())

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=True)
            self.assertFalse((target / ".claude" / "skills").is_symlink())
            self.assertEqual(
                (target / ".claude" / "skills" / "core" / "SKILL.md").read_text(encoding="utf-8"), "skill\n"
            )

    def test_project_context_becomes_project_owned_after_seed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            self.installer.install(source, target, write=True, copy_adapters=False)
            context = target / ".agents" / "project-context.md"
            context.write_text("project-specific context\n", encoding="utf-8")
            (source / ".agents" / "project-context.md").write_text("new template seed\n", encoding="utf-8")

            self.installer.install(source, target, write=True, copy_adapters=False)

            self.assertEqual(context.read_text(encoding="utf-8"), "project-specific context\n")

    def test_rejects_manifest_path_outside_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            manifest = target / ".agents" / ".template-manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                json.dumps({"files": {"../outside": "0" * 64}, "adapters": {}, "hooks": {}}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(self.installer.InstallConflict, "unsafe manifest path"):
                self.installer.install(source, target, write=True, copy_adapters=False)

    def test_rejects_canonical_path_through_external_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = self._source(root / "source"), self._target(root)
            outside = root / "outside"
            outside.mkdir()
            (target / ".agents").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(self.installer.InstallConflict, "escapes project"):
                self.installer.install(source, target, write=True, copy_adapters=False)


if __name__ == "__main__":
    unittest.main()
