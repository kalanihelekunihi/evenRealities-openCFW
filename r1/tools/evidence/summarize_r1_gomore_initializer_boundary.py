#!/usr/bin/env python3
"""Emit the exact GoMore-linked sensor-algorithm initializer boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_output_abi import IMAGE_SHA256


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000


def _function(
    entry: int,
    end_exclusive: int,
    role: str,
    sha256: str,
    callsites: tuple[int, ...],
) -> dict[str, object]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": end_exclusive - entry,
        "role": role,
        "provider_family": "gomore_health_algorithm_candidate",
        "sha256": sha256,
        "callsites": callsites,
    }


# Descriptive roles are boundary labels, not claims about private GoMore names.
# The root is reached only from an already SHA-pinned GoMore sleep-algorithm
# function. Six helpers are private to the root; the remaining state initializer
# is called only by that root and an already pinned GoMore algorithm-domain body.
GOMORE_INITIALIZER_FUNCTIONS = [
    _function(
        0x000715D4, 0x000715F6,
        "substate_initialize_with_shared_parameter",
        "0fb50e78394481e7e2b599c4ed64a53c1e42015b34928b87e249eacaa761f2cc",
        (0x00071A94,),
    ),
    _function(
        0x00071A32, 0x00071B24,
        "sensor_algorithm_composite_state_initialize",
        "3bc8ccd01acf0aab9317c04ea0644de381addf80b0843e6e4be71c74d7e9a2c3",
        (0x0006FFAE,),
    ),
    _function(
        0x00071B42, 0x00071B72,
        "two_window_and_nested_state_initialize",
        "0c24e69b87f43683184f417ee39b3d8ccc1564b31d9d70d1b61eecd317e052da",
        (0x00071A40,),
    ),
    _function(
        0x00071CD8, 0x00071D3E,
        "parameter_default_and_316_byte_state_initialize",
        "95bbba4d3a166d78d9d75589cb89b2497350420ef1397d7425ddd991f9c1518c",
        (0x00071AB6,),
    ),
    _function(
        0x00071D3E, 0x00071D62,
        "8444_byte_state_initialize_with_parameter_pointer",
        "345c039b99399c78751c9a400362f13bb524e150d1e81add2305d9bf609e7bfb",
        (0x00071AD6,),
    ),
    _function(
        0x00071D96, 0x00071D9E,
        "single_byte_substate_reset",
        "71901dacf0e9d57b7c001d4c0609c5b9fdd0667f5892fac5eb68ba0a693ac4fa",
        (0x00071A70,),
    ),
    _function(
        0x00071DD8, 0x00071E2C,
        "1736_byte_history_state_initialize",
        "0720d2275c53388404ef98f1a447e058c82f9af17d5d564adf39418ce0526ed7",
        (0x00069872, 0x00071B4A),
    ),
    _function(
        0x000720CE, 0x000720EE,
        "1028_byte_state_initialize_with_three_and_half_defaults",
        "08083b768d15be991dd89bf35dd4133ca019f4ec4d84184c38c0a9a444a03487",
        (0x00071AF0,),
    ),
]


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions = []
    for function in GOMORE_INITIALIZER_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"GoMore initializer boundary changed at 0x{entry:08x}")
        actual_callsites = tuple(
            address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
        )
        if actual_callsites != function["callsites"]:
            raise ValueError(
                f"GoMore initializer callers changed at 0x{entry:08x}: "
                f"{actual_callsites} != {function['callsites']}"
            )
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callsites": [f"0x{address:08x}" for address in actual_callsites],
        })

    return {
        "analysis": "R1 GoMore-linked sensor-algorithm initializer boundary",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "root": "0x00071a32",
        "root_callsite": "0x0006ffae",
        "root_caller_entry": "0x0006fea0",
        "functions": functions,
        "source_lineage": {
            "status": "gomore_health_algorithm_candidate",
            "private_symbols_claimed": False,
            "local_implementation_authorized": False,
            "reason": (
                "The root is exclusively called by an already SHA-pinned GoMore sleep body, "
                "initializes ten already gated GoMore substates plus these private helpers, "
                "and no licensed provider package or private symbols are available."
            ),
        },
        "safety": {
            "static_parser_only": True,
            "vendor_algorithm_reimplementation_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
