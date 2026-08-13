#!/usr/bin/env python3
"""Fail-closed linked-object and provider audit for G2 service_settings.c."""
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
FUNCTION_MAP = ROOT / "tools/manifests/g2-service-settings-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-service-settings-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-service-settings-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "4b6992a2b993892e9ddcb49b4e93d0628f0db8f9f6194fee09110fc83a133099",
    CLOSURE: "d19b3e746f19b877a83966e063d9d9986267ea06bb5953a5c49eba46b8cc1093",
    PROVIDER_MAP: "3473742c8de06bcfa815d2c526912b509c3dd19d81be75eaa54b97197090a283",
}

RETAINED_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git\platform\service\settings"
    r"\service_settings.c"
)
PATH_RUN = 0x006E_9EE0
PATH_POINTER_CELLS = [0x0046_BB70, 0x0046_C660]

PHYSICAL = (0x0046_B0EC, 0x0046_C73C)
PHYSICAL_BYTES = 5_712
PHYSICAL_SHA256 = "fa6d6bb48321fb41da57627c3f8fa0ec9c4215e21dfd8bea7421b84f7406e9c0"
BODY_BYTES = 5_146
BODY_SHA256 = "094b0f0d32f03eadf7e16ac72e17c55e8cb9bebd8eb50326369643eef5ce66de"
POOL_REGIONS = 19
POOL_BYTES = 566
POOL_SHA256 = "37645b571c04a9f68c2c671871f6efe4844aff8de6e87ff3053751c5ead71f7a"

PRECEDING_FUNCTION = (0x0046_AEEA, 0x0046_B004)
PRECEDING_FUNCTION_SHA256 = "5ff425ada382100b5faf23a2ef38591f116187c2f67082e892bcdf5dabc2c252"
PRECEDING_POOL = (0x0046_B004, 0x0046_B0EC)
PRECEDING_POOL_SHA256 = "974ed588397d384ea6b5432ce102993a83cc6cea0b32eece4751469d27d86812"
FOLLOWING_OBJECT = (0x0046_C73C, 0x0046_C984)
FOLLOWING_OBJECT_SHA256 = "129ff88839a933f90af5ae9f3417a3ff53f90314dde5b80a5446a7147e6c3869"

ENTRY_COUNT = 117
EXTERNAL_ENTRY_COUNT = 94
ENTRY_SHA256 = "74576174c5252aa92e68f03d360e854fe6009bf341777685cf1fc9daae942e51"
BODY_CALL_COUNT = 340
INTERNAL_BODY_CALL_COUNT = 23
BODY_CALL_SHA256 = "f0093f145e2e71d4ccd02475f13e946a32d0dbae252dd283e9cdd99e2d1214e0"
STORED = [(0x0046_C698, 0x0046_B3E5)]
STORED_SHA256 = "a498f894baaa919337de1fb35235c44bfb25757a872724c08600e6c74fbf91d3"

# These two halfword-aligned bit patterns decode as BL only when the decoder
# starts in the middle of a valid 32-bit UDIV/MUL instruction.  Both targets
# are outside the authenticated image and are not provider edges.
FALSE_BODY_DECODES = {
    (0x0046_C44A, 0x0005_C85C): (0x0046_C448, bytes.fromhex("b1fbf0f7")),
    (0x0046_C4A0, 0x0087_09E4): (0x0046_C49E, bytes.fromhex("00fb04f0")),
}

EXTERNAL_TARGET_COUNTS = {
    0x0043_9BE4: 3,   # IAR __aeabi_memcpy prefix
    0x0043_9C04: 3,   # IAR aligned memcpy entry
    0x0043_C0E4: 4,   # IAR memory fill
    0x0043_CE9E: 50,  # EasyLogger backend
    0x0043_D0CE: 150, # EasyLogger level gate
    0x0043_D574: 50,  # EasyLogger structured output
    0x0044_3484: 2,   # G2 display-ready predicate
    0x0044_87AC: 3,   # G2 OTA-active predicate
    0x0044_8E34: 2,   # G2 deferred save-event post
    0x0044_90CC: 1,   # CMSIS osKernelGetTickCount
    0x0044_A1C6: 1,   # G2 device-time provider
    0x0044_B5A0: 3,   # IAR strncpy
    0x0045_A568: 11,  # G2 role accessor
    0x0045_A570: 1,   # G2 role/profile accessor
    0x0046_5480: 3,   # G2 message transport
    0x0046_6890: 1,   # G2 brightness dispatch
    0x0046_C9D0: 1,   # G2 display level application
    0x0047_394C: 1,   # G2 display-task accessor
    0x0049_ACD4: 1,   # first-party CRC-16/CCITT provider
    0x0049_BE04: 2,   # G2 device-status notification
    0x0049_EB96: 2,   # G2 wear/input state
    0x004A_6D58: 2,   # sensor-hub open
    0x004A_6DCA: 2,   # sensor-hub close
    0x004A_6E3C: 1,   # sensor-hub IMU/head-up command
    0x004A_BE60: 5,   # product-mode getter
    0x004A_CAD0: 2,   # case-state predicate
    0x004A_D8FA: 1,   # CHG_GetSoc
    0x004A_D900: 1,   # CHG_GetIsCharging
    0x004A_E81C: 1,   # display brightness provider
    0x004A_E8E8: 1,   # settings initialization provider
    0x004A_E946: 1,   # ALS scale provider
    0x004A_EA56: 1,   # battery callback registration
    0x004A_EC04: 1,   # SVC_KvdbWriteSetting
    0x004A_ED88: 1,   # SVC_KvdbWriteAlsScale
    0x004A_F73A: 1,   # SVC_NvdbGetSysData
    0x004B_04C4: 1,   # SVC_KvdbWriteTerminalMode
}

