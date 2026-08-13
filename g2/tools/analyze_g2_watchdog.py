#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 first-party watchdog driver."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-watchdog-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-watchdog-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-watchdog-provenance.tsv"
PINS = {
    FUNCTION_MAP: "a9108d6865b4d6876721a6a3b698d059e08ec084a43780734aa827f0855b13a5",
    CLOSURE: "1b262f42bb068048d1f5267b8d7e932697ec3cdf244a019cae9fa3f501e649fa",
    PROVENANCE: "9aeb9f4c76df2c02223f04f1a8edac48006bac49575d33fd5a909f7c25e17ef9",
}
PHYSICAL = (0x0052F2E0, 0x0052F38C)
PHYSICAL_SHA256 = "4b8cced37db8e7615e81d8c5e27b5d1b5e76edde307c4e6f4834382020acd29c"
BODY_SHA256 = "fe30dc1324c0de0255f865ef659ef945608527661b00fc520cb1168e7d9b08a2"
POOL = (0x0052F36C, 0x0052F38C)
POOL_SHA256 = "26df699091c504939cf2e158811c5464a7a8020f1ba49986afde8d5f87eb667c"
ENTRY_SHA256 = "3b5c1979e405e185863f86fc4af638e7d5d9f32edce3bbcf59cfa055ed3130e3"
BODY_CALL_SHA256 = "ec3181e804812dea6d90305676c737d416362cad6bcb2732bc590453ff8ce8b3"
PATH_ADDRESS = 0x0071B5EC
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\driver\wdt\watchdog.c"
WORDS = {
    0x0052F36C: 0x00789F30,
    0x0052F370: 0x00789F20,
    0x0052F374: PATH_ADDRESS,
    0x0052F378: 0x0078C92C,
    0x0052F37C: 0x0077D87C,
    0x0052F380: 0x00789F50,
    0x0052F384: 0x00789F40,
    0x0052F388: 0x00774800,
}
STRINGS = {
    PATH_ADDRESS: RETAINED_PATH,
    0x00789F30: "watchdog_init",
    0x00789F20: "watchdog_init",
    0x0078C92C: "watchdog",
    0x0077D87C: "[watchdog]watchdog_init",
    0x00789F50: "watchdog_enable",
    0x00789F40: "watchdog_enable",
    0x00774800: "[watchdog]watchdog_enable",
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
    if len(rows) != 2 or sum(map(len, bodies)) != 140:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *POOL)) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
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
    if len(entry) != 2 or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("BL entry closure changed")
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if len(exterior) != 1 or interior or entry_bw or interior_bw:
        raise AuditError("exterior/strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 13 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_addresses = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_addresses.append((BASE + offset, value))
    if raw_addresses:
        raise AuditError("unexpected stored entry/interior pointer")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("watchdog.c" in source.get("path", "").lower() for source in overlay["sources"])
    if routed:
        raise AuditError("unimplemented watchdog driver unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 2,
            "body_bytes": 140,
            "owned_noncode_bytes": 32,
            "physical_bytes": 172,
            "direct_bl_entry_sites": 2,
            "exterior_bl_entry_sites": 1,
            "direct_body_calls": 13,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        },
        "behavior": {
            "init_calls_enable": True,
            "selector_provider": "0x0050938e",
            "selector_argument": 0,
            "required_selector_value": 1,
            "watchdog_enable_provider": "0x00511882",
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
    print("G2 watchdog driver audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
