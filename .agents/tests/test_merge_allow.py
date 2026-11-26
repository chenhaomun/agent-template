from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import install_template
from install_template import CLAUDE_ALLOW, SOURCE_ROOT, InstallConflict, merge_allow


class MergeAllowTest(unittest.TestCase):
    def test_adds_rules_to_empty_settings(self) -> None:
        self.assertEqual(merge_allow({}, CLAUDE_ALLOW)["permissions"]["allow"], list(CLAUDE_ALLOW))

    def test_keeps_existing_rules_and_deny_list(self) -> None:
        current = {"permissions": {"allow": ["Bash(ls)", CLAUDE_ALLOW[0]], "deny": ["Bash(rm:*)"]}, "model": "x"}
        merged = merge_allow(current, CLAUDE_ALLOW)
        self.assertEqual(merged["permissions"]["allow"], ["Bash(ls)", *CLAUDE_ALLOW])
        self.assertEqual(merged["permissions"]["deny"], ["Bash(rm:*)"])
        self.assertEqual(merged["model"], "x")

    def test_unchanged_when_present(self) -> None:
        current = {"permissions": {"allow": list(CLAUDE_ALLOW)}}
        self.assertIs(merge_allow(current, CLAUDE_ALLOW), current)

    def test_rules_match_template_settings(self) -> None:
        allow = json.loads((SOURCE_ROOT / ".claude/settings.json").read_text(encoding="utf-8"))["permissions"]["allow"]
        self.assertTrue(set(CLAUDE_ALLOW) <= set(allow))

    def test_install_labels_only_what_changed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            settings = target / ".claude/settings.json"
            settings.parent.mkdir()
            settings.write_text(json.dumps({"permissions": {"allow": ["Bash(ls)"]}}), encoding="utf-8")

            changes = install_template.install(SOURCE_ROOT, target, write=False, copy_adapters=True)
            self.assertIn("merge template hooks and permissions: .claude/settings.json", changes)
            with contextlib.redirect_stdout(io.StringIO()):
                install_template.install(SOURCE_ROOT, target, write=True, copy_adapters=True)
            allow = json.loads(settings.read_text(encoding="utf-8"))["permissions"]["allow"]
            self.assertEqual(allow, ["Bash(ls)", *CLAUDE_ALLOW])

            data = json.loads(settings.read_text(encoding="utf-8"))
            data["permissions"]["allow"] = ["Bash(ls)"]
            settings.write_text(json.dumps(data), encoding="utf-8")
            changes = install_template.install(SOURCE_ROOT, target, write=False, copy_adapters=True)
            self.assertIn("merge template permissions: .claude/settings.json", changes)

    def test_rejects_invalid_allow(self) -> None:
        with self.assertRaises(InstallConflict):
            merge_allow({"permissions": {"allow": "Bash(*)"}}, CLAUDE_ALLOW)


if __name__ == "__main__":
    unittest.main()
