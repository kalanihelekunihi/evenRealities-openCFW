#!/usr/bin/env python3
"""Fail-closed linked-object audit for G2 central-role and RingLink policy."""
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
FUNCTION_MAP = ROOT / "tools/manifests/g2-app-ble-central-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-app-ble-central-closure.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "2d11f226179bfbab4590de602d654b0cbaf84b2d400ab82327fba97721f4a06d",
    CLOSURE: "892e810d65fe260e775a6cb4a72d7a2a6a221648973ace4e0c9ab48e4294afb0",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_central.c"
PATH_RUN = 0x006F_F9B8
PATH_POINTER_CELLS = [
    0x004A_02D4,
    0x004A_0FCC,
    0x004A_1AF0,
    0x004A_1FBC,
    0x004A_28EC,
    0x004A_3158,
    0x004A_3554,
]

PHYSICAL = (0x0049_F828, 0x004A_35B0)
PHYSICAL_BYTES = 15_752
PHYSICAL_SHA256 = "8038f98faaa62f91addd9e09c1ae18b215c74abfb07579c21c20282a1e6a205d"
BODY_BYTES = 14_288
BODY_SHA256 = "37e1f0ccd8c0ee6946de90bf2bf01b4b7dddfc5fbde171519e705979e1351181"
POOL_REGIONS = 30
POOL_BYTES = 1_464
POOL_SHA256 = "62c6aa7b38fdb4f5b73ead2b0c21ecda54b7075c6903855246c644cc99914cb5"

# The immediately preceding bytes are the literal pool for
# platform\protocols\ring_service\ring_connect_policy.c.  The following
# bytes begin independently rooted IMU helpers.  These pins prevent an
# adjacency-only expansion of either source object.
PRECEDING_POOL = (0x0049_F744, 0x0049_F828)
PRECEDING_POOL_SHA256 = "7d15d4ff35e78076d0263615ea3d19309ed6e836801140133c2ff09cc5219faa"
FOLLOWING_OBJECT = (0x004A_35B0, 0x004A_360E)
FOLLOWING_OBJECT_SHA256 = "d09e68347e5b1a5848b2252d9e618cdc0fb953554ac375d7c2e2d17995231620"

ENTRY_COUNT = 160
EXTERNAL_ENTRY_COUNT = 58
ENTRY_SHA256 = "d47b5afe099a407e91854de77b0d71a1f945307bbcd3fd5f928d66fd6f794f30"
BODY_CALL_COUNT = 851
INTERNAL_BODY_CALL_COUNT = 102
BODY_CALL_SHA256 = "97f0ee83f5e6f4719e4f39046cde4093210453368bf58bccf13e041d9bca49c6"
STORED_COUNT = 17
STORED_SHA256 = "86efd218917fb8b57d6d80b2e3f7c5b2e65353c742ff43ecd52aa2e54062d748"
INTERIOR_DECODES = [(0x0063_1CEE, 0x0049_FAF4)]

RECOVERED_TERMINALS = {
    # Six functions missed by the baseline Ghidra sweep.  Their entries have
    # independent BL/table roots and their complete linear CFGs terminate at
    # these pinned return encodings before a literal pool or the next body.
    0x004A_1B60: (0x004A_1F2C, bytes.fromhex("07b0f0bd")),
    0x004A_21CC: (0x004A_2248, bytes.fromhex("1fbd")),
    0x004A_22C6: (0x004A_22DC, bytes.fromhex("7047")),
    0x004A_285C: (0x004A_2862, bytes.fromhex("01bd")),
    0x004A_2EA4: (0x004A_2FAE, bytes.fromhex("07b030bd")),
    0x004A_316C: (0x004A_34AA, bytes.fromhex("0cb0bde8f081")),
}

STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0078_C9B4: "IDLE",
    0x0078_C9BC: "OPENING",
    0x0078_A004: "CONNECTED",
    0x0077_DAEC: "LOCAL_DISCONNECTING",
    0x0077_4D5C: "SWITCH_DISCONNECTING",
    0x0078_A010: "CANCELLING",
    0x0078_A01C: "UNPAIRING",
    0x0077_DB00: "_SetRingLinkState",
    0x0077_DB14: "_bleMasterScanStop",
    0x0078_A034: "_masterScan",
    0x0077_4D8C: "_bleMasterScanReport",
    0x0077_4DBC: "_masterConnectCancel",
    0x0078_4D10: "_masterConnect",
    0x0078_4D20: "_bleMasterGetCB",
    0x0078_4D30: "_masterProcMsg",
    0x0077_4E4C: "APP_MasterHanderInit",
    0x0076_8E80: "APP_MasterSetTargetAddrName",
    0x0077_DBA0: "APP_MasterScanEvent",
    0x0077_4E7C: "APP_MasterSetPhyEvent",
    0x0075_1A70: "APP_MasterSysStartTryConnectRing",
    0x0075_1AB8: "APP_MasterOnDominantHandChangedEx",
    0x0076_8ED4: "APP_MasterCleanupRingUnpair",
    0x0075_1B00: "APP_MasterCancelRingConnectRetry",
    0x0077_4E94: "APP_MasterRingMacIsSet",
    0x0075_1B24: "APP_MasterTryReconnectRingByScene",
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
    if len(rows) != 44:
        raise AuditError(f"function inventory changed: {len(rows)}")

    starts: set[int] = set()
    strict_interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    anchored = 0
    previous_end = PHYSICAL[0]
    gaps: list[bytes] = []
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
    if anchored != 24:
        raise AuditError(f"source-path anchor census changed: {anchored}")
    if sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body inventory changed")
    if len(gaps) != POOL_REGIONS or sum(map(len, gaps)) != POOL_BYTES:
        raise AuditError("literal-pool interval inventory changed")
    if _sha256(b"".join(gaps)) != POOL_SHA256:
        raise AuditError("literal-pool bytes changed")

    physical = _slice(blob, *PHYSICAL)
    if len(physical) != PHYSICAL_BYTES or _sha256(physical) != PHYSICAL_SHA256:
        raise AuditError("physical central object changed")
    if _sha256(_slice(blob, *PRECEDING_POOL)) != PRECEDING_POOL_SHA256:
        raise AuditError("preceding ring-policy boundary changed")
    if _sha256(_slice(blob, *FOLLOWING_OBJECT)) != FOLLOWING_OBJECT_SHA256:
        raise AuditError("following IMU boundary changed")

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
    for offset in range(0, len(blob) - 3, 2):
        address = BASE + offset
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in strict_interiors:
            interior.append((address, target))
    if len(entries) != ENTRY_COUNT or _pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct entry topology changed")
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if external_entries != EXTERNAL_ENTRY_COUNT:
        raise AuditError("external direct entry census changed")
    if interior != INTERIOR_DECODES:
        raise AuditError(f"strict-interior raw BL decode topology changed: {interior!r}")

    calls: list[tuple[int, int]] = []
    image_end = BASE + len(blob)
    for start, end in intervals:
        for address in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, address)
            # Reject one non-BL halfword pattern that sign-decodes below the
            # linked image; all retained call targets are linked image code.
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
    if len(stored) != STORED_COUNT or _pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored entry-pointer topology changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any(
        "app_ble_central" in item.get("path", "").lower()
        or "ble_central" in item.get("path", "").lower()
        for item in overlay["sources"]
    )
    if routed:
        raise AuditError("analysis-only central object entered production")

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
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(interior),
        },
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_cordio_central_role_and_ringlink_policy",
            "third_party_dependency": None,
            "historical_source_available": False,
            "private_producing_commit_observable": False,
        },
        "boundary": {
            "physical_start": f"0x{PHYSICAL[0]:08x}",
            "physical_end_exclusive": f"0x{PHYSICAL[1]:08x}",
            "preceded_by": "ring_connect_policy.c literal pool",
            "followed_by": "IMU helper code",
            "path_pointer_cells": [f"0x{value:08x}" for value in PATH_POINTER_CELLS],
        },
        "behavior": {
            "ringlink_states": [
                "IDLE",
                "OPENING",
                "CONNECTED",
                "LOCAL_DISCONNECTING",
                "SWITCH_DISCONNECTING",
                "CANCELLING",
                "UNPAIRING",
            ],
            "application_event_ids": list(range(0xAE, 0xB5)),
            "owner_role_aware": True,
            "rpa_resolution": True,
            "retry_backoff": True,
            "dominant_hand_switch_policy": True,
            "scene_reconnect_policy": True,
            "unpair_cleanup_policy": True,
        },
        "cross_version": {
            "prior_g2_named_functions": 21,
            "stable_named_core": [
                "_bleMasterScanStop",
                "_masterScan",
                "_bleMasterScanReport",
                "_masterConnectCancel",
                "_masterConnect",
                "dmDiscCancel",
                "_bleMasterGetCB",
                "_masterProcMsg",
                "APP_MasterConnectEvent",
                "APP_MasterUnpairDevEvent",
                "APP_MasterSetTargetAddrName",
                "auth_mode_set",
                "APP_MasterSetPhyEvent",
                "APP_MasterResetRetryConnectCnt",
            ],
            "current_delta": "expanded RingLink state, retry notification, dominant-hand, unpair cleanup, and scene reconnect policy",
            "qualification": "the older G2 decompilation is a naming/topology oracle only; every current byte and boundary is independently pinned",
        },
        "production": {
            "candidate": None,
            "production_routed": routed,
            "ownership_bytes": 0,
        },
        "limitations": [
            "the exact private G2 source and producing commit remain unavailable",
            "the single 0x00631cee halfword pattern decodes as BL to interior 0x0049faf4 but is not promoted to a callable function entry",
            "descriptive address-qualified labels are used where no exact retained or cross-version name exists",
            "linked-object closure does not make this policy ABI-compatible or production-routable",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 BLE central-role audit: PASS")
