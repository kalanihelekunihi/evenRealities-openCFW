#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_glasses_case object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-glasses-case-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-glasses-case-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-glasses-case-provenance.tsv"
PINS = {
    FUNCTION_MAP: "9a4b8121f28d1b0692a6ce7416b8f33946246b39b64ae66cf8acd03d5013d5fe",
    CLOSURE: "a3d6a92a20a5540c070e3fb2d8fdef5946d2cbe14a24c780157bc968e19137c7",
    PROVENANCE: "051a928dd67a5bc3f46154204f7beeed0455459f1fe793061ed5ac8e1cdf8703",
}
PHYSICAL = (0x00510A0C, 0x00510FD8)
PHYSICAL_SHA256 = "ac1926863f4700afd938a0f9d234c3a6c0be103f327f591c7cc066d13be61bf2"
POOL = (0x00510F5C, 0x00510FD8)
POOL_SHA256 = "e6e942104a74517b41485867b0b592911951af365363935b324d92110a362de1"
BODY_SHA256 = "39f291afe8bb87e933c35c4d28ed0a66f7f925dcdb0ca765b2bf3562f25e2472"
ENTRY_SHA256 = "8b88414a2a4ea904a86c373f4489b4925766a5ba0942d815639a37690086ea2b"
BODY_CALL_SHA256 = "ac3635c1e3013186a5d1f9cada25caac3e1089d399281468c5e3e6da88d8ef25"
RAW_WINDOW_SHA256 = "8dc7a9779381da6b39105f4564beb7fe749aa1f578dc0bfb91eccb70dfe543a4"
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_glasses_case\pb_service_glasses_case.c"
)
POOL_WORDS = (
    0x0078DEBC, 0x007579C8, 0x006D7B1C, 0x00787DA0, 0x0077A2AC,
    0x00787DB0, 0x007633F0, 0x200F5A90, 0x0077793C, 0x0078DEC4,
    0x00781DF4, 0x0074C33C, 0x0076F684, 0x00736704, 0x0077A2C4,
    0x0074C364, 0x00781E08, 0x00787DC0, 0x0077A2DC, 0x00763410,
    0x00781E1C, 0x00763430, 0x2037C5A0, 0x200F5A9C, 0x0078B714,
    0x0076F6A0, 0x0077A2F4, 0x0074C38C, 0x00781E30, 0x007579EC,
    0x20074FFA,
)
STRINGS = {
    0x0078DEBC: "len=%d",
    0x007579C8: "APP_PbRxGlassesCaseFrameDataProcess",
    0x006D7B1C: RETAINED_PATH,
    0x00787DA0: "pb.glasses_case",
    0x0077A2AC: "[pb.glasses_case]len=%d",
    0x00787DB0: "pData is NULL",
    0x007633F0: "[pb.glasses_case]pData is NULL",
    0x0078DEC4: "(none)",
    0x00781DF4: "Decoding failed: %s",
    0x0074C33C: "[pb.glasses_case]Decoding failed: %s",
    0x0076F684: "glasses_case command_id: %d",
    0x00736704: "[pb.glasses_case]glasses_case command_id: %d",
    0x0077A2C4: "Unknown command_id: %d",
    0x0074C364: "[pb.glasses_case]Unknown command_id: %d",
    0x00787DC0: "POINTER NULL",
    0x0077A2DC: "PB_RxGlassesCaseInfo",
    0x00763410: "[pb.glasses_case]POINTER NULL",
    0x00763430: "APP_PbTxEncodeGlassesCaseInfo",
    0x0078B714: "txLen = %d",
    0x0076F6A0: "[pb.glasses_case]txLen = %d",
    0x0077A2F4: "Encoding failed: %s\n",
    0x0074C38C: "[pb.glasses_case]Encoding failed: %s\n",
    0x007579EC: "APP_PbNotifyEncodeGlassesCaseInfo",
}
ASSERT_RECORDS = {
    0x00781E08: "00000000000000001c7b6d00dca2770056000000",
    0x00781E1C: "00000000000000001c7b6d003034760064000000",
    0x00781E30: "00000000000000001c7b6d00ec7975008a000000",
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
    if len(rows) != 4 or sum(map(len, bodies)) != 1360:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")
    pool = image_slice(data, *POOL)
    if len(pool) != 124 or sha256(pool) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if struct.unpack("<31I", pool) != POOL_WORDS:
        raise AuditError("literal pool layout changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("80b50020"):
        raise AuditError("next-function boundary changed")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    for address, expected_hex in ASSERT_RECORDS.items():
        if image_slice(data, address, address + 20).hex() != expected_hex:
            raise AuditError(f"assert record changed at 0x{address:08x}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == 0x006D7B1C]
    if path_cells != [0x00510F64, 0x00781E10, 0x00781E24, 0x00781E38]:
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
        (0x004ABF7E, 0x00510DEC), (0x004ACB52, 0x00510A0C),
        (0x00510B9C, 0x00510BFE), (0x00510BA8, 0x00510C70),
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
    if len(calls) != 86 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_windows: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_windows.append((BASE + offset, value))
    if len(raw_windows) != 6 or pair_digest(raw_windows) != RAW_WINDOW_SHA256:
        raise AuditError("raw pointer-window closure changed")
    if any((value & ~1) in starts for _, value in raw_windows):
        raise AuditError("unexpected stored exact-entry pointer")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("pb_service_glasses_case" in source.get("path", "").lower()
                 for source in overlay["sources"])
    if routed:
        raise AuditError("unimplemented glasses-case service unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 4,
            "body_bytes": 1360,
            "owned_pool_bytes": 124,
            "physical_bytes": 1484,
            "direct_bl_entry_sites": 4,
            "direct_body_calls": 86,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 6,
        },
        "contracts": {
            "rx_status": {"success": 0, "unsupported_or_invalid": 1,
                          "null": 2, "decode_failure": 0x2B},
            "tx_status": {"success": 0, "null": 2, "encode_failure": 0x2B},
            "command_id": 1,
            "nested_payload_tag": 3,
            "route": 1,
            "service": "0x81",
            "decoded_message": "0x200f5a90",
            "encoded_message": "0x200f5a9c",
            "message_bytes": 10,
            "encode_buffer": "0x2037c5a0",
            "encode_capacity": 0x100,
            "notify_sequence": "0x20074ffa",
            "case_info_bytes": ["battery", "charging", "lid", "glasses_present", "error"],
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": [row["function"] for row in rows],
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
    print("G2 pb_service_glasses_case audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
