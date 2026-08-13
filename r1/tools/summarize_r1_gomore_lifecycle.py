#!/usr/bin/env python3
"""Validate the R1 GoMore initialization, update, output, and checkpoint lifecycle.

The parser is intentionally static. It checks fixed application bytes, direct Thumb branches,
scatter-initialized module descriptors, and the fixed SRAM layout. It never executes firmware,
reads a device, emits key material, or starts a health worker.
"""

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


IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
CONTROL_STATE = 0x20006DA0
MODULE_DESCRIPTOR_OFFSET = 0x24
MODULE_DESCRIPTOR_BYTES = 0x10
EXPECTED_DESCRIPTOR_PREFIXES = [0x02, 0x1E, 0x1E, 0x02, 0x04, 0x0C, 0x00]

EXPECTED_BYTES = {
    # Sensor startup initializes the GoMore layer with prior-state restore enabled.
    0x0004A21C: "10b502f0d1f9fff7d1f802f0c7f8002001f0b4fd",
    # Reinitialization disables slot four, removes the common timer, clears 0x2e0 bytes, and
    # tail-calls the initializer with argument one.
    0x0004C37C: "0b4810b590f84000c00703d000210420fdf740f8074844f075fe4ff438710648dbf705fabde810400120fff7f7bc",
    # Initializer prologue and the two vendor-init attempts (the second follows error -5).
    0x0004BD98: "2de9f04f99b082461cf0befc04461cf038fb054645f09efb",
    0x0004BF84: "49467d48dbf70ffc3ef00aff82460146794b01aab84823f081ff07003cd045f0a3fa",
    # Vendor engine allocation, 0x39e0-byte clear, and prior-state pointer install.
    0x0006FEA0: "2de9f0410f4690461d46494e3060301d0068b7f701fc43f6e0113068b7f775fc306800f54050",
    # Prior-state validation: a non-negative first word requires every one of 0x2e0 bytes to be
    # zero; otherwise error -5 is returned. A clean record receives the high-bit marker.
    0x0006FF0E: "306800f54050d0f8dc090068002820db002311e0e85c70b16ff004040121234630a2084612f051fa316801f5405181f8d8492046e2e75b1cf8f7ebfb9842e9d8",
    # User initialization and successful vendor startup tail.
    0x0006FF78: "3168c1f8907101f5a071404601f056ff0446002c0cda012123461ea2084612f01ffa306800f5405080f8d8492046b0e7306800f5a07001f040fd4ff0ff31",
    # One-second idle update and common successful-input cleanup.
    0x0006ACA4: "10b5074c00f016f8204629f069fb01f085fa002803d0bde8104000f003b810bd",
    # Timestamp/timezone/PPG-channel/wear-unknown input refresh.
    0x0006ACD8: "10b520f063f8084c206020f067f8a08001206077e1f764fc00b1012080f0010084f8300010bd",
    # Accelerometer/raw-optical readiness handshake and worker-driven update.
    0x0006B0D4: "70b5fff707fd0446fff740fd54ea000109d00a4d04426a7802f00101c2f3400202d0114204d170bd0c4201d11042fad001f0c6f8",
    # Worker callback prefixes: the accelerometer and raw-optical paths dereference before their
    # null checks in this production build.
    0x0006B114: "f0b491f8b430002941d0192b00d91923204a0020dfed200a",
    0x0006B1B8: "002915d0087800ee100a0a48b8ee400a80ed0a0a08484178",
    0x0006B1F4: "002911d0487a042801d904204872074a82f8240006480022",
    0x0006B228: "30b40a7800291ed0192a00d919220f4b00201a770de000bf",
    # Result normalization, first-three failure logging, and 60-failure reinitialization.
    0x0006C1C0: "f8b51c4c05004ff000062fd0e078032821d225f08bf9184fc00703d125f086f9400708d5386800902b4614a213a14ff0906025f021fa25f079f980070bd51a481a492a46401ac008012101eb004018a13b680df0e0fbe078401cc0b2e0703c2802d3e670e0f7aaf80020f8bd",
    # Worker-driven update and the active-slot output switch.
    0x0006C294: "2de9f04f97b06f4cfef71cfd204628f06ff8fff78bff00287ed06b486b4900250322401ac7086a4e",
    0x0006C2C8: "06eb05100078c00709d0042d07d2dfe805f002b1070c04f17800dcf7c1fda9e0",
    # Slot-three sleep flags and slot-four PPG transition.
    0x0006C3B4: "96f8401094f9620001f0010188423bd0012819d02ee025f08ff8c00703d125f08bf8400705d53ca23ba14ff0806025f029f925f081f8800726d5012000eb07403ea10df0e3fa1fe025f076f8c00703d125f072f8400705d53fa23fa14ff0406025f010f925f068f8800703d5404641a10df0ccfa96f84000c00701d0002100e001210420dcf7eaff",
    # Vendor update and monotonic-time normalization.
    0x00094384: "2de9f04387b004465548407c012854d1b4f90400009053a2002102202368eef7",
    0x00068570: "00280ed00849096801f54051d1f8dc194968ca1c824203d3c21c914200d8481c704701207047",
    # The compiled license-window helper is a constant false stub in this image.
    0x00072ACE: "00207047",
    # Graceful thread exit requests the live 0x2e0-byte state and appends it to pKey.bin.
    0x00046C36: "012000eb07402b46324620a132f0c8fe2cf01ffd24f08bf817f049fa4af04bfc",
    0x0006AD64: "08b50020adf800006846fff739ff002803d0bdf8001000f019ff08bd",
    0x0006ABE4: "002803d04ff43871018001487047000054e00120",
    # Auth setup includes conditional plaintext `%s` diagnostics for the recovered key buffer.
    0x0006B2E8: "40216846fff71cfd4849474a0600a2eb01014ff001004fead1014ff0",
}

