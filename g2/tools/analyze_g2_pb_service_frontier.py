#!/usr/bin/env python3
"""Rank retained G2 pb_service translation units from authenticated anchors."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = Path("/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth")
FRONTIER = ROOT / "tools/manifests/g2-pb-service-frontier.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-frontier-provenance.tsv"
PINS = {
    FRONTIER: "d8bf149c8341032b173b1b1f12784ec7de6fe15121ac23e88a14969c51aba3a9",
    PROVENANCE: "2198083a1c34395928c03b0429ceedccb498f509b4f6a883ac017087dd5bbd23",
}
BEGIN_RE = re.compile(
    r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+) body_start=([0-9a-f]+) body_end=([0-9a-f]+)",
    re.IGNORECASE,
)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def analyze(corpus: Path = CORPUS) -> dict:
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import analyze_apollo_embedded_source_paths as paths

    report = paths.analyze(corpus_root=corpus)
    ends: dict[int, tuple[int, int]] = {}
    for log in sorted((corpus / "logs").glob("apollo-*.log")):
        for line in log.read_text(encoding="utf-8").splitlines():
            match = BEGIN_RE.search(line)
            if match:
                entry, start, end = (int(value, 16) for value in match.groups())
                ends[entry] = (start, end + 1)

    derived = []
    for record in report["paths"]:
        if "pb_service_" not in record["relative"]:
            continue
        entries = [item["entry"] for item in record["function_references"]]
        spans = [ends[entry] for entry in entries]
        derived.append({
            "retained_path": record["relative"],
            "anchored_functions": len(entries),
            "min_body_start": min(start for start, _ in spans),
            "max_body_end_exclusive": max(end for _, end in spans),
            "anchored_body_bytes": sum(end - start for start, end in spans),
            "path_string": record["run"],
            "pointer_cells": len(record["pointer_cells"]),
        })
    derived.sort(key=lambda item: (item["anchored_body_bytes"], item["retained_path"]))

    with FRONTIER.open(newline="") as handle:
        expected_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(derived) != 15 or len(expected_rows) != 15:
        raise AuditError("pb_service path census changed")
    for rank, (actual, expected) in enumerate(zip(derived, expected_rows), 1):
        checks = {
            "rank": rank,
            "retained_path": actual["retained_path"],
            "anchored_functions": actual["anchored_functions"],
            "min_body_start": actual["min_body_start"],
            "max_body_end_exclusive": actual["max_body_end_exclusive"],
            "anchored_body_bytes": actual["anchored_body_bytes"],
            "path_string": actual["path_string"],
            "pointer_cells": actual["pointer_cells"],
        }
        parsed = {
            "rank": int(expected["rank"]),
            "retained_path": expected["retained_path"],
            "anchored_functions": int(expected["anchored_functions"]),
            "min_body_start": int(expected["min_body_start"], 0),
            "max_body_end_exclusive": int(expected["max_body_end_exclusive"], 0),
            "anchored_body_bytes": int(expected["anchored_body_bytes"]),
            "path_string": int(expected["path_string"], 0),
            "pointer_cells": int(expected["pointer_cells"]),
        }
        if checks != parsed:
            raise AuditError(f"frontier row changed at rank {rank}")

    return {
        "surface": {
            "retained_pb_service_paths": 15,
            "anchored_functions": sum(item["anchored_functions"] for item in derived),
            "anchored_body_bytes": sum(item["anchored_body_bytes"] for item in derived),
            "corpus_functions": report["ghidra_correlation"]["corpus"]["functions"],
            "decompile_failures": report["ghidra_correlation"]["corpus"]["decompile_failures"],
        },
        "selected": {
            "path": derived[0]["retained_path"],
            "anchored_functions": derived[0]["anchored_functions"],
            "anchored_body_bytes": derived[0]["anchored_body_bytes"],
            "interval_lower_bound": "[0x0059f53c,0x0059fa68)",
        },
        "next": [item["retained_path"] for item in derived[:3]],
        "qualification": "retained-path anchors are lower bounds, not whole-TU inventories",
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service frontier audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
