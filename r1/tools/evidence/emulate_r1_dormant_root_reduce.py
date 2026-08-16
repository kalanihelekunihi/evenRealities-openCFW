#!/usr/bin/env python3
"""Execute isolated production-Thumb dormant root-reducer fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


DORMANT_ROOT_REDUCE = 0x000888A0
STATE = RAM_BASE + 0x60000


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def bits_float(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value))[0]


def execute(
    fixture: LocomotionFirmwareFixture,
    primary: float,
    secondary: float,
    auxiliary: float,
    flags: int = 0,
    previous_primary: float = 0.0,
    previous_kinetic: float = 0.0,
    mode: int = 0,
) -> dict[str, Any]:
    state = bytearray(0x30)
    struct.pack_into("<f", state, 0x00, 1.2)
    struct.pack_into("<f", state, 0x04, 70.0)
    struct.pack_into("<f", state, 0x08, previous_primary)
    struct.pack_into("<f", state, 0x10, previous_kinetic)
    struct.pack_into("<H", state, 0x24, flags)
    fixture.uc.mem_write(STATE, bytes(state))
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(primary))
    fixture.uc.reg_write(UC_ARM_REG_S1, float_bits(secondary))
    fixture.uc.reg_write(UC_ARM_REG_S2, float_bits(auxiliary))
    fixture.call(DORMANT_ROOT_REDUCE, STATE, mode)
    output_bits = fixture.uc.reg_read(UC_ARM_REG_S0)
    result_state = bytes(fixture.uc.mem_read(STATE, len(state)))
    return {
        "output_bits": f"0x{output_bits:08x}",
        "output": bits_float(output_bits),
        "stored_primary": struct.unpack_from("<f", result_state, 0x08)[0],
        "stored_kinetic": struct.unpack_from("<f", result_state, 0x10)[0],
    }


def run(image: bytes) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    low_zero = execute(fixture, 0.5, 0.0, 165.0)
    low_suppressed = execute(fixture, 0.5, 0.01, 165.0)
    low_retained = execute(fixture, 0.5, 0.25, 165.0)
    high = execute(
        fixture, 2.0, 0.0, 165.0,
        previous_primary=1.5, previous_kinetic=100.0,
    )
    high_mode = execute(
        fixture, 2.0, 0.25, 165.0,
        previous_primary=1.5, previous_kinetic=100.0, mode=1,
    )
    flagged_mode = execute(
        fixture, 2.0, 0.25, 165.0, flags=0x0440,
        previous_primary=1.5, previous_kinetic=100.0, mode=1,
    )

    assert low_zero["output_bits"] == "0x41e8424f"
    assert low_suppressed == low_zero
    assert low_retained["output_bits"] == "0x42f81636"
    assert high == {
        "output_bits": "0x42f38306",
        "output": bits_float(0x42F38306),
        "stored_primary": 2.0,
        "stored_kinetic": 140.0,
    }
    assert high_mode["output_bits"] == "0x4359d631"
    assert high_mode["stored_primary"] == bits_float(0x4000FF02)
    assert high_mode["stored_kinetic"] == 142.1875
    assert flagged_mode["output_bits"] == "0x43713576"
    assert flagged_mode["stored_primary"] == high_mode["stored_primary"]
    assert flagged_mode["stored_kinetic"] == high_mode["stored_kinetic"]
    return {
        "fixture_groups": 6,
        "low_zero": low_zero,
        "low_suppressed": low_suppressed,
        "low_retained": low_retained,
        "high": high,
        "high_mode": high_mode,
        "flagged_mode": flagged_mode,
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
