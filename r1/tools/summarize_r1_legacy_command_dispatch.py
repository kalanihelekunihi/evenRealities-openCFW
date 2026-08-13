#!/usr/bin/env python3
"""Pin the R1 legacy command-frame router without cloning its handlers."""

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

R1_LEGACY_COMMAND_DISPATCH_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0004E258,
    "end_exclusive": 0x0004E428,
    "size": 464,
    "role": "legacy command workspace initialization and opcode routing",
    "symbol": "r1_legacy_command_route_frame",
    "sha256": "be3357d945c4470611d70da7e97691fe9fb6a87bbda16b8da2e6d3eea48e3ca1",
    "callers": ((0x0004514E, "BL"),),
    "inventory": "ghidra_functions_csv",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

OPCODE_HANDLERS = {
    0x11: 0x00062584,
    0x12: 0x00062546,
    0x21: 0x0006244E,
    0x22: 0x000624F4,
    0x23: 0x0006249C,
    0x24: 0x000624C8,
    0x34: 0x00062412,
    0x37: 0x000628F6,
    0x40: 0x000629D4,
    0x52: 0x00062834,
    0x53: 0x00062388,
    0x54: 0x000628AE,
    0x55: 0x00062A5C,
    0x56: 0x00062840,
    0x57: 0x000628CC,
    0x85: 0x00092B98,
    0x88: 0x00033850,
    0x89: 0x0006A714,
    0x8A: 0x00062B4C,
    0x91: 0x0006210C,
    0x94: 0x0004E1F8,
    0x95: 0x00062BEC,
    0xF2: 0x00062C30,
}


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in R1_LEGACY_COMMAND_DISPATCH_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"legacy command dispatcher changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    workspace_pointer = struct.unpack_from(
        "<I", image, 0x0004E428 - LOAD_BASE
    )[0]
    if workspace_pointer != 0x2001A174:
        raise ValueError("legacy command workspace pointer changed")

    return {
        "analysis": "R1 legacy command-frame dispatcher",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 464,
        "functions": functions,
        "behavior": {
            "workspace_bytes": 36,
            "workspace_pointer": f"0x{workspace_pointer:08x}",
            "opcode_offset": 2,
            "recognized_opcode_count": len(OPCODE_HANDLERS),
            "opcode_handlers": {
                f"0x{opcode:02x}": f"0x{handler:08x}"
                for opcode, handler in OPCODE_HANDLERS.items()
            },
            "unknown_return": "0xffffffff",
            "recognized_return": 0,
            "pair_auth_opcode": "0x88",
            "pair_auth_response_byte": 2,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "router_only_implemented": True,
            "handler_implementations_admitted_by_this_closure": False,
            "stock_unbounded_copy_preserved": False,
            "bounded_workspace_required": True,
        },
        "safety": {
            "pure_route_selection": True,
            "live_command_handler_invocation": False,
            "pairing_or_authorization_state_mutation": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
