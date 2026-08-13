#!/usr/bin/env python3
"""Fail-closed linked-object and provider audit for G2 health.c."""
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
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb


AuditError = common.AuditError
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-health-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-health-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-health-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "3e8e71032fdd6f8c53dc7808fc9d1cdf622ba176cbbf051bd5b03d49d6bfe78c",
    CLOSURE: "59829d1378b502e3112284d29db94cd055adb4a39e9933c5e4dcbdca6e1bcdbe",
    PROVIDER_MAP: "04570cfee3f6a964a9995d92a90ccd8e64ea7e8dc3efe3e5e2e3b3843a3f01af",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\health\health.c"
PATH_RUN = 0x0071_58E0
PATH_POINTER_CELLS = [0x004F_FDDC]
PHYSICAL = (0x004F_FBD8, 0x004F_FE14)
PHYSICAL_SHA256 = "e8407d029614793fe55708cd7fd814bfd01f845b4d2608ce46dc357115d9f179"
BODY_BYTES = 504
BODY_SHA256 = "f6306371340e0e19606c34c2a93dc8aeeef28c5456ad337ff3b66a4ba44d25b1"
INSTRUCTION_COUNT = 209
INSTRUCTION_DIGEST = "ccb8ec08b3fc502f9bf357ec9c2d02ff90f5435ef36e7dcef29f2511eea5a0bf"
POOL = (0x004F_FDD0, 0x004F_FE14)
POOL_SHA256 = "a5c65d7291dbe522690532d0b97c1af866e0dc0d1cb7464b80b40d31b101b8c7"
PRECEDING_FUNCTION = (0x004F_FAC8, 0x004F_FB38)
PRECEDING_FUNCTION_SHA256 = "4197720b21e052a462b1f50a5221c2a374a3087ec1bfc3ca3c19272e72bb67a4"
PRECEDING_POOL = (0x004F_FB38, 0x004F_FBD8)
PRECEDING_POOL_SHA256 = "cf57d082dea418e840b65e1ed8b8ff3523f921c0372631cca17da6df83204eb9"
FOLLOWING_FUNCTION = (0x004F_FE14, 0x004F_FEB4)
FOLLOWING_FUNCTION_SHA256 = "447dd30df4bbd52e21829eb388b4af58d919f05a2dfc75a25e83538bc310a383"

