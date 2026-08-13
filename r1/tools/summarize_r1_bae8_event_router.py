#!/usr/bin/env python3
"""Pin the R1 BAE8 custom-service event router and callback registration."""

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

R1_BAE8_EVENT_ROUTER_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0005D5E0,
    "end_exclusive": 0x0005D782,
    "size": 418,
    "role": "BAE8 custom-service event routing and link-state policy",
    "symbol": "r1_bae8_event_route",
    "sha256": "a767809ef6dd28fd1e49ca67838942c7eae79ea180b781f0e8dcc7d078d3c7d3",
    "callers": (),
    "inventory": "ghidra_functions_csv",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

CALLBACK_POINTER_ADDRESS = 0x0004E6E4
CALLBACK_THUMB_POINTER = 0x0005D5E1


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in R1_BAE8_EVENT_ROUTER_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"BAE8 event router changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [],
        })

    pointer = struct.unpack_from(
        "<I", image, CALLBACK_POINTER_ADDRESS - LOAD_BASE
    )[0]
    if pointer != CALLBACK_THUMB_POINTER:
        raise ValueError("BAE8 event callback pointer changed")

    return {
        "analysis": "R1 BAE8 custom-service event router",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 418,
        "functions": functions,
        "registration": {
            "configuration_function": "0x0004e66c",
            "service_configuration_function": "0x000529bc",
            "callback_pointer_address": f"0x{CALLBACK_POINTER_ADDRESS:08x}",
            "callback_thumb_pointer": f"0x{pointer:08x}",
            "service_callback_offset": "0x2c",
            "direct_callers_expected": 0,
        },
        "event_routes": {
            "2": "BC receive path",
            "3": "EUS receive reassembly at 0x00032198",
            "6": "link group A lookup plus glasses-role assignment",
            "7": "link group A lookup plus glasses-role assignment",
            "8": "link group B lookup",
            "9": "link group B lookup",
            "other": "ignore",
        },
        "clean_room_behavior": {
            "planner": "src/r1_runtime.c::r1_runtime_plan_bae8_event",
            "EUS_runtime": "src/r1_runtime.c::r1_runtime_receive_eus",
            "provider_operations_executed_by_planner": False,
            "unknown_event_ignored": True,
        },
        "dependencies": {
            "BAE8_service_registration": "R1 configuration over Nordic SDK GATT providers",
            "link_context_lookup": "Nordic SDK ble_link_ctx_manager",
            "BC_receivers": ["0x00033af8", "0x00033dbc"],
            "event_helper": "0x00065d64",
            "factory_marker_accessor": "0x0007ba24",
            "dependency_implementations_admitted": False,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "vendor_implementation_identified": False,
            "unresolved_callees_reclassified": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
