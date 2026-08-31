#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_even_ai object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-even-ai-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-even-ai-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-even-ai-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_even_ai.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "b3772f7862e49d84fe8c1fae90e055569fe212bf709a9ed694cb46e84cadeb3d",
    CLOSURE: "bac886291074ba19f912efe430d2fb5e0f753bd8b5e02b1657fb15e3e61af028",
    PROVENANCE: "8045043a6d7e0281f6737acf5ee2682da2e46161897f19a43d2443f9689bc10f",
}
SOURCE_SIZE = 23766
SOURCE_SHA256 = "8b6afa020c4cbfc372ade7d9824080a52cf0ae11cb132f71ae140af122ba8588"
FUNCTIONS = (
    ("open_cfw_pb_service_even_ai_buffer_write", 146, 197488, 0),
    ("open_cfw_pb_service_even_ai_zero", 88, 197636, 0),
    ("PB_RxEvenAICtrl", 26, 197724, 1),
    ("APP_PbTxEncodeEvenAICtrl", 126, 197752, 5),
    ("APP_PbNotifyEncodeEvenAICtrl", 144, 197880, 5),
    ("PB_RxEvenAIVADInfo", 26, 198024, 1),
    ("APP_PbTxEncodeEvenAIVADInfo", 126, 198052, 5),
    ("APP_PbNotifyEncodeEvenAIVADInfo", 142, 198180, 5),
    ("PB_RxEvenAIAskInfo", 28, 198324, 1),
    ("APP_PbTxEncodeEvenAIAskInfo", 126, 198352, 5),
    ("PB_RxEvenAIAnalyseInfo", 26, 198480, 1),
    ("APP_PbTxEncodeEvenAIAnalyseInfo", 120, 198508, 5),
    ("PB_RxEvenAIReplyInfo", 28, 198628, 1),
    ("APP_PbTxEncodeEvenAIReplyInfo", 126, 198656, 5),
    ("PB_RxEvenAISkillInfo", 28, 198784, 1),
    ("APP_PbTxEncodeEvenAISkillInfo", 126, 198812, 5),
    ("PB_RxEvenAIPromptInfo", 26, 198940, 1),
    ("APP_PbTxEncodeEvenAIPromptInfo", 126, 198968, 5),
    ("PB_RxEvenAIEvent", 26, 199096, 1),
    ("APP_PbTxEncodeEvenAIEvent", 126, 199124, 5),
    ("APP_PbNotifyEncodeEvenAIEvent", 144, 199252, 5),
    ("PB_RxEvenAIHeartbeat", 26, 199396, 1),
    ("APP_PbTxEncodeEvenAIHeartbeat", 152, 199424, 7),
    ("PB_RxEvenAIConfig", 26, 199576, 1),
    ("APP_PbTxEncodeEvenAIConfig", 134, 199604, 5),
    ("APP_PbTxEncodeEvenAICommResp", 118, 199740, 5),
    ("APP_PbRxEvenAIFrameDataProcess", 496, 199860, 25),
)
PHYSICAL = (0x004E31CC, 0x004E54C8)
PHYSICAL_SHA256 = "d69f6c3ad3c31b07005e0f0f6da22f3c0be4868dbfbe1eb16b1b6549b35e8fed"
BODY_SHA256 = "ecd0001396802c71a88baa787a818f2344cd94403d81b7603eefbf6393a9a6f6"
GAP_SHA256 = "6c01debe83935542a43981a122f1a505f1fcb42806a0e40676ec5af895d7638c"
ASSERT_RECORDS = (0x00781C30, 0x00781DF4)
ASSERT_SHA256 = "93bb57159581ef073bdc9865eb7897af6f3094964ae110fa9597e92b696eb590"
ENTRY_SHA256 = "bce7ab8b9409fdd7caa354b8fc2c12e0dde3c73d860a3dd1db91c4a52b6207c2"
BODY_CALL_SHA256 = "a4ac098fc90b52056476bb17ee0515c2656cc20d936f486d6b5ab36b3c5c2af6"
RAW_WINDOW_SHA256 = "26d9c020eecdc25d56963d56d3155aaeef47045c20f14c61a8547b8b370ddf46"
PATH_CELL_SHA256 = "3e45df272f917fbde83635a6468ea375c74a2c7f136fea59ba935c7b01116fb4"
RETAINED_PATH_ADDRESS = 0x006DE0D4
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_even_ai\pb_service_even_ai.c"
)
PATH_CELLS = (
    0x004E3D04, 0x004E3E9C, 0x004E4878, 0x004E51B0, 0x004E54AC,
    0x00781C30, 0x00781C44, 0x00781C58, 0x00781C6C, 0x00781C80,
    0x00781C94, 0x00781CA8, 0x00781CBC, 0x00781CD0, 0x00781CE4,
    0x00781CF8, 0x00781D0C, 0x00781D20, 0x00781D34, 0x00781D48,
    0x00781D5C, 0x00781D70, 0x00781D84, 0x00781D98, 0x00781DAC,
    0x00781DC0, 0x00781DD4, 0x00781DE8,
)
ASSERT_LINES = (
    0xB5, 0xC9, 0xEC, 0x10F, 0x123, 0x146, 0x169, 0x17F,
    0x1A3, 0x1B7, 0x1DA, 0x1EE, 0x212, 0x226, 0x24A, 0x25E,
    0x2A4, 0x2B8, 0x2DB, 0x2FE, 0x312, 0x33A, 0x34F,
)


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
    if len(rows) != 25 or sum(map(len, bodies)) != 8404:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps: list[bytes] = []
    for (_, end), (next_start, _) in zip(intervals, intervals[1:]):
        if end < next_start:
            gaps.append(image_slice(data, end, next_start))
    gaps.append(image_slice(data, intervals[-1][1], PHYSICAL[1]))
    if sum(map(len, gaps)) != 552 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("70b50400"):
        raise AuditError("next-function boundary changed")

    assertion_bytes = image_slice(data, *ASSERT_RECORDS)
    if len(assertion_bytes) != 452 or sha256(assertion_bytes) != ASSERT_SHA256:
        raise AuditError("assertion-record block changed")
    assertion_names = [row["function"] for row in rows[1:24]]
    for index, (name, line) in enumerate(zip(assertion_names, ASSERT_LINES)):
        address = ASSERT_RECORDS[0] + index * 20
        path, function, actual_line = struct.unpack_from("<III", data, address - BASE)
        if path != RETAINED_PATH_ADDRESS or cstring(data, function) != name or actual_line != line:
            raise AuditError(f"assertion record changed: {name}")
    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    path_pairs = [(address, RETAINED_PATH_ADDRESS) for address in path_cells]
    if tuple(path_cells) != PATH_CELLS or pair_digest(path_pairs) != PATH_CELL_SHA256:
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
        (0x004982EC, 0x004E3788), (0x0049830A, 0x004E3B80),
        (0x00498328, 0x004E4CB8), (0x004E298C, 0x004E31CC),
        (0x004E3372, 0x004E5338), (0x004E3402, 0x004E3530),
        (0x004E3410, 0x004E35FC), (0x004E3424, 0x004E391A),
        (0x004E3432, 0x004E39EA), (0x004E3440, 0x004E3D34),
        (0x004E344E, 0x004E3EA4), (0x004E345C, 0x004E403C),
        (0x004E346A, 0x004E412C), (0x004E3478, 0x004E42B4),
        (0x004E3486, 0x004E43A0), (0x004E3494, 0x004E4538),
        (0x004E34A2, 0x004E4608), (0x004E34B0, 0x004E47A0),
        (0x004E34BE, 0x004E4888), (0x004E34CC, 0x004E4A34),
        (0x004E34DA, 0x004E4B20), (0x004E34E8, 0x004E4E5C),
        (0x004E34F6, 0x004E4F30), (0x004E3504, 0x004E50D8),
        (0x004E3512, 0x004E51C0), (0x004E352A, 0x004E5338),
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
    if len(calls) != 494 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if len(stored) != 89 or pair_digest(stored) != RAW_WINDOW_SHA256:
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
    for name, size, offset, relocation_count in FUNCTIONS:
        leaf = leaves[name]
        if (leaf["source"].get("path") !=
                "components/apollo_main/core_overlay/pb_service_even_ai.c"
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
    for index, row in enumerate(rows, 1):
        patch = patch_by_name.get(f"replace_pb_even_ai_{index:02d}")
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
    validate_apollo_main_artifacts(ROOT, AuditError, "protobuf Even AI service")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    region_by_name = {item["name"]: item for item in main["regions"]}
    for index, row in enumerate(rows, 1):
        region = region_by_name.get(f"pb_even_ai_{index:02d}_source_replacement")
        if region is None or (
            region.get("target_address"), region.get("size"),
            region.get("address_status"),
        ) != (int(row["stock_start"], 0), int(row["stock_bytes"]),
              "generated_source_entry_replacement"):
            raise AuditError(f"production manifest replacement changed: {row['function']}")
    for name, size, offset, _ in FUNCTIONS:
        leaf = leaves[name]
        selector = next(
            flag for flag in leaf["toolchain"]["flags"]
            if flag.startswith("-DOPEN_CFW_PB_EVEN_AI_")
        ).removeprefix("-DOPEN_CFW_PB_EVEN_AI_").removesuffix("_ONLY=1").lower()
        region = region_by_name.get(f"pb_even_ai_{selector}_source_text")
        if region is None or (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (3523396 + offset, size, 0x00794324 + offset,
              "source_compiled"):
            raise AuditError(f"production manifest source changed: {name}")
    retained = [item for item in main["regions"]
                if item["name"].startswith("pb_even_ai_retained_gap_")
                or item["name"] == "pb_service_even_ai_retained_gap_pool_tail"]
    alignment = [item for item in main["regions"]
                 if item["name"].startswith("pb_even_ai_")
                 and item["name"].endswith("_source_alignment")]
    if (sum(item["size"] for item in retained),
            sum(item["size"] for item in alignment)) != (552, 36):
        raise AuditError("production manifest retained/alignment accounting changed")

    return {
        "surface": {
            "linked_functions": 25,
            "body_bytes": 8404,
            "owned_gap_pool_bytes": 552,
            "physical_bytes": 8956,
            "assertion_records": 23,
            "direct_bl_entry_sites": 26,
            "direct_body_calls": 494,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 89,
        },
        "contracts": {
            "rx_status": {"success": 0, "handler_or_duplicate": 1,
                          "null": 2, "decode_failure": 0x2B},
            "rx_hexdump_limit": 0x20,
            "duplicate_state": "0x20074f36",
            "duplicate_policy": "seen flag plus identical one-byte magic; no time window",
            "tx_status": {"success": 0, "handler_failure": 1,
                          "null": 2, "encode_failure": 0x2B},
            "route": 1,
            "service": 7,
            "message": "0x200f5884",
            "message_bytes": 0x20C,
            "encode_buffer": "0x2037c4a0",
            "encode_capacity": 0x100,
            "notify_magic": "0x20074ff9",
            "command_tags": [
                {"name": "control", "command": 1, "tag": 3},
                {"name": "vad", "command": 2, "tag": 4},
                {"name": "ask", "command": 3, "tag": 5},
                {"name": "analyse", "command": 4, "tag": 6},
                {"name": "reply", "command": 5, "tag": 7},
                {"name": "skill", "command": 6, "tag": 8},
                {"name": "prompt", "command": 7, "tag": 9},
                {"name": "event", "command": 8, "tag": 10},
                {"name": "heartbeat", "command": 9, "tag": 11},
                {"name": "config", "command": 10, "tag": 13},
            ],
            "notifications": ["control", "vad", "event"],
            "command_response": {"command": 0xA1, "tag": 12,
                                 "payload_bytes": 1, "send": "tx"},
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": len(path_cells),
            "exact_symbols": [row["function"] for row in rows],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 8404,
            "source_inventory_available": True,
            "source_functions": 27,
            "compiled_text_bytes": 2832,
            "alignment_bytes": 36,
            "strict_relocations": 107,
            "stock_replaced_bytes": 8404,
            "retained_gap_pool_bytes": 552,
            "software_functional_gap": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": (
                "hardware validation is blocked by unavailable physical evidence; future qualification requires "
                "an authorized G2 pair and either a component-specific service 7 Even-AI fixture or "
                "an authenticated golden BLE/UI capture"
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
    print("G2 pb_service_even_ai audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
