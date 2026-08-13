#!/usr/bin/env python3
"""Run isolated production-Thumb fixtures for the dormant 32-byte speed smoother.

The only caller is inside the stock-disabled estimator and its zero-initialized state leaves this
helper inactive. This harness invokes the SHA-pinned function directly with synthetic Float32
values and private emulated RAM to recover status, warm-up, clamp, EMA and output-flag behavior
without accessing BLE, sensors, health storage, or a physical ring.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


SPEED_SMOOTHER = 0x0004C6DC
STATE = RAM_BASE + 0x7A00
OUTPUT = RAM_BASE + 0x7A40
UNUSED_OUTPUT = RAM_BASE + 0x7A44
FLAG_OUTPUT = RAM_BASE + 0x7A48


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def float_record(bits: int) -> dict[str, Any]:
    return {
        "bits": f"0x{bits:08x}",
        "value": struct.unpack("<f", struct.pack("<I", bits))[0],
    }


class DormantSpeedSmootherFirmwareFixture:
    def __init__(
        self,
        image: bytes,
        *,
        enabled: int = 1,
        maximum_raw_rise: float = 5,
        maximum_raw_fall: float = 4,
        maximum_output_rise: float = 3,
        maximum_output_fall: float = 2,
    ) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        state = bytearray(32)
        state[0] = enabled & 0xFF
        struct.pack_into(
            "<4f",
            state,
            0x10,
            maximum_raw_rise,
            maximum_raw_fall,
            maximum_output_rise,
            maximum_output_fall,
        )
        self.machine.uc.mem_write(STATE, bytes(state))

    def update(self, value: float, interval_milliseconds: int = 1_000) -> dict[str, Any]:
        sentinel = b"\xa5\xa5\xa5\xa5"
        self.machine.uc.mem_write(OUTPUT, sentinel)
        self.machine.uc.mem_write(UNUSED_OUTPUT, sentinel)
        self.machine.uc.mem_write(FLAG_OUTPUT, sentinel)
        self.machine.uc.reg_write(UC_ARM_REG_S0, float_bits(value))
        status = self.machine.call(
            SPEED_SMOOTHER,
            STATE,
            OUTPUT,
            UNUSED_OUTPUT,
            FLAG_OUTPUT,
            interval_milliseconds & 0xFFFF_FFFF,
        )
        state = bytes(self.machine.uc.mem_read(STATE, 32))
        return {
            "input": float_record(float_bits(value)),
            "interval_milliseconds": interval_milliseconds,
            "status": status,
            "output": float_record(struct.unpack("<I", self.machine.uc.mem_read(OUTPUT, 4))[0]),
            "unused_output_raw": bytes(
                self.machine.uc.mem_read(UNUSED_OUTPUT, 4)
            ).hex(),
            "stable_or_clamped_flag_raw": bytes(
                self.machine.uc.mem_read(FLAG_OUTPUT, 4)
            ).hex(),
            "state": {
                "enabled_raw": state[0],
                "sample_count": state[1],
                "reserved_header": state[2:4].hex(),
                "sum": float_record(struct.unpack("<I", state[4:8])[0]),
                "output": float_record(struct.unpack("<I", state[8:12])[0]),
                "previous_raw_input": float_record(struct.unpack("<I", state[12:16])[0]),
                "limits": [
                    float_record(bits) for bits in struct.unpack("<4I", state[16:32])
                ],
            },
        }


def isolated_case(
    image: bytes,
    value: float,
    *,
    enabled: int = 1,
    interval_milliseconds: int = 1_000,
    limits: tuple[float, float, float, float] = (5, 4, 3, 2),
) -> dict[str, Any]:
    fixture = DormantSpeedSmootherFirmwareFixture(
        image,
        enabled=enabled,
        maximum_raw_rise=limits[0],
        maximum_raw_fall=limits[1],
        maximum_output_rise=limits[2],
        maximum_output_fall=limits[3],
    )
    return fixture.update(value, interval_milliseconds)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    inactive = isolated_case(image, 10, enabled=0)
    noncanonical_enable = isolated_case(image, 10, enabled=2)
    interval_bounds = {
        str(interval): isolated_case(image, 10, interval_milliseconds=interval)
        for interval in (699, 700, 1_000, 1_300, 1_301)
    }
    invalid_limits = {
        str(index): isolated_case(
            image,
            10,
            limits=tuple(0 if current == index else value for current, value in enumerate((5, 4, 3, 2))),
        )
        for index in range(4)
    }

    warmup_fixture = DormantSpeedSmootherFirmwareFixture(image)
    warmup = [
        warmup_fixture.update(value)
        for value in (10, 20, 40, 0, 50, 60, 70, 80, 90, 100)
    ]
    first_ema = warmup_fixture.update(110)

    wide_fixture = DormantSpeedSmootherFirmwareFixture(
        image,
        maximum_raw_rise=100,
        maximum_raw_fall=100,
        maximum_output_rise=100,
        maximum_output_fall=100,
    )
    regular_change = [wide_fixture.update(value) for value in (10, 20)]
    stable = wide_fixture.update(15)

    exact_raw_boundaries_fixture = DormantSpeedSmootherFirmwareFixture(image)
    exact_raw_boundaries = [
        exact_raw_boundaries_fixture.update(value) for value in (10, 20, 25, 21)
    ]
    nan_input = isolated_case(image, math.nan)
    nan_limit = isolated_case(image, 10, limits=(math.nan, 4, 3, 2))

    assert inactive["status"] == 0x1389
    assert noncanonical_enable["status"] == 0x1389
    assert inactive["output"]["bits"] == "0xa5a5a5a5"
    assert inactive["stable_or_clamped_flag_raw"] == "a5a5a5a5"
    assert [interval_bounds[str(value)]["status"] for value in (699, 700, 1_000, 1_300, 1_301)] == [
        0x138A, 0xFFFF_FFFF, 0xFFFF_FFFF, 0xFFFF_FFFF, 0x138A,
    ]
    assert all(item["status"] == 0x138B for item in invalid_limits.values())
    assert [item["state"]["sample_count"] for item in warmup] == list(range(1, 11))
    assert first_ema["state"]["sample_count"] == 10
    assert all(item["unused_output_raw"] == "a5a5a5a5" for item in warmup)
    assert regular_change[0]["stable_or_clamped_flag_raw"] == "01a5a5a5"
    assert regular_change[1]["stable_or_clamped_flag_raw"] == "00a5a5a5"
    assert stable["stable_or_clamped_flag_raw"] == "01a5a5a5"
    assert exact_raw_boundaries[2]["state"]["previous_raw_input"]["bits"] == "0x41c80000"
    assert exact_raw_boundaries[3]["state"]["previous_raw_input"]["bits"] == "0x41a80000"
    assert nan_input["status"] == 0xFFFF_FFFF
    assert nan_limit["status"] == 0xFFFF_FFFF

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "function": f"0x{SPEED_SMOOTHER:08x}",
        "constants": {
            "warmup_samples": 10,
            "ema_input_weight_bits": "0x3eb33333",
            "ema_previous_weight_bits": "0x3f266666",
        },
        "inactive": inactive,
        "noncanonical_enable": noncanonical_enable,
        "interval_bounds": interval_bounds,
        "invalid_limits": invalid_limits,
        "warmup": warmup,
        "first_ema": first_ema,
        "regular_change": regular_change,
        "stable": stable,
        "exact_raw_boundaries": exact_raw_boundaries,
        "nan_input": nan_input,
        "nan_limit": nan_limit,
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
