#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_teleprompt object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-teleprompt-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-teleprompt-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-teleprompt-provenance.tsv"
PINS = {
    FUNCTION_MAP: "ada7f62b647ff85189ceecb5eb95b74e907f0f5af16e68432c0b292e6d651aaf",
    CLOSURE: "04feed5d56d43550c5204236e201f5f9ad4df694ea88ef5361d60684a217dc7a",
    PROVENANCE: "bd119a525fc365f8cd847531f83444a59e44d1dcc5aa7a0731d0d481519eacae",
}
PHYSICAL = (0x005885B4, 0x00588D74)
PHYSICAL_SHA256 = "06e85d974b48111ab51fbfdff1cc23c56e1274f4971f1ca5407989440b75d0cc"
TAIL = (0x00588CF2, 0x00588D74)
TAIL_SHA256 = "9bd568fdf74affc604e3f493fa2fa3665bc5a08a87e1b828be1a8271364ef0c8"
BODY_SHA256 = "24f933ac204a24fdd8946526538df3b7e301314c079c8ea60a7b0c59813f8b3b"
ENTRY_SHA256 = "5e4c0ef3ef52542ca56e9096513b22e90ccae468c7581d55ac1fcd6f4f5a6ff4"
BODY_CALL_SHA256 = "282e521c4d6235324b225e5c55e988324055d5074328f2303b73b5667fa58a91"
FALSE_INTERIOR_SHA256 = "daf1c8e90e6bd4a796331e1a3db3e5cdb6bfa023aeb1368e33cb22e427eb784b"
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_teleprompt\pb_service_teleprompt.c"
)
TAIL_WORDS = (
    0x0076FA90, 0x00757E90, 0x006D9634, 0x00787F10,
    0x0074C6D4, 0x007824AC, 0x0077C304, 0x0078DF74,
    0x007824C0, 0x00757EB4, 0x20074FFE, 0x007178C0,
    0x006F514C, 0x20074870, 0x006F5198, 0x006E12C0,
    0x200F873C, 0x2037C9A0, 0x007824D4, 0x00757ED8,
    0x00757EFC, 0x007824E8, 0x0076FAAC, 0x0077A6CC,
    0x007637F0, 0x00763810, 0x0076FAC8, 0x0076FAE4,
    0x00763830, 0x00763850, 0x0076FB00, 0x0076FB1C,
)
STRINGS = {
    0x0076FA90: "pData or message is NULL",
    0x00757E90: "APP_PbRxTelepromptFrameDataProcess",
    0x006D9634: RETAINED_PATH,
    0x00787F10: "pb.teleprompt",
    0x0074C6D4: "[pb.teleprompt]pData or message is NULL",
    0x007824AC: "Teleprompt_pb_rx",
    0x0078DF74: "(none)",
    0x007824C0: "Decoding failed: %s",
    0x00757EB4: "[pb.teleprompt]Decoding failed: %s",
    0x007178C0: "command_id: %d, magic number = %d, last magic number = %d",
    0x006F514C: "[pb.teleprompt]command_id: %d, magic number = %d, last magic number = %d",
    0x006F5198: "Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore",
    0x006E12C0: "[pb.teleprompt]Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore",
    0x007824D4: "Encoding failed: %s",
    0x00757ED8: "APP_PbTelepromptTxEncodeCommResp",
    0x00757EFC: "[pb.teleprompt]Encoding failed: %s",
    0x007824E8: "Teleprompt_pb_resp",
    0x0076FAAC: "APP_PbTxEncodeStatusNotify",
    0x0077A6CC: "Teleprompt_pb_notify",
    0x007637F0: "APP_PbTxEncodeFileListRequest",
    0x00763810: "Teleprompt_pb_file_list_request",
    0x0076FAC8: "APP_PbTxEncodeFileSelect",
    0x0076FAE4: "Teleprompt_pb_file_select",
    0x00763830: "APP_PbTxEncodePageDataRequest",
    0x00763850: "Teleprompt_pb_page_data_request",
    0x0076FB00: "APP_PbTxEncodeScrollSync",
    0x0076FB1C: "Teleprompt_pb_scroll_sync",
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
    if len(rows) != 7 or sum(map(len, bodies)) != 1854:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")
    tail = image_slice(data, *TAIL)
    if len(tail) != 130 or sha256(tail) != TAIL_SHA256 or tail[:2] != b"\0\0":
        raise AuditError("alignment/literal tail changed")
    if struct.unpack("<32I", tail[2:]) != TAIL_WORDS:
        raise AuditError("literal pool layout changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("1fb5dff8"):
        raise AuditError("next-function boundary changed")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == 0x006D9634]
    if path_cells != [0x00588CFC]:
        raise AuditError("retained path-pointer closure changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entry: list[tuple[int, int]] = []
    raw_interior: list[tuple[int, int]] = []
    entry_bw: list[tuple[int, int]] = []
    interior_bw: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            raw_interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    expected_entry = [
        (0x0055416A, 0x0058887A), (0x00555450, 0x00588C16),
        (0x00555870, 0x00588968), (0x005560B8, 0x00588A56),
        (0x0058A00A, 0x005885B4), (0x0058A05E, 0x00588792),
        (0x0058A0B4, 0x00588792), (0x0058A10C, 0x00588792),
        (0x0058A11A, 0x00588792), (0x0058A2A8, 0x0058887A),
        (0x0058ACC6, 0x00588B40),
    ]
    if entry != expected_entry or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("direct entry closure changed")
    expected_false = [(0x0057FE74, 0x005885D8)]
    if raw_interior != expected_false or pair_digest(raw_interior) != FALSE_INTERIOR_SHA256:
        raise AuditError("raw interior candidate closure changed")
    if image_slice(data, 0x0057FE72, 0x0057FE76) != bytes.fromhex("00fb08f0"):
        raise AuditError("MUL overlap proof changed")
    if entry_bw or interior_bw:
        raise AuditError("direct B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 98 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if stored:
        raise AuditError("unexpected stored entry/interior pointer")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("pb_service_teleprompt" in source.get("path", "").lower()
                 for source in overlay["sources"])
    if routed:
        raise AuditError("unimplemented teleprompt service unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 7,
            "body_bytes": 1854,
            "owned_tail_bytes": 130,
            "physical_bytes": 1984,
            "direct_bl_entry_sites": 11,
            "direct_body_calls": 98,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "false_halfword_bl_candidates": 1,
        },
        "contracts": {
            "rx_status": {"success": 0, "decode_failure": 5,
                          "null": 6, "duplicate": 13},
            "duplicate_window_ms": 3000,
            "rx_hexdump_limit": 0x20,
            "tx_status": {"success": 0, "encode_failure": 0x2B},
            "tx_pointer_null_guards": False,
            "route": 1,
            "service": 6,
            "message": "0x200f873c",
            "message_bytes": 0xF58,
            "encode_buffer": "0x2037c9a0",
            "encode_capacity": 0x100,
            "last_magic": "0x20074ffe",
            "last_magic_tick": "0x20074870",
            "envelopes": {
                "command_response": {"command": 0xA6, "tag": 12, "send": "tx",
                                     "payload_bytes": 1, "caller_magic": True},
                "status": {"command": 0xA1, "tag": 7, "send": "notify",
                           "payload_bytes": 2},
                "file_list": {"command": 0xA2, "tag": 8, "send": "notify",
                              "payload_bytes": 1},
                "file_select": {"command": 0xA3, "tag": 9, "send": "notify",
                                "payload_bytes": 0x42},
                "page_data": {"command": 0xA4, "tag": 10, "send": "notify",
                              "payload_bytes": 4},
                "scroll_sync": {"command": 0xA5, "tag": 11, "send": "notify",
                                "payload_bytes": 12},
            },
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
    print("G2 pb_service_teleprompt audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
