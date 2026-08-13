#!/usr/bin/env python3
"""Pin the private GoMore IIR coefficient designer called by its sleep initializer."""

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

GOMORE_IIR_DESIGNER_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x000717AC,
    "end_exclusive": 0x00071A06,
    "size": 602,
    "role": "private trigonometric IIR coefficient designer",
    "symbol": "gomore_private_iir_coefficient_designer",
    "sha256": "e36eeef662d968d1ab90a95916d778d50d3e4f1dd413ada83391f0cfecc0913a",
    "caller_count": 1,
    "caller_digest": "c3241b26a340377a2209af39688abacd05d37251bc051d05a96f5db075e5f7c8",
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in GOMORE_IIR_DESIGNER_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"GoMore IIR designer body mismatch at 0x{start:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, start)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"GoMore IIR designer caller set mismatch at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    return {
        "analysis": "supplemental GoMore private IIR coefficient-designer boundary",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 602,
        "functions": functions,
        "callgraph": {
            "sole_caller_function": "0x00071d62",
            "sole_callsite": "0x00071d76",
            "caller_existing_provider_family": "gomore_health_algorithm_candidate",
            "caller_existing_audit_scope": "sleep_algorithm",
            "outside_caller_exclusivity": True,
        },
        "dependencies": {
            "cosf": "0x00038a5c",
            "sinf": "0x0003ae04",
            "powf": "0x0003a620",
            "dependency_provider_family": "arm_toolchain_runtime",
            "dependency_bodies_included": False,
        },
        "boundary": {
            "provider_family": "gomore_health_algorithm_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "private_symbol_or_sdk_version_resolved": False,
            "local_algorithm_reimplementation_authorized": False,
            "toolchain_math_reimplementation_authorized": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_sensor_data_read": False,
            "algorithm_or_coefficients_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
