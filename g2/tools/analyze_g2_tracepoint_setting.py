#!/usr/bin/env python3
"""Fail-closed linked-object/provider audit for G2 tracepoint_setting.c."""
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
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x0043_7FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-tracepoint-setting-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-tracepoint-setting-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-tracepoint-setting-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "e599cd2d863c10ae7c5b714a464cb881127b5fa297e3a777816af35598924cf6",
    CLOSURE: "5d603172d4bc81c384f2bfd5ac2fe6bd8206d5a7e65e98c7dcf18f72c981e0bc",
    PROVIDER_MAP: "e1d51a7630e2ce7b94565c01b5b7f8c11b6bbdda7978e54ef8d045f3e6d7ff39",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\tracepoint\tracepoint_setting.c"
PATH_RUN = 0x006F_6EFC
PATH_POINTER_CELLS = [0x005E_E798, 0x005E_E8B4, 0x005E_F014]
PHYSICAL = (0x005E_DADC, 0x005E_F0B0)
PHYSICAL_BYTES = 5_588
PHYSICAL_SHA256 = "2ca261b24af1f8cc441f159e55a0f74b403e1668dcd3432199f37f5b5d74f0ca"
BODY_BYTES = 5_100
BODY_SHA256 = "5eb33cca3f8d78f650e6ee0ced70c57a07ddc47688e469c9fe8620694b838bc5"
POOL_REGIONS = 8
POOL_BYTES = 488
POOL_SHA256 = "973cbc7de4006c3d51107eeb7b84622f649f18e02e2f0085ec51148368f4f3d0"

PRECEDING_FUNCTION = (0x005E_D492, 0x005E_D4F8)
PRECEDING_FUNCTION_SHA256 = "b8715c0e166f6f452783498a8d1546cbc4ec0d4e48b79c2f40df8d24d2f2f255"
PRECEDING_POOL = (0x005E_D4F8, 0x005E_DADC)
PRECEDING_POOL_SHA256 = "4977ff518645445755ddaa9e3c5fc85850215be381d71600b638bd52e9378089"
FOLLOWING_OBJECT = (0x005E_F0B0, 0x005E_F100)
FOLLOWING_OBJECT_SHA256 = "068f18ded5c0a6f0b7ab544426763526a38e175c053528c6fec0eba98162a1bb"

ENTRY_COUNT = 42
ENTRY_SHA256 = "f5ba21e0ebde98174a7e4083a61cd57def9435cfdd4c0a9aae3893ead77e28af"
BODY_CALL_COUNT = 294
INTERNAL_BODY_CALL_COUNT = 42
BODY_CALL_SHA256 = "8d5766f66f09f2af91a9b348e2bfe8c19c5c47585ddd8f329784ccf56e0452b3"
STORED = [(0x006A_46D4, 0x005E_EEC5)]
STORED_SHA256 = "301a6acfd361438670b8ba7be9bcfef9a276979f0ca9f5f845fbb7afb3893d43"

EXTERNAL_TARGET_COUNTS = {
    0x0043_9C04: 3, 0x0043_C0E4: 6,
    0x0043_CE9E: 41, 0x0043_D0CE: 123, 0x0043_D574: 41,
    0x0044_A43C: 2, 0x0044_B5A0: 1, 0x0044_B610: 2, 0x0044_B728: 2,
    0x0045_A568: 3, 0x0046_5480: 1, 0x0046_CACC: 1,
    0x0047_4550: 1, 0x0047_45F4: 1, 0x0047_4814: 1, 0x0047_4870: 1,
    0x0047_498C: 2, 0x0047_4B02: 2, 0x0047_4BB8: 2, 0x0047_4C66: 2,
    0x0047_5B14: 2, 0x0047_8110: 1, 0x0047_E088: 2,
    0x0048_D874: 2, 0x0048_EC9E: 1, 0x0048_F49C: 2,
    0x0049_0120: 2, 0x0049_05F4: 1, 0x0049_0C32: 1,
}

RECOVERED_RETURNS = {
    0x005E_E788: bytes.fromhex("30bd"),
    0x005E_E87C: bytes.fromhex("30bd"),
    0x005E_EB42: bytes.fromhex("f0bd"),
    0x005E_EFA8: bytes.fromhex("70bd"),
}

STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0076_6D70: "tracepoint_insert_file_sorted",
    0x0077_CD9C: "tracepoint_scan_files",
    0x0077_3958: "tracepoint_encode_response",
    0x0077_3974: "tracepoint_send_to_phone",
    0x0077_3990: "tracepoint_send_to_master",
    0x0077_CDB4: "tracepoint_reply_result",
    0x0075_BDB4: "tracepoint_handle_request_file_name",
    0x0076_6DB0: "tracepoint_handle_delete_file",
    0x0077_39AC: "tracepoint_delete_all_files",
    0x0076_6DF0: "tracepoint_handle_delete_all",
    0x0077_39C8: "tracepoint_handle_ble_data",
    0x0075_BE8C: "tracepoint_handle_slave_file_list",
    0x0075_02AC: "tracepoint_setting_common_data_handler",
    0x0078_EC14: "/log/tp",
    0x0078_4504: "/log/tp/tp_%u.bin",
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


def _validate_provider_pins() -> None:
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise AuditError("EasyLogger provider commit changed")
    nanopb = json.loads((ROOT / "third_party/nanopb/PROVENANCE.json").read_text())
    if nanopb["upstream"]["selected_commit"] != "98bf4db69897b53434f3d0ba72e0a3ab1a902824":
        raise AuditError("nanopb compatibility commit changed")
    if nanopb["selection"]["exact_g2_point_release_proven"]:
        raise AuditError("nanopb exact-point-release qualification changed")
    littlefs = json.loads((ROOT / "third_party/littlefs/PROVENANCE.json").read_text())
    if littlefs["upstream"]["selected_commit"] != "0494ce7169f06a734a7bd7585f49a9fa91fa7318":
        raise AuditError("littlefs source-equivalent commit changed")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    for marker in ("9.20 is therefore a practical lower bound", "9.60.2", "Exact EWARM/ICCARM release"):
        if marker not in iar:
            raise AuditError("IAR family-level provenance assessment changed")


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    _validate_provider_pins()
    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        provider_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 21 or len(provider_rows) != 5:
        raise AuditError("function or provider inventory changed")
    edges = sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows)
    if edges != sum(EXTERNAL_TARGET_COUNTS.values()):
        raise AuditError("provider edge accounting changed")

    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    gaps: list[bytes] = []
    anchored = 0
    previous_end = PHYSICAL[0]
    for row in rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        if start in starts or start < previous_end or start >= end:
            raise AuditError(f"invalid or overlapping function at 0x{start:08x}")
        if previous_end < start:
            gaps.append(_slice(blob, previous_end, start))
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
        gaps.append(_slice(blob, previous_end, PHYSICAL[1]))
    if anchored != 9 or intervals[0][0] != PHYSICAL[0] or previous_end > PHYSICAL[1]:
        raise AuditError("path anchor or object interval changed")
    if sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body inventory changed")
    if len(gaps) != POOL_REGIONS or sum(map(len, gaps)) != POOL_BYTES or _sha256(b"".join(gaps)) != POOL_SHA256:
        raise AuditError("literal-pool inventory changed")
    if len(_slice(blob, *PHYSICAL)) != PHYSICAL_BYTES or _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical tracepoint-settings object changed")
    for bounds, expected, label in (
        (PRECEDING_FUNCTION, PRECEDING_FUNCTION_SHA256, "preceding terminal function"),
        (PRECEDING_POOL, PRECEDING_POOL_SHA256, "preceding terminal pool"),
        (FOLLOWING_OBJECT, FOLLOWING_OBJECT_SHA256, "following FreeType object"),
    ):
        if _sha256(_slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} boundary changed")
    for address, expected in RECOVERED_RETURNS.items():
        if _slice(blob, address, address + len(expected)) != expected:
            raise AuditError(f"recursive return changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if _c_string(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    word = struct.pack("<I", PATH_RUN)
    hits, cursor = [], blob.find(word)
    while cursor >= 0:
        hits.append(BASE + cursor)
        cursor = blob.find(word, cursor + 1)
    if hits != PATH_POINTER_CELLS:
        raise AuditError(f"source-path pointer topology changed: {hits!r}")

    sys.path.insert(0, str(ROOT / "tools"))
    import recover_apollo_embedded_source_paths as decoder

    entries: list[tuple[int, int]] = []
    strict: list[tuple[int, int]] = []
    unknown: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            strict.append((site, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown.append((site, target))
    if len(entries) != ENTRY_COUNT or _pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct entry topology changed")
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if external_entries or strict or unknown:
        raise AuditError("entry closure changed")

    calls: list[tuple[int, int]] = []
    image_end = BASE + len(blob)
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None and BASE <= target < image_end:
                calls.append((site, target))
    if len(calls) != BODY_CALL_COUNT or _pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body callee topology changed")
    if sum(target in starts for _, target in calls) != INTERNAL_BODY_CALL_COUNT:
        raise AuditError("internal body-call census changed")
    external_counts = Counter(target for _, target in calls if not (PHYSICAL[0] <= target < PHYSICAL[1]))
    if dict(external_counts) != EXTERNAL_TARGET_COUNTS:
        raise AuditError(f"provider target accounting changed: {external_counts!r}")

    encoded_starts = starts | {entry | 1 for entry in starts}
    stored: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_starts:
            stored.append((BASE + offset, value))
    if stored != STORED or _pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored callback topology changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("tracepoint_setting" in item.get("path", "").lower() for item in overlay.get("sources", [])) or any(
        "tracepoint_setting" in str(item).lower() for item in overlay.get("functions", [])
    )
    if routed:
        raise AuditError("tracepoint settings unexpectedly became production-routed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_tracepoint_file_list_and_command_policy",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": len(rows), "path_anchored_functions": anchored,
            "additional_recovered_functions": len(rows) - anchored,
            "recursive_decode_recoveries": len(RECOVERED_RETURNS),
            "body_bytes": sum(map(len, bodies)), "literal_pool_regions": len(gaps),
            "literal_pool_bytes": sum(map(len, gaps)), "physical_bytes": PHYSICAL_BYTES,
            "direct_bl_entry_sites": len(entries), "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls), "internal_direct_body_calls": INTERNAL_BODY_CALL_COUNT,
            "external_direct_body_calls": len(calls) - INTERNAL_BODY_CALL_COUNT,
            "stored_entry_pointers": len(stored), "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "behavior": {
            "directory": "/log/tp", "filename_pattern": "tp_%u.bin",
            "display_name_pattern": "%c:%c%u", "roles": ["L", "R"],
            "commands": ["heartbeat", "file-list", "delete-file", "delete-all"],
            "peer_and_phone_routing": True, "sorted_file_inventory": True,
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows), "direct_external_targets": len(external_counts),
            "direct_external_calls": sum(external_counts.values()),
            "easylogger": {"version": "2.2.99 source-equivalent core", "calls": 205,
                "commit_interval": "cd93d9c768415f4b7279f2d3ef2366ce15ea087c..a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"},
            "nanopb": {"compatible_release_range": "0.4.7..0.4.9.1", "selected_version": "0.4.9",
                "selected_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824", "exact_g2_point_release": None, "calls": 7},
            "littlefs": {"selected_source_equivalent_version": "v2.10.1",
                "selected_commit": "0494ce7169f06a734a7bd7585f49a9fa91fa7318", "direct_calls": 0,
                "wrapper_calls": 14, "exact_historical_checkout": None},
            "iar_dlib": {"floor": "EWARM 9.20+", "leading_candidate": "9.60.2",
                "exact_release": None, "calls": 19, "new_version_discriminator": False},
            "assessment": "all upstream relationships terminate at admitted provider seams; no opaque third-party definition is embedded",
        },
        "boundary": {"physical_start": f"0x{PHYSICAL[0]:08x}", "physical_end_exclusive": f"0x{PHYSICAL[1]:08x}",
            "path_pointer_cells": [f"0x{x:08x}" for x in PATH_POINTER_CELLS],
            "preceded_by": "terminal-session literal pool", "followed_by": "independent FreeType object"},
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "the exact private G2 source and producing commit remain unavailable",
            "nanopb and littlefs commits are selected source-equivalent baselines rather than proof of the private checkout",
            "the object adds no exact IAR release or archive discriminator",
            "production admission requires clean-room schema/policy implementation and target BLE/filesystem validation",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 tracepoint-settings audit: PASS")
