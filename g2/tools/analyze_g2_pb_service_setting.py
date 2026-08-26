#!/usr/bin/env python3
"""Fail-closed stock and production audit of G2 pb_service_setting."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-setting-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-setting-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-setting-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_setting.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "59f77f3102881d030c5cdfff4bd43da9f061545cd5d47c4ad30e4a751a4708b4",
    CLOSURE: "3f53fa20acbeadb61f4a660f5512a80abef3d5c3e3638cd86646c7fa1d42675b",
    PROVENANCE: "67b02d52464f8dd30c597b0dc05a438a697396624773f56bb58fac9b9eaaf34b",
}
SOURCE_SIZE = 18393
SOURCE_SHA256 = "203b260e1e12286734073e587507eaceaec351a307c7243c3beecabb8fe97abd"
FUNCTIONS = (
    ("open_cfw_pb_service_setting_buffer_write", 146, 265564, 0,
     "buffer_write"),
    ("open_cfw_pb_service_setting_zero", 88, 265712, 0, "zero"),
    ("setting_is_duplicate_message", 22, 265800, 0, "duplicate"),
    ("setting_parse_data_package", 124, 265824, 3, "parse"),
    ("setting_respond_to_app", 104, 265948, 4, "respond"),
    ("setting_build_full_status_package", 418, 266052, 5, "build_status"),
    ("setting_respond_with_local_data", 120, 266472, 4, "respond_local"),
    ("setting_respond_to_app_serialize", 90, 266592, 4,
     "respond_serialize"),
    ("setting_respond_with_local_data_serialize", 90, 266684, 4,
     "respond_local_serialize"),
    ("setting_notify_common", 252, 266776, 6, "notify_common"),
    ("setting_notify_device_status_to_app", 50, 267028, 4,
     "notify_status"),
    ("setting_notify_recalibration_status_to_app", 76, 267080, 2,
     "notify_recalibration"),
    ("notify_silent_mode_to_app", 70, 267156, 2, "notify_silent"),
)
PATCH_SUFFIXES = (
    "duplicate", "parse", "respond", "build_status", "respond_local",
    "respond_serialize", "respond_local_serialize", "notify_common",
    "notify_status", "notify_recalibration", "notify_silent",
)
MANIFEST_PATCH_NAMES = (
    "pb_setting_is_duplicate_message_source_replacement",
    "pb_setting_parse_data_package_source_replacement",
    "pb_setting_respond_to_app_source_replacement",
    "pb_setting_build_full_status_package_source_replacement",
    "pb_setting_respond_with_local_data_source_replacement",
    "pb_setting_respond_to_app_serialize_source_replacement",
    "pb_setting_respond_with_local_data_serialize_source_replacement",
    "pb_setting_notify_common_source_replacement",
    "pb_setting_notify_device_status_to_app_source_replacement",
    "pb_setting_notify_recalibration_status_to_app_source_replacement",
    "pb_setting_notify_silent_mode_source_replacement",
)
PHYSICAL = (0x0049B198, 0x0049C070)
PHYSICAL_SHA256 = "af57ba66a30263a8e01d0975696d760f93ebe403f8988af911f811dad72f5268"
BODY_SHA256 = "ee22c4e8bb16352019d0cc8462f5522ee026ba29ccd334d90e366a2ce3b23d87"
GAPS = (
    (0x0049BBB0, 0x0049BBFC, "1471c469926c285c2146f02100b574ab1c867002ad75f33d2a085cf2c3a04b8d"),
    (0x0049BDEC, 0x0049BE04, "aed3743aee9e94a5425dea32fd7cfe84f7968b8f50abff644c68895866163df9"),
    (0x0049BEA8, 0x0049BEAC, "a48afbbc36d42eaeee750a927489e438cdced0ee8050e4da5f568bd3110a3dfd"),
    (0x0049BF16, 0x0049BF24, "769cc3582a2576fc93f92e69a82f00a888b417a08e474eff8908080c817bd061"),
    (0x0049BF98, 0x0049C070, "64f2e3d60848095811e1e9837ad0f37d2d185d0907dd75b651080108fa68acf4"),
)
GAP_SHA256 = "a888b97fd501039b114ffe1897120215496bc9cdbd5137b4c8fc4644a513acc2"
ENTRY_SHA256 = "0fb2ba284a6cafbc32918d557e0ebdc7c747ac48cac5a5a76c1d2ffa8cbba73a"
BODY_CALL_SHA256 = "0e9bf0eb237eb3107b44092dbc7a2a70e68c3e91cf74b508fa7478fe6c3995e6"
RAW_WINDOW_SHA256 = "e1fe7a3e9b76ac6c9af4394a723262d6b3d8a609a67adfcebd0d6d5389589cbe"
RETAINED_PATH_ADDRESS = 0x006DE2B4
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_setting\pb_service_setting.c"
)
SYMBOLS = {
    0x00763790: "setting_is_duplicate_message",
    0x0076F9E8: "setting_parse_data_package",
    0x0077A684: "setting_respond_to_app",
    0x00757DDC: "setting_build_full_status_package",
    0x007637B0: "setting_respond_with_local_data",
    0x00757E24: "setting_respond_to_app_serialize",
    0x00741628: "setting_respond_with_local_data_serialize",
    0x0077A6B4: "setting_notify_common",
    0x00757E48: "setting_notify_device_status_to_app",
    0x007416AC: "setting_notify_recalibration_status_to_app",
    0x0076FA74: "notify_silent_mode_to_app",
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    return data[start - BASE:end - BASE]


def pair_digest(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def cstring(data: bytes, address: int) -> str:
    offset = address - BASE
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return data[offset:end].decode("ascii")


def thumb_bw_target(data: bytes, address: int) -> int | None:
    first, second = struct.unpack_from("<HH", data, address - BASE)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1, j2 = (second >> 13) & 1, (second >> 11) & 1
    i1, i2 = (~(j1 ^ sign)) & 1, (~(j2 ^ sign)) & 1
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def analyze(image_path: Path = IMAGE) -> dict:
    data = image_path.read_bytes()
    if len(data) != 3_523_396 or sha256(data) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    for row in rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 11 or sum(map(len, bodies)) != 3466:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 334 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("80b51c22"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    for address, expected in SYMBOLS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained symbol changed at 0x{address:08x}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != [0x0049BBBC, 0x0049C028]:
        raise AuditError("retained path-pointer closure changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entry: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    entry_bw: list[tuple[int, int]] = []
    interior_bw: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    expected_entry = [
        (0x0046690C, 0x0049B1F8), (0x004669CC, 0x0049B900),
        (0x00466A66, 0x0049BA58), (0x00467102, 0x0049BEAC),
        (0x00467ED6, 0x0049BE04), (0x00467EF2, 0x0049BEAC),
        (0x00467EF6, 0x0049BE04), (0x00469534, 0x0049BF24),
        (0x00469966, 0x0049BF24), (0x00469AC4, 0x0049BF24),
        (0x0046B446, 0x0049BE04), (0x0046BB6A, 0x0049BE04),
        (0x0049B328, 0x0049B198), (0x0049B7E4, 0x0049B4DA),
        (0x0049B9B2, 0x0049B3D4), (0x0049BB0A, 0x0049B7C4),
        (0x0049BE58, 0x0049B4DA), (0x0049BEA0, 0x0049BBFC),
        (0x0049BF0E, 0x0049BBFC), (0x0049BF90, 0x0049BBFC),
        (0x0049E6F0, 0x0049BE04), (0x0049E9EC, 0x0049BE04),
        (0x004AE804, 0x0049BE04),
    ]
    if entry != expected_entry or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("direct entry closure changed")
    if interior or entry_bw or interior_bw:
        raise AuditError("direct strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 221 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    expected_stored = [
        (0x0043C2B4, 0x0049B819), (0x004761B1, 0x0049B6D5),
        (0x004B33D6, 0x0049B2C9), (0x004BB7AA, 0x0049B289),
        (0x004BC218, 0x0049B289), (0x004D7224, 0x0049B289),
        (0x00509748, 0x0049B929), (0x0053AC8B, 0x0049B54A),
        (0x0058ED02, 0x0049BE4C), (0x005A50FD, 0x0049BF48),
        (0x005EED87, 0x0049BDD5), (0x005F4CB0, 0x0049B209),
        (0x005F9963, 0x0049B4D5),
    ]
    if stored != expected_stored or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

    literal_checks = {
        0x0049BBB0: 0x20074868, 0x0049BBF0: 0x20074860,
        0x0049BBF4: 0x20074864, 0x0049BDF0: 0x200725A0,
        0x0049BDF4: 0x20072608, 0x0049BFFC: 0x200706EC,
        0x0049C030: 0x2007486C, 0x0049BBD0: 0x0077772C,
        0x0049C03C: 0x0077772C,
    }
    if any(struct.unpack_from("<I", data, address - BASE)[0] != value
           for address, value in literal_checks.items()):
        raise AuditError("setting workspace/global closure changed")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sha256(source) != SOURCE_SHA256:
        raise AuditError("production source changed")
    overlay = json.loads(OVERLAY.read_text())
    names = {item[0] for item in FUNCTIONS}
    leaves = {item.get("function"): item for item in overlay["relocated_leaves"]
              if item.get("function") in names}
    if set(leaves) != names:
        raise AuditError("production leaf inventory changed")
    for name, size, offset, relocation_count, _ in FUNCTIONS:
        leaf = leaves[name]
        if (leaf["source"].get("path") !=
                "components/apollo_main/core_overlay/pb_service_setting.c"
                or leaf["source"].get("size") != SOURCE_SIZE
                or leaf["source"].get("sha256") != SOURCE_SHA256
                or leaf.get("profiles") != ["apple-clang"]
                or leaf.get("strict_relocation_contract") is not True
                or (leaf["expected"].get("size"),
                    leaf["expected"].get("offset"),
                    leaf["expected"].get("alignment")) != (size, offset, 4)
                or len(leaf.get("relocations", [])) != relocation_count):
            raise AuditError(f"production leaf changed: {name}")
    patch_by_name = {item.get("name"): item for item in overlay["patch_sites"]}
    for suffix, row in zip(PATCH_SUFFIXES, rows):
        patch = patch_by_name.get(f"replace_pb_setting_{suffix}")
        expected = (
            int(row["stock_start"], 0), int(row["stock_bytes"]),
            row["stock_sha256"], "b_w", row["function"], ["apple-clang"],
        )
        if patch is None or (
            patch.get("runtime_address"), patch.get("expected_size"),
            patch.get("expected_sha256"), patch.get("branch"),
            patch.get("target_function"), patch.get("profiles"),
        ) != expected:
            raise AuditError(f"production patch changed: {row['function']}")
    report = json.loads(REPORT.read_text())
    if (report["overlay"]["size"], report["overlay"]["sha256"],
            report["component"]["size"], report["component"]["sha256"]) != (
        332148, "588a29c8d680068b6f27dd2cff831dcfd5aa71a91e4f9f97537d9bcb4a0d145d",
        3855544, "df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc",
    ):
        raise AuditError("production build pins changed")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    if (main["provider"].get("size"), main["provider"].get("sha256"),
            manifest["package"].get("expected_size"),
            manifest["package"].get("expected_sha256")) != (
        3855544, "df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc",
        4634038, "3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731",
    ):
        raise AuditError("production manifest pins changed")
    region_by_name = {item["name"]: item for item in main["regions"]}
    for region_name, row in zip(MANIFEST_PATCH_NAMES, rows):
        region = region_by_name.get(region_name)
        if region is None or (
            region.get("target_address"), region.get("size"),
            region.get("address_status"),
        ) != (int(row["stock_start"], 0), int(row["stock_bytes"]),
              "generated_source_entry_replacement"):
            raise AuditError(
                f"production manifest replacement changed: {row['function']}"
            )
    for name, size, offset, _, region_suffix in FUNCTIONS:
        region = region_by_name.get(f"pb_setting_{region_suffix}_source_text")
        if region is None or (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (3523396 + offset, size, 0x00794324 + offset,
              "source_compiled"):
            raise AuditError(f"production manifest source changed: {name}")
    retained = [item for item in main["regions"]
                if item["name"].startswith("pb_setting_retained_gap_")]
    alignment = [item for item in main["regions"]
                 if item["name"].startswith("pb_setting_")
                 and item["name"].endswith("_source_alignment")]
    if sum(item["size"] for item in retained) != 334 or any(
            item.get("address_status") != "official_blob"
            for item in retained) or sum(
                item["size"] for item in alignment) != 14:
        raise AuditError("production retained/alignment accounting changed")

    return {
        "surface": {
            "linked_functions": 11, "body_bytes": 3466,
            "owned_gap_pool_bytes": 334, "physical_bytes": 3800,
            "direct_bl_entry_sites": 23, "direct_body_calls": 221,
            "stored_exact_entry_pointers": 0, "strict_interior_ingress": 0,
            "raw_instruction_windows": 13, "manually_restored_bodies": 2,
        },
        "contracts": {
            "parse_status": {"accepted": 1, "rejected_or_duplicate": 0},
            "serializer_status": {"success_or_not_master": 0,
                                  "invalid_command_or_null": 1,
                                  "encode_failure": 0x2B},
            "route": 1, "service": 9,
            "message": "0x200725a0", "message_bytes": 0x68,
            "encode_buffer": "0x200706ec", "encode_capacity": 0x100,
            "response_command": 1, "full_status": {"command": 2, "tag": 4},
            "status_notifications": {
                "recalibration": {"command": 3, "tag": 5, "selector": 1},
                "silent_mode": {"command": 3, "tag": 5, "selector": 2},
            },
            "last_magic": "0x20074868", "notification_magic": "0x2007486c",
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": list(SYMBOLS.values()),
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 3466,
            "source_inventory_available": True,
            "source_functions": 13,
            "compiled_text_bytes": 1650,
            "alignment_bytes": 14,
            "strict_relocations": 38,
            "stock_replaced_bytes": 3466,
            "retained_gap_pool_bytes": 334,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized live G2 service 0x09 setting peer BLE, full-"
                "status, recalibration-status, or silent-mode workflow "
                "evidence is available; the authorized right temple is "
                "nonresponsive and the left temple must remain stock."
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError, UnicodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service_setting audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
