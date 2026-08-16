#!/usr/bin/env python3
"""Execute the production-Thumb GoMore sleep graph builders in isolated RAM."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import (
    IMAGE_SHA256,
    LocomotionFirmwareFixture,
    RAM_BASE,
)


FAMILY_ZERO_BUILDER = 0x0002874C
FAMILY_NONZERO_BUILDER = 0x0002966C
GRAPH = RAM_BASE + 0x6A000
MODEL = RAM_BASE + 0x6B000
GRAPH_BYTES = 0x1B8


def model_words(count: int, seed: int) -> list[int]:
    return [
        (seed + index * 0x01020305) & 0xFFFFFFFF
        for index in range(count)
    ]


def execute(image: bytes, family: int) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    count = {0: 1714, 1: 952, 2: 1092}[family]
    words = model_words(count, 0x3E800000 + family * 0x00100000)
    fixture.uc.mem_write(MODEL, struct.pack(f"<{count}I", *words))
    fixture.uc.mem_write(GRAPH, b"\xA5" * GRAPH_BYTES)
    if family == 0:
        end = fixture.call(FAMILY_ZERO_BUILDER, GRAPH, MODEL)
    else:
        end = fixture.call(FAMILY_NONZERO_BUILDER, family, GRAPH, MODEL)
    graph = bytes(fixture.uc.mem_read(GRAPH, GRAPH_BYTES))
    return {
        "family": family,
        "model_words": count,
        "return": f"0x{end:08x}",
        "graph_sha256": hashlib.sha256(graph).hexdigest(),
        "quantizer_words": [
            f"0x{word:08x}" for word in struct.unpack_from("<3I", graph, 0)
        ],
        "first_aligned_header": graph[0x0C:0x14].hex(),
        "first_add_words": [
            f"0x{word:08x}" for word in struct.unpack_from("<4I", graph, 0x78)
        ],
        "second_add_words": [
            f"0x{word:08x}" for word in struct.unpack_from("<4I", graph, 0xE0)
        ],
        "tail_headers": {
            "parallel": graph[0x144:0x14C].hex(),
            "serial": graph[0x18C:0x194].hex(),
        },
        "padding_words": [
            f"0x{struct.unpack_from('<I', graph, offset)[0]:08x}"
            for offset in (0x74, 0xDC, 0x1A4)
        ],
    }


def run(image: bytes) -> dict[str, Any]:
    fixtures = {
        "family_zero": execute(image, 0),
        "family_one": execute(image, 1),
        "family_two": execute(image, 2),
    }
    expected = {
        "family_zero": {
            "return": "0x2006cac8",
            "graph_sha256":
                "1075666dfa6fd86a99c441c7a75944838b082100dc0464bd0dc080c2412e49e7",
            "quantizer_words": ["0x00000000", "0x3f800000", "0x000293fd"],
            "first_aligned_header": "05010202041b0100",
            "first_add_words": [
                "0x00000000", "0x4e9e2e3c", "0x4fa03141", "0x00036c7d",
            ],
            "second_add_words": [
                "0x00000000", "0x1c389638", "0x1d3a993d", "0x00036c7d",
            ],
            "tail_headers": {
                "parallel": "010100001b080100",
                "serial": "010100000b080100",
            },
        },
        "family_one": {
            "return": "0x2006bee0",
            "graph_sha256":
                "bf42bd75d49bde7b185e2223754fa717b7f7e6fa628790957e2c3878eb7193fc",
            "quantizer_words": ["0x3e900000", "0x3f920305", "0x000293fd"],
            "first_aligned_header": "0501020204200100",
            "first_add_words": [
                "0x00000000", "0x9031f38b", "0x9133f690", "0x00036c7d",
            ],
            "second_add_words": [
                "0x00000000", "0x0f2f7001", "0x10317306", "0x00036c7d",
            ],
            "tail_headers": {
                "parallel": "0101000020040100",
                "serial": "0101000001040100",
            },
        },
        "family_two": {
            "return": "0x2006c110",
            "graph_sha256":
                "057ed06b4bcbe805a73207688662d764b3ccc876e9b381c524ca28beb915a9c8",
            "quantizer_words": ["0x3ea00000", "0x3fa20305", "0x000293fd"],
            "first_aligned_header": "0501020204200100",
            "first_add_words": [
                "0x00000000", "0x9041f38b", "0x9143f690", "0x00036c7d",
            ],
            "second_add_words": [
                "0x00000000", "0x0f3f7001", "0x10417306", "0x00036c7d",
            ],
            "tail_headers": {
                "parallel": "0101000020080100",
                "serial": "0101000001080100",
            },
        },
    }
    for name, expected_fields in expected.items():
        for field, expected_value in expected_fields.items():
            assert fixtures[name][field] == expected_value
        assert fixtures[name]["padding_words"] == ["0xa5a5a5a5"] * 3
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
