#!/usr/bin/env python3
"""Validate the production cumulative-activity producer and explicit refresh service.

This parser is static and read-only. It does not execute firmware, connect to BLE, read a physical
sensor or SRAM, publish an event, mutate flash, or access a host health store.
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


RANGES = {
    (0x48D48, 0x48D96): "b807b4e462d853fe5044855ff754544bc03b523dcbf68f8de44e837184bec661",
    (0x48D9C, 0x48DFC): "610e7b2d98a33ae6c0f84e39a6213743aad1b4c11cee7d4589121da0da9d1190",
    (0x48E68, 0x48FE4): "9e8d594396de8cfaac2ec0bb9b6b66e954b1c07dbb8447da87bd362611fbb0fe",
    (0x49068, 0x49164): "a5436baeea82dcfdcd92ffa967adab36803e28864c6d6f0e32d3989ba3dcdbde",
    (0x491BC, 0x491CC): "065dd491ac13c9c34c5c2d60094aea54c85f5f7136f156546af62e4fa8f5696c",
    (0x4EDDC, 0x4EE00): "ea7fcb6fa0bb8e5b9d931e0ac6fd10e999f51e5a16995af376cbb21ea843dd2f",
    (0x5AA14, 0x5AB0A): "90c63f8ffa27c90d548d4f0bb7f1400cf354a3aa8833e3314a249a61d7ca7f82",
}

BRANCHES = {
    0x48D48: [0x3C3FC],
    0x48D9C: [0x4A240],
    0x48E68: [0x6C2E2],
    0x49068: [0x42108],
    0x491BC: [0x4EDE0],
}

LITERALS = {
    0x48D98: 0x20006ECC,
    0x48DFC: 0x20006EBC,
    0x48FEC: 0x20006EBC,
    0x49164: 0x20006EBC,
    0x491CC: 0x20006EBC,
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image sha256: {digest}")

    ranges = []
    for (start, end), wanted in RANGES.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != wanted:
            raise ValueError(f"range 0x{start:x}...0x{end:x}: {actual}")
        ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual,
        })

    branches: dict[str, list[str]] = {}
    for target, wanted in BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != wanted:
            raise ValueError(f"branches to 0x{target:x}: {actual}")
        branches[f"0x{target:08x}"] = [f"0x{address:08x}" for address in actual]

    literals: dict[str, str] = {}
    for address, wanted in LITERALS.items():
        actual = struct.unpack("<I", flash_bytes(image, base, address, address + 4))[0]
        if actual != wanted:
            raise ValueError(f"literal 0x{address:x}: 0x{actual:x}")
        literals[f"0x{address:08x}"] = f"0x{actual:08x}"

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "state": {
            "address": "0x20006ebc",
            "bytes": 24,
            "fields": [
                "window-published raw byte +0",
                "transition-pending raw byte +1",
                "reserved UInt16LE +2",
                "transition-start timestamp UInt32LE +4",
                "baseline steps UInt32LE +8",
                "baseline all-kcal UInt16LE +12",
                "baseline active-kcal UInt16LE +14",
                "current steps UInt32LE +16",
                "current all-kcal UInt16LE +20",
                "current active-kcal UInt16LE +22",
            ],
        },
        "periodic_producer": {
            "address": "0x00048e68",
            "input_record": "steps UInt32LE, all-kcal UInt16LE, active-kcal UInt16LE",
            "cleans_baseline_at_exact_local_day_start": True,
            "window_seconds": 600,
            "publication_remainder_seconds": "595...599",
            "writes_window_published": True,
            "rollback_policy": "rebase without event and mark window published",
        },
        "explicit_refresh": {
            "address": "0x00049068",
            "uses_last_current_snapshot": True,
            "publication_remainder_seconds": "0...599",
            "writes_window_published": False,
            "returns_public_response": False,
            "rollback_policy": "rebase without event",
        },
        "shared_availability": {
            "eligible": "sleep-result status != 1 and wear-fusion state == 2",
            "unavailable": "sleep-result status == 1 or wear-fusion state == 0",
            "transitional":
                "sleep-result status != 1 and wear-fusion state is nonzero/non-2",
            "transition_grace_seconds_inclusive": 900,
            "transition_rebase_at_elapsed_seconds": 901,
        },
        "event_11": {
            "bytes": 12,
            "fields": [
                "all-kcal delta UInt16LE",
                "active-kcal delta UInt16LE",
                "steps delta low UInt16LE",
                "duration within current ten-minute window UInt16LE",
                "firmware timestamp UInt32LE",
            ],
            "zero_delta_is_publishable": True,
        },
        "packed_cache_correction": {
            "packed_fields": "steps[11:0], active-kcal[21:12], all-kcal[31:22]",
            "daily_item": "bucket, steps, active-kcal, all-kcal",
            "first_party_disposition": "skips active-kcal and presents bytes 5...6 as allKcal",
            "source_is_firmware_image_only": False,
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "sram_access": False,
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
