#!/usr/bin/env python3
"""Exercise dormant dynamics reducer `0x888a0` in private production-Thumb emulation."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


REDUCER = 0x000888A0
STATE = RAM_BASE + 0x7E00


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def float_record(bits: int) -> dict[str, Any]:
    return {
        "bits": f"0x{bits:08x}",
        "value": struct.unpack("<f", struct.pack("<I", bits))[0],
    }


def run_case(
    image: bytes,
    *,
    primary: float,
    secondary: float,
    auxiliary: float,
    first_parameter: float = 1.2,
    second_parameter: float = 70,
    previous_transformed: float = 0,
    previous_power_term: float = 0,
    flags: int = 0,
    mode: int = 0,
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(44)
    struct.pack_into(
        "<fffff", state, 0,
        first_parameter, second_parameter, previous_transformed, 0, previous_power_term,
    )
    struct.pack_into("<H", state, 0x24, flags)
    fixture.uc.mem_write(STATE, bytes(state))
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(primary))
    fixture.uc.reg_write(UC_ARM_REG_S1, float_bits(secondary))
    fixture.uc.reg_write(UC_ARM_REG_S2, float_bits(auxiliary))
    fixture.call(REDUCER, STATE, mode)
    final_state = bytes(fixture.uc.mem_read(STATE, 44))
    return {
        "primary": float_record(float_bits(primary)),
        "secondary": float_record(float_bits(secondary)),
        "auxiliary": float_record(float_bits(auxiliary)),
        "mode": mode,
        "flags": f"0x{flags:04x}",
        "output": float_record(fixture.uc.reg_read(UC_ARM_REG_S0)),
        "state_before_float32_bits": [
            f"0x{bits:08x}" for bits in struct.unpack("<9I", state[:36])
        ],
        "state_after_float32_bits": [
            f"0x{bits:08x}" for bits in struct.unpack("<9I", final_state[:36])
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    fixtures = {
        "subunit_zero_secondary": run_case(
            image, primary=0.5, secondary=0, auxiliary=165
        ),
        "unit_zero_secondary": run_case(
            image, primary=1, secondary=0, auxiliary=165
        ),
        "superunit_zero_secondary_mode_zero": run_case(
            image, primary=2, secondary=0, auxiliary=165
        ),
        "superunit_zero_secondary_mode_one": run_case(
            image, primary=2, secondary=0, auxiliary=165, mode=1
        ),
        "superunit_trigonometric": run_case(
            image, primary=2, secondary=1, auxiliary=165
        ),
        "subunit_large_secondary_retained": run_case(
            image, primary=0.5, secondary=10, auxiliary=165
        ),
        "subunit_boundary_near_secondary_retained": run_case(
            image, primary=0.5, secondary=0.1, auxiliary=165
        ),
        "subunit_small_secondary_suppressed": run_case(
            image, primary=0.5, secondary=0.01, auxiliary=165
        ),
        "flagged_subunit": run_case(
            image, primary=0.5, secondary=0, auxiliary=165, flags=0x0440
        ),
        "falling_power_term": run_case(
            image,
            primary=2,
            secondary=0,
            auxiliary=165,
            previous_power_term=200,
        ),
        "stable_power_term": run_case(
            image,
            primary=2,
            secondary=0,
            auxiliary=165,
            previous_power_term=140,
        ),
    }

    expected_outputs = {
        "subunit_zero_secondary": "0x41e8424f",
        "unit_zero_secondary": "0x4268424f",
        "superunit_zero_secondary_mode_zero": "0x434e3254",
        "superunit_zero_secondary_mode_one": "0x434ed9ae",
        "superunit_trigonometric": "0x44197b59",
        "subunit_large_secondary_retained": "0x456f578f",
        "subunit_boundary_near_secondary_retained": "0x428612d4",
        "subunit_small_secondary_suppressed": "0x41e8424f",
        "flagged_subunit": "0x3fa40dad",
        "falling_power_term": "0x4300a2f7",
        "stable_power_term": "0x4300a2f7",
    }
    assert {
        name: fixture["output"]["bits"] for name, fixture in fixtures.items()
    } == expected_outputs
    assert fixtures["superunit_zero_secondary_mode_zero"][
        "state_after_float32_bits"
    ][2:5] == ["0x40000000", "0x00000000", "0x430c0000"]
    assert fixtures["superunit_trigonometric"]["state_after_float32_bits"][2:5] == [
        "0x400f1bbd", "0x00000000", "0x432f0000",
    ]
    assert fixtures["subunit_zero_secondary"]["state_after_float32_bits"] == fixtures[
        "subunit_zero_secondary"
    ]["state_before_float32_bits"]

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "function": f"0x{REDUCER:08x}",
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
