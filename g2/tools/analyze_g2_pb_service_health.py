#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_health object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-health-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-health-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-health-provenance.tsv"
PINS = {
    FUNCTION_MAP: "ad537fecc545895e0aea563c0f99ff41a87b6b0462b60ef4c7ec1649f9a4a221",
    CLOSURE: "a50cc002ef2cc5f95cf1d44b4e1b1ef37435d3c64cfd97d56ad0f0c2ea7d182f",
    PROVENANCE: "870b08b8bd6d540e39760abc48b1c95eb6990550ae3af17a726e8774a36b51e9",
}
PHYSICAL = (0x0055A558, 0x0055B2A4)
PHYSICAL_SHA256 = "9020db98fd11e16ce082853f8556a94795330c4f1f178ab6765685c1438ff1ab"
BODY_SHA256 = "13f8aad04ac998d93e5ce8c836cdbaa7633fbe0ab128a9a6395e2fe7665bb6dc"
GAPS = (
    (0x0055AB90, 0x0055ABE0, "a2c14466f889dc5a1a4437ddd50e8dceda2cba85e786d63478846f302aa69371"),
    (0x0055AD52, 0x0055AD78, "38ccf4bde78cb5f4dac46b430243dfcf587dcf266f12bb730ac8e599a8905205"),
    (0x0055AF00, 0x0055AF14, "1b51bdd31d48b5aaaa2f18fa68b4ab05dfd981d95c3a06de5c519710f1212bc1"),
    (0x0055B058, 0x0055B06C, "fb6b962b9a36d9f044fe49a81177128b3deb745376382f527a43d9a7d9e40bd2"),
    (0x0055B20A, 0x0055B2A4, "f647e3f310c4f14441d57ef6fbb81327b904a0d7c31067bdb400fb6d50036ff5"),
)
GAP_SHA256 = "c2d3d3d79212fe12b139f420b07a3ad907f1ae391290b68a9a1ee0177d289d87"
ASSERT_RECORDS = (0x00781E80, 0x00781F20)
ASSERT_SHA256 = "d60ee030f371c3c3032c4833556e1c7b94ed29195b021900664d795e0cc00d88"
ENTRY_SHA256 = "797890f14acfc2883c146beb1177aafba703e12f47a1817d25bd302fd0953e4e"
BODY_CALL_SHA256 = "1103059660848fa4b2c83c7b8f73ec9e786f5f02b464f4d830398e010e9b2346"
RAW_WINDOW_SHA256 = "b8a3f10b322ed0b9e0394b16f55df14f16aedbe57bf411523a6a6d90359b641f"
RETAINED_PATH_ADDRESS = 0x006DE134
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_health\pb_service_health.c"
)
SYMBOLS = (
    (0x0077A324, "PB_RxHealthSingleData", 109),
    (0x00763490, "APP_PbTxEncodeHealthSingleData", 132),
    (0x00781E6C, "PB_RxHealthMultData", 213),
    (0x007634D0, "APP_PbTxEncodeHealthMultData", 237),
    (0x0076F6D8, "PB_RxHealthSingleHighlight", 313),
    (0x00757A34, "APP_PbTxEncodeHealthSingleHighlight", 336),
    (0x0076F6F4, "PB_RxHealthMultHighlight", 374),
    (0x00757A7C, "APP_PbTxEncodeHealthMultHighlight", 398),
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
    offset = address - BASE
    first, second = struct.unpack_from("<HH", data, offset)
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
    if len(rows) != 8 or sum(map(len, bodies)) != 3092:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 312 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("a9b1b1fa"):
        raise AuditError("next-function boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    assertions = image_slice(data, *ASSERT_RECORDS)
    if sha256(assertions) != ASSERT_SHA256:
        raise AuditError("assertion records changed")
    for index, (symbol, name, line) in enumerate(SYMBOLS):
        if cstring(data, symbol) != name:
            raise AuditError(f"retained symbol changed at 0x{symbol:08x}")
        record = struct.unpack_from("<5I", assertions, index * 20)
        if record != (0, 0, RETAINED_PATH_ADDRESS, symbol, line):
            raise AuditError(f"assertion metadata changed: {name}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != [0x0055ABB8, 0x0055B234, 0x00781E88, 0x00781E9C,
                      0x00781EB0, 0x00781EC4, 0x00781ED8, 0x00781EEC,
                      0x00781F00, 0x00781F14]:
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
        (0x0055A4F0, 0x0055A558), (0x0055A4FC, 0x0055A702),
        (0x0055A50A, 0x0055A8A2), (0x0055A516, 0x0055AA14),
        (0x0055A524, 0x0055ABE0), (0x0055A530, 0x0055AD78),
        (0x0055A53E, 0x0055AF14), (0x0055A54A, 0x0055B06C),
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
    if len(calls) != 180 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")
    helper_calls = [(0x0055A656, 0x005598CC), (0x0055A960, 0x00559AD2),
                    (0x0055ACA2, 0x00559DFC), (0x0055AFBC, 0x00559FB8)]
    if not all(call in calls for call in helper_calls):
        raise AuditError("health-data helper topology changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if stored != [(0x00643337, 0x0055B1FF)] or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

    workspace = tuple(struct.unpack_from("<I", data, address - BASE)[0]
                      for address in (0x0055AD70, 0x0055AD74,
                                      0x0055B260, 0x0055B264))
    if workspace != (0x2037C6A0, 0x200F5DC4, 0x2037C6A0, 0x200F5DC4):
        raise AuditError("shared health workspace changed")
    if (struct.unpack_from("<I", data, 0x0055ABB0 - BASE)[0] != 0x00777A14
            or struct.unpack_from("<I", data, 0x0055B224 - BASE)[0] != 0x00777A14):
        raise AuditError("health nanopb field descriptor changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("pb_service_health" in source.get("path", "").lower()
                 for source in overlay["sources"])
    if routed:
        raise AuditError("unimplemented health service entered production overlay")

    return {
        "surface": {
            "linked_functions": 8, "body_bytes": 3092,
            "owned_gap_pool_bytes": 312, "physical_bytes": 3404,
            "assertion_records": 8, "direct_bl_entry_sites": 8,
            "direct_body_calls": 180, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 1,
            "manually_restored_bodies": 1,
        },
        "contracts": {
            "rx_status": {"success": 0, "helper_failure": 1, "null": 2},
            "rx_helpers": [f"0x{target:08x}" for _, target in helper_calls],
            "tx_status": {"success": 0, "encode_failure": 0x2B, "null": 2},
            "envelopes": {1: "single_data_tag_3", 2: "multiple_data_tag_4",
                          3: "single_highlight_tag_5", 4: "multiple_highlight_tag_6"},
            "route": 1, "service": 0x0E,
            "message": "0x200f5dc4", "message_bytes": 0x31C,
            "encode_buffer": "0x2037c6a0", "encode_capacity": 0x100,
            "multi_highlight_count_bits": 16,
            "multi_highlight_wrapper_has_explicit_count_bound": False,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": [name for _, name, _ in SYMBOLS],
            "assertion_lines": [line for _, _, line in SYMBOLS],
        },
        "production": {
            "candidate": None, "production_routed": routed,
            "ownership_bytes": 0, "source_inventory_available": False,
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError, UnicodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service_health audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
