#!/usr/bin/env python3
"""Decode R1 battery voltage curves and charging cadence tables without executing firmware."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import decompress_scatter, mapped_offset


DEFAULT_BASE = 0x27000
DEFAULT_SCATTER_SOURCE = 0xC4610
DEFAULT_SCATTER_RUNTIME = 0x200064A8
DEFAULT_SCATTER_LENGTH = 0x195C
DEFAULT_CHARGE_CADENCE = 0x200068BC
CURVE_SEGMENTS = 20
CURVE_WORDS = CURVE_SEGMENTS * 3
CURVE_BYTES = CURVE_WORDS * 2
DISCHARGE_CURVES = [0x99D16, 0x99D8E, 0x99E06, 0x99E7E]
CHARGING_INITIAL_CURVES = [0x99EF6, 0x99F6E, 0x99FE6, 0x9A05E]


def decode_curve(image: bytes, base: int, address: int) -> dict[str, Any]:
    offset = mapped_offset(address, base, len(image))
    if offset + CURVE_BYTES > len(image):
        raise ValueError(f"curve at 0x{address:08x} extends beyond the image")
    words = struct.unpack_from(f"<{CURVE_WORDS}H", image, offset)
    segments = [
        {
            "index": index,
            "lower_millivolts": words[index * 3],
            "upper_millivolts": words[index * 3 + 1],
            "percentage_points_word": words[index * 3 + 2],
            "percentage_points_low_byte": words[index * 3 + 2] & 0xFF,
        }
        for index in range(CURVE_SEGMENTS)
    ]
    return {
        "address": f"0x{address:08x}",
        "segments": segments,
        "percentage_point_sum": sum(
            segment["percentage_points_low_byte"] for segment in segments
        ) & 0xFF,
        "first_lower_millivolts": segments[0]["lower_millivolts"],
        "last_upper_clamp_millivolts": segments[-1]["upper_millivolts"],
        "all_percentage_words_are_five": all(
            segment["percentage_points_word"] == 5 for segment in segments
        ),
    }


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
    charge_cadence_address: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)
    cadence_offset = charge_cadence_address - scatter_runtime
    cadence_bytes = 4 * 6 * 2
    if cadence_offset < 0 or cadence_offset + cadence_bytes > len(runtime):
        raise ValueError("charging cadence table is outside the scatter image")
    cadence_words = struct.unpack_from("<24H", runtime, cadence_offset)
    cadence_profiles = []
    for index in range(4):
        values = list(cadence_words[index * 6:(index + 1) * 6])
        cadence_profiles.append({
            "battery_type_raw": index + 1,
            "seconds_per_percent_below_85": values[0],
            "seconds_per_percent_85_through_89": values[1],
            "seconds_per_percent_90_through_94": values[2],
            "seconds_per_percent_95_through_99": values[3],
            "trailing_words_unlabeled": values[4:],
        })

    def labeled_curves(addresses: list[int]) -> list[dict[str, Any]]:
        return [
            {"battery_type_raw": index + 1, **decode_curve(image, base, address)}
            for index, address in enumerate(addresses)
        ]

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "discharge_curves": labeled_curves(DISCHARGE_CURVES),
        "charging_initial_curves": labeled_curves(CHARGING_INITIAL_CURVES),
        "charging_cadence_address": f"0x{charge_cadence_address:08x}",
        "charging_cadence_profiles": cadence_profiles,
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
    parser.add_argument(
        "--charge-cadence-address",
        type=parse_integer,
        default=DEFAULT_CHARGE_CADENCE,
    )
    arguments = parser.parse_args()
    print(json.dumps(summarize(
        arguments.image,
        arguments.base,
        arguments.scatter_source,
        arguments.scatter_runtime,
        arguments.scatter_length,
        arguments.charge_cadence_address,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
