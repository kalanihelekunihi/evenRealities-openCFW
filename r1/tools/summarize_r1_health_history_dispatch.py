#!/usr/bin/env python3
"""Validate the R1 health-history dispatcher, descriptor roles, and event-14 residue.

This is a static, read-only parser for production application 2.2.6.0009. It proves that the
fourth word copied into accepted event-14 records is the health registration table binary-search
lower bound left in r3, not caller context, and inventories the common cache callbacks without
connecting to a ring or publishing an internal event.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset


IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
DISPATCHER_ADDRESS = 0x0008_2BE8
LOOKUP_ADDRESS = 0x0008_3298
REGISTRATION_TABLE_ADDRESS = 0x0009_A454
REGISTRATION_COUNT = 14
DESCRIPTOR_TABLE_ADDRESS = 0x0009_9BF4
DESCRIPTOR_COUNT = 6
EVENT_CONSUMER_ADDRESS = 0x0008_B8E8

EXACT_RANGES = (
    (
        "health_dispatcher",
        0x0008_2BE8,
        0x0008_2C0C,
        "ff5e7848057eb0dea0cb0c7ab34611f8078e872058ed98ec2caed34c464c41c3",
    ),
    (
        "registration_binary_search",
        0x0008_3298,
        0x0008_32D2,
        "08f095baacd3db6d15b3ba898b9bea78e5e88201eda5f4e5f3a6aeba34892313",
    ),
    (
        "activity_point",
        0x0008_2C10,
        0x0008_2C44,
        "38b7a30aaa28b66ced1d8db8098441027418b61c60a271b7d735b3061588bed3",
    ),
    (
        "activity_daily",
        0x0008_2C44,
        0x0008_2C8A,
        "5e2461720215c94cc77eed9e32ff388a9cce6995c3682fd0999e68c7717c1187",
    ),
    (
        "heart_rate_daily",
        0x0008_2C8A,
        0x0008_2CCE,
        "0d894dafa96718a3638b86f859c7f78749e510b9a65363804f00773e195a1b61",
    ),
    (
        "heart_rate_variability_daily",
        0x0008_2CCE,
        0x0008_2D14,
        "e16ef0a20149f768089960c93ccce019a0389e3d40c936a15cb8c0946e91dde6",
    ),
    (
        "sleep_daily",
        0x0008_2D14,
        0x0008_2D5A,
        "469a8cab4688bd659871bbeda25950bc45453c4a8327d6367cfa5f56b02f1e43",
    ),
    (
        "blood_oxygen_daily",
        0x0008_2D5A,
        0x0008_2D9E,
        "9f70c796bdc8f65813c32e84196afdad27e2db4fec870653315ccb63ad40a941",
    ),
    (
        "heart_rate_point",
        0x0008_2E34,
        0x0008_2E66,
        "32ed4a2778d06affc3ebd1c2bf348c2fb3739a2d407fd2014e1375bf460228cc",
    ),
    (
        "heart_rate_variability_point",
        0x0008_2E66,
        0x0008_2E9A,
        "0315d7ca6369eb120efd44ec981a4291a073f30b1a7ad7a3124aa6717bdf2bae",
    ),
    (
        "blood_oxygen_point",
        0x0008_2E9A,
        0x0008_2ECE,
        "0c84ec05328aa8a87b8132094fa6dfa5cf8dc6fb5d80e9445c9bf293196416cc",
    ),
    (
        "event_14_consumer",
        0x0008_B8E8,
        0x0008_BA80,
        "2cc0295c20559ba8ea45db9c9a344edbb245d065daf4fa92871a7642c94329a4",
    ),
)

EXPECTED_REGISTRATIONS = (
    (0x0101, 0x0008_2C8B, "heart_rate_daily", True),
    (0x0102, 0x0008_2E35, "heart_rate_point", True),
    (0x0103, 0x0008_2DBF, "heart_rate_other", False),
    (0x0201, 0x0008_2D5B, "blood_oxygen_daily", True),
    (0x0202, 0x0008_2E9B, "blood_oxygen_point", True),
    (0x0203, 0x0008_2DFB, "blood_oxygen_other", False),
    (0x0401, 0x0008_2CCF, "heart_rate_variability_daily", True),
    (0x0402, 0x0008_2E67, "heart_rate_variability_point", True),
    (0x0403, 0x0008_2DF9, "heart_rate_variability_other", False),
    (0x0501, 0x0008_2C45, "activity_daily", True),
    (0x0502, 0x0008_2C11, "activity_refresh", True),
    (0x0601, 0x0008_2D15, "sleep_daily", True),
    (0x0602, 0x0008_2D9F, "sleep_other", False),
    (0x7F01, 0x0008_2ECF, "testable_health", False),
)

EXPECTED_DESCRIPTORS = (
    (0, 3, 0x0007_0649, 0x0007_06A5, 0x0007_062D, "heart_rate"),
    (1, 3, 0x0009_0DF1, 0x0009_0E4D, 0x0009_0DD5, "blood_oxygen"),
    (2, 3, 0x0009_1919, 0x0009_1955, 0x0009_18DF, "temperature"),
    (3, 3, 0x0009_113F, 0x0009_1159, 0x0009_1125, "stress"),
    (4, 24, 0x0004_82A9, 0x0004_832D, 0x0004_8289, "activity"),
    (5, 6, 0x0007_06D9, 0x0007_073D, 0x0007_06BF, "heart_rate_variability"),
)

EXPECTED_RESIDUES = (0, 1, 0, 3, 3, 5, 0, 7, 7, 9, 7, 11, 11, 13)
DESCRIPTOR_TABLE_SHA256 = (
    "c0e60ff170a1abd778c59369db220f8cecb7cca1c03cb8b916546ac07e9d419c"
)


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def registration_search_residue(
    records: tuple[tuple[int, int, str, bool], ...],
    key: int,
) -> int | None:
    """Mirror 0x83298: return r3 (the current lower bound) on an exact match."""
    lower = 0
    upper = len(records) - 1
    while lower <= upper:
        middle = (lower + upper) // 2
        candidate = records[middle][0]
        if candidate == key:
            return lower
        if candidate < key:
            lower = middle + 1
        else:
            upper = middle - 1
    return None


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected application SHA-256: {digest}")

    verified_ranges: list[dict[str, Any]] = []
    for name, start, end, expected_hash in EXACT_RANGES:
        actual_hash = hashlib.sha256(flash_bytes(image, base, start, end - start)).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"{name} hash changed: {actual_hash}")
        verified_ranges.append({
            "name": name,
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual_hash,
        })

    registration_bytes = flash_bytes(
        image, base, REGISTRATION_TABLE_ADDRESS, REGISTRATION_COUNT * 8
    )
    parsed_registrations = tuple(
        (
            struct.unpack_from("<H", registration_bytes, index * 8)[0],
            struct.unpack_from("<I", registration_bytes, index * 8 + 4)[0],
        )
        for index in range(REGISTRATION_COUNT)
    )
    if parsed_registrations != tuple(
        (item[0], item[1]) for item in EXPECTED_REGISTRATIONS
    ):
        raise ValueError("health registration table changed")

    residues = tuple(
        registration_search_residue(EXPECTED_REGISTRATIONS, item[0])
        for item in EXPECTED_REGISTRATIONS
    )
    if residues != EXPECTED_RESIDUES:
        raise ValueError(f"registration search residues changed: {residues}")

    descriptor_bytes = flash_bytes(
        image, base, DESCRIPTOR_TABLE_ADDRESS, DESCRIPTOR_COUNT * 16
    )
    descriptor_hash = hashlib.sha256(descriptor_bytes).hexdigest()
    if descriptor_hash != DESCRIPTOR_TABLE_SHA256:
        raise ValueError(f"health descriptor table hash changed: {descriptor_hash}")
    parsed_descriptors = tuple(
        struct.unpack_from("<BBHIII", descriptor_bytes, index * 16)
        for index in range(DESCRIPTOR_COUNT)
    )
    expected_descriptor_words = tuple(
        (metric, length, 0, read_callback, write_callback, init_callback)
        for metric, length, read_callback, write_callback, init_callback, _ in (
            EXPECTED_DESCRIPTORS
        )
    )
    if parsed_descriptors != expected_descriptor_words:
        raise ValueError("health descriptor table changed")

    registrations = []
    for item, residue in zip(EXPECTED_REGISTRATIONS, residues):
        packed, handler, semantic, publishes_event_14 = item
        registrations.append({
            "packed_command_identifier": f"0x{packed:04x}",
            "handler_thumb": f"0x{handler:08x}",
            "semantic": semantic,
            "publishes_event_14": publishes_event_14,
            "dispatcher_lower_bound_residue_raw": residue,
        })

    descriptors = []
    for metric, length, read_callback, write_callback, init_callback, semantic in (
        EXPECTED_DESCRIPTORS
    ):
        descriptors.append({
            "metric_raw": metric,
            "metric": semantic,
            "serialized_field_length": length,
            "reserved_raw": 0,
            "slot_read_callback_thumb": f"0x{read_callback:08x}",
            "slot_write_callback_thumb": f"0x{write_callback:08x}",
            "cache_initialize_callback_thumb": f"0x{init_callback:08x}",
        })

    return {
        "analysis": "R1 health-history dispatcher and common-cache descriptors",
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "dispatcher": f"0x{DISPATCHER_ADDRESS:08x}",
        "registration_binary_search": f"0x{LOOKUP_ADDRESS:08x}",
        "registration_table": f"0x{REGISTRATION_TABLE_ADDRESS:08x}",
        "registration_count": len(registrations),
        "event_14_consumer": f"0x{EVENT_CONSUMER_ADDRESS:08x}",
        "event_14_consumer_read_offsets": [0, 1, 2],
        "event_14_consumer_reads_dispatcher_residue_word": False,
        "event_14_record_layout": [
            "metric_raw:UInt8",
            "query_kind_raw:UInt8",
            "request_serial:UInt16LE",
            "dispatcher_lower_bound_residue_raw:UInt32LE",
        ],
        "registrations": registrations,
        "descriptor_table": f"0x{DESCRIPTOR_TABLE_ADDRESS:08x}",
        "descriptor_table_sha256": descriptor_hash,
        "descriptor_callback_order": [
            "slot_read_or_fallback",
            "slot_write",
            "cache_initialize_or_reset",
        ],
        "descriptors": descriptors,
        "verified_ranges": verified_ranges,
        "negative_findings": {
            "event_14_fourth_word_is_caller_context": False,
            "event_14_consumer_uses_fourth_word": False,
            "temperature_event_14_registration": False,
            "stress_event_14_registration": False,
        },
        "safety": {
            "static_firmware_read_only": True,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "internal_event_publication": False,
            "flash_mutation": False,
            "captured_health_data_read": False,
        },
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    arguments = parser.parse_args()
    print(json.dumps(
        summarize(arguments.image, arguments.base),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
