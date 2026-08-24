#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_dev_setting object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-dev-setting-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-dev-setting-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-dev-setting-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_dev_setting.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "089228c6fa53e296dd6384441b97b7016b886d2a918da2b6d93174aeff6e13be",
    CLOSURE: "3f2ecb318601b373b1cff284fe0811d629e1d29645bd56eb519950de54f868c4",
    PROVENANCE: "b9821581cacebb933823382d712c4ba120cf29b0890b5329872900e868b42b1d",
}
SOURCE_SIZE = 15562
SOURCE_SHA256 = "bfb6a066ccb43b91f0d026cbc26078ecead559297d7289bacd52a389f5193215"
FUNCTIONS = (
    ("open_cfw_pb_service_dev_setting_buffer_write", 148, 207380, 0,
     "buffer_write"),
    ("open_cfw_pb_service_dev_setting_transmit", 212, 207528, 5,
     "transmit"),
    ("PB_RxRestoreFactory", 140, 207740, 14, "rx_restore"),
    ("PB_TxEncodeRestoreFactory", 52, 207880, 1, "tx_restore"),
    ("PB_RxQuickRestart", 18, 207932, 1, "rx_restart"),
    ("PB_TxEncodeQuickRestart", 52, 207952, 1, "tx_restart"),
    ("PB_RxBaseConnHeartBeat", 20, 208004, 1, "rx_heartbeat"),
    ("PB_TxEncodeBaseConnHeartBeat", 52, 208024, 1, "tx_heartbeat"),
    ("PB_RxTimeSyncInfo", 84, 208076, 3, "rx_time"),
    ("PB_TxEncodeTimeSyncInfo", 84, 208160, 2, "tx_time"),
    ("PB_RxAudControl", 10, 208244, 0, "rx_audio"),
    ("PB_TxEncodeAudControl", 62, 208256, 1, "tx_audio"),
)
PATCH_SUFFIXES = (
    "rx_restore", "tx_restore", "rx_restart", "tx_restart",
    "rx_heartbeat", "tx_heartbeat", "rx_time", "tx_time", "rx_audio",
    "tx_audio",
)
PHYSICAL = (0x00542DC4, 0x00543C48)
PHYSICAL_SHA256 = "f65791291601ac4dc39715a64b3efbe361a6df101a3c691d6aa17af680abfd99"
BODY_SHA256 = "dc1d832025cc77165d7be3e84a37074fb244e78fe6558f2b0941a048f0404d04"
GAPS = (
    (0x005436CE, 0x005436F0, "1d5b33a427fa05efb031aef84f8bcabedf2cac7c40a0df111218fd3c1753966b"),
    (0x00543908, 0x00543918, "3dd43fb96bd93b873c1b468442cc79c4bbcc619c070a297886c9ec9f71be5526"),
    (0x005439BA, 0x005439E4, "c3a84191f0d2939c2b6a0b932fa2dc141cd64e5e43aa3ee286e9384c2d59671b"),
    (0x00543B88, 0x00543C48, "57e4e19f43f30600c4733813598afd5f422138b530bbb1b15c7d294b855c6f96"),
)
GAP_SHA256 = "021cd839f9bdc85358f25bf9340d0662e6bc736b41b35786c3604ba374de0cdc"
ASSERT_RECORDS = (0x007819F8, 0x00781B88)
ASSERT_SHA256 = "a513de66ae1940cd5f522095ab144e1a957e434893d10f387c6c6fab0228e318"
ENTRY_SHA256 = "1c23bf7a1acaecbaadb20d2f7a9da65ff3962c4ea85fdd685e0cc16143ad9192"
BODY_CALL_SHA256 = "c93696123aa2ac6808f9d7751e6ff0c303e3f7f7c2f23deb1c32f291ab5271a0"
RAW_WINDOW_SHA256 = "3bc5d2956ccaf1a1947f827f00af261140e0795c07a182523f725884224e45be"
RETAINED_PATH_ADDRESS = 0x006D94FC
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_dev_config\pb_service_dev_setting.c"
)
ASSERTIONS = (
    (0x00781980, "PB_RxRestoreFactory", 90),
    (0x0076F534, "PB_TxEncodeRestoreFactory", 137),
    (0x0076F534, "PB_TxEncodeRestoreFactory", 138),
    (0x0076F534, "PB_TxEncodeRestoreFactory", 139),
    (0x007819A8, "PB_RxQuickRestart", 172),
    (0x0077A0FC, "PB_TxEncodeQuickRestart", 189),
    (0x0077A0FC, "PB_TxEncodeQuickRestart", 190),
    (0x0077A0FC, "PB_TxEncodeQuickRestart", 191),
    (0x0077A114, "PB_RxBaseConnHeartBeat", 224),
    (0x00763190, "PB_TxEncodeBaseConnHeartBeat", 240),
    (0x00763190, "PB_TxEncodeBaseConnHeartBeat", 241),
    (0x00763190, "PB_TxEncodeBaseConnHeartBeat", 242),
    (0x007819BC, "PB_RxTimeSyncInfo", 276),
    (0x0077A144, "PB_TxEncodeTimeSyncInfo", 299),
    (0x0077A144, "PB_TxEncodeTimeSyncInfo", 300),
    (0x0077A144, "PB_TxEncodeTimeSyncInfo", 301),
    (0x00787D60, "PB_RxAudControl", 338),
    (0x0077A15C, "PB_TxEncodeAudControl", 354),
    (0x0077A15C, "PB_TxEncodeAudControl", 355),
    (0x0077A15C, "PB_TxEncodeAudControl", 356),
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
    if len(rows) != 10 or sum(map(len, bodies)) != 3432:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 284 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("70b54024"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    assertions = image_slice(data, *ASSERT_RECORDS)
    if sha256(assertions) != ASSERT_SHA256:
        raise AuditError("assertion records changed")
    for index, (symbol, name, line) in enumerate(ASSERTIONS):
        if cstring(data, symbol) != name:
            raise AuditError(f"retained symbol changed: {name}")
        if struct.unpack_from("<5I", assertions, index * 20) != (
                0, 0, RETAINED_PATH_ADDRESS, symbol, line):
            raise AuditError(f"assertion metadata changed: {name}/{line}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    expected_path_cells = [0x005436DC, 0x00543BF4] + list(range(0x00781A00, 0x00781B7D, 20))
    if path_cells != expected_path_cells:
        raise AuditError("retained path-pointer closure changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entry: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    bw: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts or target in interiors:
            bw.append((site, target))
    expected_entry = [
        (0x004D8964, 0x00542DC4), (0x004D897E, 0x00542F38),
        (0x004D89C6, 0x00543378), (0x004D89F6, 0x00543426),
        (0x004D8A3E, 0x005430FC), (0x004D8A58, 0x005431B4),
        (0x004D8AA0, 0x005435DE), (0x004D8ABA, 0x005436F0),
        (0x004D8B02, 0x00543918), (0x004D8B1C, 0x005439E4),
    ]
    if entry != expected_entry or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("direct entry closure changed")
    if interior or bw:
        raise AuditError("direct strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 222 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if stored != [(0x006432F7, 0x00543A00)] or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

    if struct.unpack_from("<I", data, 0x00543BD0 - BASE)[0] != 0x20004394:
        raise AuditError("time-sync cache global changed")

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
                "components/apollo_main/core_overlay/pb_service_dev_setting.c"
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
        patch = patch_by_name.get(f"replace_pb_dev_setting_{suffix}")
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
        240692, "2db11ff707bf253280eb07667c3d76954347cc9e31796c7589faf788fed629ae",
        3764088, "b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed",
    ):
        raise AuditError("production build pins changed")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    if (main["provider"].get("size"), main["provider"].get("sha256"),
            manifest["package"].get("expected_size"),
            manifest["package"].get("expected_sha256")) != (
        3764088, "b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed",
        4542582, "275a9e691c0bad851f7adbc80ed2abc1580e13d67f031912e198f984d18f7f85",
    ):
        raise AuditError("production manifest pins changed")
    region_by_name = {item["name"]: item for item in main["regions"]}
    for suffix, row in zip(PATCH_SUFFIXES, rows):
        region = region_by_name.get(
            f"pb_dev_setting_{suffix}_source_replacement"
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
        region = region_by_name.get(f"pb_dev_setting_{suffix}_source_text")
        if region is None or (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (3523396 + offset, size, 0x00794324 + offset,
              "source_compiled"):
            raise AuditError(f"production manifest source changed: {name}")
    retained = [item for item in main["regions"]
                if item["name"].startswith("pb_dev_setting_retained_gap_")]
    alignment = [item for item in main["regions"]
                 if item["name"].startswith("pb_dev_setting_")
                 and item["name"].endswith("_source_alignment")]
    if sum(item["size"] for item in retained) != 284 or any(
            item.get("address_status") != "official_blob"
            for item in retained) or sum(
                item["size"] for item in alignment) != 6:
        raise AuditError("production retained/alignment accounting changed")

    return {
        "surface": {
            "linked_functions": 10, "body_bytes": 3432,
            "owned_gap_pool_bytes": 284, "physical_bytes": 3716,
            "assertion_records": 20, "direct_bl_entry_sites": 10,
            "direct_body_calls": 222, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 1,
        },
        "contracts": {
            "rx_status": {"success": 0, "null": 2},
            "tx_status": {"success": 0, "null": 2, "encode_failure": 0x2B},
            "commands": {0x0D: "restore_factory_tag_0x0c",
                         0x0E: "base_heartbeat_tag_0x0d",
                         0x0F: "quick_restart_tag_0x0e",
                         0x80: "time_sync_tag_0x80",
                         0x81: "audio_control_tag_0x81"},
            "route": 1, "service": 0x80,
            "time_sync_cache": "0x20004394", "time_sync_bytes": 5,
            "transmit_buffers": "caller_owned",
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{value:08x}" for value in path_cells],
            "exact_symbols": list(dict.fromkeys(name for _, name, _ in ASSERTIONS)),
            "assertion_lines": [line for _, _, line in ASSERTIONS],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "source_inventory_available": True,
            "production_routed": True,
            "ownership_bytes": 3432,
            "source_functions": 12,
            "compiled_text_bytes": 934,
            "alignment_bytes": 6,
            "strict_relocations": 30,
            "stock_replaced_bytes": 3432,
            "retained_gap_pool_bytes": 284,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized live G2 service 0x80 device-setting peer BLE, "
                "factory-reset, quick-restart, base-heartbeat, clock-sync, "
                "persistence, or audio-control workflow evidence is available; "
                "the authorized right temple is nonresponsive and the left "
                "temple must remain stock."
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 pb_service_dev_setting audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service_dev_setting audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
