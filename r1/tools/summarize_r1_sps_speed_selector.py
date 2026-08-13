#!/usr/bin/env python3
"""Validate the R1 SPS speed-selector inputs, formulas, and stock constant-output defect.

The parser is static and version-pinned. It connects the zero-only host reference input, dormant
GPD input, accelerometer-derived speed candidate, priority selector, reciprocal pace field, and
copied output ABI. It never changes SRAM, executes the engine, or injects a reference speed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import FIELDS as INPUT_FIELDS
from summarize_r1_gomore_output_abi import FIELDS as OUTPUT_FIELDS, IMAGE_SHA256


EXPECTED_RANGE_SHA256 = {
    (0x00071714, 0x000717A2): "3112c51e53dd2e756960eb870445b953280183300cc7b70a3c5ae25fc74940af",
    (0x00094590, 0x00094694): "e0ec2adb814118836f143c52750a75bc91ffc913845942ddab6de0f7f9a82fb8",
    (0x0005EF1C, 0x0005F22C): "f04b2e7aeb8a80e847c8a18316b8f0b7c5e28acb94455cfc9983582d306487a9",
    (0x000610C8, 0x00061170): "4e29f64ce14853e7a90295e12ca5eea4f1b2fafec01ba5a824eb4b84837b81e2",
    (0x000684FC, 0x00068570): "4183e73b694bf41dda5eb0a12ab3ae9473603104e2e9cfd50881cf12b4255cf0",
    (0x00068DE0, 0x00068E54): "59c52793808e986bcd079e95b0df2c86c0cb3998a6912679fd446f53f9c01a6a",
    (0x00068E5C, 0x00068F5C): "6a731da94a6c94cd51d6d7fe28f538410030e6cbc4abccf220623abc69cc9a15",
    (0x00069E94, 0x00069F28): "2753ea6f9855f37608922af73196da42987b871ad3b4fb5b5e0c233c0d2068a7",
    (0x00069F3C, 0x00069F7C): "e7b6fdf85a1ad6e9f66390f39c05b95a38390526f2975f8aff34ed5446712773",
    (0x00071100, 0x00071150): "beb5a883f3f657e984ce29eb56f0fb7f6e94327c1a351b4d22cfd5bbc7cb0e3d",
    (0x00070F44, 0x00070FDA): "3a92d3fa6a98418c1b34d3117864f963de2bfc9a44bed873340a2d3c64aa5e42",
    (0x000883B0, 0x000883D0): "f72854e9bbd1981900a8aaca9750dd8d4e08e2a3078cdfa1926ca57d393262a9",
    (0x0006773C, 0x0006774E): "dd54f264fac45771aa24ed549ea0d7c4a09070e33b09691391b511251ce35b41",
    (0x000484A8, 0x000484CA): "e79867d4a293644691d22121caf3ce1d7489663325d342c35bfa00454ec040cf",
    (0x000B19F4, 0x000B1A6C): "5fd57c8e8122822ab2a0c9a2edaba6f6445d51b79ed15e46eb2e7bddb7d73e6c",
    (0x00071DB6, 0x00071DC8): "e3c32568d179427a8d764fa0f4035143ef5efdec75321bf37638d2076e427e47",
    (0x0006FF66, 0x0006FF78): "101ca5c5d30c423f81e0f8ff0b0d0f4518bb891d3b465537fea255c832ee194a",
}

EXPECTED_DIRECT_BRANCHES = {
    0x00071714: [0x00071DD2],
    0x00094590: [0x000944AE],
    0x0005EF1C: [0x000600DC, 0x000600F2],
    0x000610C8: [0x0006013A, 0x0006014C],
    0x000684FC: [0x0005F0B0, 0x0005F180],
    0x00068DE0: [0x00068530],
    0x00068E5C: [0x0006853A],
    0x00069E94: [0x00068514],
    0x00069F3C: [0x0006851E],
    0x00071100: [0x00071A66],
    0x00070F44: [0x00071148],
    0x000883B0: [0x00071142],
    0x0006773C: [0x0006854A],
    0x000484A8: [0x0005EF8E, 0x0005EF9E, 0x0006855C],
    0x00071DB6: [0x0006FF74],
}

EXPECTED_FLOAT32 = {
    0x0005F22C: 0.0,
    0x0005F230: 0.2,
    0x0005F244: 6.0,
    0x0005F248: 14.0,
    0x0005F24C: 20.0,
    0x0005F260: 7.0,
    0x00061190: 0.0,
    0x00061194: 3600.0,
    0x00071150: 0.0,
}

EXPECTED_FLOAT64 = {
    0x0005F234: 0.25,
    0x0005F23C: 0.75,
    0x0005F250: 0.15,
    0x0005F258: 0.85,
}

REFERENCE_ADAPTER_BYTES = bytes.fromhex("94ed0b0a80ed540a")

EXPECTED_MODEL_TABLE_BITS = (
    0x3BBE6E0E, 0xBE952A90, 0xC6002839, 0x39C6CDCD, 0x39997D65, 0x42C375D0,
    0x3D666AB6, 0xBC5BA131, 0x3BB3BEDF, 0xBF7535B8, 0x432DAD60, 0x432F2E7B,
    0x44DF07BD, 0x40B908FD, 0x41471339, 0x43982465, 0x3F5ABE4F, 0x3F8EE557,
    0x3FC4413D, 0x4131EECE, 0x432DAD60, 0x432F2E7B, 0x44DF07BD, 0x40B908FD,
    0x41471339, 0x43982465, 0x3F5ABE4F, 0x3F8EE557, 0x3FC4413D, 0x4131EECE,
)


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + (end - start)]


def unpack(image: bytes, base: int, address: int, kind: str) -> float:
    width = 4 if kind == "f" else 8
    return struct.unpack("<" + kind, flash_bytes(image, base, address, address + width))[0]


def c_string(image: bytes, base: int, address: int) -> str:
    offset = mapped_offset(address, base, len(image))
    return image[offset:image.index(b"\0", offset)].decode("ascii")


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    verified_ranges = []
    for (start, end), expected_digest in EXPECTED_RANGE_SHA256.items():
        actual_digest = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual_digest != expected_digest:
            raise ValueError(
                f"unexpected SPS range 0x{start:08x}...0x{end:08x}: {actual_digest}"
            )
        verified_ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual_digest,
        })

    branches: dict[str, list[str]] = {}
    for target, expected_callsites in EXPECTED_DIRECT_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected_callsites:
            raise ValueError(
                f"unexpected branches to 0x{target:08x}: {actual} != {expected_callsites}"
            )
        branches[f"0x{target:08x}"] = [f"0x{item:08x}" for item in actual]

    if flash_bytes(image, base, 0x00094654, 0x0009465C) != REFERENCE_ADAPTER_BYTES:
        raise ValueError("unexpected host-reference to engine-reference adapter bytes")

    model_table_bits = struct.unpack(
        "<30I", flash_bytes(image, base, 0x000B19F4, 0x000B1A6C)
    )
    if model_table_bits != EXPECTED_MODEL_TABLE_BITS:
        raise ValueError(f"unexpected SPS model table: {model_table_bits}")

    constants: dict[str, float] = {}
    for address, expected in EXPECTED_FLOAT32.items():
        actual = unpack(image, base, address, "f")
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-6):
            raise ValueError(f"unexpected Float32 at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual
    for address, expected in EXPECTED_FLOAT64.items():
        actual = unpack(image, base, address, "d")
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"unexpected Float64 at 0x{address:08x}: {actual}")
        constants[f"0x{address:08x}"] = actual

    diagnostic = c_string(image, base, 0x00061170)
    if diagnostic != "[SPS] sRef:%f sGpd:%f sAcc:%f":
        raise ValueError(f"unexpected SPS diagnostic: {diagnostic!r}")

    reference_inputs = [field for field in INPUT_FIELDS if field["io_offset"] == 0x2C]
    if reference_inputs != [{
        "io_offset": 0x2C,
        "width": 4,
        "storage": "opaque32",
        "semantic": "legacy_zero_word",
        "writer": "initial_zero_only",
        "consumption": "every_update",
    }]:
        raise ValueError(f"unexpected host reference input definition: {reference_inputs}")

    selected_outputs = [
        field for field in OUTPUT_FIELDS
        if (field["engine_offset"], field["io_offset"]) in {(0x224, 0x58), (0x22C, 0x5C)}
    ]
    if [(field["engine_offset"], field["io_offset"], field["width"])
            for field in selected_outputs] != [(0x224, 0x58, 4), (0x22C, 0x5C, 1)]:
        raise ValueError(f"unexpected SPS copied outputs: {selected_outputs}")
    if any(field["engine_offset"] == 0x228 for field in OUTPUT_FIELDS):
        raise ValueError("internal reciprocal pace unexpectedly entered the copied ABI")

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "diagnostic": diagnostic,
        "selector": {
            "function": "0x000610c8",
            "priority": ["sRef", "sGpd", "sAcc"],
            "validity": "first value greater than or equal to zero",
            "all_invalid_selected_value": -1.0,
            "source_codes": {"sRef": 0, "sGpd": 1, "sAcc": 2, "none": 3},
            "selected_engine_offset": "0x224",
            "selected_io_offset": "0x58",
            "source_engine_offset": "0x22c",
            "source_io_offset": "0x5c",
            "reciprocal_pace_engine_offset": "0x228",
            "reciprocal_pace_formula": "speed > 0 ? 3600 / speed : 0",
            "reciprocal_pace_is_copied": False,
            "distance_unit_is_proven": False,
        },
        "inputs": {
            "sRef": {
                "engine_offset": "0x150",
                "host_io_offset": "0x2c",
                "initializer": -1.0,
                "stock_per_update_value": 0.0,
                "host_writer_after_initial_zero_found": False,
            },
            "sGpd": {
                "engine_offset": "0x1ac",
                "initializer": -1.0,
                "production_writer_found": False,
            },
            "sAcc": {
                "engine_offset": "0x21c",
                "producer": "0x0005ef1c",
                "model_dispatch": "0x000684fc",
                "state_1_candidate_range": {"minimum": 2.0, "maximum": 7.0},
                "state_1_alternate_minimum": 4.0,
                "state_2_candidate_range": {"minimum": 6.0, "maximum": 20.0},
                "state_2_alternate_maximum": 14.0,
                "speed_domain_is_formula_supported": True,
                "kilometers_per_hour_is_inferred_not_proven": True,
            },
        },
        "accelerometer_candidate": {
            "initializer": "0x00071100",
            "state_bytes": 88,
            "state_layout": {
                "smoothed_state_2_float": 0,
                "smoothed_state_1_float": 4,
                "state_2_model": {"offset": 8, "bytes": 28, "model_type": 0},
                "state_1_model": {"offset": 36, "bytes": 28, "model_type": 1},
                "config_pointer": 64,
                "latest_secondary_float": 68,
                "latest_primary_float": 72,
                "missing_update_count_uint32": 76,
                "startup_cooldown_uint16": 80,
                "reserved_uint32": 84,
            },
            "model_substate_layout": {
                "model_type_uint32": 0,
                "accumulated_secondary_float": 4,
                "accumulated_primary_float": 8,
                "accepted_count_uint16": 12,
                "calibration_slope_float": 16,
                "calibration_intercept_float": 20,
                "calibration_enabled_uint32": 24,
            },
            "restored_calibration": {
                "source": "736-byte GoMore previous-state checkpoint",
                "source_byte_offset": 8,
                "bytes": 16,
                "word_order": [
                    "state_2_slope", "state_2_intercept",
                    "state_1_slope", "state_1_intercept",
                ],
                "zero_word_behavior": "retain initializer default for that word",
                "default_slope": 1.0,
                "default_intercept": 0.0,
                "zeroed_state_enables_calibration": False,
                "pointer_binding_function": "0x00071db6",
                "pointer_binding_callsite": "0x0006ff74",
            },
            "gate": {
                "requires_smoothed_state_equal_raw_state": True,
                "relative_rate_cadence_difference_maximum_exclusive": 0.2,
                "rejected_raw_state": 255,
                "cadence_zero_and_rate_zero_difference": 0.0,
                "cadence_zero_and_nonzero_rate_difference": 1.0,
                "rejected_candidate": -1.0,
                "rejected_status": 1,
            },
            "model_status": {"default": 2, "restored_calibration": 3},
            "state_1": {
                "inputs": [
                    "feature_4_rate", "height_centimeters",
                    "feature_0_mean_magnitude_sd", "feature_3_mean_z",
                ],
                "primary_model": "0x00069e94",
                "secondary_model": "0x00069f3c",
                "new_weight": 0.15,
                "prior_weight": 0.85,
                "default_clamp": [4.0, 7.0],
                "calibrated_clamp": [2.0, 7.0],
            },
            "state_2": {
                "inputs": ["height_centimeters", "feature_5_rate", "feature_2_mean_magnitude"],
                "primary_model": "0x00068de0",
                "secondary_model": "0x00068e5c",
                "secondary_third_transform": "sign(normalized) * sqrt(abs(normalized))",
                "new_weight": 0.25,
                "prior_weight": 0.75,
                "default_clamp": [6.0, 14.0],
                "calibrated_clamp": [6.0, 20.0],
            },
            "gap_bookkeeping": {
                "startup_cooldown_updates": 8,
                "elapsed_missing_count_increment": "elapsed - 1",
                "replays_latest_positive_models_when_elapsed_below": 8,
                "insufficient_smoothed_state_code": 254,
            },
            "model_table_address": "0x000b19f4",
            "model_table_float32_bits": [f"0x{value:08x}" for value in model_table_bits],
            "phone_reimplementation_available": True,
        },
        "stock_effective_output": {
            "selected_value": 0.0,
            "source_code": 0,
            "source": "sRef",
            "sAcc_can_win_selection": False,
            "reason": "zero-only sRef is nonnegative and has first priority",
        },
        "constants": constants,
        "verified_ranges": verified_ranges,
        "direct_branches": branches,
        "safety": {
            "static_read_only": True,
            "live_reference_injection_exposed": False,
            "live_sram_reader_exposed": False,
            "vendor_engine_execution_exposed": False,
            "raw_values_preserved": True,
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
