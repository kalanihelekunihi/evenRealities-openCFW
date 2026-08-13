#!/usr/bin/env python3
"""Validate the exact HRV daily callbacks, early-clock FIFO, merge, and ACK lifecycle."""

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
    (0x000706BE, 0x000706D8): "f4a86ec4286f18f864911061109b87063d94a31cd197c6abbfb756013734fbae",
    (0x000706D8, 0x00070736): "5241cad16c7e682056e5b6f25f103ad0c3d1b88af8ab97913360dfe0b6e76055",
    (0x0007073C, 0x00070758): "9dd7974520aa2ac186932885a80a7fdc9351078836a7e01a4f683aaea6a1f5b4",
    (0x0008AD98, 0x0008AD9E): "83bf9b6c537471a134b89fdc8be3c871e03df2082c405ecdfaacfaceafedb021",
    (0x0008D6D8, 0x0008D790): "5f8ccf9aba46b19945fa0295e9735b0935eef83d4a472da43564d22e1001631b",
    (0x00040A74, 0x00040A82): "67fcd7ee83d2e426bbcd020ef70acfadb2ebe130f7656d220a0e2f1ef25a049e",
    (0x00040A88, 0x00040B46): "8ac6c7231fce570c28ca84a06345b32b138ad7c2f9c106b05696f983cae176b6",
    (0x00040984, 0x00040A18): "cd659383195854fd85ebbaa2d837771d46ef7f46f175a5f891621664e5103d88",
    (0x00040BD4, 0x00040CE4): "b8d57eff20cbf8bbf0974511706a14184316004c27a8101119e0244a4943f8b6",
    (0x00041638, 0x00041768): "ae6d3409b7f2b8fcb5797463f6a9e60d6e8eb8713f41669fae46122da15b9640",
    (0x0008C750, 0x0008CA9C): "7acd63f9ecafc97fde7f19cba9446f51737e1ee7e47d56cd0359628d47648042",
}

EXPECTED_BRANCHES = {
    0x0008D6D8: [0x0007072C],
    0x00040A74: [0x00041640, 0x0008C8E8, 0x0008CA36],
    0x00040A88: [0x0008D788],
    0x00040984: [0x00040CD0],
    0x00041638: [0x0008CA7C],
    0x0008C750: [0x0008B16A, 0x0008BA06],
}

EXPECTED_LITERALS = {
    0x00070738: 0x38640900,
    0x0008D790: 0x38640900,
    0x00040A18: 0x200067AB,
    0x00040A1C: 0x2001636C,
    0x00040A84: 0x200067AB,
    0x00040BCC: 0x200067AB,
    0x00040BD0: 0x2001636C,
    0x00041768: 0x200067AB,
    0x0004176C: 0x2001636C,
    0x0008CC7C: 0x00040BD5,
    0x0008CD18: 0x200067AB,
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

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "daily_callbacks": {
            "reset": "0x000706be",
            "read": "0x000706d8",
            "write": "0x0007073c",
            "stock_index_bounds_check": False,
            "reset_clears_only_slot_bytes": 144,
            "reset_replaces_signed_offset_at": "0x90",
            "reset_replaces_day_start_at": "0x9c",
            "reset_preserves_latest_and_reserved_bytes": True,
            "read_copies_slot_before_clock_checks": True,
        },
        "early_clock_path": {
            "time_status_accessor": "0x0008ad98",
            "legacy_cutoff_timestamp": 946_080_000,
            "nonzero_status_returns_copied_slot": True,
            "clock_above_cutoff_returns_copied_slot": True,
            "zero_average_returns_copied_slot": True,
            "nonzero_early_slot_is_zeroed_after_queue_attempt": True,
            "cached_signed_offset_is_divided_as_uint16": True,
            "offset_minutes_divisor": 60,
            "negative_offset_example": {"minutes": -300, "unsigned_hours": 1087},
            "queue_entry_day_start": 0,
            "queue_entry_offset_minutes": 0,
            "independent_clock_reads": 3,
        },
        "unsynced_queue": {
            "metadata_address": "0x200067ab",
            "metadata_layout": ["read UInt8", "write UInt8", "count UInt8"],
            "entry_storage_address": "0x2001636c",
            "capacity": 24,
            "entry_bytes": 20,
            "entry_layout": {
                "aggregate_average_maximum_minimum_uint16": "0x00...0x05",
                "retained_reserved": "0x06...0x07",
                "local_day_start_uint32": "0x08...0x0b",
                "recorded_timestamp_uint32": "0x0c...0x0f",
                "signed_utc_offset_minutes": "0x10...0x11",
                "hour_index": "0x12",
                "retained_tail": "0x13",
            },
            "full_queue_overwrites_oldest": True,
            "consume_erases_contiguous_oldest_prefix": True,
            "consume_keeps_write_index": True,
            "merge_function": "0x00041638",
            "merge_skips_future_day_or_timestamp": True,
            "same_day_hour_overwrites_prior_slot": True,
        },
        "acknowledgement": {
            "callback": "0x00040bd4",
            "callback_thumb_literal": "0x00040bd5",
            "modes": {
                "0": "flash history: advance persisted cursor",
                "1": "unsynced queue: consume through packet maximum",
                "2": "current RAM: advance persisted cursor",
            },
            "future_mode_0_or_2_ack_is_ignored": True,
            "mode_1_does_not_advance_persisted_cursor": True,
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
