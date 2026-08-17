#!/usr/bin/env python3
"""Pin the Ghidra-omitted R1 Goodix open-mode policy callback."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE
from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
CALLBACK_POINTER_ADDRESS = 0x0009A59C
PROVIDER_TARGET = 0x00050B00
TABLE_ADDRESS = 0x000816B0
STATE_BASE_LITERAL_ADDRESS = 0x00081740

R1_GOODIX_OPEN_MODE_POLICY_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0008165C,
    "end_exclusive": 0x0008170A,
    "size": 174,
    "symbol": "r1_goodix_open_mode_plan_build",
    "sha256": "eecd6ba14ea56d621ef0731e0c3e7166b68eba67bee08576c5635a37531e0b0e",
    "callers": (),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

EXPECTED_TABLE = bytes((31, 5, 12, 22, 36, 16, 31, 40, 24, 28))
EXPECTED_TARGETS = (
    0x000816EE, 0x000816BA, 0x000816C8, 0x000816DC, 0x000816F8,
    0x000816D0, 0x000816EE, 0x00081700, 0x000816E0, 0x000816E8,
)
EXPECTED_CLEAR_MAP = {
    1: (0, 16),
    2: (40, 24),
    3: (188, 2),
    4: (16, 24),
    5: (64, 124),
    6: None,
    7: (216, 24),
    8: (192, 12),
    9: (204, 12),
}


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_GOODIX_OPEN_MODE_POLICY_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
    callers = tuple(
        address for address, _kind in
        direct_thumb_branches_to(image, DEFAULT_BASE, entry)
    )
    callback_pointer = struct.unpack_from(
        "<I", image, CALLBACK_POINTER_ADDRESS - DEFAULT_BASE
    )[0]
    provider_sites = tuple(
        (address, kind) for address, kind in
        direct_thumb_branches_to(image, DEFAULT_BASE, PROVIDER_TARGET)
        if entry <= address < end
    )
    table = image[TABLE_ADDRESS - DEFAULT_BASE:
                  TABLE_ADDRESS - DEFAULT_BASE + len(EXPECTED_TABLE)]
    targets = tuple(TABLE_ADDRESS + 2 * offset for offset in table)
    state_base = struct.unpack_from(
        "<I", image, STATE_BASE_LITERAL_ADDRESS - DEFAULT_BASE
    )[0]
    string_address = 0x0008170C
    diagnostic = image[string_address - DEFAULT_BASE:
                       string_address - DEFAULT_BASE + 22]
    log_literals = tuple(struct.unpack_from(
        "<II", image, 0x00081724 - DEFAULT_BASE
    ))
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"] or \
            callback_pointer != entry + 1 or \
            provider_sites != ((0x000816F4, "B.W"),) or \
            table != EXPECTED_TABLE or targets != EXPECTED_TARGETS or \
            state_base != 0x2001A23C or \
            diagnostic != b"[RING]ppg open type:%d" or \
            log_literals != (0x000C44FC, 0x000C441C):
        raise ValueError("R1 Goodix open-mode policy changed")

    return {
        "analysis": "R1 Goodix open-mode state policy",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": int(function["size"]),
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "function": {
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [],
        },
        "registration": {
            "callback_pointer_address": f"0x{CALLBACK_POINTER_ADDRESS:08x}",
            "callback_thumb_pointer": f"0x{callback_pointer:08x}",
            "direct_callers_expected": 0,
        },
        "dispatch": {
            "table_address": f"0x{TABLE_ADDRESS:08x}",
            "table_bytes": list(table),
            "targets": [f"0x{target:08x}" for target in targets],
            "state_base": f"0x{state_base:08x}",
            "clear_map": {str(mode): value
                          for mode, value in EXPECTED_CLEAR_MAP.items()},
            "provider_tail_callsite": "0x000816f4",
            "provider_target": f"0x{PROVIDER_TARGET:08x}",
        },
        "behavior": {
            "zero_input_returns_without_provider": True,
            "nonzero_input_narrows_to_uint8": True,
            "all_nonzero_inputs_request_provider_open": True,
            "diagnostic_only_for_narrowed_modes_0_through_4": True,
            "mode_6_shares_mode_2_provider_path_without_state_clear": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "goodix_provider_reimplemented": False,
            "logging_reimplemented": False,
            "live_optical_control_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
