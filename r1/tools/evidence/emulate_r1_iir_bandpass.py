#!/usr/bin/env python3
"""Execute isolated production-Thumb band-pass IIR design fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import (
    IMAGE_SHA256,
    LocomotionFirmwareFixture,
    RAM_BASE,
)


DESIGNER = 0x000711B4
OUTPUT = RAM_BASE + 0x69400
CUTOFFS = RAM_BASE + 0x69500


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def execute(
    image: bytes, order: int, low: float, high: float
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(OUTPUT, b"\xA5" * 0x30)
    fixture.uc.mem_write(CUTOFFS, struct.pack("<2f", low, high))
    fixture.call(DESIGNER, OUTPUT, order, CUTOFFS)
    words = struct.unpack("<12I", fixture.uc.mem_read(OUTPUT, 0x30))
    return {
        "order": order,
        "cutoff_bits": [f"0x{float_bits(value):08x}" for value in (low, high)],
        "record_words": [f"0x{word:08x}" for word in words],
    }


def run(image: bytes) -> dict[str, Any]:
    fixtures = {
        "order1": execute(image, 1, 0.10, 0.30),
        "sleep_peak": execute(image, 2, 0.016, 0.16),
        "raw_optical": execute(image, 2, 0.0104, 0.96),
    }
    expected_words = {
        "order1": [
            "0xa5a5a5a5", "0x00000000", "0x3f800000", "0xbfa45cb4",
            "0x3f027042", "0xa5a5a5a5", "0xa5a5a5a5", "0x3e7b1f7b",
            "0x00000000", "0xbe7b1f7b", "0xa5a5a5a5", "0xa5a5a5a5",
        ],
        "sleep_peak": [
            "0xa5a5a5a5", "0x00000000", "0x3f800000", "0xc0552c25",
            "0x408676e0", "0xc01980f5", "0x3f071cb3", "0x3d1d6014",
            "0x00000000", "0xbd9d6014", "0x00000000", "0x3d1d6014",
        ],
        "raw_optical": [
            "0xa5a5a5a5", "0x00000000", "0x3f800000", "0xbe0647aa",
            "0xbfe271ce", "0x3dd66071", "0x3f4ca43a", "0x3f64e157",
            "0x00000000", "0xbfe4e157", "0x00000000", "0x3f64e157",
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
