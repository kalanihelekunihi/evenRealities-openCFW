#!/usr/bin/env python3
"""Pin the no-effect delay callback installed in the R1 i2c_5 descriptor."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import (
    DEFAULT_BASE,
    DEFAULT_SCATTER_LENGTH,
    DEFAULT_SCATTER_RUNTIME,
    DEFAULT_SCATTER_SOURCE,
    decompress_scatter,
    mapped_offset,
)
from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
I2C5_DESCRIPTOR = 0x20007550
DELAY_CALLBACK_OFFSET = 0x28

R1_I2C5_DELAY_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00054AF0,
    "end_exclusive": 0x00054AFC,
    "size": 12,
    "role": "no-effect delay callback installed in software-driven i2c_5",
    "symbol": "r1_twi_i2c5_delay_noop",
    "sha256": "33ff9323be43957254a5dbd6680b5e2103e8484374493bdfcf56d6e35c48256a",
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

    function = R1_I2C5_DELAY_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
    callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, entry))
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"]:
        raise ValueError("R1 i2c_5 delay callback changed")

    source_offset = mapped_offset(
        DEFAULT_SCATTER_SOURCE, DEFAULT_BASE, len(image)
    )
    runtime, consumed = decompress_scatter(
        image[source_offset:], DEFAULT_SCATTER_LENGTH
    )
    pointer_offset = I2C5_DESCRIPTOR - DEFAULT_SCATTER_RUNTIME + \
        DELAY_CALLBACK_OFFSET
    pointer = struct.unpack_from("<I", runtime, pointer_offset)[0]
    if pointer != entry + 1:
        raise ValueError(f"unexpected i2c_5 delay pointer: 0x{pointer:08x}")

    return {
        "analysis": "R1 i2c_5 no-effect delay callback",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 12,
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "functions": [{
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [],
        }],
        "registration": {
            "scatter_source": f"0x{DEFAULT_SCATTER_SOURCE:08x}",
            "scatter_consumed_bytes": consumed,
            "descriptor_address": f"0x{I2C5_DESCRIPTOR:08x}",
            "descriptor_delay_offset": f"0x{DELAY_CALLBACK_OFFSET:02x}",
            "callback_thumb_pointer": f"0x{pointer:08x}",
            "direct_callers_expected": 0,
        },
        "behavior": {
            "input_argument_ignored": True,
            "nop_instruction_count": 5,
            "returns_without_side_effect": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "live_bus_timing_enabled": False,
            "gpio_or_transfer_provider_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
