#!/usr/bin/env python3
"""Fail-closed object/provider audit for G2 text_stream_service.c."""
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
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_dashboard_watchface_manager as indirect_common
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb


AuditError = common.AuditError
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-text-stream-service-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-text-stream-service-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-text-stream-service-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "2f2ec5c419b150913dc285cf97d23f164a9c62746403aef0654e2f4b1d3f1d61",
    CLOSURE: "6c552fe4fc2bd351113bb1c3e8168d0ddd9ac53f3873b9e9902e2a8f3c6c1e39",
    PROVIDER_MAP: "2404a773d0bb73d8c992ae9ea2d3653c60505ec26c7bf80e3489a21b88b4f0a5",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\text_stream_service.c"
PATH_RUN = 0x006F_6C50
PATH_POINTER_CELLS = [0x0055_33B4]
PHYSICAL = (0x0055_2B30, 0x0055_37CC)
PHYSICAL_SHA256 = "b607d79a5dd360049f8a4ea11bd8131537a07d79b34f3660e2d65358d407915b"
BODY_BYTES = 3_188
BODY_SHA256 = "aff2cdcd232a1448c2b3c400320ebab37f252036813779e5f0f09f036bfdc099"
INSTRUCTION_COUNT = 1_361
INSTRUCTION_DIGEST = "a789dd3a68710debb52f96c5b2b26d6e9798e462b412d0678d259b1aed78135e"
OUTER_POOLS = [
    (0x0055_2CF4, 0x0055_2CF8),
    (0x0055_3050, 0x0055_3054),
    (0x0055_33AC, 0x0055_33CC),
]
OUTER_POOL_SHA256 = "95ee13b37b9447ed7613c37757f162eb9da45a8d645b1ec4510576bb68afcd00"
PRECEDING_OBJECT_TAIL = (0x0055_2AB0, 0x0055_2B30)
PRECEDING_OBJECT_TAIL_SHA256 = "b2f65417b675b5d0040c972e850c505f8520b722fd44eab3f2ba89ea76184ffe"
FOLLOWING_FUNCTION = (0x0055_37CC, 0x0055_389A)
FOLLOWING_FUNCTION_SHA256 = "b6dfaafe03a917a7e1648d716ba4de8286e6ff4cb41b7336979f301b9f326f5e"

