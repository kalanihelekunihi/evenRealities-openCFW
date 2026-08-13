#!/usr/bin/env python3
"""Pin the R1 structured-log record encoder and live-cache boundary.

This static parser does not render or export private logs. It distinguishes the
R1 record/cache policy from Nordic's separately linked logging frontend, the
toolchain runtime, RTOS primitives, the unresolved clock/device providers, and
the separately audited log.bin writer/export path.
"""

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
    entry: int,
    end_exclusive: int,
    role: str,
    symbol: str,
    sha256: str,
    caller_count: int,
    caller_digest: str,
    inventory: str = "ghidra_functions_csv",
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": end_exclusive - entry,
        "role": role,
        "symbol": symbol,
        "sha256": sha256,
        "caller_count": caller_count,
        "caller_digest": caller_digest,
        "inventory": inventory,
    }


R1_STRUCTURED_LOG_FUNCTIONS = (
    _function(0x00041C5C, 0x00041D02, "live-cache copy/peek primitive",
              "r1_structured_log_cache_copy",
              "cb425dfaba16301000dc30cc2414a65fa38e5a9e666884e78bee6fba5238136d",
              4, "9eaf095c6985ef21cd5e43bec3e65f3c08aa0bd330de6d135d1a2519ff01cd74"),
    _function(0x00041D08, 0x00041D2C, "live-cache available-byte count",
              "r1_structured_log_cache_available",
              "69308738acf4eda4a30f11a56355410236fd1f84c3181131550c8068f055e83f",
              2, "019a8b6ede9bf255f65f0364d6f39a2109d17f169e142c6d3f42fc9941fc03b8"),
    _function(0x00041D30, 0x00041E7C, "typed structured-log argument encoder",
              "r1_structured_log_encode_typed",
              "510877878471f5dc80ccc7057d67b40bf029b0fcc26024d5be59d816b6d85751",
              1, "b559f764d9b799f0e197ccbf785d619f88591878343b18060c76dca6f79aa1a9"),
    _function(0x00041E80, 0x00041F42, "live-cache append and flush policy",
              "r1_structured_log_cache_append",
              "607f8998e89c5067fcd13f04645f67f9ba6dce736bfa42e22479268fc26ed1cb",
              2, "5384d6fedde0e5e72bc264728e3521fab9bbbc427247ce66939e3279131d5c28"),
    _function(0x00046FD4, 0x0004723C, "format-aware structured-log argument encoder",
              "r1_structured_log_encode_format",
              "0e99618a9f34da9d8214dc35dd56fa05db03eb5de7f912e943565bce719e1bfd",
              1, "e2133bf58db5a6f99dc75c1080ae2b21f3b270a4818ffaa83dd52df064d8be9e"),
    _function(0x000514BC, 0x000514DC, "abstract clock-record timestamp adapter",
              "r1_structured_log_timestamp_adapter",
              "ac040b9ebf3c508fb228429b3ac268643ab792b2076d4797c4a14e81953c82fe",
              4, "97b7d079cde3d90dc69a6ceec2664852d9af3f49b2586b1a0e533ce612b296b4"),
    _function(0x000590A0, 0x000590A6, "log-export active-state query",
              "r1_structured_log_export_active",
              "3c0a2c335e8fcf80c4100a66f61a44a70183c0c30be0a8749f802571f9a6902e",
              3, "3277cbbe22cc6dc6138637bc2d8e1120b5d46ed0696730ab88e9805e5d52c961"),
    _function(0x00091460, 0x00091490, "live-cache read facade",
              "r1_structured_log_cache_read",
              "47b58f1680a5cbcc2f7eb93823e9df7e1ee5fdf3a98b915a40272e083d50f398",
              2, "e2d6edfd18f60cf3845e2d11deb3728d016454aec8c0c1225e447a1692800a18"),
    _function(0x00091490, 0x00091494, "live-cache count facade",
              "r1_structured_log_cache_count",
              "219b0cc1c96eb5343766394099da9a0fc9692c8d92fe005de5b0229afb943e86",
              1, "81efb33a15708f2dbb16ca311bd2292b7e080569d4d459f57008a43866124a50",
              "manual_provenance_supplement"),
    _function(0x00091494, 0x0009149A, "structured-log threshold setter",
              "r1_structured_log_threshold_set",
              "0594a3e6604c4c62a70819ee5094ceab26fb2eb8fbb5280fd4b92fff602100ce",
              1, "82eaaa19743421237c964b8b8e418e863a6c757144caa2ebff798f19e75df84f",
              "manual_provenance_supplement"),
    _function(0x000914A0, 0x000914E2, "periodic 4096-byte cache persistence",
              "r1_structured_log_periodic_persist",
              "32b8d5508582b1b5a506b727788fb363dd50b8fdf4072cc688f51d6ff3a6a123",
              1, "22bdf62f61c408829248e976230fc8aff44cabee4475974426b917f69f410d43",
              "manual_provenance_supplement"),
    _function(0x000914EC, 0x000914F2, "structured-log mode getter",
              "r1_structured_log_mode_get",
              "8f61f3207c802be9d89b3cfa1748adc458586b81abe646a9bf7b237057fa521b",
              2554, "1b352fe71b1189f3de992e6747083421109c006831ebd62f0310066c9501db15"),
    _function(0x000914F8, 0x000914FE, "structured-log mode setter",
              "r1_structured_log_mode_set",
              "2e9cd305fe6b02a0dab2e3f8d223d6c3eb0961e10d18c0f961bb0dd9a567f4a5",
              2, "abb6c959ffc21767aaa4dbe048aa7ee4280e2164b45f2a8062623c11f595eb60",
              "manual_provenance_supplement"),
    _function(0x000915A8, 0x00091634, "typed structured-log public facade",
              "r1_structured_log_typed",
              "b1c5c8fb913084c95d2d8cb3525ae8f87fc996322522c2b91e20aa102b15cb14",
              4, "2b46309234488cb5a422108c4e390eb3625fad31adec2c24c662522f9feba40d"),
    _function(0x00091638, 0x000916C2, "format-aware structured-log public facade",
              "r1_structured_log_format",
              "1149c1622b0e178d5239f810d6eb25afdb8f76fd4fe742e1b63dfa49be888cfd",
              853, "ecacf5b0bf93f342ed20970eedc948c0eda94f1b98678bc15f0fe5fefaf5d11f"),
    _function(0x00091864, 0x0009186A, "clock-source availability getter",
              "r1_structured_log_clock_available",
              "8f61f3207c802be9d89b3cfa1748adc458586b81abe646a9bf7b237057fa521b",
              4, "0b179a78042f47e34b30ae0de37ab62bb87c3769e56231549bd2e4d9c6084525"),
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in R1_STRUCTURED_LOG_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(function["size"]) or hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"structured-log body mismatch at 0x{start:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, start)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or caller_digest != function["caller_digest"]:
            raise ValueError(f"structured-log caller set mismatch at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    return {
        "analysis": "R1 structured-log encoder and live-cache closure",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(functions),
        "function_bytes": sum(int(function["size"]) for function in functions),
        "ghidra_function_count": sum(
            function["inventory"] == "ghidra_functions_csv" for function in functions
        ),
        "manual_function_count": sum(
            function["inventory"] == "manual_provenance_supplement" for function in functions
        ),
        "functions": functions,
        "record": {
            "magic": "0x7b",
            "sequence_bytes": 1,
            "tick_modulus": 1000,
            "fixed_header_bits": "0xdc000000",
            "nordic_std_address_bits": 22,
            "maximum_argument_payload_bytes": 32,
            "copied_string_bytes": 16,
            "normal_persistence_bytes": 4096,
            "periodic_gate_raw": 10000,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "third_party_implementation_identified": False,
            "nordic_log_frontend_reimplemented": False,
            "toolchain_runtime_reimplemented": False,
            "rtos_critical_section_reimplemented": False,
            "clock_calendar_provider_reimplemented": False,
            "generic_device_registry_reimplemented": False,
            "log_bin_writer_or_export_sender_emitted": False,
        },
        "safety": {
            "static_parser_only": True,
            "private_log_content_read": False,
            "live_export_sender_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
