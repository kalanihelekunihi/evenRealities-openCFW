#!/usr/bin/env python3
"""Pin the R1 sleep.db iterator and synchronization-marker writer.

This analyzer reads only the supplied firmware image. It never executes firmware, calls a
partition operation, connects to a ring, emits a storage event, or accesses health data.
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
    (0x0005B39C, 0x0005B578):
        "fbb51a9d383d7a4e3632b69801f9de7cff267d7528238968a7149d1a68eff96e",
    (0x0005B6F4, 0x0005B7D8):
        "6839d24e4015e2c0504547343f2eae799b02263853968d7b0004bbc801378a14",
}

EXPECTED_BRANCHES = {
    0x0005B39C: [0x0008B828],
    0x0005B6F4: [0x0008E1EA],
}

EXPECTED_LITERALS = {
    0x0005B578: 0x000C44FC,
    0x0005B57C: 0x000C441C,
    0x0005B580: 0x200067B4,
    0x0005B61C: 0x11223344,
    0x0005B7D8: 0x000C44FC,
    0x0005B7DC: 0x000C441C,
    0x0005B7E0: 0x11223344,
    0x0005B7E4: 0x200067B4,
}

EXPECTED_STRINGS = {
    0x0005B584: b"[RING]sleep storage iter callback is null\x00",
    0x0005B5B0: b"sleep storage iter callback is null\x00",
    0x0005B5D4: b"[RING]sleep storage iter malloc fail\x00",
    0x0005B5FC: b"sleep storage iter malloc fail\x00",
    0x0005B620: b"[RING]sleep storage iter data size too large, offset: %08X\x00",
    0x0005B65C: b"sleep storage iter data size too large, offset: %08X\x00",
    0x0005B694: b"[RING]sleep storage iter crc error, offset: %08X\x00",
    0x0005B6C8: b"sleep storage iter crc error, offset: %08X\x00",
    0x0005B7E8: b"[RING]sync status buffer is null\x00",
    0x0005B80C: b"sync status buffer is null\x00",
    0x0005B828: b"[RING]sleep storage write synchronize to head fail:%d\x00",
    0x0005B860: b"sleep storage write synchronize to head fail:%d\x00",
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
        "iterator": {
            "arguments": "skip-synchronized raw value, callback, caller context",
            "allocation_bytes": 232,
            "scan": "physical sectors, then eight 24-byte headers per sector",
            "termination": "stop each sector when either copied timestamp is erased",
            "skip_policy": (
                "any nonzero skip flag omits records whose marker equals 0x11223344"
            ),
            "oversized_policy": "aligned lengths above 232 are logged and skipped",
            "read_callback_results": "ignored for header and payload reads",
            "crc_failure": (
                "emit private event 0x2002, return zero, abort all iteration, and free"
            ),
            "callback_zero": "stop all iteration but preserve successful return value one",
            "callback_metadata": (
                "eight bytes: synchronized boolean, three zero padding bytes, "
                "absolute 24-byte header address"
            ),
        },
        "marker_writer": {
            "arguments": "context buffer and byte count; void return",
            "context_bytes": 12,
            "count": "low8(byte count / 12); partial tail ignored",
            "context": "absolute header address, expected start, expected end",
            "read_bytes": 24,
            "read_callback_result": "ignored",
            "eligibility": "stored start and end both equal expected values",
            "write": "four-byte 0x11223344 marker at absolute header address + 20",
            "write_failure": "log only; continue remaining contexts without retry",
            "address_validation": "none in production",
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "physical_flash_reads": False,
            "physical_flash_writes_or_erases": False,
            "private_storage_events_emitted": False,
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
