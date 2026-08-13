#!/usr/bin/env python3
"""Fail-closed linked-object and provider audit for G2 ux_system.c."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_THUMB, Cs
from capstone.arm import ARM_OP_IMM


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x0043_7FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-ux-system-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-ux-system-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-ux-system-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "f9a6033eead28073b5a3ee031a2176ee30b4b2966263e9bf51042f62e2ace1af",
    CLOSURE: "780dd011b0bcdcad6768404dde691fa86a155e6f4c6505107fa25f779753dee2",
    PROVIDER_MAP: "55b33daa903a1959db233bd301b94751253367b83884d5af432192dba0de7b1d",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_system\ux_system.c"
PATH_RUN = 0x0070_874C
PATH_POINTER_CELLS = [0x0047_D914]

PHYSICAL = (0x0047_CE90, 0x0047_D9C4)
PHYSICAL_BYTES = 2_868
PHYSICAL_SHA256 = "fa0bea56067c3d0e694058691c6c6b3c039958f78a2e1edfd3a7f9cce2d74f33"
BODY_BYTES = 2_668
BODY_SHA256 = "44c5fcc50ecbda71e71b08248f0e6315fd41da260878826ac499aa94b3e79d97"
REACHABLE_INSTRUCTION_COUNT = 985
REACHABLE_CODE_BYTES = 2_668
REACHABLE_CODE_SHA256 = BODY_SHA256
REACHABLE_INSTRUCTION_DIGEST = "237ed3d420ad0719ee79d0d7e4ca50720890a05c83bdf39dee4f8faf08949bcb"

OUTER_POOL = (0x0047_D8FC, 0x0047_D9C4)
OUTER_POOL_SHA256 = "24c58ea9e090b4db81db0fdbf94d06191b23f2fdd80d574dbd171e723ec4b9d2"
PRECEDING_FUNCTION = (0x0047_CE28, 0x0047_CE90)
PRECEDING_FUNCTION_SHA256 = "aab7f85a28c15deb789bf8271954c77ac3f24f9f7ae414832631d62f6acb2da7"
FOLLOWING_FUNCTIONS = (0x0047_D9C4, 0x0047_D9F0)
FOLLOWING_FUNCTIONS_SHA256 = "ce6150663a819e06a473f1a635dacdd4a9238a3590789ffea99df3a09be282ca"

ENTRY_COUNT = 51
EXTERNAL_ENTRY_COUNT = 35
ENTRY_SHA256 = "2cf162b0a82b2ecfa43680bf9432ca88211a5dc87f17120863b59cdff93fcb0f"
BODY_CALL_COUNT = 163
INTERNAL_BODY_CALL_COUNT = 16
BODY_CALL_SHA256 = "4d5451be8e89fe7bd1c071af77c50895c07c7c5d4af43ba075a9244c7f4d8798"
STORED = [(0x006A_4744, 0x0047_CF61)]
STORED_SHA256 = "8b4a7de1a78f42c1d67cffa89efd8137d2b0cdb27f8327ded8ab0fe5e143e357"

EXTERNAL_TARGET_COUNTS = {
    0x0043_CE9E: 19,
    0x0043_D0CE: 57,
    0x0043_D574: 19,
    0x0045_A568: 22,
    0x0046_4D1C: 1,
    0x0046_51E0: 3,
    0x0046_B0EC: 1,
    0x0047_4100: 1,
    0x0047_432C: 1,
    0x0047_697E: 2,
    0x0047_6ACE: 2,
    0x0049_E448: 4,
    0x004A_2914: 6,
    0x004A_2EA4: 2,
    0x004A_2FDC: 1,
    0x004A_BD60: 2,
    0x004D_306C: 4,
}

STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0076_8170: "UX_LocalSystemStatusSyncHandler",
    0x0078_C908: "ux.setting",
    0x0077_D7EC: "SYSTEM_OTA_STATUS_ID\r\n",
    0x0076_81B0: "SYSTEM_BLE_STATUS_ID ROLE = %s",
    0x0072_61E0: "SYSTEM_BLE_STATUS_REPLY_ID state come from peer = %d",
    0x0074_6BC0: "SYSTEM_BLE_STATUS_RING_MAC_SET_ID status=%d",
    0x0074_6BEC: "SYSTEM_BLE_STATUS_RING_REPLY_ID status=%d",
    0x0076_81D0: "SYSTEM_BLE_STATUS_RING_QUERY_ID",
    0x0072_6288: "CB_EVENT_BLE_STATUS_CHANGE UX_GetSystemBLEStatus() = %d",
    0x0073_0CFC: "RPC_SyncRingStatusWithPeer skip, ring mac not set",
    0x0077_4774: "RPC_SyncRingStatusWithPeer",
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


def _instruction_digest(pairs: list[tuple[int, int]]) -> str:
    return _sha256(b"".join(struct.pack("<IH", *pair) for pair in pairs))


def _c_string(blob: bytes, address: int) -> str:
    offset = address - BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _recover_function(blob: bytes, start: int, end: int) -> tuple[dict[int, object], list[tuple[int, int]]]:
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
    decoder.detail = True
    pending = [start]
    seen: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    while pending:
        address = pending.pop()
        if address in seen:
            continue
        if not start <= address < end:
            raise AuditError(f"control flow escaped function at 0x{address:08x}")
        decoded = list(decoder.disasm(_slice(blob, address, min(address + 4, end)), address, count=1))
        if not decoded:
            raise AuditError(f"Thumb decode failed at 0x{address:08x}")
        instruction = decoded[0]
        if address + instruction.size > end:
            raise AuditError(f"instruction crosses function end at 0x{address:08x}")
        seen[address] = instruction
        following = address + instruction.size
        mnemonic = instruction.mnemonic
        if mnemonic in ("bl", "blx"):
            if not instruction.operands or instruction.operands[0].type != ARM_OP_IMM:
                raise AuditError(f"indirect call at 0x{address:08x}")
            calls.append((address, instruction.operands[0].imm))
            pending.append(following)
            continue
        if (mnemonic.startswith("pop") and "pc" in instruction.op_str) or mnemonic in ("bx", "bxj"):
            continue
        if mnemonic.startswith("ldr") and instruction.op_str.startswith("pc,"):
            continue
        if mnemonic in ("tbb", "tbh"):
            raise AuditError(f"unclosed jump table at 0x{address:08x}")
        if mnemonic in ("cbz", "cbnz"):
            pending.extend((following, instruction.operands[-1].imm))
            continue
        is_branch = mnemonic in ("b", "b.w") or (
            mnemonic.startswith("b") and mnemonic not in ("bic", "bfi", "bfc", "bl", "blx")
        )
        if is_branch:
            if not instruction.operands or instruction.operands[0].type != ARM_OP_IMM:
                raise AuditError(f"unresolved branch at 0x{address:08x}")
            pending.append(instruction.operands[0].imm)
            if mnemonic not in ("b", "b.w"):
                pending.append(following)
            continue
        pending.append(following)
    return seen, calls


def _uncovered(interval: tuple[int, int], instructions: dict[int, object]) -> list[tuple[int, int]]:
    covered: set[int] = set()
    for address, instruction in instructions.items():
        covered.update(range(address, address + instruction.size))
    result: list[tuple[int, int]] = []
    cursor, end = interval
    while cursor < end:
        if cursor in covered:
            cursor += 1
            continue
        gap_end = cursor + 1
        while gap_end < end and gap_end not in covered:
            gap_end += 1
        result.append((cursor, gap_end))
        cursor = gap_end
    return result


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise AuditError("EasyLogger provider commit changed")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        provider_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 11 or len(provider_rows) != 4:
        raise AuditError("function or provider inventory changed")
    provider_edges = sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows)
    if provider_edges != sum(EXTERNAL_TARGET_COUNTS.values()):
        raise AuditError("provider edge accounting changed")

    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    anchored = 0
    previous_end = PHYSICAL[0]
    outer_gaps: list[bytes] = []
    for row in rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        if start in starts or start < previous_end or start >= end:
            raise AuditError(f"invalid or overlapping function at 0x{start:08x}")
        if previous_end < start:
            outer_gaps.append(_slice(blob, previous_end, start))
        body = _slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(body)
        anchored += row["source_path_anchor"] == "yes"
        previous_end = end
    if previous_end < PHYSICAL[1]:
        outer_gaps.append(_slice(blob, previous_end, PHYSICAL[1]))
    if intervals[0][0] != PHYSICAL[0] or anchored != 2:
        raise AuditError("object start or path-anchor census changed")
    if sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function-body inventory changed")
    if outer_gaps != [_slice(blob, *OUTER_POOL)] or _sha256(outer_gaps[0]) != OUTER_POOL_SHA256:
        raise AuditError("outer compiler pool changed")
    if len(_slice(blob, *PHYSICAL)) != PHYSICAL_BYTES or _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical ux-system object changed")
    for bounds, expected, label in (
        (PRECEDING_FUNCTION, PRECEDING_FUNCTION_SHA256, "preceding runtime function"),
        (FOLLOWING_FUNCTIONS, FOLLOWING_FUNCTIONS_SHA256, "following ring-policy functions"),
    ):
        if _sha256(_slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} boundary changed")

    all_instructions: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    embedded: list[tuple[int, int]] = []
    for interval in intervals:
        recovered, function_calls = _recover_function(blob, *interval)
        if set(recovered).intersection(all_instructions):
            raise AuditError("recursive instruction inventories overlap")
        all_instructions.update(recovered)
        calls.extend(function_calls)
        embedded.extend(_uncovered(interval, recovered))
    instruction_pairs = sorted((address, instruction.size) for address, instruction in all_instructions.items())
    code = b"".join(_slice(blob, address, address + instruction.size) for address, instruction in sorted(all_instructions.items()))
    if (
        len(all_instructions) != REACHABLE_INSTRUCTION_COUNT
        or _instruction_digest(instruction_pairs) != REACHABLE_INSTRUCTION_DIGEST
        or len(code) != REACHABLE_CODE_BYTES
        or _sha256(code) != REACHABLE_CODE_SHA256
        or embedded
    ):
        raise AuditError("recursive reachable-instruction closure changed")
    calls.sort()
    if len(calls) != BODY_CALL_COUNT or _pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("reachable body-call topology changed")
    if sum(target in starts for _, target in calls) != INTERNAL_BODY_CALL_COUNT:
        raise AuditError("internal body-call census changed")
    external_counts = Counter(target for _, target in calls if target not in starts)
    if dict(external_counts) != EXTERNAL_TARGET_COUNTS:
        raise AuditError(f"provider target accounting changed: {external_counts!r}")

    for address, expected in STRINGS.items():
        if _c_string(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    path_word = struct.pack("<I", PATH_RUN)
    path_hits, cursor = [], blob.find(path_word)
    while cursor >= 0:
        path_hits.append(BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if path_hits != PATH_POINTER_CELLS:
        raise AuditError(f"source-path pointer topology changed: {path_hits!r}")

    sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
    import recover_apollo_embedded_source_paths as thumb

    entries: list[tuple[int, int]] = []
    strict: list[tuple[int, int]] = []
    unknown: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = thumb._thumb_bl_target(blob, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            strict.append((site, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown.append((site, target))
    if len(entries) != ENTRY_COUNT or _pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct entry topology changed")
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if external_entries != EXTERNAL_ENTRY_COUNT or strict or unknown:
        raise AuditError("entry/interior closure changed")

    encoded_starts = starts | {start | 1 for start in starts}
    stored: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_starts:
            stored.append((BASE + offset, value))
    if stored != STORED or _pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored callback topology changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = "ux_system" in json.dumps(overlay).lower()
    if routed:
        raise AuditError("ux system unexpectedly became production-routed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_system_status_and_ring_sync_policy",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": len(rows),
            "ghidra_discovered_functions": 10,
            "path_anchored_functions": anchored,
            "baseline_ghidra_path_anchors": 1,
            "additional_recovered_functions": 1,
            "body_bytes": sum(map(len, bodies)),
            "reachable_instruction_bytes": len(code),
            "embedded_data_regions": 0,
            "embedded_data_bytes": 0,
            "outer_pool_regions": len(outer_gaps),
            "outer_pool_bytes": sum(map(len, outer_gaps)),
            "physical_bytes": PHYSICAL_BYTES,
            "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": INTERNAL_BODY_CALL_COUNT,
            "external_direct_body_calls": len(calls) - INTERNAL_BODY_CALL_COUNT,
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "behavior": {
            "status_ids": {
                "1": "OTA status",
                "2": "BLE status",
                "3": "BLE status reply",
                "4": "ring-MAC-set status",
                "5": "ring query",
                "6": "ring reply",
            },
            "packed_status_bits": {
                "0": "self OTA",
                "1": "peer OTA",
                "2": "self BLE",
                "3": "peer BLE",
                "4": "self ring",
                "5": "peer ring",
                "6": "ring MAC set",
            },
            "system_ble_status": "true only when packed bits 2 and 3 are both set",
            "peer_service_id": "0x0103",
            "ring_mac_guarded_sync": True,
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows),
            "direct_external_targets": len(external_counts),
            "direct_external_calls": sum(external_counts.values()),
            "easylogger": {
                "version": "2.2.99 source-equivalent core",
                "selected_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
                "diagnostic_calls": 95,
            },
            "g2_first_party_calls": 52,
            "new_version_discriminator": False,
            "assessment": "all upstream relationships terminate at admitted or bounded provider seams; no opaque third-party definition is embedded",
        },
        "boundary": {
            "physical_start": f"0x{PHYSICAL[0]:08x}",
            "physical_end_exclusive": f"0x{PHYSICAL[1]:08x}",
            "path_pointer_cells": [f"0x{value:08x}" for value in PATH_POINTER_CELLS],
            "preceded_by": "independent IAR arithmetic runtime function",
            "followed_by": "independent ring-policy helper cluster",
        },
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "the exact private G2 source and producing commit remain unavailable",
            "semantic helper names are inferred; only names explicitly marked exact are retained strings",
            "the object adds no dependency-version discriminator beyond the admitted EasyLogger baseline",
            "production admission requires a clean-room status schema and target role/ring/BLE validation",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 ux-system audit: PASS")
