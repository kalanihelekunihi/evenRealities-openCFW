#!/usr/bin/env python3
"""Pin the R1 HR/SpO2 current-RAM caches to sparse day-packet policy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_SCALAR_HEALTH_RAM_CACHE_MERGE_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x0003FEF4,
        "end_exclusive": 0x00040060,
        "size": 364,
        "role": "R1 heart-rate current-RAM cache to sparse day-packet policy",
        "symbol": "r1_heart_rate_ram_cache_merge",
        "sha256": "723e050917b4559d3378ac66c5a31635fbffd4a31af444c14cfe352b0c3b1b3e",
        "callers": ((0x0008C48E, "BL"),),
        "inventory": "ghidra_functions_csv",
    },
    {
        "entry": 0x000440C4,
        "end_exclusive": 0x00044230,
        "size": 364,
        "role": "R1 SpO2 current-RAM cache to sparse day-packet policy",
        "symbol": "r1_spo2_ram_cache_merge",
        "sha256": "6b64439ca9d0f871794294f8ba83f089ff975ed440fe8ac8ab114df4e00d832f",
        "callers": ((0x0008D0A0, "BL"),),
        "inventory": "ghidra_functions_csv",
    },
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    functions = []
    for function in R1_SCALAR_HEALTH_RAM_CACHE_MERGE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"scalar RAM-cache merge changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })
    return {
        "analysis": "R1 scalar-health current-RAM history merge policy",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 2,
        "function_bytes": 728,
        "functions": functions,
        "behavior": {
            "requires_nonzero_builder_and_day": True,
            "window_start_must_precede_firmware_time": True,
            "cache_day_and_timezone_refreshed": True,
            "builder_ack_mode": 2,
            "hour_seconds": 3600,
            "hour_count": 24,
            "current_hour_index_capped": 23,
            "current_hour_included_outside_window": True,
            "other_hours_require_inclusive_window": True,
            "zero_average_ignored": True,
            "bytes_per_present_slot": 4,
            "acknowledgement_clamped_to_firmware_time": True,
            "flush_only_when_nonempty": True,
            "builder_mode_restored": True,
        },
        "dependencies": {
            "time_provider": "0x0008ada4",
            "timezone_provider": "0x0008adb4",
            "heart_rate_cache_accessor": "0x0005ace0",
            "spo2_cache_accessor": "0x0005baec",
            "heart_rate_builder_reset": "0x0003fa84",
            "spo2_builder_reset": "0x00043c80",
            "heart_rate_acknowledgement_clamp": "0x0003f9dc",
            "spo2_acknowledgement_clamp": "0x00043bd4",
            "heart_rate_builder_flush": "0x0004011c",
            "spo2_builder_flush": "0x000442f4",
            "logging": ["0x000914ec", "0x00091638", "0x000799d6"],
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "clean_room_api": "r1_health_u8_ram_cache_merge",
            "shared_between_metrics": True,
            "time_or_logging_provider_reimplemented": False,
            "transport_or_storage_provider_reimplemented": False,
            "biometric_algorithm_included": False,
        },
        "hardening": {
            "future_requested_day_rejected": True,
            "reason": "avoid the stock unsigned day-index subtraction wrap",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
