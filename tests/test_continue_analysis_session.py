import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('session', Path(__file__).resolve().parents[1] / 'tools/continue_analysis_session.py')
session = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(session)


class SessionTests(unittest.TestCase):
    def test_resume_restores_current_policy_and_checkpoint_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            policy = root / 'docs/g2-reconstruction-driver-prompt.md'
            policy.write_text('Display introduction\n---\nUpdated C recovery policy')
            text = session.resume_prompt({'root': directory, 'id': 'AM-001'})
            self.assertIn('knowledge/AM-001.json', text)
            self.assertIn('Updated C recovery policy', text)
            self.assertNotIn('Display introduction', text)
            self.assertIn('working-tree input hashes', text)
            self.assertIn('record blocked', text)
            policy.write_text('Display introduction\n---\nNewer policy')
            self.assertIn('Newer policy', session.resume_prompt({'root': directory, 'id': 'AM-001'}))

    def test_reset_timezone_and_rollover(self):
        now = dt.datetime(2026, 9, 11, 18, tzinfo=dt.timezone.utc)
        msg = "You've hit your session limit · resets 4:30pm (America/Chicago)"
        self.assertEqual(session.reset_time(msg, now), dt.datetime(2026, 9, 11, 21, 31, tzinfo=dt.timezone.utc).timestamp())
        self.assertEqual(session.reset_time(msg, now + dt.timedelta(hours=5)), dt.datetime(2026, 9, 12, 21, 31, tzinfo=dt.timezone.utc).timestamp())
        local_reset = session.reset_time("You've hit your usage limit; resets at 4:30pm", now)
        self.assertGreater(local_reset, now.timestamp())
        self.assertEqual(session.reset_time('usage limit reached', now), now.timestamp() + 900)
        self.assertEqual(session.reset_time("You've hit your session limit", now), now.timestamp() + 900)
        self.assertIsNone(session.reset_time('Authentication failed', now))

    def fixture(self, root, code):
        state = root / 'build/continue-analysis'
        for name in ('logs', 'results', 'paused'):
            (state / name).mkdir(parents=True)
        mock = root / 'mock.py'
        mock.write_text(code)
        prompt = root / 'prompt.md'
        prompt.write_text('Original assignment')
        cp = state / 'paused/AM-001.test.json'
        session.atomic_json(cp, dict(root=str(root), id='AM-001', stamp='test', sid='known-session',
                                    prompt=str(prompt), timeout=0, cmd=[sys.executable, str(mock)]))
        return state, cp

    def test_limit_preserves_progress_and_resumes_same_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, cp = self.fixture(root, '''import json,sys,pathlib
p=pathlib.Path('progress.c')
if '--session-id' in sys.argv:
    assert sys.argv[-1]=='known-session'
    p.write_text('completed work')
    pathlib.Path('build/continue-analysis/results/AM-001.json').write_text('{"status":"partial"}')
    print(json.dumps(dict(is_error=True,result="You've hit your session limit · resets 4:30pm (America/Chicago)")))
    sys.exit(1)
assert '--resume' in sys.argv and sys.argv[-1]=='known-session'
assert p.read_text()=='completed work'
assert 'Continue the assigned work' in sys.stdin.read()
assert not pathlib.Path('build/continue-analysis/results/AM-001.json').exists()
print(json.dumps(dict(is_error=False,result='CA-STATUS: done')))
''')
            # Simulate arriving at the reset without a real multi-hour sleep.
            with patch.object(session, 'reset_time', side_effect=[0, None]):
                self.assertEqual(session.run(cp), 0)
            self.assertFalse(cp.exists())
            self.assertTrue((state / 'logs/AM-001.test.attempt-1.result.json').exists())
            self.assertIn('session limit', (state / 'logs/AM-001.test.attempt-1.raw').read_text())
            self.assertIn('done', (state / 'logs/AM-001.test.json').read_text())

    def test_recover_saved_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            state, cp = self.fixture(Path(directory), "import sys,json; assert '--resume' in sys.argv; print(json.dumps({'result':'ok'}))")
            data = json.loads(cp.read_text())
            data.update(started=True, resume_at=1, attempt=3)
            session.atomic_json(cp, data)
            self.assertEqual(session.run(cp), 0)
            self.assertTrue((state / 'logs/AM-001.test.attempt-4.raw').exists())

    def test_timeout_ends_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            state, cp = self.fixture(Path(directory), "import time; time.sleep(30)")
            data = json.loads(cp.read_text())
            data['timeout'] = 0.001
            session.atomic_json(cp, data)
            self.assertEqual(session.run(cp), 124)
            self.assertFalse(cp.exists())

    def test_nonlimit_failure_is_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            state, cp = self.fixture(Path(directory), "import sys,json; print(json.dumps({'is_error':True,'result':'Authentication failed'})); sys.exit(1)")
            self.assertEqual(session.run(cp), 1)
            self.assertFalse((state / 'logs/AM-001.test.attempt-2.raw').exists())

    def test_stderr_only_startup_failure_remains_actionable(self):
        with tempfile.TemporaryDirectory() as directory:
            state, cp = self.fixture(Path(directory),
                "import sys; print('Operation not permitted: session database', file=sys.stderr); sys.exit(1)")
            self.assertEqual(session.run(cp), 1)
            result = json.loads((state / 'logs/AM-001.test.json').read_text())
            self.assertIn('Operation not permitted: session database', result['result'])
            self.assertTrue(result['is_error'])
            self.assertFalse((state / 'logs/AM-001.test.attempt-2.raw').exists())

    def test_successful_limit_discussion_is_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            state, cp = self.fixture(
                Path(directory),
                "import json; print(json.dumps({'is_error':False,'result':'usage limit handling is done'}))")
            self.assertEqual(session.run(cp), 0)
            self.assertFalse((state / 'logs/AM-001.test.attempt-2.raw').exists())

    def test_provider_commands_use_native_yolo_and_resume_flags(self):
        prompt = Path(__file__)
        base = dict(sid='the-session', model_explicit=False, effort='', max_budget_usd='')
        cases = {
            'claude-yolo': dict(executable='claude-yolo', model='claude-sonnet-5'),
            'codex-yolo': dict(executable='codex-yolo', model='gpt-5.6-luna'),
            'muse': dict(executable='muse', model='muse-spark-1.3-contributor'),
            'agy': dict(executable='agy', model=''),
            'grok': dict(executable='grok', model=''),
        }
        commands = {}
        for provider, values in cases.items():
            data = dict(base, provider=provider, **values)
            commands[(provider, False)] = session.build_command(data, False, prompt)[0]
            commands[(provider, True)] = session.build_command(data, True, prompt)[0]
        self.assertIn('gpt-5.6-luna', commands[('codex-yolo', False)])
        self.assertEqual(commands[('codex-yolo', True)][2], 'resume')
        self.assertIn('muse-spark-1.3-contributor', commands[('muse', False)])
        self.assertIn('--yolo', commands[('muse', False)])
        self.assertIn('--conversation', commands[('agy', True)])
        self.assertNotIn('--model', commands[('agy', False)])
        self.assertIn('--resume', commands[('grok', True)])
        self.assertNotIn('--model', commands[('grok', False)])
        self.assertIn('bypassPermissions', commands[('claude-yolo', False)])
        self.assertIn('bypassPermissions', commands[('grok', False)])

    def test_codex_spark_model_uses_codex_command_path(self):
        prompt = Path(__file__)
        data = dict(provider='codex-yolo', executable='codex-yolo', sid='',
                    model='gpt-5.3-codex-spark', model_explicit=False,
                    effort='', max_budget_usd='')
        command, _ = session.build_command(data, False, prompt)
        self.assertEqual(command[:2], ['codex-yolo', 'exec'])
        self.assertEqual(command[command.index('--model') + 1], 'gpt-5.3-codex-spark')

    def test_provider_output_normalization(self):
        codex = '\n'.join([
            json.dumps({'type': 'thread.started', 'thread_id': 'codex-session'}),
            json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'done'}}),
        ])
        self.assertEqual(session.parse_output('codex-yolo', codex, 0)['session_id'], 'codex-session')
        self.assertEqual(session.parse_output('codex-yolo', codex, 0)['result'], 'done')
        agy = json.dumps({'conversation_id': 'agy-session', 'status': 'SUCCESS', 'response': 'done'})
        self.assertEqual(session.parse_output('agy', agy, 0)['session_id'], 'agy-session')
        muse = json.dumps({'stream': {'kind': 'session', 'id': 'muse-session'},
                           'payload': {'kind': 'run_terminal', 'terminal': 'completed', 'text': 'done'}})
        self.assertEqual(session.parse_output('muse', muse, 0)['result'], 'done')

    def test_codex_limit_resumes_discovered_thread_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / 'build/continue-analysis'
            for name in ('logs', 'results', 'paused', 'running'):
                (state / name).mkdir(parents=True)
            prompt = root / 'prompt.md'
            prompt.write_text('Original assignment')
            mock = root / 'mock-codex'
            mock.write_text('''#!/usr/bin/env python3
import json, pathlib, sys
calls = pathlib.Path('calls')
previous = calls.read_text() if calls.exists() else ''
calls.write_text(previous + json.dumps(sys.argv[1:]) + '\\n')
if 'resume' not in sys.argv:
    print(json.dumps({'type':'thread.started','thread_id':'codex-thread'}))
    print(json.dumps({'type':'item.completed','item':{'type':'error','message':'usage limit reached'}}))
    sys.exit(1)
assert 'codex-thread' in sys.argv
print(json.dumps({'type':'thread.started','thread_id':'codex-thread'}))
print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'CA-STATUS: done'}}))
''')
            mock.chmod(0o755)
            checkpoint = state / 'paused/AM-001.test.json'
            session.atomic_json(checkpoint, dict(
                root=str(root), id='AM-001', stamp='test', sid='', prompt=str(prompt),
                timeout=0, provider='codex-yolo', executable=str(mock),
                model='gpt-5.6-luna', model_explicit=False, effort='', max_budget_usd=''))
            with patch.object(session, 'reset_time', side_effect=[0, None]):
                self.assertEqual(session.run(checkpoint), 0)
            calls = (root / 'calls').read_text().splitlines()
            self.assertEqual(len(calls), 2)
            self.assertIn('resume', json.loads(calls[1]))
            self.assertIn('codex-thread', json.loads(calls[1]))
            self.assertIn('CA-STATUS: done', (state / 'logs/AM-001.test.json').read_text())


if __name__ == '__main__':
    unittest.main()
