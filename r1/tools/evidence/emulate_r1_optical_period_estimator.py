#!/usr/bin/env python3
"""Execute isolated production-Thumb optical-period estimator fixtures."""

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
    UC_ARM_REG_R3,
    UC_ARM_REG_SP,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


ESTIMATOR = 0x00069834
INITIALIZE = 0x00071DD8
SHIFT = 0x000948D8
EXTREMA = 0x000647C4
PEAK_MATCH = 0x00064380
INTERVAL_MERGE = 0x0004857C
CONTROL_EXTRACT = 0x00056DC0
FEATURE_REDUCE = 0x00068840

STATE = RAM_BASE + 0x58000
INPUT = RAM_BASE + 0x59000
INPUT_RECORD = INPUT + 0x100
OUTPUT = RAM_BASE + 0x59200


def bits(address_data: bytes) -> list[str]:
    return [f"0x{word:08x}" for word in struct.unpack("<2I", address_data)]


def initialize(machine: LocomotionFirmwareFixture) -> None:
    machine.uc.mem_write(STATE, b"\x00" * 0x6C8)
    machine.call(INITIALIZE, STATE, 0, 0, 0)
    machine.uc.mem_write(INPUT_RECORD, struct.pack("<I", INPUT))


def call(machine: LocomotionFirmwareFixture, elapsed: int, flags: int) -> dict[str, Any]:
    machine.uc.mem_write(OUTPUT, b"\xA5" * 8)
    status = machine.call(
        ESTIMATOR, STATE, elapsed, INPUT_RECORD, flags, OUTPUT, OUTPUT + 4
    )
    output = bytes(machine.uc.mem_read(OUTPUT, 8))
    return {
        "status": status,
        "output_bits": bits(output),
        "current_window": struct.unpack(
            "<I", bytes(machine.uc.mem_read(STATE + 0x54, 4))
        )[0],
        "interval_count": machine.uc.mem_read(STATE + 0x51, 1)[0],
        "cooldown": machine.uc.mem_read(STATE + 0x50, 1)[0],
        "tolerance_bits": bits(bytes(machine.uc.mem_read(STATE + 0x6C0, 8))),
    }


class SelectionFixture:
    def __init__(
        self,
        image: bytes,
        mode1: tuple[float, float],
        mode2: tuple[float, float],
        fallback: tuple[float, float],
    ) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        initialize(self.machine)
        self.mode1 = mode1
        self.mode2 = mode2
        self.fallback = fallback
        self.control_modes: list[int] = []
        self.fallback_calls = 0
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        stack = uc.reg_read(UC_ARM_REG_SP)
        if address == SHIFT:
            self._return(uc)
        elif address == EXTREMA:
            maxima_count, minima_count = struct.unpack(
                "<II", bytes(uc.mem_read(stack + 8, 8))
            )
            uc.mem_write(maxima_count, b"\x04")
            uc.mem_write(minima_count, b"\x04")
            self._return(uc)
        elif address == PEAK_MATCH:
            reference_count = struct.unpack(
                "<I", bytes(uc.mem_read(stack, 4))
            )[0]
            median_output = struct.unpack(
                "<I", bytes(uc.mem_read(stack + 4, 4))
            )[0]
            uc.mem_write(uc.reg_read(UC_ARM_REG_R3), b"\x04")
            uc.mem_write(reference_count, b"\x04")
            uc.mem_write(median_output, struct.pack("<f", 50.0))
            self._return(uc)
        elif address == INTERVAL_MERGE:
            mean_output = struct.unpack(
                "<I", bytes(uc.mem_read(stack, 4))
            )[0]
            uc.mem_write(STATE + 0x51, b"\x04")
            uc.mem_write(mean_output, struct.pack("<f", 1.0))
            self._return(uc)
        elif address == CONTROL_EXTRACT:
            primary, secondary, mode = struct.unpack(
                "<III", bytes(uc.mem_read(stack + 4, 12))
            )
            selected = self.mode1 if mode == 1 else self.mode2
            uc.mem_write(primary, struct.pack("<f", selected[0]))
            uc.mem_write(secondary, struct.pack("<f", selected[1]))
            self.control_modes.append(mode)
            self._return(uc)
        elif address == FEATURE_REDUCE:
            primary, secondary = struct.unpack(
                "<II", bytes(uc.mem_read(stack, 8))
            )
            uc.mem_write(primary, struct.pack("<f", self.fallback[0]))
            uc.mem_write(secondary, struct.pack("<f", self.fallback[1]))
            self.fallback_calls += 1
            self._return(uc)

    def run(self) -> dict[str, Any]:
        self.machine.uc.mem_write(STATE + 0x54, struct.pack("<I", 9))
        self.machine.uc.mem_write(INPUT, b"\x00" * 100)
        result = call(self.machine, 0, 0)
        result["control_modes"] = self.control_modes
        result["fallback_calls"] = self.fallback_calls
        return result


def run(image: bytes) -> dict[str, Any]:
    warmup_machine = LocomotionFirmwareFixture(image)
    initialize(warmup_machine)
    warmup_machine.uc.mem_write(INPUT, b"\x00" * 100)
    warmup = [call(warmup_machine, 0, 0) for _ in range(10)]
    assert [item["status"] for item in warmup] == [1] * 10
    assert [item["current_window"] for item in warmup] == list(range(1, 11))
    assert all(item["output_bits"] == ["0xbf800000", "0x00000000"] for item in warmup)
    assert warmup[-1]["tolerance_bits"] == ["0xbf400000", "0xbf400000"]

    gap_machine = LocomotionFirmwareFixture(image)
    initialize(gap_machine)
    gap_machine.uc.mem_write(INPUT, struct.pack("<25f", *map(float, range(25))))
    gap = call(gap_machine, 3, 0)
    assert gap == {
        "status": 1,
        "output_bits": ["0xbf800000", "0x00000000"],
        "current_window": 3,
        "interval_count": 0,
        "cooldown": 9,
        "tolerance_bits": ["0xbf800000", "0xbf800000"],
    }
    reset = call(gap_machine, 21, 0x40)
    assert reset["status"] == 1
    assert reset["current_window"] == 0
    assert reset["interval_count"] == 0
    assert reset["cooldown"] == 0
    assert reset["tolerance_bits"] == ["0xbf800000", "0xbf800000"]

    close = SelectionFixture(
        image, (12.0, 0.6), (12.5, 0.7), (15.0, 0.8)
    ).run()
    assert close["status"] == 0
    assert close["output_bits"] == ["0x41440000", "0x3f47ae14"]
    assert close["control_modes"] == [1, 2]
    assert close["fallback_calls"] == 1

    fallback = SelectionFixture(
        image, (12.0, 0.2), (16.0, 0.25), (14.0, 0.75)
    ).run()
    assert fallback["status"] == 0
    assert fallback["output_bits"] == ["0x41600000", "0x3f400000"]

    return {
        "fixture_groups": 4,
        "warmup_final": warmup[-1],
        "gap": gap,
        "reset": reset,
        "close_candidates": close,
        "fallback_override": fallback,
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
