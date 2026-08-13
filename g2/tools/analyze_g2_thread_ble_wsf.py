#!/usr/bin/env python3
"""Fail-closed audit for the G2 product BLE WSF thread translation unit."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-thread-ble-wsf-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-thread-ble-wsf-provenance.tsv"
CLOSURE = ROOT / "tools/manifests/g2-thread-ble-wsf-closure.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "e7240823d46b1d7fea83f2ee74bd4d187a2cb15ce88783a8b8561755aceccfd8",
    PROVENANCE: "0ae5232fcbb5e5f23eb7c2119842dfc9914f89418288a756caac503bdd213959",
    CLOSURE: "07b277cdb56eb339ff95b48d6e437f2047e5d1fd3830d96967c5f2bbcb802c3f",
}

BODY_BYTES = 656
BODY_SHA256 = "514c822a09a496897861fd8f81603e95b07c83e7b8c401779f5ad4973d611d9f"
PHYSICAL_SPAN = (0x004D0A4C, 0x004D0D24)
PHYSICAL_SHA256 = "497f72ef17c0ae3607a255057bcfe4bc9f0599ebfab9fea8d40b56923db94e49"
LITERAL_POOL = (0x004D0CDC, 0x004D0D24)
LITERAL_POOL_SHA256 = "d6c4a22566c5d0bd523bf5723afb6b13919b210c88e365d63ca04e0d2d72be17"
TASK_ATTRIBUTES = (0x0075B838, 0x0075B85C)
TASK_ATTRIBUTES_SHA256 = "3de23514e8e1fec1c26809144605f5bdb8cee48f949a5a78839f756627d8d715"
DIRECT_CALL_COUNT = 27
DIRECT_CALL_DIGEST = "982c8ddf0171814ac78a0ba6b65da5c5127a9ca7513945fb9859c5f65c619284"
BODY_CALL_COUNT = 50
BODY_CALL_DIGEST = "2e9e033e128c8fb0d50a1b4dc03d801bf3063c542f58cd5fd63a90b75033662f"
STORED_ENTRY = [(0x004D0CF8, 0x004D0A4D)]
STORED_ENTRY_DIGEST = "7b5af863fef7e426c36016829833856998635f2757cc55dd1e860c2815ee2029"
ENTRY_LOOKALIKE = [(0x007940DD, 0x004D0AF7)]
ENTRY_LOOKALIKE_DIGEST = "9ee9d3ccef7d5fa2a5728732a5d9b39b6c89d76cb2cdf8e32f738c61178cd326"

EXPECTED_CALLERS = {
    "threadBleWsfTask": [],
    "threadBleWsfStart": [0x004D0A56],
    "_thread_resource_init": [0x004D0A52],
    "threadBleWsfLoopInit": [0x004D0A5A],
    "threadBleWsfEnter": [0x004D0A4E],
    "threadBleWsfReady": [0x004D0A5E],
    "threadBleWsfInit": [],
    "threadBleWsfDeinit": [],
    "threadBleWsfTakeTxReady": [0x004D0B72, 0x004D0B88, 0x004D0C30],
    "thread_ble_wsf_wait_tx_ready": [
        0x004BDD96,
        0x004BE0A8,
        0x004BE5F0,
        0x004BE90A,
        0x004C4BFE,
    ],
    "threadBleWsfWaitOnce": [0x00475402],
    "thread_ble_wsf_tx_complete_notify": [
        0x004A07D2,
        0x004B7646,
        0x004B7734,
        0x004B77A6,
        0x004BDDF4,
        0x004BE144,
        0x004BE308,
        0x004BE376,
        0x004BE37C,
        0x004BE68C,
        0x004BE9A6,
        0x004C4A04,
        0x004C4C5C,
    ],
}

LITERAL_WORDS = {
    0x004D0CDC: 0x20004068,
    0x004D0CE0: 0x007104A4,
    0x004D0CE4: 0x0077CC1C,
    0x004D0CE8: 0x006FE39C,
    0x004D0CEC: 0x00789AB0,
    0x004D0CF0: 0x006F6CE8,
    0x004D0CF4: 0x0075B838,
    0x004D0CF8: 0x004D0A4D,
    0x004D0CFC: 0x0074FE24,
    0x004D0D00: 0x00766A30,
    0x004D0D04: 0x00724928,
    0x004D0D08: 0x00739D94,
    0x004D0D0C: 0x007104E4,
    0x004D0D10: 0x0072F1C4,
    0x004D0D14: 0x0075BB50,
    0x004D0D18: 0x00707294,
    0x004D0D1C: 0x006F6D34,
    0x004D0D20: 0x006E5610,
}

TASK_ATTRIBUTE_WORDS = {
    0x0075B838: 0x0078EBA4,
    0x0075B83C: 0,
    0x0075B840: 0x20072140,
    0x0075B844: 0x70,
    0x0075B848: 0x20043A98,
    0x0075B84C: 0x4000,
    0x0075B850: 0x31,
    0x0075B854: 1,
    0x0075B858: 0,
}

EXPECTED_STRINGS = {
    0x006FE39C: r"D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_wsf.c",
    0x007104A4: "BLE WSF semaphore initialized: max_count=%d, initial_count=%d",
    0x0077CC1C: "_thread_resource_init",
    0x00789AB0: "task.ble.wsf",
    0x0074FE24: "wait_tx_ready count >= 20(400ms), break",
    0x00766A30: "thread_ble_wsf_wait_tx_ready",
    0x00739D94: "wait_tx_ready success, time = %d ms, count = %d",
    0x0072F1C4: "Failed to release semaphore, status: %d, count: %d",
    0x0075BB50: "thread_ble_wsf_tx_complete_notify",
    0x006F6D34: "tx_complete_notify: semaphore already at max count (%d), skipping release",
    0x0078EBA4: "ble_wsf",
}


class AuditError(RuntimeError):
    """Raised when authenticated BLE WSF-thread evidence changes."""


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


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("thread_ble_wsf_thumb", path)
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
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned BLE WSF-thread input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 12 or [int(row["recovery_order"]) for row in rows] != list(range(1, 13)):
        raise AuditError("BLE WSF-thread body inventory changed")

    bodies: list[bytes] = []
    ranges: list[tuple[int, int]] = []
    starts: dict[int, str] = {}
    interiors: set[int] = set()
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock body changed: {row['function']}")
        bodies.append(raw)
        ranges.append((start, end))
        starts[start] = row["function"]
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("BLE WSF-thread body concatenation changed")
    if sha256(image_slice(blob, *PHYSICAL_SPAN)) != PHYSICAL_SHA256:
        raise AuditError("BLE WSF-thread physical interval changed")
    if sha256(image_slice(blob, *LITERAL_POOL)) != LITERAL_POOL_SHA256:
        raise AuditError("BLE WSF-thread literal pool changed")
    if sha256(image_slice(blob, *TASK_ATTRIBUTES)) != TASK_ATTRIBUTES_SHA256:
        raise AuditError("BLE WSF-thread task attributes changed")

    for cell, expected in {**LITERAL_WORDS, **TASK_ATTRIBUTE_WORDS}.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"BLE WSF-thread word changed at 0x{cell:08x}")
    for address, expected in EXPECTED_STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"BLE WSF-thread string changed at 0x{address:08x}")

    decoder = load_decoder()
    callers = {name: [] for name in starts.values()}
    ingress: list[tuple[int, int]] = []
    interior_bl: list[tuple[int, int]] = []
    wide_entries: list[tuple[int, int]] = []
    interior_wide: list[tuple[int, int]] = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            ingress.append((address, target))
            callers[starts[target]].append(address)
        if target in interiors:
            interior_bl.append((address, target))
        first, second = struct.unpack("<HH", image_slice(blob, address, address + 4))
        target = thumb_wide_branch_target(address, first, second)
        if target in starts:
            wide_entries.append((address, target))
        if target in interiors:
            interior_wide.append((address, target))
    if callers != EXPECTED_CALLERS:
        raise AuditError("BLE WSF-thread direct callers changed")
    if len(ingress) != DIRECT_CALL_COUNT or packed_pairs_digest(ingress) != DIRECT_CALL_DIGEST:
        raise AuditError("BLE WSF-thread direct-call ingress changed")
    if interior_bl or wide_entries or interior_wide:
        raise AuditError("new wide/strict-interior BLE WSF-thread ingress appeared")

    body_calls: list[tuple[int, int]] = []
    for start, end in ranges:
        for address in range(start, end, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                body_calls.append((address, target))
    if len(body_calls) != BODY_CALL_COUNT or packed_pairs_digest(body_calls) != BODY_CALL_DIGEST:
        raise AuditError("BLE WSF-thread provider-call closure changed")

    stored_entries: list[tuple[int, int]] = []
    stored_interiors: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        address = BASE + offset
        if target in starts:
            stored_entries.append((address, value))
        elif target in interiors:
            stored_interiors.append((address, value))
    if stored_entries != STORED_ENTRY + ENTRY_LOOKALIKE:
        raise AuditError("raw BLE WSF-thread stored-entry windows changed")
    if packed_pairs_digest(STORED_ENTRY) != STORED_ENTRY_DIGEST:
        raise AuditError("genuine task-entry pointer digest changed")
    if packed_pairs_digest(ENTRY_LOOKALIKE) != ENTRY_LOOKALIKE_DIGEST:
        raise AuditError("rejected entry-lookalike digest changed")
    if ENTRY_LOOKALIKE[0][0] % 2 == 0 or stored_interiors:
        raise AuditError("BLE WSF-thread pointer classification changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image_path), "sha256": IMAGE_SHA256},
        "surface": {
            "bounded_bodies": 12,
            "body_bytes": BODY_BYTES,
            "physical_start": PHYSICAL_SPAN[0],
            "physical_end_exclusive": PHYSICAL_SPAN[1],
            "physical_bytes": PHYSICAL_SPAN[1] - PHYSICAL_SPAN[0],
            "literal_pool_bytes": LITERAL_POOL[1] - LITERAL_POOL[0],
            "direct_bl_ingress_sites": len(ingress),
            "direct_provider_calls": len(body_calls),
            "stored_entry_pointers": STORED_ENTRY,
            "excluded_unaligned_entry_lookalikes": ENTRY_LOOKALIKE,
            "stored_strict_interior_pointers": 0,
            "direct_strict_interior_branches": 0,
            "wide_branch_entry_targets": 0,
        },
        "thread": {
            "name": "ble_wsf",
            "entry": 0x004D0A4C,
            "control_block": 0x20004068,
            "thread_handle_offset": 0x08,
            "tx_ready_semaphore_offset": 0x14,
            "cmsis_control_block": 0x20072140,
            "cmsis_control_block_bytes": 0x70,
            "stack": 0x20043A98,
            "stack_bytes": 0x4000,
            "priority": 0x31,
            "semaphore_max_count": 1,
            "semaphore_initial_count": 1,
            "dispatcher": 0x0052B9D0,
            "startup_wrapper": 0x004B80F0,
        },
        "flow_control": {
            "immediate_take_timeout": 0,
            "retry_take_timeout": 10,
            "retry_delay_ticks": 10,
            "max_retry_count": 20,
            "diagnostic_bound_ms": 400,
            "release_only_when_count_zero": True,
            "release_when_count_nonzero": False,
        },
        "lineage": {
            "retained_product_path": r"D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_wsf.c",
            "exact_product_source_recovered": False,
            "whole_file_source_exact": False,
            "historical_generating_commit_resolved": False,
            "provider_oracle": "CMSIS-FreeRTOS v10.5.1",
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
        print("G2 BLE WSF thread closed: 12 bodies / 728 physical bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
