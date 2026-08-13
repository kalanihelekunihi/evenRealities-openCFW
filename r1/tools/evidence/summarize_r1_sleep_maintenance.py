#!/usr/bin/env python3
"""Pin R1 sleep.db initialization, record counting, and destructive reset policy.

This analyzer reads only the supplied firmware image. It never executes firmware, connects to a
ring, reads a physical partition, invokes an erase callback, or accesses a health store.
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
    (0x0005B0F8, 0x0005B18A):
        "b228d9b6bfa3574fe2430951f8a9cf8c4610af350ffb4ce03f3b095a46c77255",
    (0x0005B23C, 0x0005B28C):
        "285fac8e97bff70248473cf0f79f00c89566cab4d62dc4790c9f1a55ba21ba92",
    (0x0005B2F8, 0x0005B328):
        "2e8216f009494b6115d22deb8b0dc55e47fe15a342cd54a463750fd8b8c2e80b",
    (0x0005B32C, 0x0005B398):
        "8d19f0e8dd091cd3e72857ddfb1ccaa2a89df9721239ca06627e77328cf461e0",
}

EXPECTED_BRANCHES = {
    0x0005B0F8: [0x0008DD8C],
    0x0005B23C: [0x0008B1D6],
    0x0005B2F8: [0x0005B246, 0x0005B94A, 0x0008DD88],
    0x0005B32C: [0x0005B23E],
}

EXPECTED_LITERALS = {
    0x0005B198: 0x200067B4,
    0x0005B19C: 0x000C44FC,
    0x0005B1A0: 0x000C441C,
    0x0005B2C0: 0x000C44FC,
    0x0005B2C4: 0x000C441C,
    0x0005B328: 0x200067B4,
    0x0005B398: 0x200067B4,
}

EXPECTED_STRINGS = {
    0x0005B18C: b"sleep.db\x00",
    0x0005B1A4: b"[RING]sleep db not find fal partition\x00",
    0x0005B1CC: b"sleep db not find fal partition\x00",
    0x0005B1EC: b"[RING]log flash not find fal flash device\x00",
    0x0005B218: b"log flash not find fal flash device\x00",
    0x0005B28C: b"[RING]sleep storage data delete all, sleep num: %d\x00",
    0x0005B2C8: b"sleep storage data delete all, sleep num: %d\x00",
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
        "maintenance_policy": {
            "initialization": {
                "success": "store partition and flash-device handles, then set initialized byte to 1",
                "partition_lookup_failure": (
                    "clear partition handle; preserve prior initialized byte and flash-device handle"
                ),
                "flash_device_lookup_failure": (
                    "clear partition handle after storing a null device handle; preserve initialized byte"
                ),
            },
            "record_counter": {
                "scan": "physical sectors, then eight physical headers per sector",
                "termination": "stop each sector when either copied timestamp is erased",
                "maximum_official_count": 16,
                "read_callback_result": "ignored",
            },
            "full_reset": {
                "sector_count": "low8(partition length >> 12)",
                "erase_bytes_per_sector": 4_096,
                "erase_callback_results": "ignored",
            },
            "delete_all": "count first; invoke full reset only when record count is nonzero",
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
