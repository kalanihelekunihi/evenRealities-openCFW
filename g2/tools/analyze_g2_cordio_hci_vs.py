#!/usr/bin/env python3
"""Clean-room inclusion and reset-sequence audit for Ambiq hci_vs_apollo3.c."""

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
FUNCTION_MAP = ROOT / "tools/manifests/ambiq-cordio-hci-vs-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/ambiq-cordio-hci-vs-provenance.tsv"
CLOSURE = ROOT / "tools/manifests/ambiq-cordio-hci-vs-closure.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "349e19aad00c7e4e46c2fef263a42d1c2e7ae7b98324acc22eebf8eefbbb0e23",
    PROVENANCE: "945ca20cc175e24f98d934cc8cc30d963feec8e9f999117464a0261521ab9e72",
    CLOSURE: "6eea8091612489c703db3231812cca721b5a84305a1e23e9c840a655d01d720b",
}

MODULE_START = 0x00569B04
MODULE_END = 0x00569D4C
MODULE_SHA256 = "9509223fa164fab9f580b13bb3cab31e17d41929c636f43b1a4ba5fc435af441"
BODY_BYTES = 546
BODY_SHA256 = "6c3463af9d30f55b582fd4bf51cfeb90931c2bfc1b72b8544803d75c65dee3a0"
LITERAL_POOL = (0x00569D26, 0x00569D4C)
LITERAL_POOL_SHA256 = "1901036189b5185ef77121a80e96f6af9ff63a69e3a094ee4b9340b0b45abcba"
LITERAL_WORDS = {
    0x00569D28: 0x20071478,  # hciCoreCb
    0x00569D2C: 0x20000028,  # hciLeSupFeatCfg
    0x00569D30: 0x20074FD0,  # reset random-command counter
    0x00569D34: 0x0078D6DC,  # event mask
    0x00569D38: 0x0078D6E4,  # LE event mask
    0x00569D3C: 0x0078D6EC,  # event-mask page 2
    0x00569D40: 0x200714E0,  # hciCoreCb.bdAddr
    0x00569D44: 0x200714D8,  # hciCoreCb.leStates
    0x00569D48: 0x20073870,  # hciCb
}
DIRECT_CALL_COUNT = 5
DIRECT_CALL_DIGEST = "096ce229c3c5fa6d8159a34fd3a7481b17965d3a3f6ff7d47bb592597267b9b8"
BODY_CALL_COUNT = 25
BODY_CALL_DIGEST = "2f7f5c5d3ddc779541d509e0be1e0b852a9c1474d775367a33a4c6d1ef278514"
SOURCE_ONLY = ["hciCoreVsCmdCmplRcvd", "hciCoreVsEvtRcvd", "hciCoreHwErrorRcvd", "HciVsInit"]


class AuditError(RuntimeError):
    """Raised when authenticated HCI vendor-sequence evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first >= last:
        raise AuditError(f"invalid image span [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("hci_vs_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def packed_pairs_digest(pairs: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned HCI vendor-sequence input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row["function"] for row in rows if row["stock_status"] == "source_only"]
    if len(rows) != 8 or len(linked) != 4 or source_only != SOURCE_ONLY:
        raise AuditError("HCI vendor-sequence source inventory changed")

    bodies = []
    ranges = []
    starts = set()
    interiors = set()
    for row in linked:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock HCI vendor-sequence body changed: {row['function']}")
        bodies.append(raw)
        ranges.append((start, end))
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("HCI vendor-sequence body concatenation changed")
    if sha256(image_slice(blob, MODULE_START, MODULE_END)) != MODULE_SHA256:
        raise AuditError("HCI vendor-sequence physical interval changed")
    pool = image_slice(blob, *LITERAL_POOL)
    if sha256(pool) != LITERAL_POOL_SHA256 or pool[:2] != b"\x00\x00":
        raise AuditError("HCI vendor-sequence literal pool changed")
    for cell, expected in LITERAL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"HCI vendor-sequence literal changed at 0x{cell:08x}")

    decoder = load_decoder()
    ingress = []
    interior_calls = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            ingress.append((address, target))
        elif target in interiors:
            interior_calls.append((address, target))
    if len(ingress) != DIRECT_CALL_COUNT or packed_pairs_digest(ingress) != DIRECT_CALL_DIGEST:
        raise AuditError("HCI vendor-sequence direct ingress changed")
    if interior_calls:
        raise AuditError("direct call into HCI vendor-sequence strict interior appeared")

    body_calls = []
    for start, end in ranges:
        for address in range(start, end, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                body_calls.append((address, target))
    if len(body_calls) != BODY_CALL_COUNT or packed_pairs_digest(body_calls) != BODY_CALL_DIGEST:
        raise AuditError("HCI vendor-sequence provider closure changed")

    stored_entries = []
    stored_interiors = []
    for address in range(BASE, BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", image_slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((address, value))
        elif target in interiors:
            stored_interiors.append((address, value))
    if stored_entries or stored_interiors:
        raise AuditError("stored HCI vendor-sequence entry/interior pointer appeared")

    return {
        "schema_version": 1,
        "image": {"path": str(image_path), "sha256": IMAGE_SHA256},
        "module": {
            "start": MODULE_START,
            "end_exclusive": MODULE_END,
            "physical_bytes": MODULE_END - MODULE_START,
            "linked_function_count": len(linked),
            "linked_function_bytes": BODY_BYTES,
            "source_inventory_functions": len(rows),
            "source_only_functions": SOURCE_ONLY,
            "literal_pool_bytes": len(pool),
            "direct_bl_ingress_sites": len(ingress),
            "direct_provider_calls": len(body_calls),
            "stored_entry_pointers": 0,
            "strict_interior_pointers": 0,
        },
        "abi": {
            "hci_core_cb": 0x20071478,
            "hci_cb": 0x20073870,
            "le_supported_features_config": 0x20000028,
            "feature_width_bits": 64,
            "reset_rand_count": 4,
            "default_tx_power_parameter": 6,
        },
        "reset_sequence": {
            "start_sends_reset": True,
            "start_updates_bd_address": True,
            "reset_completion_sends_nvds_update": True,
            "nvds_completion_sets_rf_power": True,
            "rf_power_completion_sets_event_mask": True,
            "nvds_opcode": 0xFFF2,
            "rf_power_opcode": 0xFCC4,
            "standard_mask_and_capability_sequence_follows": True,
            "four_rand_completions_finish_reset": True,
        },
        "lineage": {
            "classification": "product hybrid Apollo3/Cooper reset sequence",
            "historical_generating_commit_resolved": False,
            "whole_file_source_exact": False,
            "r25_license": "Arm Cordio proprietary SLA",
            "later_oracle_license": "Ambiq BSD-3-Clause-style notice",
        },
        "production": {
            "stock_bytes_replaced": 0,
            "source_owned_bytes_added": 0,
            "vendor_source_copied": False,
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
        print("Ambiq HCI vendor sequence closed: 4 linked / 4 source-only; hybrid reset chain pinned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
