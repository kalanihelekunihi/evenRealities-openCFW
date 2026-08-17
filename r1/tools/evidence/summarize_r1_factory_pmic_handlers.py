#!/usr/bin/env python3
"""Pin the three Ghidra-omitted R1 factory PMIC handlers."""

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

R1_FACTORY_PMIC_HANDLER_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x0004F4A4,
        "end_exclusive": 0x0004F4B6,
        "size": 18,
        "symbol": "r1_factory_pmic_current_diagnostic_plan_build",
        "sha256": "63368b0d8baa9f979c34e43d8fcb22d62d9b3d406e628a5909a45434405e986b",
        "callers": (),
        "inventory": "manual_provenance_supplement",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
    {
        "entry": 0x0004F4D4,
        "end_exclusive": 0x0004F50C,
        "size": 56,
        "symbol": "r1_factory_pmic_power_off_plan_build",
        "sha256": "2eb10962b78d9955ba18e7e248c54634961c3c0ed1c5a56b39559deca79076dc",
        "callers": (),
        "inventory": "manual_provenance_supplement",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
    {
        "entry": 0x0004F524,
        "end_exclusive": 0x0004F57C,
        "size": 88,
        "symbol": "r1_factory_pmic_register_diagnostic_plan_build",
        "sha256": "0c99a9668a257b387077589dcbc77e87c608c80e7dfaf5fea540bc463c03455c",
        "callers": (),
        "inventory": "manual_provenance_supplement",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
)

ENVELOPES = (
    (0x0004F4A4, 0x0004F4D4, 48,
     "a531e776e4f86cfaabb77ed89fc1e0638c004b0de1b51a44924624e907c3455b"),
    (0x0004F4D4, 0x0004F524, 80,
     "854b9cd35972c89007c794b2cffc5db3cf2a0976d196a034fee1362df9f66733"),
    (0x0004F524, 0x0004F598, 116,
     "aebf19ec25374940a9ec71d7e9b02e6f248ccda9c4094ded1bcc501a68a9b277"),
)

EXPECTED_STRINGS = {
    0x0004F4B8: b"pmic_isns_voltage:%d mv\r\n",
    0x0004F50C: b"at_pmic_power_off\r\n",
    0x0004F57C: b"pmic_register_read:\r\n",
    0x000BF6AC: b"0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X\r\n",
    0x00099431: b"AT^PMIC_READ",
    0x00099458: b"AT^PMIC_OFF",
    0x00099464: b"AT^PMIC_ISNS",
}

EXPECTED_LOCAL_CALLS = {
    0x0004F4A4: {
        0x000506A4: ((0x0004F4A6, "BL"),),
        0x0004EF24: ((0x0004F4AE, "BL"),),
    },
    0x0004F4D4: {
        0x0004EF24: ((0x0004F4D8, "BL"),),
        0x00091290: ((0x0004F4E6, "BL"),),
        0x0008ADA4: ((0x0004F4F2, "BL"),),
        0x00073710: ((0x0004F4FA, "BL"),),
        0x0007D6F4: ((0x0004F504, "BL"),),
    },
    0x0004F524: {
        0x00050748: ((0x0004F532, "BL"),),
        0x0004EF24: ((0x0004F538, "BL"), (0x0004F572, "BL")),
    },
}

COMMAND_RECORDS = (
    (0x000C4210, 0x00099431, 0x0004F525, "AT^PMIC_READ"),
    (0x000C4240, 0x00099458, 0x0004F4D5, "AT^PMIC_OFF"),
    (0x000C4250, 0x00099464, 0x0004F4A5, "AT^PMIC_ISNS"),
)


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
    for function in R1_FACTORY_PMIC_HANDLER_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - DEFAULT_BASE:end - DEFAULT_BASE]
        callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, start))
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"] or \
                any(_local_calls(image, start, end, target) != expected
                    for target, expected in EXPECTED_LOCAL_CALLS[start].items()):
            raise ValueError(f"R1 factory PMIC handler changed at 0x{start:08x}")
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
            raise ValueError(f"R1 factory PMIC envelope changed at 0x{start:08x}")
        envelope_bytes += len(body)

    if {address: _read_c_string(image, address)
            for address in EXPECTED_STRINGS} != EXPECTED_STRINGS:
        raise ValueError("R1 factory PMIC strings changed")
    registrations = []
    for record_address, name_pointer, handler_pointer, command in COMMAND_RECORDS:
        actual_name, actual_handler = struct.unpack_from(
            "<II", image, record_address - DEFAULT_BASE)
        if (actual_name, actual_handler) != (name_pointer, handler_pointer):
            raise ValueError(f"R1 factory PMIC table changed at 0x{record_address:08x}")
        registrations.append({
            "table_record_address": f"0x{record_address:08x}",
            "command_name_pointer": f"0x{name_pointer:08x}",
            "command": command,
            "handler_thumb_pointer": f"0x{handler_pointer:08x}",
            "direct_callers": 0,
        })
    format_pointer = struct.unpack_from(
        "<I", image, 0x0004F594 - DEFAULT_BASE)[0]
    if format_pointer != 0x000BF6AC:
        raise ValueError("R1 PMIC register format pointer changed")

    return {
        "analysis": "R1 factory PMIC handlers",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 3,
        "function_bytes": sum(
            int(item["size"]) for item in R1_FACTORY_PMIC_HANDLER_FUNCTIONS),
        "envelope_bytes": envelope_bytes,
        "ghidra_function_count": 0,
        "manual_supplement_count": 3,
        "functions": functions,
        "registrations": tuple(registrations),
        "current_sense_contract": {
            "provider_result_preserved": True,
            "handler_return_value": 1,
        },
        "power_off_contract": {
            "persistent_power_state": 2,
            "battery_millivolt_bits": 14,
            "packed_word": "((battery_mv & 0x3fff) << 2) | 2",
            "timestamp_preserved": True,
            "power_thread_flag": 1,
            "handler_return_value": 1,
        },
        "register_diagnostic_contract": {
            "provider_register": 9,
            "provider_read_bytes": 1,
            "formatted_bytes": 10,
            "formatted_layout": "register_9,zero[9]",
            "handler_return_value": 1,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "yhm2710_transport_reimplemented_here": False,
            "adc_sampling_reimplemented_here": False,
            "time_provider_reimplemented_here": False,
            "kv_persistence_reimplemented_here": False,
            "thread_signal_reimplemented_here": False,
            "logging_reimplemented": False,
            "live_power_off_exposed": False,
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
