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

from unicorn.arm_const import (
    UC_ARM_REG_S0,
    UC_ARM_REG_S1,
    UC_ARM_REG_S2,
    UC_ARM_REG_S3,
)

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
LOCOMOTION_TRANSITION = 0x000761F8
LOCOMOTION_CONTROL_EXTRACT = 0x00056DC0
STATE = RAM_BASE + 0x4000
SOURCE = RAM_BASE + 0x4100
FEATURES = RAM_BASE + 0x4200
OUTPUT = RAM_BASE + 0x4300
CONTROL_STATE = RAM_BASE + 0x5000
CONTROL_EXPANDED = RAM_BASE + 0x5800
CONTROL_FIRST_INDICES = RAM_BASE + 0x5C00
CONTROL_SECOND_INDICES = RAM_BASE + 0x5C20
CONTROL_VALUES = RAM_BASE + 0x5D00
CONTROL_PRIMARY = RAM_BASE + 0x5E00
CONTROL_SECONDARY = RAM_BASE + 0x5E04


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

    def transition(
        self,
        total: int,
        initialized: bool,
        estimate: float,
        target: float,
        pair: tuple[int, int],
        shape: tuple[float, float],
    ) -> dict[str, Any]:
        self.machine.uc.mem_write(DIRECT_OUTPUT, struct.pack("<I", total))
        self.machine.uc.mem_write(DIRECT_OUTPUT + 8, bytes(pair))
        self.machine.uc.mem_write(DIRECT_OUTPUT + 16, bytes([initialized]))
        self.machine.uc.mem_write(DIRECT_OUTPUT + 20, struct.pack("<f", estimate))
        for register, value in (
            (UC_ARM_REG_S0, target),
            (UC_ARM_REG_S2, shape[0]),
            (UC_ARM_REG_S3, shape[1]),
        ):
            self.machine.uc.reg_write(register, float_bits(value))
        self.machine.call(
            LOCOMOTION_TRANSITION,
            DIRECT_OUTPUT,
            DIRECT_OUTPUT + 8,
            DIRECT_OUTPUT + 16,
            DIRECT_OUTPUT + 20,
        )
        return {
            "input": {
                "total": total,
                "initialized": initialized,
                "estimate": estimate,
                "target": target,
                "pair": list(pair),
                "shape": list(shape),
            },
            "total": struct.unpack(
                "<I", self.machine.uc.mem_read(DIRECT_OUTPUT, 4)
            )[0],
            "initialized": bool(
                self.machine.uc.mem_read(DIRECT_OUTPUT + 16, 1)[0]
            ),
            "estimate": struct.unpack(
                "<f", self.machine.uc.mem_read(DIRECT_OUTPUT + 20, 4)
            )[0],
        }

    def control_filter(
        self,
        sample_period: float,
        difference_scale: float,
        mode: int,
        samples: tuple[tuple[int, float, float], ...],
    ) -> dict[str, Any]:
        self.machine.uc.mem_write(CONTROL_STATE, b"\x00" * 0x6C8)
        self.machine.uc.mem_write(CONTROL_STATE + 0x51, bytes([len(samples)]))
        self.machine.uc.mem_write(
            CONTROL_STATE + 0x6C0,
            struct.pack("<2f", sample_period, difference_scale),
        )
        for index, (position, first, second) in enumerate(samples):
            record = CONTROL_STATE + 0x5C + index * 16
            self.machine.uc.mem_write(record, struct.pack("<H2x2f", position, first, second))
        self.machine.uc.mem_write(CONTROL_EXPANDED, b"\x00" * 1000)
        self.machine.uc.mem_write(CONTROL_FIRST_INDICES, b"\x00" * 20)
        self.machine.uc.mem_write(CONTROL_SECOND_INDICES, b"\x00" * 20)
        self.machine.uc.mem_write(CONTROL_VALUES, b"\x00" * 160)
        self.machine.uc.mem_write(CONTROL_PRIMARY, struct.pack("<f", -9.0))
        self.machine.uc.mem_write(CONTROL_SECONDARY, struct.pack("<f", -9.0))
        status = self.machine.call(
            LOCOMOTION_CONTROL_EXTRACT,
            CONTROL_STATE,
            CONTROL_EXPANDED,
            CONTROL_FIRST_INDICES,
            CONTROL_SECOND_INDICES,
            CONTROL_VALUES,
            CONTROL_PRIMARY,
            CONTROL_SECONDARY,
            mode,
        )
        return {
            "sample_period": sample_period,
            "difference_scale": difference_scale,
            "mode": mode,
            "status": status,
            "controls": list(struct.unpack(
                "<2f", self.machine.uc.mem_read(CONTROL_VALUES, 8)
            )),
            "primary": struct.unpack(
                "<f", self.machine.uc.mem_read(CONTROL_PRIMARY, 4)
            )[0],
            "secondary": struct.unpack(
                "<f", self.machine.uc.mem_read(CONTROL_SECONDARY, 4)
            )[0],
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
        (60.0, 69.0, 78.0),
        (60.0, 60.0, 120.0),
        (120.0, 60.0, 132.0),
        (100.0, 60.0, 132.0),
        (102.0, 50.0, 51.0),
        (108.0, 50.0, 51.0),
        (50.0, 50.0, 50.0),
    ]
    estimators = {
        "state_1": [fixture.estimator(STATE_1_ESTIMATOR, item) for item in estimator_inputs],
        "state_2": [fixture.estimator(STATE_2_ESTIMATOR, item) for item in estimator_inputs],
    }
    transitions = [
        fixture.transition(*item)
        for item in (
            (10, False, 0.0, 20.0, (10, 10), (1.0, 1.0)),
            (20, True, 20.0, 20.0, (20, 1), (0.0, 0.0)),
            (21, True, 20.25, 20.0, (21, 2), (0.0, 0.0)),
            (10, False, 0.0, 20.0, (7, 10), (1.0, 1.0)),
            (5, False, 0.0, 20.0, (5, 10), (1.0, 0.5)),
            (10, False, 0.0, 5.0, (10, 10), (1.0, 1.0)),
        )
    ]
    control_samples = (
        (0, 30.0, 20.0),
        (100, 21.0, 20.0),
        (200, 0.0, 0.0),
    )
    control_filters = [
        fixture.control_filter(100.0, 10.0, mode, control_samples)
        for mode in (1, 2)
    ]

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
        "locomotion_transitions": transitions,
        "locomotion_control_filters": control_filters,
    }, indent=2))


if __name__ == "__main__":
    main()
