#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_health object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-health-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-health-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-health-provenance.tsv"
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_health.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
OVERLAY_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "ad537fecc545895e0aea563c0f99ff41a87b6b0462b60ef4c7ec1649f9a4a221",
    CLOSURE: "1558817e12d8b5b4baa3e2c583db99eaecc5ffcbffaba21af174aeed037766a0",
    PROVENANCE: "955bab8b24158f8b614c8abdcdde41780b1b03738ce2bc23053027256f63f0e3",
}
PHYSICAL = (0x0055A558, 0x0055B2A4)
PHYSICAL_SHA256 = "9020db98fd11e16ce082853f8556a94795330c4f1f178ab6765685c1438ff1ab"
BODY_SHA256 = "13f8aad04ac998d93e5ce8c836cdbaa7633fbe0ab128a9a6395e2fe7665bb6dc"
GAPS = (
    (0x0055AB90, 0x0055ABE0, "a2c14466f889dc5a1a4437ddd50e8dceda2cba85e786d63478846f302aa69371"),
    (0x0055AD52, 0x0055AD78, "38ccf4bde78cb5f4dac46b430243dfcf587dcf266f12bb730ac8e599a8905205"),
    (0x0055AF00, 0x0055AF14, "1b51bdd31d48b5aaaa2f18fa68b4ab05dfd981d95c3a06de5c519710f1212bc1"),
    (0x0055B058, 0x0055B06C, "fb6b962b9a36d9f044fe49a81177128b3deb745376382f527a43d9a7d9e40bd2"),
    (0x0055B20A, 0x0055B2A4, "f647e3f310c4f14441d57ef6fbb81327b904a0d7c31067bdb400fb6d50036ff5"),
)
GAP_SHA256 = "c2d3d3d79212fe12b139f420b07a3ad907f1ae391290b68a9a1ee0177d289d87"
ASSERT_RECORDS = (0x00781E80, 0x00781F20)
ASSERT_SHA256 = "d60ee030f371c3c3032c4833556e1c7b94ed29195b021900664d795e0cc00d88"
ENTRY_SHA256 = "797890f14acfc2883c146beb1177aafba703e12f47a1817d25bd302fd0953e4e"
BODY_CALL_SHA256 = "1103059660848fa4b2c83c7b8f73ec9e786f5f02b464f4d830398e010e9b2346"
RAW_WINDOW_SHA256 = "b8a3f10b322ed0b9e0394b16f55df14f16aedbe57bf411523a6a6d90359b641f"
RETAINED_PATH_ADDRESS = 0x006DE134
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_health\pb_service_health.c"
)
SYMBOLS = (
    (0x0077A324, "PB_RxHealthSingleData", 109),
    (0x00763490, "APP_PbTxEncodeHealthSingleData", 132),
    (0x00781E6C, "PB_RxHealthMultData", 213),
    (0x007634D0, "APP_PbTxEncodeHealthMultData", 237),
    (0x0076F6D8, "PB_RxHealthSingleHighlight", 313),
    (0x00757A34, "APP_PbTxEncodeHealthSingleHighlight", 336),
    (0x0076F6F4, "PB_RxHealthMultHighlight", 374),
    (0x00757A7C, "APP_PbTxEncodeHealthMultHighlight", 398),
)
PRODUCTION_PIN = (12366, "2a5faf89b2fc881b8ae2a19a28f1a2ba780fb7776939c5a560879f1c8791b6d6")
PRODUCTION_LEAVES = (
    ("open_cfw_pb_service_health_buffer_write", "OPEN_CFW_PB_HEALTH_BUFFER_WRITE_ONLY", 154, "71d648ce7fbfe3eb8bcfe0a8ec96ea07f901bedff55b5f8cda47426181d8da76", 243424),
    ("PB_RxHealthSingleData", "OPEN_CFW_PB_HEALTH_RX_SINGLE_ONLY", 24, "fcf1eadf5f4cae6df209d800556053f4afa7938e9d648f1fbf1ab6ce55fd367d", 243580),
    ("APP_PbTxEncodeHealthSingleData", "OPEN_CFW_PB_HEALTH_TX_SINGLE_ONLY", 204, "24699770a105c5391f0fabd4e123b77adf72f7141be3071cae80b7f8c12b6998", 243604),
    ("PB_RxHealthMultData", "OPEN_CFW_PB_HEALTH_RX_MULTIPLE_ONLY", 24, "a859f96aa5044a913132468af5bcdec05b1481a9451b6ab18f170a64627f4df4", 243808),
    ("APP_PbTxEncodeHealthMultData", "OPEN_CFW_PB_HEALTH_TX_MULTIPLE_ONLY", 138, "065695a56049fe570ee0aaeeeffe9dff575e25f7cb1ca3a99f6f5a264a881dfc", 243832),
    ("PB_RxHealthSingleHighlight", "OPEN_CFW_PB_HEALTH_RX_SINGLE_HIGHLIGHT_ONLY", 24, "a99320f11b41dbdaec7856ac72713c7164dc8d655d56ae6aec251011a4bb7577", 243972),
    ("APP_PbTxEncodeHealthSingleHighlight", "OPEN_CFW_PB_HEALTH_TX_SINGLE_HIGHLIGHT_ONLY", 138, "5ef15f8136af16cb5d85d1f10c8b73f4e4c58c9707f9fae3bddbdf8aaada0eb1", 243996),
    ("PB_RxHealthMultHighlight", "OPEN_CFW_PB_HEALTH_RX_MULTIPLE_HIGHLIGHTS_ONLY", 24, "d236fdddab28b4e00659c89de08e5f78aa65271e64d642bcc4257f8cf726fdb2", 244136),
    ("APP_PbTxEncodeHealthMultHighlight", "OPEN_CFW_PB_HEALTH_TX_MULTIPLE_HIGHLIGHTS_ONLY", 210, "3b2e84fbf1957833fe68495e1970fb9f8bf95b99f0c3bffaaf63a8adfc1946d7", 244160),
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
    offset = address - BASE
    first, second = struct.unpack_from("<HH", data, offset)
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
    if len(rows) != 8 or sum(map(len, bodies)) != 3092:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 312 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("a9b1b1fa"):
        raise AuditError("next-function boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    assertions = image_slice(data, *ASSERT_RECORDS)
    if sha256(assertions) != ASSERT_SHA256:
        raise AuditError("assertion records changed")
    for index, (symbol, name, line) in enumerate(SYMBOLS):
        if cstring(data, symbol) != name:
            raise AuditError(f"retained symbol changed at 0x{symbol:08x}")
        record = struct.unpack_from("<5I", assertions, index * 20)
        if record != (0, 0, RETAINED_PATH_ADDRESS, symbol, line):
            raise AuditError(f"assertion metadata changed: {name}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != [0x0055ABB8, 0x0055B234, 0x00781E88, 0x00781E9C,
                      0x00781EB0, 0x00781EC4, 0x00781ED8, 0x00781EEC,
                      0x00781F00, 0x00781F14]:
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
        (0x0055A4F0, 0x0055A558), (0x0055A4FC, 0x0055A702),
        (0x0055A50A, 0x0055A8A2), (0x0055A516, 0x0055AA14),
        (0x0055A524, 0x0055ABE0), (0x0055A530, 0x0055AD78),
        (0x0055A53E, 0x0055AF14), (0x0055A54A, 0x0055B06C),
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
    if len(calls) != 180 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")
    helper_calls = [(0x0055A656, 0x005598CC), (0x0055A960, 0x00559AD2),
                    (0x0055ACA2, 0x00559DFC), (0x0055AFBC, 0x00559FB8)]
    if not all(call in calls for call in helper_calls):
        raise AuditError("health-data helper topology changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if stored != [(0x00643337, 0x0055B1FF)] or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

    workspace = tuple(struct.unpack_from("<I", data, address - BASE)[0]
                      for address in (0x0055AD70, 0x0055AD74,
                                      0x0055B260, 0x0055B264))
    if workspace != (0x2037C6A0, 0x200F5DC4, 0x2037C6A0, 0x200F5DC4):
        raise AuditError("shared health workspace changed")
    if (struct.unpack_from("<I", data, 0x0055ABB0 - BASE)[0] != 0x00777A14
            or struct.unpack_from("<I", data, 0x0055B224 - BASE)[0] != 0x00777A14):
        raise AuditError("health nanopb field descriptor changed")

    production = PRODUCTION_SOURCE.read_bytes()
    if (len(production), sha256(production)) != PRODUCTION_PIN:
        raise AuditError("production health service changed")
    overlay = json.loads(OVERLAY.read_text())
    leaf_names = {item[0] for item in PRODUCTION_LEAVES}
    selected = {item.get("function"): item for item in overlay.get("relocated_leaves", [])
                if item.get("function") in leaf_names}
    if set(selected) != leaf_names or not leaf_names.issubset(set(overlay.get("functions", []))):
        raise AuditError("production health service leaf inventory changed")
    relocation_count = 0
    for name, selector, size, digest, offset in PRODUCTION_LEAVES:
        leaf = selected[name]
        source, tool, pin = leaf.get("source", {}), leaf.get("toolchain", {}), leaf.get("expected", {})
        if source.get("path") != "components/apollo_main/core_overlay/pb_service_health.c" or (source.get("size"), source.get("sha256")) != PRODUCTION_PIN:
            raise AuditError(f"production source contract changed: {name}")
        if f"-D{selector}=1" not in tool.get("flags", []) or leaf.get("profiles") != ["apple-clang"] or not leaf.get("strict_relocation_contract"):
            raise AuditError(f"production toolchain contract changed: {name}")
        if (pin.get("size"), pin.get("sha256"), pin.get("alignment"), pin.get("offset")) != (size, digest, 4, offset):
            raise AuditError(f"production leaf pin changed: {name}")
        relocation_count += len(leaf.get("relocations", []))
    if relocation_count != 20:
        raise AuditError("production health service relocation closure changed")
    stock_by_start = {int(row["stock_start"], 0): row for row in rows}
    sites = {item.get("runtime_address"): item for item in overlay.get("patch_sites", [])
             if item.get("runtime_address") in stock_by_start}
    if set(sites) != set(stock_by_start):
        raise AuditError("production health service entry routing changed")
    for address, row in stock_by_start.items():
        site = sites[address]
        if site.get("expected_size") != int(row["stock_bytes"]) or site.get("expected_sha256") != row["stock_sha256"] or site.get("target_function") != row["function"] or site.get("branch") != "b_w" or site.get("profiles") != ["apple-clang"]:
            raise AuditError(f"production stock route changed: {row['function']}")
    build = json.loads(OVERLAY_REPORT.read_text())
    if (build["overlay"]["size"], build["overlay"]["sha256"], build["component"]["size"], build["component"]["sha256"]) != (332148, "588a29c8d680068b6f27dd2cff831dcfd5aa71a91e4f9f97537d9bcb4a0d145d", 3855544, "df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc"):
        raise AuditError("production health service build pins changed")
    built = {item.get("extraction", {}).get("function"): item
             for item in build.get("relocated_leaves", [])
             if item.get("extraction", {}).get("function") in leaf_names}
    if set(built) != leaf_names or sum(item[2] for item in PRODUCTION_LEAVES) != 940 or sum(item["placement"].get("padding_before", 0) for item in built.values()) != 8:
        raise AuditError("production compiled health service closure changed")
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    regions = main["regions"]
    generated = [item for item in regions if item.get("address_status") == "generated_source_entry_replacement" and item.get("target_address") in stock_by_start]
    appended = [item for item in regions if item.get("address_status") == "source_compiled" and 8190468 <= item.get("target_address", 0) < 8191414]
    if len(generated) != 8 or sum(item["size"] for item in generated) != 3092 or len(appended) != 9 or sum(item["size"] for item in appended) != 940:
        raise AuditError("production health service manifest closure changed")
    if (main["provider"]["size"], main["provider"]["sha256"], manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]) != (3855544, "df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc", 4634038, "3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731"):
        raise AuditError("production health service package pins changed")

    return {
        "surface": {
            "linked_functions": 8, "body_bytes": 3092,
            "owned_gap_pool_bytes": 312, "physical_bytes": 3404,
            "assertion_records": 8, "direct_bl_entry_sites": 8,
            "direct_body_calls": 180, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 1,
            "manually_restored_bodies": 1,
        },
        "contracts": {
            "rx_status": {"success": 0, "helper_failure": 1, "null": 2},
            "rx_helpers": [f"0x{target:08x}" for _, target in helper_calls],
            "tx_status": {"success": 0, "encode_failure": 0x2B, "null": 2},
            "envelopes": {1: "single_data_tag_3", 2: "multiple_data_tag_4",
                          3: "single_highlight_tag_5", 4: "multiple_highlight_tag_6"},
            "route": 1, "service": 0x0E,
            "message": "0x200f5dc4", "message_bytes": 0x31C,
            "encode_buffer": "0x2037c6a0", "encode_capacity": 0x100,
            "multi_highlight_count_bits": 16,
            "multi_highlight_wrapper_has_explicit_count_bound": True,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": [name for _, name, _ in SYMBOLS],
            "assertion_lines": [line for _, _, line in SYMBOLS],
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/pb_service_health.c",
            "production_routed": True, "source_inventory_available": True,
            "source_functions": 9, "compiled_text_bytes": 940,
            "alignment_bytes": 8, "stock_replaced_bytes": 3092,
            "strict_relocations": 20, "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized physical G2/EM9305 health-service evidence "
                "is available in this workspace."
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
    print("G2 pb_service_health audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
