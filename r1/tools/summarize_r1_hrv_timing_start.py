#!/usr/bin/env python3
"""Pin the R1 HRV timed-window start orchestration policy."""

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

R1_HRV_TIMING_START_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00049F0C,
    "end_exclusive": 0x0004A08A,
    "size": 382,
    "role": "R1 HRV timed-window start and rollback orchestration policy",
    "symbol": "r1_hrv_timing_start_plan",
    "sha256": "3bb468fcdc552cc184a6433e9cea379e4eeb751b8526effa6f037cca14c99516",
    "callers": ((0x00049B30, "BL"), (0x00049E4C, "B.W")),
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    functions = []
    for function in R1_HRV_TIMING_START_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"HRV timing-start function changed at 0x{entry:08x}")
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
        "analysis": "R1 HRV timed-window start policy",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 382,
        "functions": functions,
        "behavior": {
            "required_mode": 1,
            "pending_flags_must_be_clear": 2,
            "health_and_timing_gates": True,
            "existing_timeout_or_stream_suppresses_start": True,
            "hourly_delay_seconds": 120,
            "catchup_hour_phase_skip_start": 3450,
            "catchup_hour_phase_skip_end": 3599,
            "catchup_delay_seconds_outside_skip": 120,
            "timeout_units": "delay seconds multiplied by 1000",
            "workspace_clear_bytes": 208,
            "one_shot_stream_registration": True,
            "registration_failure_deletes_timeout": True,
        },
        "dependencies": {
            "health_gate": "0x000493f8",
            "timing_gate": "0x0004c5b8",
            "time_provider": "0x0008ad40",
            "timeout_create": "0x0008a310",
            "sensor_stream_register": "0x000897e8",
            "timeout_delete": "0x00049ef4",
            "logging": ["0x000914ec", "0x00091638", "0x000799c0", "0x000799d6"],
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "clean_room_api": "r1_hrv_plan_timing_start",
            "timer_provider_reimplemented": False,
            "sensor_stream_provider_reimplemented": False,
            "time_or_logging_provider_reimplemented": False,
            "biometric_algorithm_included": False,
        },
        "safety": {
            "pure_planner_only": True,
            "live_timer_operation": False,
            "live_sensor_registration": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
