#!/usr/bin/env python3
"""Run isolated production-Thumb fixtures for the dormant HR/speed ratio accumulator.

Wrapper 0x94270 invokes this path only under an otherwise-unwritten estimator flag combination.
The harness uses synthetic values and private emulated RAM to validate its bins, running moments,
30-sample decision and resets without BLE, sensors, health storage, or physical-device access.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


WRAPPER = 0x00094270
ACCUMULATOR = 0x00096634
BIN_HELPER = 0x00094698
STATE = RAM_BASE + 0x7000


def float_record(bits: int) -> dict[str, Any]:
    return {
        "bits": f"0x{bits:08x}",
        "value": struct.unpack("<f", struct.pack("<I", bits))[0],
    }


class DormantRatioAccumulatorFirmwareFixture:
    def __init__(
        self,
        image: bytes,
        *,
        thresholds: list[float] | None = None,
        profile_flag: int = 0,
    ) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.machine.uc.mem_write(STATE, bytes(0x33C))
        self.machine.uc.mem_write(STATE + 0x0D, bytes([profile_flag & 0xFF]))
        if thresholds is not None:
            if len(thresholds) != 5:
                raise ValueError("thresholds must contain five Float32 values")
            self.machine.uc.mem_write(STATE + 0x170, struct.pack("<5f", *thresholds))

    @staticmethod
    def records(data: bytes) -> list[dict[str, Any]]:
        return [float_record(bits) for bits in struct.unpack("<6I", data)]

    def update(self, heart_rate: int, speed: float, *, flags: int = 0x0004) -> dict[str, Any]:
        self.machine.uc.mem_write(STATE + 0x24, struct.pack("<f", speed))
        self.machine.uc.mem_write(STATE + 0x56, struct.pack("<H", flags))
        self.machine.call(WRAPPER, STATE, 0, heart_rate & 0xFFFF_FFFF)
        state = bytes(self.machine.uc.mem_read(STATE, 0x33C))
        return {
            "heart_rate": heart_rate,
            "speed": float_record(struct.unpack("<I", struct.pack("<f", speed))[0]),
            "flags": f"0x{flags:04x}",
            "selected_heart_rate": struct.unpack("<i", state[0x1C:0x20])[0],
            "thresholds": [
                float_record(bits) for bits in struct.unpack("<5I", state[0x170:0x184])
            ],
            "primary_sum_bins": self.records(state[0x1C0:0x1D8]),
            "primary_count_bins": self.records(state[0x1D8:0x1F0]),
            "all_heart_rate_mean": float_record(struct.unpack("<I", state[0x210:0x214])[0]),
            "all_sample_count": float_record(struct.unpack("<I", state[0x214:0x218])[0]),
            "qualified_square_sum": float_record(
                struct.unpack("<I", state[0x218:0x21C])[0]
            ),
            "qualified_heart_rate_mean": float_record(
                struct.unpack("<I", state[0x21C:0x220])[0]
            ),
            "qualified_speed_mean": float_record(
                struct.unpack("<I", state[0x220:0x224])[0]
            ),
            "qualified_sample_count": float_record(
                struct.unpack("<I", state[0x224:0x228])[0]
            ),
            "secondary_sum_bins": self.records(state[0x228:0x240]),
            "secondary_count_bins": self.records(state[0x240:0x258]),
        }


def run_sequence(
    image: bytes,
    values: list[tuple[int, float]],
    *,
    thresholds: list[float] | None = None,
    profile_flag: int = 0,
    flags: int = 0x0004,
) -> list[dict[str, Any]]:
    fixture = DormantRatioAccumulatorFirmwareFixture(
        image, thresholds=thresholds, profile_flag=profile_flag
    )
    return [fixture.update(hr, speed, flags=flags) for hr, speed in values]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    flag_disabled = run_sequence(image, [(72, 6)], flags=0)
    speed_boundary = run_sequence(image, [(72, 4), (72, 4.000_000_5)])
    zero_thresholds = run_sequence(image, [(72, 6)])
    bins_profile_zero = run_sequence(
        image,
        [(55, 6), (65, 6), (75, 6), (85, 6), (95, 6), (105, 6)],
        thresholds=[60, 70, 80, 90, 100],
        profile_flag=0,
    )
    bins_profile_one = run_sequence(
        image,
        [(55, 6)],
        thresholds=[60, 70, 80, 90, 100],
        profile_flag=1,
    )
    stable_thirty = run_sequence(image, [(72, 6)] * 30)
    lower_all_mean = run_sequence(image, [(60, 4)] + [(72, 6)] * 30)
    high_dispersion = run_sequence(image, [(60 if index % 2 == 0 else 80, 6) for index in range(30)])

    assert flag_disabled[-1]["all_sample_count"]["bits"] == "0x00000000"
    assert speed_boundary[0]["qualified_sample_count"]["bits"] == "0x00000000"
    assert speed_boundary[1]["qualified_sample_count"]["bits"] == "0x3f800000"
    assert zero_thresholds[-1]["primary_sum_bins"][5]["bits"] == "0x3daaaaab"
    assert zero_thresholds[-1]["qualified_square_sum"]["bits"] == "0x45a20000"
    assert [item["bits"] for item in bins_profile_zero[-1]["primary_sum_bins"]] == [
        "0x3e0848fc", "0x3dbd0bd1", "0x3da3d70a",
        "0x3d909091", "0x3d8158ed", "0x3d6a0ea1",
    ]
    assert bins_profile_one[-1]["primary_sum_bins"][0]["bits"] == "0x3e1374bd"
    assert stable_thirty[-1]["primary_sum_bins"][5]["bits"] == "0x401fffff"
    assert stable_thirty[-1]["qualified_sample_count"]["bits"] == "0x00000000"
    assert lower_all_mean[-1]["all_heart_rate_mean"]["bits"] == "0x428f39ce"
    assert lower_all_mean[-1]["secondary_sum_bins"][5]["bits"] == "0x3daaaaab"
    assert lower_all_mean[-1]["secondary_count_bins"][5]["bits"] == "0x3f800000"
    assert high_dispersion[-1]["qualified_sample_count"]["bits"] == "0x00000000"
    assert high_dispersion[-1]["primary_count_bins"][5]["bits"] == "0x41f00000"

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "functions": {
            "wrapper": f"0x{WRAPPER:08x}",
            "accumulator": f"0x{ACCUMULATOR:08x}",
            "bin_helper": f"0x{BIN_HELPER:08x}",
        },
        "flag_disabled": flag_disabled,
        "speed_boundary": speed_boundary,
        "zero_thresholds": zero_thresholds,
        "bins_profile_zero": bins_profile_zero,
        "bins_profile_one": bins_profile_one,
        "stable_thirty": stable_thirty,
        "lower_all_mean": lower_all_mean,
        "high_dispersion": high_dispersion,
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
