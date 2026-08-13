#!/usr/bin/env python3
"""Run production R1 Thumb step-accumulator fixtures in an isolated emulator.

This is a read-only validation helper for application 2.2.6.0009. It executes only the stock
initializer and cadence-to-step accumulator against private emulated RAM; it neither connects to
Bluetooth nor changes a ring. Unicorn is intentionally optional and is not a runtime dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_C1_C0_2,
    UC_ARM_REG_FPEXC,
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_SP,
)


IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
LOAD_BASE = 0x00027000
FLASH_MAP_BASE = 0x00020000
RAM_BASE = 0x20000000
RAM_SIZE = 0x00040000
STATE = RAM_BASE + 0x1000
MOTION_RECORD = RAM_BASE + 0x1100
OUTPUT = RAM_BASE + 0x1200
STACK = RAM_BASE + 0x30000
RETURN_SENTINEL = RAM_BASE + 0x3F000

INITIALIZER = 0x00071D9E
ACCUMULATOR = 0x00061198
LOG_FUNCTION = 0x000823D8


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def u32(data: bytes) -> int:
    return struct.unpack("<I", data)[0]


def f32(data: bytes) -> float:
    return struct.unpack("<f", data)[0]


class StepFirmwareFixture:
    def __init__(self, image: bytes) -> None:
        digest = hashlib.sha256(image).hexdigest()
        if digest != IMAGE_SHA256:
            raise ValueError(f"unexpected image SHA-256: {digest}")

        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        flash_end = align_up(LOAD_BASE + len(image), 0x1000)
        self.uc.mem_map(FLASH_MAP_BASE, flash_end - FLASH_MAP_BASE)
        self.uc.mem_write(LOAD_BASE, image)
        self.uc.mem_map(RAM_BASE, RAM_SIZE)
        self.uc.reg_write(UC_ARM_REG_C1_C0_2, 0x00F00000)
        self.uc.reg_write(UC_ARM_REG_FPEXC, 0x40000000)
        self.uc.hook_add(UC_HOOK_CODE, self._hook_code)
        self.call(INITIALIZER, STATE)

    def _hook_code(self, uc: Uc, address: int, _size: int, _user_data: object) -> None:
        # The post-result diagnostic logger does not affect accumulator state. Returning from it
        # avoids emulating unrelated RTOS/serial machinery while retaining all production math.
        if address == LOG_FUNCTION:
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def call(self, address: int, *arguments: int) -> None:
        stack = STACK
        self.uc.reg_write(UC_ARM_REG_SP, stack)
        registers = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3]
        for index, register in enumerate(registers):
            self.uc.reg_write(register, arguments[index] if index < len(arguments) else 0)
        for index, argument in enumerate(arguments[4:]):
            self.uc.mem_write(stack + index * 4, struct.pack("<I", argument))
        self.uc.reg_write(UC_ARM_REG_LR, RETURN_SENTINEL | 1)
        self.uc.emu_start(address | 1, RETURN_SENTINEL)

    def update(self, cadence: int, elapsed_seconds: int) -> dict[str, Any]:
        if not 0 <= cadence <= 0xFF:
            raise ValueError("cadence must fit UInt8")
        if not 0 <= elapsed_seconds <= 0xFFFFFFFF:
            raise ValueError("elapsed_seconds must fit UInt32")
        self.uc.mem_write(MOTION_RECORD, bytes((0, 0, cadence)))
        self.uc.mem_write(OUTPUT, b"\x00" * 4)
        self.call(ACCUMULATOR, STATE, elapsed_seconds, MOTION_RECORD, 0, OUTPUT)
        state = bytes(self.uc.mem_read(STATE, 0x1C))
        output = bytes(self.uc.mem_read(OUTPUT, 4))
        return {
            "cadence": cadence,
            "elapsed_seconds": elapsed_seconds,
            "emitted_step_delta": f32(output),
            "emitted_step_delta_bits": f"0x{u32(output):08x}",
            "pending_step_delta": f32(state[4:8]),
            "pending_step_delta_bits": f"0x{u32(state[4:8]):08x}",
            "consecutive_nonzero_updates": u32(state[8:12]),
            "consecutive_zero_updates": u32(state[12:16]),
            "emission_threshold": u32(state[16:20]),
            "cadence_history": list(state[20:25]),
        }


def run_sequence(image: bytes, sequence: list[tuple[int, int]]) -> list[dict[str, Any]]:
    fixture = StepFirmwareFixture(image)
    return [fixture.update(cadence, elapsed) for cadence, elapsed in sequence]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()
    fixtures = {
        "steady_100": run_sequence(image, [(100, 1)] * 6),
        "one_missing_update": run_sequence(image, [(100, 1), (0, 1)] + [(100, 1)] * 5),
        "two_missing_updates": run_sequence(
            image, [(100, 1), (0, 1), (0, 1)] + [(100, 1)] * 5
        ),
        "elapsed_3_then_4": run_sequence(image, [(120, 3)] * 5 + [(120, 4)]),
    }
    print(json.dumps({"image_sha256": IMAGE_SHA256, "fixtures": fixtures}, indent=2))


if __name__ == "__main__":
    main()
