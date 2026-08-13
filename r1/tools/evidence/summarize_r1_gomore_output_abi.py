#!/usr/bin/env python3
"""Validate the complete R1 GoMore engine-to-host output-copy ABI.

This is a static, read-only firmware parser. It pins the exact 27-field copy routine, its sole
production caller, all literal roots of the fixed host I/O block, and the stock activity/sleep
consumers. It never reads live SRAM, starts the vendor engine, or emits health/key material.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to


IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
IO_STATE_ADDRESS = 0x2001A56C
IO_STATE_BYTES = 0x108
VENDOR_ENGINE_BYTES = 0x39E0
ENGINE_POINTER_SLOT = 0x20007C4C
OUTPUT_COPY_FUNCTION = 0x00059D9C

# Exact function body through BX LR. The literal immediately following it is validated separately.
OUTPUT_COPY_HEX = (
    "2f495830096801f5c07191ed290a80ed000a91f8ac20027191ed350a00ed040a"
    "91ed3e0a00ed030a91ed3f0a00ed020a91ed010a80ed120a91ed020a80ed130a"
    "91f87521027291f87621427291f877218272d1f844210261d1f84821426191f8"
    "5e21027691f85f21427691f86021827691f86121c276b1f8422120f8142c91f8"
    "9a2000f8042c91f8992000f8252c4a7880f828208a7880f829200a7880f82a20"
    "91f88021027791f881214277d1f888210262b1f89021c284b1f88c1181847047"
)

# Copy order is intentional and mirrors function 0x59d9c exactly. Width is the actual load/store
# width. A Float32 classification is made only where a producer independently uses VFP values.
FIELDS: list[dict[str, Any]] = [
    {"engine_offset": 0x224, "io_offset": 0x58, "width": 4, "storage": "float32", "semantic": "sps_selected_speed_candidate"},
    {"engine_offset": 0x22C, "io_offset": 0x5C, "width": 1, "storage": "uint8", "semantic": "sps_selected_speed_source_code"},
    {"engine_offset": 0x254, "io_offset": 0x48, "width": 4, "storage": "float32", "semantic": "energy_total_kcal"},
    {"engine_offset": 0x278, "io_offset": 0x4C, "width": 4, "storage": "float32", "semantic": "energy_s_kcal"},
    {"engine_offset": 0x27C, "io_offset": 0x50, "width": 4, "storage": "float32", "semantic": "energy_a_kcal"},
    {"engine_offset": 0x184, "io_offset": 0xA0, "width": 4, "storage": "float32", "semantic": "respiratory_rate_candidate_breaths_per_minute"},
    {"engine_offset": 0x188, "io_offset": 0xA4, "width": 4, "storage": "float32", "semantic": "respiratory_rate_confidence"},
    {"engine_offset": 0x2F5, "io_offset": 0x60, "width": 1, "storage": "uint8", "semantic": "sleep_stage_code"},
    {"engine_offset": 0x2F6, "io_offset": 0x61, "width": 1, "storage": "uint8", "semantic": "sleep_stage_updated"},
    {"engine_offset": 0x2F7, "io_offset": 0x62, "width": 1, "storage": "uint8", "semantic": "sleep_stage_ppg_request", "host_consumer": "sleep"},
    {"engine_offset": 0x2C4, "io_offset": 0x68, "width": 4, "storage": "uint32", "semantic": "sleep_interval_start_unix_seconds"},
    {"engine_offset": 0x2C8, "io_offset": 0x6C, "width": 4, "storage": "uint32", "semantic": "sleep_interval_end_unix_seconds"},
    {"engine_offset": 0x2DE, "io_offset": 0x70, "width": 1, "storage": "uint8", "semantic": "sleep_lifecycle_flags", "host_consumer": "sleep"},
    {"engine_offset": 0x2DF, "io_offset": 0x71, "width": 1, "storage": "uint8", "semantic": "sleep_transition_reason_code"},
    {"engine_offset": 0x2E0, "io_offset": 0x72, "width": 1, "storage": "uint8", "semantic": "sleep_interval_classification_code"},
    {"engine_offset": 0x2E1, "io_offset": 0x73, "width": 1, "storage": "uint8", "semantic": "sleep_interval_reconciliation_code"},
    {"engine_offset": 0x2C2, "io_offset": 0x44, "width": 2, "storage": "opaque16", "semantic": "dormant_initialization_zero"},
    {"engine_offset": 0x21A, "io_offset": 0x54, "width": 1, "storage": "uint8", "semantic": "motion_step_cadence_per_minute"},
    {"engine_offset": 0x219, "io_offset": 0x33, "width": 1, "storage": "uint8", "semantic": "motion_classifier_state_code"},
    {"engine_offset": 0x181, "io_offset": 0x80, "width": 1, "storage": "uint8", "semantic": "dormant_initialization_zero"},
    {"engine_offset": 0x182, "io_offset": 0x81, "width": 1, "storage": "uint8", "semantic": "dormant_estimator_status_low_byte"},
    {"engine_offset": 0x180, "io_offset": 0x82, "width": 1, "storage": "uint8", "semantic": "dormant_initialization_zero"},
    {"engine_offset": 0x300, "io_offset": 0x74, "width": 1, "storage": "uint8", "semantic": "dormant_initialization_one"},
    {"engine_offset": 0x301, "io_offset": 0x75, "width": 1, "storage": "uint8", "semantic": "dormant_initialization_zero"},
    {"engine_offset": 0x308, "io_offset": 0x78, "width": 4, "storage": "uint32", "semantic": "activity_steps", "host_consumer": "activity"},
    {"engine_offset": 0x310, "io_offset": 0x7E, "width": 2, "storage": "uint16", "semantic": "activity_kcal", "host_consumer": "activity"},
    {"engine_offset": 0x30C, "io_offset": 0x7C, "width": 2, "storage": "uint16", "semantic": "activity_all_kcal", "host_consumer": "activity"},
]

EXPECTED_IO_LITERAL_LOCATIONS = [
    0x00049678,
    0x0004C308,
    0x0006ACC4,
    0x0006ACD4,
    0x0006AD00,
    0x0006B1A8,
    0x0006B1EC,
    0x0006B220,
    0x0006B274,
    0x0006C238,
    0x0006C458,
]

EXPECTED_DIRECT_BRANCHES = {
    OUTPUT_COPY_FUNCTION: [0x000944BC],
    0x00076500: [0x000944B6],
    0x00048E68: [0x0006C2E2],
    0x00049E58: [0x0006C2EC],
}

EXPECTED_BYTES = {
    # Successful vendor update calls the compiled no-op, then the output copier.
    0x000944AA: "2946204600f06ff807462046e2f723f82046c5f76efc306800f5",
    # Worker output switch: activity consumer, slot-two no-op, then slot-three sleep logic.
    0x0006C2C8: "06eb05100078c00709d0042d07d2dfe805f002b1070c04f17800dcf7c1fda9e0",
    # Host sleep-stage request and lifecycle-flag reads.
    0x0006C2F2: "94f8700081071cd525f0f7f8c00703d125f0f3f8400706d594f87030",
    # Activity subscriber diagnostics independently label the packed three-field record.
    0x0004EDDC: "1cb56846faf7ecf9bdf80630bdf8041002a0009a00f098f801201cbd",
    # Sleep-stage module writes code, updated marker, and PPG-request bytes through one pointer.
    0x00060DDA: "4ff0000987f80190",
}


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def pointer_locations(image: bytes, base: int, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    return [base + offset for offset in range(len(image)) if image.startswith(needle, offset)]


def c_string(image: bytes, base: int, address: int) -> str:
    offset = mapped_offset(address, base, len(image))
    return image[offset:image.index(b"\0", offset)].decode("ascii")


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    expected_copy = bytes.fromhex(OUTPUT_COPY_HEX)
    actual_copy = flash_bytes(image, base, OUTPUT_COPY_FUNCTION, len(expected_copy))
    if actual_copy != expected_copy:
        raise ValueError("unexpected GoMore output-copy function bytes")
    if struct.unpack("<I", flash_bytes(image, base, 0x00059E5C, 4))[0] != ENGINE_POINTER_SLOT:
        raise ValueError("unexpected GoMore engine pointer-slot literal")

    for address, expected_hex in EXPECTED_BYTES.items():
        expected = bytes.fromhex(expected_hex)
        actual = flash_bytes(image, base, address, len(expected))
        if actual != expected:
            raise ValueError(
                f"unexpected output ABI bytes at 0x{address:08x}: "
                f"{actual.hex()} != {expected.hex()}"
            )

    branches: dict[str, list[str]] = {}
    for target, expected_callsites in EXPECTED_DIRECT_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected_callsites:
            raise ValueError(
                f"unexpected branches to 0x{target:08x}: {actual} != {expected_callsites}"
            )
        branches[f"0x{target:08x}"] = [f"0x{item:08x}" for item in actual]

    io_literals = pointer_locations(image, base, IO_STATE_ADDRESS)
    if io_literals != EXPECTED_IO_LITERAL_LOCATIONS:
        raise ValueError(f"unexpected I/O-state literal roots: {io_literals}")

    occupied_io: set[int] = set()
    occupied_engine: set[int] = set()
    for field in FIELDS:
        io_range = set(range(field["io_offset"], field["io_offset"] + field["width"]))
        engine_range = set(
            range(field["engine_offset"], field["engine_offset"] + field["width"])
        )
        if occupied_io & io_range or occupied_engine & engine_range:
            raise ValueError(f"overlapping output field: {field}")
        if max(io_range) >= IO_STATE_BYTES or max(engine_range) >= VENDOR_ENGINE_BYTES:
            raise ValueError(f"out-of-range output field: {field}")
        occupied_io |= io_range
        occupied_engine |= engine_range

    if len(FIELDS) != 27 or len(occupied_io) != 57:
        raise ValueError("unexpected output-field coverage")
    if 0xA8 in occupied_io:
        raise ValueError("dormant slot-two +0xa8 unexpectedly populated by output copier")

    formats = {
        "activity": c_string(image, base, 0x0004EDF8),
        "energy": c_string(image, base, 0x0005FE72),
        "metabolic": c_string(image, base, 0x0005FE98),
    }
    expected_formats = {
        "activity": "all_kcal:%d, steps:%d, kcal:%d\n",
        "energy": "+?[kcal]=%f [sKcal]=%f [aKcal]=%f\r\n",
        "metabolic": "[met]=%f [fat]=%f [carb]=%f\r\n",
    }
    if formats != expected_formats:
        raise ValueError(f"unexpected GoMore output diagnostic formats: {formats}")

    copied = []
    for field in FIELDS:
        copied.append({
            "engine_offset": f"0x{field['engine_offset']:03x}",
            "io_offset": f"0x{field['io_offset']:02x}",
            "width": field["width"],
            "storage": field["storage"],
            "semantic": field.get("semantic", "unresolved"),
            "host_disposition": (
                f"consumed_by_{field['host_consumer']}"
                if "host_consumer" in field
                else "copied_without_stock_host_reader"
            ),
        })

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "copy_function": f"0x{OUTPUT_COPY_FUNCTION:08x}",
        "engine_pointer_slot": f"0x{ENGINE_POINTER_SLOT:08x}",
        "io_state_address": f"0x{IO_STATE_ADDRESS:08x}",
        "io_state_bytes": IO_STATE_BYTES,
        "field_count": len(FIELDS),
        "copied_bytes": len(occupied_io),
        "stock_host_consumed_field_count": sum("host_consumer" in item for item in FIELDS),
        "copied_without_stock_host_reader_count": sum(
            "host_consumer" not in item for item in FIELDS
        ),
        "fields": copied,
        "dormant_slot_two": {
            "io_offset": "0xa8",
            "populated_by_output_copy": False,
            "consumer": "compiled no-op 0x00049e58",
        },
        "io_state_literal_roots": [f"0x{item:08x}" for item in io_literals],
        "direct_branches": branches,
        "diagnostic_formats": formats,
        "safety": {
            "live_sram_reader_exposed": False,
            "engine_or_worker_sender_exposed": False,
            "offline_snapshot_decoder_requires_exact_264_bytes": True,
            "unknown_fields_remain_raw": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image, args.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
