#!/usr/bin/env python3
"""Pin the R1 legacy opcode-0x91 ATI/touch calibration command policy."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
CALL_GRAPH = ROOT / "research/decompilation/application/call-graph.csv"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


R1_ATI_CALIBRATION_COMMAND_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0006210C,
    "end_exclusive": 0x000622B8,
    "size": 416,
    "role": "legacy opcode-0x91 ATI and touch-calibration command policy",
    "symbol": "r1_ati_calibration_command_plan",
    "sha256": "843951c84bc7b1def3a71058540210ee6eab68aacd2d20eb17e1e3e772664f98",
    "callers": ((0x0004E3EE, "BL"),),
    "inventory": "ghidra_functions_csv",
    "segments": (
        (0x0006210C, 0x00062132),
        (0x0006213E, 0x000622B8),
    ),
},)

JUMP_TABLE_ADDRESS = 0x00062132
JUMP_TABLE_BYTES = bytes.fromhex("06233a5362758496b1b5b900")


def callsites_to(entry: int) -> tuple[tuple[int, str], ...]:
    with CALL_GRAPH.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return tuple(sorted(
            (int(row["from_address"], 16), "BL")
            for row in rows
            if int(row["callee_entry"], 16) == entry and
            row["reference_type"] == "UNCONDITIONAL_CALL"
        ))


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in R1_ATI_CALIBRATION_COMMAND_FUNCTIONS:
        entry = int(function["entry"])
        segments = tuple(function["segments"])
        body = b"".join(
            image[start - LOAD_BASE:end - LOAD_BASE]
            for start, end in segments
        )
        callers = callsites_to(entry)
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"ATI calibration command changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in segments
            ],
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    table = image[JUMP_TABLE_ADDRESS - LOAD_BASE:
                  JUMP_TABLE_ADDRESS - LOAD_BASE + len(JUMP_TABLE_BYTES)]
    if table != JUMP_TABLE_BYTES:
        raise ValueError("ATI calibration command jump table changed")

    return {
        "analysis": "R1 legacy ATI/touch-calibration command policy",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 416,
        "functions": functions,
        "jump_table": {
            "address": f"0x{JUMP_TABLE_ADDRESS:08x}",
            "bytes_hex": table.hex(),
            "subcommand_count": 11,
        },
        "behavior": {
            "opcode": "0x91",
            "subcommand_offset": 3,
            "argument_0_offset": 4,
            "argument_1_offset": 5,
            "default_response_status": 5,
            "query_success_response_status": 6,
            "event_flags": {
                "1": "0x00000040",
                "2": "0x00000080",
                "3": "0x00000100",
                "4": "0x00000200",
                "5": "0x00000400",
                "6": "0x00000800",
            },
            "configuration_words": {
                "3": [1, 1],
                "4": [2, 2],
                "5": [3, 1],
                "6": [4, 1],
            },
            "subcommand_6_booleanizes_argument_0": True,
            "subcommand_7_query_failure_value": "0xff",
            "subcommands_8_9_touch_source": 2,
            "subcommand_10_returns_ring_size": True,
            "unknown_subcommand_uses_default_response": True,
        },
        "dependencies": {
            "raw_print_level_store": "0x00093414",
            "event_flags_post": "0x00093504",
            "configuration_queue": "0x00093514",
            "calibration_read": "0x00072898",
            "response_transport": "0x0008967c",
            "touch_open": "0x0008e7d0",
            "touch_close": "0x0008e6a0",
            "ring_size_read": "0x0006a1cc",
            "logging": ["0x000914ec", "0x00091638", "Nordic nrf_log frontend"],
        },
        "ownership": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "local_surface": "bounded side-effect-free command planner",
            "iqs7211e_provider_reimplemented": False,
            "nordic_cmsis_queue_reimplemented": False,
            "transport_or_logging_reimplemented": False,
        },
        "safety": {
            "pure_planner_only": True,
            "live_touch_operation": False,
            "calibration_mutation": False,
            "transport_send": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
