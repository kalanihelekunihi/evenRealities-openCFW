#!/usr/bin/env python3
"""Pin the production system packetAck (0x7e) callback-resolution contract.

This analyzer reads only the supplied image. It never sends BLE traffic, resolves a live pending
request, invokes a device callback, accesses sensors/storage, or contacts physical hardware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


RANGES = [
    (
        0x000842CC,
        0x000842EC,
        "c12d71da129cc9b2728efaa5ec62e6559b0d5f56e30b5c2eb34fa245aa1b228a",
        "system packetAck handler",
    ),
    (
        0x00083028,
        0x000830A4,
        "c9255dbfec632de4de0f3d02373fb1dff794a1b8d6c380e318304744d8276486",
        "pending-callback resolver",
    ),
    (
        0x00082BD4,
        0x00082BE6,
        "1f0181948d602c0210ecae853b284d17e6b01d0e14a901c8b6548d03d81c9dac",
        "payload-presence helper",
    ),
]
HANDLER_START = 0x000842CC
HANDLER_END = 0x000842EC
RESOLVER_START = 0x00083028
RESOLVER_END = 0x000830A4
PAYLOAD_HELPER = 0x00082BD4
LOCK_ENTER = 0x00048234
LOCK_EXIT = 0x00048258
REGISTRATION_ADDRESS = 0x0009A54C
REGISTRATION_BYTES = bytes.fromhex("7e000000cd420800")
PENDING_TABLE_LITERAL_ADDRESS = 0x000830A4
PENDING_TABLE_ADDRESS = 0x20019EF4
EXPECTED_PAYLOAD_HELPER_BRANCHES = [
    0x00083D0C,
    0x00083FC6,
    0x00084154,
    0x000842D0,
    0x000842F4,
    0x000843D0,
    0x000844B8,
    0x000844F4,
    0x000845C2,
    0x000846EE,
    0x0008487A,
    0x00084A1A,
]
EXPECTED_LOCK_ENTER_BRANCHES = [
    0x000824A4,
    0x000825CA,
    0x00083034,
    0x00083A0A,
    0x00083B40,
    0x00083B64,
]
EXPECTED_LOCK_EXIT_BRANCHES = [
    0x00082534,
    0x00082662,
    0x00083080,
    0x0008309C,
    0x00083AB0,
    0x00083B56,
    0x00083B7A,
]


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


def checked_range(
    image: bytes,
    base: int,
    start: int,
    end: int,
    expected: str,
    label: str,
) -> dict[str, str]:
    actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
    if actual != expected:
        raise ValueError(f"unexpected {label} range: {actual}")
    return {
        "label": label,
        "start": f"0x{start:08x}",
        "end_exclusive": f"0x{end:08x}",
        "sha256": actual,
    }


def branch_addresses(image: bytes, base: int, target: int) -> list[int]:
    return [address for address, _ in direct_thumb_branches_to(image, base, target)]


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")
    verified = [
        checked_range(image, base, start, end, sha, label)
        for start, end, sha, label in RANGES
    ]
    registration = flash_bytes(
        image, base, REGISTRATION_ADDRESS, REGISTRATION_ADDRESS + len(REGISTRATION_BYTES)
    )
    if registration != REGISTRATION_BYTES:
        raise ValueError(f"unexpected packetAck registration: {registration.hex()}")
    if branch_addresses(image, base, RESOLVER_START) != [0x000842E4]:
        raise ValueError("unexpected pending-callback resolver callers")
    if branch_addresses(image, base, PAYLOAD_HELPER) != EXPECTED_PAYLOAD_HELPER_BRANCHES:
        raise ValueError("unexpected payload-helper callers")
    if branch_addresses(image, base, LOCK_ENTER) != EXPECTED_LOCK_ENTER_BRANCHES:
        raise ValueError("unexpected lock-enter callers")
    if branch_addresses(image, base, LOCK_EXIT) != EXPECTED_LOCK_EXIT_BRANCHES:
        raise ValueError("unexpected lock-exit callers")
    if direct_thumb_branches_to(image, base, HANDLER_START):
        raise ValueError("table-dispatched packetAck handler acquired a direct branch")
    table_literal = int.from_bytes(
        flash_bytes(
            image,
            base,
            PENDING_TABLE_LITERAL_ADDRESS,
            PENDING_TABLE_LITERAL_ADDRESS + 4,
        ),
        "little",
    )
    if table_literal != PENDING_TABLE_ADDRESS:
        raise ValueError(f"unexpected pending table literal: 0x{table_literal:08x}")

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": verified,
        "registration": {
            "address": f"0x{REGISTRATION_ADDRESS:08x}",
            "system_subcommand": "0x7e",
            "handler_thumb": "0x000842cd",
            "raw_hex": registration.hex(),
        },
        "payload_gate": {
            "declared_frame_length_offset": 8,
            "header_bytes": 12,
            "only_no_payload_value": 12,
            "every_other_uint16_value_is_treated_as_payload_present": True,
            "significant_payload_bytes_read": 6,
            "minimum_payload_length_checked": False,
            "short_declared_payload_can_be_read_past": True,
        },
        "acknowledged_key": {
            "module_offset": 0,
            "command_offset": 1,
            "subcommand_offset": 2,
            "reserved_offset_ignored": 3,
            "sequence_uint16_le_offset": 4,
        },
        "pending_table": {
            "runtime_address": f"0x{PENDING_TABLE_ADDRESS:08x}",
            "entry_count": 32,
            "entry_stride": 20,
            "active_offset": 0,
            "module_offset": 1,
            "command_offset": 2,
            "subcommand_offset": 3,
            "sequence_uint16_le_offset": 4,
            "callback_thumb_offset": 8,
            "callback_context_offset": 12,
            "unread_tail_offset": 16,
        },
        "match_semantics": {
            "scan_order": "index 0 through 31",
            "first_exact_active_match_only": True,
            "fields_cleared_under_lock": ["active", "callback_thumb", "callback_context"],
            "key_and_unread_tail_preserved": True,
            "callback_invoked_after_unlock": True,
            "null_callback_still_consumes_match": True,
            "callback_argument": "saved callback context",
            "protocol_response_emitted": False,
        },
        "complete_direct_branch_sets": {
            "resolver": ["0x000842e4"],
            "payload_helper": [f"0x{value:08x}" for value in EXPECTED_PAYLOAD_HELPER_BRANCHES],
            "lock_enter": [f"0x{value:08x}" for value in EXPECTED_LOCK_ENTER_BRANCHES],
            "lock_exit": [f"0x{value:08x}" for value in EXPECTED_LOCK_EXIT_BRANCHES],
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "live_callback_resolution": False,
            "sensor_access": False,
            "storage_access": False,
            "health_store_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image, args.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
