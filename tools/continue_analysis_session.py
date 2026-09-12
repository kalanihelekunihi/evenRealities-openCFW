#!/usr/bin/env python3
"""Supervise one persisted coding-agent session across provider usage limits."""
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

RESUME_PROMPT = (
    "Continue the assigned work from the preserved session after the usage limit. "
    "Inspect existing files and any running background commands before continuing. "
    "Preserve completed work. Re-check integration lock ownership before shared edits. "
    "Write an updated result file when finished.\n"
)


def resume_prompt(data):
    """Restore durable knowledge and apply the current workflow to old sessions too."""
    root = Path(data["root"])
    knowledge = root / "build/continue-analysis/knowledge" / (data["id"] + ".json")
    policy = root / "docs/g2-reconstruction-driver-prompt.md"
    text = RESUME_PROMPT + (
        "\nEXECUTION MODE: continue the assigned reconstruction/tooling item; do not start a process review.\n"
        "Read the durable knowledge checkpoint if present: %s\n"
        "Validate scope and relevant working-tree input hashes before reusing receipts. Save updated knowledge atomically after meaningful progress.\n"
        "If the only remaining blockers are unchanged, record blocked with explicit prerequisites and wake conditions instead of rerunning identical gates.\n"
        "Retain the original assignment's hard rules, result schema, and admission gates.\n" % knowledge)
    if policy.is_file():
        text += "\nCURRENT WORKFLOW:\n" + policy.read_text().split("\n---\n", 1)[-1].strip() + "\n"
    return text


def reset_time(message, now=None):
    """Return the next retry epoch, or None when this is not a usage-limit error."""
    limit = re.search(
        r"(?:session|usage|rate|token|credit|quota).{0,32}(?:limit|exhaust|exceed|reset)"
        r"|(?:hit|reached|exceeded).{0,32}(?:limit|quota)|rate_limit_error|resource_exhausted",
        message, re.I | re.S)
    if not limit:
        return None
    now = now or dt.datetime.now(dt.timezone.utc)
    match = re.search(
        r"resets?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)"
        r"(?:\s*\(([^)]+)\))?", message, re.I)
    if match:
        try:
            hour, minute, period, zone = match.groups()
            local = now.astimezone(ZoneInfo(zone)) if zone else now.astimezone()
            target = local.replace(
                hour=int(hour) % 12 + (12 if period.lower() == "pm" else 0),
                minute=int(minute or 0), second=0, microsecond=0)
            if target <= local:
                target += dt.timedelta(days=1)
            return target.timestamp() + 60
        except (ValueError, KeyError):
            pass
    match = re.search(r"(?:retry|resets?).{0,20}(\d+)\s*(seconds?|minutes?|hours?)", message, re.I)
    if match:
        count = int(match.group(1))
        unit = match.group(2).lower()
        seconds = count * (3600 if unit.startswith("hour") else 60 if unit.startswith("minute") else 1)
        return now.timestamp() + seconds + 60
    return now.timestamp() + 900


