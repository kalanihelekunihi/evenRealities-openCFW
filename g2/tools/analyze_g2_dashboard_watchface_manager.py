#!/usr/bin/env python3
"""Fail-closed object/provider audit for G2 dashboard_watchface_manager.c."""
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
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb


AuditError = common.AuditError
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-dashboard-watchface-manager-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-dashboard-watchface-manager-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-dashboard-watchface-manager-provider-map.tsv"
VTABLE_MAP = ROOT / "tools/manifests/g2-dashboard-watchface-vtables.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "bc15b9af96bc3ded29b8b52f03d6208ff128ec045e138b68ba5564e48d373168",
    CLOSURE: "0f9952ccdd58421f8f1347a477b38ede6ada90e6fcd20e5f8fa75eff1caff63e",
    PROVIDER_MAP: "87c9e27c1bb362c5b9fad30de878c880d4cbb39c1660def8ef9a1fb5b40e7103",
    VTABLE_MAP: "12c8c8cacdd880e1aa1708beb594ed887ccc0463f587ac577733e37945d73c78",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_manager.c"
PATH_RUN = 0x006E_748C
PATH_POINTER_CELLS = [0x0050_07E4]
PHYSICAL = (0x0050_0410, 0x0050_0824)
PHYSICAL_SHA256 = "d8601437f9e7d1159c4033ec34a17b57a8fe3d390b35369ef76e912ffdac479f"
BODY_BYTES = 956
BODY_SHA256 = "527f175409db33aaecd5bfbbfb808e74bb32ed19a1252b0f9bb2faea010bd396"
INSTRUCTION_COUNT = 415
INSTRUCTION_DIGEST = "d6e3b4f4abf8aa1842aa511f48482cddf782bc1c48bfb3d4aa7360f4ba63a181"
OUTER_POOL = (0x0050_07CC, 0x0050_0824)
OUTER_POOL_SHA256 = "50d66cff81d1918a5f0bda3b3badfe75706000dbbb9c30b72ea9555fb6b9a543"
PRECEDING_FUNCTION = (0x0050_03E4, 0x0050_03F2)
PRECEDING_FUNCTION_SHA256 = "92fc210181007cdd8335cfa0248b7f5866a1a7e93d84149a9ebebb826d79a38e"
PRECEDING_POOL = (0x0050_03F2, 0x0050_0410)
PRECEDING_POOL_SHA256 = "8dd85319d46353c7505c4abcc1b04d496e2d4d2d39fd0b97bfc068c3d53eae9c"
FOLLOWING_FUNCTION = (0x0050_0824, 0x0050_083E)
FOLLOWING_FUNCTION_SHA256 = "53909f77f1348568fa56f7290fed23d07cc27313434f28a21075a9d5829e8f7e"

ENTRY_COUNT = 24
EXTERNAL_ENTRY_COUNT = 21
ENTRY_SHA256 = "ccd6b4596ee8a43fdf0e644ebea7cf4ea0627fe9bd24c897e28d9b5d2e771b8b"
CALL_COUNT = 34
INTERNAL_CALL_COUNT = 3
CALL_SHA256 = "c98e9d7bd6c57e6e63fa21da5e72b98ed392388e29b6c7e416a3d5485c300b2b"
INDIRECT_SITES = [
    0x0050_045C, 0x0050_0624, 0x0050_0642, 0x0050_065C, 0x0050_0676,
    0x0050_0692, 0x0050_06F4, 0x0050_070E, 0x0050_0728, 0x0050_0742,
    0x0050_075C, 0x0050_0776, 0x0050_0792, 0x0050_07AC, 0x0050_07C8,
]
INDIRECT_SHA256 = "7338341f2a1451e2a5278c2cb8305e55a1e31f1a8217a474036bf887df3b132f"
STORED = [(0x0078_9044, 0x0050_0410)]
STORED_SHA256 = "29139efed7a2bd631634a7554882853502147f8d3fc6670cabf0f7c713c9afe3"
EXTERNAL_TARGET_COUNTS = {
    0x0043_CE9E: 6,
    0x0043_D0CE: 18,
    0x0043_D574: 6,
    0x0055_8142: 1,
}
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0076_AC24: "layout create returned %d",
    0x0078_A7C0: "try_create",
    0x0077_EC30: "dashboard.wf.mgr",
    0x0075_34E0: "dashboard_watchface_manager_init",
    0x0076_AC40: "manager init: parent NULL",
    0x0073_DB60: "manager init: already inited, deinit first",
    0x0076_AC5C: "manager init OK, kind=%d",
    0x0073_DBB8: "manager init: all layouts failed to create",
    0x0072_8824: "dashboard_watchface_manager_set_battery: level=%d",
    0x0074_9024: "dashboard_watchface_manager_set_battery",
}
VTABLE_CONCAT_SHA256 = "f0a22e5166ec590bd729846b3e3b9e05bd575291e0cd4aa73a985002c5f1502c"


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _address_digest(addresses: list[int]) -> str:
    return _sha256(b"".join(struct.pack("<I", address) for address in addresses))


