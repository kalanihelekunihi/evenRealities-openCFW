#!/usr/bin/env python3
"""Pin production deviceInfo and deviceSn response construction.

This analyzer reads only the supplied image. It never opens BLE, reads a physical identifier,
accesses live KV state, contacts hardware, or emits identity data from a device.
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
        0x00083D5C,
        0x00083D92,
        "ca488bc5d2c09ccdc2b23498dca88d567f1c9608d89903be56e84bc8a914f54d",
        "deviceInfo handler",
    ),
    (
        0x00083DB0,
        0x00083DE4,
        "8450589e77e0cac3080025f8a0d4d97a6b00e44d306165b3081a485a54f321f0",
        "deviceSn handler",
    ),
    (
        0x00083872,
        0x00083896,
        "5042d1eefd585ef1f71e9f7a0e9098c2df75358ba66c4402c0fa6c3197dce0c9",
        "fixed-32-byte deviceInfo response wrapper",
    ),
    (
        0x0007BA78,
        0x0007BABE,
        "e0798f9c1010c8dff11ebfc078a447b33494e900e8090f4af1a9f2fb896cfa31",
        "fixed-15-byte product-serial getter",
    ),
]
DEVICE_INFO_HANDLER = 0x00083D5C
DEVICE_INFO_HANDLER_END = 0x00083D92
DEVICE_SERIAL_HANDLER = 0x00083DB0
DEVICE_SERIAL_HANDLER_END = 0x00083DE4
FORMATTER = 0x00038080
DEVICE_INFO_RESPONSE = 0x00083872
DEVICE_SERIAL_GETTER = 0x0007BA78
GENERIC_RESPONSE = 0x00084C5E
DEVICE_INFO_REGISTRATION = 0x0009A4D4
DEVICE_INFO_REGISTRATION_BYTES = bytes.fromhex("020000005d3d0800")
DEVICE_SERIAL_REGISTRATION = 0x0009A534
DEVICE_SERIAL_REGISTRATION_BYTES = bytes.fromhex("10000000b13d0800")
APPLICATION_VERSION_ADDRESS = 0x00083D94
APPLICATION_VERSION = b"2.2.6.0009"
FORMAT_ADDRESS = 0x00083DA0
FORMAT = b"%s"
HARDWARE_VERSION_ADDRESS = 0x00083DA4
HARDWARE_VERSION = b"603MV1.9.3"
EXPECTED_FORMATTER_BRANCHES = [
    0x00041ACE,
    0x0004F290,
    0x0004F40E,
    0x0006ABBC,
    0x000774C8,
    0x00083D72,
    0x00083D7E,
    0x0008EF66,
    0x0008EFEA,
    0x0009153A,
    0x0009156A,
]
EXPECTED_SERIAL_GETTER_BRANCHES = [
    0x00048A74,
    0x0006251C,
    0x0006253E,
    0x00062ACE,
    0x0006A1EE,
    0x00083DC6,
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


def checked_c_string(image: bytes, base: int, address: int, expected: bytes) -> str:
    actual = flash_bytes(image, base, address, address + len(expected) + 1)
    if actual != expected + b"\0":
        raise ValueError(f"unexpected string at 0x{address:08x}: {actual!r}")
    return actual[:-1].decode("ascii")


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")
    verified = [
        checked_range(image, base, start, end, sha, label)
        for start, end, sha, label in RANGES
    ]
    registrations = [
        (
            DEVICE_INFO_REGISTRATION,
            DEVICE_INFO_REGISTRATION_BYTES,
            "0x02",
            "0x00083d5d",
        ),
        (
            DEVICE_SERIAL_REGISTRATION,
            DEVICE_SERIAL_REGISTRATION_BYTES,
            "0x10",
            "0x00083db1",
        ),
    ]
    registration_output = []
    for address, expected, subcommand, handler in registrations:
        actual = flash_bytes(image, base, address, address + 8)
        if actual != expected:
            raise ValueError(f"unexpected identity registration at 0x{address:08x}")
        registration_output.append({
            "address": f"0x{address:08x}",
            "system_subcommand": subcommand,
            "handler_thumb": handler,
            "raw_hex": actual.hex(),
        })
    if branch_addresses(image, base, FORMATTER) != EXPECTED_FORMATTER_BRANCHES:
        raise ValueError("unexpected bounded-formatter callers")
    if branch_addresses(image, base, DEVICE_INFO_RESPONSE) != [0x00083D8A]:
        raise ValueError("unexpected deviceInfo response-wrapper callers")
    if branch_addresses(image, base, DEVICE_SERIAL_GETTER) != EXPECTED_SERIAL_GETTER_BRANCHES:
        raise ValueError("unexpected product-serial getter callers")
    generic_calls = [
        address
        for address in branch_addresses(image, base, GENERIC_RESPONSE)
        if DEVICE_SERIAL_HANDLER <= address < DEVICE_SERIAL_HANDLER_END
    ]
    if generic_calls != [0x00083DDC]:
        raise ValueError(f"unexpected deviceSn response calls: {generic_calls}")
    if direct_thumb_branches_to(image, base, DEVICE_INFO_HANDLER):
        raise ValueError("table-dispatched deviceInfo handler acquired a direct branch")
    if direct_thumb_branches_to(image, base, DEVICE_SERIAL_HANDLER):
        raise ValueError("table-dispatched deviceSn handler acquired a direct branch")

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": verified,
        "registrations": registration_output,
        "device_info": {
            "payload_bytes": 32,
            "slot_count": 2,
            "slot_bytes": 16,
            "bounded_string_capacity_including_nul": 16,
            "slot_0": {
                "source_address": f"0x{APPLICATION_VERSION_ADDRESS:08x}",
                "value": checked_c_string(
                    image, base, APPLICATION_VERSION_ADDRESS, APPLICATION_VERSION
                ),
                "meaning": "application version",
            },
            "slot_1": {
                "source_address": f"0x{HARDWARE_VERSION_ADDRESS:08x}",
                "value": checked_c_string(
                    image, base, HARDWARE_VERSION_ADDRESS, HARDWARE_VERSION
                ),
                "meaning": "hardware version",
            },
            "format_string": checked_c_string(image, base, FORMAT_ADDRESS, FORMAT),
            "request_serial_echoed": True,
            "incoming_session_argument_used": False,
            "response_session_source": "current EUS session helper",
        },
        "device_serial": {
            "payload_bytes": 15,
            "source": "product serial field in 124-byte NV record",
            "valid_path": "copy exactly 15 bytes without requiring a NUL terminator",
            "unavailable_path_hex": "ff" * 15,
            "optional_length_output_when_called_by_handler": False,
            "request_serial_echoed": True,
            "incoming_session_argument_used": True,
            "identifier_sensitive": True,
        },
        "client_model_difference": {
            "broader_device_info_payload_bytes": 64,
            "broader_device_info_slot_bytes": 32,
            "broader_device_serial_payload_bytes": 30,
            "this_production_image_uses_broader_shapes": False,
        },
        "complete_direct_branch_sets": {
            "bounded_formatter": [f"0x{value:08x}" for value in EXPECTED_FORMATTER_BRANCHES],
            "device_info_response": ["0x00083d8a"],
            "device_serial_getter": [
                f"0x{value:08x}" for value in EXPECTED_SERIAL_GETTER_BRANCHES
            ],
            "device_serial_generic_response": ["0x00083ddc"],
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "live_identity_access": False,
            "storage_access": False,
            "sensor_access": False,
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
