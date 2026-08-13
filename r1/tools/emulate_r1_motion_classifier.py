#!/usr/bin/env python3
"""Run isolated production-Thumb fixtures for the final R1 motion/cadence classifier.

The harness maps the SHA-pinned application image and private emulated RAM only. It calls the
17-byte initializer and pure classifier functions; it has no BLE, sensor, storage, or device access.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2

from emulate_r1_locomotion_window import (
    DIRECT_OUTPUT,
    IMAGE_SHA256,
    LocomotionFirmwareFixture,
    RAM_BASE,
)


INITIALIZER = 0x00071188
CLASSIFIER = 0x0005F4B6
STATE_1_ESTIMATOR = 0x00058060
STATE_2_ESTIMATOR = 0x00057F8C
STATE = RAM_BASE + 0x4000
SOURCE = RAM_BASE + 0x4100
FEATURES = RAM_BASE + 0x4200
OUTPUT = RAM_BASE + 0x4300


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def bits_float(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value))[0]


def feature_record(
    state: int,
    rate: float,
    *,
    feature_4: float | None = None,
    rates: tuple[float, float, float] | None = None,
) -> bytes:
    rate_11, rate_12, rate_13 = rates or (rate, rate, rate)
    floats = [
        300.0, 200.0, 1_500.0, 0.0,
        rate if feature_4 is None else feature_4,
        rate, 0.0, 0.0, 1.0, 0.0, 1.0, rate_11, rate_12, rate_13,
    ]
    predicates = [1, 1, 1, 0xFF, 0xFF, 1] if state == 1 else [1] * 6
    return struct.pack("<14f6B", *floats, *predicates)


class MotionClassifierFirmwareFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.reset()

    def reset(self) -> None:
        self.machine.uc.mem_write(STATE, b"\x00" * 0x40)
        self.machine.uc.mem_write(OUTPUT, b"\x00" * 8)
        self.machine.call(INITIALIZER, STATE)

    def update(
        self,
        record: bytes | None,
        *,
        elapsed_seconds: int = 1,
        source_invalid: bool = False,
    ) -> dict[str, Any]:
        if record is not None and len(record) != 62:
            raise ValueError("classifier feature record must be exactly 62 bytes")
        self.machine.uc.mem_write(SOURCE, b"\x00" * 0x20)
        self.machine.uc.mem_write(SOURCE + 12, bytes([int(source_invalid)]))
        self.machine.uc.mem_write(FEATURES, record or b"\x00" * 62)
        self.machine.call(
            CLASSIFIER,
            STATE,
            elapsed_seconds,
            SOURCE,
            0,
            FEATURES,
            OUTPUT,
        )
        return {
            "output": list(self.machine.uc.mem_read(OUTPUT, 3)),
            "state_17_bytes": list(self.machine.uc.mem_read(STATE, 17)),
        }

    def estimator(self, address: int, values: tuple[float, float, float]) -> dict[str, Any]:
        self.machine.uc.mem_write(DIRECT_OUTPUT, b"\x00" * 8)
        for register, value in zip(
            (UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2),
            values,
        ):
            self.machine.uc.reg_write(register, float_bits(value))
        self.machine.call(address, DIRECT_OUTPUT)
        result_bits = self.machine.uc.reg_read(UC_ARM_REG_S0)
        return {
            "input": list(values),
            "result_float32_bits": f"0x{result_bits:08x}",
            "result": bits_float(result_bits),
            "consensus": self.machine.uc.mem_read(DIRECT_OUTPUT, 1)[0],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()
    fixture = MotionClassifierFirmwareFixture(image)

    state_1 = []
    for _ in range(5):
        state_1.append(fixture.update(feature_record(1, 100.0)))
    fixture.reset()
    state_2 = []
    for _ in range(5):
        state_2.append(fixture.update(feature_record(2, 150.0)))

    fixture.reset()
    state_2_high_history = [
        fixture.update(feature_record(2, rate))
        for rate in (150.0, 170.0, 190.0, 210.0, 130.0)
    ]

    fixture.reset()
    invalid_gap = [
        fixture.update(feature_record(1, 100.0)),
        fixture.update(feature_record(1, 100.0), elapsed_seconds=3, source_invalid=True),
        fixture.update(feature_record(1, 100.0)),
    ]

    fixture.reset()
    state_1_crossing_and_prior = [
        fixture.update(feature_record(1, 60.0, feature_4=120.0))
        for _ in range(3)
    ]
    state_1_crossing_and_prior.append(
        fixture.update(feature_record(1, 60.0, feature_4=0.0))
    )

    fixture.reset()
    state_1_double_prior = [
        fixture.update(feature_record(1, 60.0, feature_4=0.0))
        for _ in range(3)
    ]
    state_1_double_prior.append(fixture.update(feature_record(
        1,
        120.0,
        feature_4=0.0,
        rates=(120.0, 120.0, 0.0),
    )))

    estimator_inputs = [
        (125.0, 125.0, 125.0),
        (150.0, 150.0, 150.0),
        (100.0, 100.0, 100.0),
        (60.0, 120.0, 60.0),
        (60.0, 70.0, 80.0),
        (80.0, 70.0, 60.0),
        (130.0, 70.0, 130.0),
    ]
    estimators = {
        "state_1": [fixture.estimator(STATE_1_ESTIMATOR, item) for item in estimator_inputs],
        "state_2": [fixture.estimator(STATE_2_ESTIMATOR, item) for item in estimator_inputs],
    }

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "initializer_state": [0xFE] * 5 + [0] * 10 + [1, 1],
        "steady_state_1": state_1,
        "steady_state_2": state_2,
        "state_2_high_history": state_2_high_history,
        "invalid_elapsed_3": invalid_gap,
        "state_1_crossing_and_prior": state_1_crossing_and_prior,
        "state_1_double_prior": state_1_double_prior,
        "estimators": estimators,
    }, indent=2))


if __name__ == "__main__":
    main()
