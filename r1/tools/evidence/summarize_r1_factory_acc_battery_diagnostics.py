#!/usr/bin/env python3
"""Pin the Ghidra-omitted factory accelerometer and battery diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE
from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_FACTORY_ACC_BATTERY_DIAGNOSTIC_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x0004ED64,
        "end_exclusive": 0x0004EDAC,
        "size": 72,
        "symbol": "r1_factory_acc_diagnostic_plan_decode",
        "sha256": "c2ee443870c8d5c7e1426d03d974cb57f49984144cec1e066203fe15a62ecbdf",
        "callers": (),
        "inventory": "manual_provenance_supplement",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
    {
        "entry": 0x0004EE18,
        "end_exclusive": 0x0004EE38,
        "size": 32,
        "symbol": "r1_factory_battery_diagnostic_plan_build",
        "sha256": "9e5e60affb55774064cbe965e53c75d58cc6cac278660b2a70ad6df47b52446a",
        "callers": (),
        "inventory": "manual_provenance_supplement",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
)

ENVELOPES = (
    (0x0004ED64, 0x0004EDDC, 120,
     "590e953ab4c6f02a3f30ebdc8b7aee9d85df5773d4bf4d47ab5a3b6d39efbdbc"),
    (0x0004EE18, 0x0004EE64, 76,
     "839287d11a6963f9d812a5d3b8c5379649f37fca0f9e724f26974ce1f50bbae2"),
)

EXPECTED_STRINGS = {
    0x0004ED5C: b"at",
    0x0004ED60: b"acc",
    0x0004EDB0: b"[%d],accx:%d, accy:%d, accz:%d\n",
    0x0004EDD0: b"==========\n",
    0x0004EE3C: b"bat adc:%d mV, percent:%d, type:%d\r\n",
    0x0009944D: b"AT^BAT_ADC",
}

EXPECTED_LOCAL_CALLS = {
    0x0004ED64: {
        0x0004EF24: ((0x0004ED94, "BL"), (0x0004EDAA, "B.W")),
    },
    0x0004EE18: {
        0x00091290: ((0x0004EE1A, "BL"),),
        0x00091270: ((0x0004EE20, "BL"),),
        0x0007BB44: ((0x0004EE26, "BL"),),
        0x0004EF24: ((0x0004EE32, "BL"),),
    },
}


def _read_c_string(image: bytes, address: int) -> bytes:
    start = address - DEFAULT_BASE
    return image[start:image.index(b"\0", start)]


def _local_calls(
    image: bytes, start: int, end: int, target: int,
) -> tuple[tuple[int, str], ...]:
    return tuple(
        item for item in direct_thumb_branches_to(image, DEFAULT_BASE, target)
        if start <= item[0] < end
    )


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in R1_FACTORY_ACC_BATTERY_DIAGNOSTIC_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - DEFAULT_BASE:end - DEFAULT_BASE]
        callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, start))
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"] or \
                any(_local_calls(image, start, end, target) != expected
                    for target, expected in EXPECTED_LOCAL_CALLS[start].items()):
            raise ValueError(
                f"R1 factory diagnostic changed at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [],
        })

    envelope_bytes = 0
    for start, end, size, expected_sha256 in ENVELOPES:
        body = image[start - DEFAULT_BASE:end - DEFAULT_BASE]
        if len(body) != size or hashlib.sha256(body).hexdigest() != expected_sha256:
            raise ValueError(
                f"R1 factory diagnostic envelope changed at 0x{start:08x}")
        envelope_bytes += len(body)

    strings = {
        address: _read_c_string(image, address) for address in EXPECTED_STRINGS
    }
    acc_callback_pointer = struct.unpack_from(
        "<I", image, 0x0004ED58 - DEFAULT_BASE)[0]
    command_name_pointer, battery_handler_pointer = struct.unpack_from(
        "<II", image, 0x000C4230 - DEFAULT_BASE)
    if strings != EXPECTED_STRINGS or \
            acc_callback_pointer != 0x0004ED65 or \
            command_name_pointer != 0x0009944D or \
            battery_handler_pointer != 0x0004EE19:
        raise ValueError("R1 factory diagnostic registration or strings changed")

    return {
        "analysis": "R1 factory accelerometer and battery diagnostics",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 2,
        "function_bytes": sum(
            int(item["size"])
            for item in R1_FACTORY_ACC_BATTERY_DIAGNOSTIC_FUNCTIONS),
        "envelope_bytes": envelope_bytes,
        "ghidra_function_count": 0,
        "manual_supplement_count": 2,
        "functions": functions,
        "registrations": (
            {
                "kind": "sensor_stream_callback",
                "pointer_address": "0x0004ed58",
                "thumb_pointer": "0x0004ed65",
                "listener": "at",
                "topic": "acc",
                "direct_callers": 0,
            },
            {
                "kind": "factory_command",
                "table_record_address": "0x000c4230",
                "command_name_pointer": "0x0009944d",
                "command": "AT^BAT_ADC",
                "thumb_pointer": "0x0004ee19",
                "direct_callers": 0,
            },
        ),
        "accelerometer_contract": {
            "record_bytes": 182,
            "triplet_capacity": 30,
            "triplet_stride": 6,
            "count_offset": 180,
            "axis_encoding": "signed_int16_little_endian",
            "decimation": 5,
            "maximum_emitted_samples": 6,
            "emitted_indices": (0, 5, 10, 15, 20, 25),
            "terminator_always_emitted": True,
        },
        "battery_contract": {
            "accessor_order": (
                "battery_millivolts", "battery_percent", "battery_type"),
            "format_order": (
                "battery_millivolts", "battery_percent", "battery_type"),
            "handler_return_value": 1,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "sensor_stream_reimplemented_here": False,
            "battery_accessors_reimplemented_here": False,
            "factory_command_router_reimplemented_here": False,
            "logging_reimplemented": False,
            "live_sensor_control_exposed": False,
            "live_factory_command_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2,
                     sort_keys=True))


if __name__ == "__main__":
    main()
