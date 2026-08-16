#!/usr/bin/env python3
"""Execute isolated production-Thumb locomotion-classifier fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


CLASSIFIER = 0x00067E4C
STATE = RAM_BASE + 0x60000
OUTPUT = RAM_BASE + 0x61000


def build_state(active: bool) -> bytes:
    state = bytearray(0x26E)
    rings = {
        0x02: 500,
        0x12: 300,
        0x22: 100,
        0x32: 1000,
        0x42: 500 if active else 0,
        0x204: 450,
        0x214: 100,
        0x224: 10,
        0x234: 10,
        0x244: 10,
        0x254: 10,
    }
    for offset, value in rings.items():
        struct.pack_into("<8h", state, offset, *([value] * 8))
    state[0x52] = 5
    history = [900] * 200
    if active:
        for index in range(0, 200, 20):
            history[index:index + 5] = [1300] * 5
    struct.pack_into("<200H", state, 0x54, *history)
    struct.pack_into("<5h", state, 0x264, 1001, 1002, 1003, 1004, 1005)
    return bytes(state)


def execute(fixture: LocomotionFirmwareFixture, active: bool) -> dict[str, Any]:
    fixture.uc.mem_write(STATE, build_state(active))
    fixture.uc.mem_write(OUTPUT, b"\xA5" * 0x3E)
    result = fixture.call(CLASSIFIER, STATE, OUTPUT)
    output = bytes(fixture.uc.mem_read(OUTPUT, 0x3E))
    trend_history = bytes(fixture.uc.mem_read(STATE + 0x264, 10))
    return {
        "return": result,
        "feature_bits": [
            f"0x{struct.unpack_from('<I', output, offset)[0]:08x}"
            for offset in (0x00, 0x04, 0x08, 0x0C, 0x10, 0x14)
        ],
        "autocorrelation_bits": [
            f"0x{struct.unpack_from('<I', output, offset)[0]:08x}"
            for offset in (0x20, 0x28, 0x2C, 0x30, 0x34)
        ],
        "reserved_24": f"0x{struct.unpack_from('<I', output, 0x24)[0]:08x}",
        "flags": list(output[0x38:0x3E]),
        "trend_history_i16": list(struct.unpack("<5h", trend_history)),
    }


def run(image: bytes) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    inactive = execute(fixture, False)
    active = execute(fixture, True)

    assert inactive == {
        "return": 0,
        "feature_bits": [
            "0x42c80000", "0x43fa0000", "0x447a0000",
            "0x43960000", "0x00000000", "0x00000000",
        ],
        "autocorrelation_bits": [
            "0xbf800000", "0xbf800000", "0x00000000",
            "0x00000000", "0x00000000",
        ],
        "reserved_24": "0xa5a5a5a5",
        "flags": [255, 255, 1, 255, 1, 255],
        "trend_history_i16": [1002, 1003, 1004, 1005, 2274],
    }
    assert active == {
        "return": 0,
        "feature_bits": [
            "0x42c80000", "0x43fa0000", "0x447a0000",
            "0x43960000", "0x42960000", "0x42f9ffff",
        ],
        "autocorrelation_bits": [
            "0x3f800000", "0x3f800000", "0x42960000",
            "0x42960f02", "0x42960f02",
        ],
        "reserved_24": "0xa5a5a5a5",
        "flags": [1, 1, 1, 255, 1, 1],
        "trend_history_i16": [1002, 1003, 1004, 1005, 1732],
    }
    return {
        "fixture_groups": 2,
        "inactive": inactive,
        "active": active,
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
