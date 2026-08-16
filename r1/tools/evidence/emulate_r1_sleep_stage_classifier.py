#!/usr/bin/env python3
"""Assert the stock 0x88450 fixed sleep-stage classifier contract."""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


SLEEP_ENGINE_OPEN = 0x00090F44
SLEEP_STAGE_CLASSIFIER = 0x00088450
STATE = RAM_BASE + 0x50000
OUTPUT = RAM_BASE + 0x53000
STATE_BYTES = 8440
LOAD_BASE = 0x00027000


def word(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address - LOAD_BASE)[0]


def descriptor(image: bytes, base: int, offset: int) -> dict[str, Any]:
    position = base + offset - LOAD_BASE
    pointer, count = struct.unpack_from("<II", image, position)
    dimensions = struct.unpack_from("<3H", image, position + 8)
    flags = image[position + 14]
    scale_bits = struct.unpack_from("<I", image, position + 16)[0]
    return {
        "offset": f"0x{offset:03x}",
        "data": f"0x{pointer:08x}",
        "count": count,
        "dimensions": list(dimensions[:flags & 3]),
        "flags": f"0x{flags:02x}",
        "scale_bits": f"0x{scale_bits:08x}",
    }


def model_schema(image: bytes, base: int) -> dict[str, Any]:
    offsets = [index * 20 for index in range(51)]
    records = [descriptor(image, base, offset) for offset in offsets]
    return {
        "base": f"0x{base:08x}",
        "record_count": len(records),
        "parameter_bytes":
            int(records[-1]["data"], 16) + records[-1]["count"] * 2 -
            int(records[0]["data"], 16),
        "records": records,
    }


def samples(kind: str) -> list[float]:
    if kind == "zero":
        return [0.0] * 90
    if kind == "ramp":
        return [index / 90.0 for index in range(90)]
    if kind == "sine":
        return [math.sin(index * 0.2) for index in range(90)]
    raise ValueError(kind)


def execute(image: bytes, mode: int, kind: str, calls: int = 1) -> dict[str, Any]:
    machine = LocomotionFirmwareFixture(image)
    state = bytearray(STATE_BYTES)
    state[8437] = mode
    for index, value in enumerate(samples(kind)):
        struct.pack_into("<f", state, 1004 + index * 4, value)
    machine.uc.mem_write(STATE, bytes(state))
    machine.call(SLEEP_ENGINE_OPEN, STATE)
    results = []
    for _ in range(calls):
        machine.uc.mem_write(OUTPUT, b"\xa5" * 20)
        machine.call(SLEEP_STAGE_CLASSIFIER, OUTPUT, STATE, 1)
        record = bytes(machine.uc.mem_read(OUTPUT, 20))
        probabilities = struct.unpack_from("<4f", record)
        results.append({
            "probability_bits": [
                f"0x{word:08x}"
                for word in struct.unpack_from("<4I", record)
            ],
            "probabilities": list(probabilities),
            "selected": record[16],
            "sum": sum(probabilities),
        })
    return {"mode": mode, "samples": kind, "calls": results}


def pending(image: bytes) -> dict[str, Any]:
    machine = LocomotionFirmwareFixture(image)
    machine.uc.mem_write(STATE, bytes(STATE_BYTES))
    machine.call(SLEEP_ENGINE_OPEN, STATE)
    before = bytes(machine.uc.mem_read(STATE, STATE_BYTES))
    machine.uc.mem_write(OUTPUT, b"\xa5" * 20)
    machine.call(SLEEP_STAGE_CLASSIFIER, OUTPUT, STATE, 2)
    after = bytes(machine.uc.mem_read(STATE, STATE_BYTES))
    return {
        "record": bytes(machine.uc.mem_read(OUTPUT, 20)).hex(),
        "state_bytes_changed": sum(
            left != right for left, right in zip(before, after)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    model_bases = [word(image, 0x00088860), word(image, 0x00088864)]
    assert model_bases == [0x000B1C4C, 0x000B2048]
    schemas = [model_schema(image, base) for base in model_bases]
    expected_shapes = {
        0x000: (12, [4, 1, 3]),
        0x064: (96, [8, 4, 3]),
        0x0C8: (192, [8, 8, 3]),
        0x12C: (192, [8, 8, 3]),
        0x190: (192, [8, 8, 3]),
        0x1F4: (192, [8, 8, 3]),
        0x258: (192, [8, 8, 3]),
        0x2BC: (3840, [32, 120]),
        0x2E4: (1024, [32, 32]),
        0x30C: (3072, [96, 32]),
        0x320: (3072, [96, 32]),
        0x334: (3072, [96, 32]),
        0x348: (3072, [96, 32]),
        0x35C: (96, [96]),
        0x370: (96, [96]),
        0x384: (96, [96]),
        0x398: (96, [96]),
        0x3AC: (1024, [32, 32]),
        0x3D4: (128, [4, 32]),
        0x3E8: (4, [4]),
    }
    for schema in schemas:
        assert schema["record_count"] == 51
        assert schema["parameter_bytes"] == 21824
        by_offset = {
            int(record["offset"], 16): record
            for record in schema["records"]
        }
        for offset, (count, dimensions) in expected_shapes.items():
            assert by_offset[offset]["count"] == count
            assert by_offset[offset]["dimensions"] == dimensions

    fixtures = {
        "mode0_zero_recurrent": execute(image, 0, "zero", 2),
        "mode0_ramp": execute(image, 0, "ramp"),
        "mode0_sine": execute(image, 0, "sine"),
        "mode100_zero_recurrent": execute(image, 100, "zero", 2),
        "mode100_ramp": execute(image, 100, "ramp"),
        "mode100_sine": execute(image, 100, "sine"),
    }
    expected_first_bits = {
        "mode0_zero_recurrent": [
            "0x3d2121fc", "0x3e10107d", "0x3f001497", "0x3ea3aa54"
        ],
        "mode0_ramp": [
            "0x3e060792", "0x3e761d0f", "0x3ec02e66", "0x3e81bf48"
        ],
        "mode0_sine": [
            "0x3e806b3d", "0x3dfaaad3", "0x3ee66324", "0x3e350dd8"
        ],
        "mode100_zero_recurrent": [
            "0x3b1bf200", "0x3e4d39ad", "0x3ef94762", "0x3e9ee3e3"
        ],
        "mode100_ramp": [
            "0x3da09fa0", "0x3e8e3583", "0x3ebe7b30", "0x3e8b2764"
        ],
        "mode100_sine": [
            "0x3e8468f6", "0x3e3ed4c4", "0x3eb92d12", "0x3e45ff31"
        ],
    }
    for name, fixture in fixtures.items():
        first = fixture["calls"][0]
        assert first["probability_bits"] == expected_first_bits[name]
        assert first["selected"] == 2
        assert 0.999999 < first["sum"] < 1.000001
    assert fixtures["mode0_zero_recurrent"]["calls"][1][
        "probability_bits"
    ] == ["0x3d7f04a0", "0x3dfc5e4a", "0x3f00cfb4", "0x3e9f6870"]
    assert fixtures["mode100_zero_recurrent"]["calls"][1][
        "probability_bits"
    ] == ["0x3a9ffb00", "0x3e3b467f", "0x3f004ba3", "0x3ea1257e"]
    pending_fixture = pending(image)
    assert pending_fixture == {
        "record": "0000803f00000000000000000000000000000000",
        "state_bytes_changed": 4,
    }

    print(json.dumps({
        "function": "0x00088450",
        "fixtures": fixtures,
        "model_schemas": schemas,
        "non_first_iteration": pending_fixture,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
