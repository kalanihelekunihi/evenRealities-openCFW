#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party Hongshi/A6N-G ULED driver."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-uled-a6ng-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-uled-a6ng-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-uled-a6ng-provenance.tsv"
PINS = {
    FUNCTION_MAP: "c2f1c7d5b9e666e25e3746143ed2ebf854b15d15871d9413816ef8388795605c",
    CLOSURE: "870551f6c1cbfce954d2e3d61d308801f1280e393a8378667e1032edd1fc09f7",
    PROVENANCE: "00224a232188e2f9b2011b89e6df013d545ff57181d07117c8824b4fef6113b9",
}
PHYSICAL = (0x005BBD48, 0x005BD3A0)
PHYSICAL_SHA256 = "b4fc94ee5c7b645975b89e50425e5b400e7525e28721894c3f3517113dc52846"
BODY_SHA256 = "067122a8e2f85e5837971a237602bacda5106e9b3c82f79f19d9629da15ab88c"
GAPS = [
    (0x005BC87A, 0x005BC8B4),
    (0x005BCB24, 0x005BCB28),
    (0x005BCB64, 0x005BCB6C),
    (0x005BCBB0, 0x005BCBB4),
    (0x005BCBFE, 0x005BCC10),
    (0x005BCD2A, 0x005BCD44),
    (0x005BCDDE, 0x005BCE00),
    (0x005BCF28, 0x005BCF68),
    (0x005BD2B8, 0x005BD39C),
]
NONCODE_SHA256 = "f8d5c55d7b44585bcf4774d784ed19f9ad7eb17cddc1ad24b0930a226cb08caa"
ENTRY_COUNT = 99
ENTRY_SHA256 = "57ee0a5dfeb09c6d44775b357bfd9d8f961649810fdc4ac396ca0d9258ac5077"
BODY_CALL_COUNT = 366
BODY_CALL_SHA256 = "004ab10fe0a7d4e982370adab0e15655ca6c4cc54b1236b91cc7e72cc1cb768a"
FALSE_BL_WINDOWS = {
    0x005BC6CA: bytes.fromhex("04f0a0f2"),
    0x005BC6E6: bytes.fromhex("f0f59df6"),
    0x005BC70E: bytes.fromhex("f0f580f6"),
    0x005BCC90: bytes.fromhex("f4f44ff4"),
}
OPS_OBJECT = (0x0070AFE0, 0x0070B024)
OPS_SHA256 = "ec5c1f936d6fb6967cd8ec6c2f5756de67e17c4c872bd20b8ae5ce16fa73304a"
OPS_ENTRIES = [
    (0x0070AFE4, 0x005BBD49), (0x0070AFE8, 0x005BC76F),
    (0x0070AFEC, 0x005BBD71), (0x0070AFF0, 0x005BBDA5),
    (0x0070AFF4, 0x005BCB6D), (0x0070AFF8, 0x005BCBB5),
    (0x0070AFFC, 0x005BC6AF), (0x0070B000, 0x005BCB29),
    (0x0070B004, 0x005BCC11), (0x0070B008, 0x005BC4C1),
    (0x0070B00C, 0x005BCD45), (0x0070B010, 0x005BCC19),
    (0x0070B014, 0x005BD015), (0x0070B018, 0x005BD39D),
    (0x0070B01C, 0x005BC8B5),
]
STORED_ENTRY_SHA256 = "808f45a0f1feab19c5674e7ffbbbe20745314c31492d18e5a8805ff47dbe1678"
RAW_INTERIOR_WINDOWS = [(0x00643447, 0x005BCB00), (0x00644B47, 0x005BC400)]
RAW_INTERIOR_SHA256 = "5b7a4c1b213abe2d41218d4ea776df52200efc9f6bc5463189c768e5619d94ef"
TEMPLATES = [0x0076B12C, 0x0076B148, 0x0076B164, 0x0076B180]
TEMPLATE_SHA256 = "e25b08f08ee39a2376c7d8eb46f5e2fe9aa06549d735624fe6a10beecb413549"
CONFIG_STREAM = (0x00728ED8, 0x00728F0A)
CONFIG_SHA256 = "817aab4e4b6763d2f1eccc26599caad6d867a3e42a8e6d4ac1f16fbcb3e96e13"
STATUS_PREAMBLE = (0x0078D484, 0x0078D48C)
STATUS_SHA256 = "e3280ece11de406ed5063c8fb4a05dcee97cbf2ffce4ffc67ff698de7039a067"
PATH_ADDRESS = 0x006ECCA8
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\driver\uled\hongshi_a6ng\drv_mspi_a6ng.c"
WORDS = {
    0x005BC8A8: PATH_ADDRESS,
    0x005BD2F0: PATH_ADDRESS,
    0x005BC87C: 0x20074510,
    0x005BC880: 0x20074518,
    0x005BC884: 0x20074514,
    0x005BC888: 0x20000770,
    0x005BC88C: 0x20000758,
    0x005BC894: 0x2007451C,
    0x005BC898: 0x0076B12C,
    0x005BC89C: 0x0076B148,
}
STRINGS = {
    PATH_ADDRESS: RETAINED_PATH,
    0x00785C80: "driver.a6n-g",
    0x00753B34: "am_devices_mspi_hongshi_read_bank",
    0x00753B58: "am_devices_mspi_hongshi_configure",
    0x007496DC: "am_devices_hongshi_set_display_offset",
    0x00749754: "am_devices_mspi_hongshi_setBrightness",
    0x00753BC4: "am_devices_mspi_hongshi_read_chipId",
    0x0075F7B0: "am_device_mspi_hongshi_read_sn",
    0x0074977C: "am_devices_hongshi_QSPI_PartialReflash",
    0x00733614: "am_devices_hongshi_QSPI_PartialReflash_async",
    0x00753BE8: "am_devices_hongshi_status_recovery",
    0x00733674: "am_devices_hongshi_status_check_and_recovery",
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
    if len(rows) != 22 or sum(map(len, bodies)) != 5276:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    noncode = b"".join(image_slice(data, *gap) for gap in GAPS)
    if len(noncode) != 444 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned non-code changed")

    for address, expected in WORDS.items():
        actual = struct.unpack("<I", image_slice(data, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    if sha256(image_slice(data, *OPS_OBJECT)) != OPS_SHA256:
        raise AuditError("external ULED operations object changed")
    if struct.unpack("<17I", image_slice(data, *OPS_OBJECT)) != (
        0, *(target for _, target in OPS_ENTRIES), 1
    ):
        raise AuditError("external operations-table ABI changed")
    templates = b"".join(image_slice(data, address, address + 28) for address in TEMPLATES)
    if sha256(templates) != TEMPLATE_SHA256:
        raise AuditError("request templates changed")
    if sha256(image_slice(data, *CONFIG_STREAM)) != CONFIG_SHA256:
        raise AuditError("configuration stream changed")
    if sha256(image_slice(data, *STATUS_PREAMBLE)) != STATUS_SHA256:
        raise AuditError("status preamble changed")

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
    if len(entry) != ENTRY_COUNT or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("BL entry closure changed")
    if any(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entry):
        raise AuditError("unexpected exterior BL entry")
    if interior or entry_bw or interior_bw:
        raise AuditError("direct strict-interior/B.W closure changed")

    for site, expected in FALSE_BL_WINDOWS.items():
        if image_slice(data, site, site + 4) != expected:
            raise AuditError(f"qualified VFP window changed at 0x{site:08x}")
    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            if site in FALSE_BL_WINDOWS:
                continue
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != BODY_CALL_COUNT or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded_entries = starts | {value | 1 for value in starts}
    encoded_interiors = interiors | {value | 1 for value in interiors}
    stored_entries: list[tuple[int, int]] = []
    stored_interiors: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded_entries:
            stored_entries.append((BASE + offset, value))
        if value in encoded_interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != OPS_ENTRIES or pair_digest(stored_entries) != STORED_ENTRY_SHA256:
        raise AuditError("stored operations-table closure changed")
    if stored_interiors != RAW_INTERIOR_WINDOWS or pair_digest(stored_interiors) != RAW_INTERIOR_SHA256:
        raise AuditError("raw interior overlap qualification changed")
    if any(site % 2 == 0 for site, _ in stored_interiors):
        raise AuditError("unaligned overlap became executable-looking")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any(
        token in source.get("path", "").lower()
        for source in overlay["sources"]
        for token in ("a6ng", "hongshi")
    )
    if routed:
        raise AuditError("unimplemented Hongshi driver unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 22,
            "body_bytes": 5276,
            "owned_noncode_bytes": 444,
            "physical_bytes": 5720,
            "direct_bl_entry_sites": 99,
            "exterior_bl_entry_sites": 0,
            "direct_body_calls": 366,
            "stored_entry_pointers": 15,
            "strict_interior_ingress": 0,
            "qualified_vfp_windows": 4,
            "qualified_raw_overlap_windows": 2,
        },
        "abi": {
            "request_bytes": 28,
            "request_templates": 4,
            "mspi_handle": "0x20074510",
            "framebuffer": "0x20074514",
            "clear_callback": "0x20074518",
            "command_scratch": "0x2007451c",
            "brightness_state": "0x20074520",
            "offset_mode_flag": "0x2007501a",
            "operations_table": "0x0070afe0",
            "operations_callbacks": 15,
        },
        "display": {
            "width": 640,
            "height": 480,
            "bits_per_pixel": 4,
            "scanline_bytes": 320,
            "offset_saturation": 16,
            "chip_id_register": "0x06",
            "chip_id_value": "0x01",
            "status_be": "0x84",
            "status_62": ["0x77", "0x57"],
            "mirror_d8_mask": "0x20",
            "configuration_bytes": 50,
            "status_preamble_bytes": 8,
            "set_current_is_stub": True,
            "set_mode_is_stub": True,
        },
        "production": {
            "candidate": None,
            "production_routed": routed,
            "ownership_bytes": 0,
            "source_inventory_available": False,
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 Hongshi/A6N-G ULED audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
