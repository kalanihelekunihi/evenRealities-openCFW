#!/usr/bin/env python3
"""Run production R1 locomotion-window fixtures in isolated emulated RAM.

The helper executes application 2.2.6.0009 functions 0x710d4 and 0x5ed14 only. It has no BLE,
sensor, storage, or device access and exists to validate the bounded Swift reconstruction against
the original Thumb arithmetic and state layout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_C1_C0_2,
    UC_ARM_REG_FPEXC,
    UC_ARM_REG_LR,
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
RAM_SIZE = 0x00080000
STATE = RAM_BASE + 0x1000
INPUT = RAM_BASE + 0x2000
AXIS_X = RAM_BASE + 0x2100
AXIS_Y = RAM_BASE + 0x2200
AXIS_Z = RAM_BASE + 0x2300
OUTPUT = RAM_BASE + 0x2400
DIRECT_HISTORY = RAM_BASE + 0x2500
DIRECT_OUTPUT = RAM_BASE + 0x2800
DIRECT_COUNTS = RAM_BASE + 0x2900
DIRECT_SHAPE = RAM_BASE + 0x2910
STACK = RAM_BASE + 0x70000
RETURN_SENTINEL = RAM_BASE + 0x7F000

INITIALIZER = 0x000710D4
PREPROCESSOR = 0x0005ED14
AUTOCORRELATION = 0x0005C5F0
CROSSING_WRAPPER = 0x00056CF4

ARRAY_OFFSETS = {
    "x_std": 0x002,
    "z_mean": 0x012,
    "magnitude_std": 0x022,
    "magnitude_mean": 0x032,
    "magnitude_range": 0x042,
    "x_mean": 0x1E4,
    "y_mean": 0x1F4,
    "y_std": 0x204,
    "z_std": 0x214,
    "magnitude_mean_absolute_difference": 0x224,
    "x_mean_absolute_difference": 0x234,
    "y_mean_absolute_difference": 0x244,
    "z_mean_absolute_difference": 0x254,
}


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def unpack_i16s(data: bytes) -> list[int]:
    return list(struct.unpack("<" + "h" * (len(data) // 2), data))


class LocomotionFirmwareFixture:
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
        self.call(INITIALIZER, STATE)

    def call(self, address: int, *arguments: int) -> int:
        self.uc.reg_write(UC_ARM_REG_SP, STACK)
        for register, argument in zip(
            (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), arguments
        ):
            self.uc.reg_write(register, argument)
        for index, argument in enumerate(arguments[4:]):
            self.uc.mem_write(STACK + index * 4, struct.pack("<I", argument))
        self.uc.reg_write(UC_ARM_REG_LR, RETURN_SENTINEL | 1)
        self.uc.emu_start(address | 1, RETURN_SENTINEL)
        return self.uc.reg_read(UC_ARM_REG_R0)

    def autocorrelation(self, magnitudes: list[int]) -> dict[str, Any]:
        if len(magnitudes) != 100 or any(not 0 <= value <= 0xFFFF for value in magnitudes):
            raise ValueError("autocorrelation input must be 100 UInt16 magnitudes")
        self.uc.mem_write(DIRECT_HISTORY, struct.pack("<100H", *magnitudes))
        # Wrapper 0x56d78 initializes fields 8/10 to -1 and fields 11...13 to zero.
        self.uc.mem_write(
            DIRECT_OUTPUT,
            struct.pack("<5I", 0xBF800000, 0xBF800000, 0, 0, 0),
        )
        self.uc.mem_write(DIRECT_COUNTS, b"\x00\x00")
        self.uc.mem_write(DIRECT_SHAPE, b"\x00" * 8)
        self.call(
            AUTOCORRELATION,
            DIRECT_HISTORY,
            DIRECT_OUTPUT,
            DIRECT_OUTPUT + 4,
            DIRECT_OUTPUT + 8,
            DIRECT_OUTPUT + 12,
            DIRECT_OUTPUT + 16,
            DIRECT_COUNTS,
            DIRECT_SHAPE,
        )
        output = bytes(self.uc.mem_read(DIRECT_OUTPUT, 20))
        shape = bytes(self.uc.mem_read(DIRECT_SHAPE, 8))
        return {
            "input_head": magnitudes[:12],
            "output_float32_bits": [
                f"0x{value:08x}" for value in struct.unpack("<5I", output)
            ],
            "output_float32": list(struct.unpack("<5f", output)),
            "turning_counts": list(self.uc.mem_read(DIRECT_COUNTS, 2)),
            "shape_float32_bits": [
                f"0x{value:08x}" for value in struct.unpack("<2I", shape)
            ],
            "shape_float32": list(struct.unpack("<2f", shape)),
        }

    def crossing(self, magnitudes: list[int], baseline: int) -> dict[str, Any]:
        if len(magnitudes) != 200 or any(not 0 <= value <= 0xFFFF for value in magnitudes):
            raise ValueError("crossing input must be 200 UInt16 magnitudes")
        if not -0x8000 <= baseline <= 0x7FFF:
            raise ValueError("baseline must fit Int16")
        self.uc.mem_write(STATE, b"\x00" * 0x26E)
        self.uc.mem_write(STATE + 0x32, struct.pack("<8h", *([baseline] * 8)))
        self.uc.mem_write(STATE + 0x52, b"\x00")
        self.uc.mem_write(DIRECT_HISTORY, struct.pack("<200H", *magnitudes))
        self.uc.mem_write(DIRECT_OUTPUT, b"\x00" * 8)
        self.call(
            CROSSING_WRAPPER,
            STATE,
            DIRECT_HISTORY,
            DIRECT_OUTPUT,
            DIRECT_OUTPUT + 4,
        )
        output = bytes(self.uc.mem_read(DIRECT_OUTPUT, 8))
        return {
            "mode_2_float32_bits": f"0x{struct.unpack('<I', output[:4])[0]:08x}",
            "mode_1_float32_bits": f"0x{struct.unpack('<I', output[4:])[0]:08x}",
            "mode_2": struct.unpack("<f", output[:4])[0],
            "mode_1": struct.unpack("<f", output[4:])[0],
        }

    def update(
        self,
        axes: tuple[list[float], list[float], list[float]] | None,
        elapsed_seconds: int,
    ) -> dict[str, Any]:
        if axes is None:
            self.uc.mem_write(INPUT, struct.pack("<III", AXIS_X, AXIS_Y, AXIS_Z) + b"\x01")
        else:
            if any(len(axis) != 25 for axis in axes):
                raise ValueError("each axis must contain 25 Float32 values")
            for address, axis in zip((AXIS_X, AXIS_Y, AXIS_Z), axes):
                self.uc.mem_write(address, struct.pack("<25f", *axis))
            self.uc.mem_write(INPUT, struct.pack("<III", AXIS_X, AXIS_Y, AXIS_Z) + b"\x00")
        self.uc.mem_write(OUTPUT, b"\x00" * 64)
        return_code = self.call(PREPROCESSOR, STATE, elapsed_seconds, INPUT, OUTPUT)
        state = bytes(self.uc.mem_read(STATE, 0x26E))
        output = bytes(self.uc.mem_read(OUTPUT, 62))
        output_bits = [f"0x{value:08x}" for value in struct.unpack("<14I", output[:56])]
        return {
            "return_code": return_code,
            "missing_magnitude_mean_slots": state[0],
            "circular_index": state[0x52],
            "summary_arrays": {
                name: unpack_i16s(state[offset : offset + 16])
                for name, offset in ARRAY_OFFSETS.items()
            },
            "magnitude_history_head": unpack_i16s(state[0x54 : 0x54 + 24]),
            "magnitude_history_tail": unpack_i16s(state[0x54 + 376 : 0x54 + 400]),
            "detector_history": unpack_i16s(state[0x264 : 0x26E]),
            "output_float32_bits": output_bits,
            "output_flags": list(output[56:62]),
        }


def fixture_axes(update: int) -> tuple[list[float], list[float], list[float]]:
    return (
        [float(1000 + update * 100 + index * 7) for index in range(25)],
        [float(-300 + update * 20 + index * 3) for index in range(25)],
        [float(200 - update * 10 - index * 2) for index in range(25)],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    steady = LocomotionFirmwareFixture(image)
    steady_updates = [steady.update(fixture_axes(index), 1) for index in range(5)]

    gaps = LocomotionFirmwareFixture(image)
    gap_updates = [gaps.update(fixture_axes(index), 1) for index in range(4)]
    gap_updates.append(gaps.update(fixture_axes(4), 2))
    gap_updates.append(gaps.update(None, 1))
    gap_updates.append(gaps.update(fixture_axes(5), 9))

    assert [item["return_code"] for item in steady_updates] == [0] * 5
    assert [item["missing_magnitude_mean_slots"] for item in steady_updates] == [
        7, 6, 5, 4, 3
    ]
    assert [item["circular_index"] for item in steady_updates] == [1, 2, 3, 4, 5]
    assert steady_updates[0]["magnitude_history_tail"] == [
        1135, 1140, 1146, 1152, 1158, 1164,
        1170, 1175, 1181, 1187, 1193, 1199,
    ]
    assert steady_updates[0]["output_flags"] == [255] * 6
    assert steady_updates[3]["output_flags"] == [1, 255, 1, 255, 255, 255]
    assert [item["return_code"] for item in gap_updates[-3:]] == [0, 1, 1]
    assert gap_updates[-2]["circular_index"] == 7
    assert gap_updates[-2]["magnitude_history_tail"] == [
        1495, 1488, 1482, 1476, 1469, 1463,
        1457, 1451, 1444, 1438, 1432, 1426,
    ]
    assert gap_updates[-1]["missing_magnitude_mean_slots"] == 8
    assert gap_updates[-1]["circular_index"] == 0
    assert gap_updates[-1]["magnitude_history_tail"] == [0] * 12

    direct = LocomotionFirmwareFixture(image)
    autocorrelation = {}
    for period in (12, 15, 20, 25, 30, 35):
        values = [
            int(1_500 + 800 * math.sin(2 * math.pi * index / period))
            for index in range(100)
        ]
        autocorrelation[f"sine_period_{period}"] = direct.autocorrelation(values)
    autocorrelation["alternating_10"] = direct.autocorrelation([
        700 if (index // 5) % 2 == 0 else 2_300 for index in range(100)
    ])
    crossing = {}
    for period in range(8, 56):
        values = [
            int(1_500 + 800 * math.sin(2 * math.pi * index / period))
            for index in range(200)
        ]
        crossing[f"sine_period_{period}"] = direct.crossing(values, 1_500)

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "steady": steady_updates,
        "gap_invalid_reset": gap_updates,
        "autocorrelation": autocorrelation,
        "crossing": crossing,
    }, indent=2))


if __name__ == "__main__":
    main()
