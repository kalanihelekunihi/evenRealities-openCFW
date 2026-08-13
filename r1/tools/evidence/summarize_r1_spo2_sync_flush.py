#!/usr/bin/env python3
"""Pin the R1 SpO2 packet-builder reset and bounded sync-flush behavior."""

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


R1_SPO2_SYNC_FLUSH_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x00043C80,
        "end_exclusive": 0x00043CA0,
        "size": 32,
        "role": "SpO2 day-packet builder reset preserving transport configuration",
        "symbol": "r1_spo2_sync_builder_reset",
        "sha256": "3725b1988300ebb4258420db5e99c5cddc5674b826476027653d69ec00437e0b",
        "caller_count": 5,
        "caller_digest": "b762f5092da727783ae81104c94509b1c5fe56116a157aa1e638c37eb0e1ec84",
        "inventory": "ghidra_functions_csv",
    },
    {
        "entry": 0x000442F4,
        "end_exclusive": 0x00044516,
        "size": 546,
        "role": "SpO2 day-packet flush and acknowledgement-context orchestration",
        "symbol": "r1_spo2_sync_flush",
        "sha256": "19780f7fc4d8f489e8776cfacd080a445258c250845460e305942bfa41f4ccc2",
        "caller_count": 5,
        "caller_digest": "ecdfc23f484617afc3b91a9806dc95757358bf6e16dcb311e69f571eb834667e",
        "inventory": "ghidra_functions_csv",
    },
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in R1_SPO2_SYNC_FLUSH_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"SpO2 sync-flush body mismatch at 0x{start:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, start)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"SpO2 sync-flush caller set mismatch at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    return {
        "analysis": "R1 SpO2 day-packet reset and sync-flush closure",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 2,
        "function_bytes": 578,
        "functions": functions,
        "packet": {
            "hour_slots": 24,
            "bytes_per_present_slot": 4,
            "fixed_prefix_bytes": 12,
            "header_count_bytes": 1,
            "header_timezone_bytes": 2,
            "header_day_timestamp_bytes": 4,
            "header_latest_value_bytes": 5,
            "ack_context_bytes": 8,
            "future_packet_drop": True,
            "builder_reset_after_attempt": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "third_party_implementation_identified": False,
            "freertos_allocator_reimplemented": False,
            "time_calendar_provider_reimplemented": False,
            "topic_or_transport_sender_reimplemented": False,
            "structured_logging_reimplemented": False,
            "sensor_or_biometric_algorithm_included": False,
        },
        "safety": {
            "static_parser_only": True,
            "private_history_read": False,
            "live_sender_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
