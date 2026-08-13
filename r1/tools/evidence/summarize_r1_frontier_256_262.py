#!/usr/bin/env python3
"""Pin and source-route the 256...262-byte R1 frontier and exclusive provider helpers."""

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


R1_FRONTIER_256_262_PRODUCT_FUNCTIONS = (
    _function(
        0x00084524, 260,
        "eae704a3150d3880f21815ed4517e5a3367af3b8f7b2766106f4449998478fdc",
        "r1_system_settings_plan_command",
        "R1 system-settings read/write and REG1 action policy", (),
        "r1_product_specific", "clean_room_behavior_only", (0x0009A530,),
    ),
    _function(
        0x0004B718, 256,
        "08780302207c762a1a7ba9ee59e1c614ae89578c60b700013d9602aee5eda657",
        "r1_temperature_mode_plan_transition",
        "R1 temperature stream and timed-mode transition policy",
        ((0x0004BAC2, "BL"),), "r1_product_specific",
        "clean_room_behavior_only",
    ),
)


R1_FRONTIER_256_262_GOODIX_ADAPTER_FUNCTIONS = (
    _function(
        0x00081744, 272,
        "2b61c1a9d01a3eab9eb560558798972795e00249c8c72211d8b44d73cb8772e2",
        "r1_goodix_diagnostic_select",
        "R1 bounded selector over a licensed-provider Goodix diagnostic snapshot",
        (), "r1_goodix_provider_adapter",
        "clean_room_adapter_only_use_licensed_provider", (0x0009A5A4,),
        inventory_size=262,
    ),
)


GOMORE_FRONTIER_256_262_FUNCTIONS = (
    _function(
        0x0007CA94, 260,
        "601cceb77f1e3a94d5c4bbe9223d1cfd267638a6277eb03fe27d013db18949d7",
        "", "GoMore private floating-point max/average pooling executor", (),
        "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable", (0x00074C68,),
    ),
    _function(
        0x0007244E, 258,
        "ac1c79308e186202e3fb298ef473010525cf680e1d1ac65e4251edc93283116a",
        "", "GoMore private sleep/history force-wake reducer",
        ((0x0005D3AA, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00074C48, 30,
        "a0e429fbedac3cf956c04e4de5639e9e5844a71b3c8d9a2c0a2b0d0ad9cc5dcf",
        "", "GoMore private floating-point pooling descriptor constructor",
        ((0x00028964, "BL"), (0x0002986A, "BL")),
        "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0005D370, 130,
        "2cc47e755db4f4db4f05f82c7816eeae93d5f4cc747a155ff540a0b19417718b",
        "", "GoMore private force-wake snapshot wrapper",
        ((0x0006B540, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0007266A, 90,
        "4c60739a7802948cdf8700259c53e8d1dbaa7fa5d224f76d4987251769621f0d",
        "", "GoMore private sleep-history tail reconciliation",
        ((0x0005D3E8, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00072572, 154,
        "e74c076e8bcb4ca939a662ae38f6c032aafd8ee2db4242eb51584cf49a374ee9",
        "", "GoMore private sleep-history snapshot selector",
        ((0x00067BE4, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00072024, 158,
        "7c46d4b1395d569af656440d9ef203ceaf884c0ea37ce3417d416013e2c2f1fc",
        "", "GoMore private sleep/history weighted merge",
        ((0x00060D68, "BL"), (0x0007251C, "BL")),
        "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006476C, 4,
        "35670bb79141dd43ff99efdf7b3389dba10de780c792cf02a685a59f85553750",
        "", "GoMore private timestamp-field setter",
        ((0x00060CDE, "BL"), (0x0007248A, "BL"), (0x000725C6, "BL")),
        "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00068354, 198,
        "4f4c70498ed4fdc1349de57ff55db3e0ea5fe61354b0ab6273d0e04ecc300285",
        "", "GoMore private two-bit sleep-stage range extraction",
        ((0x000696E4, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00069500, 30,
        "71ab9471bda03a2df47e72f45d5d6df3582b6d75b1a4ac055f7dd844fde4d4d9",
        "", "GoMore private two-bit sleep-stage lookup",
        ((0x00068386, "BL"), (0x000683AA, "BL"),
         (0x000683D6, "BL"), (0x000683EE, "BL"),
         (0x00072696, "BL")), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
)


ALL_FUNCTIONS = (
    R1_FRONTIER_256_262_PRODUCT_FUNCTIONS
    + R1_FRONTIER_256_262_GOODIX_ADAPTER_FUNCTIONS
    + GOMORE_FRONTIER_256_262_FUNCTIONS
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
            (int(callsite), str(kind))
            for callsite, kind in direct_thumb_branches_to(
                image, LOAD_BASE, int(function["entry"])
            )
        )
        if observed != function["callers"]:
            raise ValueError(
                f"direct callers changed at 0x{function['entry']:08x}: {observed}"
            )
        for pointer_ref in function["pointer_refs"]:
            offset = pointer_ref - LOAD_BASE
            expected = int(function["entry"]) | 1
            if int.from_bytes(image[offset:offset + 4], "little") != expected:
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
        "analysis": "256...262-byte ownership frontier plus exclusive GoMore helpers",
        "image_sha256": digest,
        "function_count": len(ALL_FUNCTIONS),
        "function_bytes": sum(int(item["size"]) for item in ALL_FUNCTIONS),
        "inventory_bytes": sum(int(item["inventory_size"]) for item in ALL_FUNCTIONS),
        "frontier_function_count": 5,
        "frontier_function_bytes": 1306,
        "frontier_inventory_bytes": 1296,
        "exclusive_helper_count": 8,
        "exclusive_helper_bytes": 794,
        "product_function_count": len(R1_FRONTIER_256_262_PRODUCT_FUNCTIONS),
        "goodix_adapter_count": len(R1_FRONTIER_256_262_GOODIX_ADAPTER_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_256_262_FUNCTIONS),
        "functions": functions,
        "safety": {
            "live_goodix_access": False,
            "gomore_provider_reimplemented": False,
            "persistent_write": False,
            "regulator_svc_invoked": False,
            "sensor_stream_mutated": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
