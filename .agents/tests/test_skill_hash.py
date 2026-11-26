from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import check_template
from _template_lib import skill_hash


class SkillHashTest(unittest.TestCase):
    def test_crlf_and_os_junk_do_not_change_hash(self) -> None:
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            Path(a, "SKILL.md").write_bytes(b"line one\nline two\n")
            Path(b, "SKILL.md").write_bytes(b"line one\r\nline two\r\n")
            Path(b, ".DS_Store").write_bytes(b"junk")
            self.assertEqual(skill_hash(Path(a)), skill_hash(Path(b)))

    def test_content_change_changes_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp, "SKILL.md")
            path.write_text("a", encoding="utf-8")
            before = skill_hash(Path(temp))
            path.write_text("b", encoding="utf-8")
            self.assertNotEqual(before, skill_hash(Path(temp)))


class LockCheckTest(unittest.TestCase):
    def run_check(self, root: Path) -> list[str]:
        old = check_template.ROOT
        try:
            check_template.ROOT = root
            errors: list[str] = []
            check_template.check_skills_lock(errors)
            return errors
        finally:
            check_template.ROOT = old

    def make_root(self, temp: str, lock_hash: str | None) -> Path:
        root = Path(temp)
        (root / ".agents/skills/one").mkdir(parents=True)
        (root / ".agents/skills/one/SKILL.md").write_text("x", encoding="utf-8")
        (root / ".agents/skills/two").mkdir()
        (root / ".agents/skills/two/SKILL.md").write_text("y", encoding="utf-8")
        entry = {"sourceType": "local", "skillPath": "skills/one/SKILL.md"}
        if lock_hash:
            entry["computedHash"] = lock_hash
        (root / "skills-lock.json").write_text(json.dumps({"skills": {"one": entry}}), encoding="utf-8")
        return root

    def test_template_source_flags_stale_hash_and_missing_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            errors = self.run_check(self.make_root(temp, "0" * 64))
            self.assertTrue(any("one computedHash is stale" in e for e in errors))
            self.assertTrue(any("no provenance entry for two" in e for e in errors))

    def test_installed_project_skips_hash_and_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp, "0" * 64)
            (root / ".agents/.template-manifest.json").write_text("{}", encoding="utf-8")
            self.assertEqual(self.run_check(root), [])


if __name__ == "__main__":
    unittest.main()
