#!/usr/bin/env python3
"""Run isolated production-Thumb fixtures for the R1 heart-rate selector.

The harness maps only the SHA-pinned application and private emulated RAM. It invokes the
one-byte initializer and selector with synthetic caller-owned Float32 values; it has no BLE,
sensor, flash-write, health-store, or physical-device access.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


INITIALIZER = 0x0007170A
SELECTOR = 0x000605DC
STATE = RAM_BASE + 0x6000
DIRECT = RAM_BASE + 0x6100
ESTIMATED = RAM_BASE + 0x6200
OUTPUT = RAM_BASE + 0x6300


def bits_float(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits))[0]


def describe_float(raw: bytes) -> dict[str, Any]:
    bits = struct.unpack("<I", raw)[0]
    value = bits_float(bits)
    return {
        "bits": f"0x{bits:08x}",
        "value": value if math.isfinite(value) else str(value),
    }


class HeartRateSelectorFirmwareFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.machine.uc.mem_write(STATE, b"\xa5")
        self.initializer_return = self.machine.call(INITIALIZER, STATE)
        self.initialized_state = self.machine.uc.mem_read(STATE, 1)[0]

    def select(
        self,
        *,
        direct_bits: int,
        estimated_bits: int,
        estimated_quality_bits: int,
        state: int = 0,
        elapsed_seconds: int = 1,
    ) -> dict[str, Any]:
        self.machine.uc.mem_write(STATE, bytes([state]))
        self.machine.uc.mem_write(DIRECT, struct.pack("<I", direct_bits))
        self.machine.uc.mem_write(
            ESTIMATED,
            struct.pack("<II", estimated_bits, estimated_quality_bits),
        )
        self.machine.uc.mem_write(OUTPUT, b"\xa5" * 12)
        return_code = self.machine.call(
            SELECTOR,
            STATE,
            elapsed_seconds,
            DIRECT,
            ESTIMATED,
            OUTPUT,
        )
        raw = bytes(self.machine.uc.mem_read(OUTPUT, 12))
        return {
            "return_code": return_code,
            "selected_heart_rate": describe_float(raw[0:4]),
            "quality": describe_float(raw[4:8]),
            "source_code": raw[8],
            "untouched_tail": list(raw[9:12]),
            "state_after": self.machine.uc.mem_read(STATE, 1)[0],
        }


def f32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    fixture = HeartRateSelectorFirmwareFixture(args.image.read_bytes())

    forty = f32_bits(40.0)
    two_forty = f32_bits(240.0)
    direct = f32_bits(72.0)
    estimated = f32_bits(81.5)
    quality = f32_bits(0.375)
    cases = {
        "direct_preferred": fixture.select(
            direct_bits=direct,
            estimated_bits=estimated,
            estimated_quality_bits=quality,
        ),
        "nonzero_state_disables_direct": fixture.select(
            state=1,
            direct_bits=direct,
            estimated_bits=estimated,
            estimated_quality_bits=quality,
        ),
        "lower_boundary_inclusive": fixture.select(
            direct_bits=forty,
            estimated_bits=estimated,
            estimated_quality_bits=quality,
        ),
        "one_float_below_lower_boundary": fixture.select(
            direct_bits=forty - 1,
            estimated_bits=estimated,
            estimated_quality_bits=quality,
        ),
        "upper_boundary_inclusive": fixture.select(
            direct_bits=two_forty,
            estimated_bits=estimated,
            estimated_quality_bits=quality,
        ),
        "one_float_above_upper_boundary": fixture.select(
            direct_bits=two_forty + 1,
            estimated_bits=estimated,
            estimated_quality_bits=quality,
        ),
        "both_invalid": fixture.select(
            direct_bits=f32_bits(39.0),
            estimated_bits=f32_bits(241.0),
            estimated_quality_bits=quality,
        ),
        "nan_and_infinity": fixture.select(
            direct_bits=0x7FC00000,
            estimated_bits=0x7F800000,
            estimated_quality_bits=0x7FC12345,
        ),
        "elapsed_argument_is_ignored": fixture.select(
            state=1,
            elapsed_seconds=0xFFFF_FFFF,
            direct_bits=direct,
            estimated_bits=estimated,
            estimated_quality_bits=0xDEAD_BEEF,
        ),
    }

    assert fixture.initializer_return == 0
    assert fixture.initialized_state == 0
    assert cases["direct_preferred"]["return_code"] == 0
    assert cases["direct_preferred"]["quality"]["bits"] == "0x3f800000"
    assert cases["nonzero_state_disables_direct"]["return_code"] == 1
    assert cases["nonzero_state_disables_direct"]["quality"]["bits"] == "0x3ec00000"
    assert cases["lower_boundary_inclusive"]["return_code"] == 0
    assert cases["one_float_below_lower_boundary"]["return_code"] == 1
    assert cases["upper_boundary_inclusive"]["return_code"] == 0
    assert cases["one_float_above_upper_boundary"]["return_code"] == 1
    assert cases["both_invalid"]["return_code"] == 0x40
    assert cases["nan_and_infinity"]["return_code"] == 0x40
    assert cases["elapsed_argument_is_ignored"]["quality"]["bits"] == "0xdeadbeef"
    assert all(case["untouched_tail"] == [0xA5, 0xA5, 0xA5] for case in cases.values())

    print(json.dumps({
        "initializer": {
            "function": f"0x{INITIALIZER:08x}",
            "return_code": fixture.initializer_return,
            "state_byte": fixture.initialized_state,
        },
        "selector_function": f"0x{SELECTOR:08x}",
        "cases": cases,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "flash_writes": False,
            "health_store_access": False,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
