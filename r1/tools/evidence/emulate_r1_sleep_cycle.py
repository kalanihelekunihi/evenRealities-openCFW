#!/usr/bin/env python3
"""Execute isolated production-Thumb sleep-cycle coordinator fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Callable

from emulate_r1_locomotion_window import (
    IMAGE_SHA256,
    LocomotionFirmwareFixture,
    RAM_BASE,
)


COORDINATOR = 0x00060B80
STATE = RAM_BASE + 0x68000
CURRENT_TIME = RAM_BASE + 0x68200
TIMEZONE = RAM_BASE + 0x68210
MINUTE_RECORD = RAM_BASE + 0x68220
LOWER_RECORD = RAM_BASE + 0x68230
ACTIVE_RECORD = RAM_BASE + 0x68250
RING_SAMPLE = RAM_BASE + 0x68260
UNUSED = RAM_BASE + 0x68270
QUALITY_RECORD = RAM_BASE + 0x68280
OUTPUT = RAM_BASE + 0x682A0
CONFIGURATION = RAM_BASE + 0x682D0


Setup = Callable[[bytearray], None]


def default_policy() -> bytes:
    return struct.pack("<hHBBBB", 1, 60, 1, 0, 24, 0)


def execute(
    image: bytes,
    setup: Setup,
    *,
    elapsed: int,
    current: int,
    minute_sample: float = 0.0,
    ring_sample: float = 0.0,
    active: bool = False,
    upper: bool = False,
    lower: bool = False,
    quality4: bool = False,
    quality6: bool = True,
    initial_output_flags: int = 0,
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(0x13C)
    policy = default_policy()
    state[0x130:0x138] = policy
    struct.pack_into("<I", state, 0x138, CONFIGURATION)
    setup(state)
    fixture.uc.mem_write(STATE, bytes(state))
    fixture.uc.mem_write(CURRENT_TIME, struct.pack("<I", current))
    fixture.uc.mem_write(TIMEZONE, struct.pack("<h", 0))
    fixture.uc.mem_write(MINUTE_RECORD, b"\x00" * 8)
    fixture.uc.mem_write(MINUTE_RECORD + 4, struct.pack("<f", minute_sample))
    fixture.uc.mem_write(LOWER_RECORD, b"\x00" * 0x10)
    fixture.uc.mem_write(LOWER_RECORD + 0xC, bytes([lower]))
    fixture.uc.mem_write(ACTIVE_RECORD, b"\x00" * 8)
    fixture.uc.mem_write(ACTIVE_RECORD + 4, bytes([upper, active]))
    fixture.uc.mem_write(RING_SAMPLE, struct.pack("<f", ring_sample))
    fixture.uc.mem_write(UNUSED, b"\x00" * 4)
    fixture.uc.mem_write(QUALITY_RECORD, b"\x00" * 8)
    fixture.uc.mem_write(QUALITY_RECORD + 4, bytes([quality4, 0, quality6]))
    output = bytearray(0x20)
    output[0x1A] = initial_output_flags
    fixture.uc.mem_write(OUTPUT, bytes(output))
    fixture.uc.mem_write(CONFIGURATION, b"\x00\x00" + policy)
    result = fixture.call(
        COORDINATOR,
        STATE,
        elapsed,
        CURRENT_TIME,
        TIMEZONE,
        MINUTE_RECORD,
        LOWER_RECORD,
        ACTIVE_RECORD,
        RING_SAMPLE,
        UNUSED,
        QUALITY_RECORD,
        OUTPUT,
    )
    final_state = bytes(fixture.uc.mem_read(STATE, 0x138))
    final_output = bytes(fixture.uc.mem_read(OUTPUT, 0x20))
    return {
        "return": result,
        "step": {
            "active_start": struct.unpack_from("<I", final_state, 0xA4)[0],
            "active": final_state[0xA8],
            "activity_latch": final_state[0xA9],
            "clamp_start": struct.unpack_from("<I", final_state, 0xAC)[0],
            "countdown": struct.unpack_from("<I", final_state, 0xB0)[0],
            "forced": final_state[0xB4],
            "local_window": final_state[0xB6],
        },
        "decision": list(final_state[0xB8:0xC0]),
        "current_hex": final_state[0xC0:0xE8].hex(),
        "previous_descriptor_hex": final_state[0xE8:0x110].hex(),
        "previous_interval_hex": final_state[0x110:0x130].hex(),
        "policy_hex": final_state[0x130:0x138].hex(),
        "output_hex": final_output.hex(),
        "state_sha256": hashlib.sha256(final_state).hexdigest(),
    }


def no_setup(state: bytearray) -> None:
    del state


def force_open(state: bytearray) -> None:
    state[0xB4] = 1


def metric_start(state: bytearray) -> None:
    for index in range(15):
        struct.pack_into("<f", state, index * 4, 1.0)
        state[0x48 + index] = 50


def metric_close(state: bytearray) -> None:
    state[0xB8] = 1
    struct.pack_into("<I", state, 0xC0, 1000)
    struct.pack_into("<I", state, 0xC8, 10)
    struct.pack_into("<i", state, 0xD8, 4)
    struct.pack_into("<f", state, 0xDC, 50.0)
    state[0xE4] = 2


def clear_active_clamp(state: bytearray) -> None:
    struct.pack_into("<I", state, 0xAC, 100)


def run(image: bytes) -> dict[str, Any]:
    fixtures = {
        "no_transition": execute(
            image, no_setup, elapsed=10, current=36000,
        ),
        "forced_open": execute(
            image, force_open, elapsed=0, current=1000,
            initial_output_flags=4,
        ),
        "metric_open": execute(
            image, metric_start, elapsed=0, current=1000,
            minute_sample=1.0, ring_sample=50.0,
            initial_output_flags=4,
        ),
        "metric_close": execute(
            image, metric_close, elapsed=0, current=2000,
            ring_sample=50.0, initial_output_flags=4,
        ),
        "active_clamp_clear": execute(
            image, clear_active_clamp, elapsed=0, current=1000,
            active=True,
        ),
    }
    expected = {
        "no_transition": {
            "state_sha256":
                "fe22ef96952d834a012093dc1d38bf9c02b47158983ff04687014f3ecf6b73e6",
            "decision": [0, 0, 7, 0, 0, 0, 0, 0],
            "output_hex":
                "0000000000000000000000000000000000000000000000000000000700000000",
            "step": {
                "active_start": 0, "active": 0, "activity_latch": 0,
                "clamp_start": 36000, "countdown": 290, "forced": 0,
                "local_window": 1,
            },
        },
        "forced_open": {
            "state_sha256":
                "404b0be8fb850ef3a3590786e8d8d748e2cce85af3814ee0d6376b7e1a43bd60",
            "decision": [1, 4, 5, 0, 0, 0, 0, 0],
            "output_hex":
                "0000000000000000000000000000000000000000000000000000030500000000",
            "step": {
                "active_start": 0, "active": 0, "activity_latch": 0,
                "clamp_start": 0, "countdown": 0, "forced": 0,
                "local_window": 1,
            },
        },
        "metric_open": {
            "state_sha256":
                "398051cd5ba366c5188cc3a1630fcb8b787bb0813dfafcae058747e217979877",
            "decision": [1, 2, 0, 0, 0, 0, 0, 0],
            "output_hex":
                "0000000000000000000000000000000000000000000000000000030000000000",
            "step": {
                "active_start": 0, "active": 0, "activity_latch": 0,
                "clamp_start": 0, "countdown": 0, "forced": 0,
                "local_window": 1,
            },
        },
        "metric_close": {
            "state_sha256":
                "d988fccdfc8ef2667ddffd361207fb8812eeeb9b9ba909183c624a5a65351fd1",
            "decision": [0, 1, 1, 0, 0, 0, 0, 0],
            "output_hex":
                "e8030000c6070000e8030000d007000000000000e803000000000c0103020000",
            "step": {
                "active_start": 0, "active": 0, "activity_latch": 0,
                "clamp_start": 0, "countdown": 0, "forced": 0,
                "local_window": 0,
            },
        },
        "active_clamp_clear": {
            "state_sha256":
                "41c7c673e0b867ced3932628684b26e4872717999525d8179e493b47b471e425",
            "decision": [0, 0, 4, 0, 251, 255, 255, 255],
            "output_hex":
                "0000000000000000000000000000000000000000000000000000000400000000",
            "step": {
                "active_start": 1000, "active": 1, "activity_latch": 1,
                "clamp_start": 0, "countdown": 0, "forced": 0,
                "local_window": 1,
            },
        },
    }
    for name, expected_fields in expected.items():
        for field, expected_value in expected_fields.items():
            assert fixtures[name][field] == expected_value
    return {
        "image_sha256": IMAGE_SHA256,
        "fixture_groups": len(fixtures),
        "fixtures": fixtures,
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
