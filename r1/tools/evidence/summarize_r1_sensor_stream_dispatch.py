#!/usr/bin/env python3
"""Pin the unresolved generic sensor-stream timer dispatch callback."""

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
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


SENSOR_STREAM_DISPATCH_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0008A1E0,
    "end_exclusive": 0x0008A310,
    "size": 422,
    "role": "generic timer-driven sensor-stream sample and listener dispatch",
    "symbol": "sensor_stream_timer_dispatch_candidate",
    "sha256": "86e00a0dc3b033c1b4c0ab1414c1fc94b87e0679190ead386c6b2df7f8d444e4",
    "callers": (),
    "inventory": "ghidra_functions_csv",
    "segments": (
        (0x0008A1E0, 0x0008A310),
        (0x00089BA8, 0x00089C1E),
    ),
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in SENSOR_STREAM_DISPATCH_FUNCTIONS:
        entry = int(function["entry"])
        segments = tuple(function["segments"])
        body = b"".join(
            image[start - LOAD_BASE:end - LOAD_BASE]
            for start, end in segments
        )
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"sensor-stream dispatch body changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in segments
            ],
            "callers": [],
        })

    pointer_location = 0x00089ACC
    callback = struct.unpack_from("<I", image, pointer_location - LOAD_BASE)[0]
    if callback != 0x0008A1E1:
        raise ValueError("sensor-stream timer callback pointer changed")

    return {
        "analysis": "unresolved generic named sensor-stream subscription framework",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 422,
        "functions": functions,
        "indirect_entry": {
            "pointer_location": f"0x{pointer_location:08x}",
            "thumb_pointer": f"0x{callback:08x}",
            "direct_callsite_count": 0,
        },
        "behavior": {
            "timer_context_object_offset": "0x0c",
            "provider_read_hook_offset": "provider operations + 0x08",
            "sample_buffer_offset": "0x14",
            "sample_buffer_cursor_offset": "0x18",
            "listener_list_offset": "0x2c",
            "listener_callback_offset": "0x10",
            "listener_rate_offset": "0x0d",
            "dispatch_active_flag": "bit 1 of object + 0x28",
            "pending_unregister_flag": "bit 2 of object + 0x28",
            "deferred_listener_flag": "bit 0 of listener + 0x14",
            "sample_buffer_wraps": True,
            "rate_mismatch_uses_resize_copy_helper": True,
            "deferred_cleanup_tail_target": "0x00089ba8",
            "empty_list_releases_buffer_and_timer": True,
        },
        "dependencies": {
            "list_first": "0x0005d8e6",
            "list_next": "0x0005d8ee",
            "list_remove": "0x0005d998",
            "list_is_empty": "0x0005d986",
            "free": "0x00095d48",
            "sample_buffer_resize_copy": "0x0007d0d8",
            "retime_continuation": "0x0008a068",
            "release_continuation": "0x0008a180",
        },
        "boundary": {
            "provider_family": "unknown_sensor_stream_framework_candidate",
            "source_disposition": "investigate_before_implementing",
            "attributable_source_identified": False,
            "local_framework_reimplementation_authorized": False,
            "dependent_list_allocator_timer_code_admitted": False,
            "provider_read_and_listener_hooks_admitted": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_sensor_data_read": False,
            "timer_callback_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
