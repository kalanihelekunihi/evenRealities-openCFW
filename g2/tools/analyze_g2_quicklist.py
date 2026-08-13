#!/usr/bin/env python3
"""Fail-closed linked-object and provider audit for G2 quicklist.c."""
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
FUNCTION_MAP = ROOT / "tools/manifests/g2-quicklist-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-quicklist-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-quicklist-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "7cbc40669aa9ad0c520500f1e9c6d2b7b366e8beec86ba5529771b5103bbfde1",
    CLOSURE: "6280b543fcdf8e62b222d68f612448d7d7621d39a19b4143b7807d6f77e17900",
    PROVIDER_MAP: "88da688a17f6d47c4008e7e0adb53587ec8acb6958148900e689bbd138f6c3fc",
}
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\quicklist\quicklist.c"
PATH_RUN = 0x0070_4F40
PATH_POINTER_CELLS = [0x004F_FBB4]
PHYSICAL = (0x004F_FA70, 0x004F_FBD8)
PHYSICAL_SHA256 = "b663f4b2708698befa099cc7396e637d25bf8d8177af315532236ca9e013051a"
BODY_BYTES = 310
BODY_SHA256 = "f29da20ba77503b002e58aa15b3872a0a0326631523cca2c2f9f368f1c882cc1"
INSTRUCTION_COUNT = 129
INSTRUCTION_DIGEST = "3d6dbf24b0e7866e38714567f73193cc6b91cfff071f3a5d7ecefeaf1e323b42"
OUTER_GAPS = [(0x004F_FBA6, 0x004F_FBD8)]
OUTER_GAPS_SHA256 = "298971132c30d395795da23dfa28c05d9e6ed19bdf9febdc1a9a23b9f8038d2d"
PRECEDING_FUNCTION = (0x004F_F99A, 0x004F_FA44)
PRECEDING_FUNCTION_SHA256 = "2f7d2bffbe3aea243c730a055e12d04e771aef98125c01a072b6a746f240878f"
PRECEDING_POOL = (0x004F_FA44, 0x004F_FA70)
PRECEDING_POOL_SHA256 = "5b6f8497a0d814000f0d5eaea1d73ffb2ebb5244884a04b357514cbec88b30cd"
FOLLOWING_FUNCTION = (0x004F_FBD8, 0x004F_FC32)
FOLLOWING_FUNCTION_SHA256 = "ce202179945c7a53466944719fb13fc4009cb20cf4739958b36a7b1ae5222b6e"
ENTRY_COUNT = 25
EXTERNAL_ENTRY_COUNT = 24
ENTRY_SHA256 = "492f94d6af0a3fe7cedeb80d6ae1b7041ad4b4163bad5f0d41da16062b1f4c2a"
CALL_COUNT = 22
INTERNAL_CALL_COUNT = 1
CALL_SHA256 = "bb99728bb1caa0f2e3b71311e5a3c2840f21f593c7dfd7d27079f27cea99dd2b"
STORED = [(0x006A_45F4, 0x004F_FB39)]
STORED_SHA256 = "31a4642cccc09d3dfef868b855deaa78223b442c45dfd16c54e2b681d9be281b"
EXTERNAL_TARGET_COUNTS = {
    0x0043_CE9E: 3, 0x0043_D0CE: 9, 0x0043_D574: 3,
    0x0044_971C: 1, 0x0044_97B6: 1, 0x0044_981C: 1,
    0x004F_5E84: 1, 0x0055_894C: 1, 0x0055_8B3C: 1,
}
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0074_2574: "Failed to create quicklist storage mutex",
    0x0077_08C8: "quicklist_data_mutex_init",
    0x0078_85B0: "quicklist.page",
    0x0078_85C0: "mutex is NULL",
    0x0077_AFFC: "quicklist_lock_storage",
    0x0077_B014: "Unknown event type: %d",
    0x0076_4690: "Quicklist_common_data_handler",
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
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53" or nanopb["upstream"]["selected_commit"] != "98bf4db69897b53434f3d0ba72e0a3ab1a902824":
        raise AuditError("provider commit changed")
    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        provider_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 4 or len(provider_rows) != 3 or sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows) != 21:
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
        starts.add(start); interiors.update(range(start + 2, end, 2)); intervals.append((start, end)); bodies.append(body)
        anchored += row["source_path_anchor"] == "yes"
        previous_end = end
    if previous_end < PHYSICAL[1]:
        outer_bounds.append((previous_end, PHYSICAL[1]))
    outer_bytes = b"".join(common._slice(blob, *bounds) for bounds in outer_bounds)
    if anchored != 3 or sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256 or outer_bounds != OUTER_GAPS or _sha256(outer_bytes) != OUTER_GAPS_SHA256:
        raise AuditError("body, anchor, or pool inventory changed")
    if len(common._slice(blob, *PHYSICAL)) != 360 or _sha256(common._slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical quicklist object changed")
    for bounds, expected, label in ((PRECEDING_FUNCTION, PRECEDING_FUNCTION_SHA256, "preceding function"), (PRECEDING_POOL, PRECEDING_POOL_SHA256, "preceding pool"), (FOLLOWING_FUNCTION, FOLLOWING_FUNCTION_SHA256, "following health initializer")):
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} changed")

    all_instructions: dict[int, object] = {}; calls: list[tuple[int, int]] = []; embedded = []
    for interval in intervals:
        recovered, function_calls = common._recover_function(blob, *interval)
        all_instructions.update(recovered); calls.extend(function_calls); embedded.extend(common._uncovered(interval, recovered))
    code = b"".join(common._slice(blob, address, address + instruction.size) for address, instruction in sorted(all_instructions.items()))
    pairs = sorted((address, instruction.size) for address, instruction in all_instructions.items())
    if len(all_instructions) != INSTRUCTION_COUNT or common._instruction_digest(pairs) != INSTRUCTION_DIGEST or len(code) != BODY_BYTES or _sha256(code) != BODY_SHA256 or embedded:
        raise AuditError("instruction closure changed")
    calls.sort()
    external_counts = Counter(target for _, target in calls if target not in starts)
    if len(calls) != CALL_COUNT or common._pair_digest(calls) != CALL_SHA256 or sum(target in starts for _, target in calls) != INTERNAL_CALL_COUNT or dict(external_counts) != EXTERNAL_TARGET_COUNTS:
        raise AuditError("call topology changed")
    for address, expected in STRINGS.items():
        if common._c_string(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")
    path_word = struct.pack("<I", PATH_RUN); path_hits = []; cursor = blob.find(path_word)
    while cursor >= 0:
        path_hits.append(common.BASE + cursor); cursor = blob.find(path_word, cursor + 1)
    if path_hits != PATH_POINTER_CELLS:
        raise AuditError("path pointer topology changed")

    entries = []; strict = []; unknown = []
    for offset in range(0, len(blob) - 3, 2):
        site = common.BASE + offset; target = thumb._thumb_bl_target(blob, site)
        if target in starts: entries.append((site, target))
        elif target in interiors: strict.append((site, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]: unknown.append((site, target))
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if len(entries) != ENTRY_COUNT or common._pair_digest(entries) != ENTRY_SHA256 or external_entries != EXTERNAL_ENTRY_COUNT or strict or unknown:
        raise AuditError("entry topology changed")
    encoded = starts | {start | 1 for start in starts}; stored = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded: stored.append((common.BASE + offset, value))
    if stored != STORED or common._pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored callback topology changed")
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = "quicklist" in json.dumps(overlay).lower()
    if routed: raise AuditError("quicklist unexpectedly became production-routed")

    return {
        "schema_version": 1, "analysis_mode": "read-only; fail-closed linked-object and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {"retained_path": RETAINED_PATH, "ownership": "g2_local_quicklist_mutex_and_common_event_policy", "historical_source_available": False, "private_producing_commit_observable": False, "embedded_third_party_definitions": []},
        "surface": {"linked_functions": 4, "ghidra_discovered_functions": 2, "additional_recovered_functions": 2, "path_anchored_functions": anchored, "baseline_ghidra_path_anchors": 1, "body_bytes": len(code), "reachable_instruction_bytes": len(code), "embedded_data_regions": 0, "outer_pool_regions": len(outer_bounds), "outer_pool_bytes": len(outer_bytes), "physical_bytes": 360, "direct_bl_entry_sites": len(entries), "external_direct_bl_entry_sites": external_entries, "direct_body_calls": len(calls), "internal_direct_body_calls": 1, "external_direct_body_calls": 21, "stored_entry_pointers": len(stored), "strict_interior_raw_bl_decodes": len(strict), "unrecovered_direct_object_targets": len(unknown)},
        "behavior": {"mutex_create": "lazy osMutexNew", "mutex_acquire_timeout": "osWaitForever", "handled_common_events": [0], "event_zero": "parse quicklist data then invoke local ready and refresh providers", "other_events": "log unknown event"},
        "provider_boundary": {"provider_rows": 3, "direct_external_targets": len(external_counts), "direct_external_calls": sum(external_counts.values()), "easylogger": {"calls": 15, "selected_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"}, "cmsis_freertos": {"calls": 3, "version": "v10.5.1", "selected_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53", "production_source_owned": True}, "nanopb": {"direct_calls": 0, "through_first_party_quicklist_provider": True, "selected_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824"}, "g2_first_party_calls": 3, "new_version_discriminator": False, "assessment": "no opaque third-party definition is embedded"},
        "boundary": {"physical_start": "0x004ffa70", "physical_end_exclusive": "0x004ffbd8", "path_pointer_cells": ["0x004ffbb4"], "preceded_by": "dashboard status sender and pool", "followed_by": "health mutex initializer"},
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": ["the private source and producing commit remain unavailable", "the quicklist schema/provider is outside this object", "no new dependency-version discriminator is present", "target concurrency and UI validation are required before production admission"],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 quicklist audit: PASS")
