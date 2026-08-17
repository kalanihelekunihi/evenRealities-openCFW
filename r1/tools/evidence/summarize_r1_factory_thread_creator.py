#!/usr/bin/env python3
"""Pin the Ghidra-omitted R1 factory-input thread creator."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import (
    DEFAULT_BASE, DEFAULT_SCATTER_LENGTH, DEFAULT_SCATTER_RUNTIME,
    DEFAULT_SCATTER_SOURCE, decompress_scatter,
)
from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_FACTORY_THREAD_CREATOR_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00045C54,
    "end_exclusive": 0x00045C84,
    "size": 48,
    "symbol": "r1_factory_input_thread_creation_plan_build",
    "sha256": "d85c228dacba440caeda739336298761c7a52619589196c7801535254c8255dc",
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
    function = R1_FACTORY_THREAD_CREATOR_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
    callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, entry))
    os_thread_new_calls = tuple(
        (address, kind)
        for address, kind in direct_thumb_branches_to(
            image, DEFAULT_BASE, 0x0007D818)
        if entry <= address < end
    )
    literals = struct.unpack_from(
        "<III", image, 0x00045C78 - DEFAULT_BASE)
    attributes = struct.unpack_from(
        "<9I", image, 0x000992D0 - DEFAULT_BASE)
    name_start = 0x000BEA50 - DEFAULT_BASE
    name_end = image.index(b"\0", name_start)
    scatter_source = image[DEFAULT_SCATTER_SOURCE - DEFAULT_BASE:]
    scatter, _ = decompress_scatter(scatter_source, DEFAULT_SCATTER_LENGTH)
    state_offset = 0x200066B0 - DEFAULT_SCATTER_RUNTIME
    state_words = struct.unpack_from("<II", scatter, state_offset)
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"] or \
            os_thread_new_calls != ((0x00045C5C, "BL"),) or \
            literals != (0x000992D0, 0x0009230D, 0x200066B0) or \
            attributes != (
                0x000BEA50, 0, 0, 0, 0, 8192, 39, 1, 0,
            ) or image[name_start:name_end] != b"factory_test" or \
            state_words != (0x00045C55, 0x00045C3D):
        raise ValueError("R1 factory-input thread creator changed")

    return {
        "analysis": "R1 factory-input thread creator",
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
            "state_block": "0x200066b0",
            "scatter_create_pointer": "0x00045c55",
            "scatter_stop_pointer": "0x00045c3d",
            "thread_entry_pointer": "0x0009230d",
        },
        "attributes": {
            "name": "factory_test",
            "stack_bytes": 8192,
            "priority_raw": 39,
            "trustzone_module": 1,
            "attribute_bits": 0,
            "control_block_memory": 0,
            "stack_memory": 0,
        },
        "result_policy": {
            "handle_stored_at_state_offset": 8,
            "null_handle_enters_fail_stop": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "cmsis_provider_reimplemented": False,
            "live_thread_creation_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
