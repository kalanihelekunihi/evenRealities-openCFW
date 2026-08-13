#!/usr/bin/env python3
"""Pin and source-route the 224...230-byte R1 ownership frontier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(
    entry: int, size: int, sha256: str, symbol: str, role: str,
    callers: tuple[tuple[int, str], ...], provider_family: str,
    source_disposition: str, pointer_refs: tuple[int, ...] = (),
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
        "pointer_refs": pointer_refs,
        "provider_family": provider_family,
        "source_disposition": source_disposition,
    }


R1_FRONTIER_224_230_PRODUCT_FUNCTIONS = (
    _function(
        0x00049838, 230,
        "fa53e4fba782075d0566bf47659cdb6b6968c0e1ec6a703a123a75613c8223cd",
        "r1_heart_rate_mode_plan_transition",
        "R1 heart-rate mode stream and 600-second timer transition policy",
        ((0x000499D2, "BL"),), "r1_product_specific",
        "clean_room_behavior_only",
    ),
    _function(
        0x00065D64, 228,
        "75633aa478660597d6d07d0d344b854aabfc4bc9073b27531d2a0055e3f6d29c",
        "r1_delayed_event_cancel",
        "R1 delayed-event callback/context cancellation and timer reschedule",
        (
            (0x00032180, "BL"), (0x000451E4, "BL"),
            (0x000451EC, "BL"), (0x0004527C, "BL"),
            (0x000453CA, "BL"), (0x00045458, "BL"),
            (0x0004548E, "BL"), (0x00045906, "BL"),
            (0x00045978, "BL"), (0x00046736, "BL"),
            (0x00047F46, "BL"), (0x00047F60, "BL"),
            (0x0004CA52, "BL"), (0x0004CA5C, "BL"),
            (0x0004D124, "BL"), (0x0004D5DA, "BL"),
            (0x0004DDC0, "BL"), (0x0004DE8A, "BL"),
            (0x0004E0BA, "BL"), (0x0004E0C6, "BL"),
            (0x0004E0D4, "BL"), (0x0004E208, "BL"),
            (0x00051B8C, "B.W"), (0x00052C04, "BL"),
            (0x00052CF0, "BL"), (0x00052CFC, "BL"),
            (0x00052E3A, "BL"), (0x00052E42, "BL"),
            (0x00052E4A, "BL"), (0x00052F72, "BL"),
            (0x0005D690, "BL"), (0x0006A79E, "BL"),
            (0x0006A7B4, "BL"), (0x0006A7E8, "BL"),
            (0x0006A804, "BL"), (0x0006A962, "BL"),
            (0x0006A96A, "BL"), (0x0007F32C, "BL"),
            (0x0007F334, "BL"), (0x0007F3D4, "BL"),
            (0x0007F434, "BL"), (0x0007F4BC, "BL"),
            (0x0007F59E, "BL"), (0x00084138, "BL"),
            (0x000846E8, "BL"), (0x00091FF8, "BL"),
            (0x000920E4, "B.W"), (0x00092BAA, "BL"),
            (0x00092BB2, "BL"), (0x00092EFA, "BL"),
            (0x0009343E, "BL"), (0x00096AE6, "BL"),
            (0x00096BFC, "BL"), (0x00096C0E, "BL"),
            (0x00096D52, "BL"),
        ),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00094C74, 226,
        "1c94d828ab675943b6e946655e8692329c49d0225cf7ed5236f89c8276a1ca1d",
        "r1_ring_stability_observe",
        "R1 eight-sample gate and 600-decision ring-stability detector",
        ((0x000492B2, "BL"),), "r1_product_specific",
        "clean_room_behavior_only",
    ),
    _function(
        0x0004D2F4, 224,
        "d9fa60a25d56e12c8f24f697a3968c09372cd391844b5c3aba07e9ab22ad6c0c",
        "r1_connection_phy_update_plan",
        "R1 connected-link gate around Nordic sd_ble_gap_phy_update",
        ((0x000533DA, "B.W"),), "r1_product_specific",
        "clean_room_behavior_only",
    ),
)


R1_FRONTIER_224_230_PRODUCT_HELPERS = (
    _function(
        0x000499C4, 22,
        "b25b08f1958e86b465cacaf0c87c7e08f29ae8a933af81bd2451ecb6f0308e75",
        "r1_heart_rate_mode_plan_transition",
        "R1 bounded mode-0...3 setter around the transition policy",
        ((0x0004220E, "B.W"),), "r1_product_specific",
        "clean_room_behavior_only",
    ),
    _function(
        0x00094A60, 76,
        "a2c725e76ef322e3dec200e1253e06609be1dac965d6fb79007cc38a9dee2297",
        "r1_ring_stability_observe",
        "R1 eight-value rolling window feeder used by the detector",
        ((0x000492AA, "BL"),), "r1_product_specific",
        "clean_room_behavior_only",
    ),
)


NORDIC_FRONTIER_224_230_FUNCTIONS = (
    _function(
        0x000309DC, 224,
        "2d2b8f7f9339240a2e01c58ae1beddcddb69619d29a48d4b043823cfea9c84af",
        "nrfx_pdm_irq_handler",
        "Nordic nrfx PDM STARTED/STOPPED double-buffer interrupt handler",
        (), "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk", (0x000270B4,),
    ),
)


SHARED_QUANTIZED_FRONTIER_224_230_FUNCTIONS = (
    _function(
        0x00036C7C, 228,
        "9a93470b26a6b71044994554398155f661cf05e24cc969e641d3d9330267d1ce",
        "shared_quantized_int8_add_candidate",
        "unattributed scale/zero-point int8 elementwise add executor",
        (), "unknown_shared_quantized_neural_runtime_candidate",
        "investigate_before_implementing", (0x00074CD8,),
    ),
)


ALL_FUNCTIONS = (
    R1_FRONTIER_224_230_PRODUCT_FUNCTIONS
    + R1_FRONTIER_224_230_PRODUCT_HELPERS
    + NORDIC_FRONTIER_224_230_FUNCTIONS
    + SHARED_QUANTIZED_FRONTIER_224_230_FUNCTIONS
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
    frontier_entries = {0x000309DC, 0x00036C7C, 0x00049838,
                        0x0004D2F4, 0x00065D64, 0x00094C74}
    frontier = [item for item in ALL_FUNCTIONS if item["entry"] in frontier_entries]
    helpers = [item for item in ALL_FUNCTIONS if item["entry"] not in frontier_entries]
    return {
        "image_sha256": digest,
        "function_count": len(ALL_FUNCTIONS),
        "function_bytes": sum(int(item["size"]) for item in ALL_FUNCTIONS),
        "frontier_function_count": len(frontier),
        "frontier_function_bytes": sum(int(item["size"]) for item in frontier),
        "supporting_helper_count": len(helpers),
        "supporting_helper_bytes": sum(int(item["size"]) for item in helpers),
        "product_function_count": len(R1_FRONTIER_224_230_PRODUCT_FUNCTIONS),
        "product_helper_count": len(R1_FRONTIER_224_230_PRODUCT_HELPERS),
        "nordic_function_count": len(NORDIC_FRONTIER_224_230_FUNCTIONS),
        "shared_quantized_runtime_count": len(SHARED_QUANTIZED_FRONTIER_224_230_FUNCTIONS),
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
            f"{result['function_bytes']} bytes in the 224...230-byte closure"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
