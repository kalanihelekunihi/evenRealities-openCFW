#!/usr/bin/env python3
"""Validate the complete R1 host-to-GoMore input ABI and dormant HRV lane.

The parser is static and version-pinned. It validates I/O initialization, every callback/update
signature, fixed buffer pointers, all literal roots, input consumption, and reset behavior. It
never reads live SRAM, starts a worker, or injects physiological data.
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
SENSOR_FLOAT_ARRAY_ADDRESS = 0x2001A3DC
CONTROL_STATE_ADDRESS = 0x20006DA0
HRV_BUFFER_ADDRESS = CONTROL_STATE_ADDRESS + 0x1C

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

EXPECTED_BYTES = {
    # Successful initialization clears the full I/O block and installs four 100-byte Float32
    # buffers plus a pointer to the separate eight-byte HRV control buffer.
    0x0004C01C: (
        "85f800804ff48471b848dbf7c0fbb748b74981606431c1606431016164318161"
        "2b491c310162"
    ),
    # Success cleanup clears only raw-optical and accelerometer sample counts.
    0x0006ACC8: "02480021017701757047",
    # Per-attempt timestamp/timezone/channel/wear-unknown refresh.
    0x0006ACD8: "10b520f063f8084c206020f067f8a08001206077e1f764fc00b1012080f0010084f8300010bd",
    # Direct-HR callback, including persistent Float32 write and readiness bit.
    0x0006B1B8: "002915d0087800ee100a0a48b8ee400a80ed0a0a0848417841f004014170",
    # HRV callback: clamp count to four, store count at I/O +0x24, clear/copy the separate
    # control-state buffer at +0x1c. It has no readiness bit or update call.
    0x0006B1F4: "002911d0487a042801d904204872074a82f8240006480022c2610262487a420003481c30bcf7a0ba7047",
    # Raw-optical callback prefix and count clamp.
    0x0006B228: "30b40a7800291ed0192a00d919220f4b00201a770de000bf",
}

# Full input-adapter body through POP. Pinning the complete function makes the absence of reads at
# I/O +0x20/+0x24 and the conditional zero-only +0x31/+0x32 lane reproducible.
UPDATE_ADAPTER_HEX = (
    "f0b5ebb004460e463e4f3868c0f89061a188a0f88c11a169519152a9c0f87011"
    "00f5b8710091237f627f51a9ccf72afa94f8300018b13968012081f874013d68"
    "94f8300085f87501a0695090207fa5f87c01607f012800d9012085f87e01607f"
    "d8b3207fc8b3002085f87f01002050a905eb800351f82020c3f87821401c0128"
    "f6dba0680290e068039020690490002005a900ebc00202eb001205eb800301eb8"
    "202c3f8c821401c0328f2db227d05f5e47302a92846ccf7a3f9386894ed0a0a"
    "80ed5b0a94ed0b0a80ed540a00f54051d1f8d429022a03d009e0ffe70120c3e7"
    "14f8312f80f8f522627880f8f622d1f8dc1900f5a0704968711acbf783fc6bb0"
    "0020f0bd"
)

EXPECTED_DIRECT_BRANCHES = {
    0x0006ACD8: [0x0006ACA8, 0x0006C29C],
    0x0006ACC8: [0x0006ACBE, 0x0006C44C],
    0x00094590: [0x000944AE],
    0x00060A14: [0x000945BC],
    0x00060990: [0x00094646],
}

FIELDS: list[dict[str, Any]] = [
    {"io_offset": 0x00, "width": 4, "storage": "uint32", "semantic": "unix_seconds", "writer": "per_attempt_refresh", "consumption": "every_update"},
    {"io_offset": 0x04, "width": 2, "storage": "int16", "semantic": "timezone_offset_minutes", "writer": "per_attempt_refresh", "consumption": "every_update"},
    {"io_offset": 0x08, "width": 4, "storage": "static_pointer", "semantic": "accelerometer_axis_0_buffer", "writer": "successful_initialization", "consumption": "every_update"},
    {"io_offset": 0x0C, "width": 4, "storage": "static_pointer", "semantic": "accelerometer_axis_1_buffer", "writer": "successful_initialization", "consumption": "every_update"},
    {"io_offset": 0x10, "width": 4, "storage": "static_pointer", "semantic": "accelerometer_axis_2_buffer", "writer": "successful_initialization", "consumption": "every_update"},
    {"io_offset": 0x14, "width": 1, "storage": "uint8", "semantic": "accelerometer_sample_count", "writer": "accelerometer_callback", "consumption": "every_update"},
    {"io_offset": 0x18, "width": 4, "storage": "static_pointer", "semantic": "raw_optical_buffer", "writer": "successful_initialization", "consumption": "every_update"},
    {"io_offset": 0x1C, "width": 1, "storage": "uint8", "semantic": "raw_optical_sample_count", "writer": "raw_optical_callback", "consumption": "every_update"},
    {"io_offset": 0x1D, "width": 1, "storage": "uint8", "semantic": "raw_optical_channel_count", "writer": "per_attempt_refresh", "consumption": "every_update"},
    {"io_offset": 0x20, "width": 4, "storage": "static_pointer", "semantic": "hrv_auxiliary_buffer", "writer": "successful_initialization", "consumption": "configured_but_not_read"},
    {"io_offset": 0x24, "width": 1, "storage": "uint8", "semantic": "hrv_auxiliary_value_count", "writer": "hrv_callback", "consumption": "configured_but_not_read"},
    {"io_offset": 0x28, "width": 4, "storage": "float32", "semantic": "direct_heart_rate", "writer": "heart_rate_callback", "consumption": "every_update"},
    {"io_offset": 0x2C, "width": 4, "storage": "opaque32", "semantic": "legacy_zero_word", "writer": "initial_zero_only", "consumption": "every_update"},
    {"io_offset": 0x30, "width": 1, "storage": "bool", "semantic": "wear_state_is_unknown", "writer": "per_attempt_refresh", "consumption": "every_update"},
    {"io_offset": 0x31, "width": 1, "storage": "uint8", "semantic": "mode_2_legacy_byte_0", "writer": "initial_zero_only", "consumption": "engine_mode_2_only"},
    {"io_offset": 0x32, "width": 1, "storage": "uint8", "semantic": "mode_2_legacy_byte_1", "writer": "initial_zero_only", "consumption": "engine_mode_2_only"},
]


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def literal_u32(image: bytes, base: int, address: int) -> int:
    return struct.unpack("<I", flash_bytes(image, base, address, 4))[0]


def pointer_locations(image: bytes, base: int, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    return [base + offset for offset in range(len(image)) if image.startswith(needle, offset)]


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    for address, expected_hex in EXPECTED_BYTES.items():
        expected = bytes.fromhex(expected_hex)
        actual = flash_bytes(image, base, address, len(expected))
        if actual != expected:
            raise ValueError(
                f"unexpected input ABI bytes at 0x{address:08x}: "
                f"{actual.hex()} != {expected.hex()}"
            )

    expected_adapter = bytes.fromhex(UPDATE_ADAPTER_HEX)
    actual_adapter = flash_bytes(image, base, 0x00094590, len(expected_adapter))
    if actual_adapter != expected_adapter:
        raise ValueError("unexpected complete GoMore input-adapter body")

    branches: dict[str, list[str]] = {}
    for target, expected_callsites in EXPECTED_DIRECT_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected_callsites:
            raise ValueError(
                f"unexpected branches to 0x{target:08x}: {actual} != {expected_callsites}"
            )
        branches[f"0x{target:08x}"] = [f"0x{item:08x}" for item in actual]

    literals = {
        "control_state": literal_u32(image, base, 0x0004C0EC),
        "io_state": literal_u32(image, base, 0x0004C308),
        "sensor_float_array": literal_u32(image, base, 0x0004C30C),
        "hrv_callback_io": literal_u32(image, base, 0x0006B220),
        "hrv_callback_control": literal_u32(image, base, 0x0006B224),
    }
    expected_literals = {
        "control_state": CONTROL_STATE_ADDRESS,
        "io_state": IO_STATE_ADDRESS,
        "sensor_float_array": SENSOR_FLOAT_ARRAY_ADDRESS,
        "hrv_callback_io": IO_STATE_ADDRESS,
        "hrv_callback_control": CONTROL_STATE_ADDRESS,
    }
    if literals != expected_literals:
        raise ValueError(f"unexpected GoMore input ABI literals: {literals}")

    io_literals = pointer_locations(image, base, IO_STATE_ADDRESS)
    if io_literals != EXPECTED_IO_LITERAL_LOCATIONS:
        raise ValueError(f"unexpected I/O-state literal roots: {io_literals}")

    static_pointers = {
        "accelerometer_axis_0": SENSOR_FLOAT_ARRAY_ADDRESS,
        "accelerometer_axis_1": SENSOR_FLOAT_ARRAY_ADDRESS + 100,
        "accelerometer_axis_2": SENSOR_FLOAT_ARRAY_ADDRESS + 200,
        "raw_optical": SENSOR_FLOAT_ARRAY_ADDRESS + 300,
        "hrv_auxiliary": HRV_BUFFER_ADDRESS,
    }
    consumed_offsets = [
        field["io_offset"] for field in FIELDS
        if field["consumption"] != "configured_but_not_read"
    ]
    dormant_offsets = [
        field["io_offset"] for field in FIELDS
        if field["consumption"] == "configured_but_not_read"
    ]
    if consumed_offsets != [0, 4, 8, 12, 16, 20, 24, 28, 29, 40, 44, 48, 49, 50]:
        raise ValueError(f"unexpected consumed input offsets: {consumed_offsets}")
    if dormant_offsets != [0x20, 0x24]:
        raise ValueError(f"unexpected dormant input offsets: {dormant_offsets}")

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "io_state_address": f"0x{IO_STATE_ADDRESS:08x}",
        "io_state_bytes": IO_STATE_BYTES,
        "input_adapter": "0x00094590",
        "defined_input_field_count": len(FIELDS),
        "consumed_input_field_count": len(consumed_offsets),
        "configured_but_not_read_field_count": len(dormant_offsets),
        "fields": [
            {
                **field,
                "io_offset": f"0x{field['io_offset']:02x}",
            }
            for field in FIELDS
        ],
        "static_pointers": {
            name: f"0x{address:08x}" for name, address in static_pointers.items()
        },
        "buffers": {
            "accelerometer_axis_float32_count_each": 25,
            "raw_optical_float32_count": 25,
            "hrv_auxiliary_uint16_count": 4,
        },
        "lifecycle": {
            "full_io_zero_after_successful_vendor_init": True,
            "refreshes_each_attempt": ["unix_seconds", "timezone_offset_minutes", "raw_optical_channel_count", "wear_state_is_unknown"],
            "success_clears": ["accelerometer_sample_count", "raw_optical_sample_count"],
            "failure_preserves_sample_counts": True,
            "heart_rate_persists_until_callback_or_worker_disable": True,
            "hrv_auxiliary_persists_until_callback_or_worker_disable": True,
            "hrv_auxiliary_consumed_by_vendor_update": False,
            "mode_2_legacy_bytes_have_host_writer": False,
            "legacy_word_has_host_writer_after_initial_zero": False,
        },
        "io_state_literal_roots": [f"0x{item:08x}" for item in io_literals],
        "direct_branches": branches,
        "safety": {
            "live_sram_reader_exposed": False,
            "worker_or_input_injection_sender_exposed": False,
            "offline_snapshot_requires_health_consent": True,
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
