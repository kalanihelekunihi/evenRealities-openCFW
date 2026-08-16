#!/usr/bin/env python3
"""Execute isolated production-Thumb sleep-stage decision fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any, Callable

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


DECIDER = 0x0005C19C
OUTPUT = RAM_BASE + 0x66000
STATE = RAM_BASE + 0x66104
REFERENCE = RAM_BASE + 0x66200
PRIOR = RAM_BASE + 0x66210
EXTERNAL = RAM_BASE + 0x66220


def execute(
    fixture: LocomotionFirmwareFixture,
    setup: Callable[[bytearray, int], None],
    *,
    current: int = 1000,
    elapsed: int = 0,
    reference: int = 0,
    prior: int = 0,
    external: int = 0,
    preceding_fraction: float = 0.0,
) -> dict[str, Any]:
    storage = bytearray(0xBB)
    struct.pack_into("<f", storage, 0, preceding_fraction)
    setup(storage, 4)
    fixture.uc.mem_write(STATE - 4, bytes(storage))
    fixture.uc.mem_write(OUTPUT, b"\xA5" * 8)
    fixture.uc.mem_write(REFERENCE, struct.pack("<I", reference))
    fixture.uc.mem_write(PRIOR, bytes([prior]))
    fixture.uc.mem_write(EXTERNAL, b"\x00" * 6)
    fixture.uc.mem_write(EXTERNAL + 5, bytes([external]))
    fixture.call(
        DECIDER, OUTPUT, STATE, current, elapsed,
        REFERENCE, PRIOR, EXTERNAL,
    )
    output = bytes(fixture.uc.mem_read(OUTPUT, 8))
    return {
        "record": list(output[:4]),
        "adjustment": struct.unpack_from("<i", output, 4)[0],
    }


def no_setup(storage: bytearray, base: int) -> None:
    del storage, base


def metrics_setup(
    storage: bytearray, base: int, fraction: float = 1.0, value: int = 50
) -> None:
    for index in range(15):
        struct.pack_into("<f", storage, base + index * 4, fraction)
        storage[base + 0x48 + index] = value
    struct.pack_into("<I", storage, base + 0xAC, 0)


def run(image: bytes) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)

    def set_byte(offset: int, value: int) -> Callable[[bytearray, int], None]:
        def setup(storage: bytearray, base: int) -> None:
            storage[base + offset] = value
        return setup

    def set_word(offset: int, value: int) -> Callable[[bytearray, int], None]:
        def setup(storage: bytearray, base: int) -> None:
            struct.pack_into("<I", storage, base + offset, value)
        return setup

    fixtures = {
        "forced_stage": execute(fixture, set_byte(0xB4, 1)),
        "countdown": execute(fixture, set_word(0xB0, 1), prior=1),
        "external": execute(fixture, no_setup, external=1),
        "elapsed": execute(fixture, no_setup, elapsed=601),
        "reference_timeout": execute(
            fixture, no_setup, current=0xA8C0, prior=1
        ),
        "transition_block": execute(fixture, set_byte(0xA8, 1)),
        "metric_start": execute(fixture, metrics_setup),
        "metric_average_reject": execute(
            fixture,
            lambda storage, base: metrics_setup(storage, base, value=100),
        ),
        "metric_low_fraction": execute(
            fixture,
            lambda storage, base: metrics_setup(storage, base, fraction=0.0),
            current=120,
            prior=1,
        ),
    }
    assert fixtures == {
        "forced_stage": {"record": [1, 4, 5, 0], "adjustment": 0},
        "countdown": {"record": [1, 0, 7, 0], "adjustment": 0},
        "external": {"record": [0, 0, 6, 0], "adjustment": 0},
        "elapsed": {"record": [0, 0, 3, 0], "adjustment": -10},
        "reference_timeout": {"record": [0, 1, 8, 0], "adjustment": 0},
        "transition_block": {"record": [0, 0, 4, 0], "adjustment": -15},
        "metric_start": {"record": [1, 2, 0, 0], "adjustment": 0},
        "metric_average_reject": {
            "record": [0, 0, 2, 0], "adjustment": 0,
        },
        "metric_low_fraction": {
            "record": [0, 1, 1, 0], "adjustment": 0,
        },
    }
    return {
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