ENTRY_COUNT = 58
EXTERNAL_ENTRY_COUNT = 57
ENTRY_SHA256 = "2a918441945c501b62209b68dd14cf8a6ab4f3074ea5549a6fc1aa118e92ca40"
CALL_COUNT = 34
INTERNAL_CALL_COUNT = 1
CALL_SHA256 = "bf9004a6055c909275d637870a3c6adb0313decd1dab96cb1bbafb27b935b85b"
STORED = [(0x006A_4544, 0x004F_FCA3)]
STORED_SHA256 = "6c82f581e920988fb83180feae804e5387802acf74f9cc123acbd226a3108684"
EXTERNAL_TARGET_COUNTS = {
    0x0043_CE9E: 5,
    0x0043_D0CE: 15,
    0x0043_D574: 5,
    0x0044_3484: 1,
    0x0044_34D0: 1,
    0x0044_971C: 1,
    0x0044_97B6: 1,
    0x0044_981C: 1,
    0x0045_A568: 1,
    0x0046_4BB2: 1,
    0x0055_A350: 1,
}
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0074_A3D4: "Failed to create health storage mutex",
    0x0077_79CC: "health_data_mutex_init",
    0x0078_AB14: "health.page",
    0x0078_6090: "mutex is NULL",
    0x0077_F734: "health_lock_storage",
    0x0077_79E4: "Invalid raw_data or len",
    0x0076_BCFC: "Health_common_data_handler",
    0x0077_F748: "Unknown command: %d",
    0x0077_79FC: "Unknown event type: %d",
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
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise AuditError("EasyLogger provider commit changed")
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise AuditError("CMSIS-FreeRTOS provider commit changed")
    nanopb = json.loads((ROOT / "third_party/nanopb/PROVENANCE.json").read_text())
    if nanopb["upstream"]["selected_commit"] != "98bf4db69897b53434f3d0ba72e0a3ab1a902824":
        raise AuditError("nanopb compatibility commit changed")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        provider_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 4 or len(provider_rows) != 4:
        raise AuditError("function or provider inventory changed")
    if sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows) != 33:
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
            outer_gaps.append(common._slice(blob, previous_end, start))
        body = common._slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(body)
        anchored += row["source_path_anchor"] == "yes"
        previous_end = end
    if previous_end < PHYSICAL[1]:
        outer_gaps.append(common._slice(blob, previous_end, PHYSICAL[1]))
    if anchored != 3 or sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function-body or path-anchor inventory changed")
    if outer_gaps != [common._slice(blob, *POOL)] or _sha256(outer_gaps[0]) != POOL_SHA256:
        raise AuditError("compiler pool changed")
    if len(common._slice(blob, *PHYSICAL)) != 572 or _sha256(common._slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical health object changed")
    for bounds, expected, label in (
        (PRECEDING_FUNCTION, PRECEDING_FUNCTION_SHA256, "preceding quicklist function"),
        (PRECEDING_POOL, PRECEDING_POOL_SHA256, "preceding quicklist pool"),
        (FOLLOWING_FUNCTION, FOLLOWING_FUNCTION_SHA256, "following page-state function"),
    ):
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} boundary changed")

    all_instructions: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    embedded: list[tuple[int, int]] = []
    for interval in intervals:
        recovered, function_calls = common._recover_function(blob, *interval)
        all_instructions.update(recovered)
        calls.extend(function_calls)
        embedded.extend(common._uncovered(interval, recovered))
    instruction_pairs = sorted((address, instruction.size) for address, instruction in all_instructions.items())
    code = b"".join(common._slice(blob, address, address + instruction.size) for address, instruction in sorted(all_instructions.items()))
    if len(all_instructions) != INSTRUCTION_COUNT or common._instruction_digest(instruction_pairs) != INSTRUCTION_DIGEST or len(code) != BODY_BYTES or _sha256(code) != BODY_SHA256 or embedded:
        raise AuditError("recursive instruction closure changed")
    calls.sort()
    if len(calls) != CALL_COUNT or common._pair_digest(calls) != CALL_SHA256:
        raise AuditError("body-call topology changed")
    if sum(target in starts for _, target in calls) != INTERNAL_CALL_COUNT:
        raise AuditError("internal call census changed")
    external_counts = Counter(target for _, target in calls if target not in starts)
    if dict(external_counts) != EXTERNAL_TARGET_COUNTS:
        raise AuditError(f"provider target accounting changed: {external_counts!r}")

    for address, expected in STRINGS.items():
        if common._c_string(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    path_word = struct.pack("<I", PATH_RUN)
    path_hits, cursor = [], blob.find(path_word)
    while cursor >= 0:
        path_hits.append(common.BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if path_hits != PATH_POINTER_CELLS:
        raise AuditError(f"source-path pointer topology changed: {path_hits!r}")

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
    if len(entries) != ENTRY_COUNT or common._pair_digest(entries) != ENTRY_SHA256 or external_entries != EXTERNAL_ENTRY_COUNT or strict or unknown:
        raise AuditError("entry/interior topology changed")

    encoded_starts = starts | {start | 1 for start in starts}
    stored: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_starts:
            stored.append((common.BASE + offset, value))
    if stored != STORED or common._pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored callback topology changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = "health" in json.dumps(overlay).lower()
    if routed:
        raise AuditError("health object unexpectedly became production-routed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_health_mutex_and_common_event_policy",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": len(rows), "ghidra_discovered_functions": 2,
            "path_anchored_functions": anchored, "baseline_ghidra_path_anchors": 1,
            "additional_recovered_functions": 2, "body_bytes": len(code),
            "reachable_instruction_bytes": len(code), "embedded_data_regions": 0,
            "outer_pool_regions": len(outer_gaps), "outer_pool_bytes": sum(map(len, outer_gaps)),
            "physical_bytes": 572, "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": external_entries, "direct_body_calls": len(calls),
            "internal_direct_body_calls": INTERNAL_CALL_COUNT,
            "external_direct_body_calls": len(calls) - INTERNAL_CALL_COUNT,
            "stored_entry_pointers": len(stored), "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "behavior": {
            "mutex_create": "lazy osMutexNew",
            "mutex_acquire_timeout": "osWaitForever",
            "handled_common_events": [0, 5],
            "event_zero": "decode health payload and conditionally post a six-byte service-one record",
            "event_five": "validate nonempty input and accept command byte one; log other commands",
            "other_events": "log unknown event",
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows), "direct_external_targets": len(external_counts),
            "direct_external_calls": sum(external_counts.values()),
            "easylogger": {"diagnostic_calls": 25, "version": "2.2.99 source-equivalent core", "selected_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"},
            "cmsis_freertos": {"calls": 3, "version": "v10.5.1", "selected_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53", "production_source_owned": True},
            "nanopb": {"direct_calls": 0, "through_first_party_health_provider": True, "compatible_release_range": "0.4.7..0.4.9.1", "selected_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824"},
            "g2_first_party_calls": 5, "new_version_discriminator": False,
            "assessment": "all upstream relationships terminate at admitted provider seams; no opaque third-party definition is embedded",
        },
        "boundary": {"physical_start": "0x004ffbd8", "physical_end_exclusive": "0x004ffe14", "path_pointer_cells": ["0x004ffddc"], "preceded_by": "quicklist unlock function and pool", "followed_by": "page-state-sync initializer"},
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "the exact private G2 source and producing commit remain unavailable",
            "the first-party health protobuf provider and schema are outside this object",
            "the object adds no dependency-version discriminator",
            "production admission requires target concurrency and health-message validation",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 health audit: PASS")
