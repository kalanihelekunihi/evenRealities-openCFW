#!/usr/bin/env python3
"""Execute isolated production-Thumb Float32 convolution fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


EXECUTOR = 0x00076BDC
DESCRIPTOR = RAM_BASE + 0x5A000
INPUT_TENSOR = RAM_BASE + 0x5A100
OUTPUT_TENSOR = RAM_BASE + 0x5A120
INPUT_ARRAY = RAM_BASE + 0x5A140
OUTPUT_ARRAY = RAM_BASE + 0x5A144
WEIGHTS = RAM_BASE + 0x5A200
BIASES = RAM_BASE + 0x5A400
INPUT = RAM_BASE + 0x5A500
OUTPUT = RAM_BASE + 0x5A900


def words(values: list[float]) -> list[str]:
    packed = struct.pack(f"<{len(values)}f", *values)
    return [
        f"0x{value:08x}"
        for value in struct.unpack(f"<{len(values)}I", packed)
    ]


def fixture(
    machine: LocomotionFirmwareFixture,
    descriptor: tuple[int, int, int, int, int, int, int, int, float],
    input_shape: tuple[int, int],
    output_shape: tuple[int, int],
    input_values: list[float],
    weights: list[float],
    biases: list[float],
) -> dict[str, Any]:
    kernel, stride, left, right, channels, outputs, groups, activation, alpha = (
        descriptor
    )
    input_channels, input_width = input_shape
    output_channels, output_width = output_shape
    machine.uc.mem_write(
        DESCRIPTOR,
        struct.pack(
            "<8BfII", kernel, stride, left, right, channels, outputs, groups,
            activation, alpha, WEIGHTS, BIASES,
        ),
    )
    machine.uc.mem_write(
        INPUT_TENSOR, struct.pack("<5I", 4, 1, input_channels, input_width, INPUT)
    )
    machine.uc.mem_write(
        OUTPUT_TENSOR,
        struct.pack("<5I", 4, 1, output_channels, output_width, OUTPUT),
    )
    machine.uc.mem_write(INPUT_ARRAY, struct.pack("<I", INPUT_TENSOR))
    machine.uc.mem_write(OUTPUT_ARRAY, struct.pack("<I", OUTPUT_TENSOR))
    machine.uc.mem_write(INPUT, b"\xA5" * 0x400)
    machine.uc.mem_write(OUTPUT, b"\xA5" * 0x200)
    machine.uc.mem_write(INPUT, struct.pack(f"<{len(input_values)}f", *input_values))
    machine.uc.mem_write(WEIGHTS, struct.pack(f"<{len(weights)}f", *weights))
    machine.uc.mem_write(BIASES, struct.pack(f"<{len(biases)}f", *biases))
    machine.call(EXECUTOR, DESCRIPTOR, INPUT_ARRAY, OUTPUT_ARRAY, 0)
    output_count = output_channels * output_width
    output_data = bytes(machine.uc.mem_read(OUTPUT, output_count * 4))
    restored_input = bytes(machine.uc.mem_read(INPUT, len(input_values) * 4))
    return {
        "output_bits": [
            f"0x{value:08x}"
            for value in struct.unpack(f"<{output_count}I", output_data)
        ],
        "input_restored": restored_input == struct.pack(
            f"<{len(input_values)}f", *input_values
        ),
    }


def run(image: bytes) -> dict[str, Any]:
    machine = LocomotionFirmwareFixture(image)
    kernel3 = fixture(
        machine,
        (3, 1, 1, 1, 2, 2, 1, 0, 0.0),
        (2, 4), (2, 4),
        [1.0, 2.0, 3.0, 4.0, 10.0, 20.0, 30.0, 40.0],
        [1.0, 0.0, -1.0, 0.1, 0.0, -0.1,
         0.5, 0.5, 0.5, 0.0, 0.0, 0.0],
        [0.5, -1.0],
    )
    depthwise = fixture(
        machine,
        (3, 1, 1, 1, 2, 2, 2, 0, 0.0),
        (2, 3), (2, 3),
        [1.0, 2.0, 3.0, 10.0, 20.0, 30.0],
        [0.0, 1.0, 0.0, 0.0, 2.0, 0.0],
        [0.0, 1.0],
    )
    kernel5 = fixture(
        machine,
        (5, 1, 2, 2, 1, 1, 1, 1, 0.25),
        (1, 5), (1, 5),
        [-1.0, -2.0, -3.0, 4.0, 5.0],
        [1.0, 1.0, 1.0, 1.0, 1.0],
        [0.0],
    )
    sigmoid = fixture(
        machine,
        (1, 1, 0, 0, 1, 1, 1, 2, 0.0),
        (1, 3), (1, 3),
        [-100.0, 0.0, 100.0], [1.0], [0.0],
    )

    assert kernel3["input_restored"] and depthwise["input_restored"]
    assert kernel5["input_restored"] and sigmoid["input_restored"]
    assert kernel3["output_bits"] == words(
        [-3.5, -3.5, -3.5, 6.5, 0.5, 2.0, 3.5, 2.5]
    )
    assert depthwise["output_bits"] == words(
        [1.0, 2.0, 3.0, 21.0, 41.0, 61.0]
    )
    assert kernel5["output_bits"] == words(
        [-1.5, -0.5, 3.0, 4.0, 6.0]
    )
    assert sigmoid["output_bits"] == [
        "0x0041edc4", "0x3f000000", "0x3f800000",
    ]

    return {
        "fixture_groups": 4,
        "kernel3": kernel3,
        "depthwise_kernel3": depthwise,
        "kernel5_leaky_relu": kernel5,
        "kernel1_sigmoid": sigmoid,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
