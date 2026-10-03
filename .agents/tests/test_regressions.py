from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

from test_agent_tools import ROOT, load_tool
import test_install_template


class InstallerRegressionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = test_install_template.InstallTemplateTest()
        self.fixture.setUp()
        self.installer = self.fixture.installer

    def test_nested_adapter_symlink_aborts_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source = self.fixture._source(root / "source")
            target = self.fixture._target(root)
            outside = root / "outside"
            outside.mkdir()
            adapter = target / ".claude/skills/core"
            adapter.parent.mkdir(parents=True)
            adapter.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(self.installer.InstallConflict):
                self.installer.install(source, target, write=True, copy_adapters=True)
            self.assertEqual(list(outside.iterdir()), [])
            self.assertFalse((target / "AGENTS.md").exists())

    def test_distribution_excludes_local_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source = self.fixture._source(root / "source")
            folder = source / ".agents/skills/core"
            for name in ("notes.md.bak-123", ".env", ".env.local", "settings.local.json"):
                (folder / name).write_text("local", encoding="utf-8")
            (folder / ".env.example").write_text("EXAMPLE=", encoding="utf-8")
            files = self.installer.template_files(source)
            self.assertIn(".agents/skills/core/.env.example", files)
            self.assertFalse(any(".bak-" in name or name.endswith(".local") for name in files))
            self.assertNotIn(".agents/skills/core/.env", files)
            self.assertNotIn(".agents/skills/core/settings.local.json", files)

    def test_fresh_install_context_describes_destination_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source = self.fixture._source(root / "source")
            target = self.fixture._target(root)
            (target / "lib/features/login").mkdir(parents=True)
            self.installer.install(source, target, write=True, copy_adapters=True)
            checker = load_tool("check_project_context")
            self.assertEqual(checker.check_context(target), [])
            content = (target / ".agents/project-context.md").read_text(encoding="utf-8")
            self.assertNotIn("Reusable agent-configuration template", content)
            self.assertIn("lib/features/login", content)


class AdapterRegressionTest(unittest.TestCase):
    def test_metadata_validator_rejects_flat_ui_fields(self) -> None:
        library = load_tool("_template_lib")
        flat = 'display_name: Example\nshort_description: Example\ndefault_prompt: Example\n'
        self.assertTrue(library.openai_metadata_errors(flat))
        nested = "interface:\n" + "\n".join("  " + line for line in flat.splitlines()) + "\n"
        self.assertEqual(library.openai_metadata_errors(nested), [])

    def test_same_name_custom_role_is_preserved(self) -> None:
        sync = load_tool("sync_shared")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = root / "source", root / "target"
            source.mkdir()
            target.mkdir()
            (source / "developer.md").write_text(
                "---\nname: developer\ndescription: Developer\n---\nTemplate role", encoding="utf-8"
            )
            custom = target / "developer.toml"
            content = 'name = "custom"\n'
            custom.write_text(content, encoding="utf-8")
            with patch.object(sync, "SUBAGENTS", source), patch.object(sync, "CODEX_AGENTS", target):
                with self.assertRaisesRegex(RuntimeError, "unowned"):
                    sync.generate_codex_agents([])
            self.assertEqual(custom.read_text(encoding="utf-8"), content)

    def test_instruction_backslashes_and_control_characters_round_trip(self) -> None:
        import tomllib

        sync = load_tool("sync_shared")
        for body in (r"Use C:\Users\example.", r"Match \bword\b.", 'quote"\n\t\r\b\f'):
            with self.subTest(body=body):
                result = tomllib.loads(sync.render_codex_toml("dev", "Description\nwith tab\t", body))
                self.assertEqual(result["developer_instructions"], body)
                self.assertEqual(result["description"], "Description\nwith tab\t")

    def test_legacy_metadata_migrates_without_losing_custom_prompt(self) -> None:
        sync = load_tool("sync_shared")
        with tempfile.TemporaryDirectory() as temp:
            skills = Path(temp)
            skill = skills / "example"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: example\ndescription: Example\n---\nBody", encoding="utf-8"
            )
            adapter = skill / "agents/openai.yaml"
            adapter.write_text('display_name: Example\nshort_description: Custom\ndefault_prompt: "Keep this"\n', encoding="utf-8")
            with patch.object(sync, "SKILLS", skills):
                sync.generate_openai_adapters([])
                first = adapter.read_text(encoding="utf-8")
                sync.generate_openai_adapters([])
            self.assertIn('interface:\n  display_name: Example', first)
            self.assertIn('  default_prompt: "Keep this"', first)
            self.assertEqual(adapter.read_text(encoding="utf-8"), first)


