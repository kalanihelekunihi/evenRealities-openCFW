#!/usr/bin/env python3
"""Pin Nordic HAL inline instances omitted from the R1 Ghidra inventory."""

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

R1_NORDIC_OMITTED_HAL_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x0007902C,
        "end_exclusive": 0x0007903E,
        "size": 18,
        "symbol": "nrf_gpio_cfg_default",
        "source": "modules/nrfx/hal/nrf_gpio.h",
        "sha256": "0225ea03c5a9447c82d7a50a869c409e1415b8b56d6aca2da81ec9037d99e1a4",
        "callers": (),
        "scatter_thumb_pointer_addresses": (0x200075F0,),
        "role": "default GPIO configuration inline",
    },
    {
        "entry": 0x000791E4,
        "end_exclusive": 0x000791F8,
        "size": 20,
        "symbol": "nrf_gpio_pin_clear",
        "source": "modules/nrfx/hal/nrf_gpio.h",
        "sha256": "5d9088f1d1399da831f929bd6c63b824486fbbefaca6605772b6bb1f9d428b3e",
        "callers": (),
        "scatter_thumb_pointer_addresses": (0x200075D4,),
        "role": "GPIO OUTCLR inline",
    },
    {
        "entry": 0x00079E10,
        "end_exclusive": 0x00079E20,
        "size": 16,
        "symbol": "nrf_saadc_channel_input_set",
        "source": "modules/nrfx/hal/nrf_saadc.h",
        "sha256": "89cc89d1dc3ea948787e9ab258dded01450b8bdf17c6408f6983c0ba4493015a",
        "callers": (0x0007AF28, 0x0007AF62, 0x0007B0C8, 0x0007B0DC, 0x0007B126),
        "scatter_thumb_pointer_addresses": (),
        "role": "SAADC channel positive/negative input selector inline",
    },
)


def _all_runtime_pointer_addresses(runtime: bytes, pointer: int) -> tuple[int, ...]:
    needle = struct.pack("<I", pointer)
    addresses: list[int] = []
    offset = 0
    while True:
        found = runtime.find(needle, offset)
        if found < 0:
            return tuple(addresses)
        addresses.append(DEFAULT_SCATTER_RUNTIME + found)
        offset = found + 1


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    source_offset = mapped_offset(DEFAULT_SCATTER_SOURCE, DEFAULT_BASE, len(image))
    runtime, consumed = decompress_scatter(
        image[source_offset:], DEFAULT_SCATTER_LENGTH
    )

    output: list[dict[str, Any]] = []
    for function in R1_NORDIC_OMITTED_HAL_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
        callers = tuple(
            address for address, _kind in
            direct_thumb_branches_to(image, DEFAULT_BASE, entry)
        )
        pointer_addresses = _all_runtime_pointer_addresses(runtime, entry + 1)
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"] or \
                pointer_addresses != function["scatter_thumb_pointer_addresses"]:
            raise ValueError(
                f"Nordic omitted HAL inline changed at 0x{entry:08x}"
            )
        output.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [f"0x{address:08x}" for address in callers],
            "scatter_thumb_pointer_addresses": [
                f"0x{address:08x}" for address in pointer_addresses
            ],
        })

    saadc_literal = struct.unpack_from(
        "<I", image, 0x00079E20 - DEFAULT_BASE
    )[0]
    if saadc_literal != 0x40007000:
        raise ValueError(f"unexpected SAADC base literal: 0x{saadc_literal:08x}")

    return {
        "analysis": "Nordic SDK 17.1.0 omitted HAL inline closure",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(output),
        "function_bytes": sum(
            int(function["size"])
            for function in R1_NORDIC_OMITTED_HAL_FUNCTIONS
        ),
        "ghidra_function_count": 0,
        "manual_supplement_count": len(output),
        "functions": output,
        "saadc": {
            "base_literal_address": "0x00079e20",
            "base_literal": "0x40007000",
            "literal_is_outside_executable_extent": True,
            "direct_callers": 5,
        },
        "scatter": {
            "source": f"0x{DEFAULT_SCATTER_SOURCE:08x}",
            "runtime": f"0x{DEFAULT_SCATTER_RUNTIME:08x}",
            "consumed_bytes": consumed,
            "gpio_thumb_pointer_count": 2,
        },
        "boundary": {
            "provider_family": "nordic_nrf5_sdk_17_1_0",
            "source_disposition": "use_nordic_sdk",
            "local_reimplementation_required": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
