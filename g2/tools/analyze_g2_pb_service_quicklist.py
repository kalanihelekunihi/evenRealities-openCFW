#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_quicklist object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-quicklist-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-quicklist-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-quicklist-provenance.tsv"
PINS = {
    FUNCTION_MAP: "018faa96061d3156726c798ad4954f736ca5591c966bd8f101788270d2463b8a",
    CLOSURE: "c70ab0713c93b8e70fb52d596181c350ae7ac2229d270b87befef6e6346481d8",
    PROVENANCE: "b86472137a745e00aa2a2c33364d20527257b3a9725316fce509b939bb5f16d1",
}
PHYSICAL = (0x0055894C, 0x005597F0)
PHYSICAL_SHA256 = "50654068015e5cced557275529f0ebf3cfe2b16e9d34c86e2071607ac9fb5a18"
BODY_SHA256 = "422a8a9bf8b95f2407dff2a37edd28e4086da06184f1aa99ca42e99ec9e831eb"
GAPS = (
    (0x0055918A, 0x005591B0, "ffd8aaea700ba5b91481167dfed69a0578c7818977b902d87b16c3ea55a3caad"),
    (0x0055936A, 0x00559378, "d84c9ac1bd94f269a397a4bca36e0c40d5e83cdf268057482a9cd208c944c9b4"),
    (0x00559432, 0x00559470, "f53eff7bde31a16c9797d1208f9b6c3e245f7716b2d48a2ef547e53771ca005a"),
    (0x005595DE, 0x0055960C, "697b950045fa217f4de06939e180b6542529a30f9d012c5e4064db17f44220be"),
    (0x00559778, 0x005597F0, "ccd9e9acf2f2ebc486a7dec51afe4d45f23530cc75d429cf759f4a6610ac72a9"),
)
GAP_SHA256 = "e9bbff217f66e505c5bf9932b5192b496a7283ee4887e6fb511da63579f9e8ec"
ASSERT_RECORDS = (0x00782344, 0x007823E4)
ASSERT_SHA256 = "782c5a58bb054935084fb8b10622180f60b7c79998c7e8cdf12158c3a1f4ca65"
ENTRY_SHA256 = "2688f2c811ba0737303ee433102341de6cc20291a0bdfc80ba92c6757fe3cbe2"
BODY_CALL_SHA256 = "f87b32d457eb75abfe5d2a89b3dbff883a7bbf3f581436dd65a9819e18a93bb9"
RAW_WINDOW_SHA256 = "4fed5dbd9cfc450632021930eb8aa176b7bae9e2bdfc7a9deb09d7703eb05991"
RETAINED_PATH_ADDRESS = 0x006DB358
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_quicklist\pb_service_quicklist.c"
)
EXACT_SYMBOLS = (
    (0x00757C98, "APP_PbRxQuicklistFrameDataProcess"),
    (0x0076F940, "APP_DecodePbRxQuicklistData"),
)
ASSERT_SYMBOLS = (
    (0x0078231C, "PB_RxQuicklistItem", 151),
    (0x0076F994, "APP_PbTxEncodeQuicklistItem", 165),
    (0x0077A5AC, "PB_RxQuicklistMultItems", 240),
    (0x00757D28, "APP_PbTxEncodeQuicklistMultItems", 254),
    (0x0074C594, "APP_PbNotifyEncodeQuicklistMultItems", 290),
    (0x00782330, "PB_RxQuicklistEvent", 331),
    (0x00763690, "APP_PbTxEncodeQuicklistEvent", 344),
    (0x00757D4C, "APP_PbNotifyEncodeQuicklistEvent", 380),
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
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 10 or sum(map(len, bodies)) != 3468:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 280 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("c0b20228"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    for address, name in EXACT_SYMBOLS:
        if cstring(data, address) != name:
            raise AuditError(f"retained symbol changed: {name}")
    assertions = image_slice(data, *ASSERT_RECORDS)
    if sha256(assertions) != ASSERT_SHA256:
        raise AuditError("assertion records changed")
    for index, (symbol, name, line) in enumerate(ASSERT_SYMBOLS):
        if cstring(data, symbol) != name:
            raise AuditError(f"retained assertion symbol changed: {name}")
        if struct.unpack_from("<5I", assertions, index * 20) != (
                0, 0, RETAINED_PATH_ADDRESS, symbol, line):
            raise AuditError(f"assertion metadata changed: {name}/{line}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != [0x0055936C, 0x0055946C, 0x005597C8,
                      0x0078234C, 0x00782360, 0x00782374, 0x00782388,
                      0x0078239C, 0x007823B0, 0x007823C4, 0x007823D8]:
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
        (0x004F609E, 0x0055960C), (0x004F6502, 0x005591B0),
        (0x004FFB4E, 0x0055894C), (0x004FFB56, 0x00558B3C),
        (0x00558AEA, 0x00558CB0), (0x00558AF6, 0x00558D9E),
        (0x00558B06, 0x00558F34), (0x00558B12, 0x00558FFE),
        (0x00558B22, 0x00559378), (0x00558B2E, 0x00559470),
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
    if len(calls) != 199 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if stored != [(0x0047A8CD, 0x005594F8)] or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

    literal_checks = {
        0x005591A4: 0x200F624C, 0x005591A8: 0x0077B02C,
        0x005595FC: 0x2037A5A0, 0x00559600: 0x200F7484,
        0x00559784: 0x20074FFD, 0x005597A8: 0x0077B02C,
        0x005597E0: 0x2037A5A0, 0x005597E4: 0x200F7484,
    }
    if any(struct.unpack_from("<I", data, address - BASE)[0] != value
           for address, value in literal_checks.items()):
        raise AuditError("quicklist workspace/descriptor closure changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("pb_service_quicklist" in source.get("path", "").lower()
                 for source in overlay["sources"])
    if routed:
        raise AuditError("unimplemented quicklist service entered production overlay")

    return {
        "surface": {
            "linked_functions": 10, "body_bytes": 3468,
            "owned_gap_pool_bytes": 280, "physical_bytes": 3748,
            "assertion_records": 8, "direct_bl_entry_sites": 10,
            "direct_body_calls": 199, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 1,
        },
        "contracts": {
            "rx_status": {"null": 2, "decode_failure": 0x2B,
                          "success": "handler_or_transmit_result"},
            "tx_status": {"success": 0, "null": 2,
                          "encode_failure": 0x2B, "notify_failure": -1},
            "commands": {1: "item_tag_3", 2: "multi_items_tag_4",
                         3: "event_tag_5"},
            "event_values": [1, 2], "item_stride": 0xE8,
            "route": 1, "service": 0x0C,
            "decoded_message": "0x200f624c", "decoded_message_bytes": 0x1238,
            "transmit_message": "0x200f7484", "transmit_message_bytes": 0x1238,
            "encode_buffer": "0x2037a5a0", "encode_capacity": 0x400,
            "notification_sequence": "0x20074ffd",
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{value:08x}" for value in path_cells],
            "exact_symbols": [name for _, name in EXACT_SYMBOLS]
                             + [name for _, name, _ in ASSERT_SYMBOLS],
            "assertion_lines": [line for _, _, line in ASSERT_SYMBOLS],
        },
        "production": {
            "candidate": None, "source_inventory_available": False,
            "production_routed": False, "ownership_bytes": 0,
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 pb_service_quicklist audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service_quicklist audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
