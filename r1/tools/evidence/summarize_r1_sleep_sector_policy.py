#!/usr/bin/env python3
"""Pin the R1 sleep.db sector-count, finder, rollover, and closer policy.

This analyzer reads only the supplied firmware image. It never executes firmware, connects to a
ring, reads a physical partition, invokes an erase/write callback, or accesses a health store.
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


EXPECTED_RANGES = {
    (0x0008FC6C, 0x0008FD64):
        "686e6fc16de7d8946780deb01c921f1bcc16b2456542962342828e169e733ed3",
    (0x0008FE14, 0x0008FE28):
        "2920c0ce717284fab4d45c81b9b46755415d667d850154bf6cb0ebc4b7e8f9ec",
    (0x0008FE28, 0x0008FE8C):
        "69e470efe0e021888273a12768c06c98b1ae0a5e06b7fefba6605f6b62ffc4ff",
    (0x000901E4, 0x000902A4):
        "1e79879af7116b111a3d6fa2424e9baaee319438ef0d675787aadac492c7ad35",
}

EXPECTED_BRANCHES = {
    0x0008FC6C: [0x0005B920],
    0x0008FE14: [
        0x0005B2FC, 0x0005B332, 0x0005B3B8, 0x0008FC70,
        0x0008FCC0, 0x0008FE2C, 0x0009020E,
    ],
    0x0008FE28: [0x0005B8C0],
    0x000901E4: [0x0008FF7C, 0x0009008E],
}

EXPECTED_LITERALS = {
    0x0008FD64: 0x200067B4,
    0x0008FE24: 0x200067B4,
    0x0008FE8C: 0x200067B4,
    0x0008FE90: 0xCCFFAABB,
    0x0008FE94: 0x66889977,
    0x000902A4: 0x200067B4,
    0x000902A8: 0xCCFFAABB,
    0x000902AC: 0x66889977,
}

EXPECTED_STRINGS = {
    0x0008FD70: b"[RING]sleep storage erase sector out of range\x00",
    0x0008FDA0: b"sleep storage erase sector out of range\x00",
    0x0008FDC8: b"[RING]sleep storage erase offset: %08X\x00",
    0x0008FDF0: b"sleep storage erase offset: %08X\x00",
    0x000902B0: b"[RING]sleep storage write full count: %d\x00",
    0x000902E4: b"sleep storage write full count: %d\x00",
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


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
        "sector_policy": {
            "sector_count": "low8(partition length >> 12); official descriptor yields 2",
            "finder_first_match_predicates": [
                "state word 0 == 0xffffffff",
                "state word 1 == 0xffffffff and close sequence == 0xffffffff",
                "state word 0 == 0xccffaabb and state word 1 != 0x66889977",
            ],
            "finder_no_match_result": "0xffffffff",
            "rollover_selection": (
                "strictly lowest non-erased close sequence; first index wins ties"
            ),
            "rollover_all_erased_sequence_fallback": 0,
            "rollover_requested_erase_bytes": 4_096,
            "closer_header_words": [
                "0xccffaabb", "0x66889977",
                "minimum non-erased close sequence + 1, or 1", "0x00000000",
            ],
            "closer_success": "flash writer result equals zero",
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "physical_flash_reads": False,
            "physical_flash_writes_or_erases": False,
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
