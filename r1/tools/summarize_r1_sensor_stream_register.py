#!/usr/bin/env python3
"""Pin the unresolved generic sensor-stream listener registration routine."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

SENSOR_STREAM_REGISTER_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00089890,
    "end_exclusive": 0x00089A60,
    "size": 464,
    "role": "generic named sensor-stream listener registration and rate retiming",
    "symbol": "sensor_stream_register_candidate",
    "sha256": "2c0548e1abf6024d7dcb79b9e1768a9ac4687de976aaa80896ccd6912866e15c",
    "callers": ((0x00089804, "BL"),),
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in SENSOR_STREAM_REGISTER_FUNCTIONS:
        entry = int(function["entry"])
        body = image[entry - LOAD_BASE:int(function["end_exclusive"]) - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"sensor-stream register body changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    callback = struct.unpack_from("<I", image, 0x00089ACC - LOAD_BASE)[0]
    if callback != 0x0008A1E1:
        raise ValueError("sensor-stream timer callback pointer changed")
    return {
        "analysis": "unresolved generic named sensor-stream subscription framework",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 464,
        "functions": functions,
        "behavior": {
            "listener_name_maximum_bytes": 8,
            "requested_order_capped_at": 1,
            "listener_list_offset": "0x2c",
            "listener_callback_offset": "0x10",
            "listener_rate_offset": "0x0d",
            "empty_list_allocates_sample_buffer": True,
            "higher_rate_resizes_existing_buffer": True,
            "timer_period_formula": "1024 / requested rate",
            "timer_callback_thumb_pointer": f"0x{callback:08x}",
            "optional_provider_open_hook": True,
        },
        "boundary": {
            "provider_family": "unknown_sensor_stream_framework_candidate",
            "source_disposition": "investigate_before_implementing",
            "attributable_source_identified": False,
            "local_framework_reimplementation_authorized": False,
            "list_allocator_timer_and_resize_dependencies_admitted": False,
            "provider_open_hook_admitted": False,
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
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
