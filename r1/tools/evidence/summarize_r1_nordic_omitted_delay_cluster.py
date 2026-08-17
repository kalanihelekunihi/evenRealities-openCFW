#!/usr/bin/env python3
"""Pin the complete compiler-emitted Nordic microsecond-delay cluster."""

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
WRAPPER_BODY_SHA256 = "365d45f07ec7fae67922708c6a9ba072af22db02bb8419756150378123dcbf7d"
DELAY_BODY_SHA256 = "583d680532875ef2b855cbedbdfcdbdd74329d19ba88d3e52c36b6b634a75165"
SOURCE = "modules/nrfx/soc/nrfx_coredep.h"

DELAY_WRAPPERS: tuple[dict[str, Any], ...] = (
    {"entry": 0x0007A6DC, "target": 0x0009A640, "inventory": "manual_provenance_supplement",
     "callers": (), "scatter_thumb_pointer_addresses": (0x20007428,)},
    {"entry": 0x0007A6EC, "target": 0x0009A650, "inventory": "manual_provenance_supplement",
     "callers": (), "scatter_thumb_pointer_addresses": (0x20007498,)},
    {"entry": 0x0007A6FC, "target": 0x0009A660, "inventory": "manual_provenance_supplement",
     "callers": (), "scatter_thumb_pointer_addresses": (0x200075E8,)},
    {"entry": 0x0007A70C, "target": 0x0009C790, "inventory": "manual_provenance_supplement",
     "callers": (0x0007B0FC, 0x0007B18A), "scatter_thumb_pointer_addresses": ()},
    {"entry": 0x0007A71C, "target": 0x0009C7A0, "inventory": "ghidra_functions_csv",
     "callers": (0x00093906, 0x00093932, 0x0009393E, 0x00093950),
     "scatter_thumb_pointer_addresses": ()},
    {"entry": 0x0007A72C, "target": 0x0009D3D0, "inventory": "ghidra_functions_csv",
     "callers": (0x0002EB40, 0x0002EB4A), "scatter_thumb_pointer_addresses": ()},
)

R1_NORDIC_OMITTED_DELAY_FUNCTIONS: tuple[dict[str, Any], ...] = tuple(
    {
        "entry": int(wrapper["entry"]),
        "end_exclusive": int(wrapper["entry"]) + 12,
        "size": 12,
        "symbol": "nrfx_coredep_delay_us",
        "source": SOURCE,
        "sha256": WRAPPER_BODY_SHA256,
        "inventory": "manual_provenance_supplement",
    }
    for wrapper in DELAY_WRAPPERS
    if wrapper["inventory"] == "manual_provenance_supplement"
) + tuple(
    {
        "entry": int(wrapper["target"]),
        "end_exclusive": int(wrapper["target"]) + 6,
        "size": 6,
        "symbol": "nrfx_coredep_delay_us::delay_machine_code",
        "source": SOURCE,
        "sha256": DELAY_BODY_SHA256,
        "inventory": "manual_provenance_supplement",
    }
    for wrapper in DELAY_WRAPPERS
)


def _runtime_pointer_addresses(runtime: bytes, pointer: int) -> tuple[int, ...]:
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

    wrappers: list[dict[str, Any]] = []
    for wrapper in DELAY_WRAPPERS:
        entry = int(wrapper["entry"])
        target = int(wrapper["target"])
        body = image[entry - DEFAULT_BASE:entry - DEFAULT_BASE + 12]
        literal = struct.unpack_from("<I", image, entry - DEFAULT_BASE + 12)[0]
        callers = tuple(
            address for address, _kind in
            direct_thumb_branches_to(image, DEFAULT_BASE, entry)
        )
        pointer_addresses = _runtime_pointer_addresses(runtime, entry + 1)
        if hashlib.sha256(body).hexdigest() != WRAPPER_BODY_SHA256 or \
                literal != target + 1 or callers != wrapper["callers"] or \
                pointer_addresses != wrapper["scatter_thumb_pointer_addresses"]:
            raise ValueError(f"Nordic delay wrapper changed at 0x{entry:08x}")
        target_body = image[
            target - DEFAULT_BASE:target - DEFAULT_BASE + 6
        ]
        if hashlib.sha256(target_body).hexdigest() != DELAY_BODY_SHA256:
            raise ValueError(f"Nordic delay machine code changed at 0x{target:08x}")
        wrappers.append({
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{entry + 12:08x}",
            "target": f"0x{target:08x}",
            "target_end_exclusive": f"0x{target + 6:08x}",
            "literal_thumb_pointer": f"0x{literal:08x}",
            "inventory": wrapper["inventory"],
            "callers": [f"0x{address:08x}" for address in callers],
            "scatter_thumb_pointer_addresses": [
                f"0x{address:08x}" for address in pointer_addresses
            ],
        })

    return {
        "analysis": "Nordic SDK 17.1.0 omitted microsecond-delay cluster",
        "image": str(image_path),
        "image_sha256": digest,
        "wrapper_count": 6,
        "machine_code_count": 6,
        "function_count": 12,
        "function_bytes": 108,
        "ghidra_function_count": 2,
        "manual_supplement_count": 10,
        "manual_supplement_bytes": 84,
        "wrapper_body_sha256": WRAPPER_BODY_SHA256,
        "machine_code_body_sha256": DELAY_BODY_SHA256,
        "wrappers": wrappers,
        "scatter": {
            "source": f"0x{DEFAULT_SCATTER_SOURCE:08x}",
            "runtime": f"0x{DEFAULT_SCATTER_RUNTIME:08x}",
            "consumed_bytes": consumed,
            "registered_wrapper_count": 3,
        },
        "behavior": {
            "zero_returns_without_delay": True,
            "cycles_per_microsecond": 64,
            "delay_loop_instruction_sequence": "SUBS #3; BHI; BX LR",
        },
        "boundary": {
            "provider_family": "nordic_nrf5_sdk_17_1_0",
            "source_disposition": "use_nordic_sdk",
            "source": SOURCE,
            "local_reimplementation_required": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
