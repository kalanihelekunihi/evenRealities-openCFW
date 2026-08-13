#!/usr/bin/env python3
"""Validate the R1 final-sleep predicate, low-power path, and GoMore publisher."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


EXPECTED_RANGES = {
    (0x0004A3E8, 0x0004A440):
        "12a06e087ffac257a35968f3956c65a90abd2cb994965016ad948d3981a43d93",
    (0x0004A5BC, 0x0004A652):
        "e891b4c517a099fc65814f4b90184b35da5211ae7c447cb40611931a48b00a59",
    (0x0004A704, 0x0004A78A):
        "27704d1f5294b814fd2ba6be219f3dd716876ff3645ff96585d1ef9a225944d6",
    (0x0006B50C, 0x0006B64A):
        "a4becd15f14171d74d4321de59447ba8aae9e480e79d0f39bd0ebdaf1b8b5dfd",
    (0x0006C294, 0x0006C452):
        "9542debc41ea37d4d496a8e985df1f13545b0593471f74c1ef4b2c038a2fe3d9",
}

EXPECTED_BRANCHES = {
    0x0004A3E8: [0x0004A76A],
    0x0004A5BC: [0x000421C0],
    0x0004A704: [0x0006B5FE, 0x0006C3A6],
    0x0004A7F4: [0x0006C32E, 0x0006C36C],
    0x0004C6C0: [0x0004A3EC],
    0x0006B50C: [0x0004A4FE, 0x0004A63E, 0x0004AA7E],
}

EXPECTED_LITERALS = {
    0x0004A478: 0x000C44FC,
    0x0004A47C: 0x000C441C,
    0x0004A678: 0x000C44FC,
    0x0004A67C: 0x000C441C,
    0x0004A69C: 0x20006ED4,
    0x0004A7C0: 0x000C44FC,
    0x0004A7C4: 0x000C441C,
    0x0006C458: 0x2001A56C,
    0x0006C45C: 0x000C44FC,
    0x0006C460: 0x000C441C,
    0x0006C464: 0x20006DC4,
}

EXPECTED_STRINGS = {
    0x0004A440: b"[RING]sleep drop: no living confirm during sleep period\x00",
    0x0004A480: b"sleep drop: no living confirm during sleep period\x00",
    0x0004A654: b"[RING]algo sleep low power event\x00",
    0x0004A680: b"algo sleep low power event\x00",
    0x0006C468: b"[RING]Sleep Period On, %d\x00",
    0x0006C498: b"[RING]Sleep Period Off, %d\x00",
    0x0006C4CC: b"[RING]gomore sensor_malloc failed\x00",
    0x0006C50C: b"[RING]Sleep Stage PPG On\x00",
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + end - start]


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    ranges = []
    for (start, end), expected in EXPECTED_RANGES.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != expected:
            raise ValueError(f"unexpected range 0x{start:08x}...0x{end:08x}: {actual}")
        ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual,
        })

    branches: dict[str, list[str]] = {}
    for target, expected in EXPECTED_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected:
            raise ValueError(f"unexpected branches to 0x{target:08x}: {actual}")
        branches[f"0x{target:08x}"] = [f"0x{address:08x}" for address in actual]

    literals: dict[str, str] = {}
    for address, expected in EXPECTED_LITERALS.items():
        actual = struct.unpack("<I", flash_bytes(image, base, address, address + 4))[0]
        if actual != expected:
            raise ValueError(f"unexpected literal at 0x{address:08x}: 0x{actual:08x}")
        literals[f"0x{address:08x}"] = f"0x{actual:08x}"

    strings: dict[str, str] = {}
    for address, expected in EXPECTED_STRINGS.items():
        actual = flash_bytes(image, base, address, address + len(expected))
        if actual != expected:
            raise ValueError(f"unexpected string at 0x{address:08x}: {actual!r}")
        strings[f"0x{address:08x}"] = expected[:-1].decode("ascii")

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "diagnostic_strings": strings,
        "final_sleep_validation": {
            "living_confirmation_source": "wear runtime +0x02",
            "drop_when_living_confirmation_is_zero": True,
            "drop_when": "type is 1 and compact-stage count at +0x1e is zero",
            "otherwise_publish": True,
            "system_event": "0x000d",
            "payload_length": "UInt16 wrapping addition of 32 and compact-stage count",
            "production_builder_workspace_bytes": 0x0B40,
        },
        "low_power": {
            "required_sleep_status": 1,
            "new_sleep_status": 0,
            "calls_sleep_shutdown": True,
            "requests_final_sleep_result": True,
            "publishes_system_event": "0x000c",
            "published_payload": [0],
        },
        "gomore_output_consumer": {
            "lifecycle_field_offset": "0x70",
            "period_on_bit": "0x02",
            "period_off_bit": "0x04",
            "final_result_ready_bit": "0x08",
            "period_on_precedes_period_off": True,
            "final_result_nested_under_period_off": True,
            "ppg_request_field_offset": "0x62",
            "ppg_authorization_mode": 4,
            "final_result_workspace_bytes": 0x0B40,
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
            "health_store_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image, args.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
