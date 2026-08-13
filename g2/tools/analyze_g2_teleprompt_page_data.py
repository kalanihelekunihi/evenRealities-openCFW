#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 teleprompt page-cache object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-teleprompt-page-data-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-teleprompt-page-data-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-teleprompt-page-data-provenance.tsv"
PINS = {
    FUNCTION_MAP: "8d97e3b48296f7a417a28ee4e29f651e93bb7407de949b0146bfd81db05b1615",
    CLOSURE: "ea26e26afab3be186aacf6d7aab94b9d4b4d3a33879543b161e73ab4065384ea",
    PROVENANCE: "a09b30aba0cfb69f0f74cf47a8bce29ad22a4d6f59efdd9e0476c605c90c8721",
}
PHYSICAL = (0x0058A8E0, 0x0058BCE0)
PHYSICAL_SHA256 = "39167e7d97a2f9d2c125882edef4fc235ec5f3063b5f3e156476e8c783f67649"
BODY_SHA256 = "5da153c2173a50fe75a00f5085a162b9ceda69964b9e29aa0daeb521f8177770"
GAP_SHA256 = "29c0ca1038ac82167e6718bcff0ea676fafe1388296d85fe4522e3e44516b3eb"
ENTRY_SHA256 = "e6ab20b22083d26017ae553e4d8ded0a31d1bc20fa5ca8bd67727cdc9403bbd8"
BODY_CALL_SHA256 = "25782111c5e64ea9c41c9440306b8f9f98f5b89769622a00883953a45a4b2ed5"
RAW_WINDOW_SHA256 = "cfccfd732069d4d20b33b882e1a686d4359c5bc05c482bdbaa376488d7ab3ea5"
RETAINED_PATH_ADDRESS = 0x006F0128
RETAINED_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt"
    r"\teleprompt_page_data.c"
)
PATH_CELLS = (0x0058B350, 0x0058BC4C)
EXACT_SYMBOLS = (
    (0x00789770, "page_data_lock"),
    (0x0074EF9C, "teleprompt_preload_timer_ensure_created"),
    (0x00772C54, "request_page_data_locked"),
    (0x00765E70, "teleprompt_request_page_data"),
    (0x0075ADAC, "teleprompt_preload_timer_callback"),
    (0x00772C70, "teleprompt_page_data_init"),
    (0x00772CA8, "teleprompt_page_data_deinit"),
    (0x00772CE0, "teleprompt_page_data_update"),
    (0x00772D18, "teleprompt_page_data_get"),
    (0x00765EF0, "teleprompt_page_data_set_window"),
)
GAPS = (
    (0x0058B056, 0x0058B058, "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
    (0x0058B344, 0x0058B370, "0de2165b97e3b980cebc3635ef2f452746f17403ddf6c89763bd311d13721ad4"),
    (0x0058B528, 0x0058B568, "009ba948d2a5f6e7128d5f3b443566db9ad6c903ae2dfb3b18d5851239e36851"),
    (0x0058B82E, 0x0058B83C, "6a4907c9b9cf8fc86047034a91e02459c685cccdd12d530c673e49fc0791ea30"),
    (0x0058B8EC, 0x0058B8F0, "2d8d8464f6a38861fdcef08baaffb427f5872d3048e3a89e4f61ce7eb72c91f2"),
    (0x0058B952, 0x0058B980, "9ce208230f6acdf4a42912df3c491fd2e6a80942c986fafd9821e916721871a9"),
    (0x0058BC06, 0x0058BCE0, "dd72b27ab29853696fc9a73d6dd2a6246c6ecd3379fb58c9d1466c6204e7ac9f"),
)
RAW_WINDOWS = ((0x00535809, 0x0058A8F8), (0x006A44A3, 0x0058AADB))


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
    if len(rows) != 21 or sum(map(len, bodies)) != 4_728:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps: list[bytes] = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 392 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(image_slice(data, 0x0058A8C0, PHYSICAL[0])) != \
            "ba0e94efd7c84561d3912ab906421ea92851bd2e30a7164d67716edb06ee154b":
        raise AuditError("previous-object pool boundary changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 8) != bytes.fromhex(
            "3eb50400002c1cd1"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    if any(cstring(data, address) != name for address, name in EXACT_SYMBOLS):
        raise AuditError("retained teleprompt symbol changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != list(PATH_CELLS):
        raise AuditError("retained path-pointer closure changed")

    literal_contract = {
        0x0058B344: 0x20074A6C,
        0x0058B358: 0x20074A70,
        0x0058B530: 0x2010A328,
        0x0058BC08: 0x2010A328,
        0x0058BC18: 0x20074A70,
        0x0058BC40: 0x20074A6C,
        0x0058BCB0: 0x2006B11C,
    }
    if any(struct.unpack_from("<I", data, site - BASE)[0] != value
           for site, value in literal_contract.items()):
        raise AuditError("page-cache state literal changed")
    if image_slice(data, 0x0058A974, 0x0058A978) != bytes.fromhex("0ff2e160"):
        raise AuditError("timer callback materialization changed")

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
    if len(entries) != 81 or pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct BL entry closure changed")
    external = [pair for pair in entries
                if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if len(external) != 17 or pair_digest(external) != \
            "7e4c58f7b4464d9cdfd9f7c20750ab15855218f37370102b7897f852f49c4fc3":
        raise AuditError("external direct-entry closure changed")
    if interior or bw_hits:
        raise AuditError("strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 276 or pair_digest(calls) != BODY_CALL_SHA256:
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
    if raw_windows != list(RAW_WINDOWS) or pair_digest(raw_windows) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any(site % 2 == 0 for site, _ in raw_windows):
        raise AuditError("classified raw window became instruction-aligned")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any("teleprompt_page_data" in source.get("path", "").lower()
           for source in overlay["sources"]):
        raise AuditError("unimplemented teleprompt cache entered production overlay")

    return {
        "surface": {
            "retained_path_anchors": 9,
            "restored_non_anchor_functions": 12,
            "linked_functions": 21,
            "body_bytes": 4_728,
            "owned_gap_pool_bytes": 392,
            "physical_bytes": 5_120,
            "direct_bl_entry_sites": 81,
            "external_direct_bl_entry_sites": 17,
            "direct_body_calls": 276,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "b_w_entry_or_interior_targets": 0,
            "raw_instruction_windows": 2,
        },
        "contracts": {
            "state_base_address": "0x2010a328",
            "state_bytes": 0x51A4,
            "slot_count": 20,
            "slot_stride": 0x414,
            "page_copy_bytes": 0x40C,
            "slot_status_offset": 0x40C,
            "slot_request_time_offset": 0x410,
            "status_empty": 0,
            "status_loading": 1,
            "status_loaded": 2,
            "total_pages_offset": 0x5190,
            "window_start_offset": 0x5194,
            "visible_ready_offset": 0x5198,
            "window_change_time_offset": 0x519C,
            "initialized_offset": 0x51A0,
            "window_valid_offset": 0x51A1,
            "mutex_handle_address": "0x20074a6c",
            "preload_timer_handle_address": "0x20074a70",
            "get_copy_address": "0x2006b11c",
            "visible_window_pages": 4,
            "ensure_pages_before": 5,
            "ensure_pages_after": 8,
            "request_debounce_ms": 500,
            "loading_timeout_ms": 5_000,
            "preload_timer_ms": 2_500,
            "callback_entry": "0x0058b059",
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
        print(f"G2 teleprompt page-cache audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 teleprompt page-cache audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
