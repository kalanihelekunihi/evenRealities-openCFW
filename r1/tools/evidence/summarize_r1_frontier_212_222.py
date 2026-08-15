#!/usr/bin/env python3
"""Pin and source-route the 212...222-byte R1 ownership frontier."""

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
    source_disposition: str, pointer_refs: tuple[int, ...] = (),
    inventory_size: int | None = None,
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": entry + size,
        "size": size,
        "inventory_size": size if inventory_size is None else inventory_size,
        "inventory": "ghidra_functions_csv",
        "sha256": sha256,
        "symbol": symbol,
        "role": role,
        "callers": callers,
        "pointer_refs": pointer_refs,
        "provider_family": provider_family,
        "source_disposition": source_disposition,
    }


R1_FRONTIER_212_222_PRODUCT_FUNCTIONS = (
    _function(
        0x0008F780, 220,
        "1182a58fa44d1a6604a6ce199c0ec9bb89197836f565778749646780ea7e786d",
        "r1_sleep_sync_ack_plan",
        "R1 stored-sleep ACK validation, event publication, and context release policy",
        (), "r1_product_specific", "clean_room_behavior_only", (0x0008DC08,),
    ),
    _function(
        0x000628F6, 220,
        "224de31e3354cda25afccaaf1fe79e2ed5c86f487d26a12d51c2f04cce7c9066",
        "r1_system_control_command_37_plan",
        "R1 system-control command 0x37 query, delay, reset, and reply policy",
        ((0x0004E33E, "BL"), (0x00062632, "B.W")),
        "r1_product_specific", "clean_room_behavior_only", inventory_size=214,
    ),
)


R1_FRONTIER_212_222_NORDIC_ADAPTERS = (
    _function(
        0x0003E7A8, 216,
        "02a62857a01de71165b3333acd731a9ed84b68fc39d627c207d30dfa89aba1f1",
        "r1_bae8_hvx_serialized_send_adapter",
        "R1 semaphore serialization and retry policy around Nordic BAE8 HVX",
        ((0x0004E658, "BL"), (0x0004E666, "BL")),
        "r1_nordic_sdk_provider_adapter",
        "clean_room_adapter_only_use_nordic_sdk",
    ),
    _function(
        0x00063D50, 218,
        "06f96e508e382495c190e183b3b19a50416e91b5d575108c5acd5a9712374f10",
        "r1_fds_event_adapter",
        "R1 FDS event-to-persistence-event translation and retry scheduling",
        (), "r1_nordic_sdk_provider_adapter",
        "clean_room_adapter_only_use_nordic_sdk", (0x0007E8B0,), 212,
    ),
)


R1_FRONTIER_212_222_CMBACKTRACE_ADAPTERS = (
    _function(
        0x0008EF28, 224,
        "34d34c056f5fda6c96f8e9bee2208126192d8ba1cdba5d428dd6f9c78db80c7e",
        "r1_fault_thread_snapshot_adapter",
        "R1 task-table formatting around FreeRTOS and CmBacktrace fault reporting",
        ((0x00058626, "BL"),), "r1_cmbacktrace_provider_adapter",
        "clean_room_adapter_only_use_authenticated_provider", inventory_size=218,
    ),
)


GOODIX_FRONTIER_212_222_FUNCTIONS = (
    _function(
        0x00072FB8, 222,
        "1052d75e35458b9e04cafb0c1c6161750ce7aad4520647ddc460bb3607109eaa",
        "goodix_primitives_zero_masked_sign_runs",
        "Goodix sign-mask contiguous-run output fill",
        ((0x0007675A, "BL"),), "goodix_gh3x2x_candidate",
        "clean_room_reimplementation_owner_authorized",
    ),
)


UNKNOWN_SENSOR_STREAM_FRONTIER_212_222_FUNCTIONS = (
    _function(
        0x0008A45C, 222,
        "3780414589164761818b5d19148d6f7caae185a4a680b0b7045ed3a1b5a9acdb",
        "sensor_stream_timer_poll_candidate",
        "unattributed sensor-stream timer sweep and minimum-delay selection",
        ((0x00092344, "BL"), (0x000925D8, "BL")),
        "unknown_sensor_stream_framework_candidate",
        "clean_room_reimplementation_owner_authorized",
    ),
)


ALL_FUNCTIONS = (
    R1_FRONTIER_212_222_PRODUCT_FUNCTIONS
    + R1_FRONTIER_212_222_NORDIC_ADAPTERS
    + R1_FRONTIER_212_222_CMBACKTRACE_ADAPTERS
    + GOODIX_FRONTIER_212_222_FUNCTIONS
    + UNKNOWN_SENSOR_STREAM_FRONTIER_212_222_FUNCTIONS
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
                f"direct callers changed at 0x{function['entry']:08x}: {observed}"
            )
        for pointer_ref in function["pointer_refs"]:
            offset = pointer_ref - LOAD_BASE
            if int.from_bytes(image[offset:offset + 4], "little") != (int(function["entry"]) | 1):
                raise ValueError(f"pointer reference changed at 0x{pointer_ref:08x}")
        functions.append({
            **function,
            "entry": f"0x{function['entry']:08x}",
            "end_exclusive": f"0x{function['end_exclusive']:08x}",
            "callers": [
                {"callsite": f"0x{site:08x}", "kind": kind}
                for site, kind in function["callers"]
            ],
            "pointer_refs": [f"0x{ref:08x}" for ref in function["pointer_refs"]],
        })
    return {
        "image_sha256": digest,
        "function_count": len(ALL_FUNCTIONS),
        "function_bytes": sum(int(item["size"]) for item in ALL_FUNCTIONS),
        "inventory_bytes": sum(int(item["inventory_size"]) for item in ALL_FUNCTIONS),
        "product_function_count": len(R1_FRONTIER_212_222_PRODUCT_FUNCTIONS),
        "nordic_adapter_count": len(R1_FRONTIER_212_222_NORDIC_ADAPTERS),
        "cmbacktrace_adapter_count": len(R1_FRONTIER_212_222_CMBACKTRACE_ADAPTERS),
        "goodix_function_count": len(GOODIX_FRONTIER_212_222_FUNCTIONS),
        "unknown_sensor_stream_count": len(UNKNOWN_SENSOR_STREAM_FRONTIER_212_222_FUNCTIONS),
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
            f"{result['function_bytes']} bytes in the 212...222-byte closure"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
