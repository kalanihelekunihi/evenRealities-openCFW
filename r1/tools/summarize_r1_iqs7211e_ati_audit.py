#!/usr/bin/env python3
"""Pin the R1 IQS7211E ATI-error diagnostic audit policy."""

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

R1_IQS7211E_ATI_AUDIT_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00041A40,
    "end_exclusive": 0x00041BB4,
    "size": 372,
    "role": "R1 IQS7211E ATI-error periodic diagnostic audit",
    "symbol": "r1_iqs7211e_ati_error_audit_policy",
    "sha256": "51820b7e27a675b7dd1b217f477e4aeaa7d3cd75ee5dd913bbdae642d4c109c3",
    "callers": ((0x0006FA2A, "BL"),),
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    function = R1_IQS7211E_ATI_AUDIT_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - LOAD_BASE:end - LOAD_BASE]
    callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
    if len(body) != function["size"] or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"]:
        raise ValueError("IQS7211E ATI audit function changed")
    literals = {
        "value_format": image[0x41BB8 - LOAD_BASE:0x41BBC - LOAD_BASE],
        "seven_by_three": image[0x41BBC - LOAD_BASE:0x41BC0 - LOAD_BASE],
        "eight_by_three": image[0x41BEC - LOAD_BASE:0x41BF0 - LOAD_BASE],
    }
    if literals != {
        "value_format": b"%u \0",
        "seven_by_three": b"7x3\0",
        "eight_by_three": b"8x3\0",
    }:
        raise ValueError(f"IQS7211E ATI audit literals changed: {literals}")
    return {
        "analysis": "R1 IQS7211E ATI-error diagnostic audit closure",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "callers": [{"callsite": f"0x{address:08x}", "kind": kind}
                    for address, kind in callers],
        "behavior": {
            "sequence_update": "UInt32 increment with wrap on every call",
            "first_sequence_audited": True,
            "later_interval_ticks": 10000,
            "tick_subtraction": "UInt32 wrap",
            "device_address": "0x56",
            "register": "0xe3",
            "seven_by_three_channels": 21,
            "eight_by_three_channels": 24,
            "sample_encoding": "little-endian UInt16",
            "inactive_map_value": "0xff",
            "empty_active_minimum": 0,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "clean_room_apis": ["r1_iqs7211e_ati_audit_begin",
                                "r1_iqs7211e_ati_audit_summarize"],
            "iqs7211e_transport_reimplemented": False,
            "cmsis_tick_reimplemented": False,
            "logging_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
