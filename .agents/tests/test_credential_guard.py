from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / '.agents/tools/hook_guard_credentials.py'


class CredentialGuardTest(unittest.TestCase):
    def run_guard(self, payload, cwd=ROOT):
        return subprocess.run(
            [sys.executable, str(GUARD)], input=json.dumps(payload),
            text=True, capture_output=True, cwd=cwd,
        )

    def test_blocks_direct_reads_without_echoing_payload(self):
        for path in ['.env', 'config/.env.production', 'android/key.properties',
                     'keys/release.jks', 'keys/AuthKey.p8', '.aws/credentials',
                     'service-account.json', 'production/credentials.json']:
            with self.subTest(path=path):
                result = self.run_guard({'tool_name': 'Read', 'tool_input': {'file_path': path}})
                self.assertEqual(result.returncode, 2)
                self.assertIn('Blocked by SECURITY.md', result.stderr)
                self.assertNotIn(path, result.stderr)

    def test_blocks_shell_and_nested_inputs(self):
        for command in ['cat .env.production', 'git show HEAD:.env',
                        'python3 -c "print(open(\'release.jks\').read())"',
                        'printenv', 'security find-generic-password -w',
                        'aws secretsmanager get-secret-value --secret-id test',
                        'aws ssm get-parameter --name test --with-decryption',
                        'echo "$API_TOKEN"', 'gh auth token']:
            with self.subTest(command=command):
                result = self.run_guard({'tool_name': 'exec_command', 'tool_input': {'cmd': command}})
                self.assertEqual(result.returncode, 2)
        result = self.run_guard({'tool_name': 'multi_tool', 'tool_input': {
            'calls': [{'tool_input': {'file_path': '.env.production'}}]}})
        self.assertEqual(result.returncode, 2)

    def test_resolves_symlinks_without_reading_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.env').write_text('DO_NOT_PRINT_THIS')
            (root / 'ordinary.txt').symlink_to(root / '.env')
            result = self.run_guard({'cwd': tmp, 'tool_name': 'Read',
                                     'tool_input': {'file_path': 'ordinary.txt'}}, root)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('DO_NOT_PRINT_THIS', result.stdout + result.stderr)

    def test_allows_source_and_example_schema(self):
        for path in ['lib/app.dart', '.env.example', 'config/.env.template', 'SECURITY.md',
                     '.agents/tools/hook_guard_credentials.py']:
            result = self.run_guard({'tool_name': 'Read', 'tool_input': {'file_path': path}})
            self.assertEqual(result.returncode, 0)
        result = self.run_guard({'tool_name': 'Bash', 'tool_input': {'command': 'git status --short'}})
        self.assertEqual(result.returncode, 0)

    def test_blocks_file_uri_and_windows_paths(self):
        for path in ['file:///tmp/%2Eenv.production', 'C:\\project\\.env.production']:
            result = self.run_guard({'tool_name': 'Read', 'tool_input': {'path': path}})
            self.assertEqual(result.returncode, 2)

    def test_hook_is_registered_for_all_tools_in_both_adapters(self):
        for name in ['.claude/settings.json', '.codex/hooks.json']:
            entries = json.loads((ROOT / name).read_text())['hooks']['PreToolUse']
            self.assertTrue(any(entry.get('matcher') == '.*' and any(
                'hook_guard_credentials.py' in hook.get('command', '')
                for hook in entry.get('hooks', [])) for entry in entries))

    def test_patch_checks_paths_not_documentation_content(self):
        safe = '*** Begin Patch\n*** Update File: SECURITY.md\n@@\n+Never read .env\n*** End Patch'
        result = self.run_guard({'tool_name': 'apply_patch', 'tool_input': safe})
        self.assertEqual(result.returncode, 0)
        result = self.run_guard({'tool_name': 'apply_patch', 'tool_input': safe.replace('SECURITY.md', '.env')})
        self.assertEqual(result.returncode, 2)

    def test_malformed_payload_fails_closed(self):
        for raw in ['{', '[]', 'null']:
            result = subprocess.run([sys.executable, str(GUARD)], input=raw,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
