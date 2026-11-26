from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import review_gate


class ReviewGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        self.write("app.txt", "v1\n")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-qm", "init"],
            cwd=self.root,
            check=True,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, text: str) -> None:
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        stamp = path.stat().st_mtime_ns + 1_000_000_000
        os.utime(path, ns=(stamp, stamp))

    def payload(self) -> dict:
        return {"cwd": str(self.root), "session_id": "s1"}

    def turn(self) -> None:
        review_gate.turn_start(self.payload())

    def stop(self) -> dict:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            review_gate.stop(self.payload())
        return json.loads(out.getvalue()) if out.getvalue().strip() else {}

    def record(self, result: str, note: str = "") -> int:
        previous = Path.cwd()
        os.chdir(self.root)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return review_gate.record(result, note)
        finally:
            os.chdir(previous)

    def test_answer_only_turn_finishes(self) -> None:
        self.turn()
        self.assertEqual(self.stop(), {})

    def test_user_changes_before_turn_do_not_block(self) -> None:
        self.write("app.txt", "user edit\n")
        self.turn()
        self.assertEqual(self.stop(), {})

    def test_agent_change_blocks_until_recorded_and_again_after_new_edit(self) -> None:
        self.turn()
        self.write("app.txt", "v2\n")
        self.assertEqual(self.stop().get("decision"), "block")

        self.assertEqual(self.record("clean"), 0)
        self.assertEqual(self.stop(), {})

        self.turn()
        self.write("new.txt", "x\n")
        self.assertEqual(self.stop().get("decision"), "block")

    def test_unreviewed_change_still_blocks_on_next_turn(self) -> None:
        self.turn()
        self.write("app.txt", "v2\n")
        self.assertEqual(self.stop().get("decision"), "block")
        self.turn()
        self.assertEqual(self.stop().get("decision"), "block")

    def test_interrupted_turn_edits_still_need_review(self) -> None:
        self.turn()
        self.write("app.txt", "v2\n")
        self.turn()
        self.assertEqual(self.stop().get("decision"), "block")

    def test_block_cap_is_per_turn_even_when_edits_continue(self) -> None:
        self.turn()
        for index in range(review_gate.MAX_BLOCKS):
            self.write("app.txt", f"edit {index}\n")
            self.assertEqual(self.stop().get("decision"), "block")
        self.write("app.txt", "one more\n")
        self.assertNotIn("decision", self.stop())

    def test_pending_review_lets_turn_end(self) -> None:
        self.turn()
        self.write("app.txt", "v2\n")
        self.assertEqual(self.record("pending"), 0)
        self.assertEqual(self.stop(), {})

    def test_gives_up_after_max_blocks(self) -> None:
        self.turn()
        self.write("app.txt", "v2\n")
        for _ in range(review_gate.MAX_BLOCKS):
            self.assertEqual(self.stop().get("decision"), "block")
        self.assertNotIn("decision", self.stop())

    def test_missing_turn_state_allows_and_sets_baseline(self) -> None:
        self.write("app.txt", "already dirty\n")
        self.assertEqual(self.stop(), {})
        self.write("app.txt", "agent edit\n")
        self.assertEqual(self.stop().get("decision"), "block")

    def test_accepted_and_skip_need_note(self) -> None:
        self.assertEqual(self.record("skip"), 1)
        self.assertEqual(self.record("accepted"), 1)

    def test_outside_git_does_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as plain:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                review_gate.stop({"cwd": plain, "session_id": "s1"})
            self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
