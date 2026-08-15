#!/usr/bin/env python3
"""Pin the unresolved generic sensor-stream unregistration framework body."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
CALL_GRAPH = ROOT / "research/decompilation/application/call-graph.csv"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


SENSOR_STREAM_UNREGISTER_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00089B08,
    "end_exclusive": 0x0008A1AA,
    "size": 562,
    "role": "generic named sensor-stream listener unregistration and rate retiming",
    "symbol": "sensor_stream_unregister_candidate",
    "sha256": "6fd417efc7c460d1d8e2a3c234f8fd33b9d04b4324f04f2fcb251a07acefcf3a",
    "caller_count": 25,
    "caller_digest": "b8695cad6fd356c28bc05ea9bcf9a47dcc70c7223b3f18a63207a7899ad0e213",
    "inventory": "ghidra_functions_csv",
    "segments": (
        (0x00089B08, 0x00089B60),
        (0x00089C20, 0x00089CFA),
        (0x0008A068, 0x0008A13E),
        (0x0008A180, 0x0008A1AA),
    ),
},)


def callsites_to(entry: int) -> list[tuple[int, str]]:
    with CALL_GRAPH.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        result = [
            (int(row["from_address"], 16), "BL")
            for row in rows
            if int(row["callee_entry"], 16) == entry and
            row["reference_type"] == "UNCONDITIONAL_CALL"
        ]
    return sorted(result)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in SENSOR_STREAM_UNREGISTER_FUNCTIONS:
        entry = int(function["entry"])
        segments = tuple(function["segments"])
        body = b"".join(
            image[start - LOAD_BASE:end - LOAD_BASE]
            for start, end in segments
        )
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"sensor-stream unregister body mismatch at 0x{entry:08x}")
        callers = callsites_to(entry)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"sensor-stream unregister caller set mismatch at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in segments
            ],
        })

    return {
        "analysis": "unresolved generic named sensor-stream subscription framework",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 562,
        "functions": functions,
        "callgraph": {
            "direct_callsite_count": 25,
            "unique_caller_function_count": 20,
            "cross_boundary_examples": {
                "gomore_provider": "0x00049410",
                "r1_motion_adapter": "0x0006f228",
            },
        },
        "behavior": {
            "object_lookup_by_name": "0x00089d54",
            "listener_list_offset": "0x2c",
            "listener_rate_offset": "0x0d",
            "deferred_unregister_when_dispatching": True,
            "deferred_listener_flag": "bit 0 of listener + 0x14",
            "deferred_object_flag": "bit 2 of object + 0x28",
            "remaining_rate_policy": "maximum listener rate",
            "timer_period_formula": "1024 / maximum listener rate",
            "empty_list_releases_buffer_and_timer": True,
            "empty_list_invokes_optional_provider_close_hook": True,
        },
        "dependencies": {
            "list_first": "0x0005d8e6",
            "list_next": "0x0005d8ee",
            "list_remove": "0x0005d998",
            "list_is_empty": "0x0005d986",
            "allocator": "0x000855a0",
            "free": "0x00095d48",
            "sample_buffer_resize_copy": "0x0007d0d8",
            "timer_period_set": "0x0008a5d0",
            "timer_release": "0x0008a3c0",
        },
        "boundary": {
            "provider_family": "unknown_sensor_stream_framework_candidate",
            "source_disposition": "clean_room_reimplementation_owner_authorized",
            "attributable_source_identified": False,
            "local_framework_reimplementation_authorized": True,
            "dependent_list_allocator_timer_code_admitted": False,
            "provider_close_hook_admitted": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_sensor_data_read": False,
            "registration_or_unregistration_api_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
