#!/usr/bin/env python3
"""Pin the R1 final protocol response encoder/send boundary."""

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

R1_PROTOCOL_RESPONSE_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x000828B4,
        "end_exclusive": 0x00082A20,
        "size": 364,
        "role": "R1 final phone-protocol response encode/transport orchestration",
        "symbol": "r1_protocol_send_response",
        "sha256": "fce00c9e829f4cb27b24679f4a991108d3b0dc448eadc05aee034f065e42c52e",
        "callers": (
            (0x0008283E, "BL"), (0x00082876, "BL"), (0x000828AE, "BL"),
            (0x00082B8E, "BL"), (0x00082BCC, "BL"), (0x00082F36, "BL"),
            (0x00084C4E, "BL"),
        ),
        "inventory": "ghidra_functions_csv",
    },
    {
        "entry": 0x00082F9C,
        "end_exclusive": 0x00083024,
        "size": 136,
        "role": "R1 normal-model packet constructor",
        "symbol": "r1_model_encode",
        "sha256": "5a0af8389804a98f224903c1c20174548b449a93f0872dfeb4e509c20928c644",
        "callers": ((0x00082916, "BL"),),
        "inventory": "ghidra_functions_csv",
    },
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    functions = []
    function_bytes = 0
    for function in R1_PROTOCOL_RESPONSE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError("R1 protocol response boundary changed")
        function_bytes += len(body)
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
        "analysis": "R1 final protocol response encode/send policy",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(functions),
        "function_bytes": function_bytes,
        "functions": functions,
        "behavior": {
            "null_header_result": 2,
            "no_active_link_result": 5,
            "allocation_failure_result": 3,
            "transport_failure_result": 4,
            "encoded_length_overhead": 12,
            "module_index_maximum": 3,
            "status_bit_zero_selects_generated_serial": True,
            "generated_serial_postincremented": True,
            "checksum": "CRC-16/MODBUS over the complete model with zero checksum bytes",
            "allocation_always_released_after_encode_attempt": True,
            "success_result": 0,
        },
        "dependencies": {
            "primary_link_probe": "0x0004cbb0",
            "secondary_link_probe": "0x0004cb40",
            "allocator": "0x000855a0 / FreeRTOS pvPortMalloc",
            "release": "0x00095d48 / FreeRTOS vPortFree veneer",
            "packet_encoder": "0x00082f9c / locally bounded in this closure",
            "checksum": "0x0005d87c / separately classified shared CRC primitive",
            "transport_callback": "0x000827f8",
            "logging": ["0x000914ec", "0x00091638", "0x000799c8",
                        "0x000799d6", "0x000799f8"],
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "clean_room_api": "r1_protocol_send_response",
            "allocator_or_freertos_reimplemented": False,
            "ble_transport_reimplemented": False,
            "logging_provider_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
