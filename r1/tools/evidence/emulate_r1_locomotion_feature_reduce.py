#!/usr/bin/env python3
"""Execute isolated production-Thumb locomotion feature-reducer fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import (
    LOAD_BASE,
    LocomotionFirmwareFixture,
    RAM_BASE,
)


FEATURE_REDUCE = 0x00068840
EXPANDED = RAM_BASE + 0x60000
FIRST_INDICES = EXPANDED + 0x1000
SECOND_INDICES = FIRST_INDICES + 0x100
SCRATCH = SECOND_INDICES + 0x100
PRIMARY = SCRATCH + 0x200
SECONDARY = PRIMARY + 4


def float_bits(data: bytes) -> list[str]:
    return [f"0x{value:08x}" for value in struct.unpack("<2I", data)]


def execute(
    fixture: LocomotionFirmwareFixture, values: list[float]
) -> dict[str, Any]:
    if len(values) != 250:
        raise ValueError("feature reducer requires exactly 250 Float32 samples")
    fixture.uc.mem_write(EXPANDED, struct.pack("<250f", *values))
    fixture.uc.mem_write(FIRST_INDICES, b"\x00" * 20)
    fixture.uc.mem_write(SECOND_INDICES, b"\x00" * 20)
    fixture.uc.mem_write(SCRATCH, b"\x00" * 160)
    fixture.uc.mem_write(PRIMARY, b"\x00" * 8)
    status = fixture.call(
        FEATURE_REDUCE,
        EXPANDED,
        FIRST_INDICES,
        SECOND_INDICES,
        SCRATCH,
        PRIMARY,
        SECONDARY,
    )
    output = bytes(fixture.uc.mem_read(PRIMARY, 8))
    return {
        "status": status,
        "output_float32_bits": float_bits(output),
        "output": list(struct.unpack("<2f", output)),
        "first_indices": list(fixture.uc.mem_read(FIRST_INDICES, 20)),
        "second_indices": list(fixture.uc.mem_read(SECOND_INDICES, 20)),
        "scratch_float32_bits": [
            f"0x{value:08x}"
            for value in struct.unpack(
                "<8I", bytes(fixture.uc.mem_read(SCRATCH, 32))
            )
        ],
    }


def variable_triangle() -> list[float]:
    values: list[float] = []
    for period in (40, 50, 45, 55, 48):
        values.extend(float(min(index, period - index)) for index in range(period))
    values.extend([0.0] * (250 - len(values)))
    return values


def run(image: bytes) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    constant = execute(fixture, [7.0] * 250)
    regular_triangle = execute(
        fixture,
        [float(10 - abs((index % 20) - 10)) for index in range(250)],
    )
    irregular_triangle = execute(fixture, variable_triangle())

    assert constant["status"] == 0
    assert constant["output_float32_bits"] == ["0xbf800000", "0x00000000"]
    assert constant["first_indices"] == [0] * 20
    assert constant["second_indices"] == [0] * 20

    assert regular_triangle["status"] == 0
    assert regular_triangle["output_float32_bits"] == [
        "0xbf800000",
        "0x00000000",
    ]
    assert regular_triangle["first_indices"][:12] == list(range(13, 234, 20))
    assert regular_triangle["second_indices"][:12] == list(range(3, 224, 20))
    assert regular_triangle["scratch_float32_bits"] == ["0x42160000"] * 8

    assert irregular_triangle["status"] == 0
    assert irregular_triangle["output_float32_bits"] == [
        "0x41760e19",
        "0x3f2ac478",
    ]
    assert irregular_triangle["first_indices"][:5] == [22, 66, 114, 164, 216]
    assert irregular_triangle["second_indices"][:5] == [5, 42, 92, 137, 191]
    assert irregular_triangle["scratch_float32_bits"] == [
        "0x41885d17",
        "0x417a0000",
        "0x41700000",
        "0x4166c4ec",
        "0x41a22983",
        "0x41700000",
        "0x41855555",
        "0x415e38e4",
    ]

    constants = {
        "threshold_scale": struct.unpack(
            "<d", image[0x00068C6C - LOAD_BASE : 0x00068C74 - LOAD_BASE]
        )[0],
        "sample_rate_divisor": struct.unpack(
            "<d", image[0x00068C74 - LOAD_BASE : 0x00068C7C - LOAD_BASE]
        )[0],
        "seconds_per_minute": struct.unpack(
            "<d", image[0x00068C7C - LOAD_BASE : 0x00068C84 - LOAD_BASE]
        )[0],
        "fallback_upper_exclusive": struct.unpack(
            "<d", image[0x00068C84 - LOAD_BASE : 0x00068C8C - LOAD_BASE]
        )[0],
        "quality_scale_float32_bits": f"0x{struct.unpack('<I', image[0x00068D14 - LOAD_BASE : 0x00068D18 - LOAD_BASE])[0]:08x}",
    }
    assert constants == {
        "threshold_scale": 0.2,
        "sample_rate_divisor": 12.5,
        "seconds_per_minute": 60.0,
        "fallback_upper_exclusive": 114.99999999999999,
        "quality_scale_float32_bits": "0x3eaaaaab",
    }
    return {
        "fixture_groups": 3,
        "constant": constant,
        "regular_triangle": regular_triangle,
        "irregular_triangle": irregular_triangle,
        "constants": constants,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
