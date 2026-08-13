#!/usr/bin/env python3
"""Run isolated production-Thumb fixtures for the dormant estimator's speed filters.

The two helpers are only reachable from the stock-disabled estimator core. This script calls the
SHA-pinned functions directly with synthetic Float32 values and private emulated RAM so their
ordered comparisons, rolling histories and rounding can be validated without enabling firmware,
accessing BLE, reading a sensor, or touching a physical ring.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_S0, UC_ARM_REG_S1

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


SPEED_GATE = 0x000908E0
MOVING_AVERAGE = 0x00090A50
GATE_HISTORY = RAM_BASE + 0x6800
AVERAGE_HISTORY = RAM_BASE + 0x6840


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def bits_float(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value))[0]


def encoded_float(value: float) -> dict[str, Any]:
    bits = float_bits(value)
    return {"bits": f"0x{bits:08x}", "value": bits_float(bits)}


class DormantSpeedFilterFirmwareFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.reset()

    def reset(self) -> None:
        self.machine.uc.mem_write(GATE_HISTORY, bytes(6 * 4))
        self.machine.uc.mem_write(AVERAGE_HISTORY, bytes(5 * 4))

    def gate(
        self,
        raw_candidate: float,
        previous_output: float,
        sample_index: int,
        flag_word: int,
    ) -> dict[str, Any]:
        self.machine.uc.reg_write(UC_ARM_REG_S0, float_bits(raw_candidate))
        self.machine.uc.reg_write(UC_ARM_REG_S1, float_bits(previous_output))
        self.machine.call(SPEED_GATE, GATE_HISTORY, sample_index, flag_word)
        output_bits = self.machine.uc.reg_read(UC_ARM_REG_S0)
        history = struct.unpack(
            "<6f", bytes(self.machine.uc.mem_read(GATE_HISTORY, 6 * 4))
        )
        return {
            "raw_candidate": encoded_float(raw_candidate),
            "previous_output": encoded_float(previous_output),
            "sample_index": sample_index,
            "flag_word": f"0x{flag_word:04x}",
            "output": encoded_float(bits_float(output_bits)),
            "history": [encoded_float(value) for value in history],
        }

    def average(
        self,
        value: float,
        sample_index: int,
        history_address: int = AVERAGE_HISTORY,
        history_word_count: int = 5,
    ) -> dict[str, Any]:
        self.machine.uc.reg_write(UC_ARM_REG_S0, float_bits(value))
        self.machine.call(MOVING_AVERAGE, history_address, sample_index)
        output_bits = self.machine.uc.reg_read(UC_ARM_REG_S0)
        history = struct.unpack(
            f"<{history_word_count}f",
            bytes(self.machine.uc.mem_read(history_address, history_word_count * 4)),
        )
        return {
            "input": encoded_float(value),
            "sample_index": sample_index,
            "output": encoded_float(bits_float(output_bits)),
            "history": [encoded_float(item) for item in history],
        }

    def process(
        self,
        raw_candidate: float,
        previous_output: float,
        sample_index: int,
        flag_word: int,
    ) -> dict[str, Any]:
        gated = self.gate(raw_candidate, previous_output, sample_index, flag_word)
        averaged = self.average(
            gated["output"]["value"],
            sample_index,
            history_address=GATE_HISTORY,
            history_word_count=6,
        )
        return {"gate": gated, "average": averaged}


def isolated_gate_case(
    image: bytes,
    raw_candidate: float,
    previous_output: float,
    sample_index: int,
    flag_word: int,
    history: list[float] | None = None,
) -> dict[str, Any]:
    fixture = DormantSpeedFilterFirmwareFixture(image)
    if history is not None:
        fixture.machine.uc.mem_write(GATE_HISTORY, struct.pack("<6f", *history))
    return fixture.gate(raw_candidate, previous_output, sample_index, flag_word)


def isolated_average_case(
    image: bytes,
    value: float,
    sample_index: int,
    history: list[float] | None = None,
) -> dict[str, Any]:
    fixture = DormantSpeedFilterFirmwareFixture(image)
    if history is not None:
        fixture.machine.uc.mem_write(AVERAGE_HISTORY, struct.pack("<5f", *history))
    return fixture.average(value, sample_index)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    first_sample_cases = {
        name: isolated_gate_case(image, value, 0, 0, 0)
        for name, value in {
            "below_boundary": 14,
            "at_boundary": 15,
            "above_boundary": 16,
            "nan": math.nan,
        }.items()
    }
    normal_rolling = isolated_gate_case(
        image,
        raw_candidate=40,
        previous_output=20,
        sample_index=4,
        flag_word=0,
        history=[20, 20, 20, 20, 0, 0],
    )
    normal_no_average_override = isolated_gate_case(
        image,
        raw_candidate=40,
        previous_output=22,
        sample_index=4,
        flag_word=0,
        history=[20, 20, 20, 20, 0, 0],
    )
    flagged_first = isolated_gate_case(image, 10, 0, 0, 0x0004)
    flagged_second = isolated_gate_case(
        image,
        raw_candidate=20,
        previous_output=10,
        sample_index=1,
        flag_word=0x1444,
        history=[5.5, 0, 0, 0, 0, 0],
    )
    flagged_rolling = isolated_gate_case(
        image,
        raw_candidate=40,
        previous_output=10,
        sample_index=5,
        flag_word=0x0400,
        history=[5.5, 7, 8, 9, 10, 0],
    )

    average_warmup = [
        isolated_average_case(
            image,
            value=value,
            sample_index=index,
            history=[10, 20, 30, 0, 0],
        )
        for index, value in ((0, 10), (1, 20), (2, 30), (3, 40))
    ]
    average_rolling = isolated_average_case(
        image,
        value=50,
        sample_index=4,
        history=[10, 20, 30, 40, 0],
    )

    sequence_fixture = DormantSpeedFilterFirmwareFixture(image)
    previous = 0.0
    sequence = []
    for index, raw in enumerate((10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 5.0)):
        result = sequence_fixture.process(raw, previous, index, 0)
        previous = result["average"]["output"]["value"]
        sequence.append(result)

    flagged_sequence_fixture = DormantSpeedFilterFirmwareFixture(image)
    previous = 0.0
    flagged_sequence = []
    for index, raw in enumerate((10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 5.0)):
        result = flagged_sequence_fixture.process(raw, previous, index, 0x1444)
        previous = result["average"]["output"]["value"]
        flagged_sequence.append(result)

    assert first_sample_cases["below_boundary"]["output"]["bits"] == "0x41600000"
    assert first_sample_cases["below_boundary"]["history"][0]["bits"] == "0x41600000"
    for name in ("at_boundary", "above_boundary"):
        assert first_sample_cases[name]["output"]["bits"] == "0x00000000"
        assert all(item["bits"] == "0x00000000" for item in first_sample_cases[name]["history"])
    assert first_sample_cases["nan"]["output"]["bits"] == "0x7fc00000"
    assert first_sample_cases["nan"]["history"][0]["bits"] == "0x7fc00000"
    assert normal_rolling["output"]["bits"] == "0x41c00000"
    assert normal_no_average_override["output"]["bits"] == "0x42200000"
    assert flagged_first["history"][0]["bits"] == "0x40b00000"
    assert average_rolling["output"]["bits"] == "0x41f00000"
    assert [item["gate"]["output"]["bits"] for item in sequence] == [
        "0x41200000", "0x41a00000", "0x41f00000", "0x42200000",
        "0x41f00000", "0x42280000", "0x4215999a",
    ]
    assert [item["average"]["output"]["bits"] for item in sequence] == [
        "0x41200000", "0x41700000", "0x41a00000", "0x41c80000",
        "0x42080000", "0x4231999a", "0x420b851e",
    ]
    assert [item["gate"]["output"]["bits"] for item in flagged_sequence] == [
        "0x41200000", "0x41a00000", "0x41f00000", "0x42200000",
        "0x42480000", "0x4212aaab", "0x42118e39",
    ]
    assert [item["average"]["output"]["bits"] for item in flagged_sequence] == [
        "0x41200000", "0x41700000", "0x41a00000", "0x41c80000",
        "0x41f00000", "0x42255556", "0x4227c71d",
    ]

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "functions": {
            "flag_dependent_gate": f"0x{SPEED_GATE:08x}",
            "five_sample_moving_average": f"0x{MOVING_AVERAGE:08x}",
        },
        "first_sample_ordered_comparison": first_sample_cases,
        "normal_rolling_average_override": normal_rolling,
        "normal_rolling_raw_fallback": normal_no_average_override,
        "flagged_first": flagged_first,
        "flagged_second": flagged_second,
        "flagged_rolling": flagged_rolling,
        "moving_average_warmup": average_warmup,
        "moving_average_rolling": average_rolling,
        "composed_unflagged_sequence": sequence,
        "composed_flagged_sequence": flagged_sequence,
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
