#!/usr/bin/env python3
"""Pin a Goodix packed-channel decoder and its private scaling helper."""

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


GOODIX_CHANNEL_DECODER_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x000335B4,
        "end_exclusive": 0x000337BE,
        "size": 522,
        "role": "private packed-channel floating-point scaling helper",
        "symbol": "goodix_private_channel_scaling_helper_candidate",
        "sha256": "f9972cff9f72e10bd9b1bfb21ebaaa92763a058f8f857ef46bd5f1b7c61e0e3f",
        "caller_count": 3,
        "caller_digest": "4242d41534fc32faa0e8f8f37faa8d28cc575e5ab1fcd0caace937d84092ecd3",
        "inventory": "ghidra_functions_csv",
    },
    {
        "entry": 0x00061DA4,
        "end_exclusive": 0x00061EF2,
        "size": 334,
        "role": "Goodix packed three-channel decoder and record assembler",
        "symbol": "goodix_packed_channel_decoder_candidate",
        "sha256": "39fff2899dacfbad91bcff003cedfdac2ce2d9f0fbdd26f7f01db54927a98bfe",
        "caller_count": 1,
        "caller_digest": "a374bf791e970f9129e4c8b9032cde9aafede331bc8a1cdd5376d4770577e942",
        "inventory": "ghidra_functions_csv",
    },
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in GOODIX_CHANNEL_DECODER_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"Goodix channel-decoder body mismatch at 0x{start:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, start)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"Goodix channel-decoder caller set mismatch at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    return {
        "analysis": "supplemental Goodix packed-channel decoder boundary",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 2,
        "function_bytes": 856,
        "functions": functions,
        "callgraph": {
            "decoder_sole_callsite": "0x0006e874",
            "decoder_caller_provider_family": "goodix_gh3x2x_candidate",
            "helper_callsites": ["0x00061e42", "0x00061e86", "0x00061eca"],
            "helper_outside_caller_count": 0,
            "version_qualifier_dependency": "0x00066890",
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "private_symbol_or_sdk_version_resolved": False,
            "local_decoder_or_scaling_reimplementation_authorized": False,
            "coefficient_tables_or_formula_emitted": False,
            "toolchain_math_reimplemented": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_sensor_data_read": False,
            "private_coefficients_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
