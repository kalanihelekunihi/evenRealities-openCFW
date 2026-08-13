#!/usr/bin/env python3
"""Validate and summarize the R1 clock-change and health-rollover pipeline.

This is a static, read-only parser for application 2.2.6.0009. It reports impact thresholds and
private callback topology but exposes no internal-event publisher, database formatter, or captured
health/timestamp payload.
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
    0x000846DC: "70b50d46064686b000213548e1f73cfb",  # public system-time handler
    0x00042A20: "3eb5040045d00c2943d16188a06848f0",  # event 0x0003 consumer
    0x0008ADC0: "3eb5214ca17a09b101203ebd20b1d0e9",  # time-manager initialization
    0x0008AEB0: "2de9f047204d824686b0a87a0c460028",  # clock/timezone setter
    0x0005A9D0: "01b530f0e7f905494968884204d00122",  # provider hour callback
    0x000428B4: "38b5c4b24ef018fec00703d14ef014fe",  # event 0x0004 consumer
    0x0008AF8C: "2de9f047164688460746052802d30020",  # callback registration
    0x0008B028: "2de9f74f314d0446174655f824000028",  # callback fan-out
    0x00070030: "2de9f0410021824a88b0084602eb0013",  # health.db init/registration
    0x0005DCE8: "2de9f04f87b0c4b233f0fcfbc0074ff0",  # hourly append
    0x0005E698: "2de9f04f87b006007ed0ad48ad4a0221",  # health.db time subscriber
    0x0005DC08: "10b5002826d081684068814222d2401a",  # GoMore time subscriber
    0x0004B698: "10b5064a0649144604203ff073fc",      # temp registry slots 4 and 3
    0x0004BAD0: "f8b5067845f00afd",                  # temperature sleep-status subscriber
    0x0004BD60: "70b5007801280fd00024",              # temperature wear-state subscriber
    0x000491B8: "7047",                              # activity no-op wear subscriber
    0x00049D28: "70b5047847f0defbc00703d1",          # heart-rate wear subscriber
    0x00049E2C: "10b5094c206918b1fff7e4ff",          # HRV hourly subscriber
    0x0004AA64: "10b50078002811d109480178",          # sleep wear subscriber
    0x0004B2FC: "70b50078012813d000240a4d",          # SpO2 wear subscriber
    0x0004AD40: "70b50a4c0025616819b109a0",          # SpO2 hourly subscriber
    0x00043788: "08b500200090194890f82400",          # protocol wear-status report
    0x0003D1B8: "10b50078144c012803d16178",          # wear-classifier sleep subscriber
}

POINTER_WORDS = {
    0x0008AE50: 0x0005A9D1,  # time provider -> hour callback
    0x00048E64: 0x000491B9,  # slot 4 -> activity no-op
    0x000497C4: 0x00049D29,  # slot 4 -> heart-rate wear policy
    0x000497C8: 0x00049E2D,  # slot 1 -> HRV hourly scheduler
    0x0004A5B8: 0x0004AA65,  # slot 4 -> sleep wear finalizer
    0x0004AAF0: 0x0004B2FD,  # slot 4 -> SpO2 wear cancellation
    0x0004AAF4: 0x0004AD41,  # slot 1 -> SpO2 hourly scheduler
    0x0004B6B8: 0x0004BD61,  # slot 4 -> temperature wear subscriber
    0x0004B6BC: 0x0004BAD1,  # slot 3 -> temperature sleep subscriber
    0x0004C314: 0x0005DC09,  # slot 0 -> GoMore time subscriber
    0x0004C62C: 0x00043789,  # slot 4 -> protocol wear-status report
    0x0004C630: 0x0003D1B9,  # slot 3 -> wear-classifier sleep subscriber
    0x00070330: 0x0005DCE9,  # registry slot 1 -> health hourly writer
    0x00070334: 0x0005E699,  # registry slot 0 -> health time subscriber
}

REGISTRATION_CALLSITE_SIGNATURES = {
    0x00048DF8: "42f0c8b8", 0x000497AE: "41f0edfb", 0x000497BC: "41f0e6bb",
    0x0004A5B0: "40f0ecbc", 0x0004AADA: "40f057fa", 0x0004AAE8: "40f050ba",
    0x0004B6A2: "3ff073fc", 0x0004B6B0: "3ff06cbc", 0x0004C05C: "3ef096ff",
    0x0004C5F4: "3ef0cafc", 0x0004C5FE: "3ef0c5fc", 0x0007010A: "1af03fff",
    0x00070114: "1af03aff",
}

CONSTANT_WORDS = {
    0x0005EA0C: 946_080_000,  # 1999-12-25T00:00:00Z
    0x0005EAC4: 86_400,
}

REQUIRED_DIAGNOSTICS = (
    b"[RING]update ts: %d, tz: %d, old_ts: %d, old_tz: %d\0",
    b"[RING]one the hour:%d, ts:%d\0",
    b"[RING]gm ts change, reinit algorithm\0",
    b"[RING]flashdb ts change, reinit flashdb\0",
    b"[RING]db_storage cross day, clean all data, zero_ts:%d,%d\0",
    b"[RING]update_time: clamp future sync ts to %u\0",
    b"[RING]db_storage append hour:%d\0",
)


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
    for address, prefix in FUNCTION_SIGNATURES.items():
        require_prefix(image, base, address, prefix)
    for address, expected in POINTER_WORDS.items():
        actual = flash_word(image, base, address)
        if actual != expected:
            raise ValueError(
                f"unexpected pointer at 0x{address:08x}: 0x{actual:08x} != 0x{expected:08x}"
            )
    for address, signature in REGISTRATION_CALLSITE_SIGNATURES.items():
        require_prefix(image, base, address, signature)
    for address, expected in CONSTANT_WORDS.items():
        actual = flash_word(image, base, address)
        if actual != expected:
            raise ValueError(
                f"unexpected constant at 0x{address:08x}: {actual} != {expected}"
            )
    for diagnostic in REQUIRED_DIAGNOSTICS:
        if diagnostic not in image:
            raise ValueError(f"missing expected diagnostic {diagnostic[:-1]!r}")

    callback_slots = [
        {
            "slot": 0,
            "semantic": "material wall-clock/timezone transition",
            "callbacks_thumb": ["0x0005e699", "0x0005dc09"],
        },
        {
            "slot": 1,
            "semantic": "local hour boundary",
            "callbacks_thumb": ["0x00049e2d", "0x0004ad41", "0x0005dce9"],
        },
        {
            "slot": 2,
            "semantic": "midnight follow-up fan-out",
            "callbacks_thumb": [],
        },
        {
            "slot": 3,
            "semantic": "sleep-status policy fan-out",
            "callbacks_thumb": ["0x0004bad1", "0x0003d1b9"],
        },
        {
            "slot": 4,
            "semantic": "wear-status policy and protocol fan-out",
            "callbacks_thumb": [
                "0x000491b9", "0x00049d29", "0x0004aa65", "0x0004b2fd",
                "0x0004bd61", "0x00043789",
            ],
        },
    ]
    if sum(len(slot["callbacks_thumb"]) for slot in callback_slots) != 13:
        raise ValueError("unexpected callback registration count")
    if sum(bool(slot["callbacks_thumb"]) for slot in callback_slots) != 4:
        raise ValueError("unexpected populated callback slot count")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "system_time_transition": {
            "public_handler": "0x000846dc",
            "internal_event": "0x0003",
            "consumer": "0x00042a20",
            "private_record_bytes": 12,
            "private_record_layout": [
                "old signed timezone minutes Int16LE @0",
                "new signed timezone minutes Int16LE @2",
                "old Unix seconds UInt32LE @4",
                "new Unix seconds UInt32LE @8",
            ],
            "clock_update_attempted_before_fanout_filter": True,
            "fanout_if_timezone_changed": True,
            "fanout_minimum_absolute_delta_seconds": 31,
            "gomore_reinitialize_on_backward_delta_seconds": 180,
            "health_db_format_on_backward_delta_seconds": 3600,
            "health_db_format_resets_known_hsync_offsets": [0, 4, 12, 16],
            "health_db_format_preserves_unresolved_hsync_offsets": [8, 20],
            "validity_floor_unix_seconds": 946_080_000,
            "validity_floor_utc": "1999-12-25T00:00:00Z",
            "local_day_divisor_seconds": 86_400,
            "cross_day_uses_each_side_timezone": True,
            "future_cursor_clamp_uses_new_timestamp": True,
        },
        "hour_boundary": {
            "provider_callback": "0x0005a9d0",
            "internal_event": "0x0004",
            "consumer": "0x000428b4",
            "private_record_bytes": 1,
            "health_db_subscriber": "0x0005dce8",
            "hrv_scheduler_subscriber": "0x00049e2c",
            "spo2_scheduler_subscriber": "0x0004ad40",
            "registered_subscriber_count": 3,
            "hrv_and_spo2_windows_are_gate_dependent": True,
            "accepted_current_hour_range": [0, 23],
            "appended_hour_expression": "current hour 0 -> 23, otherwise current hour - 1",
            "midnight_clears_six_daily_aggregate_caches": True,
            "provider_suppresses_initial_timestamp_callback": True,
            "midnight_slot_2_fanout_attempted": True,
            "midnight_slot_2_registered_subscribers": 0,
        },
        "callback_registry": {
            "registration_function": "0x0008af8c",
            "fanout_function": "0x0008b028",
            "slot_count": 5,
            "populated_slot_count": 4,
            "registered_callback_count": 13,
            "registration_callsite_count": len(REGISTRATION_CALLSITE_SIGNATURES),
            "slots": callback_slots,
        },
        "safety": {
            "static_parser_only": True,
            "captured_timestamps_emitted": False,
            "captured_health_values_emitted": False,
            "public_authenticated_system_time_path_already_supported": True,
            "private_transition_event_sender_exposed": False,
            "private_hour_event_sender_exposed": False,
            "health_db_format_sender_exposed": False,
            "impact_prediction_is_non_mutating": True,
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
