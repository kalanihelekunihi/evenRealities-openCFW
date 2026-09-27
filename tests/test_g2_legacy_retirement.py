"""Check retired entrypoints only in isolated copies, never on the live queue."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LegacyRetirementTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'tools').mkdir()
        for relative in ('continue-analysis.sh', 'tools/continue_analysis_session.py',
                         'tools/continue_analysis_dependencies.py'):
            shutil.copy2(ROOT / relative, self.root / relative)
        self.probe = self.root / 'provider-probe.sh'
        self.probe.write_text('#!/bin/sh\ntouch "$(dirname "$0")/provider-invoked"\nexit 99\n')
        self.probe.chmod(0o755)
        self.env = dict(os.environ, CA_CLI='retired-provider', CA_CLI_BIN=str(self.probe),
                        PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1')

    def snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes() if path.is_file() else None
                for path in self.root.rglob('*')}

    def shell(self, *args, env=None):
        return subprocess.run(['bash', str(self.root / 'continue-analysis.sh'), *args],
                              cwd=self.root, env=env or self.env, text=True,
                              capture_output=True, timeout=5)

    def supervisor(self, *args):
        return subprocess.run([sys.executable, str(self.root / 'tools/continue_analysis_session.py'),
                               *args], cwd=self.root, env=self.env, text=True,
                              capture_output=True, timeout=5)

    def create_queue(self):
        (self.root / 'remaining-work.md').write_text(
            '| AM-001 | P1 | todo | `0x100..0x110` | 16 | code | historical fixture | | |\n')
        (self.root / 'remaining-work.json').write_text(json.dumps({
            'meta': {}, 'items': [{'id': 'AM-001', 'component': 'apollo_main'}]}))

    def create_checkpoint(self):
        state = self.root / 'build/continue-analysis'
        for name in ('paused', 'logs', 'results', 'running', 'deferred'):
            (state / name).mkdir(parents=True, exist_ok=True)
        prompt = self.root / 'historical-prompt.md'
        prompt.write_text('Historical fixture; never execute.')
        checkpoint = state / 'paused/AM-001.test.json'
        checkpoint.write_text(json.dumps(dict(
            root=str(self.root), id='AM-001', stamp='test', sid='test-session',
            prompt=str(prompt), timeout=0, cmd=[str(self.probe)], resume_at=1)))
        return checkpoint

    def test_all_other_commands_reject_before_interpreter_or_state_access(self):
        before = self.snapshot()
        commands = (
            ('run', '-n', '1'), ('run', '--dry-run'), ('run', '--override'),
            ('resume-paused',), ('prompt', 'AM-001'), ('dependencies',),
            ('dependencies', '--reconcile'), ('dependencies', '--json'),
            ('claim', 'AM-001'), ('release', 'AM-001'), ('done', 'AM-001'),
            ('fail', 'AM-001'), ('block', 'AM-001'), ('reset-stale',),
            ('regenerate',), ('lock', 'status'), ('lock', 'acquire', 'AM-001'),
            ('lock', 'release', 'AM-001'), ('--override', 'run'), ('unknown',),
        )
        for command in commands:
            with self.subTest(command=command):
                result = self.shell(*command, env=dict(self.env, PYTHON=str(self.probe)))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('retired', result.stderr)
                self.assertIn('g2/workflow/README.md', result.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_help_needs_no_queue_provider_or_state(self):
        before = self.snapshot()
        for command in ((), ('help',), ('-h',), ('--help',)):
            with self.subTest(command=command):
                result = self.shell(*command, env=dict(self.env, PYTHON=str(self.probe)))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('retired', result.stdout)
                self.assertIn('Read-only historical diagnostics', result.stdout)
                self.assertEqual(self.snapshot(), before)

    def test_diagnostics_are_read_only_with_no_state(self):
        self.create_queue()
        before = self.snapshot()
        for command in (('status',), ('list', '--status', 'todo'),
                        ('show', 'AM-001'), ('logs', 'AM-001')):
            with self.subTest(command=command):
                result = self.shell(*command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_existing_queue_and_sessions_remain_unchanged(self):
        self.create_queue()
        checkpoint = self.create_checkpoint()
        log = self.root / 'build/continue-analysis/logs/AM-001.test.json'
        log.write_text('{"result": "historical result"}')
        before = self.snapshot()
        for command in (('status',), ('list',), ('show', 'AM-001'), ('logs', 'AM-001')):
            with self.subTest(command=command):
                result = self.shell(*command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.snapshot(), before)
        for command in (('resume-paused',), ('dependencies', '--reconcile'), ('claim', 'AM-001')):
            result = self.shell(*command)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(self.snapshot(), before)
        result = self.supervisor(str(checkpoint))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('g2/workflow/README.md', result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_supervisor_help_and_describe_are_read_only(self):
        checkpoint = self.create_checkpoint()
        before = self.snapshot()
        for args in ((), ('--help',), ('--describe', str(checkpoint))):
            with self.subTest(args=args):
                result = self.supervisor(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('retired', result.stdout)
                self.assertEqual(self.snapshot(), before)

    def test_supervisor_rejects_missing_checkpoint_before_creating_lock(self):
        before = self.snapshot()
        result = self.supervisor(str(self.root / 'missing.json'))
        self.assertEqual(result.returncode, 2)
        self.assertIn('retired', result.stderr)
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
