#!/usr/bin/env python3
"""Run isolated production-Thumb fixtures for the dormant estimator's integer HR filter.

The parent estimator and this filter's own enable byte are both stock-disabled. This harness calls
the SHA-pinned helper with synthetic integers and private emulated RAM to recover its complete
status, clamp, reset, rounding and rolling-history behavior without accessing BLE, sensors, health
storage, or a physical ring.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


HEART_RATE_FILTER = 0x00070498
HEART_RATE_WRAPPER = 0x00094270
STATE_RESET = 0x0005D2EC
STATE = RAM_BASE + 0x6C00
OUTPUT = RAM_BASE + 0x6D00
CORE_STATE = RAM_BASE + 0x6E00


def float_record(bits: int) -> dict[str, Any]:
    return {
        "bits": f"0x{bits:08x}",
        "value": struct.unpack("<f", struct.pack("<I", bits))[0],
    }


class DormantHeartRateFilterFirmwareFixture:
    def __init__(self, image: bytes, *, enabled: bool) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.machine.uc.mem_write(STATE, bytes(100))
        self.machine.uc.mem_write(OUTPUT, bytes(8))
        self.machine.uc.mem_write(STATE, bytes([int(enabled)]))

    def update(self, value: int, interval_milliseconds: int = 1_000) -> dict[str, Any]:
        self.machine.uc.mem_write(OUTPUT, b"\xa5" * 8)
        status = self.machine.call(
            HEART_RATE_FILTER,
            STATE,
            value & 0xFFFF_FFFF,
            OUTPUT,
            interval_milliseconds & 0xFFFF_FFFF,
        )
        state = bytes(self.machine.uc.mem_read(STATE, 100))
        output = bytes(self.machine.uc.mem_read(OUTPUT, 8))
        return {
            "input": value,
            "interval_milliseconds": interval_milliseconds,
            "status": status,
            "output_filtered": struct.unpack("<i", output[:4])[0],
            "output_raw": struct.unpack("<i", output[4:])[0],
            "state": {
                "enabled": state[0],
                "has_seen_positive": state[1],
                "unchanged_count": state[2],
                "positive_streak": state[3],
                "history_count": state[4],
                "missing_count": struct.unpack("<I", state[8:12])[0],
                "last_effective_input": struct.unpack("<i", state[12:16])[0],
                "average": float_record(struct.unpack("<I", state[16:20])[0]),
                "history": [
                    float_record(bits)
                    for bits in struct.unpack("<20I", state[20:100])
                ],
            },
        }


def isolated_case(
    image: bytes,
    *,
    enabled: bool,
    value: int,
    interval_milliseconds: int = 1_000,
) -> dict[str, Any]:
    return DormantHeartRateFilterFirmwareFixture(image, enabled=enabled).update(
        value, interval_milliseconds
    )


def run_sequence(image: bytes, values: list[int]) -> list[dict[str, Any]]:
    fixture = DormantHeartRateFilterFirmwareFixture(image, enabled=True)
    return [fixture.update(value) for value in values]


def wrapper_case(image: bytes, *, inner_enabled: bool, value: int) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(CORE_STATE, bytes(0x33C))
    fixture.uc.mem_write(CORE_STATE + 0x278, bytes([int(inner_enabled)]))
    fixture.call(HEART_RATE_WRAPPER, CORE_STATE, 0, value & 0xFFFF_FFFF)
    state = bytes(fixture.uc.mem_read(CORE_STATE, 0x33C))
    return {
        "inner_enabled": inner_enabled,
        "input": value,
        "selected_output": struct.unpack("<i", state[0x1C:0x20])[0],
        "previous_output": struct.unpack("<i", state[0x20:0x24])[0],
        "inner_state_enabled": state[0x278],
    }


def wrapper_sequence(
    image: bytes, *, inner_enabled: bool, values: list[int]
) -> list[dict[str, Any]]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(CORE_STATE, bytes(0x33C))
    fixture.uc.mem_write(CORE_STATE + 0x278, bytes([int(inner_enabled)]))
    results = []
    for index, value in enumerate(values):
        fixture.call(HEART_RATE_WRAPPER, CORE_STATE, index, value & 0xFFFF_FFFF)
        state = bytes(fixture.uc.mem_read(CORE_STATE, 0x33C))
        results.append({
            "input": value,
            "selected_output": struct.unpack("<i", state[0x1C:0x20])[0],
            "filter_average": float_record(
                struct.unpack("<I", state[0x288:0x28C])[0]
            ),
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    interval_bounds = {
        str(interval): isolated_case(
            image, enabled=True, value=72, interval_milliseconds=interval
        )
        for interval in (699, 700, 1_000, 1_300, 1_301)
    }
    inactive = isolated_case(image, enabled=False, value=72)
    initial_invalid = isolated_case(image, enabled=True, value=0)
    rise_clamp = run_sequence(image, [60, 67])
    rise_boundary = run_sequence(image, [60, 66])
    fall_clamp = run_sequence(image, [60, 52])
    fall_boundary = run_sequence(image, [60, 53])
    averaging = run_sequence(image, [60, 61, 62, 63])
    missing = run_sequence(image, [60, 0, 0, 0, 0, 0])
    unchanged = run_sequence(image, [60] * 22)
    rolling = run_sequence(image, list(range(60, 82)))
    stock_wrapper = wrapper_case(image, inner_enabled=False, value=72)
    enabled_wrapper = wrapper_case(image, inner_enabled=True, value=72)
    stock_wrapper_sequence = wrapper_sequence(
        image, inner_enabled=False, values=[60, 67]
    )
    enabled_wrapper_sequence = wrapper_sequence(
        image, inner_enabled=True, values=[60, 67]
    )

    assert [interval_bounds[str(value)]["status"] for value in (699, 700, 1_000, 1_300, 1_301)] == [
        0x1771, 1, 1, 1, 0x1771,
    ]
    assert inactive["status"] == 0x1772 and inactive["output_raw"] == 72
    assert initial_invalid["status"] == 0x1775 and initial_invalid["output_filtered"] == 0
    assert rise_clamp[-1]["state"]["last_effective_input"] == 66
    assert rise_boundary[-1]["state"]["last_effective_input"] == 66
    assert fall_clamp[-1]["state"]["last_effective_input"] == 53
    assert fall_boundary[-1]["state"]["last_effective_input"] == 53
    assert [item["output_filtered"] for item in averaging] == [60, 60, 60, 61]
    assert [item["status"] for item in missing] == [1, 1, 1, 1, 0x1773, 0x1775]
    assert [item["status"] for item in unchanged[-3:]] == [1, 0x1774, 0x1774]
    assert [item["output_filtered"] for item in rolling[-4:]] == [68, 69, 70, 71]
    assert rolling[-1]["state"]["history_count"] == 19
    assert rolling[-1]["state"]["history"][18]["bits"] == "0x42a20000"
    assert rolling[-1]["state"]["history"][19]["bits"] == "0x42a20000"
    assert [item["selected_output"] for item in stock_wrapper_sequence] == [60, 67]
    assert [item["selected_output"] for item in enabled_wrapper_sequence] == [60, 60]

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "functions": {
            "filter": f"0x{HEART_RATE_FILTER:08x}",
            "wrapper": f"0x{HEART_RATE_WRAPPER:08x}",
            "reset": f"0x{STATE_RESET:08x}",
        },
        "interval_bounds": interval_bounds,
        "inactive": inactive,
        "initial_invalid": initial_invalid,
        "rise_clamp": rise_clamp,
        "rise_boundary": rise_boundary,
        "fall_clamp": fall_clamp,
        "fall_boundary": fall_boundary,
        "averaging": averaging,
        "missing": missing,
        "unchanged": unchanged,
        "rolling": rolling,
        "stock_wrapper": stock_wrapper,
        "enabled_wrapper": enabled_wrapper,
        "stock_wrapper_sequence": stock_wrapper_sequence,
        "enabled_wrapper_sequence": enabled_wrapper_sequence,
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
