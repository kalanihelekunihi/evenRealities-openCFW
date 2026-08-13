#!/usr/bin/env python3
"""Exercise dynamics baseline helper `0x90c54` in private production-Thumb emulation."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0, UC_ARM_REG_S1

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


BASELINE = 0x00090C54
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
    input_bits: int,
    auxiliary_bits: int,
    state_first_bits: int,
    state_second_bits: int,
    flag_word: int,
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(44)
    struct.pack_into("<II", state, 0, state_first_bits, state_second_bits)
    struct.pack_into("<H", state, 0x24, flag_word)
    fixture.uc.mem_write(STATE, bytes(state))
    fixture.uc.reg_write(UC_ARM_REG_S0, input_bits)
    fixture.uc.reg_write(UC_ARM_REG_S1, auxiliary_bits)
    fixture.call(BASELINE, STATE)
    return {
        "input": float_record(input_bits),
        "auxiliary": float_record(auxiliary_bits),
        "state_first": float_record(state_first_bits),
        "state_second": float_record(state_second_bits),
        "flag_word": f"0x{flag_word:04x}",
        "output": float_record(fixture.uc.reg_read(UC_ARM_REG_S0)),
    }


def case(image: bytes, value: float, auxiliary: float, first: float, second: float, flags: int = 0) -> dict[str, Any]:
    return run_case(
        image,
        input_bits=float_bits(value),
        auxiliary_bits=float_bits(auxiliary),
        state_first_bits=float_bits(first),
        state_second_bits=float_bits(second),
        flag_word=flags,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    fixtures = {
        "negative": case(image, -1, 165, 0, 0),
        "zero_state_zero": case(image, 0, 165, 0, 0),
        "zero_state_half": case(image, 0.5, 165, 0, 0),
        "zero_state_one": case(image, 1, 165, 0, 0),
        "zero_state_two": case(image, 2, 165, 0, 0),
        "ordinary_half": case(image, 0.5, 165, 1.2, 70),
        "ordinary_one": case(image, 1, 165, 1.2, 70),
        "ordinary_two": case(image, 2, 165, 1.2, 70),
        "flagged_half": case(image, 0.5, 165, 1.2, 70, 0x0440),
        "flagged_one": case(image, 1, 165, 1.2, 70, 0x0440),
        "flagged_1_25": case(image, 1.25, 165, 1.2, 70, 0x0440),
        "flagged_above_1_25": run_case(
            image,
            input_bits=0x3FA00001,
            auxiliary_bits=float_bits(165),
            state_first_bits=float_bits(1.2),
            state_second_bits=float_bits(70),
            flag_word=0x0440,
        ),
        "flagged_two": case(image, 2, 165, 1.2, 70, 0x0440),
        "positive_nan": run_case(
            image,
            input_bits=0x7FC00000,
            auxiliary_bits=float_bits(165),
            state_first_bits=float_bits(1.2),
            state_second_bits=float_bits(70),
            flag_word=0,
        ),
        "positive_infinity": run_case(
            image,
            input_bits=0x7F800000,
            auxiliary_bits=float_bits(165),
            state_first_bits=float_bits(1.2),
            state_second_bits=float_bits(70),
            flag_word=0,
        ),
    }

    expected = {
        "negative": "0x00000000",
        "zero_state_zero": "0x00000000",
        "zero_state_half": "0x3d275463",
        "zero_state_one": "0x3da75463",
        "zero_state_two": "0x3f275463",
        "ordinary_half": "0x42519ebb",
        "ordinary_one": "0x42d19ebb",
        "ordinary_two": "0x42f03b79",
        "flagged_half": "0x427843ec",
        "flagged_one": "0x427843ec",
        "flagged_1_25": "0x4280cde6",
        "flagged_above_1_25": "0x42d7a33a",
        "flagged_two": "0x42f03b79",
        "positive_nan": "0x00000000",
        "positive_infinity": "0x4639e43d",
    }
    assert {
        name: fixture["output"]["bits"] for name, fixture in fixtures.items()
    } == expected

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "function": f"0x{BASELINE:08x}",
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
