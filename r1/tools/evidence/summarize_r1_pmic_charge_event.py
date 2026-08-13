#!/usr/bin/env python3
"""Pin the R1 PMIC charged-event, dock-status, and thermal policy boundary."""

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

R1_PMIC_CHARGE_EVENT_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00096AD0,
    "end_exclusive": 0x00096C62,
    "size": 402,
    "role": "R1 charge-event dock-status and thermal-control policy",
    "symbol": "r1_pmic_charge_event_plan",
    "sha256": "a079977932ae1d297bb451311bc998e001d9b3ae13efe0ff2769f14bc00ef67a",
    "callers": ((0x000463DE, "BL"), (0x00047F68, "BL"), (0x00047F82, "BL")),
    "inventory": "ghidra_functions_csv",
},)


def word(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address - LOAD_BASE)[0]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in R1_PMIC_CHARGE_EVENT_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"PMIC charge-event function changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    version = image[0x00096C6C - LOAD_BASE:0x00096C76 - LOAD_BASE]
    target_words = {
        "low_compare": word(image, 0x00096CB8),
        "low_store": word(image, 0x00096CBC),
        "mid_compare": word(image, 0x00096CC0),
        "mid_store": word(image, 0x00096CC4),
    }
    if version != b"2.2.6.0009" or target_words != {
        "low_compare": 0x40808312,
        "low_store": 0x40808312,
        "mid_compare": 0x4160F5C3,
        "mid_store": 0x4160F5C3,
    }:
        raise ValueError("PMIC charge-event literal pool changed")

    return {
        "analysis": "R1 PMIC charged-event policy closure",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 402,
        "functions": functions,
        "status_packet": {
            "working_buffer_bytes": 24,
            "dock_control_packet_bytes": 23,
            "prefix": [0, 1, 2],
            "version_offset": 13,
            "version": version.decode("ascii"),
            "reserved_zero_offsets": [11, 12, 23],
            "charge_bits": "0 not charging; 1 charging; 2 full",
            "temperature_bits": "(unsigned_milliunits / 1000) & 0x3f in bits 7..2",
            "multibyte_order": "little-endian",
        },
        "thermal_policy": {
            "zero": "no register change",
            "low_band": "1..14",
            "low_target_word": "0x40808312",
            "mid_band": "15..44",
            "mid_target_word": "0x4160f5c3",
            "high_band": "45..63",
            "high_register": "0x02",
            "high_value": "0xf8",
            "skip_equal_target": True,
        },
        "event_policy": {
            "sample_event": "0x01",
            "initial_cancel_suppression_event": "0x5a",
            "not_charging_cancel_is_unconditional": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "yhm_provider_reimplemented": False,
            "st_provider_reimplemented": False,
            "nordic_or_timer_provider_reimplemented": False,
        },
        "safety": {
            "pure_planner_only": True,
            "live_pmic_write": False,
            "live_nfc_operation": False,
            "live_event_publication": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
