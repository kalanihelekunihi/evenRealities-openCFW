#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_pair_mgr object."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-pair-mgr-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-pair-mgr-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-pair-mgr-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_pair_mgr.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "39f32fa929beeee0bcbd02272291cfbe7a5c7555f31ad8e8a35ed8f81cf21c05",
    CLOSURE: "5c3443af0269577e98e4ae8da5c822079903554f4073584a1f46eeb6f0d05251",
    PROVENANCE: "73a32c8d1ab4113b76a5b180d6c07adb27a91a7e93d0f3fb8530a770aec5089d",
}
SOURCE_SIZE = 27565
SOURCE_SHA256 = "f1d4fbadb79d34d8bacd62f7d94221236279637d55d6d7fc4401e96111ec5b3e"
FUNCTIONS = (
    ("open_cfw_pb_service_pair_mgr_buffer_write", 166, 209396, 0,
     "open_cfw_pb_service_pair_mgr_buffer_write"),
    ("pairMgrSecAuthFlagSet", 12, 209564, 0,
     "pair_mgr_sec_auth_flag_set"),
    ("pairMgrSecAuthFlagGet", 12, 209576, 0,
     "pair_mgr_sec_auth_flag_get"),
    ("PB_RxSecAuth", 106, 209588, 9, "pb_rx_sec_auth"),
    ("PB_TxEncodeSecAuth", 130, 209696, 4, "pb_tx_encode_sec_auth"),
    ("PB_TxEncodeNotifySecAuthImpl", 342, 209828, 9,
     "pb_tx_encode_notify_sec_auth_impl"),
    ("PB_RxPipeRoleChange", 20, 210172, 1, "pb_rx_pipe_role_change"),
    ("PB_TxEncodePipeRoleChange", 130, 210192, 4,
     "pb_tx_encode_pipe_role_change"),
    ("_PB_RxRingConnectInfoOwnerExecute", 192, 210324, 22,
     "pb_rx_ring_connect_info_owner_execute"),
    ("_PB_RxRingConnectInfoCommon", 52, 210516, 3,
     "pb_rx_ring_connect_info_common"),
    ("PB_RxRingConnectInfo", 6, 210568, 1, "pb_rx_ring_connect_info"),
    ("PB_LastTxEncodeRingConnectInfoTimeSet", 10, 210576, 1,
     "pb_last_tx_encode_ring_connect_info_time_set"),
    ("PB_TxEncodeRingConnectInfo", 132, 210588, 4,
     "pb_tx_encode_ring_connect_info"),
    ("PB_TxEncodeNotifyRingConnectInfoImpl", 364, 210720, 13,
     "pb_tx_encode_notify_ring_connect_info_impl"),
    ("PB_TxEncodeNotifyRingConnectInfo", 60, 211084, 3,
     "pb_tx_encode_notify_ring_connect_info"),
    ("PB_RxBleConnectParams", 38, 211144, 2, "pb_rx_ble_connect_params"),
    ("PB_TxEncodeBleConnectParams", 130, 211184, 4,
     "pb_tx_encode_ble_connect_params"),
    ("PB_RxDisconnectInfo", 52, 211316, 4, "pb_rx_disconnect_info"),
    ("PB_TxEncodeDisconnectInfo", 130, 211368, 4,
     "pb_tx_encode_disconnect_info"),
    ("PB_RxUnpairInfo", 86, 211500, 5, "pb_rx_unpair_info"),
    ("PB_TxEncodeUnpairInfo", 130, 211588, 4,
     "pb_tx_encode_unpair_info"),
)
PHYSICAL = (0x004BB3DC, 0x004BD054)
PHYSICAL_SHA256 = "563a40809c252f16286eba50c48c5ec70086a0ac925e7b0d1344f8cb5fb5f79d"
BODY_SHA256 = "959c59f6d2ef16c33f05f2084595c5eaf29ced61bb6d85354df45a94e784c94d"
GAPS = (
    (0x004BB92A, 0x004BB9B4, "c25a63977cbb4ba020fa1054bab02efe64d47d69831bd43103f0191e92c0b32b"),
    (0x004BBD96, 0x004BBDBC, "28b780869bb2c98f6341eaa2b38b9b90ffc0d392157ae23674c0a58ad82ec51a"),
    (0x004BBF2A, 0x004BBF38, "76ca8066df20526595a64be9a91941e92bfb0c889b2323aaa8d466e9271dd5e3"),
    (0x004BBF94, 0x004BBFBC, "fae253d45c1d41088a3a8a210abf342f391cb0c79d2115433e257b0b50d75f44"),
    (0x004BC188, 0x004BC1B4, "2cb1fbaa756f225ac32e6aaba4fbc31c7c5cc39426c95aaa6037a82857decc5b"),
    (0x004BC414, 0x004BC418, "dd0b9325144cce50cd7c207af268d2db1db73004117c4ceeeba078c76effff04"),
    (0x004BC4A2, 0x004BC4BC, "e54ca3f218f02d9d31b47f65ab36ab4a7afabb161a168170597ee529badda10e"),
    (0x004BC5A2, 0x004BC5C8, "dca4223bfc4b976e2624e2d465b1c198155a51923a0f1174b7ecd63967602392"),
    (0x004BC786, 0x004BC7D4, "e37e439c114c9de0b3bb7011541a605345b4c097c2f51dc5f809c42be22df89c"),
    (0x004BC90C, 0x004BC93C, "c7656b1fc43f06df9a73e6ea25d2dd5b4731bc481762cc7a93f475e1f88ece57"),
    (0x004BCB04, 0x004BCB28, "de6dea6a883a2d9fede298bae6f3d9c86aad9efd5ac42374ea66be5db2b47e4b"),
    (0x004BCDD8, 0x004BCDFC, "9212a8152be2138b9705d9ce946f348193aabbf7442ee7496b40ec6c3c055f62"),
    (0x004BCF9C, 0x004BD054, "754d54603bf284451cb17ab3f2fa5bcdd6436c2a96896969ecd6e53d525e8f08"),
)
GAP_SHA256 = "91fd838ab679b32d0c207f7fbdcb6b98a0a8c630d910e5f1fd307597eb060c91"
ASSERT_RECORDS = (0x0078213C, 0x00782308)
ASSERT_SHA256 = "a350a1e6fc4d921d078979d9a3ca0134358a12242c26507e70f8532e72a4877d"
ENTRY_SHA256 = "3b2aee8a4e2c6e27fec3a9e8161a4137031020a2a7055e2a1fbd0d7f96dceef7"
BODY_CALL_SHA256 = "1827b133f87bd571a8abdab17b2116092d18c442d7b45fdf771094d032eec320"
RAW_WINDOW_SHA256 = "2ead83783da252672f4ccc07b88d9ae1965dd4a8f0529912f5392557752d7726"
RETAINED_PATH_ADDRESS = 0x006DB290
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_dev_config\pb_service_pair_mgr.c"
)
EXACT_SYMBOLS = (
    (0x00763650, "PB_TxEncodeNotifySecAuthImpl"),
    (0x0076F7F0, "PB_TxEncodeNotifySecAuth"),
    (0x00757C08, "_PB_RxRingConnectInfoOwnerExecute"),
    (0x0076F844, "_PB_RxRingConnectInfoCommon"),
    (0x0074C4F4, "PB_LastTxEncodeRingConnectInfoTimeSet"),
    (0x0074C51C, "PB_TxEncodeNotifyRingConnectInfoImpl"),
    (0x00757C50, "PB_TxEncodeNotifyRingConnectInfo"),
)
ASSERT_SYMBOLS = (
    (0x00787E50, "PB_RxSecAuth", 62),
    (0x007820B0, "PB_TxEncodeSecAuth", 95),
    (0x007820B0, "PB_TxEncodeSecAuth", 96),
    (0x007820B0, "PB_TxEncodeSecAuth", 97),
    (0x007820D8, "PB_RxPipeRoleChange", 210),
    (0x0076F828, "PB_TxEncodePipeRoleChange", 227),
    (0x0076F828, "PB_TxEncodePipeRoleChange", 228),
    (0x0076F828, "PB_TxEncodePipeRoleChange", 229),
    (0x0076F87C, "PB_TxEncodeRingConnectInfo", 371),
    (0x0076F87C, "PB_TxEncodeRingConnectInfo", 372),
    (0x0076F87C, "PB_TxEncodeRingConnectInfo", 373),
    (0x0077A51C, "PB_RxBleConnectParams", 485),
    (0x0076F898, "PB_TxEncodeBleConnectParams", 506),
    (0x0076F898, "PB_TxEncodeBleConnectParams", 507),
    (0x0076F898, "PB_TxEncodeBleConnectParams", 508),
    (0x00782100, "PB_RxDisconnectInfo", 589),
    (0x0076F8EC, "PB_TxEncodeDisconnectInfo", 618),
    (0x0076F8EC, "PB_TxEncodeDisconnectInfo", 619),
    (0x0076F8EC, "PB_TxEncodeDisconnectInfo", 620),
    (0x00787E60, "PB_RxUnpairInfo", 665),
    (0x0077A564, "PB_TxEncodeUnpairInfo", 710),
    (0x0077A564, "PB_TxEncodeUnpairInfo", 711),
    (0x0077A564, "PB_TxEncodeUnpairInfo", 712),
)


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
    if len(rows) != 20 or sum(map(len, bodies)) != 6564:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 724 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("1cb50400"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    for address, name in EXACT_SYMBOLS:
        if cstring(data, address) != name:
            raise AuditError(f"retained symbol changed: {name}")
    assertions = image_slice(data, *ASSERT_RECORDS)
    if sha256(assertions) != ASSERT_SHA256:
        raise AuditError("assertion records changed")
    for index, (symbol, name, line) in enumerate(ASSERT_SYMBOLS):
        if cstring(data, symbol) != name:
            raise AuditError(f"retained assertion symbol changed: {name}")
        if struct.unpack_from("<5I", assertions, index * 20) != (
                0, 0, RETAINED_PATH_ADDRESS, symbol, line):
            raise AuditError(f"assertion metadata changed: {name}/{line}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    expected_path_cells = [0x004BBDA4, 0x004BC7A0, 0x004BCFA0]
    expected_path_cells += list(range(0x00782144, 0x00782300, 20))
    if path_cells != expected_path_cells:
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
        (0x0046EC38, 0x004BB73A), (0x0046ECE0, 0x004BC1B4),
        (0x004729D0, 0x004BC418), (0x0049F54C, 0x004BC418),
        (0x004B772A, 0x004BB9B4), (0x004B7730, 0x004BBF44),
        (0x004B77C8, 0x004BB9B4), (0x004B7B16, 0x004BB9BC),
        (0x004B7B9C, 0x004BB9B4), (0x004B7D02, 0x004BC418),
        (0x004BB52A, 0x004BB9B4), (0x004BBF22, 0x004BBC54),
        (0x004BBF3E, 0x004BBDBC), (0x004D861E, 0x004BB3DC),
        (0x004D863A, 0x004BB576), (0x004D868A, 0x004BB9C4),
        (0x004D86A6, 0x004BBAA0), (0x004D86F6, 0x004BBF38),
        (0x004D8712, 0x004BBFBC), (0x004D8762, 0x004BC4BC),
        (0x004D877E, 0x004BC5C8), (0x004D87CE, 0x004BC7D4),
        (0x004D87EA, 0x004BC93C), (0x004D883A, 0x004BCB28),
        (0x004D8856, 0x004BCDFC),
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
    if len(calls) != 418 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    expected_stored = [
        (0x00472C40, 0x004BC419), (0x0049F7C0, 0x004BC419),
        (0x004A1648, 0x004BC419), (0x004A2360, 0x004BC419),
        (0x004A34FC, 0x004BC419), (0x004B8470, 0x004BC419),
        (0x005E5209, 0x004BCCF8),
    ]
    if stored != expected_stored or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior pointer closure changed")
    stored_entries = [(site, value) for site, value in stored
                      if (value & ~1) in starts]
    if len(stored_entries) != 6 or any(value != 0x004BC419
                                       for _, value in stored_entries):
        raise AuditError("stored notification callback closure changed")

    literal_checks = {
        0x004BC188: 0x20074FFC,
        0x004BBFA8: 0x007766DC,
        0x004BC920: 0x007766DC,
        0x004BCFE0: 0x007766DC,
    }
    if any(struct.unpack_from("<I", data, address - BASE)[0] != value
           for address, value in literal_checks.items()):
        raise AuditError("pair-manager flag/descriptor closure changed")

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
                "components/apollo_main/core_overlay/pb_service_pair_mgr.c"
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
    for row in rows:
        patch = patch_by_name.get(f"replace_pb_pair_mgr_{row['recovery_order']}")
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
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    validate_apollo_main_artifacts(ROOT, AuditError, "protobuf pair manager")
    region_by_name = {item["name"]: item for item in main["regions"]}
    suffix_by_function = {
        name: suffix for name, _, _, _, suffix in FUNCTIONS
    }
    for row in rows:
        suffix = suffix_by_function[row["function"]]
        region = region_by_name.get(
            f"pb_pair_mgr_{suffix}_source_replacement"
        )
        if region is None or (
            region.get("target_address"), region.get("size"),
            region.get("address_status"),
        ) != (int(row["stock_start"], 0), int(row["stock_bytes"]),
              "generated_source_entry_replacement"):
            raise AuditError(
                f"production manifest replacement changed: {row['function']}"
            )
    for name, size, offset, _, suffix in FUNCTIONS:
        region = region_by_name.get(f"pb_pair_mgr_{suffix}_source_text")
        if region is None or (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (3523396 + offset, size, 0x00794324 + offset,
              "source_compiled"):
            raise AuditError(f"production manifest source changed: {name}")
    retained = [region_by_name.get(f"pb_pair_mgr_retained_gap_{index:02d}")
                for index in range(2, 15)]
    retained_intervals = [
        (item["target_address"], item["target_address"] + item["size"])
        for item in retained if item is not None
    ]
    if (any(item is None for item in retained)
            or retained_intervals != [(start, end) for start, end, _ in GAPS]
            or any(item.get("address_status") != "official_blob"
                   for item in retained if item is not None)):
        raise AuditError("production retained-gap accounting changed")
    alignment = [item for item in main["regions"]
                 if item["name"].startswith("pb_pair_mgr_")
                 and item["name"].endswith("_source_alignment")]
    if sum(item["size"] for item in alignment) != 22:
        raise AuditError("production source alignment accounting changed")

    return {
        "surface": {
            "linked_functions": 20, "path_correlated_anchors": 17,
            "restored_helpers": 3, "body_bytes": 6564,
            "owned_gap_pool_bytes": 724, "physical_bytes": 7288,
            "assertion_records": 23, "direct_bl_entry_sites": 25,
            "direct_body_calls": 418, "stored_exact_entry_pointers": 6,
            "strict_interior_ingress": 0, "raw_instruction_windows": 1,
        },
        "contracts": {
            "rx_status": {"success": 0, "null": 2},
            "tx_status": {"success": 0, "null_or_alloc_failure": 2,
                          "encode_failure": 0x2B, "notify_failure": -1},
            "commands": {4: "security_auth_tag_3", 5: "pipe_role_tag_4",
                         6: "ring_connect_tag_5", 7: "ble_params_tag_6",
                         8: "disconnect_tag_7", 9: "unpair_tag_8"},
            "route": 1, "service": 0x80,
            "notification_allocation_bytes": 0x1A8,
            "security_auth_flag": "0x20074ffc", "ring_mac_bytes": 6,
            "stored_notification_callback": "0x004bc419",
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{value:08x}" for value in path_cells],
            "exact_symbols": [name for _, name in EXACT_SYMBOLS]
                             + list(dict.fromkeys(name for _, name, _ in ASSERT_SYMBOLS)),
            "assertion_lines": [line for _, _, line in ASSERT_SYMBOLS],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "source_inventory_available": True,
            "production_routed": True, "ownership_bytes": 6564,
            "source_functions": 21,
            "compiled_text_bytes": 2300,
            "alignment_bytes": 22,
            "strict_relocations": 97,
            "stock_replaced_bytes": 6564,
            "retained_gap_pool_bytes": 724,
            "software_functional_gap": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": (
                "hardware validation is blocked by unavailable physical evidence; future qualification requires "
                "an authorized G2 pair and either a component-specific pair-manager fixture or an "
                "authenticated golden security-auth, pipe-role, ring-connect, BLE-parameter, disconnect, "
                "and unpair workflow capture"
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 pb_service_pair_mgr audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service_pair_mgr audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
