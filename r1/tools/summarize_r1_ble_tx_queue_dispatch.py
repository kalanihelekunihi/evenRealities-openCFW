#!/usr/bin/env python3
"""Pin the R1 BLE transmit-queue producer veneers and common dispatch body."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
CALL_GRAPH = ROOT / "research/decompilation/application/call-graph.csv"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


R1_BLE_TX_QUEUE_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x00034064,
        "end_exclusive": 0x00034070,
        "size": 12,
        "role": "BLE transmit-queue type-0 dispatch veneer",
        "symbol": "r1_ble_tx_queue_dispatch_type0",
        "sha256": "87384ba4fcae559338b8fda5ebfc680ea269ac253c14573d9a2be3e0898c4183",
        "caller_count": 3,
        "caller_digest": "7895ecdcb65d2d8d51bf90239f13d2185273253ba04b8363d644a6a2956e4912",
        "inventory": "ghidra_functions_csv",
        "segments": ((0x00034064, 0x00034070),),
    },
    {
        "entry": 0x00034070,
        "end_exclusive": 0x0003E48C,
        "size": 548,
        "role": "BLE transmit-queue type-2 veneer and common bounded producer",
        "symbol": "r1_ble_tx_queue_dispatch_type2",
        "sha256": "3b6bf6bff7c54cec4699a678cfe67eb59980abdf8864d2b38407d04fa3bf56f0",
        "caller_count": 5,
        "caller_digest": "7216f2153c3f3875bd540a37062e1fdc2687328da7f34895d9f1f9d6e2ac0388",
        "inventory": "ghidra_functions_csv",
        "segments": (
            (0x00034070, 0x0003407C),
            (0x0003E274, 0x0003E48C),
        ),
    },
)


def callsites_to(entry: int) -> list[tuple[int, str]]:
    with CALL_GRAPH.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return sorted(
            (int(row["from_address"], 16), "BL")
            for row in rows
            if int(row["callee_entry"], 16) == entry and
            row["reference_type"] == "UNCONDITIONAL_CALL"
        )


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in R1_BLE_TX_QUEUE_FUNCTIONS:
        entry = int(function["entry"])
        segments = tuple(function["segments"])
        body = b"".join(
            image[start - LOAD_BASE:end - LOAD_BASE]
            for start, end in segments
        )
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"BLE TX queue body mismatch at 0x{entry:08x}")
        callers = callsites_to(entry)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"BLE TX queue caller set mismatch at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in segments
            ],
        })

    return {
        "analysis": "R1 BLE transmit-queue producer closure",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 2,
        "function_bytes": 560,
        "functions": functions,
        "message_envelope": {
            "message_id_offset": 0,
            "dispatch_type_offset": 4,
            "payload_length_offset": 8,
            "payload_offset": 12,
            "allocation_size_formula": "align4(payload_length + 15)",
            "known_veneer_dispatch_types": [0, 2],
        },
        "queue_policy": {
            "near_full_threshold_percent": 90,
            "put_priority": 0,
            "put_timeout_raw": 100,
            "worker_signal_flag": 1,
            "free_envelope_on_put_failure": True,
            "return_success": 0,
            "return_failure": -1,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "third_party_implementation_identified": False,
            "freertos_heap_reimplemented": False,
            "cmsis_queue_or_thread_flags_reimplemented": False,
            "toolchain_memmove_reimplemented": False,
            "nordic_logging_reimplemented": False,
            "ble_transport_worker_reimplemented": False,
            "connection_handle_accessors_admitted": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_ble_sender_exposed": False,
            "private_payload_content_read": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
