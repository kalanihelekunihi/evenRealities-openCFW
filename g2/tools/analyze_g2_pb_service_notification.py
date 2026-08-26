#!/usr/bin/env python3
"""Fail-closed stock and production audit of G2 pb_service_notification."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-notification-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-notification-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-notification-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_notification.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "ca96883bab42fed8afd3f30efde0392ee7ee5f0e7fdeb98f1bca38653885289f",
    CLOSURE: "d9a1b20365e43d8d87281635186cee65d665a34dddf422e02828676daa444254",
    PROVENANCE: "0815221acf1a5d38397f6db41eb896f291f5bc90c415ebcc29b1088373dafb93",
}
SOURCE_SIZE = 11668
SOURCE_SHA256 = "e99566f9d7cf6c3fd00c4c0cad332600a7e2a6f6c85f55101c409780fb8e31bc"
FUNCTIONS = (
    ("open_cfw_pb_service_notification_buffer_write", 146, 264220, 0,
     "buffer_write"),
    ("open_cfw_pb_service_notification_zero", 88, 264368, 0, "zero"),
    ("open_cfw_pb_notification_encode_and_send", 258, 264456, 6,
     "common_encode"),
    ("PB_RxNotifCtrl", 48, 264716, 4, "control_rx"),
    ("APP_PbTxEncodeNotifCtrl", 10, 264764, 1, "control_tx"),
    ("APP_PbTxEncodeNotifCommResp", 10, 264776, 1, "comm_response"),
    ("APP_PbTxEncodeNotifAppIDNotInWhitelist", 520, 264788, 9,
     "app_not_whitelisted"),
    ("PB_RxNotifWhitelistCtrl", 26, 265308, 1, "whitelist_control_rx"),
    ("APP_PbTxEncodeNotifWhitelistCtrl", 10, 265336, 1,
     "whitelist_control_tx"),
    ("PB_RxNotifWhitelistChk", 10, 265348, 0, "whitelist_check_rx"),
    ("APP_PbTxEncodeNotifWhitelistChk", 10, 265360, 1,
     "whitelist_check_tx"),
    ("APP_PbRxNotificationFrameDataProcess", 190, 265372, 10,
     "dispatch"),
)
PATCH_SUFFIXES = (
    "dispatch", "rx_ctrl", "tx_ctrl", "tx_comm_resp", "notify_app",
    "rx_whitelist_ctrl", "tx_whitelist_ctrl", "rx_whitelist_check",
    "tx_whitelist_check",
)
MANIFEST_PATCH_SUFFIXES = (
    "dispatch", "control_rx", "control_tx", "comm_response",
    "app_not_whitelisted", "whitelist_control_rx", "whitelist_control_tx",
    "whitelist_check_rx", "whitelist_check_tx",
)
PHYSICAL = (0x004D6BA8, 0x004D798C)
PHYSICAL_SHA256 = "367b877b9bd7c1c6c23beee8a5d6b14b37e6f2548437b25706edb75a20959701"
BODY_SHA256 = "167ff554f205c1df565617756cf9321ccab7fcbc9bded302080997562cdd183b"
GAPS = (
    (0x004D7618, 0x004D7624, "0e0a0df2c06c5dbb65c264f8710f2ee45cf98ea66d30c23ad4325423fe5a89d6"),
    (0x004D768E, 0x004D76CC, "14790d091b374862a2febf1485275bf2ec75a702577239ec9b03062d02beb64b"),
    (0x004D78E8, 0x004D798C, "072816f3b035dd1a76dacf79e1e7ce6bc9453a462bfe7e89a98630c96a1b374f"),
)
GAP_SHA256 = "4b85b9eedc1ef5fcbddaef6215a002a83668c0af083342d881909b3a97cd6396"
ASSERT_RECORDS = (0x00781F70, 0x00781FFC)
ASSERT_SHA256 = "161417e51a66aeaa4f2ea3ca5b42418fda0675501724f700470773aca07701fe"
ENTRY_SHA256 = "f9efdb318b09dde46e31faacc772db3542dd7bdf10e46b7c0e5ef0420780e548"
BODY_CALL_SHA256 = "f1d24070c23cd5575c88b4b72c8c0c7e05e1ce1a332a77fb8e01bc25fcfa4d5e"
RAW_WINDOW_SHA256 = "31719b21bdb9c3a1c53b65141375d54b89dd3c3cdd4d38260ecae886d85310b0"
RETAINED_PATH_ADDRESS = 0x006D7B88
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_notification\pb_service_notification.c"
)
EXACT_SYMBOLS = (
    (0x0074C3B4, "APP_PbRxNotificationFrameDataProcess"),
    (0x0074C3DC, "APP_PbTxEncodeNotifAppIDNotInWhitelist"),
)
ASSERT_SYMBOLS = (
    (0x00787E10, "PB_RxNotifCtrl", 103),
    (0x0077A3B4, "APP_PbTxEncodeNotifCtrl", 122),
    (0x0076F72C, "APP_PbTxEncodeNotifCommResp", 160),
    (0x0077A3FC, "PB_RxNotifWhitelistCtrl", 243),
    (0x00757AC4, "APP_PbTxEncodeNotifWhitelistCtrl", 259),
    (0x0077A444, "PB_RxNotifWhitelistChk", 296),
    (0x00763590, "APP_PbTxEncodeNotifWhitelistChk", 312),
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
    if len(rows) != 9 or sum(map(len, bodies)) != 3318:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 238 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("70b50500"):
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
            raise AuditError(f"assertion metadata changed: {name}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != [0x004D7690, 0x004D7970, 0x00781F78, 0x00781F8C,
                      0x00781FA0, 0x00781FB4, 0x00781FC8, 0x00781FDC,
                      0x00781FF0]:
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
        (0x0048E2B2, 0x004D6BA8), (0x004BF516, 0x004D71BC),
        (0x004D6D40, 0x004D6DB0), (0x004D6D4E, 0x004D6EA2),
        (0x004D6D5C, 0x004D73D6), (0x004D6D6A, 0x004D749A),
        (0x004D6D78, 0x004D7624), (0x004D6D86, 0x004D76CC),
        (0x004D6DA6, 0x004D7038), (0x004E1B8E, 0x004D6BA8),
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
    if len(calls) != 202 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    expected_stored = [(0x005B2B75, 0x004D70B5),
                       (0x006A405F, 0x004D7100),
                       (0x006A4087, 0x004D7100)]
    if stored != expected_stored or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

    literal_checks = {
        0x004D78F8: 0x2037C7A0, 0x004D78FC: 0x200F60E0,
        0x004D76A0: 0x007799F4, 0x004D792C: 0x007799F4,
    }
    if any(struct.unpack_from("<I", data, address - BASE)[0] != value
           for address, value in literal_checks.items()):
        raise AuditError("notification workspace/descriptor closure changed")

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
                "components/apollo_main/core_overlay/pb_service_notification.c"
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
        patch = patch_by_name.get(f"replace_pb_notification_{suffix}")
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
    for suffix, row in zip(MANIFEST_PATCH_SUFFIXES, rows):
        region = region_by_name.get(
            f"pb_notification_{suffix}_source_replacement"
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
            f"pb_notification_{region_suffix}_source_text"
        )
        if region is None or (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (3523396 + offset, size, 0x00794324 + offset,
              "source_compiled"):
            raise AuditError(f"production manifest source changed: {name}")
    retained = [item for item in main["regions"]
                if item["name"].startswith("pb_notification_")
                and item["name"].endswith("_gap")]
    alignment = [item for item in main["regions"]
                 if item["name"].startswith("pb_notification_")
                 and item["name"].endswith("_source_alignment")]
    if sum(item["size"] for item in retained) != 238 or any(
            item.get("address_status") != "official_blob"
            for item in retained) or sum(
                item["size"] for item in alignment) != 16:
        raise AuditError("production retained/alignment accounting changed")

    return {
        "surface": {
            "linked_functions": 9, "body_bytes": 3318,
            "owned_gap_pool_bytes": 238, "physical_bytes": 3556,
            "assertion_records": 7, "direct_bl_entry_sites": 10,
            "direct_body_calls": 202, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 3,
        },
        "contracts": {
            "rx_status": {"success": 0, "null": 2, "decode_failure": 0x2B},
            "tx_status": {"success": 0, "null_or_alloc_failure": 2,
                          "encode_failure": 0x2B, "notify_failure": -1},
            "commands": {1: "control_tag_3", 2: "app_not_whitelisted_tag_4",
                         3: "whitelist_control_tag_6", 4: "whitelist_check_tag_7",
                         0xA1: "generic_response_tag_5"},
            "whitelist_check_status": {"cache_invalid": 1, "match": 2,
                                       "mismatch": 3},
            "route": 1, "service": 4,
            "message": "0x200f60e0", "message_bytes": 0x4C,
            "encode_buffer": "0x2037c7a0", "encode_capacity": 0x100,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{value:08x}" for value in path_cells],
            "exact_symbols": [name for _, name in EXACT_SYMBOLS]
                             + [name for _, name, _ in ASSERT_SYMBOLS],
            "assertion_lines": [line for _, _, line in ASSERT_SYMBOLS],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 3318,
            "source_inventory_available": True,
            "source_functions": 12,
            "compiled_text_bytes": 1326,
            "alignment_bytes": 16,
            "strict_relocations": 34,
            "stock_replaced_bytes": 3318,
            "retained_gap_pool_bytes": 238,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized live G2 service 0x04 peer BLE, notification-"
                "control, whitelist-control, whitelist-check, or app-not-"
                "whitelisted workflow evidence is available; the authorized "
                "right temple is nonresponsive and the left temple must "
                "remain stock."
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 pb_service_notification audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service_notification audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
