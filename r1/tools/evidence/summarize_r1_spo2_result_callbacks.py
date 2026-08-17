#!/usr/bin/env python3
"""Pin the two Ghidra-omitted R1 SpO2 result callbacks."""

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

R1_SPO2_RESULT_CALLBACK_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x0004ABEC,
        "end_exclusive": 0x0004ACD2,
        "size": 230,
        "symbol": "r1_spo2_once_result_plan",
        "sha256": "9013c99396899353c4aac5a7154920955f6de3ac906731b23c6cc4e408c1fea3",
        "callers": (),
        "inventory": "manual_provenance_supplement",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
    {
        "entry": 0x0004ADA0,
        "end_exclusive": 0x0004AE9C,
        "size": 252,
        "symbol": "r1_spo2_timing_result_plan",
        "sha256": "f37ead6711312c1dc90ea1db45c89b0bd16016667a5e9752e66ee73b69485fc8",
        "callers": (),
        "inventory": "manual_provenance_supplement",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
)

ENVELOPES = (
    (0x0004ABEC, 0x0004AD40, 340,
     "803aca9ca84c390b65ba559bcc3131fb59c02f75d3d00ad2be84a9bce2ac8578"),
    (0x0004ADA0, 0x0004AF10, 368,
     "ba960dbad79ba963d6506470bf8fbefe031ab7102818711ab3a92214e766ba30"),
)

EXPECTED_STRINGS = {
    0x000C04FC: b"[RING]algo spo2 once result: spo2:%d, r_value:%d, con:%d, level:%d, hr:%d, mark:%d",
    0x000C0550: b"algo spo2 once result: spo2:%d, r_value:%d, con:%d, level:%d, hr:%d, mark:%d",
    0x0004ACE4: b"[RING]algo spo2 once calibrated: %d -> %d",
    0x0004AD10: b"algo spo2 once calibrated: %d -> %d",
    0x0004AD34: b"spo2",
    0x000C05A0: b"[RING]algo spo2 timing result: spo2:%d, r_value:%d, con:%d, level:%d, hr:%d, mark:%d",
    0x000C05F8: b"algo spo2 timing result: spo2:%d, r_value:%d, con:%d, level:%d, hr:%d, mark:%d",
    0x0004AEAC: b"[RING]algo spo2 timing calibrated: %d -> %d",
    0x0004AED8: b"algo spo2 timing calibrated: %d -> %d",
    0x0004AF00: b"spo2",
}

EXPECTED_LOCAL_CALLS = {
    0x0004ABEC: {
        0x0004AAC0: ((0x0004AC5E, "BL"),),
        0x0004C634: ((0x0004AC68, "BL"),),
        0x0004AA98: ((0x0004AC76, "BL"),),
        0x0008D8FC: ((0x0004ACBE, "BL"),),
        0x00089B08: ((0x0004ACC6, "BL"),),
    },
    0x0004ADA0: {
        0x0004AAC0: ((0x0004AE14, "BL"),),
        0x0004C634: ((0x0004AE20, "BL"),),
        0x0004AA98: ((0x0004AE2E, "BL"),),
        0x0008D8FC: ((0x0004AE76, "BL"),),
        0x00089B08: ((0x0004AE7E, "BL"),),
        0x0004B2E4: ((0x0004AE86, "BL"),),
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
    for function in R1_SPO2_RESULT_CALLBACK_FUNCTIONS:
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
                f"R1 SpO2 result callback changed at 0x{start:08x}")
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
            raise ValueError(f"R1 SpO2 result envelope changed at 0x{start:08x}")
        envelope_bytes += len(body)

    strings = {
        address: _read_c_string(image, address) for address in EXPECTED_STRINGS
    }
    once_pointer = struct.unpack_from(
        "<I", image, 0x0004AB2C - DEFAULT_BASE)[0]
    timing_pointer = struct.unpack_from(
        "<I", image, 0x0004B0F8 - DEFAULT_BASE)[0]
    if strings != EXPECTED_STRINGS or once_pointer != 0x0004ABED or \
            timing_pointer != 0x0004ADA1:
        raise ValueError("R1 SpO2 result registration or strings changed")

    return {
        "analysis": "R1 one-shot and timing SpO2 result callbacks",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 2,
        "function_bytes": sum(int(item["size"])
                              for item in R1_SPO2_RESULT_CALLBACK_FUNCTIONS),
        "envelope_bytes": envelope_bytes,
        "ghidra_function_count": 0,
        "manual_supplement_count": 2,
        "functions": functions,
        "registrations": (
            {
                "kind": "once",
                "callback_pointer_address": "0x0004ab2c",
                "callback_thumb_pointer": "0x0004abed",
                "topic": "spo2",
                "direct_callers": 0,
            },
            {
                "kind": "timing",
                "callback_pointer_address": "0x0004b0f8",
                "callback_thumb_pointer": "0x0004ada1",
                "topic": "spo2",
                "direct_callers": 0,
            },
        ),
        "record_contract": {
            "input_bytes": 6,
            "fields": (
                "spo2", "r_value", "confidence", "signed_level",
                "heart_rate", "mark"),
            "valid_minimum": 70,
            "valid_maximum": 100,
            "transform_center": 96,
            "below_center_numerator": 5,
            "at_or_above_center_numerator": 8,
            "transform_denominator": 10,
            "signed_division": "truncate_toward_zero",
            "output_minimum": 70,
            "output_maximum": 100,
            "health_publication_gate": True,
            "event_id": 8,
            "event_bytes": 8,
            "event_layout": "adjusted_spo2_u8,zero_u8[7]",
            "timestamp_present": False,
        },
        "lifecycle": {
            "both_unregister_topic": "spo2",
            "both_clear_stream_handle": True,
            "timing_releases_timer_if_present": True,
            "timing_clears_timer_handle": True,
            "timing_marks_valid_result": True,
            "timing_marks_invalid_result": True,
            "cleanup_runs_after_invalid_or_suppressed_result": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "gomore_transform_reimplemented_here": False,
            "sensor_stream_reimplemented_here": False,
            "health_gate_reimplemented_here": False,
            "event_bus_reimplemented_here": False,
            "timer_reimplemented_here": False,
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
