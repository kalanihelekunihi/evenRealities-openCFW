#!/usr/bin/env python3
"""Pin the R1 firmware-event-loop delayed timer callback policy."""

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

R1_DELAYED_EVENT_TIMER_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00065F84,
    "end_exclusive": 0x000660FC,
    "size": 376,
    "role": "R1 firmware-event-loop delayed timer countdown and reschedule policy",
    "symbol": "r1_fw_event_loop_timer_step",
    "sha256": "85425913877b78226afdccf4570d9e082d9c4bd8ed47736da3d98531fc50402f",
    "callers": ((0x00065C78, "B.W"), (0x00065E40, "BL")),
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    functions = []
    for function in R1_DELAYED_EVENT_TIMER_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"delayed-event timer changed at 0x{entry:08x}")
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
        "analysis": "R1 firmware-event-loop delayed timer callback",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 376,
        "functions": functions,
        "behavior": {
            "slot_count": 64,
            "slot_arrays": ["event UInt32", "context UInt32", "remaining_ms UInt32"],
            "mutex_timeout": 1000,
            "standard_elapsed_source": "previous programmed timer delay",
            "direct_elapsed_tag": "0xff000000",
            "direct_elapsed_mask": "0x00ffffff",
            "countdown_saturates_at_zero": True,
            "due_dispatch_order": "ascending slot index",
            "due_dispatch_timeout": "0xffffffff",
            "due_clear_field": "event only",
            "next_delay": "minimum remaining active delay",
            "timer_restart_requires_nonzero": True,
            "tick_to_milliseconds": "uint32(kernel_tick * 1000) >> 10",
        },
        "recovered_quirks": {
            "minimum_initializer": "0xffffffff",
            "no_restart_sentinel_compared": "0x7fffffff",
            "empty_table_requests_uint32_max_timer": True,
            "exact_int32_max_delay_suppresses_restart": True,
        },
        "dependencies": {
            "event_queue_push": "0x000659e8",
            "cmsis_mutex_acquire": "0x0007d488",
            "cmsis_mutex_release": "0x0007d536",
            "cmsis_timer_start": "0x0007d9b0",
            "cmsis_kernel_tick": "0x0007d28c",
            "freertos_critical": ["0x00095cf4", "0x00095d24"],
            "logging": ["0x000914ec", "0x00091638", "0x000799c0", "0x000799d6"],
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "clean_room_api": "r1_delayed_event_timer_step",
            "cmsis_or_freertos_reimplemented": False,
            "queue_or_logging_provider_reimplemented": False,
            "live_timer_operation": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
