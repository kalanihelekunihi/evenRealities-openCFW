#!/usr/bin/env python3
"""Exercise flagged helper `0x676e0` from the dormant speed-dynamics graph.

The helper is reached only when the shared dynamics flag word contains `0x0440`; that word is zero
initialized and has no recovered writer. Fixtures use synthetic Float32 inputs and private RAM.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


THRESHOLD_CONVERTER = 0x000676E0
STATE = RAM_BASE + 0x7D00


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def float_record(bits: int) -> dict[str, Any]:
    return {
        "bits": f"0x{bits:08x}",
        "value": struct.unpack("<f", struct.pack("<I", bits))[0],
    }


def run_case(image: bytes, *, input_bits: int, state_first_bits: int) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(STATE, struct.pack("<I", state_first_bits) + bytes(40))
    fixture.uc.reg_write(UC_ARM_REG_S0, input_bits)
    fixture.call(THRESHOLD_CONVERTER, STATE)
    output_bits = fixture.uc.reg_read(UC_ARM_REG_S0)
    return {
        "input": float_record(input_bits),
        "state_first": float_record(state_first_bits),
        "output": float_record(output_bits),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    cases = {
        "ordinary": run_case(
            image, input_bits=float_bits(4), state_first_bits=float_bits(1)
        ),
        "negative": run_case(
            image, input_bits=float_bits(-4), state_first_bits=float_bits(1)
        ),
        "zero_over_zero": run_case(
            image, input_bits=float_bits(0), state_first_bits=float_bits(0)
        ),
        "positive_over_zero": run_case(
            image, input_bits=float_bits(1), state_first_bits=float_bits(0)
        ),
        "negative_over_zero": run_case(
            image, input_bits=float_bits(-1), state_first_bits=float_bits(0)
        ),
        "positive_nan": run_case(
            image, input_bits=0x7FC00000, state_first_bits=float_bits(1)
        ),
        "negative_nan": run_case(
            image, input_bits=0xFFC00000, state_first_bits=float_bits(1)
        ),
        "positive_infinity": run_case(
            image, input_bits=0x7F800000, state_first_bits=float_bits(1)
        ),
        "negative_infinity": run_case(
            image, input_bits=0xFF800000, state_first_bits=float_bits(1)
        ),
    }

    assert cases["ordinary"]["output"]["bits"] == "0x40461279"
    assert cases["negative"]["output"]["bits"] == "0xc0461279"
    assert cases["zero_over_zero"]["output"]["bits"] == "0x435c0000"
    assert cases["positive_over_zero"]["output"]["bits"] == "0x435c0000"
    assert cases["negative_over_zero"]["output"]["bits"] == "0xff800000"
    assert cases["positive_nan"]["output"]["bits"] == "0x435c0000"
    assert cases["negative_nan"]["output"]["bits"] == "0xffc00000"
    assert cases["positive_infinity"]["output"]["bits"] == "0x435c0000"
    assert cases["negative_infinity"]["output"]["bits"] == "0x435c0000"

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "function": f"0x{THRESHOLD_CONVERTER:08x}",
        "constants": {
            "absolute_offset": 2.5,
            "slope_bits": "0x3e20fba9",
            "intercept_bits": "0x3f0a2728",
            "denominator_scale_bits": "0x42c80000",
            "numerator_scale_bits": "0x42700000",
            "signed_raw_cap_bits": "0x435c0000",
        },
        "cases": cases,
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
