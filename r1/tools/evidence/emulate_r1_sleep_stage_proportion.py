#!/usr/bin/env python3
"""Execute isolated production-Thumb sleep-stage proportion fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


ADJUSTER = 0x00064CC8
VALUES = RAM_BASE + 0x65000


def signed32(value: int) -> int:
    return value - (1 << 32) if value & (1 << 31) else value


def execute(
    fixture: LocomotionFirmwareFixture,
    values: list[int],
    target: int,
    adjustment: int,
) -> dict[str, Any]:
    fixture.uc.mem_write(VALUES, bytes(values))
    result = signed32(fixture.call(
        ADJUSTER, VALUES, len(values), target, adjustment & 0xFFFFFFFF
    ))
    return {
        "input": values,
        "target": target,
        "adjustment": adjustment,
        "return": result,
        "output": list(fixture.uc.mem_read(VALUES, len(values))),
    }


def run(image: bytes) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixtures = {
        "dead_zone": execute(fixture, [1, 1, 1], 1, 6),
        "negative_long": execute(fixture, [1] * 20, 1, -20),
        "negative_short": execute(fixture, [1] * 5, 1, -7),
        "positive_trailing": execute(fixture, [1] * 3 + [2] * 12, 1, 20),
        "positive_fallback": execute(fixture, [2] * 40, 3, 20),
        "positive_target_two": execute(fixture, [2] * 40, 2, 20),
        "negative_reverse": execute(
            fixture, [3] * 14 + [0] + [3] * 14, 3, -18
        ),
    }

    assert fixtures["dead_zone"]["return"] == 6
    assert fixtures["dead_zone"]["output"] == [1, 1, 1]
    assert fixtures["negative_long"]["return"] == -8
    assert fixtures["negative_long"]["output"] == (
        [2] * 6 + [1] * 8 + [2] * 6
    )
    assert fixtures["negative_short"]["return"] == -12
    assert fixtures["negative_short"]["output"] == [2] * 5
    assert fixtures["positive_trailing"]["return"] == 14
    assert fixtures["positive_trailing"]["output"] == [1] * 9 + [2] * 6
    assert fixtures["positive_fallback"]["return"] == 8
    assert fixtures["positive_fallback"]["output"] == (
        [2] * 14 + [3] * 12 + [2] * 14
    )
    assert fixtures["positive_target_two"]["return"] == 7
    assert fixtures["positive_target_two"]["output"] == [2] * 40
    assert fixtures["negative_reverse"]["return"] == -6
    assert fixtures["negative_reverse"]["output"] == (
        [3] * 14 + [0] + [2] * 6 + [3] * 2 + [2] * 6
    )
    return {
        "fixture_groups": len(fixtures),
        "fixtures": fixtures,
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
