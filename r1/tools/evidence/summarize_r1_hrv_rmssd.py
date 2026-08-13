#!/usr/bin/env python3
"""Validate the exact R1 RMSSD filter, Float32 calculation and publication boundary."""

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
    (0x0004A24C, 0x0004A39C):
        "626f65b0231cd2debb7b3a0d6a4f70a83f4debdd71235904e57abf8fb426394d",
    (0x000575D8, 0x000577F0):
        "3a710e22a9534adab1987b52c17d3485cd34ef9df18a7bf043221a8e80a9f0ad",
    (0x0004A8BC, 0x0004A8C8):
        "71686482cd48aa2a9d9a0550f42046d05600f56afa4f6c8817263d023d6abdd2",
    (0x0004C634, 0x0004C648):
        "bb9e511c5ebd46dd5151b0c5e4679a058fe6c74e9c0316e386e73c199bd42ee1",
    (0x0008A83E, 0x0008A876):
        "3d6ffb26e2d7d73e0ead6eba1a1ee1a6544c656f8c81f9de14f4f930405487c1",
    (0x0005AF60, 0x0005B0E0):
        "b95bdb86c76d82cf825642f26fcce16e5218a61581bdef3a696eb14ba12e45ca",
    (0x00049E00, 0x00049E20):
        "55a7524d8f5c699906ceccbc69c8aabc920a02191a70b5bdafd74629e6b88c0b",
    (0x00049EF4, 0x00049F0C):
        "d6d27835c5b394eb21ba63068e18944e072621e68680a924ea274abc14a0786d",
}

EXPECTED_BRANCHES = {
    0x000575D8: [0x0004A2E4],
    0x0005AF60: [0x0008A85A],
    0x0008A83E: [0x000428AC],
    0x00049E00: [
        0x000498B8, 0x00049D8C, 0x00049E34,
        0x00049E98, 0x0004A32A, 0x0004A398,
    ],
    0x00049EF4: [
        0x000498BC, 0x00049D90, 0x00049E38,
        0x0004A044, 0x0004A332,
    ],
}

EXPECTED_LITERALS = {
    0x0004A39C: 0x2001A300,
    0x0004A3A0: 0x20006D84,
    0x0004A8C4: 0x20006ED4,
    0x0004C648: 0x2001E454,
    0x000578BC: 0x00000000,
}


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

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "rmssd": {
            "function": "0x000575d8",
            "complete": True,
            "minimum_interval_count": 2,
            "validity_initial_value": 1,
            "adjacent_change_inclusive_milliseconds": [-150, 150],
            "invalid_pair_clears_both_endpoints": True,
            "default_current_interval_maximum_milliseconds": 1100,
            "alternate_current_interval_maximum_milliseconds": 1500,
            "ceiling_check_starts_at_index": 1,
            "first_interval_ceiling_quirk": "index zero is not independently ceiling-checked",
            "accepted_difference": "absolute UInt16 milliseconds",
            "square_conversion": "VCVT.F32.S32",
            "sum": "sequential Float32 from zero",
            "divisor": "accepted difference count as Float32",
            "root": "sqrtf",
            "no_accepted_difference_result_float32_bits": "0xbf800000",
        },
        "producer": {
            "function": "0x0004a24c",
            "complete_publication_boundary": True,
            "complete_state_machine": True,
            "circular_buffer_capacity": 100,
            "state_bytes": 208,
            "state_layout": {
                "physical_uint16_buffer": "0x000...0x0c7",
                "write_index_uint16": "0x0c8",
                "buffered_count_uint16": "0x0ca",
                "nonzero_count_uint16": "0x0cc",
                "callback_count_uint16": "0x0ce",
            },
            "input_values_per_callback_maximum": 4,
            "warmup_callbacks_ignored": 9,
            "first_result_callback": 60,
            "minimum_nonzero_buffered_intervals": 70,
            "ordered_positive_rmssd_required": True,
            "nan_and_nonpositive_are_rejected_before_conversion": True,
            "independent_eligibility_function": "0x0004c634",
            "conversion": "saturating VCVT.U32.F32 toward zero",
            "positive_overflow_or_infinity": "0xffffffff",
            "event_id": 7,
            "event_payload": [
                "RMSSD low UInt16LE", "reserved UInt16LE zero", "timestamp UInt32LE",
            ],
            "uint16_store_wraps_converted_values": True,
            "positive_subunit_value_can_publish_zero": True,
            "success_and_failure_reset_the_window": True,
            "rmssd_consumes_physical_buffer_order_without_rotation": True,
            "full_buffer_replaces_write_index_then_advances_it": True,
            "zero_inputs_are_skipped_entirely": True,
            "ordinary_failure_unregisters_and_clears": True,
            "timed_window_failure_clears_state_but_keeps_subscription_and_timer": True,
            "success_unregisters_and_clears": True,
            "timed_window_success_stops_timer_and_sets_completion_byte": True,
            "reset_function": "0x00049e00",
            "timed_window_stop_function": "0x00049ef4",
        },
        "consumer": {
            "event_function": "0x0008a83e",
            "zero_timestamp_is_replaced": True,
            "aggregate_function": "0x0005af60",
            "aggregate_fields": ["latest", "average", "maximum", "minimum"],
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
