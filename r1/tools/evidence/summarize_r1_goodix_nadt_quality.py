#!/usr/bin/env python3
"""Pin a private Goodix GH_NADT channel-quality/scoring function."""

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


GOODIX_NADT_QUALITY_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00088E80,
    "end_exclusive": 0x00089086,
    "size": 518,
    "role": "private GH_NADT channel-quality flags and derived-score update",
    "symbol": "goodix_nadt_channel_quality_candidate",
    "sha256": "9c4e682f8fe366f1b1f3c68743331392e9c8c80466e6463653bbf363bf3e825f",
    "caller_count": 1,
    "caller_digest": "21a9202e4352d08144ee2a1e8a2bf7e63d6776a408fda69b0a98923af823fb52",
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in GOODIX_NADT_QUALITY_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"Goodix NADT quality body mismatch at 0x{start:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, start)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"Goodix NADT quality caller set mismatch at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    return {
        "analysis": "supplemental Goodix GH_NADT channel-quality boundary",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 518,
        "functions": functions,
        "callgraph": {
            "sole_caller_function": "0x0006e838",
            "sole_callsite": "0x0006e916",
            "caller_existing_provider_family": "goodix_gh3x2x_candidate",
            "caller_component": "GH_NADT_pre v1.0.2.0 / 548d894d",
            "outside_caller_exclusivity": True,
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "private_symbol_or_sdk_version_resolved": False,
            "local_quality_or_score_reimplementation_authorized": False,
            "thresholds_or_formula_emitted": False,
            "toolchain_math_reimplemented": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_sensor_data_read": False,
            "private_thresholds_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
