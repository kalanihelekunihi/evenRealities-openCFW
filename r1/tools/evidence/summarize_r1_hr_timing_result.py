#!/usr/bin/env python3
"""Pin the Ghidra-omitted R1 timing heart-rate result callback."""

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

FUNCTION_START = 0x00049B60
FUNCTION_END = 0x00049BEE
ENVELOPE_END = 0x00049C64

R1_HR_TIMING_RESULT_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": FUNCTION_START,
    "end_exclusive": FUNCTION_END,
    "size": FUNCTION_END - FUNCTION_START,
    "symbol": "r1_hr_timing_result_plan",
    "sha256": "7f67cff79576a5a37f457e0e79ba43c092cc2db09afea26f56e2a7cee70717a5",
    "callers": (),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

EXPECTED_STRINGS = {
    0x00049BF0: b"[RING]algo hr timing result: hr:%d, con:%d, sig:%d",
    0x00049C2C: b"algo hr timing result: hr:%d, con:%d, sig:%d",
    0x00049C5C: b"hr",
}
EXPECTED_LOCAL_CALLS = {
    0x000499E0: ((0x00049BB2, "BL"),),
    0x0004C634: ((0x00049BBA, "BL"),),
    0x0008ADA4: ((0x00049BCA, "BL"),),
    0x0008D8FC: ((0x00049BD6, "BL"),),
    0x00089B08: ((0x00049BDE, "BL"),),
    0x00049D10: ((0x00049BEA, "B.W"),),
}


def _read_c_string(image: bytes, address: int) -> bytes:
    start = address - DEFAULT_BASE
    return image[start:image.index(b"\0", start)]


def _local_calls(image: bytes, target: int) -> tuple[tuple[int, str], ...]:
    return tuple(
        item for item in direct_thumb_branches_to(image, DEFAULT_BASE, target)
        if FUNCTION_START <= item[0] < FUNCTION_END
    )


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_HR_TIMING_RESULT_FUNCTIONS[0]
    body = image[FUNCTION_START - DEFAULT_BASE:FUNCTION_END - DEFAULT_BASE]
    envelope = image[FUNCTION_START - DEFAULT_BASE:ENVELOPE_END - DEFAULT_BASE]
    callers = tuple(direct_thumb_branches_to(
        image, DEFAULT_BASE, FUNCTION_START))
    strings = {
        address: _read_c_string(image, address) for address in EXPECTED_STRINGS
    }
    callback_pointer = struct.unpack_from(
        "<I", image, 0x00049B44 - DEFAULT_BASE)[0]

    if len(body) != function["size"] or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            len(envelope) != 260 or \
            hashlib.sha256(envelope).hexdigest() != \
            "fdbe3e53648384a8845fe85d6b17ebdcd2e0f0b95550c5e6eb2b741d773804c1" or \
            callers != function["callers"] or strings != EXPECTED_STRINGS or \
            callback_pointer != FUNCTION_START + 1 or \
            any(_local_calls(image, target) != expected
                for target, expected in EXPECTED_LOCAL_CALLS.items()):
        raise ValueError("R1 timing heart-rate result callback changed")

    return {
        "analysis": "R1 timing heart-rate result callback",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": len(body),
        "envelope_bytes": len(envelope),
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "function": {
            **function,
            "entry": f"0x{FUNCTION_START:08x}",
            "end_exclusive": f"0x{FUNCTION_END:08x}",
            "callers": [],
        },
        "registration": {
            "callback_pointer_address": "0x00049b44",
            "callback_thumb_pointer": "0x00049b61",
            "topic": "hr",
            "direct_callers": 0,
        },
        "record_contract": {
            "input_bytes": 3,
            "fields": ("heart_rate", "confidence", "signal"),
            "heart_rate_minimum": 40,
            "heart_rate_maximum": 220,
            "health_publication_gate": True,
            "event_id": 6,
            "event_bytes": 8,
            "event_layout": "heart_rate_u8,zero_u8[3],firmware_clock_u32le",
        },
        "lifecycle": {
            "unregister_topic": "hr",
            "clear_timing_stream_handle": True,
            "release_timing_timer_if_present": True,
            "clear_timing_timer_handle": True,
            "runs_after_invalid_or_suppressed_result": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "sensor_stream_reimplemented_here": False,
            "clock_reimplemented_here": False,
            "event_bus_reimplemented_here": False,
            "logging_reimplemented": False,
            "live_optical_control_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2,
                     sort_keys=True))


if __name__ == "__main__":
    main()
