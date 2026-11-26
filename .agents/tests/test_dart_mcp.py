from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import dart_mcp
import install_template
from install_template import InstallConflict, entry_hash, merge_mcp

DART = {"command": "python3", "args": ["launcher"]}
TEMPLATE = {"mcpServers": {"dart": DART}}


class MergeMcpTest(unittest.TestCase):
    def test_adds_server_to_empty_config(self) -> None:
        merged, owned = merge_mcp({}, TEMPLATE, {})
        self.assertEqual(merged, TEMPLATE)
        self.assertEqual(owned, {"dart": entry_hash(DART)})

    def test_keeps_project_owned_same_name_server_and_others(self) -> None:
        current = {"mcpServers": {"dart": {"command": "custom"}, "db": {"command": "x"}}, "other": 1}
        merged, owned = merge_mcp(current, TEMPLATE, {})
        self.assertEqual(merged, current)
        self.assertEqual(owned, {})

    def test_refreshes_unchanged_template_entry(self) -> None:
        old = {"command": "python3", "args": ["old"]}
        merged, owned = merge_mcp({"mcpServers": {"dart": old}}, TEMPLATE, {"dart": entry_hash(old)})
        self.assertEqual(merged["mcpServers"]["dart"], DART)
        self.assertEqual(owned, {"dart": entry_hash(DART)})

    def test_identical_unrecorded_entry_becomes_owned(self) -> None:
        _, owned = merge_mcp({"mcpServers": {"dart": dict(DART)}}, TEMPLATE, {})
        self.assertEqual(owned, {"dart": entry_hash(DART)})

    def test_project_edit_after_install_is_kept(self) -> None:
        edited = {"command": "fvm", "args": ["dart", "mcp-server"]}
        merged, owned = merge_mcp({"mcpServers": {"dart": edited}}, TEMPLATE, {"dart": entry_hash(DART)})
        self.assertEqual(merged["mcpServers"]["dart"], edited)
        self.assertEqual(owned, {})

    def test_rejects_non_object_servers(self) -> None:
        with self.assertRaises(InstallConflict):
            merge_mcp({"mcpServers": []}, TEMPLATE, {})

    @unittest.skipUnless((install_template.SOURCE_ROOT / ".mcp.json").is_file(), "template .mcp.json absent")
    def test_install_merges_with_backup_and_preview_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            config = target / ".mcp.json"
            config.write_text(json.dumps({"mcpServers": {"db": {}}}), encoding="utf-8")

            changes = install_template.install(install_template.SOURCE_ROOT, target, write=False, copy_adapters=True)
            self.assertIn("merge template MCP servers: .mcp.json", changes)
            self.assertEqual(json.loads(config.read_text(encoding="utf-8")), {"mcpServers": {"db": {}}})

            with contextlib.redirect_stdout(io.StringIO()):
                install_template.install(install_template.SOURCE_ROOT, target, write=True, copy_adapters=True)
            self.assertEqual(set(json.loads(config.read_text(encoding="utf-8"))["mcpServers"]), {"db", "dart"})
            self.assertEqual(len(list(target.glob(".mcp.json.bak-*"))), 1)


class DartMcpLauncherTest(unittest.TestCase):
    def test_missing_sdk_reports_and_fails(self) -> None:
        err = io.StringIO()
        with mock.patch.object(dart_mcp, "sdk_command", side_effect=FileNotFoundError("FVM SDK missing")):
            with contextlib.redirect_stderr(err):
                self.assertEqual(dart_mcp.main([]), 1)
        self.assertIn("dart mcp-server unavailable", err.getvalue())

    def test_command_uses_resolved_sdk(self) -> None:
        with mock.patch.object(dart_mcp, "sdk_command", return_value=["/sdk/bin/dart"]):
            self.assertEqual(dart_mcp.server_command(["--log-file", "x"]), ["/sdk/bin/dart", "mcp-server", "--log-file", "x"])


class CodexAddOnlyTest(unittest.TestCase):
    def test_existing_dart_server_is_kept(self) -> None:
        if sys.version_info < (3, 11):
            self.skipTest("tomllib requires Python 3.11")
        import importlib.util

        spec = importlib.util.spec_from_file_location("codex_install", install_template.SOURCE_ROOT / ".codex" / "install.py")
        assert spec and spec.loader
        codex = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(codex)
        example = '[mcp_servers.dart]\ncommand = "dart"\nargs = ["mcp-server"]\n'
        for current in (
            '[mcp_servers.dart]\ncommand = "fvm"\nargs = ["dart", "mcp-server"]\n',
            '[mcp_servers]\ndart = { command = "fvm", args = ["dart", "mcp-server"] }\n',
            'mcp_servers.dart.command = "fvm"\n',
        ):
            merged, actions = codex.merge_config(current, example)
            self.assertIn('"fvm"', merged)
            self.assertNotIn('command = "dart"', merged)
            self.assertIn("keep existing [mcp_servers.dart]", actions)


if __name__ == "__main__":
    unittest.main()
