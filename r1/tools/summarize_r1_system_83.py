#!/usr/bin/env python3
"""Pin the registered but previously unlabeled R1 system subcommand 0x83 handler.

This analyzer reads only the supplied production image. It never sends a command, opens BLE,
executes firmware, accesses a sensor, or mutates device state.
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


HANDLER_START = 0x00084860
HANDLER_END = 0x00084874
HANDLER_SHA256 = "8fca7ef3e1f3fe1a461dd2dfcc6cba89221e69145ab3cbf0609e68fc229ac87f"
SYSTEM_TABLE_START = 0x0009A4CC
SYSTEM_TABLE_END = 0x0009A56C
SYSTEM_TABLE_SHA256 = "57bebd7948fd9cddfdfc4e8069492fc7b2088204d77e143e61d2f727b414ec50"
REGISTRATION_ADDRESS = 0x0009A564
REGISTRATION_BYTES = bytes.fromhex("8300000061480800")
RESPONSE_HELPER = 0x0008287C
EXPECTED_RESPONSE_HELPER_BRANCHES = [
    0x00083D2C, 0x00083D40, 0x00083E3A, 0x00083FDA, 0x000843EE,
    0x00084402, 0x000844CE, 0x0008450A, 0x000845BC, 0x00084728,
    0x0008486E, 0x00084A3A, 0x00084A98,
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
) -> dict[str, str]:
    actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
    if actual != expected:
        raise ValueError(f"unexpected range 0x{start:08x}...0x{end:08x}: {actual}")
    return {
        "start": f"0x{start:08x}",
        "end_exclusive": f"0x{end:08x}",
        "sha256": actual,
    }


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")
    ranges = [
        checked_range(image, base, HANDLER_START, HANDLER_END, HANDLER_SHA256),
        checked_range(
            image,
            base,
            SYSTEM_TABLE_START,
            SYSTEM_TABLE_END,
            SYSTEM_TABLE_SHA256,
        ),
    ]
    registration = flash_bytes(
        image,
        base,
        REGISTRATION_ADDRESS,
        REGISTRATION_ADDRESS + len(REGISTRATION_BYTES),
    )
    if registration != REGISTRATION_BYTES:
        raise ValueError(f"unexpected system 0x83 registration: {registration.hex()}")
    branches = [
        address
        for address, _ in direct_thumb_branches_to(image, base, RESPONSE_HELPER)
    ]
    if branches != EXPECTED_RESPONSE_HELPER_BRANCHES:
        raise ValueError(f"unexpected response-helper branches: {branches}")
    if direct_thumb_branches_to(image, base, HANDLER_START):
        raise ValueError("table-dispatched system 0x83 handler acquired a direct branch")

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "registration": {
            "address": f"0x{REGISTRATION_ADDRESS:08x}",
            "system_subcommand": "0x83",
            "handler_thumb": "0x00084861",
            "raw_hex": registration.hex(),
        },
        "response_helper": {
            "address": f"0x{RESPONSE_HELPER:08x}",
            "complete_direct_branch_set": [
                f"0x{address:08x}" for address in branches
            ],
            "handler_callsite": "0x0008486e",
        },
        "handler": {
            "request_fields_read": ["unaligned UInt16 serial at request + 3"],
            "request_flags_read": False,
            "request_payload_read": False,
            "request_length_checked": False,
            "response": {
                "identifier": "0x0083",
                "type_raw": 1,
                "status_raw": 0,
                "request_serial_preserved": True,
                "payload_bytes": 0,
            },
            "additional_calls": 0,
            "internal_events": 0,
            "state_reads_or_writes": 0,
            "semantic": "registered empty-success compatibility no-op",
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "state_mutation": False,
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
