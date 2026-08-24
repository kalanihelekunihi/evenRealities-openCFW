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
    AGGREGATE: "482c4f5a9831a3dd2135b23db9fcf3c5bbc0d1acf5c34c35f9a157196721b555",
    FRONTIER: "d8bf149c8341032b173b1b1f12784ec7de6fe15121ac23e88a14969c51aba3a9",
    MANIFEST_DIR / "g2-pb-service-conversate-closure.tsv": "68bef70d987506d41098eae1932a35ec44d56501e4cf32b5be9a66fba0784883",
    MANIFEST_DIR / "g2-pb-service-dev-config-closure.tsv": "2be10bb975b69388cc4de071586b67fceefa813f56080535b07634aea6fdcd22",
    MANIFEST_DIR / "g2-pb-service-dev-setting-closure.tsv": "3f2ecb318601b373b1cff284fe0811d629e1d29645bd56eb519950de54f868c4",
    MANIFEST_DIR / "g2-pb-service-even-ai-closure.tsv": "bac886291074ba19f912efe430d2fb5e0f753bd8b5e02b1657fb15e3e61af028",
    MANIFEST_DIR / "g2-pb-service-glasses-case-closure.tsv": "b3b911e860d331f3079f7810e1737a74381da4ded0e8b436933fd155faa9fab3",
    MANIFEST_DIR / "g2-pb-service-health-closure.tsv": "1558817e12d8b5b4baa3e2c583db99eaecc5ffcbffaba21af174aeed037766a0",
    MANIFEST_DIR / "g2-pb-service-notification-closure.tsv": "d9a1b20365e43d8d87281635186cee65d665a34dddf422e02828676daa444254",
    MANIFEST_DIR / "g2-pb-service-onboarding-closure.tsv": "93c2b4f62c82c37c0486ccda7702471293fa3eb77163bb8f29c321efdecde914",
    MANIFEST_DIR / "g2-pb-service-pair-mgr-closure.tsv": "a8f368b57dc515464ecb11fdc08dc36ad12b676e965922ed623b8fb19774592e",
    MANIFEST_DIR / "g2-pb-service-quicklist-closure.tsv": "d27459e9d77fd9b7c62445a841c6ecd8463b36968ebf0f121b5dd1e423586bd0",
    MANIFEST_DIR / "g2-pb-service-ring-closure.tsv": "47b2ff130fb3beb8a5d34032b4f9cb258ce0fccd6a477a04a184b7ab7b18a77f",
    MANIFEST_DIR / "g2-pb-service-setting-closure.tsv": "3f53fa20acbeadb61f4a660f5512a80abef3d5c3e3638cd86646c7fa1d42675b",
    MANIFEST_DIR / "g2-pb-service-teleprompt-closure.tsv": "1f0b285bd9e488b17e7db011d83da521b269576bf351ac6adb7ecf145686af29",
    MANIFEST_DIR / "g2-pb-service-terminal-closure.tsv": "efcb8e562d1aed8083d8ebbbfd91d8cfa1cfc58a87d4f642890ad3f154522830",
    MANIFEST_DIR / "g2-pb-service-translate-closure.tsv": "875f75f22cf1aa450b95d16e1c396498774f2fdfb22882a91f2b5dfc30e9620f",
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
