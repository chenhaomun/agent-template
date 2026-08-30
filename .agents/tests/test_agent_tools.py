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
    # Tools import siblings as top-level modules (e.g. `import _template_lib`),
    # which only resolves with the tools dir on sys.path.
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
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


class ProjectContextFreshnessTest(unittest.TestCase):
    def test_fails_when_detected_source_folder_is_unmapped(self) -> None:
        checker = load_tool("check_project_context")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agents").mkdir()
            (root / "lib" / "features" / "auth").mkdir(parents=True)
            (root / ".agents" / "project-context.md").write_text(
                "# Project Context\n\n<!-- BEGIN GENERATED STRUCTURE -->\n"
                "### Generated Structure\n\nNo detected folders yet.\n"
                "<!-- END GENERATED STRUCTURE -->\n",
                encoding="utf-8",
            )

            errors = checker.check_context(root)

        self.assertIn("lib/features/auth", "\n".join(errors))


class SkillGatingTest(unittest.TestCase):
    def _skills(self, root: Path) -> Path:
        skills = root / "skills"
        for name, stack in (("flutter-x", "flutter"), ("dart-y", "dart"), ("generic-z", None)):
            (skills / name).mkdir(parents=True)
            front = f"name: {name}\n" + (f"stack: {stack}\n" if stack else "")
            (skills / name / "SKILL.md").write_text(
                f"---\n{front}description: d\n---\nbody\n", encoding="utf-8"
            )
        return skills

    def test_gates_stack_specific_skills(self) -> None:
        lib = load_tool("_template_lib")
        with tempfile.TemporaryDirectory() as temp:
            skills = self._skills(Path(temp))

            # Non-matching stack drops both stack-specific skills.
            self.assertEqual(lib.gated_skill_names(skills, {"node"}), {"flutter-x", "dart-y"})
            # Flutter pulls in Dart (implied), so neither is gated out.
            self.assertEqual(lib.gated_skill_names(skills, {"flutter"}), set())
            # Dart keeps Dart but still gates Flutter.
            self.assertEqual(lib.gated_skill_names(skills, {"dart"}), {"flutter-x"})
            # Unknown / empty detection never gates (full set is the safe default).
            self.assertEqual(lib.gated_skill_names(skills, {"unknown"}), set())
            self.assertEqual(lib.gated_skill_names(skills, set()), set())


class AdapterPreservationTest(unittest.TestCase):
    def test_copy_mirror_preserves_project_owned_entries(self) -> None:
        sync = load_tool("sync_shared")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = root / "source", root / "target"
            source.mkdir()
            target.mkdir()
            (source / "canonical.md").write_text("new\n", encoding="utf-8")
            (target / "custom.md").write_text("custom\n", encoding="utf-8")

            sync.mirror(source, target)

            self.assertTrue((target / "custom.md").exists())
            self.assertEqual((target / "canonical.md").read_text(encoding="utf-8"), "new\n")

    def test_codex_generation_preserves_unmarked_agent(self) -> None:
        sync = load_tool("sync_shared")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subagents, adapters = root / "subagents", root / "agents"
            subagents.mkdir()
            adapters.mkdir()
            (subagents / "dev.md").write_text(
                "---\nname: dev\ndescription: Developer.\n---\nBody\n", encoding="utf-8"
            )
            custom = adapters / "custom.toml"
            custom.write_text('name = "custom"\n', encoding="utf-8")
            old_source, old_adapters = sync.SUBAGENTS, sync.CODEX_AGENTS
            try:
                sync.SUBAGENTS, sync.CODEX_AGENTS = subagents, adapters
                sync.generate_codex_agents([])
            finally:
                sync.SUBAGENTS, sync.CODEX_AGENTS = old_source, old_adapters

            self.assertTrue(custom.exists())
            self.assertTrue((adapters / "dev.toml").read_text(encoding="utf-8").startswith(sync.GENERATED_HEADER))

    def test_integrity_check_allows_unmarked_codex_agent(self) -> None:
        sync = load_tool("sync_shared")
        check = load_tool("check_template")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subagents, adapters = root / ".agents" / "subagents", root / ".codex" / "agents"
            subagents.mkdir(parents=True)
            adapters.mkdir(parents=True)
            source = "---\nname: dev\ndescription: Developer.\n---\nBody\n"
            (subagents / "dev.md").write_text(source, encoding="utf-8")
            (adapters / "dev.toml").write_text(
                sync.render_codex_toml("dev", "Developer.", "Body"), encoding="utf-8"
            )
            (adapters / "custom.toml").write_text("project owned\n", encoding="utf-8")
            (root / ".codex" / "hooks.json").write_text(
                json.dumps({"hooks": {"PreToolUse": [], "PostToolUse": [], "SessionStart": []}}),
                encoding="utf-8",
            )
            old_root = check.ROOT
            try:
                check.ROOT = root
                errors: list[str] = []
                check.check_codex(errors, 1)
            finally:
                check.ROOT = old_root

            self.assertEqual(errors, [])


class FrontmatterTest(unittest.TestCase):
    def test_strips_surrounding_quotes_from_scalars(self) -> None:
        lib = load_tool("_template_lib")

        front, body = lib.parse_frontmatter('---\nname: "foo"\ndesc: \'bar\'\n---\nbody\n')

        self.assertEqual(front["name"], "foo")
        self.assertEqual(front["desc"], "bar")
        self.assertEqual(body, "body")

    def test_keeps_bare_scalars_unchanged(self) -> None:
        lib = load_tool("_template_lib")

        front, _ = lib.parse_frontmatter("---\nname: foo\n---\nbody\n")

        self.assertEqual(front["name"], "foo")


class CodexTomlTest(unittest.TestCase):
    def test_body_with_triple_quote_round_trips(self) -> None:
        sync = load_tool("sync_shared")
        check = load_tool("check_template")
        body = 'use """triple""" and a "quote" here'

        toml = sync.render_codex_toml("dev", "d", body)
        parsed = check.parse_agent_toml(toml)

        # No silent drop: the body survives a render -> parse round trip.
        self.assertEqual(parsed["developer_instructions"], body)
        self.assertEqual(parsed["name"], "dev")

    def test_plain_body_uses_multiline_string(self) -> None:
        sync = load_tool("sync_shared")
        check = load_tool("check_template")
        body = "line one\nline two"

        parsed = check.parse_agent_toml(sync.render_codex_toml("dev", "d", body))

        self.assertEqual(parsed["developer_instructions"], body)


class CodexConfigTest(unittest.TestCase):
    def test_example_enables_documented_sol_context_window(self) -> None:
        if sys.version_info < (3, 11):
            self.skipTest("tomllib requires Python 3.11")
        import tomllib

        config = tomllib.loads((ROOT / ".codex" / "config.example.toml").read_text(encoding="utf-8"))

        self.assertEqual(config["model"], "gpt-5.6-sol")
        self.assertEqual(config["model_context_window"], 1_050_000)


if __name__ == "__main__":
    unittest.main()
