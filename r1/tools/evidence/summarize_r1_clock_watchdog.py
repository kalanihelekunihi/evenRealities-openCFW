#!/usr/bin/env python3
"""Reconstruct the production R1 system-RTC and hardware-watchdog devices.

The parser is static and read-only. It decompresses initialized RAM, validates exact firmware
signatures and reports state/configuration; it does not set time, feed a watchdog or contact a ring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import (
    DEFAULT_BASE,
    DEFAULT_SCATTER_LENGTH,
    DEFAULT_SCATTER_RUNTIME,
    DEFAULT_SCATTER_SOURCE,
    c_string,
    decompress_scatter,
    mapped_offset,
)


RTC_STATE = 0x2000737C
RTC_DESCRIPTOR = 0x20007384
RTC_RECORD_BYTES = 0x58
RTC_OPERATIONS = 0x200073DC
RTC_REGISTER = 0x000563C4
RTC_LOOKUP = 0x00050DC0
RTC_TICK_CALLBACK = 0x00056275
RTC_CONFIGURATION_SOURCE = 0x0009A638

WATCHDOG_DESCRIPTOR = 0x20007630
WATCHDOG_RECORD_BYTES = 0x2C
WATCHDOG_OPERATIONS = 0x2000765C
WATCHDOG_REGISTER = 0x00056694
WATCHDOG_LOOKUP = 0x000500D4
WATCHDOG_TIMEOUT_HANDLER = 0x00096A1F


def word(block: bytes, offset: int) -> int:
    return struct.unpack_from("<I", block, offset)[0]


def halfword(block: bytes, offset: int) -> int:
    return struct.unpack_from("<H", block, offset)[0]


def runtime_slice(runtime: bytes, runtime_base: int, address: int, length: int) -> bytes:
    offset = address - runtime_base
    if offset < 0 or offset + length > len(runtime):
        raise ValueError(f"runtime range 0x{address:08x}+0x{length:x} is outside scatter image")
    return runtime[offset:offset + length]


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def require_prefix(image: bytes, base: int, address: int, expected_hex: str) -> None:
    expected = bytes.fromhex(expected_hex)
    actual = flash_bytes(image, base, address, len(expected))
    if actual != expected:
        raise ValueError(
            f"unexpected bytes at 0x{address:08x}: {actual.hex()} != {expected.hex()}"
        )


def string_occurrence_count(image: bytes, value: str) -> int:
    needle = value.encode() + b"\x00"
    count = 0
    start = 0
    while True:
        offset = image.find(needle, start)
        if offset < 0:
            return count
        count += 1
        start = offset + 1


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)

    signatures = {
        RTC_REGISTER: "70b50b4d002405f1580600bf04eb4400",
        RTC_LOOKUP: "10b5044c2068002803d103a034f088ff",
        0x00056274: "70b5194c8cb0608807282ad36068401c",
        0x00056318: "7cb51d4d0646002404eb440000ebc400",
        0x0005639C: "72b108484168d16201eb41034088c3eb",
        0x000563F8: "2de9f041104f06460d46002404eb4400",
        0x00056444: "2de9f041134d16460746002404eb4400",
        0x0005649C: "2de9f0418cb00646150019d0dff85880",
        WATCHDOG_REGISTER: "04480168416100f12c01816114302ff0",
        WATCHDOG_LOOKUP: "10b5054c206818b904a035f0fffd2060",
        0x00056658: "70b50c4d287908b1002070bd094c0a49",
        0x00056638: "064810b5027912b119b1192010bd1320",
        0x00096A1E: "7047",
        0x0009230C: "062000f051f8002204210820ebf74cf8",
    }
    for address, prefix in signatures.items():
        require_prefix(image, base, address, prefix)

    rtc_state = runtime_slice(runtime, scatter_runtime, RTC_STATE, 8)
    if rtc_state != bytes(8):
        raise ValueError(f"unexpected initialized RTC state {rtc_state.hex()}")
    rtc = runtime_slice(runtime, scatter_runtime, RTC_DESCRIPTOR, RTC_RECORD_BYTES)
    if c_string(image, word(rtc, 0), base) != "sys rtc":
        raise ValueError("unexpected RTC descriptor name")
    if word(rtc, 0x34) != 0x40024000 or word(rtc, 0x38) != 0x00040024:
        raise ValueError("unexpected RTC2 instance descriptor")
    for offset in range(4, RTC_RECORD_BYTES):
        if offset not in range(0x34, 0x3C) and rtc[offset] != 0:
            raise ValueError(f"unexpected initialized RTC byte at +0x{offset:x}")
    rtc_ops = [
        word(runtime_slice(runtime, scatter_runtime, RTC_OPERATIONS, 0x24), offset)
        for offset in range(0, 0x24, 4)
    ]
    expected_rtc_ops = [
        0, 0, 0x00056319, 0, 0x0005639D, 0x0005649D, 0,
        0x000563F9, 0x00056445,
    ]
    if rtc_ops != expected_rtc_ops:
        raise ValueError(f"unexpected RTC operations {[hex(value) for value in rtc_ops]}")

    config_source = flash_bytes(image, base, RTC_CONFIGURATION_SOURCE, 8)
    if config_source != bytes.fromhex("0000064100000000"):
        raise ValueError(f"unexpected RTC configuration source {config_source.hex()}")

    watchdog = runtime_slice(
        runtime, scatter_runtime, WATCHDOG_DESCRIPTOR, WATCHDOG_RECORD_BYTES,
    )
    if c_string(image, word(watchdog, 0), base) != "watchdog":
        raise ValueError("unexpected watchdog descriptor name")
    if [word(watchdog, offset) for offset in (4, 8, 0x0C, 0x10, 0x14, 0x18)] != [
        0, 1, 10_000, 6, 0, 0,
    ]:
        raise ValueError("unexpected initialized watchdog record")
    if any(watchdog[offset] for offset in range(0x1C, WATCHDOG_RECORD_BYTES)):
        raise ValueError("unexpected nonzero watchdog record tail")
    watchdog_ops = [
        word(runtime_slice(runtime, scatter_runtime, WATCHDOG_OPERATIONS, 0x2C), offset)
        for offset in range(0, 0x2C, 4)
    ]
    if watchdog_ops != [
        0x00056659, 0, 0, 0, 0, 0, 0x00056639, 0, 0, 0, 0,
    ]:
        raise ValueError(f"unexpected watchdog operations {[hex(value) for value in watchdog_ops]}")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "scatter_output_bytes": len(runtime),
        "system_rtc": {
            "name": "sys rtc",
            "state_address": f"0x{RTC_STATE:08x}",
            "descriptor_address": f"0x{RTC_DESCRIPTOR:08x}",
            "record_bytes": RTC_RECORD_BYTES,
            "registration_function": f"0x{RTC_REGISTER:08x}",
            "lookup_function": f"0x{RTC_LOOKUP:08x}",
            "compiled_string_occurrences": string_occurrence_count(image, "sys rtc"),
            "peripheral": "RTC2",
            "peripheral_register_base": "0x40024000",
            "instance_descriptor_raw": "0x00040024",
            "prescaler": 4095,
            "input_frequency_hz": 32_768,
            "tick_frequency_hz": 8,
            "tick_period_milliseconds": 125,
            "interrupt_priority": 6,
            "remaining_configuration_byte_raw": 0x41,
            "initial_state": {
                "utc_offset_minutes": 0,
                "subsecond_tick": 0,
                "seconds": 0,
            },
            "tick_callback": f"0x{RTC_TICK_CALLBACK:08x}",
            "ticks_per_second": 8,
            "subsecond_counter_range": [0, 7],
            "read_composite_formula": "seconds * 1000 + subsecond_tick",
            "composite_is_true_milliseconds": False,
            "operations": {
                "address": f"0x{RTC_OPERATIONS:08x}",
                "open": "0x00056319",
                "read_time": "0x0005639d",
                "set_time": "0x0005649d",
                "read_calendar_block": "0x000563f9",
                "set_alarm_callback": "0x00056445",
            },
        },
        "hardware_watchdog": {
            "name": "watchdog",
            "descriptor_address": f"0x{WATCHDOG_DESCRIPTOR:08x}",
            "record_bytes": WATCHDOG_RECORD_BYTES,
            "registration_function": f"0x{WATCHDOG_REGISTER:08x}",
            "lookup_function": f"0x{WATCHDOG_LOOKUP:08x}",
            "compiled_string_occurrences": string_occurrence_count(image, "watchdog"),
            "behaviour_raw": 1,
            "behaviour": "run while CPU sleeps; pause while CPU is halted",
            "reload_value_milliseconds": 10_000,
            "interrupt_priority": 6,
            "allocated_reload_channel_count": 1,
            "timeout_handler": f"0x{WATCHDOG_TIMEOUT_HANDLER:08x}",
            "timeout_handler_returns_immediately": True,
            "main_event_loop_feed_function": "0x000500fc",
            "main_event_loop_function": "0x0009230c",
            "operations": {
                "address": f"0x{WATCHDOG_OPERATIONS:08x}",
                "open_start": "0x00056659",
                "feed_channel_zero_argument": "0x00056639",
            },
        },
        "safety": {
            "static_parser_only": True,
            "live_clock_or_watchdog_control": False,
            "watchdog_feed_sender_exposed": False,
        },
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    parser.add_argument("--scatter-source", type=parse_integer, default=DEFAULT_SCATTER_SOURCE)
    parser.add_argument("--scatter-runtime", type=parse_integer, default=DEFAULT_SCATTER_RUNTIME)
    parser.add_argument("--scatter-length", type=parse_integer, default=DEFAULT_SCATTER_LENGTH)
    arguments = parser.parse_args()
    print(json.dumps(summarize(
        arguments.image,
        arguments.base,
        arguments.scatter_source,
        arguments.scatter_runtime,
        arguments.scatter_length,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
