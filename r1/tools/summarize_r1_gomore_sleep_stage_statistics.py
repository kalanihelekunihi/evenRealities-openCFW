#!/usr/bin/env python3
"""Pin the private GoMore sleep-stage statistics closure in R1 firmware."""

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


GOMORE_SLEEP_STAGE_STATISTICS_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x00068FD4,
        "end_exclusive": 0x0006911A,
        "size": 326,
        "role": "sleep interval and efficiency statistics block",
        "symbol": "gomore_sleep_interval_statistics_candidate",
        "sha256": "afa31edc4912f2d02293bdd725b6762bcbb8ee3663e36c6a15e2347f389a7f60",
        "caller_count": 1,
        "caller_digest": "d22ad5def70a1f1221d442bf366d3b7207a98b0e29200b3d8feedcde1935be54",
        "inventory": "ghidra_functions_csv",
    },
    {
        "entry": 0x00069128,
        "end_exclusive": 0x000692D6,
        "size": 430,
        "role": "sleep-stage fraction, ratio, and duration statistics block",
        "symbol": "gomore_sleep_stage_statistics_candidate",
        "sha256": "7602275b0249f68eed4ef03295b1c3ae05adc949d71b71ea9b81f668afbeda0c",
        "caller_count": 1,
        "caller_digest": "1d34d2233f1d387080ade4db12979d9fa680ef3e444b1c0987b3fc6b6130b782",
        "inventory": "ghidra_functions_csv",
    },
    {
        "entry": 0x0006951E,
        "end_exclusive": 0x00069546,
        "size": 40,
        "role": "timestamp-indexed stage lookup helper",
        "symbol": "gomore_sleep_stage_lookup_candidate",
        "sha256": "68704b376c6239caa65d6a5679c08e552872b91e475fa5b93670777d3a83ead4",
        "caller_count": 2,
        "caller_digest": "34dd7928559f4af7799343fff458f2ae60ed52c88365a0ef69363d482892ccff",
        "inventory": "ghidra_functions_csv",
    },
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in GOMORE_SLEEP_STAGE_STATISTICS_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"GoMore sleep-stage statistics body mismatch at 0x{start:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, start)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"GoMore sleep-stage statistics caller set mismatch at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"address": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    return {
        "analysis": "supplemental GoMore sleep-stage statistics boundary",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 3,
        "function_bytes": 796,
        "functions": functions,
        "callgraph": {
            "finalizer_function": "0x00068f8c",
            "first_statistics_callsite": "0x00068fa4",
            "second_statistics_callsite": "0x00068fb4",
            "stage_lookup_callsites": ["0x00069050", "0x000691a6"],
            "stage_lookup_outside_caller_count": 0,
            "outside_caller_exclusivity": True,
        },
        "observable_contract": {
            "epoch_minutes": 0.5,
            "first_block_field_count": 7,
            "second_block_field_count": 12,
            "zero_ratio_denominator_result": 0.0,
            "unknown_nonzero_stage_counts_as_sleep_only_in_first_block": True,
        },
        "boundary": {
            "provider_family": "gomore_health_algorithm_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "private_symbol_or_sdk_version_resolved": False,
            "local_algorithm_reimplementation_authorized": False,
            "vendor_source_or_binary_required": True,
        },
        "safety": {
            "static_parser_only": True,
            "live_health_data_read": False,
            "algorithm_executed": False,
            "algorithm_code_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
