#!/usr/bin/env python3
"""Execute isolated production-Thumb locomotion crossing-period fixtures."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture


EXPECTED = {
    8: ("0x433b8000", "0x43009249"),
    9: ("0x4326aaaa", "0x42b99128"),
    10: ("0x43160000", "0x42c80000"),
    11: ("0x43085d17", "0x43085d17"),
    12: ("0x42f9ffff", "0x42f9ffff"),
    13: ("0x42e6c4ec", "0x42e6c4ec"),
    14: ("0x42d64924", "0x42d64924"),
    15: ("0x42c80000", "0x42c80000"),
    16: ("0x42bb8000", "0x42bb8000"),
    17: ("0x42b07878", "0x00000000"),
    18: ("0x42a6aaaa", "0x00000000"),
    19: ("0x429de50d", "0x4311294b"),
    20: ("0x42960000", "0x43152bd9"),
    21: ("0x428edb6e", "0x430edb6e"),
    22: ("0x42885d17", "0x43070000"),
    23: ("0x42826f4e", "0x4301bacf"),
    24: ("0x4279ffff", "0x42f9ffff"),
    25: ("0x42700000", "0x42ed49c2"),
    26: ("0x00000000", "0x42e6c4ec"),
    27: ("0x00000000", "0x42de38e3"),
    28: ("0x00000000", "0x42d64924"),
    29: ("0x00000000", "0x42cee584"),
    30: ("0x00000000", "0x42c80000"),
    31: ("0x00000000", "0x42c3594e"),
    32: ("0x00000000", "0x42bd7944"),
    33: ("0x00000000", "0x42b89d8a"),
    34: ("0x00000000", "0x42b31abf"),
    35: ("0x00000000", "0x42b07878"),
    36: ("0x00000000", "0x42ab6db7"),
    37: ("0x00000000", "0x42a6aaaa"),
    38: ("0x00000000", "0x42a30b21"),
    39: ("0x00000000", "0x429ebaec"),
    40: ("0x00000000", "0x4299d89e"),
    41: ("0x00000000", "0x4296c0f7"),
    42: ("0x00000000", "0x4292576a"),
    43: ("0x00000000", "0x428edb6e"),
    44: ("0x00000000", "0x42903b14"),
    45: ("0x00000000", "0x428cd856"),
    46: ("0x00000000", "0x428a3fb5"),
    47: ("0x00000000", "0x4287bf21"),
    48: ("0x00000000", "0x42842899"),
    49: ("0x00000000", "0x4283de3e"),
    50: ("0x00000000", "0x4281bacf"),
    51: ("0x00000000", "0x42817f15"),
    52: ("0x00000000", "0x00000000"),
    53: ("0x00000000", "0x00000000"),
    54: ("0x00000000", "0x00000000"),
    55: ("0x00000000", "0x00000000"),
}


def run(image: bytes) -> dict[str, Any]:
    machine = LocomotionFirmwareFixture(image)
    sine: dict[str, Any] = {}
    for period, expected in EXPECTED.items():
        values = [
            int(1_500 + 800 * math.sin(2 * math.pi * index / period))
            for index in range(200)
        ]
        result = machine.crossing(values, 1_500)
        assert result["mode_2_float32_bits"] == expected[0]
        assert result["mode_1_float32_bits"] == expected[1]
        sine[f"period_{period}"] = result

    alternating = machine.crossing([
        700 if (index // 5) % 2 == 0 else 2_300 for index in range(200)
    ], 1_500)
    assert alternating["mode_2_float32_bits"] == "0x43160000"
    assert alternating["mode_1_float32_bits"] == "0x42c8f4fa"

    rejected = {
        "constant": machine.crossing([1_500] * 200, 1_500),
        "wrapped_extreme": machine.crossing(
            [0 if index % 2 == 0 else 65_535 for index in range(200)],
            -32_768,
        ),
    }
    assert all(item["mode_2_float32_bits"] == "0x00000000" and
               item["mode_1_float32_bits"] == "0x00000000"
               for item in rejected.values())

    return {
        "fixture_groups": 51,
        "sine": sine,
        "alternating_10": alternating,
        "rejected": rejected,
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
