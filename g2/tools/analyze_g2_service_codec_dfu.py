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
PINS = {
    FUNCTION_MAP: "2b84310693115302683c9136c2c2ca0e26178c4d3b1d7b9cedd250d10428c1e6",
    CLOSURE: "c8711e1965d4992dadd252161347db53e0606f442133343cafd369dfe23ef686",
    PROVENANCE: "83b4b0873d3f739fb760425c2c8969f4626bdb723b3a042911bbc28c47dd8549",
}
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

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any("service_codec_dfu" in source.get("path", "").lower()
           for source in overlay["sources"]):
        raise AuditError("unimplemented codec DFU entered production overlay")

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
            "source_inventory": "unavailable",
            "license": "unknown",
        },
        "production": {
            "candidate": None,
            "source_inventory_available": False,
            "production_routed": False,
            "ownership_bytes": 0,
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