class ConfigMergeRegressionTest(unittest.TestCase):
    def test_array_tables_and_multiline_values_survive_merge(self) -> None:
        import tomllib

        spec = importlib.util.spec_from_file_location("codex_setup", ROOT / ".codex/install.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        current = (
            'model = "old"\nnotes = """\n[not_a_table]\nmodel = example\n"""\n'
            '[[skills.config]]\npath = "./one"\nenabled = false\n'
            '[[skills.config]]\npath = "./two"\nenabled = false\n'
            '[desktop]\ncustom = [\n  "keep",\n]\n'
        )
        example = 'model = "new"\n[desktop]\nreviewDelivery = "inline"\n'
        merged, _ = module.merge_config(current, example)
        data = tomllib.loads(merged)
        self.assertEqual(data["skills"], tomllib.loads(current)["skills"])
        self.assertEqual(data["notes"], tomllib.loads(current)["notes"])
        self.assertEqual(data["desktop"]["custom"], ["keep"])
        self.assertEqual(data["model"], "new")
        self.assertEqual(module.merge_config(merged, example)[0], merged)
        with self.assertRaises(ValueError):
            module.merge_config('[invalid', example)


class ProjectCommandRegressionTest(unittest.TestCase):
    def test_explicit_wrapper_and_project_task_take_precedence(self) -> None:
        checks = load_tool("run_checks")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agents").mkdir()
            (root / ".fvmrc").write_text('{}', encoding="utf-8")
            (root / ".agents/project-commands.json").write_text(json.dumps({
                "dart": ["custom-sdk", "dart"], "analyze": ["project-check", "analyze"],
            }), encoding="utf-8")
            with patch.object(checks.shutil, "which", side_effect=lambda name: name):
                self.assertEqual(checks.sdk_command(root, "dart"), ["custom-sdk", "dart"])
                self.assertEqual(checks.project_command(root, "analyze"), ["project-check", "analyze"])

    def test_cached_fvm_sdk_is_selected_without_global_dart(self) -> None:
        checks = load_tool("run_checks")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sdk_bin = root / ".fvm/flutter_sdk/bin"
            sdk_bin.mkdir(parents=True)
            executable = sdk_bin / ("dart.bat" if os.name == "nt" else "dart")
            executable.write_text("", encoding="utf-8")
            with patch.object(checks.shutil, "which", return_value=None):
                self.assertEqual(checks.sdk_command(root, "dart"), [str(executable)])

    def test_missing_pinned_sdk_never_falls_back_to_global(self) -> None:
        checks = load_tool("run_checks")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".fvmrc").write_text('{}', encoding="utf-8")
            with patch.object(checks.shutil, "which", return_value="global-dart"):
                with self.assertRaisesRegex(FileNotFoundError, "FVM"):
                    checks.sdk_command(root, "dart")

    def test_hook_uses_wrapper_and_stops_after_format_failure(self) -> None:
        hook = load_tool("hook_format_analyze")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "pubspec.yaml").write_text('name: example', encoding="utf-8")
            (root / "app.dart").write_text('void main() {}', encoding="utf-8")
            payload = {"cwd": str(root), "tool_input": {"file_path": "app.dart"}}
            result = SimpleNamespace(returncode=1, stdout="format failed", stderr="")
            with patch.object(hook.sys, "stdin", io.StringIO(json.dumps(payload))), \
                 patch.object(hook.sys, "stderr", io.StringIO()), \
                 patch.object(hook, "sdk_command", return_value=["wrapper", "dart"]), \
                 patch.object(hook.subprocess, "run", return_value=result) as run:
                self.assertEqual(hook.main(), 2)
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.args[0][:3], ["wrapper", "dart", "format"])
            self.assertEqual(run.call_args.kwargs["cwd"], root.resolve())


if __name__ == "__main__":
    unittest.main()
