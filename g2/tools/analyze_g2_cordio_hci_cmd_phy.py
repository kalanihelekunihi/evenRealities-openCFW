#!/usr/bin/env python3
"""Clean-room inclusion audit for Cordio's HCI PHY command wrappers."""

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
FUNCTION_MAP = ROOT / "tools/manifests/cordio-hci-cmd-phy-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/cordio-hci-cmd-phy-provenance.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "4eb24bffdd8ec27a1c11264f9af18b34621463540a56ef3881ec8f7296d7a065",
    PROVENANCE: "480e96df7805e428494deeacf864325770e1ae3479aa4b1cbf46286a17ac6667",
}

BODY_START = 0x00539E48
BODY_END = 0x00539E92
BODY_SHA256 = "99adfd215aa56b86644b456c9ccd2821ffed6d3243280bf60fbad7d0d48d4d2c"
MODULE_END = 0x00539E94
MODULE_SHA256 = "c0474ed7346e079929469434be9d0915768ce3ab16535b28e28470883e6ca780"
DIRECT_CALL_EDGES = [(0x004C5844, BODY_START)]
DIRECT_CALL_DIGEST = "02a04c8b2843d5b5aee9c9ab7ef3c5a041d01820a61ff666222975826326f0e9"
DIRECT_CALLEE_EDGES = [
    (0x00539E58, 0x0052AE38),
    (0x00539E8C, 0x0052AE5E),
]
DIRECT_CALLEE_DIGEST = "c8c4d730f16159fb0d4e06a5686ff1603d0fee71cc8dc8ee1b46d64bfcaa2a35"


class AuditError(RuntimeError):
    """Raised when authenticated HCI PHY-command evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first >= last:
        raise AuditError(f"invalid image span [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def occurrences(blob: bytes, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    return [BASE + offset for offset in range(len(blob) - 3)
            if blob[offset:offset + 4] == needle]


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("hci_cmd_phy_thumb", path)
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
            raise AuditError(f"pinned HCI PHY-command input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row["function"] for row in rows if row["stock_status"] == "source_only"]
    if len(rows) != 3 or [row["function"] for row in linked] != ["HciLeSetPhyCmd"]:
        raise AuditError("HCI PHY-command source inventory changed")
    if source_only != ["HciLeReadPhyCmd", "HciLeSetDefaultPhyCmd"]:
        raise AuditError("HCI PHY-command source-only classification changed")

    body = image_slice(blob, BODY_START, BODY_END)
    if len(body) != 74 or sha256(body) != BODY_SHA256:
        raise AuditError("HciLeSetPhyCmd body changed")
    if image_slice(blob, BODY_END, MODULE_END) != b"\x00\x00":
        raise AuditError("HCI PHY-command alignment changed")
    if sha256(image_slice(blob, BODY_START, MODULE_END)) != MODULE_SHA256:
        raise AuditError("HCI PHY-command physical interval changed")

    decoder = load_decoder()
    ingress = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        if decoder._thumb_bl_target(blob, address) == BODY_START:
            ingress.append((address, BODY_START))
    if ingress != DIRECT_CALL_EDGES or packed_pairs_digest(ingress) != DIRECT_CALL_DIGEST:
        raise AuditError("HCI PHY-command direct-call ingress changed")

    callees = []
    for address in range(BODY_START, BODY_END, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target is not None:
            callees.append((address, target))
    if callees != DIRECT_CALLEE_EDGES or packed_pairs_digest(callees) != DIRECT_CALLEE_DIGEST:
        raise AuditError("HCI PHY-command provider-call closure changed")

    interiors = set(range(BODY_START + 2, BODY_END, 2))
    stored_entries = []
    stored_interiors = []
    for address in range(BASE, BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", image_slice(blob, address, address + 4))[0]
        target = value & ~1
        if target == BODY_START:
            stored_entries.append((address, value))
        elif target in interiors:
            stored_interiors.append((address, value))
    if stored_entries or stored_interiors:
        raise AuditError("stored HCI PHY-command entry/interior pointer appeared")
    if occurrences(blob, BODY_START) or occurrences(blob, BODY_START | 1):
        raise AuditError("unaligned stored HCI PHY-command entry pointer appeared")

    return {
        "schema_version": 1,
        "image": {"path": str(image_path), "sha256": IMAGE_SHA256},
        "module": {
            "start": BODY_START,
            "end_exclusive": MODULE_END,
            "physical_bytes": MODULE_END - BODY_START,
            "linked_function_count": 1,
            "linked_function_bytes": len(body),
            "source_inventory_functions": len(rows),
            "source_only_functions": source_only,
            "direct_bl_ingress_sites": len(ingress),
            "direct_provider_calls": len(callees),
            "stored_entry_pointers": 0,
            "strict_interior_pointers": 0,
        },
        "behavior": {
            "opcode": 0x2032,
            "parameter_bytes": 7,
            "fields": ["handle", "all_phys", "tx_phys", "rx_phys", "phy_options"],
            "null_safe_allocation": True,
            "command_sent_through_hci_cmd_queue": True,
        },
        "lineage": {
            "selected_oracle": "Packetcraft r20.05c dual-chip HCI PHY command source",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "e7bb445bb080a09bf3041f98dde3d355864eaf48",
            "selected_sha256": "e9ddb84511f1163614fd3e912f903160d7fa913158690e2aff13729c522c75c6",
            "definition_bodies_match_ambiq_r25": True,
            "license": "Apache-2.0",
        },
        "production": {
            "stock_bytes_replaced": 0,
            "source_owned_bytes_added": 0,
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
        print("Cordio hci_cmd_phy closed: HciLeSetPhyCmd linked; read/default wrappers source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
