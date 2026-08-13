#!/usr/bin/env python3
"""Fail-closed linked-object/provider audit for EvenAI even_ai_timer.c."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_dashboard_watchface_manager as indirect_common
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb


AuditError = common.AuditError
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-even-ai-timer-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-even-ai-timer-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-even-ai-timer-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "86163bcb5b085691627761d6af0b3d007c0f9eb44d3cdb5f735553528c34463b",
    CLOSURE: "6a9425e8ddbdb1e4a92a59c52f9365400fc17d64a2c39de5b095f1fcf69095c3",
    PROVIDER_MAP: "2cd525d04256e895bdffd399c851f4feec4a672c27074bc6da2989fb9316cb6e",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\even_ai_timer.c"
PATH_RUN = 0x0070_26E0
PATH_POINTER_CELLS = [0x004E_3134]
FUNCTIONS = (
    (0x004E_2E10, 0x004E_2E62),
    (0x004E_2E62, 0x004E_2E86),
    (0x004E_2E86, 0x004E_2ED2),
    (0x004E_2ED2, 0x004E_2EFE),
    (0x004E_2EFE, 0x004E_3006),
    (0x004E_3006, 0x004E_304C),
    (0x004E_304C, 0x004E_306E),
    (0x004E_306E, 0x004E_30B4),
    (0x004E_30B4, 0x004E_30E0),
    (0x004E_30E0, 0x004E_3130),
    (0x004E_3194, 0x004E_31A0),
    (0x004E_31A0, 0x004E_31B0),
    (0x004E_31B0, 0x004E_31CC),
)
PHYSICAL = (0x004E_2E10, 0x004E_31CC)
PHYSICAL_SHA256 = "6248c309f6df62a7630620f260c5b1e753c5a14d121ad293b6eabaddac2eab3c"
BODY_BYTES = 856
BODY_SHA256 = "592e0bf2d3f258143e7a5bedfd3121f2c8e67ce0e6f562f6a1bf3835229e1860"
INSTRUCTION_COUNT = 350
INSTRUCTION_DIGEST = "3410765ccaececd5f82699561e2d4bbf714bcd850059959bb988f098e6fef606"
POOL = (0x004E_3130, 0x004E_3194)
POOL_SHA256 = "867f182d14f37a7cc2be9079892073292a5856b1713b89274d1e59856a4db132"
PRECEDING_TAIL = (0x004E_2DF0, 0x004E_2E10)
PRECEDING_TAIL_SHA256 = "2be148fcbb7e1693e5ca8d1dedd31337853ca2ed799e0e8670deb4d468cc926e"
FOLLOWING_HEAD = (0x004E_31CC, 0x004E_31D4)
FOLLOWING_HEAD_SHA256 = "78ec779a868b0713014f60dd6f1e7454ac81b8945f0041231b772d1da4e72cb0"

ENTRY_COUNT = 28
EXTERNAL_ENTRY_COUNT = 16
ENTRY_DIGEST = "d94c22f336915cdf2209e80302f658e9548da768434af078fc864950302f4bbd"
CALL_COUNT = 57
INTERNAL_CALL_COUNT = 12
CALL_DIGEST = "be8a63ccc8ec8cecbae69847801809575bc143a986b46487d038620724cc4ea2"
EXTERNAL_TARGET_COUNTS = {
    0x0043_C0E4: 1,
    0x0043_CE9E: 6,
    0x0043_D0CE: 18,
    0x0043_D574: 6,
    0x0044_90CC: 4,
    0x0045_A568: 4,
    0x0046_4F76: 2,
    0x0049_832E: 3,
    0x0049_8528: 1,
}
ENTRIES = [
    (0x0049_7EAC, 0x004E_304C),
    (0x004E_21E8, 0x004E_31A0),
    (0x004E_21FA, 0x004E_31A0),
    (0x004E_2290, 0x004E_2E86),
    (0x004E_22B8, 0x004E_2E86),
    (0x004E_23B0, 0x004E_31A0),
    (0x004E_25FE, 0x004E_31A0),
    (0x004E_27D2, 0x004E_31A0),
    (0x004E_292C, 0x004E_31A0),
    (0x004E_2BD2, 0x004E_31A0),
    (0x004E_2BE6, 0x004E_31A0),
    (0x004E_2CC0, 0x004E_31B0),
    (0x004E_2D2C, 0x004E_3194),
    (0x004E_2F40, 0x004E_2E86),
    (0x004E_2F72, 0x004E_2E62),
    (0x004E_2FD8, 0x004E_2E62),
    (0x004E_3122, 0x004E_306E),
    (0x004E_3196, 0x004E_2E10),
    (0x004E_319A, 0x004E_3006),
    (0x004E_31A2, 0x004E_2E62),
    (0x004E_31AA, 0x004E_304C),
    (0x004E_31B2, 0x004E_2ED2),
    (0x004E_31BA, 0x004E_2EFE),
    (0x004E_31BE, 0x004E_30B4),
    (0x004E_31C6, 0x004E_30E0),
    (0x004E_58EE, 0x004E_2E62),
    (0x004E_5940, 0x004E_2E62),
    (0x004E_5E2A, 0x004E_2E10),
]
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0078_5DF0: "even_ai.timer",
    0x0075_FE30: "even_ai_common_timer_mgr_deinit",
    0x0073_3EE4: "[even_ai.timer]even_ai_common_timer_mgr_deinit",
    0x0075_FE70: "even_ai_common_timer_mgr_stop",
    0x0073_3F14: "[even_ai.timer]even_ai_common_timer_mgr_stop",
    0x0073_EB88: "even_ai_common_timer: processing timeout",
    0x0073_EB5C: "even_ai_common_timer_mgr_process_timeout",
    0x0071_EC68: "[even_ai.timer]even_ai_common_timer: processing timeout",
    0x0075_447C: "even_ai_heartbeat_timer_mgr_deinit",
    0x0072_95C0: "[even_ai.timer]even_ai_heartbeat_timer_mgr_deinit",
    0x0075_44C4: "even_ai_heartbeat_timer_mgr_stop",
    0x0073_3F44: "[even_ai.timer]even_ai_heartbeat_timer_mgr_stop",
    0x0073_EBE0: "even_ai_heartbeat_timer: processing timeout",
    0x0073_EBB4: "even_ai_heartbeat_timer_mgr_process_timeout",
    0x0071_4CB0: "[even_ai.timer]even_ai_heartbeat_timer: processing timeout",
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _all_word_hits(blob: bytes, values: set[int]) -> list[tuple[int, int]]:
    hits = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value & 1 and (value & ~1) in values:
            hits.append((common.BASE + offset, value & ~1))
    return hits


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != common.IMAGE_SIZE or _sha256(blob) != common.IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    if (
        easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"
        or cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]
        != "d213f261b5be6bb29a7cce8b84071706b72f4d53"
        or cmsis["upstreams"]["cmsis_5"]["selected_commit"]
        != "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c"
    ):
        raise AuditError("EasyLogger or CMSIS-FreeRTOS source selection changed")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        providers = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != len(FUNCTIONS) or len(providers) != 4:
        raise AuditError("function or provider inventory changed")
    if sum(int(row["edges"].split()[0]) for row in providers) != 45:
        raise AuditError("provider edge accounting changed")

    starts: set[int] = set()
    interiors: set[int] = set()
    bodies: list[bytes] = []
    all_instructions: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    indirect: list[int] = []
    anchored = 0
    for row, expected_bounds in zip(rows, FUNCTIONS):
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        if (start, end) != expected_bounds or start in starts:
            raise AuditError("function bounds changed")
        body = common._slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function changed: {row['function']}")
        recovered, function_calls, function_indirect = indirect_common._recover_function(blob, start, end)
        if common._uncovered((start, end), recovered):
            raise AuditError(f"function contains uncovered bytes: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        bodies.append(body)
        all_instructions.update(recovered)
        calls.extend(function_calls)
        indirect.extend(function_indirect)
        anchored += row["source_path_anchor"] == "yes"

    calls.sort()
    instruction_pairs = sorted((address, insn.size) for address, insn in all_instructions.items())
    code = b"".join(
        common._slice(blob, address, address + insn.size)
        for address, insn in sorted(all_instructions.items())
    )
    if (
        anchored != 2
        or sum(map(len, bodies)) != BODY_BYTES
        or _sha256(b"".join(bodies)) != BODY_SHA256
        or code != b"".join(bodies)
        or len(all_instructions) != INSTRUCTION_COUNT
        or common._instruction_digest(instruction_pairs) != INSTRUCTION_DIGEST
        or indirect
    ):
        raise AuditError("body, instruction, anchor, or indirect-call closure changed")
    if len(common._slice(blob, *PHYSICAL)) != 956 or _sha256(common._slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical EvenAI timer object changed")
    if len(common._slice(blob, *POOL)) != 100 or _sha256(common._slice(blob, *POOL)) != POOL_SHA256:
        raise AuditError("EvenAI timer literal pool changed")
    for bounds, expected, label in (
        (PRECEDING_TAIL, PRECEDING_TAIL_SHA256, "preceding EvenAI object tail"),
        (FOLLOWING_HEAD, FOLLOWING_HEAD_SHA256, "following protobuf-service head"),
    ):
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} changed")

    external_counts = Counter(target for _, target in calls if target not in starts)
    if (
        len(calls) != CALL_COUNT
        or common._pair_digest(calls) != CALL_DIGEST
        or sum(target in starts for _, target in calls) != INTERNAL_CALL_COUNT
        or dict(external_counts) != EXTERNAL_TARGET_COUNTS
    ):
        raise AuditError("direct call topology changed")

    decoded_entries: list[tuple[int, int]] = []
    strict_interiors: list[tuple[int, int]] = []
    for address in range(common.BASE, common.BASE + len(blob) - 3, 2):
        target = thumb._thumb_bl_target(blob, address)
        if target in starts:
            decoded_entries.append((address, target))
        elif target in interiors:
            strict_interiors.append((address, target))
    if decoded_entries != ENTRIES or len(decoded_entries) != ENTRY_COUNT or common._pair_digest(decoded_entries) != ENTRY_DIGEST:
        raise AuditError("direct BL ingress changed")
    if strict_interiors:
        raise AuditError("raw BL now targets a strict function interior")
    if _all_word_hits(blob, starts) or _all_word_hits(blob, interiors):
        raise AuditError("stored entry or strict-interior pointer appeared")

    for address, expected in STRINGS.items():
        if common._c_string(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")
    path_word = struct.pack("<I", PATH_RUN)
    path_hits, cursor = [], blob.find(path_word)
    while cursor >= 0:
        path_hits.append(common.BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if path_hits != PATH_POINTER_CELLS:
        raise AuditError("retained-path pointer census changed")
    if thumb.literal_references(blob, PATH_POINTER_CELLS[0]) != [
        0x004E_2E34, 0x004E_2EAA, 0x004E_2F1A,
        0x004E_3024, 0x004E_308C, 0x004E_30FC,
    ]:
        raise AuditError("retained-path literal references changed")

    # Pin the two 12-byte private timer records and the exact unsigned-expiry
    # machinery: start writes tick/duration/state/armed, while check subtracts
    # the saved tick and compares unsigned before writing state 2/armed 0.
    if struct.unpack_from("<I", blob, 0x004E_3130 - common.BASE)[0] != 0x2007_4008:
        raise AuditError("common timer record moved")
    if struct.unpack_from("<I", blob, 0x004E_316C - common.BASE)[0] != 0x2007_4014:
        raise AuditError("heartbeat timer record moved")
    for site in (0x004E_2E74, 0x004E_2EE0, 0x004E_305C, 0x004E_30C2):
        if thumb._thumb_bl_target(blob, site) != 0x0044_90CC:
            raise AuditError("osKernelGetTickCount seam changed")
    if common._slice(blob, 0x004E_31A6, 0x004E_31AA) != bytes.fromhex("42f21070"):
        raise AuditError("fixed 10000-tick heartbeat interval changed")
    if common._slice(blob, 0x004E_2F6E, 0x004E_2F72) != bytes.fromhex("40f6b830"):
        raise AuditError("fixed 3000-tick common restart changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no hardware or flash operation",
        "identity": {
            "image_sha256": common.IMAGE_SHA256,
            "retained_path": RETAINED_PATH,
            "path_run": PATH_RUN,
            "path_pointer_cells": PATH_POINTER_CELLS,
            "physical_interval": [*PHYSICAL],
            "physical_sha256": PHYSICAL_SHA256,
            "body_sha256": BODY_SHA256,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": len(FUNCTIONS),
            "ghidra_discovered_functions": 3,
            "additional_recovered_functions": 10,
            "path_anchored_functions": anchored,
            "body_bytes": BODY_BYTES,
            "reachable_instruction_bytes": len(code),
            "outer_pool_regions": 1,
            "outer_pool_bytes": 100,
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "direct_bl_entry_sites": len(decoded_entries),
            "external_direct_bl_entry_sites": EXTERNAL_ENTRY_COUNT,
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": INTERNAL_CALL_COUNT,
            "external_direct_body_calls": len(calls) - INTERNAL_CALL_COUNT,
            "indirect_body_calls": 0,
            "stored_entry_pointers": 0,
            "strict_interior_raw_bl_decodes": 0,
            "unrecovered_direct_object_targets": 0,
        },
        "behavior": {
            "common_timer_record": 0x2007_4008,
            "heartbeat_timer_record": 0x2007_4014,
            "timer_record_bytes": 12,
            "record_fields": {"start_tick": 0, "duration_ticks": 4, "state": 8, "armed": 9},
            "expiry_arithmetic": "unsigned (current_tick - start_tick) >= duration_ticks",
            "heartbeat_default_ticks": 10_000,
            "common_restart_ticks": 3_000,
            "uses_cmsis_software_timers": False,
        },
        "provider_boundary": {
            "direct_external_calls": 45,
            "easylogger_calls": 30,
            "cmsis_freertos_tick_calls": 4,
            "iar_dlib_calls": 1,
            "first_party_calls": 10,
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "cmsis_5_commit": "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c",
            "new_version_discriminator": False,
        },
        "production": {
            "production_routed": False,
            "qualification": "behavior and provider seams are recovered; the private EvenAI object is not yet source-routed",
        },
    }


def main() -> int:
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
