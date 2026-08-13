#!/usr/bin/env python3
"""Emit the exact R1 FreeRTOS static idle/timer memory configuration seam."""

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


def _function(
    entry: int,
    end_exclusive: int,
    symbol: str,
    role: str,
    literal_address: int,
    buffer_address: int,
    callsites: tuple[int, ...],
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": end_exclusive - entry,
        "symbol": symbol,
        "role": role,
        "provider_family": "r1_provider_configuration_glue",
        "sha256": "2493b37197606152e480a50e74a2c99cfbfc851026f1545cb4ee3001568d1123",
        "literal_address": literal_address,
        "buffer_address": buffer_address,
        "callsites": callsites,
    }


FREERTOS_STATIC_MEMORY_FUNCTIONS = [
    _function(
        0x00095BB8, 0x00095BCA,
        "r1_freertos_idle_static_memory_configuration",
        "vApplicationGetIdleTaskMemory configuration callback",
        0x00095BCC,
        0x2002B4D0,
        (0x000964D8,),
    ),
    _function(
        0x00095BD0, 0x00095BE2,
        "r1_freertos_timer_static_memory_configuration",
        "vApplicationGetTimerTaskMemory configuration callback",
        0x00095BE4,
        0x2002B940,
        (0x00098CC2,),
    ),
]


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions = []
    for function in FREERTOS_STATIC_MEMORY_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"FreeRTOS static-memory seam changed at 0x{entry:08x}")
        literal_address = int(function["literal_address"])
        recovered_buffer = struct.unpack_from(
            "<I", image, literal_address - LOAD_BASE
        )[0]
        if recovered_buffer != function["buffer_address"]:
            raise ValueError(
                f"FreeRTOS static buffer changed at 0x{literal_address:08x}: "
                f"0x{recovered_buffer:08x}"
            )
        actual_callsites = tuple(
            address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
        )
        if actual_callsites != function["callsites"]:
            raise ValueError(
                f"FreeRTOS static-memory callers changed at 0x{entry:08x}: "
                f"{actual_callsites} != {function['callsites']}"
            )
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "literal_address": f"0x{literal_address:08x}",
            "buffer_address": f"0x{recovered_buffer:08x}",
            "stack_address": f"0x{recovered_buffer + 0x70:08x}",
            "callsites": [f"0x{address:08x}" for address in actual_callsites],
        })

    return {
        "analysis": "R1 FreeRTOS static idle/timer memory configuration seam",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "recovered_layout": {
            "static_task_control_block_bytes": 112,
            "stack_words": 256,
            "stack_word_bytes": 4,
            "stack_bytes": 1024,
            "allocation_bytes_per_task": 1136,
            "idle_buffer": "0x2002b4d0",
            "idle_stack": "0x2002b540",
            "timer_buffer": "0x2002b940",
            "timer_stack": "0x2002b9b0",
        },
        "source_lineage": {
            "status": "r1_application_configuration_over_freertos_provider",
            "provider": "Nordic SDK-bundled FreeRTOS 10.0.0",
            "local_implementation_authorized": True,
            "provider_implementation_authorized": False,
            "reason": (
                "FreeRTOS defines the callback contract and consumes the returned "
                "memory. The two fixed buffers, 112-byte/256-word layout, and callback "
                "bindings are recovered R1 application configuration only."
            ),
        },
        "safety": {
            "static_parser_only": True,
            "freertos_provider_reimplementation_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