EXPECTED_DIRECT_BRANCHES = {
    0x0004BD98: [0x0004A22C, 0x0004C3A6],
    0x0004C37C: [0x0005DC58, 0x0006C224, 0x0006C5C0],
    0x0006FEA0: [0x0004BF9A, 0x0004BFE6],
    0x00094384: [0x0006ACAE, 0x0006C2A2],
    0x0006C1C0: [0x0006ACB2, 0x0006C2A6],
    0x0006C294: [0x0006B104],
    0x0006AD64: [0x00046C4A],
    0x0006BBB0: [0x0006AD7A],
}


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def literal_u32(image: bytes, base: int, address: int) -> int:
    return struct.unpack("<I", flash_bytes(image, base, address, 4))[0]


def literal_pointer_locations(image: bytes, base: int, value: int) -> list[int]:
    needles = (struct.pack("<I", value), struct.pack("<I", value | 1))
    return sorted(
        base + offset
        for needle in needles
        for offset in range(len(image))
        if image.startswith(needle, offset)
    )


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    for address, expected_hex in EXPECTED_BYTES.items():
        expected = bytes.fromhex(expected_hex)
        actual = flash_bytes(image, base, address, len(expected))
        if actual != expected:
            raise ValueError(
                f"unexpected lifecycle bytes at 0x{address:08x}: "
                f"{actual.hex()} != {expected.hex()}"
            )

    branch_summary: dict[str, list[str]] = {}
    for target, expected_callsites in EXPECTED_DIRECT_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected_callsites:
            raise ValueError(
                f"unexpected calls to 0x{target:08x}: {actual} != {expected_callsites}"
            )
        branch_summary[f"0x{target:08x}"] = [f"0x{item:08x}" for item in actual]

    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)
    descriptor_start = CONTROL_STATE + MODULE_DESCRIPTOR_OFFSET - scatter_runtime
    descriptor_prefixes = [
        runtime[descriptor_start + index * MODULE_DESCRIPTOR_BYTES]
        for index in range(7)
    ]
    if descriptor_prefixes != EXPECTED_DESCRIPTOR_PREFIXES:
        raise ValueError(
            f"unexpected GoMore descriptor prefixes: {descriptor_prefixes}"
        )

    literals = {
        "io_state_from_initializer": literal_u32(image, base, 0x0004C308),
        "sensor_array_from_initializer": literal_u32(image, base, 0x0004C30C),
        "vendor_engine_from_initializer": literal_u32(image, base, 0x0004C27C),
        "previous_state_from_initializer": literal_u32(image, base, 0x0004C17C),
        "control_state_from_initializer": literal_u32(image, base, 0x0004C0EC),
        "io_state_from_update": literal_u32(image, base, 0x0006C458),
        "descriptor_base_from_update": literal_u32(image, base, 0x0006C464),
        "previous_state_from_export": literal_u32(image, base, 0x0006ABF4),
    }
    expected_literals = {
        "io_state_from_initializer": 0x2001A56C,
        "sensor_array_from_initializer": 0x2001A3DC,
        "vendor_engine_from_initializer": 0x2001A674,
        "previous_state_from_initializer": 0x2001E054,
        "control_state_from_initializer": 0x20006DA0,
        "io_state_from_update": 0x2001A56C,
        "descriptor_base_from_update": 0x20006DC4,
        "previous_state_from_export": 0x2001E054,
    }
    if literals != expected_literals:
        raise ValueError(f"unexpected GoMore SRAM literals: {literals}")

    key_log_formats = {
        "ring": flash_bytes(image, base, 0x0006B46C, 18).split(b"\0", 1)[0].decode("ascii"),
        "secondary": flash_bytes(image, base, 0x0006B480, 13).split(b"\0", 1)[0].decode("ascii"),
    }
    if "%s" not in key_log_formats["ring"] or "%s" not in key_log_formats["secondary"]:
        raise ValueError(f"unexpected key diagnostic formats: {key_log_formats}")

    idle_callback_pointer = struct.pack("<I", 0x0006ACA5)
    idle_pointer_locations = [
        base + offset
        for offset in range(len(image))
        if image.startswith(idle_callback_pointer, offset)
    ]
    if idle_pointer_locations != [0x00049680]:
        raise ValueError(f"unexpected idle callback pointers: {idle_pointer_locations}")

    checkpoint_pointer_locations = {
        "wrapper": literal_pointer_locations(image, base, 0x0006AD64),
        "append": literal_pointer_locations(image, base, 0x0006BBB0),
    }
    if checkpoint_pointer_locations != {"wrapper": [], "append": []}:
        raise ValueError(
            f"unexpected checkpoint function pointers: {checkpoint_pointer_locations}"
        )

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "scatter": {
            "source": f"0x{scatter_source:08x}",
            "compressed_end": f"0x{scatter_source + consumed:08x}",
            "runtime": f"0x{scatter_runtime:08x}",
            "runtime_bytes": len(runtime),
        },
        "initialization": {
            "host_initializer": "0x0004bd98",
            "vendor_initializer": "0x0006fea0",
            "reinitializer": "0x0004c37c",
            "auth_setup": "0x0006b27c",
            "auth_retry_count_after_first_failure": 1,
            "restore_bytes": 736,
            "vendor_engine_bytes": 14816,
            "invalid_prior_state_error": -5,
            "invalid_prior_state_retried_zeroed": True,
            "reinitialize_discards_prior_state": True,
            "reinitialize_callers": ["backward time", "profile significance", "60 update failures"],
        },
        "sram_layout": {
            "sensor_float_arrays": {"address": "0x2001a3dc", "bytes": 400},
            "io_state": {"address": "0x2001a56c", "bytes": 264},
            "vendor_engine": {"address": "0x2001a674", "bytes": 14816},
            "previous_state": {"address": "0x2001e054", "bytes": 736},
            "control_state": {"address": "0x20006da0"},
        },
        "worker_inputs": {
            "accelerometer": {
                "callback": "0x0006b114",
                "maximum_samples": 25,
                "source_stride_bytes": 6,
                "axis_scale": 0.9765625,
                "algorithm_axis_mapping": ["-source[1]", "source[0]", "source[2]"],
                "ready_bit": "0x01",
                "null_checked_after_first_dereference": True,
            },
            "raw_optical": {
                "callback": "0x0006b228",
                "maximum_samples": 25,
                "ready_bit": "0x02",
                "null_checked_after_first_dereference": True,
            },
            "heart_rate": {
                "callback": "0x0006b1b8",
                "source": "UInt8",
                "algorithm_value": "Float32",
                "ready_bit": "0x04",
                "participates_in_update_barrier": False,
            },
            "hrv_auxiliary": {
                "callback": "0x0006b1f4",
                "maximum_u16_values": 4,
                "buffer": "0x20006dbc...0x20006dc3",
                "io_pointer_offset": "0x20",
                "io_count_offset": "0x24",
                "participates_in_update_barrier": False,
                "consumed_by_vendor_update": False,
            },
            "barrier_requires_only": ["accelerometer", "raw_optical"],
        },
        "update": {
            "vendor_update": "0x00094384",
            "idle_trigger": "0x0006aca4",
            "worker_trigger": "0x0006c294",
            "worker_barrier": "0x0006b0d4",
            "input_refresh": "0x0006acd8",
            "result_handler": "0x0006c1c0",
            "idle_period_milliseconds": 1000,
            "timestamp_nearby_tolerance_seconds": 3,
            "nearby_timestamp_substitution": "previous + 1",
            "zero_timestamp_substitution": 1,
            "failure_logs": 3,
            "failure_reinitialize_threshold": 60,
            "successful_update_clears_acc_and_ppg_lengths": True,
            "failed_update_preserves_acc_and_ppg_lengths": True,
            "compiled_license_window_helper_returns_false": True,
        },
        "output_dispatch": {
            "idle_trigger_dispatches_outputs": False,
            "worker_trigger_dispatches_outputs": True,
            "active_slot_routes": {
                "0": "activity accumulator at I/O +0x78",
                "1": "no per-slot output branch",
                "2": "compiled no-op receives Float32 at I/O +0xa8",
                "3": "sleep period/final result flags at +0x70 and sleep-stage PPG at +0x62",
                "4": "no per-slot output branch",
                "5": "no per-slot output branch",
                "6": "no per-slot output branch",
            },
            "sleep_period_on_mask": "0x02",
            "sleep_period_off_mask": "0x04",
            "sleep_final_result_mask": "0x08",
            "sleep_result_buffer_bytes": 2880,
        },
        "checkpoint": {
            "live_state_export": "0x0006abe4",
            "checkpoint_wrapper": "0x0006ad64",
            "flash_append": "0x0006bbb0",
            "direct_production_callsite": "0x00046c4a",
            "context": "coordinated thread exit",
            "continuous_checkpoint_found": False,
            "checkpoint_bytes": 736,
            "literal_function_pointer_locations": checkpoint_pointer_locations,
        },
        "static_branches": branch_summary,
        "security": {
            "official_firmware_contains_plaintext_key_format_diagnostics": True,
            "key_diagnostic_format_strings": key_log_formats,
            "key_material_emitted_by_parser": False,
            "sybilsight_must_never_log_key_material": True,
            "live_engine_or_worker_sender_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    parser.add_argument(
        "--scatter-source", type=lambda value: int(value, 0), default=DEFAULT_SCATTER_SOURCE
    )
    parser.add_argument(
        "--scatter-runtime", type=lambda value: int(value, 0), default=DEFAULT_SCATTER_RUNTIME
    )
    parser.add_argument(
        "--scatter-length", type=lambda value: int(value, 0), default=DEFAULT_SCATTER_LENGTH
    )
    args = parser.parse_args()
    print(json.dumps(summarize(
        args.image,
        args.base,
        args.scatter_source,
        args.scatter_runtime,
        args.scatter_length,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
