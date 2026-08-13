#!/usr/bin/env python3
"""Pin the production R1 sleep.db body/header writer transaction.

This is a static firmware-image analyzer. It does not execute the writer, access a device or
partition, emit health data, invoke BLE, or call any flash write/close operation.
"""

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


WRITER_START = 0x0008FE98
WRITER_END = 0x000901E4
EXPECTED_WRITER_SHA256 = (
    "2b73ed8df03d025e93596cde6e5702ecab6f158057a7af1fb6a7f25ebbb7f5ff"
)

EXPECTED_BRANCHES = {
    0x0005D87C: [
        0x0005892C, 0x00058952, 0x00058972, 0x0005A2A0, 0x0005A316,
        0x0005B4E4, 0x0007334A, 0x0007BC10, 0x0007BD8A, 0x0007EE14,
        0x0007EE4E, 0x0007EE6C, 0x0008301A, 0x0008FFF0, 0x0009178C,
    ],
    0x0008FE98: [0x0005B92C],
    0x000901E4: [0x0008FF7C, 0x0009008E],
}

EXPECTED_LITERALS = {
    0x00090094: 0x200067B4,
    0x00090098: 0x000C44FC,
    0x0009009C: 0x000C441C,
}

EXPECTED_STRINGS = {
    0x000900A0: b"[RING]slp storage is full:%d, %d\x00",
    0x000900C4: b"slp storage is full:%d, %d\x00",
    0x000900E0: b"[RING]sleep storage write data to sector fail:%d\x00",
    0x00090114: b"sleep storage write data to sector fail:%d\x00",
    0x00090140: b"[RING]sleep storage write head to sector fail:%d\x00",
    0x00090174: b"sleep storage write head to sector fail:%d\x00",
    0x000901A4: b"sleep storage write data to sector success:%d, size:%d, cnt:%d\x00",
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    writer_digest = hashlib.sha256(
        flash_bytes(image, base, WRITER_START, WRITER_END)
    ).hexdigest()
    if writer_digest != EXPECTED_WRITER_SHA256:
        raise ValueError(f"unexpected writer function SHA-256: {writer_digest}")

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
        "verified_writer_range": {
            "start": f"0x{WRITER_START:08x}",
            "end_exclusive": f"0x{WRITER_END:08x}",
            "sha256": writer_digest,
        },
        "direct_branches": branches,
        "literals": literals,
        "diagnostic_strings": strings,
        "record_writer": {
            "slots_per_sector": 8,
            "vacancy": "both copied start and end words equal 0xffffffff",
            "alignment": "(requested length + 3) & 0x0000fffc",
            "initial_payload_offset": "0x00d0",
            "next_payload_offset": "previous header offset + aligned length",
            "capacity_rule": "payload offset + aligned length <= 0x1000",
            "transaction_order": [
                "write aligned body",
                "write first 20 bytes of record header",
                "after slot 7 only, write full-sector close header",
            ],
            "record_header_commit_bytes": 20,
            "record_header_fields": (
                "length@0, offset@2, erased-reserved@4, copied UTC offset@6, "
                "start@8, end@12, erased-reserved@16, CRC@18"
            ),
            "synchronization_marker_bytes_written": 0,
            "crc": "CRC-16/MODBUS over aligned source bytes including padding",
            "body_write_failure": "return 0 without header commit",
            "header_write_failure": "return 0; body may remain orphaned",
            "capacity_exhaustion": "request close and return 0, ignoring close result",
            "all_eight_headers_occupied": "return 0 without requesting close",
            "slot_7_return": "sector-closer Boolean result",
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "physical_flash_reads": False,
            "physical_flash_writes_or_erases": False,
            "captured_health_payload_emitted": False,
            "ble_access": False,
            "sensor_access": False,
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
