#!/usr/bin/env python3
"""Qualify a typed fail-closed boundary for the largest EM9305 residual."""

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
CLUSTER_MAP = ROOT / "tools/manifests/em9305-controller-cluster-map.tsv"
CANDIDATE = ROOT / "components/shared/em9305/runtime_controller_slave_connection_boundary.c"
HEADER = CANDIDATE.with_suffix(".h")
MANIFEST = ROOT / "tools/manifests/em9305-slave-connection-boundary.tsv"

FILE_PINS = {
    IMAGE: (211_948, "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"),
    RESIDUAL: (47_936, "2ac24d2abf1f4a4fbce236a82f4591a38dfdb0a71c5ca5b2f8e88bcd9a722d36"),
    CLUSTER_MAP: (3_383, "5f9c7aa69a12345da365491f09849277778e88abc4eb632600d23dcaf426209a"),
    CANDIDATE: (2_349, "85d4dbe53cc369469c041c5c7416705ff56671eb5a983d02d5fd5597de9f78b1"),
    HEADER: (1_767, "89b5f777bbfa9dc21dd93c564d104da14d89936e67ce5a7236f43f138c51e618"),
    MANIFEST: (2_980, "dfc9f74b22a993598e7cfa88e9cc793a5796d8c93d5456cf403749e371c8b131"),
}
APP_BASE = 0x00302400
APP_FILE_OFFSET = 0x424
START = 0x00329888
END = 0x0032A4BE
SIZE = END - START
STOCK_SHA256 = "45c3d2477869a9ace185078ca6b5f59621eeca07ae274414e64637e5b04f12aa"
FUNCTION_NAMES = (
    "lctrSlvConnEndOp", "lctrSlvConnExecute", "lctrSlvConnExecuteSm",
    "lctrSlvConnResetHandler", "lctrSlvConnRxCompletion",
    "lctrSlvConnTxCompletion",
)
NOP_ADDRESSES = (0x00329FD6, 0x00329FFE, 0x0032A216, 0x0032A22E)


class BoundaryError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path, expected: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    if (len(data), digest(data)) != expected:
        raise BoundaryError(f"{path}: identity drift")
    return data


def run_audit() -> dict[str, Any]:
    inputs = {path: authenticate(path, pin) for path, pin in FILE_PINS.items()}
    image = inputs[IMAGE]
    offset = APP_FILE_OFFSET + START - APP_BASE
    stock = image[offset:offset + SIZE]
    if len(stock) != SIZE or digest(stock) != STOCK_SHA256:
        raise BoundaryError("slave-connection stock segment identity drift")

    source = inputs[CANDIDATE].decode("ascii")
    header = inputs[HEADER].decode("ascii")
    combined = source + "\n" + header
    if combined.count("SPDX-License-Identifier: MIT") != 2:
        raise BoundaryError("clean-room boundary must retain both MIT declarations")
    if len(re.findall(r"\bopen_cfw_em9305_slv_conn_boundary\s*\(", combined)) != 2:
        raise BoundaryError("typed boundary symbol drift")
    for name in FUNCTION_NAMES:
        if name not in combined:
            raise BoundaryError(f"candidate evidence name drift: {name}")
    for marker in (
        "OPEN_CFW_EM9305_SLV_CONN_UNSUPPORTED",
        "OPEN_CFW_EM9305_SLV_CONN_PROVIDER_FAILED",
        "open_cfw_em9305_slv_conn_invocation",
    ):
        if marker not in combined:
            raise BoundaryError(f"candidate fail-closed marker drift: {marker}")

    parent = clusters.analyze()
    slave_clusters = [item for item in parent["clusters"] if item["name"] == "slave_connection"]
    if len(slave_clusters) != 1:
        raise BoundaryError("parent slave-connection cluster count drift")
    cluster = slave_clusters[0]
    if (
        cluster["start"], cluster["end"], cluster["size"],
        cluster["segment_sha256"], tuple(cluster["interior_nop_addresses"]),
    ) != (START, END, SIZE, STOCK_SHA256, NOP_ADDRESSES):
        raise BoundaryError("parent slave-connection cluster identity drift")
    functions = [item for item in parent["functions"] if item["cluster"] == "slave_connection"]
    if tuple(item["name"] for item in functions) != FUNCTION_NAMES:
        raise BoundaryError("parent slave-connection function order drift")
    if sum(item["size"] for item in functions) + 2 * len(NOP_ADDRESSES) != SIZE:
        raise BoundaryError("parent slave-connection function tiling drift")

    residual_rows = list(csv.DictReader(
        inputs[RESIDUAL].decode("ascii").splitlines(), delimiter="\t",
    ))
    residual_matches = [row for row in residual_rows if int(row["start"], 16) == START]
    if len(residual_matches) != 1:
        raise BoundaryError("residual slave-connection row count drift")
    residual = residual_matches[0]
    if (
        int(residual["end"], 16), int(residual["size"]), residual["sha256"],
        residual["ownership_category"], residual["family_hint"],
    ) != (
        END, SIZE, STOCK_SHA256,
        "proprietary_modern_controller_source_unavailable",
        "packetcraft_modern_controller",
    ):
        raise BoundaryError("residual slave-connection row identity drift")

    map_rows = list(csv.DictReader(
        inputs[CLUSTER_MAP].decode("ascii").splitlines(), delimiter="\t",
    ))
    slave_map = [row for row in map_rows if row["cluster"] == "slave_connection"]
    if len(slave_map) != 6 or tuple(row["name"] for row in slave_map) != FUNCTION_NAMES:
        raise BoundaryError("pinned slave-connection function map drift")
    manifest_rows = list(csv.DictReader(
        inputs[MANIFEST].decode("ascii").splitlines(), delimiter="\t",
    ))
    if len(manifest_rows) != 13:
        raise BoundaryError("slave-connection boundary manifest row-count drift")
    if manifest_rows[0]["disposition"] != "typed_unsupported_external_boundary":
        raise BoundaryError("slave-connection boundary disposition drift")
    if manifest_rows[-1]["name"] != "deferred by project direction":
        raise BoundaryError("hardware qualification policy drift")

    return {
        "status": "candidate-qualified-fail-closed",
        "read_only": True,
        "hardware_operations": False,
        "license": "MIT",
        "decision": {
            "start": START, "end_exclusive": END, "bytes": SIZE,
            "sha256": STOCK_SHA256,
            "readiness": "typed_unsupported_external_boundary",
            "decision": "six_entry_slave_connection_provider_boundary",
        },
        "function_count": 6,
        "functions": functions,
        "interior_nop_addresses": list(NOP_ADDRESSES),
        "archive_source_status": "proprietary-comparator-only",
        "exact_source_available": False,
        "redistribution_authority_resolved": False,
        "candidate": {
            "source": str(CANDIDATE.relative_to(ROOT)),
            "header": str(HEADER.relative_to(ROOT)),
            "production_routed": False,
        },
        "hardware_validation": "deferred by project direction",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("EM9305 slave connection: candidate-qualified-fail-closed")
        print("typed boundary: 1 span / 3126 bytes / 6 entries")
        print("hardware validation: deferred by project direction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
