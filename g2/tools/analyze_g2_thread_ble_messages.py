#!/usr/bin/env python3
"""Fail-closed audit for the G2 BLE message TX/RX product threads."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-thread-ble-message-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-thread-ble-message-provenance.tsv"
CLOSURE = ROOT / "tools/manifests/g2-thread-ble-message-closure.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "214c22e17ebd7a1d5685670f1d09fcd558855c8b37f5e6b49e39e869785f2b30",
    PROVENANCE: "1b71d385d9e2c306cf6362322441b2200a0ce28fc4f072ef7a7e6db73646d81e",
    CLOSURE: "05172cd7ac51df76e5474f81d46787903fec3da6c45f4d3f6af94d4df30c6d4f",
}

TX = "thread_ble_msgtx.c"
RX = "thread_ble_msgrx.c"
EXPECTED = {
    TX: {
        "bodies": 21,
        "body_bytes": 3096,
        "body_sha256": "19c94266075784b6af0aaf084e5e515f67ce9a194a3ef9202d9d0626fd6028fb",
        "physical": (0x00475290, 0x00475FC0),
        "physical_sha256": "7402dc013b7c00390e68c3881563f9a323e04dba0593bb7b6a2b0b0deca0808a",
        "data_spans": [
            (0x00475D5E, 0x00475D78),
            (0x00475DD8, 0x00475DE0),
            (0x00475E62, 0x00475E6C),
            (0x00475ED4, 0x00475FC0),
        ],
        "data_bytes": 280,
        "data_sha256": "f5b7678e5cb7bcfbcbc198f7910553c1df3a23393d8e7f4782d1aa93c2eea4eb",
        "attributes": (0x0075B85C, 0x0075B880),
        "attributes_sha256": "f5ac5cb6f8198ff1f30b17bf044acd959f6032006ee8528e38f64fbeed3b94b4",
        "direct_calls": 151,
        "direct_call_digest": "c62731109eddb44adf76505c3b59c94ed79e5f0083f7d31d80799e1d94ddfd48",
        "body_calls": 190,
        "body_call_digest": "dc5fe8defc484a4133132e63607dea90ec3087b56bdf3691bd550bc89e6ae1b8",
        "stored_entries": [(0x00475E68, 0x00475291), (0x007940C8, 0x00475349)],
        "stored_entry_digest": "aa5c0247c9d0f1c62ff11e8a6ecc4242d73cb147f340bb56451efab7c9b48016",
        "entry_lookalikes": [],
        "interior_lookalikes": 5,
        "interior_lookalike_digest": "93262d96d57bf9e9c32c99697efe1459260a7ff55d996a22ec9d2c5e95135dc3",
        "false_bl_interiors": [],
    },
    RX: {
        "bodies": 13,
        "body_bytes": 1390,
        "body_sha256": "755433ad80a06a3953d8719b87d16fd529a6579281b67561a77b9b0e35681e9b",
        "physical": (0x0048EDB0, 0x0048F3A4),
        "physical_sha256": "8dd458f569db89c4a0588af573cb6091abed7e4be60c7ee2bb60e9e7ffcacf9d",
        "data_spans": [(0x0048F126, 0x0048F12C), (0x0048F324, 0x0048F3A4)],
        "data_bytes": 134,
        "data_sha256": "e0d4ba3f2daf67a70d1c10a840229613a06e8a8997871323b349d0a8d3a97fd4",
        "attributes": (0x0075B880, 0x0075B8A4),
        "attributes_sha256": "066b8a116dcc04d3b199b03cc222a7abec42c36fd693e0b843f6004cdb0cab3b",
        "direct_calls": 12,
        "direct_call_digest": "87f15d649ae9e21536dd8aa8e8c22c507cad0081b0ab3d8e0f4a2dfc7d340fd7",
        "body_calls": 93,
        "body_call_digest": "68b94121555001b3a4e25769f709e2df0002556996d2a33feaa1d54029ef6801",
        "stored_entries": [(0x0048F340, 0x0048EDB1), (0x004C9C64, 0x0048F12D)],
        "stored_entry_digest": "96e852a35f3566a65a9b830a72bf49690e37942862003a63fc6beb8b9fc42ebb",
        "entry_lookalikes": [(0x00791D72, 0x0048F12D), (0x007940BD, 0x0048EE69)],
        "interior_lookalikes": 26,
        "interior_lookalike_digest": "05226e388332bbec1cbf51f5774115d783f4391497177d8078d45f1cb5d03deb",
        "false_bl_interiors": [(0x0048DF70, 0x0048F0CE)],
    },
}

ATTRIBUTE_WORDS = {
    TX: {
        0x0075B85C: 0x0078C5F0,
        0x0075B860: 0,
        0x0075B864: 0x200721B0,
        0x0075B868: 0x70,
        0x0075B86C: 0x20047A98,
        0x0075B870: 0x4000,
        0x0075B874: 0x30,
        0x0075B878: 1,
        0x0075B87C: 0,
    },
    RX: {
        0x0075B880: 0x0078C5FC,
        0x0075B884: 0,
        0x0075B888: 0x20072220,
        0x0075B88C: 0x70,
        0x0075B890: 0x2004BA98,
        0x0075B894: 0x4000,
        0x0075B898: 0x30,
        0x0075B89C: 1,
        0x0075B8A0: 0,
    },
}

RX_TAIL_WORDS = {
    0x0048F324: 0x20003FFC,
    0x0048F328: 0x006FE234,
    0x0048F32C: 0x0078C638,
    0x0048F330: 0x00789A50,
    0x0048F334: 0x007841A8,
    0x0048F338: 0x007734F8,
    0x0048F33C: 0x0075B880,
    0x0048F340: 0x0048EDB1,
    0x0048F344: 0x00766850,
    0x0048F348: 0x0077CB44,
    0x0048F34C: 0x00745224,
    0x0048F350: 0x0077CB5C,
    0x0048F354: 0x00789A60,
    0x0048F358: 0x0075B9C4,
    0x0048F35C: 0x00745250,
    0x0048F360: 0x00773514,
    0x0048F364: 0x0072F024,
    0x0048F368: 0x007247D8,
    0x0048F36C: 0x00707184,
    0x0048F370: 0x007103E4,
    0x0048F374: 0x006FE27C,
    0x0048F378: 0x00773530,
    0x0048F37C: 0x007841BC,
    0x0048F380: 0x0074FBA4,
    0x0048F384: 0x00766870,
    0x0048F388: 0x0074527C,
    0x0048F38C: 0x007452A8,
    0x0048F390: 0x00724810,
    0x0048F394: 0x0074FBCC,
    0x0048F398: 0x00739C14,
    0x0048F39C: 0x0075B9E8,
    0x0048F3A0: 0x00739C44,
}

EXPECTED_STRINGS = {
    0x006FE2C4: r"D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_msgtx.c",
    0x006FE234: r"D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_msgrx.c",
    0x0078C644: "ble.msgtx",
    0x0078C638: "ble.msgrx",
    0x0078C5F0: "ble_msgtx",
    0x0078C5FC: "ble_msgrx",
    0x007841A8: "thread_ble_msgrx",
    0x0077CB44: "_thread_pb_msg_handler",
    0x0077CB5C: "thread ble msgrx exit",
    0x00789A60: "_thread_exit",
    0x00773514: "Thread_BleMsgrxQueueClear",
    0x007841BC: "Thread_MsgRxFromBle",
}


class AuditError(RuntimeError):
    """Raised when authenticated BLE message-thread evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first >= last:
        raise AuditError(f"invalid image span [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def cstring(blob: bytes, address: int) -> str:
    first = address - BASE
    last = blob.find(b"\0", first)
    if first < 0 or last < first:
        raise AuditError(f"invalid C string at 0x{address:08x}")
    return blob[first:last].decode("ascii")


def packed_pairs_digest(pairs: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def packed_addresses_digest(addresses: list[int]) -> str:
    return sha256(b"".join(struct.pack("<I", address) for address in addresses))


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("thread_ble_message_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def thumb_wide_branch_target(address: int, first: int, second: int) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected_hash in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected_hash:
            raise AuditError(f"pinned BLE message-thread input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    rows_by_module: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        rows_by_module[row["module"]].append(row)
    if set(rows_by_module) != {TX, RX}:
        raise AuditError("BLE message-thread module inventory changed")

    starts: dict[int, tuple[str, str]] = {}
    interiors: dict[int, str] = {}
    ranges_by_module: dict[str, list[tuple[int, int]]] = defaultdict(list)
    bodies_by_module: dict[str, list[bytes]] = defaultdict(list)
    for module in (TX, RX):
        module_rows = rows_by_module[module]
        expected = EXPECTED[module]
        if len(module_rows) != expected["bodies"] or [
            int(row["recovery_order"]) for row in module_rows
        ] != list(range(1, expected["bodies"] + 1)):
            raise AuditError(f"{module} body order changed")
        for row in module_rows:
            start = int(row["stock_start"], 0)
            end = int(row["stock_end_exclusive"], 0)
            raw = image_slice(blob, start, end)
            if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
                raise AuditError(f"stock body changed: {row['function']}")
            starts[start] = (module, row["function"])
            interiors.update({address: module for address in range(start + 2, end, 2)})
            ranges_by_module[module].append((start, end))
            bodies_by_module[module].append(raw)

        joined = b"".join(bodies_by_module[module])
        if len(joined) != expected["body_bytes"] or sha256(joined) != expected["body_sha256"]:
            raise AuditError(f"{module} body concatenation changed")
        if sha256(image_slice(blob, *expected["physical"])) != expected["physical_sha256"]:
            raise AuditError(f"{module} physical interval changed")
        data = b"".join(image_slice(blob, *span) for span in expected["data_spans"])
        if len(data) != expected["data_bytes"] or sha256(data) != expected["data_sha256"]:
            raise AuditError(f"{module} data-island closure changed")
        if sha256(image_slice(blob, *expected["attributes"])) != expected["attributes_sha256"]:
            raise AuditError(f"{module} task attributes changed")

    for words in ATTRIBUTE_WORDS.values():
        for address, expected_word in words.items():
            word = struct.unpack("<I", image_slice(blob, address, address + 4))[0]
            if word != expected_word:
                raise AuditError(f"task attribute word changed at 0x{address:08x}")
    for address, expected_word in RX_TAIL_WORDS.items():
        word = struct.unpack("<I", image_slice(blob, address, address + 4))[0]
        if word != expected_word:
            raise AuditError(f"RX literal word changed at 0x{address:08x}")
    if image_slice(blob, 0x0048F126, 0x0048F12C) != b"\0\0mac\0":
        raise AuditError("RX inline logger category changed")
    for address, expected_string in EXPECTED_STRINGS.items():
        if cstring(blob, address) != expected_string:
            raise AuditError(f"BLE message-thread string changed at 0x{address:08x}")

    decoder = load_decoder()
    callers: dict[tuple[str, str], list[int]] = defaultdict(list)
    ingress: dict[str, list[tuple[int, int]]] = defaultdict(list)
    interior_bl: dict[str, list[tuple[int, int]]] = defaultdict(list)
    wide_entries: dict[str, list[tuple[int, int]]] = defaultdict(list)
    interior_wide: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            module, function = starts[target]
            callers[(module, function)].append(address)
            ingress[module].append((address, target))
        if target in interiors:
            interior_bl[interiors[target]].append((address, target))
        first, second = struct.unpack("<HH", image_slice(blob, address, address + 4))
        target = thumb_wide_branch_target(address, first, second)
        if target in starts:
            wide_entries[starts[target][0]].append((address, target))
        if target in interiors:
            interior_wide[interiors[target]].append((address, target))

    for row in rows:
        key = (row["module"], row["function"])
        addresses = callers[key]
        if len(addresses) != int(row["direct_bl_callers"]):
            raise AuditError(f"direct caller count changed: {row['function']}")
        if packed_addresses_digest(addresses) != row["direct_bl_caller_digest"]:
            raise AuditError(f"direct caller set changed: {row['function']}")

    body_calls: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for module in (TX, RX):
        for start, end in ranges_by_module[module]:
            for address in range(start, end, 2):
                target = decoder._thumb_bl_target(blob, address)
                if target is not None:
                    body_calls[module].append((address, target))

    for module in (TX, RX):
        expected = EXPECTED[module]
        if len(ingress[module]) != expected["direct_calls"] or packed_pairs_digest(
            ingress[module]
        ) != expected["direct_call_digest"]:
            raise AuditError(f"{module} direct-call ingress changed")
        if len(body_calls[module]) != expected["body_calls"] or packed_pairs_digest(
            body_calls[module]
        ) != expected["body_call_digest"]:
            raise AuditError(f"{module} provider-call closure changed")
        if interior_bl[module] != expected["false_bl_interiors"]:
            raise AuditError(f"{module} strict-interior BL classification changed")
        if wide_entries[module] or interior_wide[module]:
            raise AuditError(f"new {module} B.W entry/interior ingress appeared")

    # The sole raw BL-looking RX interior hit begins at the second halfword of
    # an authenticated 32-bit SMULBB, so it is not an instruction boundary.
    if image_slice(blob, 0x0048DF6E, 0x0048DF72) != bytes.fromhex("10fb01f0"):
        raise AuditError("RX false-BL instruction proof changed")

    raw_entries: dict[str, list[tuple[int, int]]] = defaultdict(list)
    raw_interiors: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        address = BASE + offset
        if target in starts:
            raw_entries[starts[target][0]].append((address, value))
        elif target in interiors:
            raw_interiors[interiors[target]].append((address, value))
    for module in (TX, RX):
        expected = EXPECTED[module]
        if raw_entries[module] != expected["stored_entries"] + expected["entry_lookalikes"]:
            raise AuditError(f"{module} raw stored-entry windows changed")
        if packed_pairs_digest(expected["stored_entries"]) != expected["stored_entry_digest"]:
            raise AuditError(f"{module} genuine stored-entry digest changed")
        if len(raw_interiors[module]) != expected["interior_lookalikes"] or packed_pairs_digest(
            raw_interiors[module]
        ) != expected["interior_lookalike_digest"]:
            raise AuditError(f"{module} raw strict-interior lookalikes changed")
        if any(address % 4 == 0 for address, _ in expected["entry_lookalikes"]):
            raise AuditError(f"{module} rejected entry lookalike became aligned")

    def surface(module: str) -> dict:
        expected = EXPECTED[module]
        return {
            "bounded_bodies": expected["bodies"],
            "body_bytes": expected["body_bytes"],
            "physical_start": expected["physical"][0],
            "physical_end_exclusive": expected["physical"][1],
            "physical_bytes": expected["physical"][1] - expected["physical"][0],
            "data_island_bytes": expected["data_bytes"],
            "direct_bl_ingress_sites": len(ingress[module]),
            "direct_provider_calls": len(body_calls[module]),
            "stored_entry_pointers": expected["stored_entries"],
            "excluded_unaligned_entry_lookalikes": expected["entry_lookalikes"],
            "raw_strict_interior_lookalikes": len(raw_interiors[module]),
            "stored_strict_interior_pointers": 0,
            "direct_strict_interior_branches": 0,
            "excluded_false_bl_interiors": expected["false_bl_interiors"],
            "wide_branch_entry_targets": 0,
        }

    return {
        "schema_version": 1,
        "image": {"path": str(image_path), "sha256": IMAGE_SHA256},
        "transmit": {
            "surface": surface(TX),
            "thread": {
                "name": "ble_msgtx",
                "entry": 0x00475290,
                "control_block": 0x20004020,
                "thread_handle_offset": 0x08,
                "queue_handle_offset": 0x0C,
                "queue_capacity": 150,
                "queue_item_bytes": 4,
                "cmsis_control_block": 0x200721B0,
                "cmsis_control_block_bytes": 0x70,
                "stack": 0x20047A98,
                "stack_bytes": 0x4000,
                "priority": 0x30,
                "lifecycle_state": 8,
            },
            "protocol": {
                "queue_flag": 0x00400000,
                "exit_flag": 0x00800000,
                "wait_mask": 0x00FFFFFF,
                "queue_message_types": [1, 2, 4, 8],
                "wsf_ready_probe_timeout": 50,
                "queue_put_timeout": 500,
            },
        },
        "receive": {
            "surface": surface(RX),
            "thread": {
                "name": "ble_msgrx",
                "entry": 0x0048EDB0,
                "control_block": 0x20003FFC,
                "thread_handle_offset": 0x08,
                "queue_handle_offset": 0x0C,
                "queue_capacity": 150,
                "queue_item_bytes": 4,
                "cmsis_control_block": 0x20072220,
                "cmsis_control_block_bytes": 0x70,
                "stack": 0x2004BA98,
                "stack_bytes": 0x4000,
                "priority": 0x30,
                "lifecycle_state": 7,
            },
            "protocol": {
                "queue_flag": 0x00400000,
                "exit_flag": 0x00800000,
                "wait_mask": 0x00FFFFFF,
                "queue_message_types": [0x80, *range(0xC0, 0xC8), 0x200, 0x400],
                "record_header_bytes": 8,
                "payload_offset": 8,
                "length_storage_bits": 16,
                "allocation_rounding": "(uint16_length + 11) & ~3",
                "queue_put_timeout": 500,
            },
        },
        "lineage": {
            "retained_product_paths": [EXPECTED_STRINGS[0x006FE2C4], EXPECTED_STRINGS[0x006FE234]],
            "exact_product_source_recovered": False,
            "whole_file_source_exact": False,
            "historical_generating_commit_resolved": False,
            "tx_clean_room_reconstruction_present": True,
            "rx_clean_room_reconstruction_present": False,
            "provider_oracle": "CMSIS-FreeRTOS v10.5.1",
        },
        "production": {
            "new_stock_bytes_replaced_by_this_audit": 0,
            "new_source_owned_bytes_added_by_this_audit": 0,
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
        print("G2 BLE message threads closed: 34 bodies / 4,900 physical bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
