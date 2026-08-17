#!/usr/bin/env python3
"""Pin the product GPIO-input registry IRQ dispatcher omitted by Ghidra."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gpio_registry import INPUTS, INPUT_RECORD_SIZE, INPUT_REGISTRY


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
CALLBACK_POINTER_ADDRESS = 0x00054C20

R1_GPIO_INPUT_IRQ_DISPATCH_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0006ED94,
    "end_exclusive": 0x0006EDC8,
    "size": 52,
    "symbol": "r1_gpio_input_irq_dispatch",
    "sha256": "cce6c3331bbeeb45f432ebab1e540905c2b218d10db5ae0a655641d844a82692",
    "callers": (),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_GPIO_INPUT_IRQ_DISPATCH_FUNCTIONS[0]
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
    registry_literal = struct.unpack_from(
        "<I", image, end - DEFAULT_BASE
    )[0]
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"] or \
            callback_pointer != entry + 1 or \
            registry_literal != INPUT_REGISTRY:
        raise ValueError("R1 GPIO input IRQ dispatcher changed")

    pins = [int(item[2]) for item in INPUTS]
    if len(INPUTS) != 7 or pins != [15, 21, 17, 18, 33, 3, 33]:
        raise ValueError("R1 GPIO input registry topology changed")

    return {
        "analysis": "R1 product GPIO-input registry IRQ dispatch",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 52,
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
        "registry": {
            "base": f"0x{INPUT_REGISTRY:08x}",
            "record_count": len(INPUTS),
            "record_size": INPUT_RECORD_SIZE,
            "pin_offset": 8,
            "callback_offset": 40,
            "linear_pins": pins,
            "duplicate_linear_pin": 33,
        },
        "behavior": {
            "dispatch_all_matching_records": True,
            "null_callbacks_skipped": True,
            "callback_pin_truncated_to_uint8": True,
            "provider_action_forwarded_unchanged": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "gpio_access_performed": False,
            "nordic_gpiote_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
