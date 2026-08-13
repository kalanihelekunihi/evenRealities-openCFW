#!/usr/bin/env python3
"""Clean-room inclusion and queue-ABI audit for Ambiq Cordio hci_cmd.c."""

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
FUNCTION_MAP = ROOT / "tools/manifests/ambiq-cordio-hci-cmd-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/ambiq-cordio-hci-cmd-provenance.tsv"
CLOSURE = ROOT / "tools/manifests/ambiq-cordio-hci-cmd-closure.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "c08e4c8e1446f8eeb00ef94aa79c27b0ddb9ee326c38632d54e310695231d3cd",
    PROVENANCE: "462d7f2ed0c8f34bde8f175fe5415f808d442b3b3650676aab56a3add86496c8",
    CLOSURE: "7899866f45ab1c748d515b3f811c2b9c90e4762c8c36f9cb79cdf7e2ea89aee2",
}

MODULE_START = 0x0052AE38
MODULE_END = 0x0052B8A4
MODULE_SHA256 = "dc34dc1f11085b6c7e8748c7edebf2e1b4dbc1568774dd8352b7fc064ca15119"
BODY_BYTES = 2_654
BODY_SHA256 = "cab0777a869c367127b83c0f51c76bb8c7fec32582d7b3f634f8e4f157ccecc1"
LITERAL_ISLAND = (0x0052B6AE, 0x0052B6BC)
LITERAL_ISLAND_SHA256 = "f68646989009779d7d768ce66f33d6b64840a54198ac3d03e6e4d814d174907c"
LITERAL_WORDS = {
    0x0052B6B0: 0x20073AA0,
    0x0052B6B4: 0x20073A90,
    0x0052B6B8: 0x20073870,
}
DIRECT_CALL_COUNT = 156
DIRECT_CALL_DIGEST = "af3562ba738d194152c84607bfa487699037fe1b459428f67db29bb8b093e57e"
BODY_CALL_COUNT = 127
BODY_CALL_DIGEST = "104e66103d9d8f30c9074d632616557d9e6dc23c7f55fee81ce2fe7bc507fec3"
ACCIDENTAL_INTERIOR_WORDS = [(0x006317C0, 0x0052B5EF)]
SOURCE_ONLY = [
    "HciLeAddDevWhiteListCmd",
    "HciLeClearWhiteListCmd",
    "HciLeReadDefDataLen",
    "HciLeReadAdvTXPowerCmd",
    "HciLeReadChanMapCmd",
    "HciLeRemoveDevWhiteListCmd",
    "HciLeSetHostChanClassCmd",
    "HciReadLocalSupFeatCmd",
    "HciReadLocalVerInfoCmd",
    "HciReadRemoteVerInfoCmd",
    "HciReadTxPwrLvlCmd",
    "HciReadAuthPayloadTimeout",
    "HciLeReadPeerResolvableAddr",
    "HciLeReadLocalResolvableAddr",
    "HciLeSetResolvablePrivateAddrTimeout",
    "HciLeReceiverTestCmd",
    "HciLeTransmitterTestCmd",
    "HciLeTestEndCmd",
    "HciLeReceiverTestCmdV3",
    "HciLeTransmitterTestCmdV3",
    "HciLeReadBufSizeCmdV2",
    "HciLeSetHostFeatureCmd",
]


class AuditError(RuntimeError):
    """Raised when authenticated HCI-command evidence changes."""


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
    spec = importlib.util.spec_from_file_location("hci_cmd_thumb", path)
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
            raise AuditError(f"pinned HCI-command input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row["function"] for row in rows if row["stock_status"] == "source_only"]
    if len(rows) != 72 or len(linked) != 50 or source_only != SOURCE_ONLY:
        raise AuditError("HCI-command source inventory changed")
    if [int(row["source_order"]) for row in rows] != list(range(1, 73)):
        raise AuditError("HCI-command source ordering changed")

    bodies = []
    starts: dict[int, str] = {}
    interiors: set[int] = set()
    for row in linked:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock body changed: {row['function']}")
        bodies.append(raw)
        starts[start] = row["function"]
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("HCI-command body concatenation changed")
    if sha256(image_slice(blob, MODULE_START, MODULE_END)) != MODULE_SHA256:
        raise AuditError("HCI-command physical interval changed")

    island = image_slice(blob, *LITERAL_ISLAND)
    if sha256(island) != LITERAL_ISLAND_SHA256 or island[:2] != b"\x00\x00":
        raise AuditError("HCI-command literal/alignment island changed")
    for cell, expected in LITERAL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"HCI-command literal changed at 0x{cell:08x}")

    decoder = load_decoder()
    ingress = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            ingress.append((address, target))
    if len(ingress) != DIRECT_CALL_COUNT or packed_pairs_digest(ingress) != DIRECT_CALL_DIGEST:
        raise AuditError("HCI-command direct-call ingress changed")

    body_calls = []
    for row in linked:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        for address in range(start, end, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                body_calls.append((address, target))
    if len(body_calls) != BODY_CALL_COUNT or packed_pairs_digest(body_calls) != BODY_CALL_DIGEST:
        raise AuditError("HCI-command direct callee closure changed")

    stored_entries = []
    stored_interiors = []
    for address in range(BASE, BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", image_slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((address, value))
        elif target in interiors:
            stored_interiors.append((address, value))
    if stored_entries or stored_interiors != ACCIDENTAL_INTERIOR_WORDS:
        raise AuditError("stored HCI-command entry/interior classification changed")

    exact_entry_windows = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if (value & ~1) in starts:
            exact_entry_windows.append((BASE + offset, value))
    if exact_entry_windows:
        raise AuditError("unaligned stored HCI-command entry pointer appeared")

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
            "inline_and_tail_data_bytes": len(island),
            "direct_bl_ingress_sites": len(ingress),
            "direct_body_call_sites": len(body_calls),
            "stored_entry_pointers": 0,
            "accepted_strict_interior_pointers": 0,
            "excluded_data_words_resembling_interior_pointers": ACCIDENTAL_INTERIOR_WORDS,
        },
        "abi": {
            "hci_cmd_cb": 0x20073A90,
            "timer_offset": 0x00,
            "queue_offset": 0x10,
            "opcode_offset": 0x18,
            "command_credit_offset": 0x1A,
            "hci_cb": 0x20073870,
            "command_header_bytes": 3,
            "command_timeout_seconds": 10,
        },
        "behavior": {
            "send_queues_before_transport": True,
            "successful_transport_dequeues_and_frees": True,
            "completion_restores_one_command_credit": True,
            "timeout_reboots_radio_then_requests_dm_reset": True,
            "reset_drains_pending_queue": True,
        },
        "lineage": {
            "selected_oracle": "AmbiqSuite R4.4.1 later official import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "106e76123c0f03f05f7ce3e4238d02b1ac98fd8f",
            "selected_sha256": "3a2d4609d803524f4765dbdfc65ec043035f2aa75526b0aa39f04873e62d5468",
            "historical_generating_commit_resolved": False,
            "whole_file_source_exact": False,
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
        print("Ambiq hci_cmd closed: 50 linked / 22 source-only; queue and command ABI pinned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
