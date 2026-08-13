#!/usr/bin/env python3
"""Pin and source-route the five-function 280...308-byte R1 frontier."""

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


R1_FRONTIER_280_308_PRODUCT_FUNCTIONS = (
    _function(
        0x00065B4C, 0x00065C80, 308,
        "6f6af2221a4b1479db34b88f6b57c9dec3f0153351637ba8fdc867c69741e11e",
        "r1_delayed_event_schedule",
        "R1 delayed-event admission, elapsed-time reconciliation, and timer plan",
        (
            (0x00032190, "B.W"), (0x0003D82C, "B.W"),
            (0x0003EA30, "BL"), (0x000452CA, "BL"),
            (0x00045354, "BL"), (0x000453D6, "BL"),
            (0x00045910, "BL"), (0x0004669E, "BL"),
            (0x00046740, "BL"), (0x0004697A, "BL"),
            (0x00047F8E, "BL"), (0x00048BC4, "B.W"),
            (0x0004CA66, "BL"), (0x0004CA76, "B.W"),
            (0x0004D172, "B.W"), (0x0004D5E8, "B.W"),
            (0x0004DDD6, "B.W"), (0x0004DE9A, "B.W"),
            (0x0004E0E2, "B.W"), (0x00051BD8, "BL"),
            (0x00052C10, "BL"), (0x00052D12, "BL"),
            (0x00052D4E, "BL"), (0x000532C8, "BL"),
            (0x0006A7F4, "BL"), (0x0006A83E, "BL"),
            (0x000775FC, "BL"), (0x0007F33E, "BL"),
            (0x0007F34C, "BL"), (0x0007F358, "BL"),
            (0x0007F3F0, "BL"), (0x0007F4C6, "BL"),
            (0x0007F4D0, "BL"), (0x0007F4DA, "BL"),
            (0x0007F5A8, "BL"), (0x00083CEA, "BL"),
            (0x00083CFC, "B.W"), (0x00084148, "B.W"),
            (0x0009117C, "B.W"), (0x00091F80, "BL"),
            (0x00091F8C, "BL"), (0x00096A6C, "BL"),
            (0x00096AB8, "BL"), (0x00096DAC, "B.W"),
        ),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00033850, 0x00033982, 306,
        "034f58f9537b96a7c9f0c0ff0c78924bb810dd8a5984bca8d51c82b17b25ecdf",
        "r1_ble_thread_message_encode",
        "R1 BLE-thread allocated message envelope and queue handoff",
        ((0x0004E3D8, "BL"), (0x0006278A, "BL"),
         (0x00083D56, "B.W"), (0x0008434C, "BL"),
         (0x00084C92, "BL"), (0x000882E4, "B.W")),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083F24, 0x00084050, 300,
        "f214c7da6cdac32ec60cfad2dbd36ac2564c6bde7da1139aab0e74ad1141a23c",
        "r1_health_settings_plan_command",
        "R1 method-sensitive health-settings read and transition planner",
        (), "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00032598, 0x000326B2, 282,
        "08fbc118a7e78dbc5d62af22c60f8566677788a25ddc42446ec0e89dc6914b9b",
        "r1_pb_fragment_message",
        "R1 six-byte pb_tran CRC-32C transport fragmenter",
        ((0x0004E82C, "BL"),), "r1_product_specific",
        "clean_room_behavior_only", inventory_size=280,
    ),
)

GOODIX_FRONTIER_280_308_FUNCTIONS = (
    _function(
        0x00029D5C, 0x00029E88, 300,
        "5d0234e082228ae93c477e354bebf963d0e8b5912b75794be21d186c276ffb7c",
        "", "Goodix GH3X2X channel decimation and rolling-window update",
        ((0x0002A856, "BL"),), "goodix_gh3x2x_candidate",
        "vendor_source_required_not_redistributable",
    ),
)

ALL_FUNCTIONS = (
    R1_FRONTIER_280_308_PRODUCT_FUNCTIONS
    + GOODIX_FRONTIER_280_308_FUNCTIONS
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
        "analysis": "280...308-byte ownership frontier",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "inventory_bytes": sum(int(row["inventory_size"]) for row in rows),
        "product_function_count": len(R1_FRONTIER_280_308_PRODUCT_FUNCTIONS),
        "goodix_function_count": len(GOODIX_FRONTIER_280_308_FUNCTIONS),
        "functions": rows,
        "safety": {
            "live_ble_or_rtos_operation": False,
            "persistent_health_mutation": False,
            "private_event_emission": False,
            "goodix_provider_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
