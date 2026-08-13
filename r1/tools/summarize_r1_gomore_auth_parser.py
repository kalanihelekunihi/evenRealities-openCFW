#!/usr/bin/env python3
"""Pin the GoMore SDK authorization-parameter parser boundary."""

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


GOMORE_AUTH_PARSER_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0008EA0C,
    "end_exclusive": 0x0008EC20,
    "size": 528,
    "role": "GoMore SDK authorization-parameter parser and dispatcher",
    "symbol": "gomore_sdk_auth_parameter_parser_candidate",
    "segments": (
        (0x0008EA0C, 0x0008EA20),
        (0x0008EA24, 0x0008EC20),
    ),
    "sha256": "4d168fed892590719ff7187b985bd55011be122106dc85f192cc300a05c660d0",
    "caller_count": 1,
    "caller_digest": "89c30133f274cf13ec81bdd160439e31ea792bd70e19e157451895aeb4d851d7",
    "inventory": "ghidra_functions_csv",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in GOMORE_AUTH_PARSER_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = b"".join(
            image[segment_start - LOAD_BASE:segment_end - LOAD_BASE]
            for segment_start, segment_end in function["segments"]
        )
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"GoMore authorization body mismatch at 0x{start:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, start)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"GoMore authorization caller set mismatch at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    return {
        "analysis": "supplemental GoMore SDK authorization-parser boundary",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 528,
        "functions": functions,
        "callgraph": {
            "sole_caller_function": "0x0006b27c",
            "sole_callsite": "0x0006b38a",
            "caller_existing_provider_family": "gomore_health_algorithm_candidate",
            "caller_diagnostic": "gomore_setAuthParameters",
            "outside_caller_exclusivity": True,
        },
        "evidence": {
            "sdk_auth_diagnostics_present": True,
            "gomore_authorization_caller_present": True,
            "dispatch_tables_present": True,
            "r1_dual_aes_callback_dependency": "0x000891a4",
            "toolchain_strtok_dependency": "0x00027854",
            "unclassified_helper_bodies_included": False,
        },
        "boundary": {
            "provider_family": "gomore_health_algorithm_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "private_symbol_or_sdk_version_resolved": False,
            "local_authorization_reimplementation_authorized": False,
            "r1_crypto_or_toolchain_reimplemented": False,
            "unclassified_helpers_admitted": False,
        },
        "safety": {
            "static_parser_only": True,
            "private_key_material_read": False,
            "authorization_material_emitted": False,
            "live_authentication_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
