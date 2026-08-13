#!/usr/bin/env python3
"""Pin and source-route the 230...248-byte R1 ownership frontier."""

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


R1_FRONTIER_230_248_PRODUCT_FUNCTIONS = (
    _function(
        0x00095168, 248,
        "ed98b97d47a79e50052c11f335e86cc96d8bbb63d0036d6ef578256d86ee2ac3",
        "r1_kv_store_get", "R1 newest-valid kv.bin slot reader", (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005E228, 236,
        "73c551c618987b0704727618c69a9896b90a535830d159bf49ef337f3631a5c6",
        "r1_ep_plan_initialization",
        "R1 ep.bin partition and flash-device readiness policy",
        ((0x0005E002, "BL"), (0x0005E06E, "BL"),
         (0x0005E094, "BL"), (0x0005E102, "BL")),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062A5C, 240,
        "b817aafc38f47db97d93cffb63f3dcf154fa5f9bf9b4b9eed86ea35c8fadb50f",
        "r1_legacy_device_info_build",
        "R1 legacy selector-0...4 device-info response formatter",
        ((0x0004E40C, "BL"), (0x000627B2, "B.W")),
        "r1_product_specific", "clean_room_behavior_only",
        inventory_size=234,
    ),
)


R1_FRONTIER_230_248_PRODUCT_HELPERS = (
    _function(
        0x0005E0EC, 40,
        "9990252180a7f869c46281832518a7649d3dcf013446395d17ae60a5ebab8d0f",
        "r1_ep_plan_initialization + r1_ep_scan_cursor",
        "R1 lazy ep.bin readiness and cursor-scan coordinator",
        ((0x0003ED90, "BL"), (0x00045D9C, "BL")),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007B9C8, 32,
        "d237bf82150a431f954bc6229616ed154be698e0b6694dee4835426da6c1f069",
        "r1_legacy_device_info_sources::accelerometer_calibration",
        "R1 six-byte accelerometer-calibration record accessor",
        ((0x00062AE2, "BL"), (0x0006F4C0, "BL")),
        "r1_product_specific", "clean_room_data_model_only",
    ),
    _function(
        0x0007B9EC, 24,
        "ddc34034403b008dc2c6cef92003cce0d19dbf8a0a8723e9385f52d9d5ce0cd2",
        "r1_legacy_device_info_sources::configuration_byte_0x78",
        "R1 configuration byte 0x78 accessor",
        ((0x0003CD66, "BL"), (0x00048BA6, "BL"),
         (0x00048BDE, "BL"), (0x0006238E, "BL"),
         (0x000623CE, "BL"), (0x00062B26, "BL"),
         (0x00081586, "BL"), (0x00096B76, "BL")),
        "r1_product_specific", "clean_room_data_model_only",
    ),
    _function(
        0x0007BA08, 22,
        "2cc2ce18e16a549ce6f7ed160952a17ae3908a5be84c4711ec2094ba36db760e",
        "r1_legacy_device_info_sources::configuration_word_0x74",
        "R1 configuration word 0x74 accessor",
        ((0x00048BAC, "BL"), (0x00048BF6, "BL"),
         (0x000623E8, "BL"), (0x00062B1E, "BL")),
        "r1_product_specific", "clean_room_data_model_only",
    ),
    _function(
        0x0007BA24, 24,
        "bab83d3250c31991eada49a1beaae1e3fb97abcb9c81dc62dde195c3d0d64fe2",
        "r1_legacy_device_info_sources::configuration_byte_0x70",
        "R1 configuration byte 0x70 accessor",
        ((0x00030EF8, "BL"), (0x0003EBC0, "BL"),
         (0x00046B5E, "BL"), (0x00046D12, "BL"),
         (0x00046E0A, "BL"), (0x000489F8, "BL"),
         (0x00048A06, "BL"), (0x00052D00, "BL"),
         (0x0005D63E, "BL"), (0x00062934, "BL"),
         (0x00062B16, "BL"), (0x00066CA2, "BL"),
         (0x00091272, "BL"), (0x00091292, "BL"),
         (0x00096AA8, "BL")),
        "r1_product_specific", "clean_room_data_model_only",
    ),
    _function(
        0x0007BA40, 50,
        "8f71c94d56628bbd6cb99647f0f004de3c627cd841f87273571eeca01d636631",
        "r1_legacy_device_info_sources::product_bsn",
        "R1 product-BSN record accessor with erased fallback",
        ((0x00062474, "BL"), (0x00062494, "BL"),
         (0x00062ABC, "BL"), (0x0006A25E, "BL")),
        "r1_product_specific", "clean_room_data_model_only",
    ),
    _function(
        0x0007BA78, 70,
        "e0798f9c1010c8dff11ebfc078a447b33494e900e8090f4af1a9f2fb896cfa31",
        "r1_legacy_device_info_sources::product_sn",
        "R1 product serial-number record accessor with erased fallback",
        ((0x00048A74, "BL"), (0x0006251C, "BL"),
         (0x0006253E, "BL"), (0x00062ACE, "BL"),
         (0x0006A1EE, "BL"), (0x00083DC6, "BL")),
        "r1_product_specific", "clean_room_data_model_only",
    ),
    _function(
        0x0007BADC, 34,
        "e3a1ca5de7529a960e94032aa2e1861ee8e158e9f13f1064d4c1b905f8641b7b",
        "r1_legacy_device_info_sources::temperature_calibration",
        "R1 six-byte temperature-calibration record accessor",
        ((0x00050E7A, "BL"), (0x00051172, "BL"),
         (0x0006242C, "BL"), (0x00062ADA, "BL")),
        "r1_product_specific", "clean_room_data_model_only",
    ),
)


GOMORE_FRONTIER_230_248_FUNCTIONS = (
    _function(
        0x000947DE, 248,
        "d8a0776a8e0c82ef262d2b0f639bd8a68fe13aa3cb3a1e5b0cbe7a6b0b7dabff",
        "", "GoMore private rolling per-minute sleep accumulator",
        ((0x000940DE, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00094070, 202,
        "5f78fdc1c263dbf976738b36f261ea354b46a6574b214c77b2e98b1ebb8c65e2",
        "", "GoMore private sleep-step orchestration",
        ((0x00060C78, "BL"),), "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00071B24, 6,
        "af8726735ff8020c5e3d8b953950de9a331d5aea1ca2d31bd3d21dc46149c4d4",
        "", "GoMore private 72-byte accumulator reset helper",
        ((0x00071D26, "BL"), (0x00094858, "BL")),
        "gomore_health_algorithm_candidate",
        "vendor_source_required_not_redistributable",
    ),
)


SHARED_QUANTIZED_FRONTIER_230_248_FUNCTIONS = (
    _function(
        0x00035E34, 242,
        "f2ecfeb5f11b06acbacf5c0c99c263c724dbdd591208bcf640742140a123a440",
        "shared_quantization_parameter_derivation_candidate",
        "unattributed quantization-scale and zero-point derivation",
        ((0x0002942C, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate",
        "investigate_before_implementing",
    ),
    _function(
        0x000293FC, 186,
        "6f27824db78a37c20e47d942305624ca744d68204c16200fd5fda9192223a026",
        "shared_float_to_signed_int8_quantizer_candidate",
        "indirect float-to-signed-int8 tensor quantizer", (),
        "unknown_shared_quantized_neural_runtime_candidate",
        "investigate_before_implementing", (0x00074D04,),
    ),
    _function(
        0x00074CE4, 30,
        "24c1b5e11fc2eda22cbd3bb0e786a2a5ef94513939778248292da18085cc3cfe",
        "shared_float_quantizer_descriptor_constructor_candidate",
        "descriptor constructor shared by GoMore and Goodix model graphs",
        ((0x0002876C, "BL"), (0x0002967E, "BL"),
         (0x0003087A, "BL"), (0x00036B7A, "BL"),
         (0x0004388E, "BL"), (0x0005D046, "BL")),
        "unknown_shared_quantized_neural_runtime_candidate",
        "investigate_before_implementing",
    ),
)


ALL_FUNCTIONS = (
    R1_FRONTIER_230_248_PRODUCT_FUNCTIONS
    + R1_FRONTIER_230_248_PRODUCT_HELPERS
    + GOMORE_FRONTIER_230_248_FUNCTIONS
    + SHARED_QUANTIZED_FRONTIER_230_248_FUNCTIONS
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
    frontier_entries = {0x000947DE, 0x00095168, 0x00035E34, 0x0005E228, 0x00062A5C}
    frontier = [item for item in ALL_FUNCTIONS if item["entry"] in frontier_entries]
    helpers = [item for item in ALL_FUNCTIONS if item["entry"] not in frontier_entries]
    return {
        "analysis": "230...248-byte ownership frontier plus supporting helpers",
        "image_sha256": digest,
        "function_count": len(ALL_FUNCTIONS),
        "function_bytes": sum(int(item["size"]) for item in ALL_FUNCTIONS),
        "inventory_bytes": sum(int(item["inventory_size"]) for item in ALL_FUNCTIONS),
        "frontier_function_count": len(frontier),
        "frontier_function_bytes": sum(int(item["size"]) for item in frontier),
        "frontier_inventory_bytes": sum(int(item["inventory_size"]) for item in frontier),
        "supporting_helper_count": len(helpers),
        "supporting_helper_bytes": sum(int(item["size"]) for item in helpers),
        "product_function_count": len(R1_FRONTIER_230_248_PRODUCT_FUNCTIONS),
        "product_helper_count": len(R1_FRONTIER_230_248_PRODUCT_HELPERS),
        "gomore_function_count": len(GOMORE_FRONTIER_230_248_FUNCTIONS),
        "shared_quantized_runtime_count": len(SHARED_QUANTIZED_FRONTIER_230_248_FUNCTIONS),
        "functions": functions,
        "safety": {
            "gomore_provider_reimplemented": False,
            "shared_neural_runtime_reimplemented": False,
            "live_flash_access": False,
            "persistent_write": False,
            "legacy_transport_sender_exposed": False,
            "live_device_identity_read": False,
        },
        "device_identity_source": "caller_supplied_only",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
