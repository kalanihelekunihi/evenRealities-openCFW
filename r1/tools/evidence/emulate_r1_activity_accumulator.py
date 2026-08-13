#!/usr/bin/env python3
"""Run isolated production-Thumb fixtures for the R1 daily activity accumulator.

The harness maps the SHA-pinned application and private emulated RAM only. It invokes the pointer
initializer and pure accumulator with synthetic caller-owned values; it has no BLE, sensor, flash,
health-store, or device access.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path
from typing import Any

from emulate_r1_step_accumulator import IMAGE_SHA256, RAM_BASE, StepFirmwareFixture, f32, u32


POINTER_INITIALIZER = 0x000720C8
ACCUMULATOR = 0x00061274
WRAPPER = RAM_BASE + 0x5000
STATE = RAM_BASE + 0x5100
UNIX_SECONDS = RAM_BASE + 0x5200
TIMEZONE = RAM_BASE + 0x5210
STEP_DELTA = RAM_BASE + 0x5220
ENERGY = RAM_BASE + 0x5300
SPEED = RAM_BASE + 0x5400
OUTPUT = RAM_BASE + 0x5500


def f32_bytes(value: float) -> bytes:
    return struct.pack("<f", value)


class ActivityFirmwareFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = StepFirmwareFixture(image)
        self.machine.uc.mem_write(WRAPPER, b"\x00" * 4)
        self.machine.uc.mem_write(STATE, b"\x00" * 52)
        self.machine.call(POINTER_INITIALIZER, WRAPPER, STATE)

    def update(
        self,
        *,
        unix_seconds: int,
        timezone_offset_minutes: int,
        step_delta: float,
        total_kcal: float,
        active_kcal: float,
        selected_speed: float,
        output_fill: int = 0xA5,
    ) -> dict[str, Any]:
        if not 0 <= unix_seconds <= 0xFFFFFFFF:
            raise ValueError("unix_seconds must fit UInt32")
        if not -0x8000 <= timezone_offset_minutes <= 0x7FFF:
            raise ValueError("timezone_offset_minutes must fit Int16")
        self.machine.uc.mem_write(UNIX_SECONDS, struct.pack("<I", unix_seconds))
        self.machine.uc.mem_write(TIMEZONE, struct.pack("<h", timezone_offset_minutes))
        self.machine.uc.mem_write(STEP_DELTA, f32_bytes(step_delta))
        energy = bytearray(44)
        energy[0:4] = f32_bytes(total_kcal)
        energy[40:44] = f32_bytes(active_kcal)
        self.machine.uc.mem_write(ENERGY, bytes(energy))
        self.machine.uc.mem_write(SPEED, f32_bytes(selected_speed))
        self.machine.uc.mem_write(OUTPUT, bytes([output_fill]) * 44)
        self.machine.call(
            ACCUMULATOR,
            WRAPPER,
            1,
            UNIX_SECONDS,
            TIMEZONE,
            STEP_DELTA,
            ENERGY,
            SPEED,
            OUTPUT,
        )
        state = bytes(self.machine.uc.mem_read(STATE, 52))
        output = bytes(self.machine.uc.mem_read(OUTPUT, 44))
        return {
            "input": {
                "unix_seconds": unix_seconds,
                "timezone_offset_minutes": timezone_offset_minutes,
                "step_delta_bits": f"0x{u32(f32_bytes(step_delta)):08x}",
                "total_kcal_bits": f"0x{u32(f32_bytes(total_kcal)):08x}",
                "active_kcal_bits": f"0x{u32(f32_bytes(active_kcal)):08x}",
                "selected_speed_bits": f"0x{u32(f32_bytes(selected_speed)):08x}",
            },
            "state": {
                "local_day_index": u32(state[0:4]),
                "timezone_offset_sign_extended": struct.unpack("<i", state[4:8])[0],
                "cumulative_step_float_bits": f"0x{u32(state[8:12]):08x}",
                "cumulative_active_kcal_float_bits": f"0x{u32(state[12:16]):08x}",
                "cumulative_all_kcal_float_bits": f"0x{u32(state[16:20]):08x}",
                "distance_float_bits": f"0x{u32(state[20:24]):08x}",
                "reserved_tail": list(state[24:52]),
            },
            "output": {
                "steps_signed": struct.unpack("<i", output[0:4])[0],
                "all_kcal_signed": struct.unpack("<i", output[4:8])[0],
                "active_kcal_signed": struct.unpack("<i", output[8:12])[0],
                "distance_bits": f"0x{u32(output[12:16]):08x}",
                "tail": list(output[16:44]),
            },
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()
    fixture = ActivityFirmwareFixture(image)
    day = 20_000
    base = day * 86_400 + 12 * 3_600
    ordinary = [
        fixture.update(
            unix_seconds=base,
            timezone_offset_minutes=-360,
            step_delta=1.5,
            total_kcal=2.75,
            active_kcal=1.25,
            selected_speed=3.6,
        ),
        fixture.update(
            unix_seconds=base + 1,
            timezone_offset_minutes=-360,
            step_delta=2.75,
            total_kcal=3.5,
            active_kcal=2.5,
            selected_speed=7.2,
        ),
        fixture.update(
            unix_seconds=base + 2,
            timezone_offset_minutes=-300,
            step_delta=-1.0,
            total_kcal=math.nan,
            active_kcal=-2.0,
            selected_speed=-1.0,
        ),
    ]
    next_day = fixture.update(
        unix_seconds=base + 86_400,
        timezone_offset_minutes=-300,
        step_delta=4.75,
        total_kcal=5.75,
        active_kcal=2.25,
        selected_speed=10.8,
    )
    infinity = fixture.update(
        unix_seconds=base + 86_401,
        timezone_offset_minutes=-300,
        step_delta=math.inf,
        total_kcal=math.inf,
        active_kcal=math.inf,
        selected_speed=math.inf,
    )

    underflow = ActivityFirmwareFixture(image).update(
        unix_seconds=0,
        timezone_offset_minutes=-1,
        step_delta=0.0,
        total_kcal=0.0,
        active_kcal=0.0,
        selected_speed=0.0,
    )
    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "ordinary_sequence": ordinary,
        "next_day_reset": next_day,
        "positive_infinity": infinity,
        "unsigned_local_time_underflow": underflow,
    }, indent=2))


if __name__ == "__main__":
    main()
