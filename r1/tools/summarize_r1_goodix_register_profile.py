#!/usr/bin/env python3
"""Pin the Goodix GH3X2X private register-profile decoder boundary."""

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

GOODIX_REGISTER_PROFILE_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0002B6E0,
    "end_exclusive": 0x0002B8E2,
    "size": 514,
    "role": "private GH3X2X eight-channel register-profile decoder",
    "symbol": "goodix_register_profile_decoder_candidate",
    "sha256": "25a1ec257775b73fe1310c36758df77a32bed3314de24d61b8574c0fe9e61a4f",
    "caller_count": 1,
    "caller_digest": "f00d34b85455f97445d8df49ec029d56a569c909aa1fcc2c5941c90202669f0e",
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    function = GOODIX_REGISTER_PROFILE_FUNCTIONS[0]
    start = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[start - LOAD_BASE:end - LOAD_BASE]
    callers = direct_thumb_branches_to(image, LOAD_BASE, start)
    caller_digest = hashlib.sha256("".join(
        f"{address:08x}:{kind}\n" for address, kind in callers
    ).encode()).hexdigest()
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            len(callers) != int(function["caller_count"]) or \
            caller_digest != function["caller_digest"]:
        raise ValueError("Goodix register-profile body or caller set mismatch")
    return {
        "analysis": "supplemental Goodix GH3X2X register-profile decoder boundary",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 514,
        "functions": [{
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
        }],
        "callgraph": {
            "sole_caller_thunk": "0x0002a810",
            "sole_callsite": "0x0002a810",
            "caller_existing_provider_family": "goodix_gh3x2x_candidate",
            "caller_branch_kind": "B.W",
            "outside_caller_exclusivity": True,
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "private_symbol_or_sdk_version_resolved": False,
            "local_profile_decoder_reimplementation_authorized": False,
            "private_profile_layout_emitted": False,
            "live_register_io_exposed": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_device_access": False,
            "private_profile_blob_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
