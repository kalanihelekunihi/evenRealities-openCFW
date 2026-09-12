#!/usr/bin/env python3
"""Normalize agent blockers into durable, machine-readable deferred work."""
import datetime as dt
import json
from pathlib import Path
import re

ITEM_RE = re.compile(r"\b(?:AM|AD|BL|EM|CD|TC|CS|XC)-\d{3}\b")


def analyze_failure_text(text):
    """Classify an agent failure that did not produce a structured result."""
    compact = " ".join(str(text).split())[:1000]
    low = compact.lower()
    if re.search(r"session|usage|rate", low) and re.search(r"limit|quota|reset", low):
        return {"kind": "usage-limit", "retryable": True, "description": compact}
    if "integration lock" in low or "lock timeout" in low:
        return {"kind": "integration", "retryable": True, "description": compact}
    if "timed out" in low or "timeout" in low:
        return {"kind": "timeout", "retryable": True, "description": compact}
    if "auth" in low or "not authenticated" in low or "credential" in low or "not logged in" in low:
        return {"kind": "authentication", "retryable": False, "description": compact}
    if "permission denied" in low or "operation not permitted" in low:
        return {"kind": "permission", "retryable": False, "description": compact}
    if "not found" in low or "not installed" in low or "missing dependency" in low:
        return {"kind": "tool", "retryable": False, "description": compact}
    return {"kind": "agent-failure", "retryable": False, "description": compact}


def _strings(value):
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value if item]


def infer_dependencies(result, item_id, known_ids):
    """Prefer explicit dependencies, then recover exact work IDs from old prose logs."""
    found = {}
    has_explicit_dependency_fields = any(
        key in result for key in ("dependencies", "waiting_on", "completion_after"))
    explicit = result.get("dependencies") or result.get("waiting_on") or []
    if isinstance(explicit, (str, dict)):
        explicit = [explicit]
    for entry in explicit:
        if isinstance(entry, str):
            dep_id, reason, required_for = entry, "explicit dependency", "completion"
        elif isinstance(entry, dict):
            dep_id = entry.get("id") or entry.get("item_id")
            reason = entry.get("reason") or entry.get("description") or "explicit dependency"
            required_for = entry.get("required_for", "completion")
        else:
            continue
        if dep_id in known_ids and dep_id != item_id:
            found[dep_id] = {"id": dep_id, "reason": str(reason)[:500],
                             "required_for": required_for, "inferred": False}
    completion_after = result.get("completion_after") or []
    if isinstance(completion_after, str):
        completion_after = [completion_after]
    for dep_id in completion_after:
        if dep_id in known_ids and dep_id != item_id:
            found.setdefault(dep_id, {"id": dep_id, "reason": "completion requested after this item",
                                      "required_for": "completion", "inferred": False})
    if not found and not has_explicit_dependency_fields and result.get("infer_dependencies", True):
        for text in _strings(result.get("blockers")) + _strings(result.get("followups")):
            for dep_id in ITEM_RE.findall(text):
                if dep_id in known_ids and dep_id != item_id:
                    found.setdefault(dep_id, {"id": dep_id, "reason": text[:500],
                                              "required_for": "completion", "inferred": True})
    return list(found.values())


def classify_requirements(result):
    explicit = result.get("missing_requirements") or []
    if isinstance(explicit, (str, dict)):
        explicit = [explicit]
    normalized = []
    for entry in explicit:
        if isinstance(entry, str):
            normalized.append({"kind": "issue", "description": entry[:1000]})
        elif isinstance(entry, dict) and (entry.get("description") or entry.get("reason")):
            normalized.append({"kind": entry.get("kind", "issue"),
                               "description": str(entry.get("description") or entry["reason"])[:1000]})
    if normalized:
        return normalized
    for text in _strings(result.get("blockers")):
        low = text.lower()
        if "hardware" in low or "physical" in low:
            kind = "hardware"
        elif "licens" in low or "eula" in low:
            kind = "license"
        elif "toolchain" in low or "not installed" in low or "not found" in low:
            kind = "tool"
        elif "config" in low or "ground truth" in low or "source" in low:
            kind = "source-or-configuration"
        elif "gate" in low or "manifest" in low or "re-pin" in low:
            kind = "integration"
        else:
            kind = "issue"
        normalized.append({"kind": kind, "description": text[:1000]})
    return normalized


def build_record(result, item_id, source_result, known_ids, statuses):
    dependencies = infer_dependencies(result, item_id, known_ids)
    requested_ids = []
    for key in ("dependencies", "waiting_on", "completion_after"):
        entries = result.get(key) or []
        if isinstance(entries, (str, dict)):
            entries = [entries]
        for entry in entries:
            dep_id = ((entry.get("id") or entry.get("item_id"))
                      if isinstance(entry, dict) else entry)
            if isinstance(dep_id, str) and dep_id != item_id:
                requested_ids.append(dep_id)
    unresolved = sorted(set(dep_id for dep_id in requested_ids if dep_id not in known_ids))
    completion_after = result.get("completion_after") or [d["id"] for d in dependencies]
    if isinstance(completion_after, str):
        completion_after = [completion_after]
    remaining = result.get("remaining_segments") or result.get("followups") or []
    if isinstance(remaining, (str, dict)):
        remaining = [remaining]
    missing_requirements = classify_requirements(result)
    missing_requirements.extend(
        {"kind": "dependency", "description": "Unknown work-item dependency: " + dep_id}
        for dep_id in unresolved)
    record = {
        "schema_version": 1,
        "id": item_id,
        "updated_at": dt.datetime.now().astimezone().isoformat(),
        "source_result": str(source_result),
        "reported_status": result.get("status", "partial"),
        "summary": str(result.get("summary", ""))[:1000],
        "bytes_source_owned": result.get("bytes_source_owned", 0),
        "files_changed": result.get("files_changed") or [],
        "tests_run": result.get("tests_run") or [],
        "gates_run": result.get("gates_run") or [],
        "blockers": result.get("blockers") or [],
        "followups": result.get("followups") or [],
        "missing_requirements": missing_requirements,
        "remaining_segments": remaining,
        "dependencies": dependencies,
        "unresolved_dependencies": unresolved,
        "completion_after": [x for x in completion_after if x in known_ids and x != item_id],
        "verification_only": bool(result.get("verification_only", False)),
    }
    return refresh_record(record, statuses)


def refresh_record(record, statuses):
    pending = list(record.get("unresolved_dependencies", []))
    for dependency in record.get("dependencies", []):
        dependency["status"] = statuses.get(dependency["id"], "missing")
        if dependency["status"] != "done":
            pending.append(dependency["id"])
    record["pending_dependencies"] = pending
    record["ready_for_completion"] = bool(record.get("dependencies")) and not pending
    return record


def merge_failure(record, issue, source_result, statuses):
    """Attach an operational failure without discarding previously saved progress."""
    record["updated_at"] = dt.datetime.now().astimezone().isoformat()
    record["last_failure"] = dict(issue, source_result=str(source_result))
    requirements = record.setdefault("missing_requirements", [])
    if not any(entry.get("kind") == issue["kind"] and
               entry.get("description") == issue["description"] for entry in requirements):
        requirements.append({"kind": issue["kind"], "description": issue["description"]})
    return refresh_record(record, statuses)


def load_record(directory, item_id):
    path = Path(directory) / (item_id + ".json")
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def save_record(directory, record):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (record["id"] + ".json")
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(path)
    return path