def _recover_function(
    blob: bytes, start: int, end: int
) -> tuple[dict[int, object], list[tuple[int, int]], list[int]]:
    """Recover a function while admitting, but pinning, register-indirect BLX."""
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
    decoder.detail = True
    pending = [start]
    seen: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    indirect: list[int] = []
    while pending:
        address = pending.pop()
        if address in seen:
            continue
        if not start <= address < end:
            raise AuditError(f"control flow escaped function at 0x{address:08x}")
        decoded = list(decoder.disasm(common._slice(blob, address, min(address + 4, end)), address, count=1))
        if not decoded:
            raise AuditError(f"Thumb decode failed at 0x{address:08x}")
        instruction = decoded[0]
        if address + instruction.size > end:
            raise AuditError(f"instruction crosses function end at 0x{address:08x}")
        seen[address] = instruction
        following = address + instruction.size
        mnemonic = instruction.mnemonic
        if mnemonic in ("bl", "blx"):
            if instruction.operands and instruction.operands[0].type == ARM_OP_IMM:
                calls.append((address, instruction.operands[0].imm))
            elif mnemonic == "blx":
                indirect.append(address)
            else:
                raise AuditError(f"unresolved direct call at 0x{address:08x}")
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
    return seen, calls, indirect


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != common.IMAGE_SIZE or _sha256(blob) != common.IMAGE_SHA256:
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
    with VTABLE_MAP.open(newline="", encoding="utf-8") as handle:
        vtable_rows = list(csv.DictReader(handle, delimiter="\t"))
    provider_edges = sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows)
    if len(rows) != 17 or len(provider_rows) != 2 or provider_edges != 31 or len(vtable_rows) != 4:
        raise AuditError("function, provider, or vtable inventory changed")

    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    anchored = 0
    previous_end = PHYSICAL[0]
    outer_bounds: list[tuple[int, int]] = []
    for row in rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        if start in starts or start < previous_end or start >= end:
            raise AuditError(f"invalid function at 0x{start:08x}")
        if previous_end < start:
            outer_bounds.append((previous_end, start))
        body = common._slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(body)
        anchored += row["source_path_anchor"] == "yes"
        previous_end = end
    if previous_end < PHYSICAL[1]:
        outer_bounds.append((previous_end, PHYSICAL[1]))
    outer_bytes = b"".join(common._slice(blob, *bounds) for bounds in outer_bounds)
    if (
        anchored != 3
        or sum(map(len, bodies)) != BODY_BYTES
        or _sha256(b"".join(bodies)) != BODY_SHA256
        or outer_bounds != [OUTER_POOL]
        or _sha256(outer_bytes) != OUTER_POOL_SHA256
    ):
        raise AuditError("body, anchor, or pool inventory changed")
    if len(common._slice(blob, *PHYSICAL)) != 1_044 or _sha256(common._slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical dashboard watchface-manager object changed")
    for bounds, expected, label in (
        (PRECEDING_FUNCTION, PRECEDING_FUNCTION_SHA256, "preceding function"),
        (PRECEDING_POOL, PRECEDING_POOL_SHA256, "preceding pool"),
        (FOLLOWING_FUNCTION, FOLLOWING_FUNCTION_SHA256, "following function"),
    ):
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} changed")

    all_instructions: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    indirect: list[int] = []
    embedded: list[tuple[int, int]] = []
    for interval in intervals:
        recovered, function_calls, function_indirect = _recover_function(blob, *interval)
        all_instructions.update(recovered)
        calls.extend(function_calls)
        indirect.extend(function_indirect)
        embedded.extend(common._uncovered(interval, recovered))
    code = b"".join(
        common._slice(blob, address, address + instruction.size)
        for address, instruction in sorted(all_instructions.items())
    )
    instruction_pairs = sorted((address, instruction.size) for address, instruction in all_instructions.items())
    if (
        len(all_instructions) != INSTRUCTION_COUNT
        or common._instruction_digest(instruction_pairs) != INSTRUCTION_DIGEST
        or len(code) != BODY_BYTES
        or _sha256(code) != BODY_SHA256
        or embedded
    ):
        raise AuditError("instruction closure changed")
    calls.sort()
    indirect.sort()
    external_counts = Counter(target for _, target in calls if target not in starts)
    if (
        len(calls) != CALL_COUNT
        or common._pair_digest(calls) != CALL_SHA256
        or sum(target in starts for _, target in calls) != INTERNAL_CALL_COUNT
        or dict(external_counts) != EXTERNAL_TARGET_COUNTS
    ):
        raise AuditError("direct call topology changed")
    if indirect != INDIRECT_SITES or _address_digest(indirect) != INDIRECT_SHA256:
        raise AuditError("indirect call topology changed")

    for address, expected in STRINGS.items():
        if common._c_string(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")
    path_word = struct.pack("<I", PATH_RUN)
    path_hits: list[int] = []
    cursor = blob.find(path_word)
    while cursor >= 0:
        path_hits.append(common.BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if path_hits != PATH_POINTER_CELLS:
        raise AuditError("path pointer topology changed")

    entries: list[tuple[int, int]] = []
    strict: list[tuple[int, int]] = []
    unknown: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        site = common.BASE + offset
        target = thumb._thumb_bl_target(blob, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            strict.append((site, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown.append((site, target))
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if (
        len(entries) != ENTRY_COUNT
        or common._pair_digest(entries) != ENTRY_SHA256
        or external_entries != EXTERNAL_ENTRY_COUNT
        or strict
        or unknown
    ):
        raise AuditError("entry topology changed")
    encoded = starts | {start | 1 for start in starts}
    stored: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded:
            stored.append((common.BASE + offset, value))
    if stored != STORED or common._pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored entry topology changed")

    vtable_blobs: list[bytes] = []
    vtable_counts: dict[int, int] = {}
    for row in vtable_rows:
        kind = int(row["kind"])
        start = int(row["stock_start"], 0)
        size = int(row["bytes"])
        table = common._slice(blob, start, start + size)
        if size != 60 or _sha256(table) != row["sha256"]:
            raise AuditError(f"watchface vtable {kind} changed")
        words = struct.unpack("<15I", table)
        non_null = [word for word in words if word]
        if len(non_null) != int(row["non_null_slots"]):
            raise AuditError(f"watchface vtable {kind} occupancy changed")
        if any(not (word & 1) or not common.BASE <= (word & ~1) < common.BASE + len(blob) for word in non_null):
            raise AuditError(f"watchface vtable {kind} has a non-Thumb or out-of-image target")
        vtable_counts[kind] = len(non_null)
        vtable_blobs.append(table)
    if _sha256(b"".join(vtable_blobs)) != VTABLE_CONCAT_SHA256:
        raise AuditError("watchface vtable aggregate changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = "dashboard_watchface_manager" in json.dumps(overlay).lower()
    if routed:
        raise AuditError("dashboard watchface manager unexpectedly became production-routed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object, indirect-dispatch, and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_dashboard_watchface_selection_and_operation_dispatch",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 17,
            "ghidra_discovered_functions": 9,
            "additional_recovered_functions": 8,
            "path_anchored_functions": anchored,
            "baseline_ghidra_path_anchors": 1,
            "body_bytes": len(code),
            "reachable_instruction_bytes": len(code),
            "embedded_data_regions": 0,
            "outer_pool_regions": len(outer_bounds),
            "outer_pool_bytes": len(outer_bytes),
            "physical_bytes": 1_044,
            "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": INTERNAL_CALL_COUNT,
            "external_direct_body_calls": sum(external_counts.values()),
            "indirect_body_calls": len(indirect),
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "behavior": {
            "watchface_kinds": [1, 2, 3, 4],
            "operation_table_words": 15,
            "operation_table_non_null_slots": vtable_counts,
            "create_slot_offset": 0,
            "deinit_slot_offset": 4,
            "battery_slot_offset": 0x18,
            "forwarded_slot_offsets": [0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C, 0x20, 0x24, 0x28, 0x2C, 0x30, 0x34, 0x38],
            "unsupported_kind": "null operations table",
            "create_failure": "log nonzero result and return null layout",
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows),
            "direct_external_targets": len(external_counts),
            "direct_external_calls": sum(external_counts.values()),
            "easylogger": {
                "calls": 30,
                "version": "2.2.99 source-equivalent core",
                "selected_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            },
            "g2_dashboard_state_getter_calls": 1,
            "first_party_vtable_calls": len(indirect),
            "cmsis_freertos_calls": 0,
            "new_version_discriminator": False,
            "assessment": "no opaque third-party definition is embedded; indirect targets terminate in pinned first-party watchface tables",
        },
        "boundary": {
            "physical_start": "0x00500410",
            "physical_end_exclusive": "0x00500824",
            "path_pointer_cells": ["0x005007e4"],
            "preceded_by": "one first-party function and compiler pool",
            "followed_by": "first-party dashboard function",
        },
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "the private source and producing commit remain unavailable",
            "semantic names for offset-only wrappers are provisional",
            "individual watchface implementations remain separate first-party objects",
            "no new dependency-version discriminator is present",
            "target UI and lifecycle validation are required before production admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 dashboard watchface-manager audit: PASS")