RECOVERED_RETURNS = {
    0x0046_B44A: bytes.fromhex("13bd"),
    0x0046_B92E: bytes.fromhex("31bd"),
    0x0046_B986: bytes.fromhex("10bd"),
    0x0046_BB6E: bytes.fromhex("7fbd"),
    0x0046_BE08: bytes.fromhex("30bd"),
    0x0046_BE68: bytes.fromhex("70bd"),
    0x0046_BFFC: bytes.fromhex("7047"),
    0x0046_C186: bytes.fromhex("02bd"),
    0x0046_C1BA: bytes.fromhex("02bd"),
    0x0046_C210: bytes.fromhex("32bd"),
    0x0046_C5F0: bytes.fromhex("13bd"),
}

STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0076_51F0: "SVC_Settings_InputEventCheck",
    0x0077_15B0: "SVC_Settings_UledCtrlCheck",
    0x0077_15CC: "SVC_Settings_AppLaunchCheck",
    0x0076_5210: "SVC_Settings_BatteryCallback",
    0x0076_5250: "SVC_Settings_DumpSettingConfig",
    0x0075_9E10: "SVC_Settings_SyncVersionOnlySend",
    0x0076_5290: "SVC_Settings_RequestLeftVersion",
    0x0076_52D0: "SVC_Settings_UpdateLeftVersion",
    0x0077_1658: "SVC_Settings_SyncHandler",
    0x0074_E394: "SVC_Settings_SaveSettingConfigToKVCheck",
    0x0075_9E34: "SVC_Settings_SaveSettingConfigToKV",
    0x0076_52F0: "SVC_Settings_SaveAlsScaleToKV",
    0x0076_5310: "SVC_Settings_AutoBrightnessOpen",
    0x0075_9E7C: "SVC_Settings_AutoBrightnessClose",
    0x0077_BCEC: "SVC_Settings_GetMaxLum",
    0x0074_37AC: "SVC_Settings_BrightnessLevelToLumAndCurrent",
    0x0077_171C: "SVC_Settings_HeadUpConfig",
    0x0078_C074: "2.2.6.10",
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
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != (
        "d213f261b5be6bb29a7cce8b84071706b72f4d53"
    ):
        raise AuditError("CMSIS-FreeRTOS provider commit changed")
    if cmsis["upstreams"]["cmsis_5"]["selected_commit"] != (
        "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c"
    ):
        raise AuditError("CMSIS_5 provider commit changed")
    easylogger = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easylogger["upstream"]["selected_commit"] != (
        "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"
    ):
        raise AuditError("EasyLogger provider commit changed")
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
    if len(rows) != 31 or len(provider_rows) != 8:
        raise AuditError("function or provider inventory changed")
    provider_edge_total = sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows)
    if provider_edge_total != sum(EXTERNAL_TARGET_COUNTS.values()):
        raise AuditError("provider edge accounting changed")

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
    if anchored != 13:
        raise AuditError(f"source-path anchor census changed: {anchored}")
    if sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body inventory changed")
    if len(gaps) != POOL_REGIONS or sum(map(len, gaps)) != POOL_BYTES:
        raise AuditError("literal-pool inventory changed")
    if _sha256(b"".join(gaps)) != POOL_SHA256:
        raise AuditError("literal-pool bytes changed")
    if len(_slice(blob, *PHYSICAL)) != PHYSICAL_BYTES or _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical settings object changed")
    for bounds, expected, label in (
        (PRECEDING_FUNCTION, PRECEDING_FUNCTION_SHA256, "preceding function"),
        (PRECEDING_POOL, PRECEDING_POOL_SHA256, "preceding pool"),
        (FOLLOWING_OBJECT, FOLLOWING_OBJECT_SHA256, "following display object"),
    ):
        if _sha256(_slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} boundary changed")

    for address, expected in RECOVERED_RETURNS.items():
        if _slice(blob, address, address + len(expected)) != expected:
            raise AuditError(f"recursive return changed at 0x{address:08x}")
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
    unknown_object_targets: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        address = BASE + offset
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in strict_interiors:
            interior.append((address, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown_object_targets.append((address, target))
    if len(entries) != ENTRY_COUNT or _pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct entry topology changed")
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if external_entries != EXTERNAL_ENTRY_COUNT or interior or unknown_object_targets:
        raise AuditError("entry closure changed")

    calls: list[tuple[int, int]] = []
    raw_out_of_image: list[tuple[int, int]] = []
    image_end = BASE + len(blob)
    for start, end in intervals:
        for address in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is None:
                continue
            if BASE <= target < image_end:
                calls.append((address, target))
            else:
                raw_out_of_image.append((address, target))
    if len(calls) != BODY_CALL_COUNT or _pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body callee topology changed")
    if sum(target in starts for _, target in calls) != INTERNAL_BODY_CALL_COUNT:
        raise AuditError("internal callee census changed")
    if set(raw_out_of_image) != set(FALSE_BODY_DECODES):
        raise AuditError("out-of-image raw halfword decode set changed")
    for _, (instruction, encoding) in FALSE_BODY_DECODES.items():
        if _slice(blob, instruction, instruction + 4) != encoding:
            raise AuditError("false-decode containing instruction changed")
    external_counts = Counter(
        target for _, target in calls if not (PHYSICAL[0] <= target < PHYSICAL[1])
    )
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
    routed = any(
        "service_settings" in item.get("path", "").lower()
        for item in overlay.get("sources", [])
    ) or any(
        "service_settings" in str(item).lower()
        for item in overlay.get("functions", [])
    )
    if routed:
        raise AuditError("settings object unexpectedly became production-routed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_settings_policy",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": len(rows),
            "path_anchored_functions": anchored,
            "additional_recovered_functions": len(rows) - anchored,
            "recursive_decode_recoveries": len(RECOVERED_RETURNS),
            "body_bytes": sum(map(len, bodies)),
            "literal_pool_regions": len(gaps),
            "literal_pool_bytes": sum(map(len, gaps)),
            "physical_bytes": len(_slice(blob, *PHYSICAL)),
            "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": INTERNAL_BODY_CALL_COUNT,
            "external_direct_body_calls": len(calls) - INTERNAL_BODY_CALL_COUNT,
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(interior),
            "unrecovered_direct_object_targets": len(unknown_object_targets),
            "out_of_image_false_positive_decodes": len(raw_out_of_image),
        },
        "boundary": {
            "physical_start": f"0x{PHYSICAL[0]:08x}",
            "physical_end_exclusive": f"0x{PHYSICAL[1]:08x}",
            "preceded_by": "independent first-party function and its terminal pool",
            "followed_by": "independently rooted LVGL display buffer-sync object",
            "path_pointer_cells": [f"0x{x:08x}" for x in PATH_POINTER_CELLS],
        },
        "behavior": {
            "version": "2.2.6.10",
            "settings_record_bytes": 28,
            "settings_crc_covered_bytes": 24,
            "version_request_throttle_ticks": 500,
            "brightness_range": [2, 100],
            "brightness_table_entries": 13,
            "luminance_ratio_entries": 11,
            "head_up_angle_range_degrees": [-90, 90],
            "peer_service_id": 9,
            "battery_callback_contexts": [0, 1],
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows),
            "direct_external_targets": len(external_counts),
            "direct_external_calls": sum(external_counts.values()),
            "cmsis_freertos": {
                "version": "v10.5.1",
                "commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
                "cmsis_5_commit": "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c",
                "calls": external_counts[0x0044_90CC],
            },
            "easylogger": {
                "version": "2.2.99 source-equivalent core",
                "commit_interval": "cd93d9c768415f4b7279f2d3ef2366ce15ea087c..a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
                "calls": sum(external_counts[x] for x in (0x0043_CE9E, 0x0043_D0CE, 0x0043_D574)),
            },
            "iar_dlib": {
                "floor": "EWARM 9.20+",
                "leading_candidate": "9.60.2",
                "exact_release": None,
                "exact_archive_options": None,
                "calls": sum(external_counts[x] for x in (0x0043_9BE4, 0x0043_9C04, 0x0043_C0E4, 0x0044_B5A0)),
                "new_version_discriminator": False,
            },
            "assessment": "all third-party relationships terminate at already authenticated or bounded provider seams; no opaque upstream definition is embedded",
        },
        "cross_version": {
            "prior_g2_named_functions_in_sequence": 21,
            "qualification": "prior G2 is a naming/topology oracle only; every current byte and boundary is independently pinned",
        },
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "the exact private G2 source and producing commit remain unavailable",
            "semantic labels are intentionally conservative where no current function-name string survives",
            "the object supplies no new discriminator for the unresolved exact IAR release or DLIB archive options",
            "behavioral closure does not make this first-party service production-routable without clean-room implementation and hardware validation",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 service-settings audit: PASS")
