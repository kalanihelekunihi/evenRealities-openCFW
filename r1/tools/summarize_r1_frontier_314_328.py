#!/usr/bin/env python3
"""Pin and source-route the five-function 314...328-byte R1 frontier."""

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
    source_disposition: str, inventory_size: int | None = None,
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": size,
        "inventory_size": size if inventory_size is None else inventory_size,
        "inventory": "ghidra_functions_csv",
        "sha256": sha256,
        "symbol": symbol,
        "role": role,
        "callers": callers,
        "provider_family": provider_family,
        "source_disposition": source_disposition,
    }


R1_FRONTIER_314_328_PRODUCT_FUNCTIONS = (
    _function(
        0x0008B184, 0x0008B2CC, 328,
        "7332ae1847cc0f7137e3d1b464c315dfa0b8b8e80b4d9af5d4ed41a5d5d5c76c",
        "r1_health_clear_all_caches",
        "R1 health clear-all cache and provider-action orchestration",
        ((0x0004603A, "BL"),), "r1_product_specific",
        "clean_room_behavior_only",
    ),
    _function(
        0x00051108, 0x00051250, 328,
        "3f7836df81f8fb76d15d03120be74c32734bf62e7f42cd3d9b68286e72738cde",
        "r1_temperature_pair_reduce",
        "R1 dual-GXT310 ten-sample trimmed mean and calibration adapter",
        ((0x0003CD3A, "BL"), (0x0004F1CE, "BL"), (0x00062C7A, "BL")),
        "r1_product_specific", "clean_room_behavior_only",
    ),
)

NORDIC_FRONTIER_314_328_FUNCTIONS = (
    _function(
        0x000317CC, 0x0003190C, 320,
        "e8a945402151326dbbba0c4e5c8660b42bc21c7e3b3a5da8d0ab02647d32e5ac",
        "nrfx_saadc_irq_handler",
        "Nordic nrfx SAADC END/STARTED/CALIBRATEDONE/STOPPED/limit IRQ handler",
        (), "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk", inventory_size=318,
    ),
)

GOMORE_FRONTIER_314_328_FUNCTIONS = (
    _function(
        0x00091B08, 0x00091C42, 314,
        "6048b5e7b5b94000f3143c5918f323df480ea0de6959a19083826ec509f06cb9",
        "", "GoMore private floating-point convolution tensor operator",
        ((0x0006531C, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000651CA, 0x00065304, 314,
        "1d346c3a4978ae586e3e784bb5430d94040c6a40cbac5593600e6e633aac5ea0",
        "", "GoMore private batch-normalization tensor operator",
        ((0x000884EA, "BL"), (0x00088546, "BL"),
         (0x0008859E, "BL"), (0x000885F6, "BL"),
         (0x00088670, "BL"), (0x000886C8, "BL"),
         (0x00088720, "BL")),
        "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
)

ALL_FUNCTIONS = (
    R1_FRONTIER_314_328_PRODUCT_FUNCTIONS
    + NORDIC_FRONTIER_314_328_FUNCTIONS
    + GOMORE_FRONTIER_314_328_FUNCTIONS
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
        "analysis": "314...328-byte ownership frontier",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "inventory_bytes": sum(int(row["inventory_size"]) for row in rows),
        "product_function_count": len(R1_FRONTIER_314_328_PRODUCT_FUNCTIONS),
        "nordic_function_count": len(NORDIC_FRONTIER_314_328_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_314_328_FUNCTIONS),
        "functions": rows,
        "safety": {
            "live_sensor_io": False,
            "persistent_database_mutation": False,
            "gomore_provider_reimplemented": False,
            "nordic_provider_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
