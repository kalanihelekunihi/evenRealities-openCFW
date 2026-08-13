#!/usr/bin/env python3
"""Validate the exact R1 HRV point-consumer, hourly-cache and latest-point boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


EXPECTED_RANGES = {
    (0x0005AF18, 0x0005AF1C):
        "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587",
    (0x0005AF20, 0x0005AF40):
        "c45cfd732074c8b89858df45fd3977789e8b48463c2840592abab2a54cb40ada",
    (0x0005AF44, 0x0005AF5A):
        "c5807aa54a723e84fbe3de5f99da9189c9f8f18c1c6af402e11f894f07e953b8",
    (0x0005AF60, 0x0005B042):
        "a3d50af5019c9c9df523d85e7394655468a7df18300610fcdabea0f315549406",
    (0x0005ABA0, 0x0005AC38):
        "54736b7b56bde2c42c36c445bb119027c03a652f8416fc604ca82f1653cc6848",
    (0x0005ACA6, 0x0005ACC4):
        "db2097db7d8c2d10a00813bc7a975efb3d86cc2c3015450f731f54e5adec3c02",
    (0x0008A83E, 0x0008A866):
        "b903e154e0ef21e0da70d41b28519db011fbaefa66f2188f703d37bcb02b1a33",
    (0x000706BE, 0x000706D8):
        "f4a86ec4286f18f864911061109b87063d94a31cd197c6abbfb756013734fbae",
    (0x000706D8, 0x00070736):
        "5241cad16c7e682056e5b6f25f103ad0c3d1b88af8ab97913360dfe0b6e76055",
    (0x0007073C, 0x00070758):
        "9dd7974520aa2ac186932885a80a7fdc9351078836a7e01a4f683aaea6a1f5b4",
}

EXPECTED_BRANCHES = {
    0x0005AF18: [
        0x0003F50A, 0x00040E3C, 0x000410DC, 0x0005A0D2,
        0x000706C4, 0x000706DE, 0x00070742, 0x0008B272,
    ],
    0x0005AF20: [0x0008D86E],
    0x0005AF44: [0x0008D884],
    0x0005AF60: [0x0008A85A],
    0x0005ABA0: [
        0x0005ADA8, 0x0005AF78, 0x0005BB44, 0x0005BD04, 0x0005BE94,
    ],
    0x0005ACA6: [
        0x0005ABEC, 0x0005AD9A, 0x0005AF6A, 0x0005BB36,
        0x0005BCF6, 0x0005BE86, 0x000881A4,
    ],
    0x0008A83E: [0x000428AC],
    0x0008B138: [
        0x0008A804, 0x0008A838, 0x0008A860, 0x0008A8D2, 0x0008DCBC,
    ],
}

EXPECTED_LITERALS = {
    0x0005AF1C: 0x200169C0,
    0x0005AF40: 0x200169C0,
    0x0005AF5C: 0x200169C0,
    0x0005B044: 0x200169C0,
    0x0005AC70: 0x20016648,
    0x00070738: 0x38640900,
}

HRV_DESCRIPTOR_ADDRESS = 0x00099C44
EXPECTED_HRV_DESCRIPTOR = bytes.fromhex(
    "05060000d90607003d070700bf060700"
)


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + end - start]


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    ranges = []
    for (start, end), expected in EXPECTED_RANGES.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != expected:
            raise ValueError(f"unexpected range 0x{start:08x}...0x{end:08x}: {actual}")
        ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual,
        })

    branches: dict[str, list[str]] = {}
    for target, expected in EXPECTED_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected:
            raise ValueError(f"unexpected branches to 0x{target:08x}: {actual}")
        branches[f"0x{target:08x}"] = [f"0x{address:08x}" for address in actual]

    literals: dict[str, str] = {}
    for address, expected in EXPECTED_LITERALS.items():
        actual = struct.unpack("<I", flash_bytes(image, base, address, address + 4))[0]
        if actual != expected:
            raise ValueError(f"unexpected literal at 0x{address:08x}: 0x{actual:08x}")
        literals[f"0x{address:08x}"] = f"0x{actual:08x}"

    descriptor = flash_bytes(
        image,
        base,
        HRV_DESCRIPTOR_ADDRESS,
        HRV_DESCRIPTOR_ADDRESS + len(EXPECTED_HRV_DESCRIPTOR),
    )
    if descriptor != EXPECTED_HRV_DESCRIPTOR:
        raise ValueError(f"unexpected HRV descriptor: {descriptor.hex()}")

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "descriptor": {
            "address": f"0x{HRV_DESCRIPTOR_ADDRESS:08x}",
            "raw_hex": descriptor.hex(),
            "metric_index": descriptor[0],
            "serialized_slot_bytes": descriptor[1],
            "callbacks_thumb": [
                f"0x{struct.unpack_from('<I', descriptor, offset)[0]:08x}"
                for offset in (4, 8, 12)
            ],
        },
        "consumer": {
            "function": "0x0008a83e",
            "input_bytes": 8,
            "input_layout": [
                "RMSSD UInt16LE", "reserved UInt16LE", "timestamp UInt32LE",
            ],
            "zero_timestamp_filled_from_firmware_clock": True,
            "nonzero_timestamp_preserved": True,
            "compact_point_bytes": 6,
            "compact_layout": ["RMSSD UInt16LE", "timestamp UInt32LE"],
            "storage_notification_metric_index": 5,
            "rmssd_range_check": None,
        },
        "aggregator": {
            "function": "0x0005af60",
            "null_input_is_noop": True,
            "slot_count": 24,
            "slot_bytes": 6,
            "slot_layout": [
                "average UInt16LE", "maximum UInt16LE", "minimum UInt16LE",
            ],
            "rolling_average_metric_index": 5,
            "local_hour_helper_calls_per_nonnull_point": 2,
            "slot_calls_can_observe_different_offset_snapshots": True,
            "minimum_zero_is_empty_sentinel": True,
            "latest_point_is_updated_for_every_nonnull_point": True,
            "average_conversion": "VCVT.U32.F32 saturating/truncating, then low UInt16",
            "count_wrap_nonzero_sum": "positive infinity -> 0xffffffff -> 0xffff",
            "count_and_sum_wrap_to_zero": "NaN -> 0",
        },
        "rolling_accumulator": {
            "array_address": "0x20016648",
            "metric_5_address": "0x20016670",
            "bytes": 8,
            "layout": {
                "local_hour_byte": "0x00",
                "reserved_byte": "0x01",
                "sample_count_uint16": "0x02",
                "sum_uint32": "0x04",
            },
            "resets_when_count_zero_or_hour_changes": True,
        },
        "hourly_cache": {
            "address": "0x200169c0",
            "modeled_capture_bytes": 160,
            "layout": {
                "24_hourly_slots": "0x00...0x8f",
                "signed_utc_offset_minutes": "0x90...0x91",
                "reserved_before_latest": "0x92",
                "latest_compact_point": "0x93...0x98",
                "reserved_after_latest": "0x99...0x9b",
                "local_day_start_timestamp": "0x9c...0x9f",
            },
            "latest_accessor_function": "0x0005af20",
            "latest_accessor_requires_nonzero_rmssd": True,
            "zero_rmssd_can_be_stored_but_is_reported_absent": True,
            "clock_initializer_function": "0x0005af44",
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
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
