#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party ULED manager object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-uled-manager-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-uled-manager-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-uled-manager-provenance.tsv"
PINS = {
    FUNCTION_MAP: "08ba5cd6e8dbe053dc4a062b5deb38b8fe5ff8601ec3089d1310beeff97bbbcb",
    CLOSURE: "56c2dc7a5e7e66cbfd9148bb43887b2c48b8345631c701f555d46e9e05cfd3e0",
    PROVENANCE: "7850e3d041c9555f40be842147ef2d265a594792404a334f1410fd6c2f044c12",
}
PHYSICAL = (0x004C9D44, 0x004CA6F8)
PHYSICAL_SHA256 = "c0630c1686b6a9d6d10802f3620206a4cf73047a53d1aed00e4b079bb410c760"
BODY_SHA256 = "502a7480281cb8beefe16a10a1a066fe7236712086eb01341c38c97161ee250e"
GAPS = [(0x004CA2AA, 0x004CA2AC), (0x004CA662, 0x004CA664),
        (0x004CA664, 0x004CA6F8)]
NONCODE_SHA256 = "e6519cf253e67cd737e6ccfa9f7533ec14380b6f1fc6ce5e3967acb1d8e6c813"
ENTRY_COUNT = 18
ENTRY_SHA256 = "dac994ae5c6265c9aedb0251a8e885cc3ed73c082b00514d072f7e6bb058152a"
EXTERIOR_COUNT = 17
BODY_CALL_COUNT = 97
BODY_CALL_SHA256 = "36ae75caf1b59ffbe7e8724ce42e3616034c1bdccb1dc68def404744c4af772a"
FALSE_BL_WINDOWS = {
    0x004CA328: bytes.fromhex("f0f100fb"),
    0x004CA3A4: bytes.fromhex("f0f0daf8"),
    0x004CA3CC: bytes.fromhex("f2f2daf8"),
    0x004CA3E8: bytes.fromhex("f3f35ff0"),
    0x004CA412: bytes.fromhex("f0f100fb"),
    0x004CA420: bytes.fromhex("f0f100fb"),
    0x004CA44E: bytes.fromhex("f0f0daf8"),
    0x004CA46A: bytes.fromhex("f0f0daf8"),
    0x004CA47A: bytes.fromhex("f2f2daf8"),
    0x004CA498: bytes.fromhex("f0f100fb"),
    0x004CA4C8: bytes.fromhex("f0f0daf8"),
    0x004CA4E4: bytes.fromhex("f0f0daf8"),
    0x004CA4F4: bytes.fromhex("f2f2daf8"),
    0x004CA51A: bytes.fromhex("f2f2daf8"),
    0x004CA536: bytes.fromhex("f3f35ff0"),
}
STORED_ENTRIES = [(0x00438090, 0x004C9D45)]
STORED_ENTRY_SHA256 = "a5b8917b149c508956bd34875b38b91e6f0824e3eaa56c05703034cb27c0dd41"
RAW_INTERIOR_WINDOWS = [(0x0064CF7B, 0x004CA600)]
RAW_INTERIOR_SHA256 = "11dbf7a72df133b0a4caa07a8dc2c9f484bd56a247f040db309f883ca68e9c1b"
RUNTIME_CALLBACK_SITE = 0x004C9FA8
RUNTIME_CALLBACK_BYTES = bytes.fromhex("0ff20130")
OPS_LIST = (0x0078EE24, 0x0078EE2C)
OPS_LIST_SHA256 = "2dfd9fd3eca94e66fbeecdd42d7dd6a26e54971d00dc7d50f2d68f028dbd63f0"
A6_RECORD = (0x0070AFE4, 0x0070B024)
A6_RECORD_SHA256 = "464b7cab7992df3dfafe8e505f4f9f7b0c1b56f46f8babbf80dce620c223e2d7"
JBD_RECORD = (0x0070B024, 0x0070B064)
JBD_RECORD_SHA256 = "7eecc0a32f95c8d1d712327198d4b473a7f065eeb1c2e8132f98526debef4418"
PATH_ADDRESS = 0x0070B064
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\driver\uled\drv_mspi_uled.c"
WORDS = {
    0x004CA664: 0x20074530,
    0x004CA670: PATH_ADDRESS,
    0x004CA674: 0x0078A8EC,
    0x004CA67C: OPS_LIST[0],
    0x004CA680: OPS_LIST[1],
    0x004CA6AC: 0x203795A0,
    0x004CA6B0: 0x200007B8,
}
STRINGS = {
    PATH_ADDRESS: RETAINED_PATH,
    0x0078A8EC: "driver.uled",
    0x007499AC: "Error - Failed to find uled driver.\r\n",
    0x00776D9C: "uled_driver_identify",
    0x00785CB0: "uled_mspi_init",
    0x0077F068: "uled_clearScreen",
    0x0077F07C: "uled_driver_init",
    0x00776DB4: "uled_safe_get_chip_id",
    0x00776DCC: "uled_driver_power_down",
    0x00776DE4: "uled_driver_power_up",
    0x00776DFC: "uled_mspi_setBrightness",
    0x00776E14: "uled_set_display_offset",
    0x0077F090: "uled_clean_fb_data",
    0x0075F830: "uled_QSPI_PartialReflash_async",
    0x0075F850: "uled_status_check_and_recovery",
    0x00785CC0: "uled_set_mode",
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
    if len(rows) != 14 or sum(map(len, bodies)) != 2332:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    noncode = b"".join(image_slice(data, *gap) for gap in GAPS)
    if len(noncode) != 152 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned non-code changed")

    for address, expected in WORDS.items():
        actual = struct.unpack("<I", image_slice(data, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    if sha256(image_slice(data, *OPS_LIST)) != OPS_LIST_SHA256:
        raise AuditError("operations linker list changed")
    if struct.unpack("<2I", image_slice(data, *OPS_LIST)) != (A6_RECORD[0], JBD_RECORD[0]):
        raise AuditError("operations linker-list members changed")
    if sha256(image_slice(data, *A6_RECORD)) != A6_RECORD_SHA256:
        raise AuditError("A6N-G operations record changed")
    if sha256(image_slice(data, *JBD_RECORD)) != JBD_RECORD_SHA256:
        raise AuditError("JBD4010 operations record changed")
    if image_slice(data, A6_RECORD[1] - 4, A6_RECORD[1]) != struct.pack("<I", 1):
        raise AuditError("A6N-G operations type changed")
    if image_slice(data, JBD_RECORD[1] - 4, JBD_RECORD[1]) != struct.pack("<I", 0):
        raise AuditError("JBD4010 operations type changed")
    if image_slice(data, RUNTIME_CALLBACK_SITE, RUNTIME_CALLBACK_SITE + 4) != RUNTIME_CALLBACK_BYTES:
        raise AuditError("runtime framebuffer callback materialization changed")

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
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if len(exterior) != EXTERIOR_COUNT:
        raise AuditError("exterior BL closure changed")
    if interior or entry_bw or interior_bw:
        raise AuditError("direct strict-interior/B.W closure changed")

    for site, expected in FALSE_BL_WINDOWS.items():
        if image_slice(data, site, site + 4) != expected:
            raise AuditError(f"qualified multiply/VFP window changed at 0x{site:08x}")
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
    if stored_entries != STORED_ENTRIES or pair_digest(stored_entries) != STORED_ENTRY_SHA256:
        raise AuditError("stored termination-entry closure changed")
    if stored_interiors != RAW_INTERIOR_WINDOWS or pair_digest(stored_interiors) != RAW_INTERIOR_SHA256:
        raise AuditError("raw interior overlap qualification changed")
    if any(site % 2 == 0 for site, _ in stored_interiors):
        raise AuditError("unaligned overlap became executable-looking")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any(
        "drv_mspi_uled" in source.get("path", "").lower()
        for source in overlay["sources"]
    )
    if routed:
        raise AuditError("unimplemented ULED manager unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 14,
            "body_bytes": 2332,
            "owned_noncode_bytes": 152,
            "physical_bytes": 2484,
            "direct_bl_entry_sites": 18,
            "exterior_bl_entry_sites": 17,
            "direct_body_calls": 97,
            "stored_entry_pointers": 1,
            "runtime_entry_materializations": 1,
            "strict_interior_ingress": 0,
            "qualified_raw_instruction_windows": 15,
            "qualified_raw_overlap_windows": 1,
        },
        "dispatch": {
            "active_operations_pointer": "0x20074530",
            "operations_records": 2,
            "record_bytes": 64,
            "callback_slots": 15,
            "type_offset": "0x3c",
            "a6ng_type": 1,
            "jbd4010_type": 0,
            "configuration_key": 1,
            "a6ng_selector_byte": "0x06",
            "clear_callback": "0x004ca2ad",
        },
        "display": {
            "framebuffer_pointer": "0x200007b8",
            "width": 640,
            "height": 480,
            "bits_per_pixel": 4,
            "scanline_bytes": 320,
            "clamped_x_end": 639,
            "clamped_y_end": 479,
            "boundary_nibbles_preserved": True,
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
    print("G2 ULED manager audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
