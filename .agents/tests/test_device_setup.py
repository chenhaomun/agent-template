from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]


def load_installer():
    spec = importlib.util.spec_from_file_location("device_setup", ROOT / ".claude" / "device-setup" / "install.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeviceSetupTest(unittest.TestCase):
    def test_preview_does_not_copy_custom_theme(self) -> None:
        installer = load_installer()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            here = root / "source"
            (here / "themes").mkdir(parents=True)
            (here / "themes" / "ocean.json").write_text("{}", encoding="utf-8")
            (here / "settings.example.json").write_text(json.dumps({"theme": "custom:ocean"}), encoding="utf-8")
            target = root / "home" / "settings.json"
            themes = target.parent / "themes"

            with contextlib.redirect_stdout(io.StringIO()):
                installer.cmd_apply(SimpleNamespace(write=False), here, target, themes)

            self.assertFalse(target.exists())
            self.assertFalse(themes.exists())

    def test_theme_name_cannot_escape_themes_directory(self) -> None:
        installer = load_installer()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(SystemExit, "invalid custom theme name"):
                installer.copy_custom_themes(root, "custom:../notes", root / "target")
            self.assertFalse((root / "target").exists())

    def test_replacing_theme_backs_up_local_copy(self) -> None:
        installer = load_installer()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = root / "source", root / "target"
            source.mkdir()
            target.mkdir()
            (source / "ocean.json").write_text("new", encoding="utf-8")
            (target / "ocean.json").write_text("local", encoding="utf-8")

            installer.copy_custom_themes(source, "custom:ocean", target, write=True)

            backups = list(target.glob("ocean.json.bak-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "local")
            self.assertEqual((target / "ocean.json").read_text(encoding="utf-8"), "new")
