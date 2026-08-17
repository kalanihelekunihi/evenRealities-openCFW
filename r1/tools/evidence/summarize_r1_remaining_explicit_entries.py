#!/usr/bin/env python3
"""Pin the final six Ghidra-analysis explicit application entries."""

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

R1_REMAINING_EXPLICIT_ENTRY_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x000547F4, "end_exclusive": 0x00054860, "size": 108,
        "symbol": "r1_analog_close_plan_build",
        "provider_family": "r1_analog_provider_adapter",
        "source_disposition": "clean_room_adapter_only_use_nordic_sdk",
        "sha256": "cd6408a273e5cd3fc6a0e8b89bee18e583e64548c8718c24691bb6331f509937",
        "callers": (),
    },
    {
        "entry": 0x00054B90, "end_exclusive": 0x00054C16, "size": 134,
        "symbol": "r1_gpio_input_open_plan_build",
        "provider_family": "r1_nordic_sdk_provider_adapter",
        "source_disposition": "clean_room_adapter_only_use_nordic_sdk",
        "sha256": "e38d6ca71816028adae320230a15921f7b1ee9a72fc2a193c04a7e54dffeca90",
        "callers": (),
    },
    {
        "entry": 0x0006F600, "end_exclusive": 0x0006F638, "size": 56,
        "symbol": "gxt310_read_temperature_milliunits",
        "provider_family": "gxcas_gxt310_candidate",
        "source_disposition": "clean_room_reimplementation_owner_authorized",
        "sha256": "f8e7e7060dc42cc772ec9e0c75bb0cd0210f4160c792f73398df0557e24dc87e",
        "callers": ((0x0006F80E, "B.W"), (0x0006F828, "B.W")),
    },
    {
        "entry": 0x0006F648, "end_exclusive": 0x0006F6B2, "size": 106,
        "symbol": "gxt310_switch_mode",
        "provider_family": "gxcas_gxt310_candidate",
        "source_disposition": "clean_room_reimplementation_owner_authorized",
        "sha256": "c2dd528f1696a7dec0fff2859d0940930d8f75de84d7d582a962e4fc9f9190fa",
        "callers": ((0x0006F808, "B.W"), (0x0006F822, "B.W")),
    },
    {
        "entry": 0x0006F738, "end_exclusive": 0x0006F794, "size": 92,
        "symbol": "gxt310_trigger_one_shot",
        "provider_family": "gxcas_gxt310_candidate",
        "source_disposition": "clean_room_reimplementation_owner_authorized",
        "sha256": "996e62bb9f1dfdb48ae224674b0771b1e6783d32fe4d8c81a003a1b21824e7b1",
        "callers": ((0x0006F81A, "B.W"), (0x0006F834, "B.W")),
    },
    {
        "entry": 0x00075290, "end_exclusive": 0x0007533A, "size": 170,
        "symbol": "r1_lis2dw12_double_tap_enable_plan_build",
        "provider_family": "r1_st_lis2dw12_provider_adapter",
        "source_disposition": "clean_room_adapter_only_use_pinned_provider",
        "sha256": "f7255c4ceb866f64a4489c915448ac6c4f1f02ffc4fdf7f1be5022648f1d0482",
        "callers": (),
    },
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")
    source = mapped_offset(DEFAULT_SCATTER_SOURCE, DEFAULT_BASE, len(image))
    runtime, _ = decompress_scatter(image[source:], DEFAULT_SCATTER_LENGTH)
    registrations = {
        "analog_close_thumb_pointer": struct.unpack_from(
            "<I", runtime, 0x20006F7C - DEFAULT_SCATTER_RUNTIME)[0],
        "gpio_input_open_thumb_pointer": struct.unpack_from(
            "<I", runtime, 0x200071FC - DEFAULT_SCATTER_RUNTIME)[0],
        "lis2dw12_double_tap_thumb_pointer": struct.unpack_from(
            "<I", image, 0x0009A740 - DEFAULT_BASE)[0],
    }
    if registrations != {
        "analog_close_thumb_pointer": 0x000547F5,
        "gpio_input_open_thumb_pointer": 0x00054B91,
        "lis2dw12_double_tap_thumb_pointer": 0x00075291,
    }:
        raise ValueError(f"explicit-entry registrations changed: {registrations}")

    functions = []
    for function in R1_REMAINING_EXPLICIT_ENTRY_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
        callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, entry))
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"explicit entry changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": tuple({"address": f"0x{address:08x}", "kind": kind}
                             for address, kind in callers),
            "inventory": "manual_provenance_supplement",
        })

    return {
        "analysis": "R1 final explicit-entry closure",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "ghidra_function_count": 0,
        "manual_supplement_count": len(functions),
        "functions": functions,
        "registrations": {
            key: f"0x{value:08x}" for key, value in registrations.items()
        },
        "analog_close_contract": {
            "record_count": 3,
            "record_size": 40,
            "nrfx_channels": (6, 4, 3),
            "uninitialize_driver_after_last_close": True,
            "not_found_status": 1,
        },
        "gpio_open_contract": {
            "record_count": 7,
            "record_size": 44,
            "pin_cnf_raw": 2,
            "initialize_gpiote_on_demand": True,
            "enable_port_event": True,
            "not_found_status": 2,
        },
        "gxt310_contract": {
            "read_scale": "signed_be16 * (1/128) * 1000",
            "mode_command_enabled": "00c2",
            "mode_command_disabled": "01c2",
            "one_shot_command": "01c1",
        },
        "lis2dw12_double_tap_contract": {
            "axis_enables": (1, 1, 1),
            "thresholds": (3, 3, 3),
            "duration_quiet_shock": (0, 0, 0),
            "tap_mode": 1,
            "int1_route_or_mask": 8,
            "return_value": 1,
        },
        "boundary": {
            "opaque_firmware_used": False,
            "hardware_operations_executed": False,
            "nordic_and_st_provider_calls_remain_external": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2,
                     sort_keys=True))


if __name__ == "__main__":
    main()
