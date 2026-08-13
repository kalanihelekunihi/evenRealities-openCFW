#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party common ULED MSPI object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-uled-mspi-common-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-uled-mspi-common-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-uled-mspi-common-provenance.tsv"
PINS = {
    FUNCTION_MAP: "dffe01b891ba32481ee8d33355902b027f87f35c7208ce2e34b274f821337dbf",
    CLOSURE: "1753186a2e629514f256193c3a15bcc4961514e80524ad82104c3506b51efa94",
    PROVENANCE: "4024f08b7079f883f66421bcd36ac03041b125dd8b98a1abaf767b26767b4440",
}
PHYSICAL = (0x0059C820, 0x0059D244)
PHYSICAL_SHA256 = "0429d9a36a81cb2442d958e6c6663e94115aeea1b0f83c95ec01e3d15e2ec836"
BODY_SHA256 = "752affeb25a07c832350240ee0ebcdf783cd329b52c6139a9cceb8b6d10fdc71"
NONCODE = (0x0059D156, 0x0059D244)
NONCODE_SHA256 = "eb8d630ca20548c42d3d8fdf0fe168e8c0daecfc331e33334460de56d247ff14"
ENTRY_COUNT = 30
ENTRY_SHA256 = "d075c1dc015a7dc9201919c65b06d4ef03ac45cd8f1acb1d7427fa0fd7332afd"
EXTERIOR_ENTRY = [
    (0x005926A8, 0x0059CF1A),
    (0x00592716, 0x0059CCDC),
    (0x00592754, 0x0059CD86),
    (0x00592786, 0x0059CC40),
    (0x005927BE, 0x0059CC40),
    (0x00592E2A, 0x0059CE1E),
    (0x005BBD98, 0x0059CF1A),
    (0x005BBE36, 0x0059CCDC),
    (0x005BBE78, 0x0059CC40),
    (0x005BCDD4, 0x0059CE1E),
    (0x005BD03C, 0x0059CCDC),
]
EXTERIOR_ENTRY_SHA256 = "1185d91a04b0e41c452685b15ffb9c6ba95c2121ecc9310ba83728577a968c3e"
BODY_CALL_COUNT = 151
BODY_CALL_SHA256 = "efdda74cd55ff8f102237617a11b90be19b36f8affa13d97de7523fcd06c66d5"
STORED_ENTRY = [(0x0059D200, 0x0059C867)]
STORED_ENTRY_SHA256 = "7f3e83e3bacf5ccccc53888043a0b6bcd5a5596c8ad0943a8f667a920012295b"
RAW_INTERIOR_WINDOWS = [(0x005119B7, 0x0059D0F8), (0x0059D5C7, 0x0059CCF8)]
RAW_INTERIOR_SHA256 = "d89fdb2d18eeaa65e83c4899dcf45613d1eb0a74d495ec73701186eaf1c4032c"
PATH_ADDRESS = 0x006F9FD4
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\driver\uled\drv_mspi_uled_common.c"
WORDS = {
    0x0059D158: 0xE000E100,
    0x0059D15C: 0xE000E400,
    0x0059D160: 0xE000ED18,
    0x0059D164: 0x20074534,
    0x0059D170: PATH_ADDRESS,
    0x0059D174: 0x0077F0A4,
    0x0059D1CC: 0x20074538,
    0x0059D1D0: 1_000_000,
    0x0059D1DC: 0x2007453C,
    0x0059D1FC: 0x200007EC,
    0x0059D200: 0x0059C867,
    0x0059D220: 0x20073FFC,
}
STRINGS = {
    PATH_ADDRESS: RETAINED_PATH,
    0x0077F0A4: "driver.uled_common",
    0x00753D08: "am_devices_mspi_device_reconfigure",
    0x0075F870: "am_devices_mspi_set_serail_mode",
    0x0075F8B0: "am_devices_mspi_set_quad_mode",
    0x00776E2C: "uled_rw_param_validate",
    0x00776E44: "am_devices_mspi_read",
    0x00776E5C: "am_devices_mspi_write",
    0x0076B308: "am_devices_mspi_qspi_write",
    0x00753DBC: "am_devices_mspi_qspi_write_async",
    0x00776E74: "am_devices_mspi_init",
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
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
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
    if len(rows) != 13 or sum(map(len, bodies)) != 2358:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    noncode = image_slice(data, *NONCODE)
    if len(noncode) != 238 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned non-code changed")
    for address, expected in WORDS.items():
        actual = struct.unpack("<I", image_slice(data, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")

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
    if interior or entry_bw or interior_bw:
        raise AuditError("direct strict-interior/B.W closure changed")
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if exterior != EXTERIOR_ENTRY or pair_digest(exterior) != EXTERIOR_ENTRY_SHA256:
        raise AuditError("exterior BL closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != BODY_CALL_COUNT or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded_entries = starts | {value | 1 for value in starts}
    encoded_interiors = interiors | {value | 1 for value in interiors}
    stored_entries = []
    stored_interiors = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded_entries:
            stored_entries.append((BASE + offset, value))
        if value in encoded_interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != STORED_ENTRY or pair_digest(stored_entries) != STORED_ENTRY_SHA256:
        raise AuditError("stored callback closure changed")
    if stored_interiors != RAW_INTERIOR_WINDOWS:
        raise AuditError("raw interior overlap closure changed")
    if pair_digest(stored_interiors) != RAW_INTERIOR_SHA256:
        raise AuditError("raw interior overlap digest changed")
    if any(site % 2 == 0 for site, _ in stored_interiors):
        raise AuditError("raw interior window became aligned")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("uled_mspi_common" in source.get("path", "") for source in overlay["sources"])
    if routed:
        raise AuditError("unimplemented driver unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 13,
            "body_bytes": 2358,
            "owned_noncode_bytes": 238,
            "physical_bytes": 2596,
            "direct_bl_entry_sites": 30,
            "exterior_bl_entry_sites": 11,
            "direct_body_calls": 151,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 2,
        },
        "abi": {
            "request_bytes": 28,
            "request_offsets": {
                "device_or_direction": 0,
                "transfer_count": 4,
                "command": 8,
                "instruction": 12,
                "instruction_length": 16,
                "data": 20,
                "handle": 24,
            },
            "hal_transfer_bytes": 24,
            "semaphore": "0x20074534",
            "completion_status": "0x200007ec",
            "serial_template_pointer": "0x20074538",
            "quad_template_pointer": "0x2007453c",
        },
        "behavior": {
            "blocking_timeout_us": 1_000_000,
            "async_timeout_ms": 3000,
            "interrupt_mask": "0x00001a80",
            "mspi_module": 0,
            "mspi_irq": 20,
            "mspi_irq_priority": 4,
            "serial_control_request": "0x18",
            "quad_control_request": "0x18",
            "errors_return_minus_one": True,
        },
        "production": {
            "candidate": None,
            "production_routed": routed,
            "ownership_bytes": 0,
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 common ULED MSPI audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
