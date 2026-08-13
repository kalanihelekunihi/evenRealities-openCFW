#!/usr/bin/env python3
"""Pin the R1 HRV current-RAM cache to sparse day-packet merge policy."""

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

R1_HRV_RAM_CACHE_MERGE_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00040DE0,
    "end_exclusive": 0x00040F5C,
    "size": 380,
    "role": "R1 HRV current-RAM cache to sparse day-packet merge policy",
    "symbol": "r1_hrv_ram_cache_merge",
    "sha256": "146d9efe6adcee580a40d9427899f358d4f9cd8e7552041ab9be041277da0fe5",
    "callers": ((0x0008CA90, "BL"),),
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    functions = []
    for function in R1_HRV_RAM_CACHE_MERGE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"HRV RAM-cache merge changed at 0x{entry:08x}")
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
        "analysis": "R1 HRV current-RAM history merge policy",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 380,
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
            "bytes_per_present_slot": 7,
            "latest_value_prefix_bytes": 6,
            "acknowledgement_clamped_to_firmware_time": True,
            "flush_only_when_nonempty": True,
            "builder_mode_restored": True,
        },
        "dependencies": {
            "time_provider": "0x0008ada4",
            "timezone_provider": "0x0008adb4",
            "hrv_cache_accessor": "0x0005af18",
            "builder_reset": "0x00040964",
            "acknowledgement_clamp": "0x000408b8",
            "builder_flush": "0x0004101c",
            "logging": ["0x000914ec", "0x00091638", "0x000799d6"],
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "clean_room_api": "r1_health_u16_ram_cache_merge",
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
