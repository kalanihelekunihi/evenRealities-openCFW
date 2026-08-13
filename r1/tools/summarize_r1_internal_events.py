#!/usr/bin/env python3
"""Validate and summarize every R1 sensor-task internal event dispatch slot.

This is a static, read-only application 2.2.6.0009 parser. Internal event identifiers are not BLE
commands; the report deliberately exposes no publisher, flash mutation, or captured health data.
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
    decompress_scatter,
    mapped_offset,
)


SENSOR_TABLE = 0x20006750
SYSTEM_TABLE = 0x20006E54
STORAGE_TABLE = 0x200066FC

HANDLER_SIGNATURES = {
    0x00042856: "002801d048f04fbc", 0x00042A20: "3eb5040045d00c29",
    0x000428B4: "38b5c4b24ef018fe", 0x00042840: "10b54af09dfd4bf0",
    0x00042896: "002803d0082901d1", 0x000428A4: "002803d0082901d1",
    0x0004296A: "002803d0082901d1", 0x00042A10: "002803d0082901d1",
    0x00042978: "10b5040024d00829", 0x00042788: "1fb5040031d00c29",
    0x00042964: "c0b24bf0f5bb0028", 0x00042960: "4bf016bac0b24bf0",
    0x0004286E: "002803d0082901d1", 0x00042860: "002803d0092901d1",
    0x0004287C: "10b5c4b20af096f9",
    0x00042118: "002801d048f0eebf", 0x000421C4: "10b5012923d1c4b2",
    0x00042128: "10b5012926d108b1", 0x00042244: "10b5012923d1c4b2",
    0x000423D8: "10b5012926d108b1", 0x00042350: "10b5012923d1c4b2",
    0x00042514: "10b5012926d108b1", 0x000422C8: "10b5012923d1c4b2",
    0x00042474: "10b5012926d108b1", 0x00042108: "06f0aebf012902d1",
    0x000425B0: "f0b587b00c297dd1", 0x0004210C: "012902d1c0b20af0",
    0x000421C0: "08f0fcb910b50129", 0x00042122: "c0b207f0eaba10b5",
    0x000423D4: "08f06eb810b50129",
    0x00042BC6: "4bf065b84bf009bb", 0x00042BCA: "4bf009bb00002de9",
    0x00042BC2: "4bf0e1b84bf065b8", 0x00042BB0: "10b54ef075fcbde8",
    0x00042B20: "38b504464ef0e2fc", 0x00042BBE: "39f0b5bc4bf0e1b8",
    0x0008D888: "70b58188c5688ab2", 0x0008D8FC: "2de9f04188460446",
}

SENSOR_EVENTS = (
    (0x0001, 0x00000000, "compiled null sensor slot", "none", None),
    (0x0002, 0x00042857, "sensor callback fan-out work item", "variable", None),
    (0x0003, 0x00042A21, "wall-clock and UTC-offset update", "fixed", 12),
    (0x0004, 0x000428B5, "hour-boundary aggregation", "fixed", 1),
    (0x0005, 0x00042841, "one-shot sensor-thread health-mode initialization", "none", None),
    (0x0006, 0x00042897, "heart-rate point publication", "fixed", 8),
    (0x0007, 0x000428A5, "heart-rate-variability point publication", "fixed", 8),
    (0x0008, 0x0004296B, "blood-oxygen point publication", "fixed", 8),
    (0x0009, 0x00042A11, "temperature point publication", "fixed", 8),
    (0x000A, 0x00042979, "stress point publication", "fixed", 8),
    (0x000B, 0x00042789, "activity delta publication", "fixed", 12),
    (0x000C, 0x00042965, "sleep-status publication", "fixed", 1),
    (0x000D, 0x00042961, "sleep-result validation and storage", "variable", None),
    (0x000E, 0x0004286F, "health-history query", "fixed", 8),
    (0x000F, 0x00042861, "unsafe synthetic daily-health injection", "fixed", 9),
    (0x0010, 0x0004287D, "testable-module state response", "fixed", 1),
)

SYSTEM_EVENTS = (
    (0x1000, 0x00042119, "system callback fan-out work item", "variable", None),
    (0x1001, 0x000421C5, "set heart-rate operating mode", "fixed", 1),
    (0x1002, 0x00042129, "heart-rate one-shot measurement control", "fixed", 1),
    (0x1003, 0x00042245, "set blood-oxygen operating mode", "fixed", 1),
    (0x1004, 0x000423D9, "blood-oxygen one-shot measurement control", "fixed", 1),
    (0x1005, 0x00042351, "set temperature operating mode", "fixed", 1),
    (0x1006, 0x00042515, "temperature one-shot measurement control", "fixed", 1),
    (0x1007, 0x000422C9, "set stress operating mode", "fixed", 1),
    (0x1008, 0x00042475, "stress one-shot measurement control", "fixed", 1),
    (0x1009, 0x00042109, "activity accumulator service", "none", None),
    (0x100A, 0x000425B1, "GoMore user-profile update", "fixed", 12),
    (0x100B, 0x0004210D, "charging-state input to wear and power policy", "fixed", 1),
    (0x100C, 0x000421C1, "sleep low-power finalization", "none", None),
    (0x100D, 0x00042123, "global health-enable update", "fixed", 1),
    (0x100E, 0x000423D5, "force-awake sleep finalization", "none", None),
)

STORAGE_EVENTS = (
    (0x2000, 0x00042BC7, "persist sleep session", "variable", None),
    (0x2001, 0x00042BCB, "commit sleep synchronized marker", "repeated_fixed", 12),
    (0x2002, 0x00042BC3, "erase sleep journal after CRC failure", "none", None),
    (0x2003, 0x00042BB1, "flush firmware-named EP queue", "none", None),
    (0x2004, 0x00042B21, "persist length-prefixed GoMore key", "fixed", 65),
    (0x2005, 0x00042BBF, "restore compiled NV defaults selected by MAC", "none", None),
    (0x2006, 0x00000000, "compiled null storage slot", "none", None),
)

REQUIRED_DIAGNOSTICS = (
    b"set hr mode: %d\0", b"set spo2 mode: %d\0", b"set temp mode: %d\0",
    b"set stress mode: %d\0", b"activity data:%d,%d,%d,%d,%d\0",
    b"service sleep status: %d\0", b"health_daily_test is NULL\0",
    b"health enable update: %d\0", b"algo sleep low power event\0",
    b"sleep storage iter crc error, offset: %08X\0",
)


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


def runtime_word(runtime: bytes, runtime_base: int, address: int) -> int:
    offset = address - runtime_base
    if offset < 0 or offset + 4 > len(runtime):
        raise ValueError(f"runtime word 0x{address:08x} is outside scatter image")
    return struct.unpack_from("<I", runtime, offset)[0]


def render_event(family: str, item: tuple[int, int, str, str, int | None]) -> dict[str, Any]:
    identifier, handler, semantic, cardinality, size = item
    return {
        "family": family,
        "identifier": f"0x{identifier:04x}",
        "handler_thumb": f"0x{handler:08x}",
        "registered": handler != 0,
        "semantic": semantic,
        "payload_cardinality": cardinality,
        "payload_or_item_bytes": size,
    }


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    for address, prefix in HANDLER_SIGNATURES.items():
        require_prefix(image, base, address, prefix)
    for diagnostic in REQUIRED_DIAGNOSTICS:
        if diagnostic not in image:
            raise ValueError(f"missing expected diagnostic {diagnostic[:-1]!r}")

    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)
    sensor_words = [
        runtime_word(runtime, scatter_runtime, SENSOR_TABLE + index * 4)
        for index in range(len(SENSOR_EVENTS))
    ]
    system_sentinel = runtime_word(runtime, scatter_runtime, SYSTEM_TABLE)
    system_words = [
        runtime_word(runtime, scatter_runtime, SYSTEM_TABLE + 4 + index * 4)
        for index in range(len(SYSTEM_EVENTS))
    ]
    storage_sentinel = runtime_word(runtime, scatter_runtime, STORAGE_TABLE)
    storage_words = [
        runtime_word(runtime, scatter_runtime, STORAGE_TABLE + 4 + index * 4)
        for index in range(len(STORAGE_EVENTS))
    ]
    if sensor_words != [item[1] for item in SENSOR_EVENTS]:
        raise ValueError("unexpected sensor event dispatch table")
    if system_sentinel != 0 or system_words != [item[1] for item in SYSTEM_EVENTS]:
        raise ValueError("unexpected system event dispatch table")
    if storage_sentinel != 0 or storage_words != [item[1] for item in STORAGE_EVENTS]:
        raise ValueError("unexpected storage event dispatch table")

    events = (
        [render_event("sensor", item) for item in SENSOR_EVENTS]
        + [render_event("system", item) for item in SYSTEM_EVENTS]
        + [render_event("storage", item) for item in STORAGE_EVENTS]
    )
    identifiers = [item["identifier"] for item in events]
    if len(events) != 38 or len(set(identifiers)) != 38:
        raise ValueError("internal event inventory is incomplete or contains duplicate IDs")
    if sum(item["registered"] for item in events) != 36:
        raise ValueError("unexpected populated internal event count")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "dispatcher": "0x0008d888",
        "publisher": "0x0008d8fc",
        "slot_count": len(events),
        "populated_slot_count": sum(item["registered"] for item in events),
        "null_slots": ["0x0001", "0x2006"],
        "leading_null_sentinels": {"system": True, "storage": True},
        "events": events,
        "negative_findings": {
            "event_id_above_sensor_0x0010": False,
            "event_id_above_system_0x100e": False,
            "event_id_above_storage_0x2006": False,
            "additional_internal_sensor_type_in_dispatch_tables": False,
        },
        "safety": {
            "static_parser_only": True,
            "captured_payloads_emitted": False,
            "identifiers_are_ble_commands": False,
            "live_internal_event_publisher_exposed": False,
            "destructive_sleep_crc_event_exposed": False,
            "persistent_storage_event_injection_exposed": False,
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
    print(json.dumps(
        summarize(
            arguments.image,
            arguments.base,
            arguments.scatter_source,
            arguments.scatter_runtime,
            arguments.scatter_length,
        ),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
