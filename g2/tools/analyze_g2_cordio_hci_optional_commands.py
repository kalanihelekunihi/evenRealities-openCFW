#!/usr/bin/env python3
"""Fail-closed exclusion audit for optional Ambiq Cordio HCI command TUs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
INVENTORY = ROOT / "tools/manifests/ambiq-cordio-hci-optional-command-exclusion.tsv"
INVENTORY_SHA256 = "5a522f5e5ccc6cc08e77c499687d4c73f49b67899d412c5b4a87056758a342d3"

HCI_CMD_ALLOC = 0x0052AE38
SHARED_CMD_INTERVAL = (0x0052AE38, 0x0052B8A4)
PHY_CMD_INTERVAL = (0x00539E48, 0x00539E94)
ALLOC_CALL_COUNT = 45
ALLOC_CALL_DIGEST = "425b3d4fdb753c813da0a790d53b157f29e95a1a491a1e96e5b0470c6abbcac6"
FILES = [
    "hci_cmd_ae.c",
    "hci_cmd_bis.c",
    "hci_cmd_cis.c",
    "hci_cmd_cte.c",
    "hci_cmd_iso.c",
    "hci_cmd_past.c",
]


class AuditError(RuntimeError):
    """Raised when optional-command exclusion evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("hci_optional_cmd_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def packed_pairs_digest(pairs: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def in_interval(address: int, interval: tuple[int, int]) -> bool:
    return interval[0] <= address < interval[1]


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    if not INVENTORY.is_file() or sha256(INVENTORY.read_bytes()) != INVENTORY_SHA256:
        raise AuditError("optional HCI-command inventory changed")

    with INVENTORY.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if [row["file"] for row in rows] != FILES:
        raise AuditError("optional HCI-command file ordering changed")
    function_names = []
    for row in rows:
        names = row["function_names"].split(";")
        if row["stock_status"] != "source_only":
            raise AuditError(f"optional command TU gained stock ownership: {row['file']}")
        if len(names) != int(row["function_count"]):
            raise AuditError(f"optional command function inventory changed: {row['file']}")
        if int(row["mandatory_alloc_calls"]) != len(names):
            raise AuditError(f"mandatory allocation topology changed: {row['file']}")
        function_names.extend(names)
    if len(function_names) != 57 or len(set(function_names)) != 57:
        raise AuditError("optional HCI-command aggregate inventory changed")

    decoder = load_decoder()
    alloc_calls = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        if decoder._thumb_bl_target(blob, address) == HCI_CMD_ALLOC:
            alloc_calls.append((address, HCI_CMD_ALLOC))
    if len(alloc_calls) != ALLOC_CALL_COUNT or packed_pairs_digest(alloc_calls) != ALLOC_CALL_DIGEST:
        raise AuditError("hciCmdAlloc caller closure changed")
    unexplained = [
        pair for pair in alloc_calls
        if not in_interval(pair[0], SHARED_CMD_INTERVAL)
        and not in_interval(pair[0], PHY_CMD_INTERVAL)
    ]
    if unexplained:
        raise AuditError("optional HCI-command allocation caller appeared")

    retained_markers = [name for name in FILES if blob.find(name.encode("ascii")) >= 0]
    if retained_markers:
        raise AuditError("optional HCI-command retained source marker appeared")

    return {
        "schema_version": 1,
        "image": {"path": str(image_path), "sha256": IMAGE_SHA256},
        "exclusion": {
            "translation_units": FILES,
            "source_inventory_functions": len(function_names),
            "source_only_functions": function_names,
            "stock_linked_functions": 0,
            "stock_owned_bytes": 0,
            "mandatory_alloc_calls_in_sources": sum(int(row["mandatory_alloc_calls"]) for row in rows),
            "stock_alloc_callers": len(alloc_calls),
            "unexplained_stock_alloc_callers": 0,
            "retained_source_markers": 0,
        },
        "lineage": {
            "selected_oracle": "AmbiqSuite R4.4.1 later official import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "historical_generating_commit_resolved": False,
            "license": "Arm Cordio proprietary SLA",
        },
        "production": {
            "stock_bytes_replaced": 0,
            "source_owned_bytes_added": 0,
            "proprietary_source_copied": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Optional Ambiq HCI commands excluded: 6 TUs / 57 source-only functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
