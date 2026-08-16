#!/usr/bin/env python3
"""Execute isolated production-Thumb low/high-pass IIR design fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0

from emulate_r1_locomotion_window import (
    IMAGE_SHA256,
    LocomotionFirmwareFixture,
    RAM_BASE,
)


DESIGNER = 0x000717AC
OUTPUT = RAM_BASE + 0x69000


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def execute(
    image: bytes, mode: int, order: int, normalized_cutoff: float
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(OUTPUT, b"\xA5" * 0x30)
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(normalized_cutoff))
    fixture.call(DESIGNER, OUTPUT, mode, order)
    words = struct.unpack("<12I", fixture.uc.mem_read(OUTPUT, 0x30))
    return {
        "mode": mode,
        "order": order,
        "normalized_cutoff_bits": f"0x{float_bits(normalized_cutoff):08x}",
        "record_words": [f"0x{word:08x}" for word in words],
    }


def run(image: bytes) -> dict[str, Any]:
    fixtures = {
        "low_order1": execute(image, 0, 1, 0.25),
        "high_order2": execute(image, 1, 2, 0.16),
        "low_order2_stock": execute(image, 0, 2, 0.16),
        "low_order3": execute(image, 0, 3, 0.10),
        "high_order4": execute(image, 1, 4, 0.40),
    }
    expected_words = {
        "low_order1": [
            "0xa5a5a5a5", "0x00000000", "0x3f800000", "0xbed413cb",
            "0xa5a5a5a5", "0xa5a5a5a5", "0xa5a5a5a5", "0x3e95f61b",
            "0x3e95f61b", "0xa5a5a5a5", "0xa5a5a5a5", "0xa5a5a5a5",
        ],
        "high_order2": [
            "0xa5a5a5a5", "0x00000000", "0x3f800000", "0xbfa7551d",
            "0x3efbcece", "0xa5a5a5a5", "0xa5a5a5a5", "0x3f332469",
            "0xbfb32469", "0x3f332469", "0xa5a5a5a5", "0xa5a5a5a5",
        ],
        "low_order2_stock": [
            "0xa5a5a5a5", "0x00000000", "0x3f800000", "0xbfa7551d",
            "0x3efbcece", "0xa5a5a5a5", "0xa5a5a5a5", "0x3d3cf4b5",
            "0x3dbcf4b5", "0x3d3cf4b5", "0xa5a5a5a5", "0xa5a5a5a5",
        ],
        "low_order3": [
            "0xa5a5a5a5", "0x00000000", "0x3f800000", "0xc017f12c",
            "0x3ff6f522", "0xbf083618", "0xa5a5a5a5", "0x3b3defa6",
            "0x3c0e73bc", "0x3c0e73bc", "0x3b3defa6", "0xa5a5a5a5",
        ],
        "high_order4": [
            "0xa5a5a5a5", "0x00000000", "0x3f800000", "0xbf483763",
            "0x3f2e1313", "0xbe3b0f57", "0x3cf6bbe0", "0x3e2b3108",
            "0xbf2b3108", "0x3f8064c6", "0xbf2b3108", "0x3e2b3108",
        ],
    }
    for name, words in expected_words.items():
        assert fixtures[name]["record_words"] == words
    return {
        "image_sha256": IMAGE_SHA256,
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
