#!/usr/bin/env python3
"""Pin exact production device-status and wear-status response/fan-out routes.

This analyzer reads only the supplied firmware image. It does not open BLE, access a ring,
sample sensors, read live SRAM/storage, or write health data.
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
        0x00083DE4,
        0x00083E26,
        "6b42d85067722733900c4ce417e54e0e5111eef9a9ac70b557bea652b2fff110",
        "requested deviceStatus handler",
    ),
    (
        0x0008345C,
        0x000834C8,
        "96b3089d1fe38dac1372b163039c2d90db54e69c049f23032917bb76017bbb4a",
        "unsolicited deviceStatus producer",
    ),
    (
        0x00083896,
        0x000838BA,
        "8e5145b9482eadf36edf4a6a99ac4143462abba7ff70adce381878233c6e2898",
        "fixed-seven-byte deviceStatus response wrapper",
    ),
    (
        0x00084B24,
        0x00084B9C,
        "e77330de5070ac1815e13ab6e8210f89f9627787316b12de9a7f3a5caa7d3969",
        "requested wearStatus handler",
    ),
    (
        0x00043788,
        0x000437F2,
        "985ff01b01f19cbd0e4d3e11dfda1c555fbc63391c6c499e4667012b6c85e82f",
        "unsolicited wearStatus producer",
    ),
    (
        0x00083C62,
        0x00083C86,
        "a2452f417276275f01e2f4ffe99487eaffec15e8f12a220bc23c02b4c9b673cc",
        "fixed-one-byte wearStatus response wrapper",
    ),
    (
        0x0004C5B8,
        0x0004C5C0,
        "1067a0bdcf3149a9042ab3fe414cc4ad4c999b48a760b1847b20abfdb05a99fa",
        "wear internal-state accessor",
    ),
    (
        0x0004C678,
        0x0004C6BC,
        "6780bbe91d384a39de17dccd23840eb2145d7492a7c6d782a1f42e0ab4809541",
        "wear glasses-relay fan-out",
    ),
    (
        0x00084C0C,
        0x00084C5E,
        "f09c7a17ed32f9f2cd8f37bf87275e3cd847f0ee6db38f82ecd9185d5d20a97a",
        "logical response-header builder",
    ),
]

DEVICE_STATUS_HANDLER = 0x00083DE4
DEVICE_STATUS_NOTIFICATION = 0x0008345C
DEVICE_STATUS_RESPONSE = 0x00083896
WEAR_STATUS_HANDLER = 0x00084B24
WEAR_STATUS_NOTIFICATION = 0x00043788
WEAR_STATUS_RESPONSE = 0x00083C62
WEAR_STATE_ACCESSOR = 0x0004C5B8
WEAR_GLASSES_RELAY = 0x0004C678
GLASSES_DISPATCH = 0x00034064
GENERIC_RESPONSE = 0x00084C0C

SYSTEM_TABLE = 0x0009A4CC
DEVICE_STATUS_REGISTRATION = bytes.fromhex("01000000e53d0800")
WEAR_STATUS_REGISTRATION = bytes.fromhex("03000000254b0800")
REQUESTED_DEVICE_STATUS_TEMPLATE = 0x0009A4C4
REQUESTED_DEVICE_STATUS_TEMPLATE_BYTES = bytes.fromhex("0002010000000000")
WEAR_STATE_RUNTIME_ADDRESS = 0x2001E454
WEAR_STATE_OFFSET = 0x24

EXPECTED_BRANCHES = {
    DEVICE_STATUS_RESPONSE: [0x000834C2, 0x00083E20],
    WEAR_STATUS_RESPONSE: [0x000437E8, 0x00084B96],
    WEAR_GLASSES_RELAY: [0x000437EC, 0x000453EA],
    WEAR_STATE_ACCESSOR: [
        0x00048EEA,
        0x0004907E,
        0x00049AEA,
        0x00049F42,
        0x0004A99C,
        0x0004AF46,
        0x0004BBF2,
        0x0004FA62,
        0x0006ACEC,
        0x00084B2C,
        0x00084B32,
    ],
    GLASSES_DISPATCH: [0x0003EBE0, 0x0004C6B6, 0x00091434],
}


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


def checked_bytes(
    image: bytes,
    base: int,
    address: int,
    expected: bytes,
    label: str,
) -> str:
    actual = flash_bytes(image, base, address, address + len(expected))
    if actual != expected:
        raise ValueError(
            f"unexpected {label} at 0x{address:08x}: "
            f"{actual.hex()} != {expected.hex()}"
        )
    return actual.hex()


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    verified = [
        checked_range(image, base, start, end, sha, label)
        for start, end, sha, label in RANGES
    ]
    branch_output: dict[str, list[str]] = {}
    for target, expected in EXPECTED_BRANCHES.items():
        actual = branch_addresses(image, base, target)
        if actual != expected:
            raise ValueError(
                f"unexpected complete branch set for 0x{target:08x}: {actual}"
            )
        branch_output[f"0x{target:08x}"] = [
            f"0x{address:08x}" for address in actual
        ]

    if direct_thumb_branches_to(image, base, DEVICE_STATUS_HANDLER):
        raise ValueError("table-dispatched deviceStatus handler acquired a direct branch")
    if direct_thumb_branches_to(image, base, WEAR_STATUS_HANDLER):
        raise ValueError("table-dispatched wearStatus handler acquired a direct branch")

    registrations = [
        {
            "address": f"0x{SYSTEM_TABLE:08x}",
            "system_subcommand": "0x01",
            "handler_thumb": "0x00083de5",
            "raw_hex": checked_bytes(
                image,
                base,
                SYSTEM_TABLE,
                DEVICE_STATUS_REGISTRATION,
                "deviceStatus registration",
            ),
        },
        {
            "address": f"0x{SYSTEM_TABLE + 0x10:08x}",
            "system_subcommand": "0x03",
            "handler_thumb": "0x00084b25",
            "raw_hex": checked_bytes(
                image,
                base,
                SYSTEM_TABLE + 0x10,
                WEAR_STATUS_REGISTRATION,
                "wearStatus registration",
            ),
        },
    ]
    template = checked_bytes(
        image,
        base,
        REQUESTED_DEVICE_STATUS_TEMPLATE,
        REQUESTED_DEVICE_STATUS_TEMPLATE_BYTES,
        "requested deviceStatus template",
    )
    if checked_bytes(
        image,
        base,
        0x000437F4,
        WEAR_STATE_RUNTIME_ADDRESS.to_bytes(4, "little"),
        "wear notification state literal",
    ) != "54e40120":
        raise AssertionError("unreachable")
    if checked_bytes(
        image,
        base,
        0x0004C6BC,
        WEAR_STATE_RUNTIME_ADDRESS.to_bytes(4, "little"),
        "wear relay state literal",
    ) != "54e40120":
        raise AssertionError("unreachable")

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": verified,
        "registrations": registrations,
        "complete_direct_branch_sets": branch_output,
        "device_status": {
            "requested_payload_bytes": 7,
            "requested_template_address": f"0x{REQUESTED_DEVICE_STATUS_TEMPLATE:08x}",
            "requested_template_hex": template,
            "requested_payload": [
                "normalized battery percentage",
                "3 full, else 1 charging, else 2 not charging",
                "0x01",
                "0x00",
                "0x00",
                "0x00",
                "0x00",
            ],
            "unsolicited_payload_bytes": 7,
            "unsolicited_payload": [
                "caller-supplied battery percentage",
                "1 charging or 2 not charging",
                "0x00",
                "0x00",
                "0x00",
                "0x00",
                "0x00",
            ],
            "requested_response_type": 3,
            "unsolicited_response_type": 2,
            "current_eus_session_used": True,
            "incoming_session_argument_used": False,
        },
        "wear_status": {
            "payload_bytes": 1,
            "internal_state_address": f"0x{WEAR_STATE_RUNTIME_ADDRESS:08x}",
            "internal_state_offset": WEAR_STATE_OFFSET,
            "requested_accessor_reads": (
                "one when first sample is 0; otherwise two independent samples"
            ),
            "requested_mapping": {
                "first sample 0": 1,
                "first nonzero and second sample 1": 2,
                "otherwise": 0,
            },
            "unsolicited_mapping": {
                "internal state 0": 1,
                "internal state nonzero": 2,
            },
            "requested_response_type": 3,
            "unsolicited_response_type": 2,
            "current_eus_session_used": True,
            "incoming_session_argument_used": False,
            "unsolicited_glasses_frame_hex_prefix": "00098c00",
            "unsolicited_glasses_frame_final_byte": (
                "0 for internal state 0; 1 for any nonzero state"
            ),
            "phone_response_precedes_glasses_dispatch": True,
            "glasses_dispatch_requires_valid_current_glasses_session": True,
        },
        "generic_response_header": {
            "bytes": [
                "(notification flag XOR 1) OR 2",
                "module 0x01",
                "command 0x00",
                "system subcommand",
                "serial UInt16LE",
                "status 0x00",
                "reserved 0x00",
            ],
            "invalid_current_session_sentinel": "0xffff",
            "invalid_session_suppresses_phone_response": True,
        },
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "live_sram_access": False,
            "storage_access": False,
            "sensor_access": False,
            "health_store_access": False,
            "executes_firmware": False,
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
