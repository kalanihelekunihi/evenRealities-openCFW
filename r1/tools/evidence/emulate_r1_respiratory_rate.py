#!/usr/bin/env python3
"""Assert the stock 0x60680 respiratory-rate history wrapper contract."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R3,
    UC_ARM_REG_SP,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


RESPIRATORY_RATE = 0x00060680
PERIOD_ESTIMATOR = 0x00069834
STATE = RAM_BASE + 0x58000
INPUT = RAM_BASE + 0x59000
SELECTORS = RAM_BASE + 0x59100
OUTPUT = RAM_BASE + 0x59200


class RespiratoryFixture:
    def __init__(self, image: bytes, rate: float, confidence: float,
                 estimator_result: int) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.rate = rate
        self.confidence = confidence
        self.estimator_result = estimator_result
        self.calls: list[tuple[int, int]] = []
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address != PERIOD_ESTIMATOR:
            return
        stack = uc.reg_read(UC_ARM_REG_SP)
        rate_output, confidence_output = struct.unpack(
            "<II", bytes(uc.mem_read(stack, 8))
        )
        uc.mem_write(rate_output, struct.pack("<f", self.rate))
        uc.mem_write(confidence_output, struct.pack("<f", self.confidence))
        self.calls.append((uc.reg_read(UC_ARM_REG_R1),
                           uc.reg_read(UC_ARM_REG_R3)))
        uc.reg_write(UC_ARM_REG_R0, self.estimator_result)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def run(self, elapsed: int, unavailable: bool,
            secondary: int, primary: int) -> dict[str, Any]:
        self.machine.uc.mem_write(STATE, b"\x00" * 0x200)
        self.machine.uc.mem_write(INPUT, b"\x00" * 16)
        self.machine.uc.mem_write(INPUT + 4, bytes([int(unavailable)]))
        self.machine.uc.mem_write(
            SELECTORS, bytes([0, secondary, primary, 0])
        )
        self.machine.uc.mem_write(OUTPUT, b"\xa5" * 8)
        status = self.machine.call(
            RESPIRATORY_RATE, STATE, elapsed, INPUT, SELECTORS, OUTPUT
        )
        state = bytes(self.machine.uc.mem_read(STATE, 48))
        output = bytes(self.machine.uc.mem_read(OUTPUT, 8))
        return {
            "status": status,
            "output_bits": [f"0x{x:08x}" for x in struct.unpack("<2I", output)],
            "modulo_counter": state[40],
            "primary_codes": list(state[41:45]),
            "secondary_codes": list(state[45:47]),
            "rate_history_bits": [
                f"0x{x:08x}" for x in struct.unpack("<5I", state[:20])
            ],
            "confidence_history_bits": [
                f"0x{x:08x}" for x in struct.unpack("<5I", state[20:40])
            ],
            "estimator_calls": self.calls,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    ordinary_fixture = RespiratoryFixture(image, 12.0, 1.0, 0)
    ordinary = ordinary_fixture.run(1, False, 1, 1)
    assert ordinary["status"] == 0
    assert ordinary["output_bits"] == ["0x41400000", "0x3f428f5c"]
    assert ordinary["modulo_counter"] == 1
    assert ordinary["primary_codes"] == [1, 0, 0, 0]
    assert ordinary["secondary_codes"] == [1, 0]
    assert ordinary["estimator_calls"] == [(1, 0)]

    gap_fixture = RespiratoryFixture(image, 30.0, 0.8, 1)
    gap = gap_fixture.run(3, True, 0, 0)
    assert gap["status"] == 0x78
    assert gap["output_bits"] == ["0x41c80000", "0x3efc8bc3"]
    assert gap["modulo_counter"] == 3
    assert gap["primary_codes"] == [2, 0, 0, 0]
    assert gap["secondary_codes"] == [2, 0]
    assert gap["estimator_calls"] == [(3, 0x40)]

    invalid_fixture = RespiratoryFixture(image, 0.0, 1.0, 0)
    invalid = invalid_fixture.run(1, False, 0, 0)
    assert invalid["status"] == 0x10
    assert invalid["output_bits"] == ["0xbf800000", "0x3f800000"]

    print(json.dumps({
        "function": "0x00060680",
        "ordinary": ordinary,
        "gap_unavailable_clamped": gap,
        "invalid_rate": invalid,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
