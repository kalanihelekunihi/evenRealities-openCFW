#!/usr/bin/env python3
"""Pin R1 target-glasses address validation, lookup, and match policy."""

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


def _function(entry: int, size: int, symbol: str, role: str, sha256: str,
              callers: tuple[tuple[int, str], ...]) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": entry + size,
        "size": size,
        "symbol": symbol,
        "role": role,
        "sha256": sha256,
        "callers": callers,
        "inventory": "ghidra_functions_csv",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    }


R1_PEER_TARGET_FUNCTIONS = (
    _function(
        0x0003D724, 54, "r1_peer_target_address_valid",
        "reject all-zero and all-0xFF target addresses",
        "0d75f1f6bd3144d7bf3cac842edac77cf9535dd18730bad740007036e96567d6",
        ((0x0004CCD8, "BL"), (0x0004CCE4, "BL")),
    ),
    _function(
        0x0004CAE4, 32, "r1_peer_address_from_slots",
        "three-slot connection-handle to peer-address accessor",
        "c8a4243594f64c864334b88fbc8af6baeb31f9ca710bd5d1f1d50d8fc62a4d00",
        ((0x00042F56, "BL"), (0x000458AA, "BL"), (0x0004CCFA, "BL")),
    ),
    _function(
        0x0004CCCC, 464, "r1_peer_is_target_glasses",
        "right/left configured target and connected peer matching policy",
        "46631ec1f7328b6ae5946d07214624383b3f700d29da918fbb5b9662c96a00e3",
        ((0x00042F76, "BL"), (0x000453E0, "BL")),
    ),
)


def _bytes(image: bytes, start: int, size: int) -> bytes:
    offset = start - LOAD_BASE
    if offset < 0 or offset + size > len(image):
        raise ValueError(f"range outside recovered image: 0x{start:08x}+{size}")
    return image[offset:offset + size]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in R1_PEER_TARGET_FUNCTIONS:
        entry = int(function["entry"])
        body = _bytes(image, entry, int(function["size"]))
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"peer-target closure changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    if _bytes(image, 0x0003D75C, 6) != bytes([0xFF] * 6):
        raise ValueError("peer-target erased-address literal changed")
    literals = {
        "erased_address": _bytes(image, 0x0003D75C, 6).hex(),
        "peer_slots": f"0x{struct.unpack('<I', _bytes(image, 0x0004CB04, 4))[0]:08x}",
        "target_addresses": f"0x{struct.unpack('<I', _bytes(image, 0x0004CE9C, 4))[0]:08x}",
    }
    if literals["peer_slots"] != "0x20008298" or \
            literals["target_addresses"] != "0x200064c9":
        raise ValueError("peer-target state pointers changed")

    return {
        "analysis": "R1 target-glasses peer-address policy",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "literals": literals,
        "behavior": {
            "address_bytes": 6,
            "peer_slot_count": 3,
            "peer_slot_bytes": 7,
            "invalid_target_values": ["000000000000", "ffffffffffff"],
            "matches_either_valid_right_or_left_target": True,
            "accepts_when_no_target_is_configured": True,
            "accepts_when_peer_lookup_is_unavailable": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "nordic_connection_and_peer_data_external": True,
            "logging_and_disconnect_actions_external": True,
            "live_ble_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
