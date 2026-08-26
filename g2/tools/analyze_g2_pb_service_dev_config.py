#!/usr/bin/env python3
"""Fail-closed stock and production audit of G2 pb_service_dev_config."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-dev-config-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-dev-config-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-dev-config-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_dev_config.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "b67dd987f128de9f5db844d769b03301c8c48d952790d155b75a877aa4c08d86",
    CLOSURE: "2be10bb975b69388cc4de071586b67fceefa813f56080535b07634aea6fdcd22",
    PROVENANCE: "d52c825658fbf7bf8c809b10cfbb6f1ec11cc1c18619374fb5011cfd7ab1b5cc",
}
SOURCE_SIZE = 11435
SOURCE_SHA256 = "46c79dbaad289491f195562aea10d3d8ba92684e7227e463b697a04f31b67bc4"
FUNCTIONS = (
    ("open_cfw_pb_service_dev_config_buffer_write", 154, 262332, 0,
     "buffer_write"),
    ("open_cfw_pb_service_dev_config_zero", 88, 262488, 0, "zero"),
    ("APP_PbRxErrorCode", 4, 262576, 0, "error_rx"),
    ("APP_PbTxEncodeErrorCode", 118, 262580, 4, "error_tx"),
    ("APP_PbRxDevCfgFrameDataProcess", 634, 262700, 29, "rx"),
)
PATCH_SUFFIXES = ("rx", "error_rx", "error_tx")
PHYSICAL = (0x004D83D8, 0x004D8F4C)
PHYSICAL_SHA256 = "d956ed13c98123c0ddb960e65c1ca1baa8629675bba7663b2978505d122f044a"
BODY_SHA256 = "401049831bcd87292d5897f5f6eca7d19eb0f8dc906233bb89d4e77a0214647b"
GAPS = (
    (0x004D8B7C, 0x004D8BE0, "820f874c0c0b8e47c49167c6381b5954949b06ec0580e34524f9102e02b901d7"),
    (0x004D8DA0, 0x004D8DB8, "1f0105932dc8cfab9a791dbeeeec75c85de4a72000b3d07a12921f94fde81659"),
    (0x004D8EAA, 0x004D8F4C, "2c93a45cdcfa236ffb932d99948987fcff39ae991190ffd5bd1af920118bed6e"),
)
GAP_SHA256 = "c28c50a8e79cf41c63c0ffc56384d7b3b6ea1481e482d64ebfcd9f78e57cbe4d"
ASSERT_RECORD = (0x0078196C, 0x00781980)
ASSERT_SHA256 = "201d48d46016292b0b8770976882b73252165e6b3daa86db4782d6344f145af7"
ENTRY_SHA256 = "205819dee593e548062c05fd0bec3d4a0775106f1d54b969b90eaf932560a00c"
BODY_CALL_SHA256 = "b153883176175f4160ac62fe02759ce3ee5a213964254be182343d5e31b5f779"
RAW_WINDOW_SHA256 = "0c3c7c805967beeeaddc71683b2351c536cdde8793121cca49be01e85a68b2fb"
RETAINED_PATH_ADDRESS = 0x006D9494
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_dev_config\pb_service_dev_config.c"
)
SYMBOLS = {
    0x00762FB0: "APP_PbRxDevCfgFrameDataProcess",
    0x00781958: "APP_PbRxErrorCode",
    0x0077A054: "APP_PbTxEncodeErrorCode",
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    return data[start - BASE : end - BASE]


def pair_digest(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def cstring(data: bytes, address: int) -> str:
    offset = address - BASE
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return data[offset:end].decode("ascii")


def thumb_bw_target(data: bytes, address: int) -> int | None:
    offset = address - BASE
    first, second = struct.unpack_from("<HH", data, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
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
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 3 or sum(map(len, bodies)) != 2646:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 286 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if image_slice(data, GAPS[-1][0], GAPS[-1][0] + 2) != b"\0\0":
        raise AuditError("tail alignment changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("f8b588b0"):
        raise AuditError("next-function boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    for address, expected in SYMBOLS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained symbol changed at 0x{address:08x}")
    assertion = image_slice(data, *ASSERT_RECORD)
    if sha256(assertion) != ASSERT_SHA256:
        raise AuditError("assertion record changed")
    if struct.unpack("<5I", assertion) != (
            0, 0, RETAINED_PATH_ADDRESS, 0x00762FB0, 45):
        raise AuditError("assertion metadata changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != [0x004D8B84, 0x004D8EEC, 0x00781974]:
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
        (0x0048EEFE, 0x004D83D8),
        (0x004D88A0, 0x004D8BE0),
        (0x004D8B72, 0x004D8DB8),
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
    if len(calls) != 172 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if len(stored) != 2 or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

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
                "components/apollo_main/core_overlay/pb_service_dev_config.c"
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
        patch = patch_by_name.get(f"replace_pb_dev_config_{suffix}")
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
    for suffix, row in zip(PATCH_SUFFIXES, rows):
        region = region_by_name.get(
            f"pb_dev_config_{suffix}_source_replacement"
        )
        if region is None or (
            region.get("target_address"), region.get("size"),
            region.get("address_status"),
        ) != (int(row["stock_start"], 0), int(row["stock_bytes"]),
              "generated_source_entry_replacement"):
            raise AuditError(
                f"production manifest replacement changed: {row['function']}"
            )
    for name, size, offset, _, region_suffix in FUNCTIONS:
        region = region_by_name.get(
            f"pb_dev_config_{region_suffix}_source_text"
        )
        if region is None or (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (3523396 + offset, size, 0x00794324 + offset,
              "source_compiled"):
            raise AuditError(f"production manifest source changed: {name}")
    retained = [item for item in main["regions"]
                if item["name"].startswith("pb_dev_config_retained_")]
    alignment = [item for item in main["regions"]
                 if item["name"].startswith("pb_dev_config_")
                 and item["name"].endswith("_source_alignment")]
    if sum(item["size"] for item in retained) != 286 or any(
            item.get("address_status") != "official_blob"
            for item in retained) or sum(
                item["size"] for item in alignment) != 4:
        raise AuditError("production retained/alignment accounting changed")

    return {
        "surface": {
            "linked_functions": 3,
            "body_bytes": 2646,
            "owned_gap_pool_bytes": 286,
            "physical_bytes": 2932,
            "assertion_records": 1,
            "direct_bl_entry_sites": 3,
            "direct_body_calls": 172,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 2,
        },
        "contracts": {
            "rx_status": {"success": 0, "null": 2, "decode_failure": 0x2B},
            "decoded_message_bytes": 0xD0,
            "commands": {
                4: "authentication", 5: "pipe_role_change",
                6: "ring_connect_info", 7: "ble_connect_param",
                8: "disconnect_info", 9: "unpair_info",
                10: "command_exception", 11: "set_device_info",
                12: "get_device_info", 13: "restore_factory_settings",
                14: "base_connect_heartbeat", 15: "quick_restart",
                128: "time_sync", 129: "audio_control",
            },
            "error_codes_logged": [1, 5, 7, 8, 9],
            "unknown_command_error": 8,
            "tx_status": {"success": 0, "encode_failure": 0x2B},
            "tx_command": 10,
            "tx_tag": 9,
            "route": 1,
            "service": 0x80,
            "message": "0x200f57b4",
            "message_bytes": 0xD0,
            "encode_buffer": "0x2037c3a0",
            "encode_capacity": 0x100,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": [row["function"] for row in rows],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 2646,
            "source_inventory_available": True,
            "source_functions": 5,
            "compiled_text_bytes": 998,
            "alignment_bytes": 4,
            "strict_relocations": 33,
            "stock_replaced_bytes": 2646,
            "retained_gap_pool_bytes": 286,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized live G2 service 0x80 master/peer BLE, timer, "
                "pairing, restart, or device-configuration workflow evidence "
                "is available; the authorized right temple is nonresponsive "
                "and the left temple must remain stock."
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
    print("G2 pb_service_dev_config audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
