#!/usr/bin/env python3
"""Reproduce the retained-path first-party closure frontier for G2 2.2.6.10.

This is a path-anchored lower-bound census, not whole-image byte coverage.
It authenticates the official image and 64-shard Ghidra corpus through the
embedded-source-path analyzer, then reconciles every first-party retained path
against the pinned per-object closure manifests.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH_ANALYZER = ROOT / "tools" / "analyze_apollo_embedded_source_paths.py"
MANIFEST_DIR = ROOT / "tools" / "manifests"
DEFAULT_CORPUS = ROOT / "research/corpus/apollo-main/ghidra/full64-j64-auth"

EXPECTED_CLOSED_LEDGER_SHA256 = (
    "1cf3f8eee73ca5a98b8659a4eafb4414c5eddf68f5895554082d68bb6a99592a"
)
EXPECTED_SURFACE = {
    "retained_first_party_paths": 234,
    "closed_paths": 234,
    "open_paths": 0,
    "paths_with_function_anchors": 200,
    "paths_without_function_anchors": 34,
    "anchored_functions": 1230,
    "closed_anchored_functions": 1230,
    "open_anchored_functions": 0,
    "cross_status_anchored_functions": 0,
    "anchored_body_bytes": 485274,
    "closed_anchored_body_bytes": 485274,
    "open_anchored_body_bytes": 0,
    "closed_manifest_body_bytes": 814846,
    "closed_manifest_physical_bytes_known": 885418,
    "closed_manifests_with_physical_bytes": 232,
    "closed_manifests_without_physical_bytes": 2,
}
EXPECTED_TOP_OPEN = [
]


class AuditError(RuntimeError):
    """Raised when authenticated evidence or the closed frontier changes."""


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_path_analyzer() -> Any:
    spec = importlib.util.spec_from_file_location("first_party_path_census", PATH_ANALYZER)
    if spec is None or spec.loader is None:
        raise AuditError("could not load embedded-source-path analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _read_closure_records(path: Path) -> list[tuple[str, dict[str, str]]]:
    lines = [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not lines:
        return []
    if lines[0] == ["metric", "value"]:
        metrics = {row[0]: row[1] for row in lines[1:] if len(row) == 2}
        retained = metrics.get("retained_path")
        return [("", metrics)] if retained else []
    if lines[0] == ["module", "metric", "value"]:
        grouped: dict[str, dict[str, str]] = {}
        for row in lines[1:]:
            if len(row) == 3:
                grouped.setdefault(row[0], {})[row[1]] = row[2]
        return [
            (module, metrics) for module, metrics in sorted(grouped.items())
            if "retained_path" in metrics
        ]
    return []


def _normalise_path(value: str, prefix: str) -> str:
    value = value.replace("/", "\\")
    return value[len(prefix):] if value.startswith(prefix) else value


def analyze(corpus_root: Path = DEFAULT_CORPUS) -> dict[str, Any]:
    path_module = _load_path_analyzer()
    base = path_module.analyze(corpus_root=corpus_root)
    correlation = base["ghidra_correlation"]
    prefix = path_module.WORKSPACE_PREFIX.decode("ascii")

    first_party = {
        record["relative"]: record
        for record in base["paths"]
        if record["root"] != "third_party"
    }
    functions = {record["entry"]: record for record in correlation["functions"]}

    closed: dict[str, dict[str, Any]] = {}
    for manifest in sorted(MANIFEST_DIR.glob("*-closure.tsv")):
        digest = _sha256(manifest.read_bytes())
        for record_id, raw_metrics in _read_closure_records(manifest):
            retained = raw_metrics["retained_path"]
            if retained in {"none", "closure_manifest"}:
                continue
            retained = _normalise_path(retained, prefix)
            if retained not in first_party:
                continue
            if retained in closed:
                raise AuditError(f"duplicate closure manifests for {retained}")
            body_bytes = raw_metrics.get("retained_body_bytes", raw_metrics.get("body_bytes"))
            if body_bytes is None:
                raise AuditError(f"closure manifest lacks body_bytes: {manifest.name}:{record_id}")
            metrics = dict(raw_metrics)
            metrics["body_bytes"] = body_bytes
            if "retained_physical_bytes" in metrics:
                metrics["physical_bytes"] = metrics["retained_physical_bytes"]
            closed[retained] = {
                "manifest": manifest.name,
                "record_id": record_id,
                "manifest_sha256": digest,
                "metrics": metrics,
            }

    ledger_text = "".join(
        f"{path}\t{item['manifest']}\t{item['record_id']}\t{item['manifest_sha256']}\n"
        for path, item in sorted(closed.items())
    )
    ledger_digest = _sha256(ledger_text.encode("utf-8"))
    if ledger_digest != EXPECTED_CLOSED_LEDGER_SHA256:
        raise AuditError(f"closed-manifest ledger changed: {ledger_digest}")

    inventory: list[dict[str, Any]] = []
    closed_entries: set[int] = set()
    open_entries: set[int] = set()
    for retained, record in sorted(first_party.items()):
        entries = {item["entry"] for item in record["function_references"]}
        body_bytes = sum(
            functions[entry]["body_end_inclusive"]
            - functions[entry]["body_start"]
            + 1
            for entry in entries
        )
        closure = closed.get(retained)
        status = "closed" if closure else "open"
        (closed_entries if closure else open_entries).update(entries)
        inventory.append(
            {
                "retained_path": retained,
                "status": status,
                "closure_manifest": closure["manifest"] if closure else None,
                "closure_manifest_sha256": (
                    closure["manifest_sha256"] if closure else None
                ),
                "anchored_functions": len(entries),
                "anchored_body_bytes": body_bytes,
            }
        )

    overlap = closed_entries & open_entries
    if overlap:
        raise AuditError("a Ghidra function is anchored by both open and closed paths")

    def body_size(entry: int) -> int:
        item = functions[entry]
        return item["body_end_inclusive"] - item["body_start"] + 1

    physical_values = [
        int(item["metrics"]["physical_bytes"])
        for item in closed.values()
        if "physical_bytes" in item["metrics"]
    ]
    surface = {
        "retained_first_party_paths": len(inventory),
        "closed_paths": len(closed),
        "open_paths": len(inventory) - len(closed),
        "paths_with_function_anchors": sum(
            item["anchored_functions"] != 0 for item in inventory
        ),
        "paths_without_function_anchors": sum(
            item["anchored_functions"] == 0 for item in inventory
        ),
        "anchored_functions": len(closed_entries | open_entries),
        "closed_anchored_functions": len(closed_entries),
        "open_anchored_functions": len(open_entries),
        "cross_status_anchored_functions": len(overlap),
        "anchored_body_bytes": sum(map(body_size, closed_entries | open_entries)),
        "closed_anchored_body_bytes": sum(map(body_size, closed_entries)),
        "open_anchored_body_bytes": sum(map(body_size, open_entries)),
        "closed_manifest_body_bytes": sum(
            int(item["metrics"]["body_bytes"]) for item in closed.values()
        ),
        "closed_manifest_physical_bytes_known": sum(physical_values),
        "closed_manifests_with_physical_bytes": len(physical_values),
        "closed_manifests_without_physical_bytes": len(closed) - len(physical_values),
    }
    if surface != EXPECTED_SURFACE:
        raise AuditError(f"first-party frontier changed: {surface!r}")

    top_open = sorted(
        (item for item in inventory if item["status"] == "open"),
        key=lambda item: (
            -item["anchored_body_bytes"],
            -item["anchored_functions"],
            item["retained_path"],
        ),
    )[:20]
    observed_top = [
        (item["retained_path"], item["anchored_functions"], item["anchored_body_bytes"])
        for item in top_open
    ]
    if observed_top != EXPECTED_TOP_OPEN:
        raise AuditError(f"open frontier ranking changed: {observed_top!r}")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; retained-path lower-bound census",
        "image": base["image"],
        "corpus": correlation["corpus"],
        "closed_manifest_ledger": {
            "entries": len(closed),
            "sha256": ledger_digest,
        },
        "surface": surface,
        "coverage_percent": {
            "closed_paths": 100.0 * surface["closed_paths"] / surface["retained_first_party_paths"],
            "closed_anchored_functions": 100.0 * surface["closed_anchored_functions"] / surface["anchored_functions"],
            "closed_anchored_body_bytes": 100.0 * surface["closed_anchored_body_bytes"] / surface["anchored_body_bytes"],
        },
        "top_open_frontier": top_open,
        "inventory": inventory,
        "limitations": [
            "retained paths are lower-bound ownership anchors; pathless translation units and functions can exist",
            "closed means linked-object boundaries and ingress are closed, not that historical source-only inventory is known",
            "anchored bytes are Ghidra body bytes and are distinct from complete physical-object bytes",
            "production ownership is tracked by per-object evidence and is not implied by closure",
        ],
    }


def _text(report: dict[str, Any]) -> str:
    surface = report["surface"]
    lines = [
        "G2 first-party retained-path frontier",
        f"  image: {report['image']['sha256']}",
        f"  paths: {surface['closed_paths']} closed / {surface['open_paths']} open / {surface['retained_first_party_paths']} total",
        f"  anchored functions: {surface['closed_anchored_functions']} closed / {surface['open_anchored_functions']} open",
        f"  anchored body bytes: {surface['closed_anchored_body_bytes']} closed / {surface['open_anchored_body_bytes']} open",
        f"  closed complete-object body bytes: {surface['closed_manifest_body_bytes']}",
        f"  closed manifest ledger: {report['closed_manifest_ledger']['sha256']}",
        "  top open paths:",
    ]
    lines.extend(
        f"    {item['anchored_body_bytes']:6d} B / {item['anchored_functions']:2d} funcs  {item['retained_path']}"
        for item in report["top_open_frontier"]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else _text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
