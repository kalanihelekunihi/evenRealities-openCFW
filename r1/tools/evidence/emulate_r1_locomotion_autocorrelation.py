#!/usr/bin/env python3
"""Execute isolated production-Thumb locomotion autocorrelation fixtures."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture


EXPECTED = {
    12: ["0x3f800000", "0x3f800000", "0x42fa0000", "0x42fabdf3", "0x42fabdf3"],
    15: ["0x3f800000", "0x3f800000", "0x42c80000", "0x42c88b88", "0x42c88b88"],
    20: ["0x3f800000", "0x3f800000", "0x42960000", "0x4295ffcf", "0x4295ffcf"],
    25: ["0x3f800000", "0x3f800000", "0x42700000", "0x426fffad", "0x426fffad"],
    30: ["0x3f800000", "0x3f800000", "0x424a3f48", "0x424994e2", "0x424994e2"],
    35: ["0x3f800000", "0x3f800000", "0x00000000", "0x00000000", "0x00000000"],
}


def run(image: bytes) -> dict[str, Any]:
    machine = LocomotionFirmwareFixture(image)
    sine: dict[str, Any] = {}
    for period, expected in EXPECTED.items():
        values = [
            int(1_500 + 800 * math.sin(2 * math.pi * index / period))
            for index in range(100)
        ]
        result = machine.autocorrelation(values)
        assert result["output_float32_bits"] == expected
        assert result["turning_counts"] == [1, 0]
        sine[f"period_{period}"] = result

    alternating = machine.autocorrelation([
        700 if (index // 5) % 2 == 0 else 2_300 for index in range(100)
    ])
    assert alternating["output_float32_bits"] == [
        "0x3f800000", "0x3f800000", "0x43160000", "0x4315cabd",
        "0x4315cabd",
    ]
    assert alternating["turning_counts"] == [1, 0]
    assert alternating["shape_float32_bits"] == ["0x3da844a3", "0x40a00000"]

    rejected = {
        "constant": machine.autocorrelation([1_500] * 100),
        "ramp": machine.autocorrelation(list(range(100))),
        "wrapped_extreme": machine.autocorrelation(
            [65_535 if index % 2 == 0 else 0 for index in range(100)]
        ),
    }
    defaults = ["0xbf800000", "0xbf800000", "0x00000000",
                "0x00000000", "0x00000000"]
    assert all(item["output_float32_bits"] == defaults
               for item in rejected.values())

    return {
        "fixture_groups": 9,
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
