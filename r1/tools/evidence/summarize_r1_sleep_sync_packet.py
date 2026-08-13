#!/usr/bin/env python3
"""Pin the R1 compact-to-wire sleep synchronization packet builder."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_SLEEP_SYNC_PACKET_FUNCTIONS = ({
    "entry": 0x0008DA24,
    "end_exclusive": 0x0008DBFC,
    "size": 472,
    "symbol": "r1_sleep_sync_packet_builder",
    "role": "compact-stage merge, clock correction, and sync-send orchestration",
    "sha256": "d3804f3dd415358d10ced85de5f8cccc64da4db33d40e37830d05096b7b86ac5",
    "callers": ((0x0008F9C2, "BL"),),
    "inventory": "ghidra_functions_csv",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")
    function = R1_SLEEP_SYNC_PACKET_FUNCTIONS[0]
    entry = int(function["entry"])
    body = image[entry - LOAD_BASE:int(function["end_exclusive"]) - LOAD_BASE]
    callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
    cutoff = struct.unpack_from("<I", image, 0x0008DBFC - LOAD_BASE)[0]
    if hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"] or cutoff != 946_080_000:
        raise ValueError("sleep synchronization packet closure changed")
    return {
        "analysis": "R1 product sleep synchronization packet builder",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 472,
        "function": {
            **function,
            "entry": "0x0008da24",
            "end_exclusive": "0x0008dbfc",
            "callers": [{"callsite": "0x0008f9c2", "kind": "BL"}],
        },
        "behavior": {
            "input_stage_encoding": "low two bits type; high six bits half-minute duration",
            "adjacent_equal_types_are_merged": True,
            "output_stage_bytes": 3,
            "legacy_clock_cutoff": cutoff,
            "legacy_timezone_forced_zero": True,
            "legacy_future_end_clamped_to_current_time": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "allocation_transport_ack_and_logging_external": True,
            "live_flash_ble_or_clock_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
