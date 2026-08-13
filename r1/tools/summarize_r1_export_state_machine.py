#!/usr/bin/env python3
"""Pin the R1 generic virtual-file export command state machine."""

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

R1_EXPORT_STATE_MACHINE_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0004E740,
    "end_exclusive": 0x0004E8AC,
    "size": 364,
    "role": "R1 generic virtual-file export command/chunk state machine",
    "symbol": "r1_export_plan_command",
    "sha256": "f07a98de9703b681ffa54275f49699297d438fad52e4eeb1e049eb4f3e4e40d3",
    "callers": ((0x00045114, "BL"),),
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    function = R1_EXPORT_STATE_MACHINE_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - LOAD_BASE:end - LOAD_BASE]
    callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"]:
        raise ValueError("R1 export state machine changed")
    return {
        "analysis": "R1 generic virtual-file export command/chunk policy",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": len(body),
        "functions": [{
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        }],
        "behavior": {
            "start_command": 0,
            "data_command": 1,
            "start_result": 1,
            "retry_result": 2,
            "complete_status": 3,
            "metadata_control_bytes": 10,
            "data_marker": 1,
            "maximum_chunk_bytes": 4096,
            "interframe_delay_ms": 50,
            "offset_advanced_after_chunk": True,
            "retry_resets_offset": True,
            "finalize_on_complete": True,
        },
        "dependencies": {
            "descriptor_callbacks": ["metadata", "read", "start", "finalize"],
            "control_sender": "0x00032408",
            "commanded_fragmenter": "0x00032598",
            "allocator": "0x000855a0 / FreeRTOS pvPortMalloc",
            "release": "0x00095d48 / FreeRTOS vPortFree veneer",
            "delay": "0x0007d154",
            "logging": "0x000799e6",
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "clean_room_api": "r1_export_plan_command",
            "virtual_file_reader_included": False,
            "raw_log_sender_included": False,
            "allocator_or_freertos_reimplemented": False,
            "transport_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
