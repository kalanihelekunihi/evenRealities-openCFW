#!/usr/bin/env python3
"""Run one persisted Claude session, checkpointing and waiting on usage limits."""
import datetime as dt
import json
import fcntl
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from zoneinfo import ZoneInfo


def reset_time(message, now=None):
    """None means ordinary failure; unknown reset formats use a 15 minute retry."""
    if not re.search(r"(?:hit|reached|exceeded).*?(?:session|usage|rate) limit|rate_limit_error", message, re.I):
        return None
    now = now or dt.datetime.now(dt.timezone.utc)
    match = re.search(r"resets?\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\s*\(([^)]+)\)", message, re.I)
    if match:
        try:
            hour, minute, period, zone = match.groups()
            local = now.astimezone(ZoneInfo(zone))
            target = local.replace(hour=int(hour) % 12 + (12 if period.lower() == 'pm' else 0),
                                   minute=int(minute or 0), second=0, microsecond=0)
            if target <= local:
                target += dt.timedelta(days=1)
            return target.timestamp() + 60
        except (ValueError, KeyError):
            pass
    return now.timestamp() + 900


def atomic_json(path, data):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(path)


def run(checkpoint):
    # Kernel lock prevents duplicate supervisors, and releases automatically on exit.
    with checkpoint.with_suffix('.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('This session already has a supervisor')
        return run_locked(checkpoint)


def run_locked(checkpoint):
    data = json.loads(checkpoint.read_text())
    root = Path(data['root'])
    state = root / 'build/continue-analysis'
    base = state / 'logs' / (data['id'] + '.' + data['stamp'])
    child = None

    def stop(signum, frame):
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while True:
        delay = data.get('resume_at', 0) - time.time()
        if delay > 0:
            print('[continue-analysis] %s paused; resuming session %s at %s' % (
                data['id'], data['sid'], dt.datetime.fromtimestamp(data['resume_at']).astimezone().isoformat()), flush=True)
            while time.time() < data['resume_at']:
                time.sleep(min(30, max(0, data['resume_at'] - time.time())))
        attempt = data.get('attempt', 0) + 1
        data['attempt'] = attempt
        # Persist resume intent before launching, including if the supervisor is interrupted.
        resumed = data.get('started', False)
        data['started'] = True
        atomic_json(checkpoint, data)
        cmd = data['cmd'] + [('--resume' if resumed else '--session-id'), data['sid']]
        prompt = ("Continue the assigned work from the preserved session after the usage limit. "
                  "Inspect existing files and any running background commands before continuing. "
                  "Preserve completed work. Re-check integration lock ownership before shared edits. "
                  "Write an updated result file when finished.\n") if resumed else Path(data['prompt']).read_text()
        out = Path(str(base) + '.attempt-%d.json' % attempt)
        err = Path(str(base) + '.attempt-%d.stderr' % attempt)
        with out.open('w') as stdout, err.open('w') as stderr:
            child = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                     cwd=root, text=True, start_new_session=True)
            try:
                child.communicate(prompt, timeout=data['timeout'] * 60 or None)
                rc = child.returncode
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                rc = 124
        output = out.read_text()
        Path(str(base) + '.json').write_text(output)
        Path(str(base) + '.stderr').write_text(err.read_text())
        try:
            result = json.loads(output)
            message = str(result.get('result', '')) if result.get('is_error') else ''
        except (ValueError, AttributeError):
            message = output
        resume_at = reset_time(message + '\n' + err.read_text()) if rc != 124 else None
        if resume_at is None:
            checkpoint.unlink()
            return rc
        data['resume_at'] = resume_at
        data['last_error'] = message
        # Claude persists its transcript; edits already live on disk. Keep partial reports too.
        partial = state / 'results' / (data['id'] + '.json')
        if partial.exists():
            Path(str(base) + '.attempt-%d.result.json' % attempt).write_bytes(partial.read_bytes())
            partial.unlink()  # don't ingest a stale report if the resumed attempt fails
        atomic_json(checkpoint, data)


if __name__ == '__main__':
    sys.exit(run(Path(sys.argv[1])))
