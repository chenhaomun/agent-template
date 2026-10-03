"""Exercise the real template's preview, install, sync, and upgrade lifecycle."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".agents/tools"))
import install_template


def run(root: Path, script: str) -> None:
    result = subprocess.run(
        [sys.executable, str(root / ".agents/tools" / script)], cwd=root,
        capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode:
        raise AssertionError((result.stdout + result.stderr)[-4000:])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="agent-template-smoke-") as temp:
        root = Path(temp).resolve()
        source = root / "source"
        files = install_template.template_files(ROOT)
        for name in (*install_template.INSTRUCTION_FILES, *install_template.HOOK_FILES):
            files[name] = ROOT / name
        for relative, original in files.items():
            destination = source / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, destination)
        for mode in (True, False):
            target = root / ("copy-project" if mode else "symlink-project")
            target.mkdir()
            instructions = target / "AGENTS.md"
            instructions.write_text("Keep this project rule.\n", encoding="utf-8")
            (target / "src").mkdir()
            install_template.install(source, target, write=False, copy_adapters=mode)
            assert not (target / ".agents").exists(), "preview wrote files"
            install_template.install(source, target, write=True, copy_adapters=mode)
            custom = target / ".codex/agents/project-custom.toml"
            custom.write_text('name = "project-custom"\n', encoding="utf-8")
            for script in ("sync_shared.py", "check_template.py", "check_project_context.py"):
                run(target, script)
            tool = source / ".agents/tools/detect_project.py"
            tool.write_text(tool.read_text(encoding="utf-8") + "\n# Smoke upgrade revision.\n", encoding="utf-8")
            install_template.install(source, target, write=True, copy_adapters=mode)
            assert (target / ".agents/tools/detect_project.py").read_bytes() == tool.read_bytes()
            assert custom.read_text(encoding="utf-8") == 'name = "project-custom"\n'
            assert "Keep this project rule." in instructions.read_text(encoding="utf-8")
            assert not install_template.install(source, target, write=False, copy_adapters=mode)
            for script in ("check_template.py", "check_project_context.py"):
                run(target, script)
    print("OK install smoke: preview, copy/symlink install, sync, upgrade, preservation, idempotence")


if __name__ == "__main__":
    main()
