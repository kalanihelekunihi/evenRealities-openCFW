#!/usr/bin/env python3
"""Emit the exact Nordic nrfx_twim transfer-completeness helper boundary."""

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

NORDIC_TWIM_COMPLETENESS_FUNCTIONS = [
    {
        "entry": 0x00098DC0,
        "end_exclusive": 0x00098E22,
        "size": 98,
        "symbol": "xfer_completeness_check",
        "source": "modules/nrfx/drivers/src/nrfx_twim.c",
        "sha256": "8446af0756cad758941444cdf80848a92b988be41f55c39b21fea02c59fbe648",
        "callsites": (0x00093A44, 0x00093DB8),
    },
]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions: list[dict[str, Any]] = []
    for function in NORDIC_TWIM_COMPLETENESS_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"Nordic TWIM completeness body changed at 0x{entry:08x}")
        actual_callsites = tuple(
            address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
        )
        if actual_callsites != function["callsites"]:
            raise ValueError(
                f"Nordic TWIM completeness callers changed: {actual_callsites} != "
                f"{function['callsites']}"
            )
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callsites": [f"0x{address:08x}" for address in actual_callsites],
        })

    return {
        "analysis": "R1 application Nordic nrfx_twim transfer completeness helper",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "provider": {
            "family": "nordic_nrf5_sdk_17_1_0",
            "disposition": "use_nordic_sdk",
            "local_reimplementation_authorized": False,
        },
        "semantics": {
            "transfer_types": ["TXTX", "TXRX", "TX", "RX"],
            "compares_primary_and_secondary_easydma_amounts": True,
            "uses_suspended_mask_for_txtx_leg_selection": True,
            "resets_twim_on_incomplete_transfer": True,
            "reset_sequence": ["ENABLE=0", "ENABLE=6"],
        },
        "safety": {
            "static_parser_only": True,
            "provider_body_reimplementation_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
