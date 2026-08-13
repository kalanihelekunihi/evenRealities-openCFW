#!/usr/bin/env python3
"""Fail-closed linked-object audit for G2 BLE peripheral-role policy."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x0043_7FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-app-ble-peripheral-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-app-ble-peripheral-closure.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "859155d823cd358923ec635d3dca20916a32ca8becb8b2d1b9c3fd1b4c6898c2",
    CLOSURE: "4eeef1abdf172df9dfdd72784684f71e51f6d11f0d9c30dcfe16fdf786f76c21",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_peripheral.c"
PATH_RUN = 0x006F_809C
PATH_POINTER_CELLS = [0x0046_DFF4, 0x0046_ED64, 0x0046_F400]

PHYSICAL = (0x0046_DB04, 0x0046_F4A4)
PHYSICAL_BYTES = 6_560
PHYSICAL_SHA256 = "d03a512b45aaa2cd3d6476a258f54270553bb82f42524838a0b23e0f700d36d3"
BODY_BYTES = 5_888
BODY_SHA256 = "fe0cd744cb976c15548cde946fd6dab79aa28cedd94c32893731f46130872f75"
POOL_REGIONS = 18
POOL_BYTES = 672
POOL_SHA256 = "eea96f23eacda207f425ab48baa9d412b062d647a3611844a59414e023923bee"

PRECEDING_OBJECT = (0x0046_DACC, 0x0046_DB04)
PRECEDING_OBJECT_SHA256 = "5440b7cf254fed6dea546b8492659cf15cf62b43f31f59df97de62bc566dac1d"
FOLLOWING_OBJECT = (0x0046_F4A4, 0x0046_F4C2)
FOLLOWING_OBJECT_SHA256 = "b94c941d90027e4de33f400ea6b3e3f9e1961cf685e42da3d8ae98c6b1757af7"

ENTRY_COUNT = 44
EXTERNAL_ENTRY_COUNT = 33
ENTRY_SHA256 = "52ab634482469bb515f153bb3df5b536bd99461e7da4cd351f912348dc360000"
BODY_CALL_COUNT = 374
INTERNAL_BODY_CALL_COUNT = 11
BODY_CALL_SHA256 = "b55b88a4174c1ca4cee78dc3f3b3b2aa99999f627fc7582ab5f0019e3af69c1f"
STORED = [
    (0x0046_EE5C, 0x0046_F099),
    (0x0046_EE60, 0x0046_F351),
    (0x0046_EFD4, 0x0046_EFFD),
    (0x004B_BDB8, 0x0046_EFFD),
    (0x004B_BF2C, 0x0046_F099),
    (0x004C_5674, 0x0046_EE71),
    (0x0058_1724, 0x0046_EE71),
    (0x0058_1730, 0x0046_EEED),
]
STORED_SHA256 = "374ed0235674d907f0326d28943c2c8e7f6bd415ee9e7389990af8e5a6c9acc6"

RECOVERED_TERMINALS = {
    0x0046_ED08: (0x0046_ED58, bytes.fromhex("0ebd")),
    0x0046_EE70: (0x0046_EED8, bytes.fromhex("07bd")),
    0x0046_EEEC: (0x0046_EF54, bytes.fromhex("07bd")),
    0x0046_EFFC: (0x0046_F08E, bytes.fromhex("1fbd")),
    0x0046_F098: (0x0046_F0DE, bytes.fromhex("07bd")),
    0x0046_F2DC: (0x0046_F326, bytes.fromhex("1fbd")),
    0x0046_F350: (0x0046_F3A0, bytes.fromhex("1fbd")),
}

STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0078_A064: "_bleAdvInit",
    0x0078_4DD0: "_blePsnIntoADV",
    0x0078_4DF0: "_bleAdvNameSet",
    0x0076_9024: "_bleSlaveRequestMtuExchange",
    0x0078_4E20: "_bleSlaveSecReq",
    0x0077_DC68: "_bleSlaveProcMsg",
    0x0078_4E40: "APP_BleNameGet",
    0x0077_DCB8: "APP_SlaveHanderInit",
    0x0076_9120: "APP_BleSlaveAdvStartEvent",
    0x0076_913C: "APP_BleSlaveAdvStopEvent",
    0x0077_4F24: "APP_BleSlaveDisconnect",
    0x0077_4F3C: "APP_BleSlaveAsCmdRole",
    0x0076_9158: "APP_IsLocalSlaveAsCmdRole",
    0x0077_DCCC: "APP_IsLeftSlaveRole",
    0x0077_4F54: "_bleSlaveSyncConnectEvt",
    0x0078_A088: "2.2.6.10",
}


class AuditError(RuntimeError):
    """Raised when authenticated evidence or the closed object changes."""


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first > last:
        raise AuditError(f"invalid image interval [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def _pair_digest(pairs: list[tuple[int, int]]) -> str:
    return _sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def _c_string(blob: bytes, address: int) -> str:
    offset = address - BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 31:
        raise AuditError(f"function inventory changed: {len(rows)}")

    starts: set[int] = set()
    strict_interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    gaps: list[bytes] = []
    anchored = 0
    previous_end = PHYSICAL[0]
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        if start in starts or start < previous_end or not start < end:
            raise AuditError(f"invalid or overlapping function at 0x{start:08x}")
        if previous_end < start:
            gaps.append(_slice(blob, previous_end, start))
        body = _slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function body changed: {row['function']}")
        starts.add(start)
        strict_interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(body)
        anchored += row["source_path_anchor"] == "yes"
        previous_end = end
    if previous_end < PHYSICAL[1]:
        gaps.append(_slice(blob, previous_end, PHYSICAL[1]))
    if intervals[0][0] != PHYSICAL[0] or previous_end > PHYSICAL[1]:
        raise AuditError("function inventory escaped physical object")
    if anchored != 12:
        raise AuditError(f"source-path anchor census changed: {anchored}")
    if sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body inventory changed")
    if len(gaps) != POOL_REGIONS or sum(map(len, gaps)) != POOL_BYTES:
        raise AuditError("literal-pool interval inventory changed")
    if _sha256(b"".join(gaps)) != POOL_SHA256:
        raise AuditError("literal-pool bytes changed")

    physical = _slice(blob, *PHYSICAL)
    if len(physical) != PHYSICAL_BYTES or _sha256(physical) != PHYSICAL_SHA256:
        raise AuditError("physical peripheral object changed")
    if _sha256(_slice(blob, *PRECEDING_OBJECT)) != PRECEDING_OBJECT_SHA256:
        raise AuditError("preceding object boundary changed")
    if _sha256(_slice(blob, *FOLLOWING_OBJECT)) != FOLLOWING_OBJECT_SHA256:
        raise AuditError("following controller-helper boundary changed")
    for entry, (terminal, encoding) in RECOVERED_TERMINALS.items():
        row = next((item for item in rows if int(item["stock_start"], 0) == entry), None)
        if row is None or terminal + len(encoding) != int(row["stock_end_exclusive"], 0):
            raise AuditError(f"recovered terminal boundary changed at 0x{entry:08x}")
        if _slice(blob, terminal, terminal + len(encoding)) != encoding:
            raise AuditError(f"recovered return encoding changed at 0x{entry:08x}")

    for address, expected in STRINGS.items():
        if _c_string(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    path_word = struct.pack("<I", PATH_RUN)
    path_hits: list[int] = []
    cursor = blob.find(path_word)
    while cursor >= 0:
        path_hits.append(BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if path_hits != PATH_POINTER_CELLS:
        raise AuditError(f"source-path pointer topology changed: {path_hits!r}")

    sys.path.insert(0, str(ROOT / "tools"))
    import recover_apollo_embedded_source_paths as decoder

    entries: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    unknown_object_targets: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        address = BASE + offset
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in strict_interiors:
            interior.append((address, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown_object_targets.append((address, target))
    if len(entries) != ENTRY_COUNT or _pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct entry topology changed")
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if external_entries != EXTERNAL_ENTRY_COUNT:
        raise AuditError("external direct entry census changed")
    if interior:
        raise AuditError(f"strict-interior raw BL decode topology changed: {interior!r}")
    if unknown_object_targets:
        raise AuditError(f"unrecovered direct object target: {unknown_object_targets!r}")

    calls: list[tuple[int, int]] = []
    image_end = BASE + len(blob)
    for start, end in intervals:
        for address in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None and BASE <= target < image_end:
                calls.append((address, target))
    if len(calls) != BODY_CALL_COUNT or _pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body callee topology changed")
    internal_calls = sum(target in starts for _, target in calls)
    if internal_calls != INTERNAL_BODY_CALL_COUNT:
        raise AuditError("internal callee census changed")

    encoded_starts = starts | {entry | 1 for entry in starts}
    stored: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_starts:
            stored.append((BASE + offset, value))
    if stored != STORED or _pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored entry-pointer topology changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any(
        "app_ble_peripheral" in item.get("path", "").lower()
        or "ble_peripheral" in item.get("path", "").lower()
        for item in overlay["sources"]
    )
    if routed:
        raise AuditError("analysis-only peripheral object entered production")

    return {
        "surface": {
            "linked_functions": len(rows),
            "path_anchored_functions": anchored,
            "additional_recovered_functions": len(rows) - anchored,
            "baseline_ghidra_functions": len(rows) - len(RECOVERED_TERMINALS),
            "recursive_decode_recoveries": len(RECOVERED_TERMINALS),
            "body_bytes": BODY_BYTES,
            "literal_pool_regions": len(gaps),
            "literal_pool_bytes": POOL_BYTES,
            "physical_bytes": len(physical),
            "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": internal_calls,
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(interior),
            "unrecovered_direct_object_targets": len(unknown_object_targets),
        },
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_cordio_peripheral_role_policy",
            "third_party_dependency": None,
            "provider_dependencies": [
                "Cordio DM/ATT/WSF",
                "admitted AmbiqSuite Cordio application framework",
                "G2 BLE profiles and event loop",
            ],
            "historical_source_available": False,
            "private_producing_commit_observable": False,
        },
        "boundary": {
            "physical_start": f"0x{PHYSICAL[0]:08x}",
            "physical_end_exclusive": f"0x{PHYSICAL[1]:08x}",
            "preceded_by": "independently rooted ring-buffer helper",
            "followed_by": "controller channel-mask helper",
            "path_pointer_cells": [f"0x{value:08x}" for value in PATH_POINTER_CELLS],
        },
        "behavior": {
            "advertising_modes": ["product-test indefinite fast", "normal fast then slow"],
            "normal_fast_window_ms": 30_000,
            "firmware_version_in_advertising": "2.2.6.10",
            "application_events": [0xAD, 0xB5, 0xB6, 0xB7],
            "mtu_exchange": True,
            "security_request": True,
            "unpair_policy": True,
            "auto_restart_policy": True,
            "command_role_policy": True,
            "left_right_role_policy": True,
            "profile_fanout": ["OTA", "EUS", "ESS", "EFS", "NUS", "ANCC"],
        },
        "third_party_boundary": {
            "selected_cordio_oracle": "AmbiqSuite 2.5.1",
            "selected_commit": "de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f",
            "packetcraft_ancestor": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "assessment": "provider API ancestry is already admitted; no function in this physical object is an opaque upstream definition",
        },
        "cross_version": {
            "prior_g2_named_functions_in_sequence": 25,
            "stable_core_through_handler_init": 13,
            "current_delta": "expanded message policy, explicit advertising event callbacks, unpair/restart work, command-role and left/right-role helpers",
            "qualification": "the older G2 decompilation is a naming/topology oracle only; every current byte and boundary is independently pinned",
        },
        "production": {
            "candidate": None,
            "production_routed": routed,
            "ownership_bytes": 0,
        },
        "limitations": [
            "the exact private G2 source and producing commit remain unavailable",
            "descriptive address-qualified labels are used where current retained names do not survive",
            "the selected Cordio commit identifies provider ancestry but cannot identify this first-party policy revision",
            "linked-object closure does not make this policy ABI-compatible or production-routable",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 BLE peripheral-role audit: PASS")
