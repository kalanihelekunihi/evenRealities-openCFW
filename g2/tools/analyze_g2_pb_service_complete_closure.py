#!/usr/bin/env python3
"""Reconcile all retained G2 protobuf-service linked-object closures."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "tools/manifests"
AGGREGATE = MANIFEST_DIR / "g2-pb-service-complete-closure.tsv"
FRONTIER = MANIFEST_DIR / "g2-pb-service-frontier.tsv"
PINS = {
    AGGREGATE: "33ecf75c8e09a12aad8d3688a532de079b05faf10e1309edca85bde383dfd924",
    FRONTIER: "d8bf149c8341032b173b1b1f12784ec7de6fe15121ac23e88a14969c51aba3a9",
    MANIFEST_DIR / "g2-pb-service-conversate-closure.tsv": "68bef70d987506d41098eae1932a35ec44d56501e4cf32b5be9a66fba0784883",
    MANIFEST_DIR / "g2-pb-service-dev-config-closure.tsv": "edee2867bb8f265a839bb0e5e79544a7b3b879e9251aaf0bbaa3bcd3d86642d0",
    MANIFEST_DIR / "g2-pb-service-dev-setting-closure.tsv": "92bbd1ec7f0b4a8eb8d0107275764c5d4d6986b3102d6155e41174b919ee5fea",
    MANIFEST_DIR / "g2-pb-service-even-ai-closure.tsv": "97fbb99dcca84ea976df2d2e8416990cde562910fe03416919c56d968c080327",
    MANIFEST_DIR / "g2-pb-service-glasses-case-closure.tsv": "b3b911e860d331f3079f7810e1737a74381da4ded0e8b436933fd155faa9fab3",
    MANIFEST_DIR / "g2-pb-service-health-closure.tsv": "a50cc002ef2cc5f95cf1d44b4e1b1ef37435d3c64cfd97d56ad0f0c2ea7d182f",
    MANIFEST_DIR / "g2-pb-service-notification-closure.tsv": "69f114c1ee7bfa8c5e8488499114a05d0a12259fefb3bd00b10802c65e5485eb",
    MANIFEST_DIR / "g2-pb-service-onboarding-closure.tsv": "cbf6a92abf2036a2aed140a641def4fe4e97115cd9484a3ed1ee82af024d2c6b",
    MANIFEST_DIR / "g2-pb-service-pair-mgr-closure.tsv": "23b3d956ee287c56f9cf295d3ce5ce68427dfd63cb9f30f75b6a5d2d68bdf19b",
    MANIFEST_DIR / "g2-pb-service-quicklist-closure.tsv": "c70ab0713c93b8e70fb52d596181c350ae7ac2229d270b87befef6e6346481d8",
    MANIFEST_DIR / "g2-pb-service-ring-closure.tsv": "47b2ff130fb3beb8a5d34032b4f9cb258ce0fccd6a477a04a184b7ab7b18a77f",
    MANIFEST_DIR / "g2-pb-service-setting-closure.tsv": "2ddfa87e0ffd8727d80cd85b280dd853d21ec3ca882e57a7e7cc4e5c0e2cb9b3",
    MANIFEST_DIR / "g2-pb-service-teleprompt-closure.tsv": "1f0b285bd9e488b17e7db011d83da521b269576bf351ac6adb7ecf145686af29",
    MANIFEST_DIR / "g2-pb-service-terminal-closure.tsv": "979f2425fc27ba6308123df5b4b1ca1c3499ef254f6ed88fdc7929b062a4d936",
    MANIFEST_DIR / "g2-pb-service-translate-closure.tsv": "ea3e7bc2509175f4261875113825ecf073617201eab2e53bd3f93618ff73ea01",
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def analyze() -> dict:
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    with AGGREGATE.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    total = rows.pop()
    if len(rows) != 15 or total["retained_path"] != "TOTAL":
        raise AuditError("aggregate inventory changed")

    with FRONTIER.open(newline="") as handle:
        frontier = list(csv.DictReader(handle, delimiter="\t"))
    frontier_paths = {row["retained_path"] for row in frontier}
    if {row["retained_path"] for row in rows} != frontier_paths:
        raise AuditError("closed path set differs from retained frontier")

    for row in rows:
        closure_path = MANIFEST_DIR / row["closure_manifest"]
        with closure_path.open(newline="") as handle:
            closure = dict(csv.reader(handle, delimiter="\t"))
        expected = {
            "linked_functions": int(row["linked_functions"]),
            "body_bytes": int(row["body_bytes"]),
            "physical_bytes": int(row["physical_bytes"]),
            "ownership_bytes": int(row["production_ownership_bytes"]),
        }
        actual = {key: int(closure[key]) for key in expected}
        if actual != expected or row["status"] != "closed":
            raise AuditError(f"closure row changed: {row['retained_path']}")

    sums = {
        "linked_functions": sum(int(row["linked_functions"]) for row in rows),
        "body_bytes": sum(int(row["body_bytes"]) for row in rows),
        "physical_bytes": sum(int(row["physical_bytes"]) for row in rows),
        "production_ownership_bytes": sum(
            int(row["production_ownership_bytes"]) for row in rows),
    }
    declared = {
        key: int(total[key]) for key in sums
    }
    if sums != declared or total["status"] != "all_15_retained_paths_closed":
        raise AuditError("aggregate totals changed")

    anchored_functions = sum(int(row["anchored_functions"]) for row in frontier)
    anchored_body_bytes = sum(int(row["anchored_body_bytes"]) for row in frontier)
    return {
        "surface": {
            "retained_paths": 15,
            **sums,
            "non_body_owned_bytes": sums["physical_bytes"] - sums["body_bytes"],
        },
        "frontier_reconciliation": {
            "anchored_functions": anchored_functions,
            "closed_linked_functions": sums["linked_functions"],
            "restored_functions": sums["linked_functions"] - anchored_functions,
            "anchored_body_bytes": anchored_body_bytes,
            "closed_body_bytes": sums["body_bytes"],
            "restored_body_bytes": sums["body_bytes"] - anchored_body_bytes,
        },
        "qualification": {
            "all_retained_paths_closed": True,
            "historical_source_inventory_complete": False,
            "production_routed_services": sum(
                int(row["production_ownership_bytes"]) > 0 for row in rows),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 pb_service complete closure audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service complete closure audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
