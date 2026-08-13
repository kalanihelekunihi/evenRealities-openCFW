#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 notification whitelist service."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-service-whitelist-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-service-whitelist-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-service-whitelist-provenance.tsv"
PINS = {
    FUNCTION_MAP: "adc530e777779dbfbc78c205c7202603766bd8daef3ec6750d2399f4769d1034",
    CLOSURE: "516c30374b639a0c18b61e61c637c4e7c3a346aea3855bffe8e680b33e780468",
    PROVENANCE: "6596b772c26085056a132ac0f1ee6e9ad31518d13f9e1735cd00866d413aa0c6",
}
PHYSICAL = (0x004D5930, 0x004D6BA8)
PHYSICAL_SHA256 = "7b35909883910abf830ae2274783a7a265c4ea1364fe3b88f7dda5956d4f07aa"
BODY_SHA256 = "dcf6b92f4d9d8ff841302754b9630848be3a517233babaec071a9f48194c7795"
GAP_SHA256 = "fd98d25dca58521e89889e939241d4b71e3efd7bf899a24c55d43388323cfed6"
ENTRY_SHA256 = "ff9289b3ac25444b86bcd6e3ccf91466f0b0adf1f66570a83d7cd1735981be81"
BODY_CALL_SHA256 = "120a48173b73041e63a2b243af4a3a6aac26f5a688745cc1269d2b69724c0cd2"
RAW_WINDOW_SHA256 = "7b09d3a6b75b3fd99a272bba1e0edb2b88e1ec5e2d11b75ccd0fd4423fd1971b"
RETAINED_PATH_ADDRESS = 0x006E51F0
RETAINED_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git\platform\service\message_notify"
    r"\service_whitelist.c"
)
PATH_CELLS = (0x004D6324, 0x004D6AF4)
EXACT_SYMBOLS = (
    (0x007719F4, "_parseJsonWhitelistToStruct"),
    (0x0077BD4C, "_printAppWhiteListInfo"),
    (0x0077BD94, "_parseWhiteListFromFS"),
    (0x00765550, "SVC_IsOnWhitelistByIdentifier"),
    (0x00771A9C, "SVC_WhitelistManagerInit"),
)
GAPS = (
    (0x004D5F30, 0x004D5F38, "6b3a06df976e90c765fccc2b30f28add907a7dc5838ac1edc31f9b807f2e302e"),
    (0x004D631C, 0x004D6360, "18a429f5e83cfe432d189b2f954f126823ce62ee144a7c5e0cd2af583c04cb12"),
    (0x004D676E, 0x004D67B8, "a24ef9c55694f8a2983eefaf7f940de1973c59f508732607f4e23e86746f87ee"),
    (0x004D6A1A, 0x004D6A20, "bae14ad19c2781296be1cdf5094edff84cd2da8e7bfffc75d4aad59b0eb23d57"),
    (0x004D6A3E, 0x004D6A5C, "0259d832e335a58a125f5df123e4da61e41c2ec76b42b013685b38ee3ff0d96a"),
    (0x004D6AC0, 0x004D6BA8, "c36cfbec50bc2635b19a9345d52b7e2ed8d60749bb7a97e235886caa3dfb5cdd"),
)
EXTERNAL_ENTRIES = (
    (0x0048E1F8, 0x004D6A5C),
    (0x0048E340, 0x004D6A5C),
    (0x0048E750, 0x004D67B8),
    (0x004BF34A, 0x004D67B8),
    (0x004D776E, 0x004D6A20),
)
RAW_DATA_WINDOW = (0x0064CF9B, 0x004D5D00)


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
    if len(rows) != 7 or sum(map(len, bodies)) != 4_310:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps: list[bytes] = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 418 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(image_slice(data, 0x004D5918, PHYSICAL[0])) != \
            "5ae02ff6e53b8366317a57fa4f157a9de18f62536411334d6743520659ce4c98":
        raise AuditError("previous-object pool boundary changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 8) != bytes.fromhex(
            "38b59eb004000d00"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    if any(cstring(data, address) != name for address, name in EXACT_SYMBOLS):
        raise AuditError("retained whitelist symbol changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != list(PATH_CELLS):
        raise AuditError("retained path-pointer closure changed")

    literal_contract = {
        0x004D6338: 0x20054718,
        0x004D6B00: 0x2007501B,
        0x004D6B3C: 0x200749A4,
        0x004D6B58: 0x20054718,
        0x004D6B78: 0x0078C0C8,
        0x004D6B7C: 0x0078C0D4,
        0x004D6BA4: 0x00771AB8,
    }
    if any(struct.unpack_from("<I", data, site - BASE)[0] != value
           for site, value in literal_contract.items()):
        raise AuditError("whitelist state/string literal changed")
    if cstring(data, 0x0078C0C8) != "com.even.sg" or \
            cstring(data, 0x0078C0D4) != "com.even.g1" or \
            cstring(data, 0x00771AB8) != "user/notify_whitelist.json":
        raise AuditError("whitelist built-in/file contract changed")

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
    if len(entries) != 9 or pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct BL entry closure changed")
    if tuple(pair for pair in entries if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])) \
            != EXTERNAL_ENTRIES:
        raise AuditError("external direct-entry closure changed")
    if interior or bw_hits:
        raise AuditError("strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 264 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    raw_windows: list[tuple[int, int]] = []
    stored_entries: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        target = (value & ~1) if value & 1 else value
        if target in starts or target in interiors:
            raw_windows.append((BASE + offset, value))
            if target in starts:
                stored_entries.append((BASE + offset, value))
    if stored_entries:
        raise AuditError("unexpected stored exact-entry pointer")
    if raw_windows != [RAW_DATA_WINDOW] or pair_digest(raw_windows) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if image_slice(data, 0x0064CF98, 0x0064CFA0) != bytes.fromhex(
            "000000005d4d0000"):
        raise AuditError("classified packed-data overlap changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any("service_whitelist" in source.get("path", "").lower()
           for source in overlay["sources"]):
        raise AuditError("unimplemented whitelist service entered production overlay")

    return {
        "surface": {
            "retained_path_anchors": 5,
            "restored_pathless_functions": 2,
            "linked_functions": 7,
            "body_bytes": 4_310,
            "owned_gap_pool_bytes": 418,
            "physical_bytes": 4_728,
            "direct_bl_entry_sites": 9,
            "external_direct_bl_entry_sites": 5,
            "direct_body_calls": 264,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "b_w_entry_or_interior_targets": 0,
            "raw_instruction_windows": 1,
        },
        "contracts": {
            "state_base_address": "0x20054718",
            "state_bytes": 8_002,
            "flag_bits": {
                "call": 0, "message": 1, "ios_mail": 2,
                "calendar": 3, "application": 4,
            },
            "application_count_offset": 1,
            "application_limit": 100,
            "application_stride": 80,
            "application_id_bytes": 64,
            "application_name_bytes": 16,
            "load_valid_address": "0x2007501b",
            "cached_crc32_address": "0x200749a4",
            "max_whitelist_buffer_len": 8_003,
            "shared_buffer_file_size_cutover": 8_503,
            "whitelist_file": "user/notify_whitelist.json",
            "built_in_identifiers": ["com.even.sg", "com.even.g1"],
            "identifier_max_bytes_exclusive": 64,
            "result_invalid": 0,
            "result_blocked": 1,
            "result_allowed": 2,
            "disabled_policy": "allow",
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
        print(f"G2 notification whitelist audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 notification whitelist audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
