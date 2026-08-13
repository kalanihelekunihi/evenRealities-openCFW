#!/usr/bin/env python3
"""Pin the omitted Goodix GH_HR private-context initializer boundary."""

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

GOODIX_HR_INIT_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x0006D204,
        "end_exclusive": 0x0006D39A,
        "size": 406,
        "role": "Goodix GH_HR private-context initializer",
        "symbol": "goodix_gh_hr_private_context_init_candidate",
        "sha256": "65fe2de6a621441725d19f187806681c1fe9f1652fafb68f1d9b2bcb4a6aa001",
        "callers": ((0x0006D41A, "BL"),),
        "inventory": "ghidra_functions_csv",
    },
    {
        "entry": 0x00072C48,
        "end_exclusive": 0x00072DBC,
        "size": 372,
        "role": "Goodix GH_HR 0x158-byte private subcontext initializer",
        "symbol": "goodix_gh_hr_private_subcontext_init_candidate",
        "sha256": "045e1b10cfe230f567b3c6dc47365ede835ce38e07b7dcb388f9f026683b03d6",
        "callers": ((0x0006D2B4, "BL"),),
        "inventory": "ghidra_functions_csv",
    },
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    functions = []
    for function in GOODIX_HR_INIT_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"Goodix HR initializer changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })
    return {
        "analysis": "Goodix GH_HR private-context initializer boundary",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(functions),
        "function_bytes": sum(int(function["size"]) for function in
                              GOODIX_HR_INIT_FUNCTIONS),
        "functions": functions,
        "provider_evidence": {
            "private_abi_string": "pv_v1.1.0",
            "sole_caller": "already gated Goodix HR version/output wrapper 0x0006d3c0",
            "primary_context_bytes": "0x150",
            "secondary_context_bytes": "0x158",
            "secondary_context_initializer": "0x00072c48",
            "secondary_initializer_sole_caller": "0x0006d2b4 in the gated primary initializer",
            "adjacent_version_builder": "0x0006d424",
            "adjacent_algorithm_core": "0x0006d51c",
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "local_reimplementation_authorized": False,
            "private_defaults_or_context_layout_admitted": False,
        },
        "safety": {
            "static_parser_only": True,
            "algorithm_execution": False,
            "biometric_data_read": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
