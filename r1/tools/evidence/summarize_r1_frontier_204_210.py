#!/usr/bin/env python3
"""Pin and source-route the 204...210-byte R1 ownership frontier."""

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


def _function(
    entry: int, size: int, sha256: str, symbol: str, role: str,
    callers: tuple[tuple[int, str], ...], provider_family: str,
    source_disposition: str,
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": entry + size,
        "size": size,
        "inventory_size": size,
        "inventory": "ghidra_functions_csv",
        "sha256": sha256,
        "symbol": symbol,
        "role": role,
        "callers": callers,
        "provider_family": provider_family,
        "source_disposition": source_disposition,
    }


R1_FRONTIER_204_210_PRODUCT_FUNCTIONS = (
    _function(
        0x00089EEC, 210,
        "d806b2f96cd7a0fa4bcab8df9bdc79e06e5fc334eb0f5fc1ce21faff64cbdd1b",
        "r1_sensor_stream_registration_plan",
        "R1 Goodix-facing named sensor-stream callback and channel registration configuration",
        ((0x0009232E, "BL"), (0x000925A4, "BL")),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008A64C, 204,
        "7ee68b0089bf6e2836055619fe34f5dc6baf3bae0e15842f2d5bf11c42b6ebb3",
        "r1_activity_flash_record_enqueue_plan",
        "R1 future-time gates and six-bucket activity-record enqueue expansion",
        ((0x0004830A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
)


R1_FRONTIER_204_210_NORDIC_ADAPTERS = (
    _function(
        0x0004D4AC, 204,
        "0ebec75306dd6e0a7450dd673be94e6c98a287f7b3a70c1b9d7b658c05dea375",
        "r1_connection_parameter_mode_adapter",
        "R1 role-aware connection-parameter mode selection around Nordic GAP SVCs",
        ((0x00045AD2, "BL"),),
        "r1_nordic_sdk_provider_adapter",
        "clean_room_adapter_only_use_nordic_sdk",
    ),
)


R1_FRONTIER_204_210_STORAGE_ADAPTERS = (
    _function(
        0x00064B24, 204,
        "663ad294afe45f1be4f7c92c16c12738514aa40fb490b9acbfce4b4c9dc9b657",
        "r1_latest_valid_flash_slot_scan_adapter",
        "R1 newest-valid-slot scan over a configured FAL flash-device read callback",
        ((0x00094F38, "BL"),),
        "r1_internal_flash_provider_adapter",
        "clean_room_adapter_only_use_nordic_sdk_and_fal",
    ),
)


SHARED_TENSOR_FRONTIER_204_210_FUNCTIONS = (
    _function(
        0x00093628, 208,
        "22fc12b0ddc3dad47d2f3deb34f97d73eea0f3bdccd643a173b5a7b6a9df9e6c",
        "shared_tensor_arena_compaction_allocator_candidate",
        "unattributed twelve-descriptor tensor arena compaction and allocation",
        ((0x00091DAC, "BL"), (0x00091DD6, "BL")),
        "unknown_shared_quantized_neural_runtime_candidate",
        "investigate_before_implementing",
    ),
)


ALL_FUNCTIONS = (
    R1_FRONTIER_204_210_PRODUCT_FUNCTIONS
    + R1_FRONTIER_204_210_NORDIC_ADAPTERS
    + R1_FRONTIER_204_210_STORAGE_ADAPTERS
    + SHARED_TENSOR_FRONTIER_204_210_FUNCTIONS
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application SHA-256: {digest}")
    functions: list[dict[str, Any]] = []
    for function in ALL_FUNCTIONS:
        start = int(function["entry"]) - LOAD_BASE
        end = int(function["end_exclusive"]) - LOAD_BASE
        body = image[start:end]
        if len(body) != function["size"] or hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"function bytes changed at 0x{function['entry']:08x}")
        observed = tuple(
            (int(site), str(kind)) for site, kind in
            direct_thumb_branches_to(image, LOAD_BASE, int(function["entry"]))
        )
        if observed != function["callers"]:
            raise ValueError(
                f"direct branch words changed at 0x{function['entry']:08x}: {observed}"
            )
        functions.append({
            **function,
            "entry": f"0x{function['entry']:08x}",
            "end_exclusive": f"0x{function['end_exclusive']:08x}",
            "callers": [
                {"callsite": f"0x{site:08x}", "kind": kind}
                for site, kind in function["callers"]
            ],
        })
    return {
        "image_sha256": digest,
        "function_count": len(ALL_FUNCTIONS),
        "function_bytes": sum(int(item["size"]) for item in ALL_FUNCTIONS),
        "product_function_count": len(R1_FRONTIER_204_210_PRODUCT_FUNCTIONS),
        "nordic_adapter_count": len(R1_FRONTIER_204_210_NORDIC_ADAPTERS),
        "storage_adapter_count": len(R1_FRONTIER_204_210_STORAGE_ADAPTERS),
        "shared_tensor_count": len(SHARED_TENSOR_FRONTIER_204_210_FUNCTIONS),
        "functions": functions,
        "safety": {
            "provider_code_implemented_locally": False,
            "code_signing_bypassed": False,
            "private_keys_included": False,
            "device_programming_performed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()
    result = summarize(arguments.image)
    if arguments.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            f"verified {result['function_count']} functions / "
            f"{result['function_bytes']} bytes in the 204...210-byte closure"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
