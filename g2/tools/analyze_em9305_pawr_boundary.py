#!/usr/bin/env python3
"""Qualify a typed fail-closed boundary for the EM9305 PAwR residual."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import analyze_em9305_controller_clusters as clusters


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
RESIDUAL = ROOT / "tools/manifests/em9305-residual-provenance-map.tsv"
CANDIDATE = ROOT / "components/shared/em9305/runtime_controller_pawr_boundary.c"
HEADER = CANDIDATE.with_suffix(".h")
MANIFEST = ROOT / "tools/manifests/em9305-pawr-boundary.tsv"
PINS = {
    IMAGE: (211_948, "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"),
    RESIDUAL: (47_936, "2ac24d2abf1f4a4fbce236a82f4591a38dfdb0a71c5ca5b2f8e88bcd9a722d36"),
    CANDIDATE: (1_766, "59856aa09f5b07c96ffac863ca4531b27493e83df3641804fcc62ac5ed802294"),
    HEADER: (1_558, "9749325de487ea513e6407ad0d47d3c596756ea2296c7df681352e364aa3b39d"),
    MANIFEST: (2_051, "461c5aa0105d8cb772aed6d07326f3aec0bdcc3d7fb4dfc7d3e8b769b94fa1cb"),
}
APP_BASE = 0x00302400
APP_FILE_OFFSET = 0x424
START, END = 0x00321C30, 0x0032233C
SIZE = END - START
SHA = "f1c6059c121b60e25cfcb722c6ee546af9d19acf06ab9b55d55bcde07eaae48d"
NAMES = (
    "lctrMstPerScanRxPerAdvPktPostHandler", "lctrMstPerScanTransferOpCommit",
    "lctrMstPerScanWithRspAbortOp", "lctrMstPerScanWithRspCommitOp",
)


class BoundaryError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_audit() -> dict[str, Any]:
    inputs = {}
    for path, pin in PINS.items():
        data = path.read_bytes()
        if (len(data), digest(data)) != pin:
            raise BoundaryError(f"{path}: identity drift")
        inputs[path] = data
    offset = APP_FILE_OFFSET + START - APP_BASE
    if digest(inputs[IMAGE][offset:offset + SIZE]) != SHA:
        raise BoundaryError("PAwR stock segment identity drift")
    combined = inputs[CANDIDATE].decode("ascii") + inputs[HEADER].decode("ascii")
    if combined.count("SPDX-License-Identifier: MIT") != 2:
        raise BoundaryError("MIT declarations drift")
    if len(re.findall(r"\bopen_cfw_em9305_pawr_boundary\s*\(", combined)) != 2:
        raise BoundaryError("PAwR boundary symbol drift")
    for marker in NAMES + ("OPEN_CFW_EM9305_PAWR_UNSUPPORTED",
                           "OPEN_CFW_EM9305_PAWR_PROVIDER_FAILED"):
        if marker not in combined:
            raise BoundaryError(f"PAwR candidate marker drift: {marker}")
    parent = clusters.analyze()
    cluster_items = [item for item in parent["clusters"] if item["name"] == "master_periodic_scan_pawr"]
    if len(cluster_items) != 1:
        raise BoundaryError("parent PAwR cluster count drift")
    cluster = cluster_items[0]
    if (cluster["start"], cluster["end"], cluster["size"], cluster["segment_sha256"],
        cluster["interior_nop_addresses"]) != (START, END, SIZE, SHA, [0x00322182]):
        raise BoundaryError("parent PAwR cluster identity drift")
    functions = [item for item in parent["functions"] if item["cluster"] == "master_periodic_scan_pawr"]
    if tuple(item["name"] for item in functions) != NAMES or sum(item["size"] for item in functions) + 2 != SIZE:
        raise BoundaryError("parent PAwR function tiling drift")
    rows = list(csv.DictReader(inputs[RESIDUAL].decode("ascii").splitlines(), delimiter="\t"))
    matches = [row for row in rows if int(row["start"], 16) == START]
    if len(matches) != 1 or (
        int(matches[0]["end"], 16), int(matches[0]["size"]), matches[0]["sha256"],
        matches[0]["ownership_category"],
    ) != (END, SIZE, SHA, "proprietary_modern_controller_source_unavailable"):
        raise BoundaryError("residual PAwR row identity drift")
    manifest = list(csv.DictReader(inputs[MANIFEST].decode("ascii").splitlines(), delimiter="\t"))
    if len(manifest) != 8 or manifest[0]["disposition"] != "typed_unsupported_external_boundary":
        raise BoundaryError("PAwR manifest decision drift")
    if manifest[-1]["name"] != "blocked by unavailable physical evidence":
        raise BoundaryError("hardware qualification policy drift")
    return {
        "status": "candidate-qualified-fail-closed", "read_only": True,
        "hardware_operations": False, "license": "MIT",
        "decision": {"start": START, "end_exclusive": END, "bytes": SIZE,
                     "sha256": SHA, "readiness": "typed_unsupported_external_boundary",
                     "decision": "four_entry_pawr_provider_boundary"},
        "function_count": 4, "functions": functions,
        "exact_source_available": False,
        "redistribution_authority_resolved": False,
        "candidate": {"source": str(CANDIDATE.relative_to(ROOT)),
                      "header": str(HEADER.relative_to(ROOT)),
                      "production_routed": False},
        "hardware_validation": "blocked by unavailable physical evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_audit()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EM9305 PAwR: candidate-qualified-fail-closed")
        print("typed boundary: 1 span / 1804 bytes / 4 entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
