#!/usr/bin/env python3
"""Execute isolated production-Thumb moving-average extrema fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


MOVING_AVERAGE_EXTREMA = 0x000647C4
VALUES = RAM_BASE + 0x60000
MAXIMA = VALUES + 0x1000
MINIMA = MAXIMA + 0x100
MAXIMA_COUNT = MINIMA + 0x100
MINIMA_COUNT = MAXIMA_COUNT + 4


def execute(
    fixture: LocomotionFirmwareFixture,
    values: list[float],
    long_window: int,
    short_window: int,
) -> dict[str, Any]:
    fixture.uc.mem_write(
        VALUES, struct.pack("<" + "f" * len(values), *values)
    )
    fixture.uc.mem_write(MAXIMA, b"\xA5" * 20)
    fixture.uc.mem_write(MINIMA, b"\x5A" * 20)
    fixture.uc.mem_write(MAXIMA_COUNT, b"\xA5" * 4)
    fixture.uc.mem_write(MINIMA_COUNT, b"\x5A" * 4)
    status = fixture.call(
        MOVING_AVERAGE_EXTREMA,
        VALUES,
        len(values),
        long_window,
        short_window,
        MAXIMA,
        MINIMA,
        MAXIMA_COUNT,
        MINIMA_COUNT,
    )
    maxima_count = fixture.uc.mem_read(MAXIMA_COUNT, 1)[0]
    minima_count = fixture.uc.mem_read(MINIMA_COUNT, 1)[0]
    return {
        "status": status,
        "maxima": list(fixture.uc.mem_read(MAXIMA, maxima_count)),
        "minima": list(fixture.uc.mem_read(MINIMA, minima_count)),
        "maxima_count": maxima_count,
        "minima_count": minima_count,
    }


def run(image: bytes) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    triangle = [
        float(10 - abs((index % 20) - 10)) for index in range(250)
    ]
    square = [
        1.0 if index % 10 < 5 else -1.0 for index in range(250)
    ]
    mode_25_6 = execute(fixture, triangle, 25, 6)
    mode_38_12 = execute(fixture, triangle, 38, 12)
    overflow = execute(fixture, square, 25, 6)

    expected_maxima = list(range(10, 250, 20))
    expected_minima = list(range(0, 250, 20))
    assert mode_25_6 == {
        "status": 0,
        "maxima": expected_maxima,
        "minima": expected_minima,
        "maxima_count": 12,
        "minima_count": 13,
    }
    assert mode_38_12 == mode_25_6
    assert overflow == {
        "status": 1,
        "maxima": [],
        "minima": [],
        "maxima_count": 0,
        "minima_count": 0,
    }
    return {
        "fixture_groups": 3,
        "triangle_25_6": mode_25_6,
        "triangle_38_12": mode_38_12,
        "overflow": overflow,
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
