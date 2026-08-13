#!/usr/bin/env python3
"""Pin and source-route the five-function 334...342-byte R1 frontier."""

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
    entry: int, end_exclusive: int, size: int, sha256: str, symbol: str,
    role: str, callers: tuple[tuple[int, str], ...], provider_family: str,
    source_disposition: str,
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": size,
        "inventory": "ghidra_functions_csv",
        "sha256": sha256,
        "symbol": symbol,
        "role": role,
        "callers": callers,
        "provider_family": provider_family,
        "source_disposition": source_disposition,
    }


R1_FRONTIER_334_342_PRODUCT_FUNCTIONS = (
    _function(
        0x00033AF8, 0x00033C4E, 342,
        "0d66762846139eee2e58bad4c4cec3c95ce4d5aee990ac7a12342c3c901bb263",
        "r1_factory_thread_message_encode",
        "R1 factory-test allocated message envelope and queue handoff",
        ((0x0005D662, "BL"),), "r1_product_specific",
        "clean_room_behavior_only",
    ),
    _function(
        0x0004D024, 0x0004D176, 338,
        "292da396faeaf54280bcc662ab6de7265b32096dcaddfa10e7e12f83fe939ec2",
        "r1_peripheral_watchdog_plan_step",
        "R1 peripheral-link invariant, advertising restart, and periodic scheduling policy",
        ((0x00092010, "BL"),), "r1_product_specific",
        "clean_room_behavior_only",
    ),
)

GOMORE_FRONTIER_334_342_FUNCTIONS = (
    _function(
        0x000653E6, 0x00065536, 336,
        "c8ac5c9174bab8d9d5b7dd9089b08e6ae8625342011ea998a559d0a6f777ba6e",
        "", "GoMore generated sleep-model multi-branch tensor graph",
        ((0x000653AC, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00090ACC, 0x00090C1A, 334,
        "070fb3bf75ac9151085d8cbecd6d2baa778096ca615b7a207292d7757d227bd5",
        "", "GoMore activity-mode energy estimator state update",
        ((0x0005F8C8, "BL"), (0x0005FB44, "BL")),
        "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
)

GOODIX_FRONTIER_334_342_FUNCTIONS = (
    _function(
        0x00074190, 0x000742DE, 334,
        "4cc0c4d0e74a60a2a41d29ede8715f8aa4bcdabdc1dc63c2add307622f165068",
        "", "Goodix GH_SPO2/dlCom bounded local-peak selector",
        ((0x00076832, "BL"),), "goodix_gh3x2x_candidate",
        "vendor_source_required_not_redistributable",
    ),
)

ALL_FUNCTIONS = (
    R1_FRONTIER_334_342_PRODUCT_FUNCTIONS
    + GOMORE_FRONTIER_334_342_FUNCTIONS
    + GOODIX_FRONTIER_334_342_FUNCTIONS
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
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
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
        "analysis": "334...342-byte ownership frontier",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "product_function_count": len(R1_FRONTIER_334_342_PRODUCT_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_334_342_FUNCTIONS),
        "goodix_function_count": len(GOODIX_FRONTIER_334_342_FUNCTIONS),
        "functions": rows,
        "safety": {
            "live_ble_or_rtos_operation": False,
            "fatal_assertion_invoked": False,
            "gomore_provider_reimplemented": False,
            "goodix_provider_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