ENTRY_COUNT = 65
EXTERNAL_ENTRY_COUNT = 34
ENTRY_SHA256 = "8f4fbb732c47bd30b51792b18a223065b9b51a14ea6ec50773e946c088c678f7"
CALL_COUNT = 144
INTERNAL_CALL_COUNT = 31
CALL_SHA256 = "6cb7294e4a2e7c7e0bd9cd90cbf273f0f3a6805c84ce2386acfc29f480a23008"
INDIRECT_SITES = [
    0x0055_2E28,
    0x0055_2E92,
    0x0055_2F54,
    0x0055_2FA4,
    0x0055_3172,
    0x0055_3270,
    0x0055_32F4,
]
INDIRECT_SHA256 = "c2922fb0d53fa5a25ae8ba28a4a27e399a2eb461a52937d4c22791a819ed18a9"
CALLBACK_CONSTRUCTIONS = [(0x0055_2FD0, 0x0055_3055)]
CALLBACK_CONSTRUCTION_SHA256 = "d3293d92010ebe89279b2db0562d6fef4ca5b977691ed0561c4a5011b62d772d"
STORED: list[tuple[int, int]] = []
STORED_SHA256 = hashlib.sha256(b"").hexdigest()
EXTERNAL_TARGET_COUNTS = {
    0x0043_9BE4: 7,
    0x0043_C0E4: 3,
    0x0043_CE9E: 2,
    0x0043_D0CE: 6,
    0x0043_D574: 2,
    0x0043_DED4: 4,
    0x0044_104C: 1,
    0x0044_120E: 1,
    0x0044_121C: 1,
    0x0044_122A: 5,
    0x0044_1238: 5,
    0x0044_93B0: 1,
    0x0044_9498: 2,
    0x0044_94D8: 7,
    0x0044_953E: 2,
    0x0044_971C: 1,
    0x0044_97B6: 10,
    0x0044_981C: 13,
    0x0044_986E: 3,
    0x0044_A43C: 7,
    0x0044_B5A0: 1,
    0x0046_3C68: 4,
    0x0046_3E1C: 1,
    0x0046_3E9A: 5,
    0x0046_CACC: 1,
    0x0047_4CD2: 1,
    0x0047_4D16: 7,
    0x0047_4D54: 1,
    0x0048_949C: 5,
    0x0048_D540: 3,
    0x0056_7C80: 1,
}
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0076_6730: "create animation timer failed",
    0x0078_9980: "animate_text",
    0x0078_4108: "text_stream_service",
    0x0072_EF20: "[text_stream_service]create animation timer failed",
    0x0077_CAE4: "newText realloc failed",
    0x0077_CACC: "ensure_text_capacity",
    0x0074_5174: "[text_stream_service]newText realloc failed",
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
    nanopb = json.loads((ROOT / "third_party/nanopb/PROVENANCE.json").read_text())
    lvgl = json.loads((ROOT / "third_party/lvgl/PROVENANCE.json").read_text())
    tlsf_note = (ROOT / "third_party/tlsf/README.openCFW.md").read_text()
    if (
        easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"
        or cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53"
        or nanopb["upstream"]["selected_commit"] != "98bf4db69897b53434f3d0ba72e0a3ab1a902824"
        or lvgl["upstream"]["selected_commit"] != "344c7c318047b7348e1be8572a9fd4260c251cfa"
        or "deff9ab509341f264addbd3c8ada533678591905" not in tlsf_note
        or "a1f743ffac0305408b39e791e0ffb45f6d9bc777" not in tlsf_note
    ):
        raise AuditError("provider commit or source-equivalence boundary changed")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        provider_rows = list(csv.DictReader(handle, delimiter="\t"))
    provider_edges = sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows)
    if len(rows) != 26 or len(provider_rows) != 8 or provider_edges != 113:
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
        or outer_bounds != OUTER_POOLS
        or _sha256(outer_bytes) != OUTER_POOL_SHA256
    ):
        raise AuditError("body, anchor, or pool inventory changed")
    if len(common._slice(blob, *PHYSICAL)) != 3_228 or _sha256(common._slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical text-stream-service object changed")
    for bounds, expected, label in (
        (PRECEDING_OBJECT_TAIL, PRECEDING_OBJECT_TAIL_SHA256, "preceding message-notification tail"),
        (FOLLOWING_FUNCTION, FOLLOWING_FUNCTION_SHA256, "following even-ai-animation function"),
    ):
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} changed")

    all_instructions: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    indirect: list[int] = []
    embedded: list[tuple[int, int]] = []
    for interval in intervals:
        recovered, function_calls, function_indirect = indirect_common._recover_function(blob, *interval)
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
    if indirect != INDIRECT_SITES or indirect_common._address_digest(indirect) != INDIRECT_SHA256:
        raise AuditError("indirect callback topology changed")
    if common._slice(blob, 0x0055_2FD0, 0x0055_2FD4) != bytes.fromhex("0ff28100"):
        raise AuditError("PC-relative animate_text callback construction changed")
    if common._pair_digest(CALLBACK_CONSTRUCTIONS) != CALLBACK_CONSTRUCTION_SHA256:
        raise AuditError("callback construction manifest changed")

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

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = "text_stream_service" in json.dumps(overlay).lower()
    if routed:
        raise AuditError("text stream service unexpectedly became production-routed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object, callback, and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_even_ai_utf8_text_stream_and_animation_preset_policy",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 26,
            "ghidra_discovered_functions": 8,
            "additional_recovered_functions": 18,
            "path_anchored_functions": anchored,
            "baseline_ghidra_path_anchors": 1,
            "body_bytes": len(code),
            "reachable_instruction_bytes": len(code),
            "embedded_data_regions": 0,
            "outer_pool_regions": len(outer_bounds),
            "outer_pool_bytes": len(outer_bytes),
            "physical_bytes": 3_228,
            "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": INTERNAL_CALL_COUNT,
            "external_direct_body_calls": sum(external_counts.values()),
            "indirect_body_calls": len(indirect),
            "pc_relative_callback_constructions": len(CALLBACK_CONSTRUCTIONS),
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "behavior": {
            "service_struct_bytes": 0x30,
            "initial_text_capacity_bytes": 0x200,
            "default_animation_period_ticks": 100,
            "buffer_policy": "two growable NUL-terminated current and pending UTF-8 buffers",
            "capacity_growth": "double existing capacity or use requested minimum",
            "animation_unit": "one complete UTF-8 code point per timer tick",
            "utf8_code_point_widths": [1, 2, 3, 4],
            "callback_field_offset": 0x18,
            "callback_dispatch_sites": len(indirect),
            "animation_timer_callback": "0x00553055 animate_text Thumb entry",
            "animation_presets": 4,
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows),
            "direct_external_targets": len(external_counts),
            "direct_external_calls": sum(external_counts.values()),
            "easylogger_calls": 10,
            "cmsis_freertos": {"calls": 39, "version": "v10.5.1", "selected_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53", "production_source_owned": True},
            "lvgl": {"calls": 17, "version": "9.3.0-compatible interval", "selected_ceiling_commit": "344c7c318047b7348e1be8572a9fd4260c251cfa"},
            "nanopb": {"calls": 5, "selected_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824"},
            "tlsf_allocator_wrappers": {"calls": 9, "selected_commit": "deff9ab509341f264addbd3c8ada533678591905"},
            "iar_dlib_calls": 22,
            "g2_first_party_calls": 11,
            "new_version_discriminator": False,
            "assessment": "no opaque third-party definition is embedded",
        },
        "boundary": {
            "physical_start": "0x00552b30",
            "physical_end_exclusive": "0x005537cc",
            "path_pointer_cells": ["0x005533b4"],
            "preceded_by": "message-notification timer object tail and pool",
            "followed_by": "even_ai_animation.c first function",
        },
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "the private source and producing commit remain unavailable",
            "semantic names other than animate_text and ensure_text_capacity are provisional",
            "seven runtime callback invocations depend on the callback supplied by the caller",
            "the exact G2 LVGL, nanopb, TLSF, and IAR generating checkouts remain bounded rather than proven",
            "target UI timing and lifecycle validation are required before production admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 text-stream-service audit: PASS")
