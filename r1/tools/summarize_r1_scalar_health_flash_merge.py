#!/usr/bin/env python3
"""Pin the twin R1 HR/SpO2 FlashDB-record merge callbacks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_SCALAR_HEALTH_FLASH_MERGE_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x00040508,
        "end_exclusive": 0x00040692,
        "size": 394,
        "role": "R1 heart-rate FlashDB record to sparse day-builder merge policy",
        "symbol": "r1_heart_rate_flash_record_merge",
        "sha256": "3b8c05a2fbc91de8a2f04a792ade31957920c04cc21289031f8074bd5b74a1ad",
        "callers": (),
        "inventory": "ghidra_functions_csv",
        "flush": "0x0004011c",
        "reset": "0x0003fa84",
    },
    {
        "entry": 0x000446B4,
        "end_exclusive": 0x0004483E,
        "size": 394,
        "role": "R1 SpO2 FlashDB record to sparse day-builder merge policy",
        "symbol": "r1_spo2_flash_record_merge",
        "sha256": "a215fc2a880381053c078871467e153f22d9bfd8d7f68c2b667c74a06c017257",
        "callers": (),
        "inventory": "ghidra_functions_csv",
        "flush": "0x000442f4",
        "reset": "0x00043c80",
    },
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    functions = []
    for function in R1_SCALAR_HEALTH_FLASH_MERGE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"scalar health flash merge changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [],
        })
    return {
        "analysis": "R1 heart-rate and SpO2 FlashDB record merge policy",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 2,
        "function_bytes": 788,
        "functions": functions,
        "behavior": {
            "required_record_bytes": 128,
            "future_timestamp_rejected": True,
            "local_hour_slot_policy": "hour 0 -> slot 23; otherwise hour - 1",
            "local_day_start_uses_hour_minute_second": True,
            "midnight_adjustment_seconds": -86400,
            "optional_previous_local_day_filter": True,
            "zero_average_ignored": True,
            "flush_on_day_or_timezone_change": True,
            "bytes_per_present_slot": 4,
            "duplicate_slot_not_overwritten": True,
            "newest_timestamp_monotonic": True,
        },
        "dependencies": {
            "flashdb_blob_read": ["0x0006366c", "0x00063d40", "0x00063672"],
            "time_calendar": ["0x0008ada4", "0x0008af40"],
            "division_helper": "0x0002754a",
            "logging": ["0x000914ec", "0x00091638", "0x000799d6"],
        },
        "clean_room": {
            "shared_api": "r1_health_u8_flash_record_merge",
            "normalized_record_only": True,
            "first_record_wins": True,
            "provider_blob_parser_included": False,
            "calendar_provider_included": False,
            "transport_provider_included": False,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "flashdb_or_time_provider_reimplemented": False,
            "transport_or_logging_reimplemented": False,
            "biometric_algorithm_included": False,
        },
        "safety": {
            "static_parser_only": True,
            "private_history_read": False,
            "live_sender_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
