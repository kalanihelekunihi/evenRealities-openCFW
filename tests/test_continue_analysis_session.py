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
    def test_reset_timezone_and_rollover(self):
        now = dt.datetime(2026, 9, 11, 18, tzinfo=dt.timezone.utc)
        msg = "You've hit your session limit · resets 4:30pm (America/Chicago)"
        self.assertEqual(session.reset_time(msg, now), dt.datetime(2026, 9, 11, 21, 31, tzinfo=dt.timezone.utc).timestamp())
        self.assertEqual(session.reset_time(msg, now + dt.timedelta(hours=5)), dt.datetime(2026, 9, 12, 21, 31, tzinfo=dt.timezone.utc).timestamp())
        self.assertEqual(session.reset_time('usage limit reached', now), None)
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
            self.assertIn('session limit', (state / 'logs/AM-001.test.attempt-1.json').read_text())
            self.assertIn('done', (state / 'logs/AM-001.test.json').read_text())

    def test_recover_saved_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            state, cp = self.fixture(Path(directory), "import sys,json; assert '--resume' in sys.argv; print(json.dumps({'result':'ok'}))")
            data = json.loads(cp.read_text())
            data.update(started=True, resume_at=1, attempt=3)
            session.atomic_json(cp, data)
            self.assertEqual(session.run(cp), 0)
            self.assertTrue((state / 'logs/AM-001.test.attempt-4.json').exists())

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
            self.assertFalse((state / 'logs/AM-001.test.attempt-2.json').exists())


if __name__ == '__main__':
    unittest.main()
