#!/usr/bin/env python3
"""Validate the R1 validated-sleep duration, storage, fallback, and sync chain."""

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


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"

R1_VALIDATED_SLEEP_DELIVERY_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x0005B890,
        "end_exclusive": 0x0005B9AC,
        "size": 284,
        "symbol": "r1_sleep_db_append",
        "role": "two-attempt sleep journal append and rollover policy",
        "sha256": "817a0854d1adce8db5bdbde8eb88bc34f235a5ebde7308ff576bb279623eaa53",
        "callers": ((0x0008DCB0, "BL"),),
        "inventory": "ghidra_functions_csv",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
    {
        "entry": 0x0008DC94,
        "end_exclusive": 0x0008DD18,
        "size": 132,
        "symbol": "r1_sleep_plan_storage_consumer",
        "role": "sleep append result to automatic-sync trigger orchestration",
        "sha256": "5c5baba208acd202ffc19aad32ad644b708259ff6989b976af31c93b8bad429b",
        "callers": ((0x00042BC6, "B.W"), (0x0008DF3C, "B.W")),
        "inventory": "ghidra_functions_csv",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
    {
        "entry": 0x0008DD90,
        "end_exclusive": 0x0008DF42,
        "size": 434,
        "symbol": "r1_sleep_plan_validated_delivery",
        "role": "one-hour sleep admission, storage-event, and fallback policy",
        "sha256": "5f375de1093b593b9df32fa774b51ffa063e7086884562e01633838373530e6c",
        "callers": ((0x00042960, "B.W"),),
        "inventory": "ghidra_functions_csv",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
)


EXPECTED_RANGES = {
    (0x0005B890, 0x0005B9AC):
        "817a0854d1adce8db5bdbde8eb88bc34f235a5ebde7308ff576bb279623eaa53",
    (0x0008DC94, 0x0008DD18):
        "5c5baba208acd202ffc19aad32ad644b708259ff6989b976af31c93b8bad429b",
    (0x0008DD90, 0x0008DF42):
        "5f375de1093b593b9df32fa774b51ffa063e7086884562e01633838373530e6c",
}

EXPECTED_BRANCHES = {
    0x0005B2F8: [0x0005B246, 0x0005B94A, 0x0008DD88],
    0x0005B890: [0x0008DCB0],
    0x0008B138: [
        0x0008A804, 0x0008A838, 0x0008A860, 0x0008A8D2, 0x0008DCBC,
    ],
    0x0008DC94: [0x00042BC6, 0x0008DF3C],
    0x0008DD90: [0x00042960],
    0x0008FC6C: [0x0005B920],
    0x0008FE28: [0x0005B8C0],
    0x0008FE98: [0x0005B92C],
}

EXPECTED_LITERALS = {
    0x0005B9AC: 0x200067B4,
    0x0005B9B0: 0x000C44FC,
    0x0005B9B4: 0x000C441C,
    0x0008DD18: 0x000C44FC,
    0x0008DD1C: 0x000C441C,
    0x0008DF70: 0x000C44FC,
    0x0008DF74: 0x000C441C,
}

EXPECTED_STRINGS = {
    0x0005B9B8: b"[RING]sleep storage not init\x00",
    0x0005B9F0: b"[RING]sleep storage fail, size too large\x00",
    0x0005BA40: b"[RING]sleep storage write data fail, flash reset\x00",
    0x0005BAA0: b"[RING]sleep storage writable sector: %d\x00",
    0x0008DD20: b"[RING]sleep data is null\x00",
    0x0008DD50: b"[RING]sleep data storage fail\x00",
    0x0008DF44: b"[RING]sleep %d-%d, type:%d, numStages:%d\x00",
    0x0008E0C8: b"[RING]sleep time is small than 1 hours\x00",
    0x0008E114: b"[RING]sleep storage msg send fail\x00",
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

    functions = []
    for function in R1_VALIDATED_SLEEP_DELIVERY_FUNCTIONS:
        entry = int(function["entry"])
        body = flash_bytes(image, base, entry, int(function["end_exclusive"]))
        callers = tuple(direct_thumb_branches_to(image, base, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"validated-sleep function changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "diagnostic_strings": strings,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "validated_sleep_delivery": {
            "initial_system_event": "0x000d",
            "initial_consumer": "0x0008dd90",
            "minimum_unsigned_duration_seconds": 3_600,
            "storage_system_event": "0x2000",
            "storage_event_failure": "direct call to 0x0008dc94",
            "storage_consumer": "0x0008dc94",
            "storage_append": "0x0005b890",
            "length": "UInt16 wrapping addition of 32 and compact-stage count",
            "automatic_sync": "only after storage append returns nonzero",
            "automatic_sync_trigger_argument": 6,
        },
        "storage_append": {
            "initialized_flag_address": "0x200067b4",
            "maximum_payload_bytes": 3_888,
            "write_attempts": 2,
            "no_writable_sector_uses_rollover": True,
            "two_failed_writes_call_reset_wrapper": "0x0005b2f8",
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
            "health_store_access": False,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "event_and_logging_frameworks_external": True,
            "flash_access_through_bounded_local_store": True,
            "stock_destructive_reset_preserved": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image, args.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
