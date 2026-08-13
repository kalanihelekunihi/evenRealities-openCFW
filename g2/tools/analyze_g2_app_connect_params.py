#!/usr/bin/env python3
"""Fail-closed linked-object audit for G2 BLE connection-parameter policy."""
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
FUNCTION_MAP = ROOT / "tools/manifests/g2-app-connect-params-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-app-connect-params-closure.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "9137155cd332c61d5537d408204404e1c280558ec7e2930ea92560071607cfe0",
    CLOSURE: "a22e3b971b6461d761fb8c9ddac6a3522dadc053830181c808e4bd2a39d2ba5b",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_connect_params.c"
PATH_RUN = 0x006F_81BC
PATH_POINTER_CELLS = [0x0047_7748, 0x0047_7AD4, 0x0047_82B8, 0x0047_874C]

PHYSICAL = (0x0047_6CBC, 0x0047_87A4)
PHYSICAL_BYTES = 6_888
PHYSICAL_SHA256 = "ab0417a12435e9d204ccee9730a8a139d203516933de7587590b071ce5390deb"
BODY_BYTES = 6_336
BODY_SHA256 = "a3833e8208708812423d9af34f1bd7e4d274730ba1698fc1870c52906605d18d"
POOL_REGIONS = 8
POOL_BYTES = 552
POOL_SHA256 = "b15934ee7037c87f54e0453cc2f2ab43d052b51ccfdc2702914ebe6429e8f83e"

# The preceding interval is the final pool of fw_event_loop.c.  The following
# interval is the independently rooted 188-byte bond-erasure helper that also
# immediately follows this policy object in the prior G2 function ordering.
PRECEDING_POOL = (0x0047_6BF0, 0x0047_6CBC)
PRECEDING_POOL_SHA256 = "d4be69e09c378bb4984fc56b42a3222bec9331fc25602fdcf8012a0ffb1babe5"
FOLLOWING_OBJECT = (0x0047_87A4, 0x0047_8860)
FOLLOWING_OBJECT_SHA256 = "f69f9265409d41f986e85779a42ef507389c18d6a99caa123060dc4de5687b1d"

ENTRY_COUNT = 39
EXTERNAL_ENTRY_COUNT = 30
ENTRY_SHA256 = "d7325e12d8747075fcfc27e288cb99ff2976ce85774f5d1208785a3b4055f0ae"
BODY_CALL_COUNT = 345
INTERNAL_BODY_CALL_COUNT = 9
BODY_CALL_SHA256 = "897a9d0be2a8b73bf851f854c1e78b6a1b1b5fad2d3d31a0a20c4d37bfd1acb8"
STORED_COUNT = 3
STORED_SHA256 = "dfbeccbfbe944e51105dcf771682b360e2caeb45037f5c4b1ce445b6f3d12ff7"
INTERIOR_DECODES = [(0x0048_3566, 0x0047_7B72), (0x0058_1EB6, 0x0047_74C4)]
INTERIOR_CONTAINERS = {
    0x0048_3564: bytes.fromhex("95fbf4f7"),  # sdiv r7,r5,r4
    0x0058_1EB4: bytes.fromhex("b2fbf5f6"),  # udiv r6,r2,r5
}

STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0077_DCE0: "_bleSlaveConnUpdate",
    0x0077_DCF4: "_isConnParamsFast",
    0x0077_DD30: "_isConnParamsSlow",
    0x0077_DD44: "_connectParamReq",
    0x0077_4F9C: "_connectParamReq_impl",
    0x0077_4FCC: "_bleConnParaConnectEvt",
    0x0077_4FFC: "_connUpdateFinishInd",
    0x0077_5014: "APP_ConnectParamHandler",
    0x0075_DCF0: "APP_ConnectParamESSSetFastMode",
    0x0075_DD10: "APP_ConnectParamOTASetFastMode",
    0x0075_DD30: "APP_ConnectParamOTASetFastMode",
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
    if len(rows) != 14:
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
    if anchored != 10:
        raise AuditError(f"source-path anchor census changed: {anchored}")
    if sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body inventory changed")
    if len(gaps) != POOL_REGIONS or sum(map(len, gaps)) != POOL_BYTES:
        raise AuditError("literal-pool interval inventory changed")
    if _sha256(b"".join(gaps)) != POOL_SHA256:
        raise AuditError("literal-pool bytes changed")

    physical = _slice(blob, *PHYSICAL)
    if len(physical) != PHYSICAL_BYTES or _sha256(physical) != PHYSICAL_SHA256:
        raise AuditError("physical connection-parameter object changed")
    if _sha256(_slice(blob, *PRECEDING_POOL)) != PRECEDING_POOL_SHA256:
        raise AuditError("preceding event-loop pool boundary changed")
    if _sha256(_slice(blob, *FOLLOWING_OBJECT)) != FOLLOWING_OBJECT_SHA256:
        raise AuditError("following bond-helper boundary changed")

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

    sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
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
    for instruction, encoding in INTERIOR_CONTAINERS.items():
        if _slice(blob, instruction, instruction + 4) != encoding:
            raise AuditError(f"interior-decode containing instruction changed at 0x{instruction:08x}")

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
    if len(stored) != STORED_COUNT or _pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored entry-pointer topology changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any(
        "app_connect_params" in item.get("path", "").lower()
        or "connect_params" in item.get("path", "").lower()
        for item in overlay["sources"]
    )
    if routed:
        raise AuditError("analysis-only connection-parameter object entered production")

    return {
        "surface": {
            "linked_functions": len(rows),
            "path_anchored_functions": anchored,
            "additional_recovered_functions": len(rows) - anchored,
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
        },
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_cordio_connection_parameter_policy",
            "third_party_dependency": None,
            "provider_dependencies": ["Cordio DM", "Cordio WSF messaging", "G2 event loop"],
            "historical_source_available": False,
            "private_producing_commit_observable": False,
        },
        "boundary": {
            "physical_start": f"0x{PHYSICAL[0]:08x}",
            "physical_end_exclusive": f"0x{PHYSICAL[1]:08x}",
            "preceded_by": "fw_event_loop.c final literal pool",
            "followed_by": "independent bond-erasure helper",
            "path_pointer_cells": [f"0x{value:08x}" for value in PATH_POINTER_CELLS],
        },
        "behavior": {
            "policy_events": {"fast": 0xA3, "slow": 0xA4, "request": 0xB9},
            "dm_events": [0x27, 0x28, 0x29, 0x40],
            "fast_interval_threshold_units": 25,
            "slow_interval_threshold_units": 72,
            "connection_ids": [1, 2, 3],
            "retry_delays_ms": [2_000, 4_000, 10_000, 30_000, 60_000],
            "ess_fast_mode": True,
            "ota_fast_mode": True,
            "central_role_guard": True,
        },
        "cross_version": {
            "prior_g2_named_functions": 15,
            "stable_current_names": [row["function"] for row in rows],
            "older_only_function": "ble_conn_param_log_format",
            "same_size_current_functions": 7,
            "current_delta": "expanded request validation and handler policy; standalone older log-format helper is absent",
            "qualification": "the older G2 decompilation is a naming/topology oracle only; every current byte and boundary is independently pinned",
        },
        "production": {
            "candidate": None,
            "production_routed": routed,
            "ownership_bytes": 0,
        },
        "limitations": [
            "the exact private G2 source and producing commit remain unavailable",
            "the two strict-interior raw BL decodes are second-halfword artifacts inside authenticated sdiv and udiv instructions",
            "the four non-path-anchored names rely on stable prior-G2 ordering and behavior",
            "linked-object closure does not make this policy ABI-compatible or production-routable",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 BLE connection-parameter audit: PASS")
