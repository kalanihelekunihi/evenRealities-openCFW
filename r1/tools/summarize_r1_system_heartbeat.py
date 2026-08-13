#!/usr/bin/env python3
"""Pin the production R1 system 0x7f heartbeat handler and its no-op callback.

This analyzer reads only the supplied image. It never executes firmware, opens BLE, contacts a
physical device, accesses sensors, or mutates a firmware event queue.
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


HANDLER_START = 0x00084130
HANDLER_END = 0x0008414C
HANDLER_SHA256 = "52ea047bdfeccc353015e3618e131cad41ca59b3fefddd16aa55a143a1523f16"
CALLBACK_START = 0x0004D2F0
CALLBACK_END = 0x0004D2F2
CALLBACK_SHA256 = "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"
SYSTEM_TABLE_START = 0x0009A4CC
SYSTEM_TABLE_END = 0x0009A56C
SYSTEM_TABLE_SHA256 = "57bebd7948fd9cddfdfc4e8069492fc7b2088204d77e143e61d2f727b414ec50"
REGISTRATION_ADDRESS = 0x0009A554
REGISTRATION_BYTES = bytes.fromhex("7f00000031410800")
CALLBACK_THUMB = 0x0004D2F1
CANCEL_DELAYED = 0x00065D64
SCHEDULE_DELAYED = 0x00065B4C
DELAY_MILLISECONDS = 0x7800
RESPONSE_HELPERS = [0x00082844, 0x0008287C, 0x00084C5E]


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


def handler_branches(image: bytes, base: int, target: int) -> list[int]:
    return [
        address
        for address, _ in direct_thumb_branches_to(image, base, target)
        if HANDLER_START <= address < HANDLER_END
    ]


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")
    ranges = [
        checked_range(image, base, HANDLER_START, HANDLER_END, HANDLER_SHA256),
        checked_range(image, base, CALLBACK_START, CALLBACK_END, CALLBACK_SHA256),
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
        raise ValueError(f"unexpected system 0x7f registration: {registration.hex()}")
    if handler_branches(image, base, CANCEL_DELAYED) != [0x00084138]:
        raise ValueError("unexpected heartbeat delayed-cancel call")
    if handler_branches(image, base, SCHEDULE_DELAYED) != [0x00084148]:
        raise ValueError("unexpected heartbeat delayed-schedule tail call")
    response_calls = {
        target: handler_branches(image, base, target)
        for target in RESPONSE_HELPERS
    }
    if any(response_calls.values()):
        raise ValueError(f"heartbeat acquired a protocol response call: {response_calls}")
    if direct_thumb_branches_to(image, base, HANDLER_START):
        raise ValueError("table-dispatched heartbeat handler acquired a direct branch")
    callback = flash_bytes(image, base, CALLBACK_START, CALLBACK_END)
    if callback != bytes.fromhex("7047"):
        raise ValueError(f"heartbeat callback is no longer bx lr: {callback.hex()}")

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "registration": {
            "address": f"0x{REGISTRATION_ADDRESS:08x}",
            "system_subcommand": "0x7f",
            "handler_thumb": "0x00084131",
            "raw_hex": registration.hex(),
        },
        "handler": {
            "request_fields_read": [],
            "request_pointer_read": False,
            "request_serial_read": False,
            "request_flags_read": False,
            "protocol_response_emitted": False,
            "cancel": {
                "helper": f"0x{CANCEL_DELAYED:08x}",
                "callback_thumb": f"0x{CALLBACK_THUMB:08x}",
                "context_filter_raw": 0,
                "meaning": "cancel every pending instance of this callback",
            },
            "schedule": {
                "helper": f"0x{SCHEDULE_DELAYED:08x}",
                "callback_thumb": f"0x{CALLBACK_THUMB:08x}",
                "context": "incoming transport/session argument",
                "delay_raw": f"0x{DELAY_MILLISECONDS:04x}",
                "delay_milliseconds": DELAY_MILLISECONDS,
            },
        },
        "callback": {
            "address": f"0x{CALLBACK_START:08x}",
            "instruction": "bx lr",
            "reads_context": False,
            "effects": 0,
        },
        "interpretation": {
            "registered": True,
            "useful_protocol_operation": False,
            "connection_liveness_signal": False,
            "reason": "no immediate response and delayed callback is an exact no-op",
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "event_queue_mutation": False,
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
