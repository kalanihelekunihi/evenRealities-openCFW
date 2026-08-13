#!/usr/bin/env python3
"""Pin the R1 heart-rate packet-builder reset and bounded sync-flush behavior."""

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


R1_HR_SYNC_FLUSH_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x0003FA84,
        "end_exclusive": 0x0003FAA4,
        "size": 32,
        "role": "heart-rate day-packet builder reset preserving transport configuration",
        "symbol": "r1_hr_sync_builder_reset",
        "sha256": "227f7e1b5970ae27d2d11e614aaa53b0f2efd4fcde80e768b09014c43a2d8281",
        "caller_count": 5,
        "caller_digest": "9459c2edec6d112a573c960318760efe169a2e03bfbaaaef05ef2db80ee19809",
        "inventory": "ghidra_functions_csv",
    },
    {
        "entry": 0x0004011C,
        "end_exclusive": 0x0004033E,
        "size": 546,
        "role": "heart-rate day-packet flush and acknowledgement-context orchestration",
        "symbol": "r1_hr_sync_flush",
        "sha256": "a9dafada8f948645789374c3eb02eea58869bb66c96fb6bdb2ef4308e71d80fd",
        "caller_count": 5,
        "caller_digest": "0e548f30adf01d5908763e494c0e4057a6756c1c91d331ee18015b58a73bd329",
        "inventory": "ghidra_functions_csv",
    },
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in R1_HR_SYNC_FLUSH_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"heart-rate sync-flush body mismatch at 0x{start:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, start)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"heart-rate sync-flush caller set mismatch at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    return {
        "analysis": "R1 heart-rate day-packet reset and sync-flush closure",
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
