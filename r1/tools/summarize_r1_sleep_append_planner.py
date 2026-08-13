#!/usr/bin/env python3
"""Pin the production R1 sleep.db append/retry/rollover/reset implementation.

This analyzer is static and read-only. It never executes firmware, connects to a ring, reads a
health store, invokes BLE, writes flash, selects a live sector, or calls the reset wrapper.
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


APPEND_START = 0x0005B890
APPEND_END = 0x0005B9AC
EXPECTED_APPEND_SHA256 = (
    "817a0854d1adce8db5bdbde8eb88bc34f235a5ebde7308ff576bb279623eaa53"
)

EXPECTED_BRANCHES = {
    0x0005B2F8: [0x0005B246, 0x0005B94A, 0x0008DD88],
    0x0005B890: [0x0008DCB0],
    0x0008FC6C: [0x0005B920],
    0x0008FE28: [0x0005B8C0],
    0x0008FE98: [0x0005B92C],
}

EXPECTED_LITERALS = {
    0x0005B9AC: 0x200067B4,
    0x0005B9B0: 0x000C44FC,
    0x0005B9B4: 0x000C441C,
}

EXPECTED_STRINGS = {
    0x0005B9B8: b"[RING]sleep storage not init\x00",
    0x0005B9F0: b"[RING]sleep storage fail, size too large\x00",
    0x0005BA40: b"[RING]sleep storage write data fail, flash reset\x00",
    0x0005BAA0: b"[RING]sleep storage writable sector: %d\x00",
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    append_digest = hashlib.sha256(
        flash_bytes(image, base, APPEND_START, APPEND_END)
    ).hexdigest()
    if append_digest != EXPECTED_APPEND_SHA256:
        raise ValueError(f"unexpected append function SHA-256: {append_digest}")

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
        "verified_append_range": {
            "start": f"0x{APPEND_START:08x}",
            "end_exclusive": f"0x{APPEND_END:08x}",
            "sha256": append_digest,
        },
        "direct_branches": branches,
        "literals": literals,
        "diagnostic_strings": strings,
        "append_state_machine": {
            "initialized_flag_address": "0x200067b4",
            "record_pointer_must_be_nonzero": True,
            "maximum_payload_bytes_inclusive": 3_888,
            "maximum_write_attempts": 2,
            "attempt_order": [
                "call writable-sector finder 0x0008fe28",
                "if finder returns 0xffffffff, call rollover selector 0x0008fc6c",
                "pass low eight bits of selected result to writer 0x0008fe98",
            ],
            "writer_nonzero_result": "return 1 immediately",
            "two_zero_writer_results": "call reset wrapper 0x0005b2f8 and return 0",
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "physical_flash_reads": False,
            "physical_flash_writes": False,
            "reset_wrapper_calls": False,
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
