#!/usr/bin/env python3
"""Run production-Thumb fixtures for the dormant per-iteration HR gate and carry-forward rule.

The parent estimator is stock-disabled. This harness invokes its SHA-pinned per-iteration helper
with synthetic inputs in private RAM and uses flag word zero, so no sensor, BLE, persistent state,
or physical-device interface is touched.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


PER_ITERATION = 0x000721B4
STATE = RAM_BASE + 0x7400
INPUT = RAM_BASE + 0x7800
CONFIG = RAM_BASE + 0x7900


def run_case(
    image: bytes,
    *,
    sample_index: int,
    heart_rate: int,
    validation_latch: int,
    previous_heart_rate: int,
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(STATE, bytes(0x33C))
    fixture.uc.mem_write(CONFIG, bytes(32))
    fixture.uc.mem_write(STATE + 0x20, struct.pack("<i", previous_heart_rate))
    fixture.uc.mem_write(STATE + 0x60, bytes([validation_latch & 0xFF]))
    fixture.uc.mem_write(
        INPUT,
        struct.pack(
            "<IIiffffIf",
            1_000,
            sample_index,
            heart_rate,
            0.0,
            0.0,
            0.0,
            0.0,
            CONFIG,
            0.0,
        ),
    )
    return_code = fixture.call(PER_ITERATION, STATE, INPUT)
    state = bytes(fixture.uc.mem_read(STATE, 0x33C))
    return {
        "sample_index": sample_index,
        "heart_rate": heart_rate,
        "initial_validation_latch": validation_latch,
        "initial_previous_heart_rate": previous_heart_rate,
        "return_code": return_code,
        "status": struct.unpack("<h", state[0x52:0x54])[0],
        "final_validation_latch": state[0x60],
        "selected_heart_rate": struct.unpack("<i", state[0x1C:0x20])[0],
        "final_previous_heart_rate": struct.unpack("<i", state[0x20:0x24])[0],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    cases = {
        "below_minimum": run_case(
            image, sample_index=0, heart_rate=35, validation_latch=0,
            previous_heart_rate=72,
        ),
        "minimum": run_case(
            image, sample_index=0, heart_rate=36, validation_latch=0,
            previous_heart_rate=72,
        ),
        "maximum": run_case(
            image, sample_index=0, heart_rate=249, validation_latch=0,
            previous_heart_rate=72,
        ),
        "above_maximum": run_case(
            image, sample_index=0, heart_rate=250, validation_latch=0,
            previous_heart_rate=72,
        ),
        "zero_before_latch": run_case(
            image, sample_index=1, heart_rate=0, validation_latch=0,
            previous_heart_rate=72,
        ),
        "zero_after_latch": run_case(
            image, sample_index=1, heart_rate=0, validation_latch=1,
            previous_heart_rate=72,
        ),
        "zero_at_index_thirty": run_case(
            image, sample_index=30, heart_rate=0, validation_latch=0,
            previous_heart_rate=72,
        ),
        "zero_at_index_zero_after_latch": run_case(
            image, sample_index=0, heart_rate=0, validation_latch=1,
            previous_heart_rate=72,
        ),
    }

    assert cases["below_minimum"]["status"] == -1016
    assert cases["above_maximum"]["status"] == -1016
    assert cases["minimum"]["status"] == 0
    assert cases["minimum"]["final_validation_latch"] == 1
    assert cases["minimum"]["selected_heart_rate"] == 36
    assert cases["maximum"]["selected_heart_rate"] == 249
    assert cases["zero_before_latch"]["status"] == -1016
    assert cases["zero_after_latch"]["status"] == 0
    assert cases["zero_after_latch"]["selected_heart_rate"] == 72
    assert cases["zero_at_index_thirty"]["selected_heart_rate"] == 72
    assert cases["zero_at_index_thirty"]["final_validation_latch"] == 0
    assert cases["zero_at_index_zero_after_latch"]["selected_heart_rate"] == 0

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "per_iteration_function": f"0x{PER_ITERATION:08x}",
        "cases": cases,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "firmware_execution_outside_private_emulation": False,
            "flash_writes": False,
            "health_store_access": False,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
