#!/usr/bin/env python3
"""Pin the indirect GoMore floating-point neural-layer runtime boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

LAYER_CONSTRUCTOR = 0x00074AAC
EXECUTOR_POINTER_ADDRESS = 0x00074B40
EXPECTED_EXECUTOR_POINTER = 0x00076BDD
EXPECTED_CONSTRUCTOR_CALLSITES = (
    0x00028994, 0x000289C0, 0x00028A14, 0x00028A40, 0x00028A6C, 0x00028A94,
    0x0002989A, 0x000298C6, 0x0002991E, 0x00029948, 0x0002997C, 0x000299AC,
    0x00043A70, 0x00043A9A, 0x00043ACA, 0x00043AF6,
)

GOMORE_NEURAL_RUNTIME_FUNCTIONS = ({
    "entry": 0x00076BDC,
    "end_exclusive": 0x000770AE,
    "size": 1234,
    "symbol": "quantized_runtime_float_conv1d_execute",
    "sha256": "61c6cdae7f85eb4096726de5fe67c5c7f85ce4bc6991ef4d45a19825779875ea",
    "provider_family": "gomore_health_algorithm_candidate",
    "source_disposition": "clean_room_reimplementation_owner_authorized",
},)


def _mapped(image: bytes, address: int, size: int) -> bytes:
    offset = address - LOAD_BASE
    if offset < 0 or offset + size > len(image):
        raise ValueError(f"address outside application image: 0x{address:08x}")
    return image[offset:offset + size]


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    function = GOMORE_NEURAL_RUNTIME_FUNCTIONS[0]
    body = _mapped(
        image,
        int(function["entry"]),
        int(function["end_exclusive"]) - int(function["entry"]),
    )
    if len(body) != function["size"] or \
            hashlib.sha256(body).hexdigest() != function["sha256"]:
        raise ValueError("GoMore neural-layer executor changed")

    pointer = struct.unpack("<I", _mapped(image, EXECUTOR_POINTER_ADDRESS, 4))[0]
    if pointer != EXPECTED_EXECUTOR_POINTER:
        raise ValueError(f"unexpected neural executor pointer: 0x{pointer:08x}")

    calls = direct_thumb_branches_to(image, LOAD_BASE, LAYER_CONSTRUCTOR)
    callsites = tuple(address for address, _encoding in calls)
    if callsites != EXPECTED_CONSTRUCTOR_CALLSITES:
        raise ValueError(f"neural layer-constructor callsites changed: {calls}")

    zero, sigmoid_limit, sigmoid_saturation = struct.unpack(
        "<fff", _mapped(image, 0x000770B0, 12)
    )
    if (zero, sigmoid_limit, sigmoid_saturation) != (0.0, 88.0, 88.0):
        raise ValueError("GoMore neural-layer activation constants changed")

    return {
        "analysis": "GoMore floating-point neural-layer runtime boundary",
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": len(body),
        "entry": "0x00076bdc",
        "body_sha256": function["sha256"],
        "indirect_dispatch": {
            "constructor": "0x00074aac",
            "pointer_address": "0x00074b40",
            "thumb_pointer": "0x00076bdd",
            "constructor_callsites": [f"0x{address:08x}" for address in callsites],
            "sleep_graph_builders": ["0x0002874c", "0x0002966c"],
            "additional_health_graph_builder": "0x0004387c",
        },
        "behavioral_census": {
            "floating_point_convolution": True,
            "specialized_kernel_widths": [1, 3, 5],
            "zero_padding_workspace": True,
            "bias_addition": True,
            "activation_modes": ["negative-slope/zero-floor", "sigmoid"],
            "sigmoid_exp_clamp": 88.0,
        },
        "ownership": {
            "provider_family": "gomore_health_algorithm_candidate",
            "source_disposition": "clean_room_reimplementation_owner_authorized",
            "exact_private_symbol_proven": False,
            "exact_sdk_version_proven": False,
            "local_reimplementation_permitted": True,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
