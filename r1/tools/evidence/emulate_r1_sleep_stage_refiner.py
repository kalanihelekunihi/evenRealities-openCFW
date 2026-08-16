#!/usr/bin/env python3
"""Assert the stock 0x81040 sleep-stage postprocessor over synthetic stages."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


REFINER = 0x00081040
STAGES = RAM_BASE + 0x62000
COUNT = RAM_BASE + 0x63000
PROFILES = {
    "mode_0": bytes.fromhex("00010700020064ec0a000a"),
    "mode_1": bytes.fromhex("01000000000278000a07ef"),
    "mode_2": bytes.fromhex("02000b00060278000a07ef"),
    "mode_3": bytes.fromhex("03000b000a03a0000a00f6"),
}
EXPECTED_FNV1A = {
    "mode_0": 0xF57EAD45,
    "mode_1": 0x6322B241,
    "mode_2": 0xC5D5BFF9,
    "mode_3": 0x4D4F568B,
}


def fnv1a(data: bytes) -> int:
    value = 0x811C9DC5
    for byte in data:
        value = ((value ^ byte) * 0x01000193) & 0xFFFFFFFF
    return value


def run(image: bytes, profile: bytes, stages: bytes) -> tuple[int, bytes]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(STAGES, stages)
    fixture.uc.mem_write(COUNT, struct.pack("<I", len(stages)))
    words = struct.unpack("<3I", profile + b"\x00")
    result = fixture.call(
        REFINER, words[0], words[1], words[2], STAGES,
        0, len(stages) * 30, COUNT,
    )
    return result, bytes(fixture.uc.mem_read(STAGES, len(stages)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()
    cycle = bytes([0] * 4 + [2] * 18 + [1] * 10 +
                  [2] * 12 + [3] * 12 + [0] * 4)
    source = cycle * 2

    summaries = {}
    for name, profile in PROFILES.items():
        result, output = run(image, profile, source)
        digest = fnv1a(output)
        assert result == 0
        assert digest == EXPECTED_FNV1A[name]
        assert all(stage <= 3 for stage in output)
        summaries[name] = {
            "configuration": profile.hex(),
            "fnv1a": f"0x{digest:08x}",
            "counts": {str(stage): output.count(stage) for stage in range(4)},
            "head": list(output[:16]),
            "tail": list(output[-16:]),
        }

    no_input = LocomotionFirmwareFixture(image)
    no_input.uc.mem_write(COUNT, struct.pack("<I", 0))
    words = struct.unpack("<3I", PROFILES["mode_0"] + b"\x00")
    result = no_input.call(
        REFINER, words[0], words[1], words[2], STAGES, 0, 0, COUNT,
    )
    assert result == 0

    print(json.dumps({
        "function": "0x00081040",
        "source_count": len(source),
        "profiles": summaries,
        "zero_count_return": result,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
