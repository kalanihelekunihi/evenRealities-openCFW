#!/usr/bin/env python3
"""Validate and summarize the R1 sensor-thread health startup policy.

This parser is static and read-only. It proves the one-shot private event and its mode selections,
but intentionally exposes no internal-event publisher or health-mode command encoder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset


FUNCTION_SIGNATURES = {
    0x00092580: "1fb50520fff716ff002210213220eaf711ff344e4ff00008",  # sensor task
    0x0004A21C: "10b502f0d1f9fff7d1f802f0c7f8002001f0b4fd",      # health services init
    0x00042840: "10b54af09dfd4bf015fd4bf087febde810404bf07ebe",  # event 0x0005
    0x0008D380: "10b504f0b3f8c00703d104f0aff84007",              # HR startup helper
    0x0008E274: "0120fcf702bb",                                  # SpO2 mode-1 helper
    0x0008E552: "0020fcf79fb9cdf7bcbb",                          # stress mode-0 helper
    0x0008E55C: "7047",                                          # temperature no-op
    0x0004B33C: "7047",                                          # temperature service init no-op
    0x0008A866: "01b59df80000042805d20122694641f2010003f0",      # HR mode wrapper
    0x0008A87E: "01b59df80000022805d20122694641f2030003f0",      # SpO2 mode wrapper
    0x0008A896: "01b59df80000022805d20122694641f2070003f0",      # stress mode wrapper
    0x000421C4: "10b5012923d1c4b24ff08ef9c00703d1",              # HR mode consumer
    0x00042244: "10b5012923d1c4b24ff04ef9c00703d1",              # SpO2 mode consumer
    0x000422C8: "10b5012923d1c4b24ff00cf9c00703d1",              # stress mode consumer
    0x00049838: "2de9f0410f46054637483849401ac008032101eb",      # HR transition
    0x0004AB40: "70b5044688421dd146f0d0fcc00703d146f0ccfc",      # SpO2 transition
    0x0004B348: "70b50e462849294a891ac908032202eb0144b042",      # stress transition
    0x00049E2C: "10b5094c206918b1fff7e4ff00f05cf800206070",      # HRV hourly callback
    0x00049F0C: "2de9f8435e4d07466878a97808437dd128780128",      # HRV window core
    0x0004AD40: "70b50a4c0025616819b109a03ef0dcfe656000f0",      # SpO2 hourly callback
    0x0004AD98: "002000f0b9b800002de9f04186b080460c4646f0",      # SpO2 catch-up thunk/core
    0x0004AF10: "2de9f84f5e4e07467078b178084373d130780128",      # SpO2 window core
}

CALLSITE_SIGNATURES = {
    # Initialize the services, create the named sensor scheduler with raw argument 10,000, and
    # publish no-payload sensor event 5 before entering the task loop.
    0x000925B0: "0520fff745ff42f210712ba0cbf7aafa351f0022286011460520fbf797f9",
    # Event 5 calls HR, SpO2, the temperature no-op, then tail-calls stress disable.
    0x00042840: "10b54af09dfd4bf015fd4bf087febde810404bf07ebe",
    # HR startup helper materializes mode 1 before its wrapper tail-call.
    0x0008D3BA: "bde810400120fdf751ba",
    # Both hourly/catch-up cores use a 3,600-second hour, 150-second cutoff, 30-second guard,
    # 120-second cap, and millisecond multiplier.
    0x00049F86: "40f0dbfe4ff46161b0fbf1f201fb1200c0f56160962873d91e38782801d204006ed0",
    0x0004AF8C: "3ff0d8fe4ff46161b0fbf1f201fb1200c0f56160962854d91e38782801d204004fd0",
}

CONSTANT_WORDS = {
    0x0004996C: 600_000,    # HR timing-mode interval
    0x00049B58: 120_000,    # health-enable timing window
    0x0004B42C: 3_600_000,  # alternate stress mode-1 interval; startup selects mode 0
}


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def flash_word(image: bytes, base: int, address: int) -> int:
    return struct.unpack("<I", flash_bytes(image, base, address, 4))[0]


def require_prefix(image: bytes, base: int, address: int, expected_hex: str) -> None:
    expected = bytes.fromhex(expected_hex)
    actual = flash_bytes(image, base, address, len(expected))
    if actual != expected:
        raise ValueError(
            f"unexpected bytes at 0x{address:08x}: {actual.hex()} != {expected.hex()}"
        )


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    for address, signature in FUNCTION_SIGNATURES.items():
        require_prefix(image, base, address, signature)
    for address, signature in CALLSITE_SIGNATURES.items():
        require_prefix(image, base, address, signature)
    for address, expected in CONSTANT_WORDS.items():
        actual = flash_word(image, base, address)
        if actual != expected:
            raise ValueError(
                f"unexpected constant at 0x{address:08x}: {actual} != {expected}"
            )

    selections = [
        {
            "metric": "heart_rate",
            "helper": "0x0008d380",
            "system_event": "0x1001",
            "mode_raw": 1,
            "mode_semantic": "timing",
            "accepted_mode_raw_values": [0, 1, 2, 3],
            "periodic_interval_ms": 600_000,
            "measurement_window_ms": None,
        },
        {
            "metric": "blood_oxygen",
            "helper": "0x0008e274",
            "system_event": "0x1003",
            "mode_raw": 1,
            "mode_semantic": "hour-boundary/catch-up timing",
            "accepted_mode_raw_values": [0, 1],
            "periodic_interval_ms": None,
            "measurement_window_ms": 120_000,
        },
        {
            "metric": "temperature",
            "helper": "0x0008e55c",
            "system_event": None,
            "mode_raw": None,
            "mode_semantic": "preserve current state through compiled no-op",
            "accepted_mode_raw_values": [],
            "periodic_interval_ms": None,
            "measurement_window_ms": None,
        },
        {
            "metric": "stress",
            "helper": "0x0008e552",
            "system_event": "0x1007",
            "mode_raw": 0,
            "mode_semantic": "disabled",
            "accepted_mode_raw_values": [0, 1],
            "periodic_interval_ms": None,
            "measurement_window_ms": None,
            "unselected_mode_1_periodic_interval_ms": 3_600_000,
        },
    ]

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "sensor_thread_startup": {
            "sensor_thread": "0x00092580",
            "health_service_initializer": "0x0004a21c",
            "sensor_scheduler_argument_raw": 10_000,
            "private_event": "0x0005",
            "private_event_consumer": "0x00042840",
            "private_event_payload_bytes": 0,
            "single_static_publish_call_before_event_loop": True,
            "selections_in_call_order": selections,
        },
        "hour_window_policy": {
            "hour_seconds": 3_600,
            "window_seconds": 120,
            "minimum_remaining_seconds_to_start": 151,
            "guard_before_next_hour_seconds": 30,
            "hourly_callbacks_are_health_wear_and_mode_gated": True,
            "startup_mode_selection_alone_guarantees_measurement": False,
        },
        "safety": {
            "static_parser_only": True,
            "public_ble_health_mode_command_proven": False,
            "private_event_sender_exposed": False,
            "health_mode_sender_exposed": False,
            "describes_power_sensitive_scheduling": True,
        },
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image, arguments.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
