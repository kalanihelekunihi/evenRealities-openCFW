#!/usr/bin/env python3
"""Pin and source-route the 264...274-byte R1 frontier and one exclusive helper."""

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


def _function(
    entry: int, size: int, sha256: str, symbol: str, role: str,
    callers: tuple[tuple[int, str], ...], provider_family: str,
    source_disposition: str,
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": entry + size,
        "size": size,
        "inventory": "ghidra_functions_csv",
        "sha256": sha256,
        "symbol": symbol,
        "role": role,
        "callers": callers,
        "provider_family": provider_family,
        "source_disposition": source_disposition,
    }


R1_FRONTIER_264_274_PRODUCT_FUNCTIONS = (
    _function(
        0x00032408, 272,
        "83301191875e916b0ab3e015539b271619b3a21d73be2ef98c6a6716ce8ed9a9",
        "r1_fragment_message",
        "R1 five-byte EUS CRC-32C transport fragmenter",
        ((0x0004E7A4, "BL"), (0x0004E804, "BL"),
         (0x0004E862, "BL"), (0x0004E896, "BL")),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003D9B8, 268,
        "47429c4059d0ff96affac47defecc12d455f1cff4673df2de03aa81ce8bd1d6a",
        "r1_battery_diagnostic_cadence_step",
        "R1 five-cycle battery status and thirty-cycle compensation diagnostic cadence",
        ((0x00032120, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003EE34, 264,
        "818b5c79dbb504b629dab1974cb8290f5fab659848e852101c06429815e0680f",
        "r1_ep_scan_cursor",
        "R1 payload-redacting ep.bin two-page journal recovery scan",
        ((0x0005E10A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
)

GOMORE_FRONTIER_264_274_FUNCTIONS = (
    _function(
        0x00067C30, 274,
        "70ea4f3fd687ed7d5f41b0903f57c72a0a1959f0ffbcf66bf9de9c6cf90bb07b",
        "", "GoMore private timestamp-to-sample segment expansion",
        ((0x00056F42, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00064274, 264,
        "91525fb97e34b1faf918a5895aa06acb208b030ea6dde49d0a8a21d2d1486e04",
        "", "GoMore private fixed-coefficient floating-point IIR filter",
        ((0x000688A2, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000641C4, 44,
        "1cf6848b2f7eba15d09cf9ce3df20aa0bca3d07db4b4a3d686ea7f08bbe04f0e",
        "", "GoMore private linear-segment fill helper",
        ((0x00067C92, "BL"), (0x00067D0C, "BL"),
         (0x00067D2E, "BL")),
        "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
)

ALL_FUNCTIONS = (
    R1_FRONTIER_264_274_PRODUCT_FUNCTIONS
    + GOMORE_FRONTIER_264_274_FUNCTIONS
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    rows = []
    for function in ALL_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if (len(body) != int(function["size"])
                or hashlib.sha256(body).hexdigest() != function["sha256"]
                or callers != function["callers"]):
            raise ValueError(f"frontier function changed: 0x{entry:08x}")
        rows.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{callsite:08x}", "kind": kind}
                for callsite, kind in callers
            ],
        })
    return {
        "analysis": "264...274-byte ownership frontier plus exclusive helper",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "frontier_function_count": 5,
        "frontier_function_bytes": 1342,
        "exclusive_helper_count": 1,
        "product_function_count": len(R1_FRONTIER_264_274_PRODUCT_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_264_274_FUNCTIONS),
        "functions": rows,
        "safety": {
            "raw_ep_payload_exposed": False,
            "flash_mutation": False,
            "live_logging": False,
            "gomore_provider_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
