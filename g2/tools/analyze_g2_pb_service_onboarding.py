#!/usr/bin/env python3
"""Fail-closed stock and production audit of G2 pb_service_onboarding."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-onboarding-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-onboarding-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-onboarding-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_onboarding.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "434c303d40090d2db952e2e87cd479a9d7c6b24a86950b370ed1ae84fbae86f2",
    CLOSURE: "93c2b4f62c82c37c0486ccda7702471293fa3eb77163bb8f29c321efdecde914",
    PROVENANCE: "75bdbf3cbe34e5ade08c1a8a407a4f459a0b35adf6a9517fe64b2452fa1ac186",
}
SOURCE_SIZE = 14758
SOURCE_SHA256 = "81a578ee935776fdb798962859800dd835f3c063e3c94c701d058c2319a56a35"
FUNCTIONS = (
    ("open_cfw_pb_service_onboarding_buffer_write", 146, 263336, 0,
     "buffer_write"),
    ("open_cfw_pb_service_onboarding_zero", 88, 263484, 0, "zero"),
    ("open_cfw_pb_onboarding_encode_and_send", 276, 263572, 6,
     "common_encode"),
    ("APP_PbRxOnboardingFrameDataProcess", 170, 263848, 9, "dispatch"),
    ("PB_RxOnboardingConfig", 20, 264020, 1, "config_rx"),
    ("APP_PbTxEncodeOnboardingConfig", 20, 264040, 1, "config_tx"),
    ("APP_PbNotifyEncodeOnboardingConfig", 44, 264060, 1,
     "config_notify"),
    ("PB_RxOnboardingHeartbeat", 10, 264104, 0, "heartbeat_rx"),
    ("APP_PbTxEncodeOnboardingHeartbeat", 20, 264116, 1,
     "heartbeat_tx"),
    ("PB_RxOnboardingEvent", 20, 264136, 1, "event_rx"),
    ("APP_PbTxEncodeOnboardingEvent", 20, 264156, 1, "event_tx"),
    ("APP_PbNotifyEncodeOnboardingEvent", 44, 264176, 1,
     "event_notify"),
)
PATCH_SUFFIXES = (
    "dispatch", "rx_config", "tx_config", "notify_config",
    "rx_heartbeat", "tx_heartbeat", "rx_event", "tx_event", "notify_event",
)
MANIFEST_PATCH_SUFFIXES = (
    "dispatch", "config_rx", "config_tx", "config_notify",
    "heartbeat_rx", "heartbeat_tx", "event_rx", "event_tx", "event_notify",
)
PHYSICAL = (0x004A78D0, 0x004A8560)
PHYSICAL_SHA256 = "3c62388010aee013633ecdb222617b023ae9a831c82eb1c5860ac8856f6c9cb5"
BODY_SHA256 = "56f0c2d54aa65832669d28bcaa24d022886fd11224595881009f2feb0a0503a6"
GAPS = (
    (0x004A81AE, 0x004A81B4, "650cfa410ddef240f40a742f5824e0d47fa690c1dcc34db8272f003ee0953f6b"),
    (0x004A833C, 0x004A8368, "bb21c0203e55c5a77d4489897dee51fff441ebdd3bdd009cd2272795a1a9805a"),
    (0x004A84D2, 0x004A8560, "46eeb6889fa8296389677d54af85b280fce92786738e756c78ad2638248da4d6"),
)
GAP_SHA256 = "0c9793e2789ea9c94675bec3252590ce396ea6c1e0e544034112e119f4b5dbfa"
ASSERT_RECORDS = (0x00782010, 0x007820B0)
ASSERT_SHA256 = "25d9cccd0716cd3d8f5fb8d62191df1c229652e05397a9c756b97eeffaab231e"
ENTRY_SHA256 = "5f989981d79f422f097af3a628a631f3867fd202ab73f4a486fbae2a8c6f3c4b"
BODY_CALL_SHA256 = "bdbd0ae07013b6c1e35a6cae51637c87b561688d193384cc3fe84083f428b59c"
RAW_WINDOW_SHA256 = "1f07e6317e1d6aa60f4d82f8887ef865603995295c1fff95ac446493551fe85a"
RETAINED_PATH_ADDRESS = 0x006D95CC
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_onboarding\pb_service_onboarding.c"
)
DISPATCH_SYMBOL = (0x00757AE8, "APP_PbRxOnboardingFrameDataProcess")
ASSERT_SYMBOLS = (
    (0x0077A48C, "PB_RxOnboardingConfig", 103),
    (0x007635D0, "APP_PbTxEncodeOnboardingConfig", 117),
    (0x00757B54, "APP_PbNotifyEncodeOnboardingConfig", 152),
    (0x0076F7B8, "PB_RxOnboardingHeartbeat", 188),
    (0x00757B78, "APP_PbTxEncodeOnboardingHeartbeat", 201),
    (0x0077A4BC, "PB_RxOnboardingEvent", 240),
    (0x007635F0, "APP_PbTxEncodeOnboardingEvent", 254),
    (0x00757B9C, "APP_PbNotifyEncodeOnboardingEvent", 294),
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
    if len(rows) != 9 or sum(map(len, bodies)) != 3024:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 192 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("80b56222"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    if cstring(data, DISPATCH_SYMBOL[0]) != DISPATCH_SYMBOL[1]:
        raise AuditError("dispatcher symbol changed")
    assertions = image_slice(data, *ASSERT_RECORDS)
    if sha256(assertions) != ASSERT_SHA256:
        raise AuditError("assertion records changed")
    for index, (symbol, name, line) in enumerate(ASSERT_SYMBOLS):
        if cstring(data, symbol) != name:
            raise AuditError(f"retained symbol changed at 0x{symbol:08x}")
        if struct.unpack_from("<5I", assertions, index * 20) != (
                0, 0, RETAINED_PATH_ADDRESS, symbol, line):
            raise AuditError(f"assertion metadata changed: {name}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != [0x004A84D4, 0x00782018, 0x0078202C, 0x00782040,
                      0x00782054, 0x00782068, 0x0078207C, 0x00782090,
                      0x007820A4]:
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
        (0x004684FC, 0x004A78D0), (0x0047E358, 0x004A8368),
        (0x004A7A6A, 0x004A7B00), (0x004A7A76, 0x004A7BC4),
        (0x004A7A84, 0x004A7EDA), (0x004A7A90, 0x004A7F4C),
        (0x004A7A9E, 0x004A80E2), (0x004A7AAA, 0x004A81B4),
        (0x004A8786, 0x004A7D4E),
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
    if len(calls) != 181 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    expected_stored = [(0x004C9B1D, 0x004A804C),
                       (0x004D0AF9, 0x004A7E4C),
                       (0x00595720, 0x004A8099)]
    if stored != expected_stored or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

    literal_checks = {
        0x004A8350: 0x200F622C, 0x004A8504: 0x200F612C,
        0x004A8508: 0x200F623C, 0x004A8524: 0x20074FFB,
        0x004A8354: 0x00779C94, 0x004A855C: 0x00779C94,
    }
    if any(struct.unpack_from("<I", data, address - BASE)[0] != value
           for address, value in literal_checks.items()):
        raise AuditError("onboarding workspace/global closure changed")

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
                "components/apollo_main/core_overlay/pb_service_onboarding.c"
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
        patch = patch_by_name.get(f"replace_pb_onboarding_{suffix}")
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
            f"pb_onboarding_{suffix}_source_replacement"
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
            f"pb_onboarding_{region_suffix}_source_text"
        )
        if region is None or (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (3523396 + offset, size, 0x00794324 + offset,
              "source_compiled"):
            raise AuditError(f"production manifest source changed: {name}")
    retained = [item for item in main["regions"]
                if item["name"].startswith("pb_onboarding_")
                and item["name"].endswith("_gap")]
    alignment = [item for item in main["regions"]
                 if item["name"].startswith("pb_onboarding_")
                 and item["name"].endswith("_source_alignment")]
    if sum(item["size"] for item in retained) != 192 or any(
            item.get("address_status") != "official_blob"
            for item in retained) or sum(
                item["size"] for item in alignment) != 8:
        raise AuditError("production retained/alignment accounting changed")

    return {
        "surface": {
            "linked_functions": 9, "body_bytes": 3024,
            "owned_gap_pool_bytes": 192, "physical_bytes": 3216,
            "assertion_records": 8, "direct_bl_entry_sites": 9,
            "direct_body_calls": 181, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 3,
        },
        "contracts": {
            "rx_status": {"success": 0, "command_or_handler_failure": 1,
                          "null": 2, "decode_failure": 0x2B},
            "tx_status": {"success": 0, "null": 2, "encode_failure": 0x2B},
            "commands": {1: "configuration_tag_3", 2: "heartbeat_tag_4",
                         3: "event_tag_5"},
            "route": 1, "service": 0x10,
            "decoded_message": "0x200f622c", "message": "0x200f623c",
            "message_bytes": 0x10, "encode_buffer": "0x200f612c",
            "encode_capacity": 0x100, "notification_sequence": "0x20074ffb",
            "heartbeat_states": {"ready": 0, "not_ready": 8},
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": [DISPATCH_SYMBOL[1]] + [name for _, name, _ in ASSERT_SYMBOLS],
            "assertion_lines": [line for _, _, line in ASSERT_SYMBOLS],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 3024,
            "source_inventory_available": True,
            "source_functions": 12,
            "compiled_text_bytes": 878,
            "alignment_bytes": 8,
            "strict_relocations": 22,
            "stock_replaced_bytes": 3024,
            "retained_gap_pool_bytes": 192,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized live G2 service 0x10 peer BLE, display-ready, "
                "onboarding-control, response, or notification workflow evidence "
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
    print("G2 pb_service_onboarding audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
