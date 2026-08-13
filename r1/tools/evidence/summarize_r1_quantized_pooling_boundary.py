#!/usr/bin/env python3
"""Pin the shared, unattributed quantized-neural pooling runtime boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

QUANTIZED_POOLING_RUNTIME_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00041816,
    "end_exclusive": 0x000419C8,
    "size": 434,
    "symbol": "shared_quantized_pooling_executor_candidate",
    "role": "indirect signed-int8 maximum/average pooling executor",
    "sha256": "a1ac9ab4d9a3ea8143872c726b60ae7c4d778f66ac8afab9b4d39816dca0cb09",
    "callers": (),
    "inventory": "ghidra_functions_csv",
},)

CONSTRUCTOR_ENTRY = 0x00074C6C
CONSTRUCTOR_END = 0x00074C8A
CONSTRUCTOR_SHA256 = "a0e429fbedac3cf956c04e4de5639e9e5844a71b3c8d9a2c0a2b0d0ad9cc5dcf"
POINTER_ADDRESS = 0x00074C8C
EXPECTED_POINTER = 0x00041817
EXPECTED_CONSTRUCTOR_CALLERS = (
    (0x000287C6, "BL"), (0x00028876, "BL"), (0x0002892E, "BL"),
    (0x000296D6, "BL"), (0x00029780, "BL"), (0x00029834, "BL"),
    (0x000438DE, "BL"), (0x0004398E, "BL"), (0x00043A42, "BL"),
    (0x0005D186, "BL"),
)


def _bytes(image: bytes, start: int, end: int) -> bytes:
    offset = start - LOAD_BASE
    if offset < 0 or end - LOAD_BASE > len(image):
        raise ValueError(f"range outside application image: 0x{start:08x}...0x{end:08x}")
    return image[offset:end - LOAD_BASE]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = QUANTIZED_POOLING_RUNTIME_FUNCTIONS[0]
    entry = int(function["entry"])
    body = _bytes(image, entry, int(function["end_exclusive"]))
    callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or callers:
        raise ValueError("quantized pooling executor changed")

    constructor = _bytes(image, CONSTRUCTOR_ENTRY, CONSTRUCTOR_END)
    constructor_callers = tuple(
        direct_thumb_branches_to(image, LOAD_BASE, CONSTRUCTOR_ENTRY)
    )
    pointer = struct.unpack("<I", _bytes(image, POINTER_ADDRESS, POINTER_ADDRESS + 4))[0]
    if hashlib.sha256(constructor).hexdigest() != CONSTRUCTOR_SHA256 or \
            constructor_callers != EXPECTED_CONSTRUCTOR_CALLERS or \
            pointer != EXPECTED_POINTER:
        raise ValueError("quantized pooling constructor topology changed")

    return {
        "analysis": "shared unattributed quantized-neural pooling boundary",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": len(body),
        "functions": [{
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callers": [],
        }],
        "indirect_dispatch": {
            "constructor": f"0x{CONSTRUCTOR_ENTRY:08x}",
            "constructor_sha256": CONSTRUCTOR_SHA256,
            "pointer_address": f"0x{POINTER_ADDRESS:08x}",
            "thumb_pointer": f"0x{pointer:08x}",
            "constructor_callsites": [
                f"0x{address:08x}" for address, _kind in constructor_callers
            ],
            "gomore_graph_builders": ["0x0002874c", "0x0002966c"],
            "goodix_graph_builders": ["0x0004387c", "0x0005d01c"],
        },
        "behavioral_census": {
            "signed_int8_input_and_output": True,
            "maximum_pooling_windows": [2, 4],
            "average_pooling_window": 3,
            "average_rounds_away_from_zero_at_half": True,
            "success_return": 0,
        },
        "boundary": {
            "provider_family": "unknown_shared_quantized_neural_runtime_candidate",
            "source_disposition": "investigate_before_implementing",
            "shared_by_gomore_and_goodix_graphs": True,
            "attributable_source_identified": False,
            "local_reimplementation_authorized": False,
        },
        "safety": {
            "static_parser_only": True,
            "neural_executor_exposed": False,
            "model_or_sensor_data_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
