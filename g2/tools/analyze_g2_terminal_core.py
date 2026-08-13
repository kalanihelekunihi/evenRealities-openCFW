#!/usr/bin/env python3
"""Fail-closed linked-object and provider audit for G2 terminal.c."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb


AuditError = common.AuditError
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-terminal-core-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-terminal-core-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-terminal-core-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "f1bd2ba8bb8f97caefd831a80c12b9a56871f1c53dfb8ac7f9742219a0dcc71b",
    CLOSURE: "fc63960c5371de00f19f42e864189a20944eb61604e9fdd176138a96ecddec7f",
    PROVIDER_MAP: "d058a37a6922fcdb6f2dcf078c85e8226adc4e1d83013b6bbbdc432aa5eb6658",
}
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\terminal\terminal.c"
PATH_RUN = 0x0070_FEA4
PATH_POINTER_CELLS = [0x005E_4778]
PHYSICAL = (0x005E_42EC, 0x005E_47CC)
PHYSICAL_SHA256 = "581cc1dcd075efda58d4a18c7def2e8bbf928b6ec12937b7470b6a679c2d80bf"
BODY_BYTES = 1_144
BODY_SHA256 = "507e4a96bafe3b5ea6e7de64e98c21cd903cc609beacec11a8308ad2205c0414"
INSTRUCTION_COUNT = 460
INSTRUCTION_DIGEST = "f4b030bb6a55167d48501f2cdee59bee27939f93731ac278e4c5e33d35562814"
OUTER_POOL = (0x005E_4764, 0x005E_47CC)
OUTER_POOL_SHA256 = "82ed65fd51b24400f5fb800359d7ea1950cc688ea635cc7b5cfb4d2cc00d53c4"
PRECEDING_FUNCTION = (0x005E_42DC, 0x005E_42EC)
PRECEDING_FUNCTION_SHA256 = "096ce5c4f9be89f1e5645cd8d564855d95efb7ef575806f8eeca5baeaa72586f"
FOLLOWING_FUNCTION = (0x005E_47CC, 0x005E_47FE)
FOLLOWING_FUNCTION_SHA256 = "b3c87d81e7f108f1ca53dd05c83836f2d9dd9a4bb7cc7609bf6f3fc2cb96ddef"
ENTRY_COUNT = 68
EXTERNAL_ENTRY_COUNT = 60
ENTRY_SHA256 = "0486e1f8c300c8b56c1c40db514b6ad280dadef244694a26fe32729f714f4e31"
CALL_COUNT = 73
INTERNAL_CALL_COUNT = 8
CALL_SHA256 = "51f63407a3d1e68ac5d864d2a9fd143bdfb4748eb942bce6b9ca776675812871"
STORED = [
    (0x006A_46B4, 0x005E_4489),
    (0x006A_46B8, 0x005E_44F7),
    (0x0079_3F87, 0x005E_444D),
]
STORED_SHA256 = "568b4e27451beae452cd2a1847b9c1fc18e53d6dbe0104c2e87e1a01795545e0"
EXTERNAL_TARGET_COUNTS = {
    0x0043_9BE4: 1,
    0x0043_C0E4: 2,
    0x0043_CE9E: 6,
    0x0043_D0CE: 18,
    0x0043_D574: 6,
    0x0044_971C: 1,
    0x0044_97B6: 1,
    0x0044_981C: 1,
    0x0045_A568: 1,
    0x0046_4BB2: 1,
    0x0046_C630: 1,
    0x0047_8110: 1,
    0x004A_BCC6: 1,
    0x0058_C238: 1,
    0x005C_E990: 1,
    0x005C_EAEC: 3,
    0x005C_EBA2: 1,
    0x005E_716C: 1,
    0x005E_720C: 1,
    0x005E_7324: 1,
    0x005E_7B74: 2,
    0x005E_8008: 1,
    0x005E_A028: 12,
}
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0075_B2E0: "terminal action mutex create failed",
    0x0075_B2BC: "terminal_action_mutex_init_internal",
    0x0078_C518: "terminal",
    0x0073_95E4: "[terminal]terminal action mutex create failed",
    0x0072_E970: "terminal is not initialized, ignore display request",
    0x0077_2F64: "terminal_request_display",
    0x0070_FEE4: "[terminal]terminal is not initialized, ignore display request",
    0x0077_2F9C: "terminal display startup",
    0x0077_2F80: "Terminal_ui_event_handler",
    0x0075_B304: "[terminal]terminal display startup",
    0x0077_C61C: "terminal display exit",
    0x0076_61F0: "[terminal]terminal display exit",
    0x0074_F3D4: "ignore terminal query reply from app",
    0x0077_2FB8: "terminal_data_recv_handler",
    0x0073_9614: "[terminal]ignore terminal query reply from app",
    0x0075_B328: "unsupported terminal command id=%d",
    0x0073_9644: "[terminal]unsupported terminal command id=%d",
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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
        or cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53"
    ):
        raise AuditError("provider commit changed")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        provider_rows = list(csv.DictReader(handle, delimiter="\t"))
    provider_edges = sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows)
    if len(rows) != 9 or len(provider_rows) != 4 or provider_edges != 65:
        raise AuditError("function or provider inventory changed")

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
        anchored != 1
        or sum(map(len, bodies)) != BODY_BYTES
        or _sha256(b"".join(bodies)) != BODY_SHA256
        or outer_bounds != [OUTER_POOL]
        or _sha256(outer_bytes) != OUTER_POOL_SHA256
    ):
        raise AuditError("body, anchor, or pool inventory changed")
    if len(common._slice(blob, *PHYSICAL)) != 1_248 or _sha256(common._slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical terminal object changed")
    for bounds, expected, label in (
        (PRECEDING_FUNCTION, PRECEDING_FUNCTION_SHA256, "preceding startup function"),
        (FOLLOWING_FUNCTION, FOLLOWING_FUNCTION_SHA256, "following terminal-ui function"),
    ):
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} changed")

    all_instructions: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    embedded: list[tuple[int, int]] = []
    for interval in intervals:
        recovered, function_calls = common._recover_function(blob, *interval)
        all_instructions.update(recovered)
        calls.extend(function_calls)
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
    external_counts = Counter(target for _, target in calls if target not in starts)
    if (
        len(calls) != CALL_COUNT
        or common._pair_digest(calls) != CALL_SHA256
        or sum(target in starts for _, target in calls) != INTERNAL_CALL_COUNT
        or dict(external_counts) != EXTERNAL_TARGET_COUNTS
    ):
        raise AuditError("call topology changed")

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
        raise AuditError("stored callback topology changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = "terminal_action_mutex_init_internal" in json.dumps(overlay).lower()
    if routed:
        raise AuditError("terminal core unexpectedly became production-routed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object, callback, and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_terminal_display_lifecycle_and_command_routing",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 9,
            "ghidra_discovered_functions": 1,
            "additional_recovered_functions": 8,
            "path_anchored_functions": anchored,
            "baseline_ghidra_path_anchors": 1,
            "body_bytes": len(code),
            "reachable_instruction_bytes": len(code),
            "embedded_data_regions": 0,
            "outer_pool_regions": len(outer_bounds),
            "outer_pool_bytes": len(outer_bytes),
            "physical_bytes": 1_248,
            "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": INTERNAL_CALL_COUNT,
            "external_direct_body_calls": sum(external_counts.values()),
            "indirect_body_calls": 0,
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "behavior": {
            "terminal_display_request_message_id": 0x30,
            "terminal_display_request_bytes": 8,
            "role_gate": "local role value equals one",
            "input_event_ids": [0x08, 0x0A, 0x44, 0x45, 0x48, 0x4A],
            "swapped_input_event_pair": [0x44, 0x45],
            "terminal_command_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0xA3, 0xFF],
            "terminal_command_dispatch_provider_calls": 12,
            "mutex_timeout": "osWaitForever",
            "stored_callbacks": ["terminal_ui_input_filter", "terminal_query_reply_handler", "Terminal_ui_event_handler"],
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows),
            "direct_external_targets": len(external_counts),
            "direct_external_calls": sum(external_counts.values()),
            "easylogger": {"calls": 30, "selected_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"},
            "cmsis_freertos": {"calls": 3, "version": "v10.5.1", "selected_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53", "production_source_owned": True},
            "iar_dlib_calls": 3,
            "g2_first_party_calls": 29,
            "nanopb_direct_calls": 0,
            "new_version_discriminator": False,
            "assessment": "no opaque third-party definition is embedded",
        },
        "boundary": {
            "physical_start": "0x005e42ec",
            "physical_end_exclusive": "0x005e47cc",
            "path_pointer_cells": ["0x005e4778"],
            "preceded_by": "runtime startup loop",
            "followed_by": "terminal_ui.c style helper",
        },
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "the private source and producing commit remain unavailable",
            "four semantic helper/callback names remain provisional",
            "terminal protobuf schemas and screen implementations are separate first-party objects",
            "no new dependency-version discriminator is present",
            "target display, role, and command-routing validation are required before production admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 terminal-core audit: PASS")
