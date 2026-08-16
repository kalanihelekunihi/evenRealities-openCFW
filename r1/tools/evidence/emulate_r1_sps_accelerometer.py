#!/usr/bin/env python3
"""Run isolated production-Thumb fixtures for the R1 accelerometer SPS candidate.

The harness maps the SHA-pinned application and private emulated RAM only. It invokes the
88-byte initializer, model dispatcher, and accelerometer candidate function with synthetic,
caller-owned feature records. It has no BLE, sensor, flash-write, health-store, or device access.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0

from emulate_r1_locomotion_window import (
    DIRECT_OUTPUT,
    IMAGE_SHA256,
    LocomotionFirmwareFixture,
    RAM_BASE,
)


INITIALIZER = 0x00071100
ACCELEROMETER_CANDIDATE = 0x0005EF1C
MODEL_DISPATCHER = 0x000684FC
STATE_2_PRIMARY_MODEL = 0x00068DE0
STATE_2_SECONDARY_MODEL = 0x00068E5C
STATE_1_PRIMARY_MODEL = 0x00069E94
STATE_1_SECONDARY_MODEL = 0x00069F3C
STATE = RAM_BASE + 0x6000
CONFIG = RAM_BASE + 0x6100
FEATURES = RAM_BASE + 0x6200
MOTION = RAM_BASE + 0x6300
PROFILE = RAM_BASE + 0x6400
OUTPUT = RAM_BASE + 0x6500
MODEL_INPUT = RAM_BASE + 0x6600


def f32_bytes(value: float) -> bytes:
    return struct.pack("<f", value)


def float_bits(value: float) -> int:
    return struct.unpack("<I", f32_bytes(value))[0]


def bits_float(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value))[0]


def describe_float(data: bytes) -> dict[str, Any]:
    bits = struct.unpack("<I", data)[0]
    return {"bits": f"0x{bits:08x}", "value": bits_float(bits)}


def feature_record(
    *,
    feature_0: float = 300.0,
    feature_2: float = 1_500.0,
    feature_3: float = 0.0,
    feature_4: float = 100.0,
    feature_5: float = 150.0,
) -> bytes:
    values = [
        feature_0,
        200.0,
        feature_2,
        feature_3,
        feature_4,
        feature_5,
        0.0,
        0.0,
        1.0,
        0.0,
        1.0,
        feature_5,
        feature_5,
        feature_5,
    ]
    return struct.pack("<14f6B", *values, *([1] * 6))


class SPSAccelerometerFirmwareFixture:
    def __init__(
        self,
        image: bytes,
        *,
        config: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0),
    ) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.machine.uc.mem_write(CONFIG, struct.pack("<4f", *config))
        self.reset()

    def reset(self) -> None:
        self.machine.uc.mem_write(STATE, b"\x00" * 88)
        self.machine.uc.mem_write(OUTPUT, b"\x00" * 8)
        self.machine.call(INITIALIZER, STATE, CONFIG)

    def update(
        self,
        *,
        state: int,
        smoothed_state: int | None = None,
        cadence: int,
        features: bytes | None = None,
        height_centimeters: float = 175.0,
        elapsed_seconds: int = 1,
    ) -> dict[str, Any]:
        if not 0 <= state <= 0xFF:
            raise ValueError("state must fit UInt8")
        if smoothed_state is None:
            smoothed_state = state
        if not 0 <= smoothed_state <= 0xFF or not 0 <= cadence <= 0xFF:
            raise ValueError("smoothed_state and cadence must fit UInt8")
        record = features or feature_record()
        if len(record) != 62:
            raise ValueError("feature record must be exactly 62 bytes")
        self.machine.uc.mem_write(FEATURES, record)
        self.machine.uc.mem_write(MOTION, bytes([state, smoothed_state, cadence]))
        self.machine.uc.mem_write(PROFILE, f32_bytes(height_centimeters))
        self.machine.uc.mem_write(OUTPUT, b"\xa5" * 8)
        return_code = self.machine.call(
            ACCELEROMETER_CANDIDATE,
            STATE,
            elapsed_seconds,
            FEATURES,
            MOTION,
            PROFILE,
            OUTPUT,
        )
        raw_state = bytes(self.machine.uc.mem_read(STATE, 88))
        raw_output = bytes(self.machine.uc.mem_read(OUTPUT, 8))
        return {
            "return_code": return_code,
            "output_candidate": describe_float(raw_output[0:4]),
            "output_status": raw_output[4],
            "output_reserved_tail": list(raw_output[5:8]),
            "state": self.describe_state(raw_state),
        }

    def direct_model(self, address: int, values: tuple[float, ...]) -> dict[str, Any]:
        self.machine.uc.mem_write(MODEL_INPUT, struct.pack("<" + "f" * len(values), *values))
        self.machine.call(address, MODEL_INPUT)
        bits = self.machine.uc.reg_read(UC_ARM_REG_S0)
        return {
            "function": f"0x{address:08x}",
            "input": list(values),
            "result": {"bits": f"0x{bits:08x}", "value": bits_float(bits)},
        }

    @staticmethod
    def describe_state(data: bytes) -> dict[str, Any]:
        def value(offset: int) -> dict[str, Any]:
            return describe_float(data[offset : offset + 4])

        def model(offset: int) -> dict[str, Any]:
            return {
                "model_type": struct.unpack("<I", data[offset : offset + 4])[0],
                "accumulated_secondary": value(offset + 4),
                "accumulated_primary": value(offset + 8),
                "accepted_count": struct.unpack("<H", data[offset + 12 : offset + 14])[0],
                "count_padding": list(data[offset + 14 : offset + 16]),
                "calibration_slope": value(offset + 16),
                "calibration_intercept": value(offset + 20),
                "calibration_enabled": struct.unpack(
                    "<I", data[offset + 24 : offset + 28]
                )[0],
            }

        return {
            "smoothed_state_2": value(0),
            "smoothed_state_1": value(4),
            "state_2_model": model(8),
            "state_1_model": model(36),
            "config_pointer": f"0x{struct.unpack('<I', data[64:68])[0]:08x}",
            "latest_secondary": value(68),
            "latest_primary": value(72),
            "missing_update_count": struct.unpack("<I", data[76:80])[0],
            "startup_cooldown": struct.unpack("<H", data[80:82])[0],
            "cooldown_padding": list(data[82:84]),
            "reserved_word": struct.unpack("<I", data[84:88])[0],
        }


def sequence(
    fixture: SPSAccelerometerFirmwareFixture,
    *,
    state: int,
    cadence: int,
    features: bytes,
    count: int = 3,
) -> list[dict[str, Any]]:
    return [
        fixture.update(state=state, cadence=cadence, features=features)
        for _ in range(count)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    stock_state_1 = SPSAccelerometerFirmwareFixture(image)
    stock_state_2 = SPSAccelerometerFirmwareFixture(image)
    state_1_features = feature_record(
        feature_0=300.0,
        feature_3=0.0,
        feature_4=100.0,
    )
    state_2_features = feature_record(feature_2=1_500.0, feature_5=150.0)

    varying_state_1 = SPSAccelerometerFirmwareFixture(image)
    varying_state_1_sequence = [
        varying_state_1.update(state=1, cadence=100, features=state_1_features),
        varying_state_1.update(
            state=1,
            cadence=100,
            features=feature_record(
                feature_0=400.0,
                feature_3=50.0,
                feature_4=105.0,
            ),
        ),
    ]
    varying_state_2 = SPSAccelerometerFirmwareFixture(image)
    varying_state_2_sequence = [
        varying_state_2.update(state=2, cadence=150, features=state_2_features),
        varying_state_2.update(
            state=2,
            cadence=150,
            features=feature_record(feature_2=1_300.0, feature_5=160.0),
        ),
    ]

    calibrated_state_1 = SPSAccelerometerFirmwareFixture(
        image,
        config=(0.0, 0.0, 2.0, 1.0),
    )
    calibrated_state_2 = SPSAccelerometerFirmwareFixture(
        image,
        config=(2.0, 1.0, 0.0, 0.0),
    )

    rejected = SPSAccelerometerFirmwareFixture(image)
    rejection_cases = {
        "state_mismatch": rejected.update(
            state=1,
            smoothed_state=2,
            cadence=100,
            features=state_1_features,
        ),
        "relative_difference_exactly_point_2": rejected.update(
            state=1,
            cadence=100,
            features=feature_record(feature_4=120.0),
        ),
        "rejected_state_ff": rejected.update(
            state=0xFF,
            cadence=0,
            features=state_1_features,
        ),
        "state_zero": rejected.update(
            state=0,
            cadence=0,
            features=state_1_features,
        ),
    }

    gap = SPSAccelerometerFirmwareFixture(image)
    gap_sequence = [
        gap.update(state=1, cadence=100, features=state_1_features),
        gap.update(
            state=1,
            cadence=100,
            features=state_1_features,
            elapsed_seconds=3,
        ),
        gap.update(
            state=1,
            smoothed_state=0xFE,
            cadence=100,
            features=state_1_features,
        ),
    ]

    direct = SPSAccelerometerFirmwareFixture(image)
    direct_models = [
        direct.direct_model(STATE_1_PRIMARY_MODEL, (100.0, 175.0, 300.0, 0.0)),
        direct.direct_model(STATE_1_SECONDARY_MODEL, (100.0, 175.0, 300.0, 0.0)),
        direct.direct_model(STATE_2_PRIMARY_MODEL, (175.0, 150.0, 1_500.0)),
        direct.direct_model(STATE_2_SECONDARY_MODEL, (175.0, 150.0, 1_500.0)),
        direct.direct_model(STATE_2_SECONDARY_MODEL, (175.0, 150.0, 1_000.0)),
    ]

    result = {
        "image_sha256": IMAGE_SHA256,
        "stock_initializer": SPSAccelerometerFirmwareFixture.describe_state(
            bytes(SPSAccelerometerFirmwareFixture(image).machine.uc.mem_read(STATE, 88))
        ),
        "stock_state_1": sequence(
            stock_state_1, state=1, cadence=100, features=state_1_features
        ),
        "stock_state_2": sequence(
            stock_state_2, state=2, cadence=150, features=state_2_features
        ),
        "varying_state_1_smoothing": varying_state_1_sequence,
        "varying_state_2_smoothing": varying_state_2_sequence,
        "calibrated_state_1": sequence(
            calibrated_state_1, state=1, cadence=100, features=state_1_features
        ),
        "calibrated_state_2": sequence(
            calibrated_state_2, state=2, cadence=150, features=state_2_features
        ),
        "rejection_cases": rejection_cases,
        "elapsed_and_missing_bookkeeping": gap_sequence,
        "direct_models": direct_models,
    }

    assert result["stock_initializer"]["startup_cooldown"] == 8
    assert result["stock_initializer"]["state_2_model"]["model_type"] == 0
    assert result["stock_initializer"]["state_1_model"]["model_type"] == 1
    assert [item["output_candidate"]["bits"]
            for item in result["stock_state_1"]] == ["0x40800000"] * 3
    assert [item["output_candidate"]["bits"]
            for item in result["stock_state_2"]] == ["0x40f26628"] * 3
    assert result["varying_state_1_smoothing"][1][
        "output_candidate"
    ]["bits"] == "0x4082efa6"
    assert result["varying_state_2_smoothing"][1][
        "output_candidate"
    ]["bits"] == "0x40f5f560"
    assert result["calibrated_state_1"][0]["output_candidate"]["bits"] == \
        "0x40e00000"
    assert result["calibrated_state_1"][0]["output_status"] == 3
    assert result["calibrated_state_2"][0]["output_candidate"]["bits"] == \
        "0x4181fe62"
    assert result["calibrated_state_2"][0]["output_status"] == 3
    assert {
        name: (item["output_candidate"]["bits"], item["output_status"])
        for name, item in result["rejection_cases"].items()
    } == {
        "state_mismatch": ("0xbf800000", 1),
        "relative_difference_exactly_point_2": ("0xbf800000", 1),
        "rejected_state_ff": ("0xbf800000", 1),
        "state_zero": ("0x00000000", 1),
    }
    assert [item["state"]["missing_update_count"]
            for item in result["elapsed_and_missing_bookkeeping"]] == [0, 2, 2]
    assert [item["result"]["bits"] for item in result["direct_models"]] == [
        "0x405b7980", "0x407de7f4", "0x40f3fcc4", "0x40f26628",
        "0x40d30d59",
    ]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
