#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 touch-controller DFU object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-service-touch-dfu-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-service-touch-dfu-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-service-touch-dfu-provenance.tsv"
PINS = {
    FUNCTION_MAP: "e78344ad5842545cdf3e8ec99ae51a041c7358052181d134d88b11e003c9a7ea",
    CLOSURE: "98007e3af0e80183c59ff0c98e28f406bdd465166216124a908ee2b2d98ec959",
    PROVENANCE: "eebe4c9a541aa9c22fbc41838f8b2e9e568886031b52dd48f2c98c1d0bc11968",
}
PHYSICAL = (0x0055FCB4, 0x00561810)
PHYSICAL_SHA256 = "b53444478efe8eac988e311ee4a19f6ee07ab024779340847d77ba6845d5887b"
BODY_SHA256 = "541a9a7deee567a6aa7b5a882a7daf4f86e65378bb1d10401cd612e69c1ba4ec"
GAP_SHA256 = "1697430b30b5f4abe684049202b42ac41e749f6679b3f3e28d4058bc2216e228"
ENTRY_SHA256 = "40886bf36c1eeff76de7e2e94d3fd85c9a47bc44efa3f2e08b37001e41020e96"
BODY_CALL_SHA256 = "51f1e146db48fafdbcc2b906a625b3926ec213e5cff7672ccda1c9eebc191fc4"
RAW_WINDOW_SHA256 = "270bf0bfd92c344c42e117a20ac246103e9ef6962d4147b714edbd1779c510bc"
RETAINED_PATH_ADDRESS = 0x006EFAE8
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\input\touchDFU\service_touch_dfu.c"
PATH_CELLS = (0x005608C4, 0x005610E4, 0x0056176C)
EXACT_SYMBOLS = (
    (0x00788F20, "TouchEnterDFU"),
    (0x00788F40, "TouchSetAppMeta"),
    (0x00783668, "TouchSendOnePacket"),
    (0x0078367C, "TouchProgramData"),
    (0x00788F50, "TouchVerifyApp"),
    (0x00788F70, "TouchExitDFU"),
    (0x00783690, "TouchSendAppFile"),
    (0x007718A4, "free_touch_firmware_memory"),
    (0x00759EC4, "get_touch_firmware_package_version"),
    (0x00759EE8, "load_touch_firmware_from_package"),
    (0x007836B8, "isTouchNeedUpgrade"),
    (0x007718F8, "TouchUpdateFirmwareCheck"),
)
GAPS = (
    (0x005608B0, 0x0056092C, "d227557aa4514c158a3e3612a3f86f8286dcbd9a6be33a1c309266487d0f0667"),
    (0x00560EA2, 0x00560EA8, "00a8f3a79a182b1de7dbd09d4fce1eebeca73bc36245f0f892af336a6cf84b40"),
    (0x00560ED4, 0x00560EFC, "bb08e91afd3cd8796c50a4c14e1771627f00ef47f757a000039d0cf5224c0883"),
    (0x00561078, 0x0056110C, "8b277a9804ea6db721e5984ce401011b3da463f421dd699e145fe57bc5ed59ef"),
    (0x00561710, 0x00561810, "357d7a2db1236e0b3a8af5d9c07d318722a245d3b2c2e884cc38a9ee1dff5731"),
)
EXTERNAL_ENTRIES = (
    (0x00512E24, 0x0056110C),
    (0x0057E79E, 0x00561036),
    (0x00581AE6, 0x0056110C),
    (0x00581AEE, 0x0056110C),
    (0x005A574A, 0x00561036),
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
    if len(rows) != 32 or sum(map(len, bodies)) != 6_430:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps: list[bytes] = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 574 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(image_slice(data, PHYSICAL[0] - 8, PHYSICAL[0])) != "5c8645f02d9cf2e4e1b926586a3f324bdda8d8544e8ae82f4152186ee7736807":
        raise AuditError("previous-object boundary changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 8) != bytes.fromhex("b7ee000a80ed000a"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    if any(cstring(data, address) != name for address, name in EXACT_SYMBOLS):
        raise AuditError("retained touch-DFU symbol changed")
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
    if len(entries) != 60 or pair_digest(entries) != ENTRY_SHA256 or interior:
        raise AuditError("direct BL entry/interior closure changed")
    external_entries = tuple(pair for pair in entries
                             if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1]))
    if external_entries != EXTERNAL_ENTRIES or bw_hits:
        raise AuditError("external/B.W ingress closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 394 or pair_digest(calls) != BODY_CALL_SHA256:
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
    if len(raw_windows) != 23 or pair_digest(raw_windows) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if aligned_entry_pointers:
        raise AuditError("stored exact-entry pointer appeared")

    if cstring(data, 0x007836A4) != "/firmware/touch.bin":
        raise AuditError("touch package path changed")
    literal_contract = {
        0x005608B0: 0x0070F2A4,
        0x005608B8: 0x20073E24,
        0x0056108C: 0x2007499C,
        0x00561090: 0x200749A0,
        0x005610AC: 0x007836A4,
        0x005610C8: 0x4B505746,
        0x005610F0: 0x20074998,
        0x00561760: 0x200739BC,
        0x005617B0: 0x2007499C,
        0x005617B4: 0x200749A0,
    }
    if any(struct.unpack_from("<I", data, site - BASE)[0] != value
           for site, value in literal_contract.items()):
        raise AuditError("touch-DFU package/state literal changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any("service_touch_dfu" in source.get("path", "").lower()
           for source in overlay["sources"]):
        raise AuditError("unimplemented touch DFU entered production overlay")

    return {
        "surface": {
            "retained_path_anchors": 12,
            "restored_pathless_functions": 20,
            "linked_functions": 32,
            "body_bytes": 6_430,
            "owned_gap_pool_bytes": 574,
            "physical_bytes": 7_004,
            "direct_bl_entry_sites": 60,
            "external_direct_bl_entry_sites": 5,
            "direct_body_calls": 394,
            "b_w_entry_or_interior_targets": 0,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 23,
        },
        "contracts": {
            "package_path": "/firmware/touch.bin",
            "package_magic": "FWPK",
            "package_header_bytes": 16,
            "firmware_record_bytes": 16,
            "touch_firmware_type": 3,
            "frame_start": 1,
            "frame_terminator": 0x17,
            "frame_payload_max_bytes": 32,
            "frame_checksum": "16-bit additive two's complement",
            "reply_max_bytes": 15,
            "send_retry_limit": 100,
            "packet_bytes": 32,
            "program_block_bytes": 128,
            "commands": {
                0x38: "enter_dfu",
                0x4C: "set_app_metadata",
                0x37: "send_packet",
                0x49: "program_block",
                0x31: "verify_application",
                0x3B: "exit_dfu",
            },
            "file_handle_address": "0x20074998",
            "firmware_buffer_pointer_address": "0x2007499c",
            "firmware_size_address": "0x200749a0",
            "current_version_address": "0x200739bc",
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
        print(f"G2 touch-DFU audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 touch-DFU audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
