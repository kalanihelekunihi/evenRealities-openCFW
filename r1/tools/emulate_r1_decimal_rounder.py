#!/usr/bin/env python3
"""Exercise Float32 decimal-rounding helper `0x80f88` in private production emulation."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0, UC_ARM_REG_S1

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture


DECIMAL_ROUNDER = 0x00080F88


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def float_record(bits: int) -> dict[str, Any]:
    return {
        "bits": f"0x{bits:08x}",
        "value": struct.unpack("<f", struct.pack("<I", bits))[0],
    }


def run_case(image: bytes, *, value_bits: int, places_bits: int) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.reg_write(UC_ARM_REG_S0, value_bits)
    fixture.uc.reg_write(UC_ARM_REG_S1, places_bits)
    fixture.call(DECIMAL_ROUNDER)
    return {
        "value": float_record(value_bits),
        "decimal_places": float_record(places_bits),
        "output": float_record(fixture.uc.reg_read(UC_ARM_REG_S0)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    fixtures = {
        name: run_case(image, value_bits=value_bits, places_bits=places_bits)
        for name, value_bits, places_bits in (
            ("positive_down", float_bits(1.2344), float_bits(3)),
            ("positive_up", float_bits(1.2346), float_bits(3)),
            ("positive_half", float_bits(1.2345), float_bits(3)),
            ("negative_down", float_bits(-1.2344), float_bits(3)),
            ("negative_up", float_bits(-1.2346), float_bits(3)),
            ("negative_half", float_bits(-1.2345), float_bits(3)),
            ("zero_places", float_bits(12.6), float_bits(0)),
            ("negative_places", float_bits(125.0), float_bits(-1)),
            ("positive_zero", float_bits(0), float_bits(5)),
            ("negative_zero", 0x80000000, float_bits(5)),
            ("positive_nan", 0x7FC00000, float_bits(3)),
            ("negative_nan", 0xFFC00000, float_bits(3)),
            ("positive_infinity", 0x7F800000, float_bits(3)),
            ("negative_infinity", 0xFF800000, float_bits(3)),
            ("huge_positive", float_bits(1.0e20), float_bits(3)),
            ("huge_negative", float_bits(-1.0e20), float_bits(3)),
            ("factor_underflow", float_bits(1), float_bits(-100)),
        )
    }

    expected = {
        "positive_down": "0x3f9df3b6",
        "positive_up": "0x3f9e147b",
        "positive_half": "0x3f9e147b",
        "negative_down": "0xbf9df3b6",
        "negative_up": "0xbf9e147b",
        "negative_half": "0xbf9df3b6",
        "zero_places": "0x41500000",
        "negative_places": "0x43020000",
        "positive_zero": "0x00000000",
        "negative_zero": "0x00000000",
        "positive_nan": "0x00000000",
        "negative_nan": "0x00000000",
        "positive_infinity": "0x4a03126f",
        "negative_infinity": "0xca03126f",
        "huge_positive": "0x4a03126f",
        "huge_negative": "0xca03126f",
        "factor_underflow": "0x00000000",
    }
    assert {
        name: fixture["output"]["bits"] for name, fixture in fixtures.items()
    } == expected

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "function": f"0x{DECIMAL_ROUNDER:08x}",
        "negative_bias_bits": "0x3ecccccd",
        "fixtures": fixtures,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "firmware_execution_outside_private_emulation": False,
            "flash_writes": False,
            "health_store_access": False,
        },
    }, indent=2, sort_keys=True, allow_nan=True))


if __name__ == "__main__":
    main()
