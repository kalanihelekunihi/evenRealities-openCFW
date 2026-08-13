#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 terminal protobuf message handler."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-terminal-pb-msg-handler-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-terminal-pb-msg-handler-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-terminal-pb-msg-handler-provenance.tsv"
PINS = {
    FUNCTION_MAP: "042dade0a6946f4435ff6679940536522725d3345583180b1de692af4cc93d73",
    CLOSURE: "012a75504338dcd6ffcb3d65efe9a40e5acad8fda4bf36c3e3f812a4ec6ad69b",
    PROVENANCE: "5d05b64d33bf7322511b0ac7977790ba1bc2d2452c4d89b6ff02ed62b679fffc",
}
PHYSICAL = (0x005E8178, 0x005EA224)
PHYSICAL_SHA256 = "935c32ef5f91486af8104652d24b97a29b2c5afb6dc3d1a3f952599cc7d740f1"
BODY_SHA256 = "908f4e8e9712ee5793cbe18868b676996b49dbcd59d9d7db3b29552b2e3b0be6"
GAP_SHA256 = "7b9b04cd006de1b723e39877de953f335149d4110a8ecacc79059abcc4dfdca6"
ENTRY_SHA256 = "99b9696b7cdcc15c45b17c34afb5800369757f1d8dd528d11ad1fc9166bf7aa7"
BODY_CALL_SHA256 = "ad193f74944d924142141201bf0af8b16e86192ff8497f19a86d388564d3cede"
RAW_WINDOW_SHA256 = "cc29b100872d40ee8890692b0764f7c65590101d611786142f19f9c98add516a"
RETAINED_PATH_ADDRESS = 0x006F0308
RETAINED_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git\app\gui\terminal"
    r"\terminal_pb_msg_handler.c"
)
PATH_CELLS = (0x005E8C14, 0x005E9380, 0x005E9F64, 0x005EA1F0)
EXACT_SYMBOLS = (
    (0x0075B3B8, "terminal_message_session_matches"),
    (0x00744BC8, "terminal_refresh_session_list_if_visible"),
    (0x0075B3DC, "terminal_apply_session_id_changed"),
    (0x0075B400, "terminal_handle_session_await_user"),
    (0x00744BF4, "terminal_request_runtime_event_if_allowed"),
    (0x00773098, "terminal_action_mode_sync"),
    (0x007730D0, "terminal_action_host_status"),
    (0x007730EC, "terminal_action_asr_result"),
    (0x00766230, "terminal_action_session_status"),
    (0x00766250, "terminal_action_agent_content"),
    (0x0077C94C, "terminal_action_query"),
    (0x00773108, "terminal_action_heart_beat"),
    (0x00773140, "terminal_action_error_msg"),
    (0x00766290, "terminal_log_session_list_items"),
    (0x007662B0, "terminal_action_session_list"),
    (0x0074F564, "terminal_action_session_switch_result"),
    (0x0075B46C, "terminal_action_new_session_result"),
    (0x0075B4B4, "terminal_action_session_id_changed"),
    (0x00773204, "terminal_machine_handler"),
)
GAPS = (
    (0x005E8C04, 0x005E8C48, "40954ab97bbe123fba02aff96ff8ddc332f77e0c288069a3413b7d38423c90e2"),
    (0x005E8E34, 0x005E8E6C, "5f4aac577195384b72fafb71eeca9d1feb3b75bba94fd3a4273b8f1365dc27a7"),
    (0x005E9026, 0x005E9064, "7588fc69b716f6f7808371a6b6b108e4e3cd4a86daa5b6f912a98a551ad7eafb"),
    (0x005E9312, 0x005E9390, "5ad054bcede0cdf0307ac9c73431f439a7bdb9bc5d3ae7d406d5239ec2835f15"),
    (0x005E98DC, 0x005E9900, "08c3019107a6336162a72f2c96c2803a8dfbaa56f542a992a213c24b82580061"),
    (0x005E9AAC, 0x005E9AB8, "5f68ed8ee44024bcbaa1693fbced8ca40596f9397ddd1b8002d6a2098905b301"),
    (0x005E9B02, 0x005E9B08, "a1dea67e0c8ac24bae7014b80f6a4c4004a093f704c5ec68fb506d55e7725bfa"),
    (0x005E9B78, 0x005E9B84, "56193eb744366d4e178ec44e73cc39f3d8fe335b2d40fe2480ba144f2f19983a"),
    (0x005E9C54, 0x005E9C78, "ce446a000c932bd28a76d461c6c8a1882eaafb85161fac2bce48295fd99d69c3"),
    (0x005E9EC2, 0x005E9EC8, "d526b59a10438ae59514e9baa0b841f3dd6da1c0fa0d56898fb2fe3cfb7d86db"),
    (0x005E9F58, 0x005E9F74, "1873ecc10b7714411c45ca2870683db8a8a47268b7c7399cd8abf5825eec2cab"),
    (0x005EA000, 0x005EA004, "73645d14a260e9dbca8fce3d3d5e5186401795295fb0d9ab4f97b3a2829a0edf"),
    (0x005EA01A, 0x005EA028, "ee117474d93823bd0c2b7eb11df3dd2fd6be47ce3ec48c0c9a79fc5ec24a7a75"),
    (0x005EA152, 0x005EA224, "efe94f1c5625b60b72b380bcd7a6079f20c748ccc8b2f5d9eef5179636819611"),
)
ACTION_TABLE = (0x0072EB78, 0x0072EBAC)
ACTION_TABLE_SHA256 = "aa7c116876db936e940a1663ec914d2c14fc8250a5c11a46532a9da7d8dd9442"
ACTION_POINTERS = (
    0,
    0x005E8847, 0x005E8C49, 0x005E8E6D, 0x005E9065,
    0x005E9391, 0x005E9901, 0x005E9AB9, 0x005E9B09,
    0x005E9C79, 0x005E9E63, 0x005E9EC9, 0x005E9F75,
)
CALLBACK_POINTERS = ((0x005E47A8, 0x005E8815), (0x005E9348, 0x005E8815))
EXTERNAL_ENTRIES = tuple((site, 0x005EA028) for site in (
    0x005E4650, 0x005E465C, 0x005E466A, 0x005E4676,
    0x005E4684, 0x005E4692, 0x005E46DA, 0x005E46E8,
    0x005E46F4, 0x005E4700, 0x005E470C, 0x005E4718,
))
RAW_INTERIOR_COLLISION = (0x00569C28, 0x005E9D6E)


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
    if len(rows) != 27 or sum(map(len, bodies)) != 7_688:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps: list[bytes] = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 676 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(image_slice(data, PHYSICAL[0] - 8, PHYSICAL[0])) != \
            "c6457a66a809354ebc5dbe26bc84bef0c7de970d63f0ddf31e7f39e7b424dae3":
        raise AuditError("previous-object boundary changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 8) != bytes.fromhex("70b504000d001600"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    if any(cstring(data, address) != name for address, name in EXACT_SYMBOLS):
        raise AuditError("retained terminal symbol changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != list(PATH_CELLS):
        raise AuditError("retained path-pointer closure changed")

    action_raw = image_slice(data, *ACTION_TABLE)
    if sha256(action_raw) != ACTION_TABLE_SHA256 or \
            struct.unpack("<13I", action_raw) != ACTION_POINTERS:
        raise AuditError("terminal action table changed")
    literal_contract = {
        0x005E8C04: 0x2006E0D0,
        0x005E9348: 0x005E8815,
        0x005EA174: 0x20074A90,
        0x005EA1F0: RETAINED_PATH_ADDRESS,
        0x005EA200: 0x20003E6C,
        0x005EA218: ACTION_TABLE[0],
    }
    if any(struct.unpack_from("<I", data, site - BASE)[0] != value
           for site, value in literal_contract.items()):
        raise AuditError("terminal state/table literal changed")

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
    if len(entries) != 56 or pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct BL entry closure changed")
    if tuple(pair for pair in entries if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])) \
            != EXTERNAL_ENTRIES:
        raise AuditError("external direct-entry closure changed")
    if interior != [RAW_INTERIOR_COLLISION] or bw_hits:
        raise AuditError("raw strict-interior/B.W closure changed")
    if image_slice(data, 0x00569C26, 0x00569C2A) != bytes.fromhex("52fa80f0"):
        raise AuditError("classified UXTAB overlap changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 432 or pair_digest(calls) != BODY_CALL_SHA256:
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
    expected_stored = list(CALLBACK_POINTERS) + [
        (ACTION_TABLE[0] + index * 4, value)
        for index, value in enumerate(ACTION_POINTERS) if value
    ]
    if stored_entries != expected_stored:
        raise AuditError("stored exact-entry closure changed")
    if len(raw_windows) != 54 or pair_digest(raw_windows) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any("terminal_pb_msg_handler" in source.get("path", "").lower()
           for source in overlay["sources"]):
        raise AuditError("unimplemented terminal handler entered production overlay")

    action_names = [None] + [
        "mode_sync", "host_status", "asr_result", "session_status",
        "agent_content", "query", "heart_beat", "error_msg",
        "session_list", "session_switch_result", "new_session_result",
        "session_id_changed",
    ]
    return {
        "surface": {
            "retained_path_anchors": 10,
            "restored_pathless_functions": 17,
            "linked_functions": 27,
            "body_bytes": 7_688,
            "owned_gap_pool_bytes": 676,
            "physical_bytes": 8_364,
            "direct_bl_entry_sites": 56,
            "external_direct_bl_entry_sites": 12,
            "direct_body_calls": 432,
            "stored_exact_entry_pointers": 14,
            "raw_direct_interior_candidates": 1,
            "classified_instruction_overlaps": 1,
            "strict_interior_ingress": 0,
            "b_w_entry_or_interior_targets": 0,
            "raw_instruction_windows": 54,
        },
        "contracts": {
            "event_min": 0,
            "event_max": 12,
            "event_actions": dict(enumerate(action_names)),
            "null_or_invalid_action_result": -1,
            "state_base_address": "0x2006e0d0",
            "states_allowing_runtime_event": [0, 2, 7, 11, 12],
            "processing_states": [1, 2, 3],
            "session_list_log_limit": 10,
            "tool_start_dedup_ms": 2_000,
            "callback_pointer_cells": [f"0x{site:08x}" for site, _ in CALLBACK_POINTERS],
            "action_table_address": "0x0072eb78",
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
        print(f"G2 terminal protobuf message-handler audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 terminal protobuf message-handler audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
