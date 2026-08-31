#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 GX8002 codec-DFU object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-service-codec-dfu-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-service-codec-dfu-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-service-codec-dfu-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/service_codec_dfu.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINS = {
    FUNCTION_MAP: "2b84310693115302683c9136c2c2ca0e26178c4d3b1d7b9cedd250d10428c1e6",
    CLOSURE: "7354a97269a6fb61a1b62724ab651fee8a59df4162b8d0a5a0dcb51f26b16748",
    PROVENANCE: "739e47f57063644aae9e383d96e5251f0cb45e866a62694b6a75c3499a94ee4c",
}
SOURCE_SHA256 = "66cc9fe843f775518c97e7db525f7a731545777762fa4d1fc0e5524b9d84c700"
FUNCTIONS = (
    "open_cfw_dfu_release_package", "open_cfw_dfu_load_package",
    "open_cfw_dfu_format_version", "open_cfw_dfu_parse_version_bytes",
    "open_cfw_dfu_get_package_version",
    "open_cfw_dfu_validate_firmware_header",
    "open_cfw_dfu_host_is_little_endian", "open_cfw_dfu_bswap32",
    "open_cfw_dfu_host_to_be32", "open_cfw_dfu_wait_token",
    "open_cfw_dfu_read_boot_header", "open_cfw_dfu_download_boot_stage1",
    "open_cfw_dfu_download_boot_stage2", "open_cfw_dfu_flash_image",
    "open_cfw_svc_codec_dfu", "open_cfw_svc_codec_check_and_upgrade",
)
PATCH_FUNCTIONS = (
    "open_cfw_dfu_load_package", "open_cfw_dfu_release_package",
    *FUNCTIONS[2:],
)
SOURCE_OFFSETS = (
    244992, 245036, 245612, 245984, 246044, 246252, 246280, 246284,
    246288, 246316, 246464, 246628, 247004, 247308, 248156, 248296,
)
SOURCE_SIZES = (
    44, 576, 372, 46, 208, 26, 4, 4, 26, 148, 164, 370, 304, 848,
    140, 110,
)
PHYSICAL = (0x00577D7C, 0x0057A46C)
PHYSICAL_SHA256 = "7586756c943d9c607ac92eab4e075d8d0fed0cea38fcf2bb7664122d1f216a35"
BODY_SHA256 = "e0487b9129f918d6e4a0caf95fcc1e75f8ebac23db36fce2aa3f2dfe22ded98b"
GAP_SHA256 = "42cffa793dfdb3987491c96e1809a1d69723d6235df129643c157fc37e4a1ffc"
ENTRY_SHA256 = "e8afc1fbe6e1a10909f767cdb7768ccc2409d921faf1f162b1f587a315b741f3"
BODY_CALL_SHA256 = "e0a20198e4441f9c07837432666ca3cdb7812c8c1a151cd360d712d4ca80272d"
RAW_WINDOW_SHA256 = "2d931ced3c374258744573c6f51c9ed0db227a894a8df72f62724c365f6ab7e3"
RETAINED_PATH_ADDRESS = 0x006FCBB4
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_codec_dfu.c"
PATH_CELLS = (0x005787E4, 0x00579160, 0x00579C78, 0x0057A3D0)
EXACT_SYMBOLS = (
    (0x00788840, "SVC_CodecDfu"),
    (0x00770FE4, "SVC_CodecCheckAndUpgrade"),
)
GAPS = (
    (0x005787D4, 0x00578810, "2f51ea92d4f95cd6135e43ccedddafd060b640dbe7295e05c967c028040e0101"),
    (0x00578A66, 0x00578A6C, "c761a84a1747159c1908888d5e8a7b2890c272d2f99856ccc3ebb7053a4a5843"),
    (0x00578A86, 0x00578AAC, "d8db0fea26048b2bf9fe3edf581d8249c983f9ad1c43f1e44452378b2b0ae46e"),
    (0x00578C4A, 0x00578CA4, "0ccbea6920cd2c39968a6960ac2e604713ad0f328bd39a2a14c06f42a3a8392a"),
    (0x00579124, 0x005791A0, "208eac3f4811577699ee314bce39a43577264e59124def992c6e46fea4989f14"),
    (0x00579638, 0x005796C8, "f9e491deec4fcd5f6331692564c710151580b746728100845652c36326c30c5c"),
    (0x00579C6A, 0x00579CBC, "49fb3c566251173ae24b954eeb18f0c763150fda9e10a5cf300403294bfce6b3"),
    (0x00579F50, 0x00579FB8, "62a1364e8e49c8d09cc6c31d090b93357c23c40e8507bef484de500bce457019"),
    (0x0057A360, 0x0057A46C, "e9bf4f6abb2d507dc78bf673ae7f4cc530d7fb22035da8bac16dac098a493350"),
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
        start, end = int(row["entry"], 0), int(row["end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["size"]) or sha256(raw) != row["sha256"]:
            raise AuditError(f"body changed: {row['name']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 16 or sum(map(len, bodies)) != 9_052:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps: list[bytes] = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 916 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(image_slice(data, PHYSICAL[0] - 16, PHYSICAL[0])) != "b618cfa86b4f627f60741912a13e059ae8308951dddd7766ced5ba247b8d6aa9":
        raise AuditError("previous-object boundary changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 8) != bytes.fromhex("010009b2002909d4"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    if any(cstring(data, address) != name for address, name in EXACT_SYMBOLS):
        raise AuditError("retained codec-DFU symbol changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != list(PATH_CELLS):
        raise AuditError("retained path-pointer closure changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entries: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    bw_hits: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts or target in interiors:
            bw_hits.append((site, target))
    if len(entries) != 34 or pair_digest(entries) != ENTRY_SHA256 or interior:
        raise AuditError("direct BL entry/interior closure changed")
    if bw_hits:
        raise AuditError("B.W entry/interior ingress appeared")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 584 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    raw_windows: list[tuple[int, int]] = []
    aligned_entry_pointers: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        target = (value & ~1) if value & 1 else value
        if target in starts or target in interiors:
            raw_windows.append((BASE + offset, value))
            if offset % 4 == 0 and target in starts:
                aligned_entry_pointers.append((BASE + offset, value))
    if raw_windows != [(0x00644AB7, 0x005797FF)]:
        raise AuditError("raw entry/interior byte-window closure changed")
    if pair_digest(raw_windows) != RAW_WINDOW_SHA256 or aligned_entry_pointers:
        raise AuditError("stored entry-pointer closure changed")

    if cstring(data, 0x00782E84) != "/firmware/codec.bin":
        raise AuditError("codec package path changed")
    literal_contract = {
        0x005787D8: 0x00782E84,
        0x00578804: 0x4B505746,
        0x00578C54: 0x20074934,
        0x00578C58: 0x20074930,
        0x00578C74: 0x2007493C,
        0x00578C78: 0x20074938,
        0x00579658: 0x2007395C,
        0x005799E4: 0x2035EE18,
        0x0057A3CC: 0x00788840,
        0x0057A410: 0x00770FE4,
        0x0057A468: 0x20074940,
    }
    if any(struct.unpack_from("<I", data, site - BASE)[0] != value
           for site, value in literal_contract.items()):
        raise AuditError("codec-DFU package/state literal changed")

    source = SOURCE.read_bytes()
    if len(source) != 23_239 or sha256(source) != SOURCE_SHA256:
        raise AuditError("codec-DFU production source changed")
    source_text = source.decode("utf-8")
    required_source_tokens = (
        "OPEN_CFW_DFU_MAGIC = 0x4b505746u",
        "OPEN_CFW_DFU_FLASH_CHUNK = 0x2000",
        "OPEN_CFW_DFU_FLASH_START_TIMEOUT = 9000000",
        "uint8_t prefix[13]={'s','e','r','i','a','l','d','o','w','n',' ','0',' '}",
        "open_cfw_dfu_download_boot_stage1",
        "open_cfw_dfu_download_boot_stage2",
        "open_cfw_svc_codec_check_and_upgrade",
        "OPEN_CFW_DFU_CODEC_VERSION(version,200u)",
    )
    if any(token not in source_text for token in required_source_tokens):
        raise AuditError("codec-DFU source contract changed")

    overlay = json.loads(OVERLAY.read_text())
    leaves = [item for item in overlay["relocated_leaves"]
              if item.get("source", {}).get("path") ==
              "components/apollo_main/core_overlay/service_codec_dfu.c"]
    if tuple(item["function"] for item in leaves) != FUNCTIONS:
        raise AuditError("codec-DFU source leaf order changed")
    if tuple(item["expected"]["offset"] for item in leaves) != SOURCE_OFFSETS:
        raise AuditError("codec-DFU source placement changed")
    if tuple(item["expected"]["size"] for item in leaves) != SOURCE_SIZES:
        raise AuditError("codec-DFU compiled text sizes changed")
    if sum(len(item["relocations"]) for item in leaves) != 71:
        raise AuditError("codec-DFU relocation closure changed")
    if any(item.get("source", {}).get("sha256") != SOURCE_SHA256
           or item.get("strict_relocation_contract") is not True
           for item in leaves):
        raise AuditError("codec-DFU source/relocation authentication changed")
    patches = [item for item in overlay["patch_sites"]
               if item.get("name", "").startswith("replace_service_codec_dfu_")]
    for index, (patch, row, function) in enumerate(
            zip(patches, rows, PATCH_FUNCTIONS), 1):
        if (
            patch.get("name") != f"replace_service_codec_dfu_{index:02d}"
            or patch.get("runtime_address") != int(row["entry"], 0)
            or patch.get("expected_size") != int(row["size"])
            or patch.get("expected_sha256") != row["sha256"]
            or patch.get("target_function") != function
            or patch.get("branch") != "b_w"
        ):
            raise AuditError(f"codec-DFU guarded redirect {index:02d} changed")
    expected = overlay["expected"]
    build = json.loads(BUILD_REPORT.read_text())
    if (build["overlay"]["size"], build["overlay"]["sha256"],
            build["component"]["size"], build["component"]["sha256"]) != (
            expected["overlay_size"], expected["overlay_sha256"],
            expected["component_size"], expected["component_sha256"]):
        raise AuditError("codec-DFU build/overlay accounting diverged")
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    if (main["provider"]["size"], main["provider"]["sha256"]) != (
            build["component"]["size"], build["component"]["sha256"]):
        raise AuditError("codec-DFU manifest/component accounting diverged")
    regions = main["regions"]
    body_regions = [item for item in regions
                    if item["name"].startswith("service_codec_dfu_")
                    and item["name"].endswith("_source_replacement")]
    gap_regions = [item for item in regions
                   if item["name"].startswith("service_codec_dfu_official_gap_")]
    text_regions = [item for item in regions
                    if item["name"].startswith("service_codec_dfu_")
                    and item["name"].endswith("_source_text")]
    align_regions = [item for item in regions
                     if item["name"].startswith("service_codec_dfu_")
                     and item["name"].endswith("_overlay_alignment")]
    if (len(body_regions), sum(item["size"] for item in body_regions),
            len(gap_regions), sum(item["size"] for item in gap_regions),
            len(text_regions), sum(item["size"] for item in text_regions),
            len(align_regions), sum(item["size"] for item in align_regions)) != (
            16, 9_052, 9, 916, 16, 3_390, 4, 24):
        raise AuditError("codec-DFU manifest ownership changed")
    package = PACKAGE.read_bytes()
    if (len(package), sha256(package)) != (
            manifest["package"]["expected_size"],
            manifest["package"]["expected_sha256"]):
        raise AuditError("codec-DFU package artifact changed")
    flash_plan = json.loads(FLASH_PLAN.read_text())
    if (not flash_plan.get("flash_regions")
            or flash_plan.get("unresolved_flash_regions") != []
            or flash_plan.get("package_sha256") !=
            manifest["package"]["expected_sha256"]):
        raise AuditError("codec-DFU flash-plan closure changed")

    external_entries = [pair for pair in entries
                        if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    return {
        "surface": {
            "retained_path_anchors": 9,
            "restored_pathless_functions": 7,
            "linked_functions": 16,
            "body_bytes": 9_052,
            "owned_gap_pool_bytes": 916,
            "physical_bytes": 9_968,
            "direct_bl_entry_sites": 34,
            "external_direct_bl_entry_sites": len(external_entries),
            "direct_body_calls": 584,
            "b_w_entry_or_interior_targets": 0,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 1,
        },
        "contracts": {
            "package_path": "/firmware/codec.bin",
            "package_magic": "FWPK",
            "package_header_bytes": 16,
            "firmware_record_bytes": 16,
            "firmware_types": {1: "boot", 2: "firmware"},
            "stage1_uart_baud": 230_400,
            "boot_header_bytes": 32,
            "transfer_chunk_bytes": 256,
            "flash_scratch_bytes": 0x2000,
            "boot_size_address": "0x20074934",
            "boot_buffer_pointer_address": "0x20074930",
            "firmware_size_address": "0x2007493c",
            "firmware_buffer_pointer_address": "0x20074938",
            "boot_header_scratch_address": "0x2007395c",
            "flash_scratch_address": "0x2035ee18",
            "package_version_cache_address": "0x20074940",
            "check_no_upgrade_return": 1,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{value:08x}" for value in path_cells],
            "exact_symbols": [name for _, name in EXACT_SYMBOLS],
            "source_inventory": "16-function clean-room production C",
            "historical_source_inventory": "unavailable",
            "license": "MIT",
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "source_inventory_available": True,
            "production_routed": True,
            "ownership_bytes": 9_052,
            "compiled_text_bytes": 3_390,
            "generated_alignment_bytes": 24,
            "strict_relocations": 71,
            "guarded_redirects": 16,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": (
                "hardware validation is blocked by unavailable physical evidence; future qualification requires "
                "an authorized G2 pair and either a component-specific codec/UART DFU fixture or an "
                "authenticated golden codec/UART DFU capture"
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 codec-DFU audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 codec-DFU audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