def atomic_json(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.replace(path)


def build_command(data, resumed, prompt_path):
    """Build a provider-native headless command and its stdin payload."""
    provider = data.get("provider", "legacy-claude")
    executable = data.get("executable")
    model = data.get("model", "")
    effort = data.get("effort", "")
    sid = data.get("sid", "")
    if "cmd" in data:  # Recover checkpoints made by the Claude-only version.
        command = list(data["cmd"])
        command += [("--resume" if resumed else "--session-id"), sid]
        return command, prompt_path.read_text()
    if provider == "claude-yolo":
        command = [executable, "-p", "--model", model,
                   "--allow-dangerously-skip-permissions", "--permission-mode",
                   "bypassPermissions", "--output-format", "json"]
        command += [("--resume" if resumed else "--session-id"), sid]
        if effort:
            command += ["--effort", effort]
        if data.get("max_budget_usd"):
            command += ["--max-budget-usd", data["max_budget_usd"]]
        return command, prompt_path.read_text()
    if provider == "codex-yolo":
        command = [executable, "exec"]
        if resumed and sid:
            command += ["resume"]
        if model:
            command += ["--model", model]
        if effort:
            command += ["--config", "model_reasoning_effort=%s" % effort]
        command += ["--json"]
        if resumed and sid:
            command += [sid]
        command += ["-"]
        return command, prompt_path.read_text()
    if provider == "muse":
        command = [executable, "exec", "--yolo", "--model", model,
                   "--session-id", sid, "--json", "--prompt-file", str(prompt_path)]
        if effort:
            command += ["--reasoning-effort", effort]
        return command, None
    if provider == "agy":
        command = [executable, "--output-format", "json", "--dangerously-skip-permissions"]
        if resumed and sid:
            command += ["--conversation", sid]
        if data.get("model_explicit") and model:
            command += ["--model", model]
        if effort:
            command += ["--effort", effort]
        command += ["--print=" + prompt_path.read_text()]
        return command, None
    if provider == "grok":
        command = [executable, "--output-format", "json",
                   "--permission-mode", "bypassPermissions", "--no-plan"]
        if resumed and sid:
            command += ["--resume", sid]
        else:
            command += ["--session-id", sid]
        if data.get("model_explicit") and model:
            command += ["--model", model]
        if effort:
            command += ["--reasoning-effort", effort]
        command += ["--prompt-file", str(prompt_path)]
        return command, None
    raise ValueError("unsupported provider %r" % provider)


def json_records(raw):
    try:
        value = json.loads(raw)
        return value if isinstance(value, list) else [value]
    except (ValueError, TypeError):
        records = []
        for line in raw.splitlines():
            try:
                records.append(json.loads(line))
            except ValueError:
                continue
        return records


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def parse_output(provider, raw, rc):
    """Normalize provider output for the existing result ingester."""
    records = json_records(raw)
    sid, texts, provider_error = "", [], False
    for record in records:
        if not isinstance(record, dict):
            continue
        provider_error |= str(record.get("type", "")).lower() in ("error", "failed", "failure")
        if isinstance(record.get("conversation_id"), str):
            sid = record["conversation_id"]
        if isinstance(record.get("thread_id"), str):
            sid = record["thread_id"]
        stream = record.get("stream")
        if isinstance(stream, dict) and stream.get("kind") == "session" and isinstance(stream.get("id"), str):
            sid = stream["id"]
        for key in ("session_id", "sessionId"):
            if isinstance(record.get(key), str):
                sid = record[key]
        for value in walk(record):
            if isinstance(value, dict):
                for key in ("session_id", "sessionId", "conversation_id", "thread_id"):
                    if isinstance(value.get(key), str):
                        sid = value[key]
        if provider in ("claude-yolo", "legacy-claude") and isinstance(record.get("result"), str):
            texts.append(record["result"])
            provider_error |= bool(record.get("is_error"))
        if provider == "agy" and isinstance(record.get("response"), str):
            texts.append(record["response"])
            provider_error |= str(record.get("status", "SUCCESS")).upper() != "SUCCESS"
        item = record.get("item")
        if provider == "codex-yolo" and isinstance(item, dict) and item.get("type") == "agent_message":
            if isinstance(item.get("text"), str):
                texts.append(item["text"])
        payload = record.get("payload")
        if provider == "muse" and isinstance(payload, dict) and payload.get("kind") == "run_terminal":
            if isinstance(payload.get("text"), str):
                texts.append(payload["text"])
            provider_error |= payload.get("terminal") == "failed"
    if not texts:
        for record in records:
            for value in walk(record):
                if isinstance(value, dict):
                    for key in ("result", "response", "final", "output", "text", "message"):
                        text = value.get(key)
                        if isinstance(text, str) and text.strip():
                            texts.append(text)
        if not texts and raw.strip():
            texts.append(raw.strip())
    result = texts[-1] if texts else "agent exited %d without a final response" % rc
    return {"provider": provider, "session_id": sid,
            "is_error": bool(rc or provider_error), "result": result}


def run(checkpoint):
    with checkpoint.with_suffix(".lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("This session already has a supervisor")
        return run_locked(checkpoint)


def run_locked(checkpoint):
    data = json.loads(checkpoint.read_text())
    root = Path(data["root"])
    state = root / "build/continue-analysis"
    base = state / "logs" / (data["id"] + "." + data["stamp"])
    child = None

    def stop(signum, frame):
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while True:
        if data.get("resume_at", 0) > time.time():
            print("[continue-analysis] %s paused; resuming %s session %s at %s" % (
                data["id"], data.get("provider", "Claude"), data.get("sid") or "(pending)",
                dt.datetime.fromtimestamp(data["resume_at"]).astimezone().isoformat()), flush=True)
            while time.time() < data["resume_at"]:
                time.sleep(min(30, max(0, data["resume_at"] - time.time())))
        attempt = data.get("attempt", 0) + 1
        data["attempt"] = attempt
        resumed = data.get("started", False)
        data["started"] = True
        atomic_json(checkpoint, data)
        attempt_prompt = Path(str(base) + ".attempt-%d.prompt.md" % attempt)
        attempt_prompt.write_text(resume_prompt(data) if resumed else Path(data["prompt"]).read_text())
        command, stdin_text = build_command(data, resumed, attempt_prompt)
        out = Path(str(base) + ".attempt-%d.raw" % attempt)
        err = Path(str(base) + ".attempt-%d.stderr" % attempt)
        with out.open("w") as stdout, err.open("w") as stderr:
            child = subprocess.Popen(
                command, stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, cwd=root, text=True, start_new_session=True)
            try:
                child.communicate(stdin_text, timeout=data["timeout"] * 60 or None)
                rc = child.returncode
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                rc = 124
        raw, stderr_text = out.read_text(), err.read_text()
        normalized = parse_output(data.get("provider", "legacy-claude"), raw, rc)
        if rc and normalized["result"] == "agent exited %d without a final response" % rc and stderr_text.strip():
            # Startup failures often have no provider JSON at all. Preserve the
            # actionable stderr tail for dependency/failure classification.
            normalized["result"] = stderr_text.strip()[-4000:]
        if normalized["session_id"]:
            data["sid"] = normalized["session_id"]
            session_file = state / "running" / (data["id"] + "." + data["stamp"] + ".session")
            session_file.write_text(data["sid"] + "\n")
        Path(str(base) + ".json").write_text(json.dumps(normalized, indent=2) + "\n")
        Path(str(base) + ".stderr").write_text(stderr_text)
        resume_at = (reset_time(raw + "\n" + stderr_text)
                     if rc != 124 and normalized["is_error"] else None)
        if resume_at is None:
            checkpoint.unlink()
            return rc
        data["resume_at"] = resume_at
        data["last_error"] = normalized["result"]
        partial = state / "results" / (data["id"] + ".json")
        if partial.exists():
            Path(str(base) + ".attempt-%d.result.json" % attempt).write_bytes(partial.read_bytes())
            partial.unlink()
        atomic_json(checkpoint, data)


def describe(checkpoint):
    data = json.loads(checkpoint.read_text())
    prompt = Path(data["prompt"])
    command, stdin_text = build_command(data, False, prompt)
    preview = ["--print=<prompt file contents>" if part.startswith("--print=") else part
               for part in command]
    rendered = " ".join(shlex.quote(part) for part in preview)
    if stdin_text is not None:
        rendered += " < " + shlex.quote(str(prompt))
    print("DRY-RUN %s: (cd %s && %s)" % (data["id"], shlex.quote(data["root"]), rendered))
    print("         prompt: %s (%d bytes), session %s" % (
        prompt, prompt.stat().st_size, data.get("sid") or "assigned by provider"))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--describe":
        describe(Path(sys.argv[2]))
    else:
        raise SystemExit(run(Path(sys.argv[1])))
