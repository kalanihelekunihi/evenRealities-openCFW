#!/usr/bin/env python3
"""Validate the R1 energy, substrate, MET, daily-total, and hidden-distance pipeline.

This parser is static, read-only, and pinned to application 2.2.6.0009. It does not execute the
vendor engine or expose an SRAM reader. It connects the persisted user profile to the production
resting-energy equations, the copied per-update calorie components, the uncopied MET/substrate
fields, the daily activity accumulator, and the unreachable stock distance candidate.
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
from summarize_r1_gomore_output_abi import FIELDS as OUTPUT_FIELDS, IMAGE_SHA256


EXPECTED_RANGE_SHA256 = {
    (0x0005F56C, 0x0005FE20): "15451810170416aadb1d8afd6d2b327d93dc7a256ae296183f1d4cf9c01af763",
    (0x00061274, 0x00061384): "91f94945bf44a2be6f1835c8c33f1e1fb96117d53f4d069ce77668c7801020df",
    (0x00068728, 0x000687FE): "4768907ae751a8d5f35c6946eb33c090962cf8829ea362b5153d62929a7bb679",
    (0x0007316C, 0x00073192): "3714729bd2e47b2523c0f5be80b83b6aabada91d4af0c86a7bc81082e59d5c0f",
    (0x00067D48, 0x00067E0E): "539fb48bd094a7a19d587a1c7cae9c90fe9b8ef2324bf41de0e047704ef69db0",
    (0x000763D8, 0x000764D2): "03f14e4a89401fd7f6332cb13f29b6245d87e85bba0dd9454384f6d281ea0e57",
    (0x00061720, 0x00061740): "27d3fd703bfba6d640a1ef932e30873b65a613a489735992983018aed947ce3f",
    (0x00068238, 0x00068256): "1c35c0872e06b152b881e56b23b10c2547baef1e9f87b44d03dae1d794f7c487",
    (0x0002F108, 0x0002F1FE): "48949d4201ce8302be987e01589ef24b8206128382e3d1bf7b1a2276a45d1f81",
    (0x0002F614, 0x0002F622): "0dc3f838683aa27c2d249f4e0335b55605788b729779bb646881bca63fdf0aca",
    (0x000883FC, 0x0008841E): "ba79d6a956ec174581f95203b332ff86d61652d1e3ccb4b09b33a9f95b5a0c56",
    (0x00071E34, 0x00071FE8): "9d4210d133a3675079e05670128af9a74f289cc0bd99ff337e57aad8f1625fc4",
    (0x0006ABF8, 0x0006ACA2): "1853f132c013c2aa3dcc3f7751170e6ef043c710fff9e06e6fca75eb17a36797",
    (0x000720C8, 0x000720CE): "19b6208894d958e4f218e7113a69e42b1ac4e9fb2a2d4c650ca475c78d293037",
}

EXPECTED_DIRECT_BRANCHES = {
    0x0005F56C: [0x00060264, 0x0006028C],
    0x00061274: [0x0006059A, 0x000605B2],
    0x00068728: [0x0005F5A8],
    0x0007316C: [0x0005D4AC, 0x0005FC6E, 0x0005FD76],
    0x00067D48: [0x0005F7B6, 0x0005FC30],
    0x000763D8: [0x0005FCB8, 0x0005FDC0],
    0x0002F108: [0x00076410],
    0x0002F614: [0x00076428, 0x0007DA9A],
    0x000883FC: [0x0005F7A6],
    0x00071E34: [0x0006FF84],
    0x0006ABF8: [0x0004BF40],
    0x000720C8: [0x00071B14],
}

EXPECTED_FLOAT32 = {
    0x0005F9A8: 86400.0,
    0x0005FE6C: 0.66,
    0x0005FE70: 0.67,
    0x00061388: 3600.0,
    0x00073194: 2.8,
    0x00073198: 0.0,
    0x0007319C: 200.0,
    0x00067E10: 0.95,
    0x00067E14: -0.9414128,
    0x00067E18: 0.0,
    0x00067E1C: 0.6406555,
    0x00067E20: 0.3537866,
    0x00067E24: 0.6920604,
    0x00067E28: 1.01,
    0x00067E2C: 1.681,
    0x00067E30: 9.29,
    0x000764D4: 0.2,
}

EXPECTED_FLOAT64 = {
    0x00068800: 5.8384,
    0x00068808: 5.5296,
    0x00068810: 11.7,
    0x00068818: 45.9584,
    0x00068820: 4.6684,
    0x00068828: 4.6692,
    0x00068830: 9.624,
    0x00068838: 143.9384,
    0x00067E34: 4.09,
    0x00067E3C: 2.862,
    0x00067E44: 4.11,
}

EXPECTED_PROFILE_DEFAULTS = [28.0, 1.0, 175.0, 75.0, -1.0, -1.0, -1.0]


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + (end - start)]


def unpack(image: bytes, base: int, address: int, kind: str) -> float | int:
    widths = {"f": 4, "d": 8, "I": 4}
    return struct.unpack(
        "<" + kind,
        flash_bytes(image, base, address, address + widths[kind]),
    )[0]


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
                f"unexpected energy range 0x{start:08x}...0x{end:08x}: {actual_digest}"
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

    constants: dict[str, float | int] = {}
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
    day_seconds = unpack(image, base, 0x00061384, "I")
    if day_seconds != 86400:
        raise ValueError(f"unexpected activity day divisor: {day_seconds}")
    constants["0x00061384"] = day_seconds

    profile_defaults = list(struct.unpack(
        "<7f", flash_bytes(image, base, 0x0009A5B4, 0x0009A5D0)
    ))
    if profile_defaults != EXPECTED_PROFILE_DEFAULTS:
        raise ValueError(f"unexpected default GoMore profile: {profile_defaults}")

    energy_diagnostic = c_string(image, base, 0x0005FE74)
    substrate_diagnostic = c_string(image, base, 0x0005FE98)
    if energy_diagnostic != "[kcal]=%f [sKcal]=%f [aKcal]=%f\r\n":
        raise ValueError(f"unexpected energy diagnostic: {energy_diagnostic!r}")
    if substrate_diagnostic != "[met]=%f [fat]=%f [carb]=%f\r\n":
        raise ValueError(f"unexpected substrate diagnostic: {substrate_diagnostic!r}")

    copied_energy = [
        field for field in OUTPUT_FIELDS
        if field["engine_offset"] in {0x254, 0x278, 0x27C, 0x308, 0x30C, 0x310}
    ]
    expected_copied = [
        (0x254, 0x48, 4), (0x278, 0x4C, 4), (0x27C, 0x50, 4),
        (0x308, 0x78, 4), (0x310, 0x7E, 2), (0x30C, 0x7C, 2),
    ]
    if [(f["engine_offset"], f["io_offset"], f["width"]) for f in copied_energy] \
            != expected_copied:
        raise ValueError(f"unexpected copied energy/activity fields: {copied_energy}")
    hidden_offsets = {0x258, 0x25C, 0x260, 0x264, 0x268, 0x26C, 0x270, 0x274, 0x314}
    if any(field["engine_offset"] in hidden_offsets for field in OUTPUT_FIELDS):
        raise ValueError("hidden energy or distance field unexpectedly entered copied ABI")

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "diagnostics": {
            "energy": energy_diagnostic,
            "substrate": substrate_diagnostic,
        },
        "profile": {
            "persistent_to_float_converter": "0x0006abf8",
            "engine_profile_converter": "0x00071e34",
            "engine_fields": {
                "height_centimeters_float32": "0x74",
                "weight_kilograms_float32": "0x78",
                "age_years_uint8": "0x7c",
                "binary_sex_uint8": "0x7d",
            },
            "default_float_record": profile_defaults,
            "binary_sex_1_daily_resting_kcal":
                "height_cm*5.5296 + weight_kg*11.7 + 45.9584 - age_years*5.8384",
            "binary_sex_0_daily_resting_kcal":
                "height_cm*4.6692 + weight_kg*9.624 + 143.9384 - age_years*4.6684",
            "resting_rate_formula": "daily_resting_kcal / 86400 seconds",
            "formula_family_name_found_in_image": False,
        },
        "per_update_energy": {
            "function": "0x0005f56c",
            "engine_output_base": "0x254",
            "float_count": 11,
            "copied_fields": {
                "total_kcal": {"engine_offset": "0x254", "io_offset": "0x48"},
                "sKcal_resting_derived": {"engine_offset": "0x278", "io_offset": "0x4c"},
                "aKcal_above_baseline_active": {"engine_offset": "0x27c", "io_offset": "0x50"},
            },
            "normal_mode_component_formula": {
                "sKcal": "resting-derived rate * elapsed_seconds",
                "aKcal": "max(total rate - resting-derived rate, 0) * elapsed_seconds",
                "total": "sKcal + aKcal",
            },
            "mode_2_component_formula": {
                "sKcal": 0.0,
                "aKcal": "max(total rate, 0) * elapsed_seconds",
                "total": "aKcal",
            },
            "negative_auxiliary_resting_scale": "0.66 / (exp(-auxiliary) + 1) + 0.67",
            "s_and_a_literal_expansions_found": False,
        },
        "hidden_energy_outputs": {
            "met_candidate": {"engine_offset": "0x258", "formula": "total_kcal*200/(weight_kg*2.8)"},
            "fat_component": {"engine_offset": "0x25c", "formula": "total_kcal*fat_fraction"},
            "carbohydrate_component": {"engine_offset": "0x260", "formula": "total_kcal-fat_component"},
            "met_zone_accumulators": {
                "engine_offsets": ["0x264", "0x268", "0x26c", "0x270", "0x274"],
                "ordinary_zone_count": 4,
                "sustained_high_zone_minimum_elapsed_seconds": 600,
            },
            "copied_to_host_io": False,
        },
        "substrate_fraction": {
            "function": "0x00067d48",
            "upper_reference_contraction": "lower + 0.95*(upper-lower)",
            "normalized_input": "(value-lower)/(contracted_upper-lower)",
            "exponential_term": "exp(0.6406555*normalized)-0.9414128",
            "transform": "(0.6920604 + 0.95*0.3537866*exponential_term)*1.01",
            "fat_term": "max((1-transform)*1.681*9.29, 0)",
            "carbohydrate_term": "max((transform*4.09-2.862)*4.11, 0)",
            "fat_fraction": "fat_term/(fat_term+carbohydrate_term), or 0 when the denominator is zero",
            "clinical_validation_found": False,
        },
        "daily_activity_accumulator": {
            "function": "0x00061274",
            "state_pointer_initializer": "0x000720c8",
            "state_bytes_cleared_on_forward_day": 52,
            "used_state_layout": {
                "local_day_uint32": [0, 4],
                "timezone_offset_sign_extended_int32": [4, 8],
                "cumulative_step_float32": [8, 12],
                "cumulative_active_kcal_float32": [12, 16],
                "cumulative_all_kcal_float32": [16, 20],
                "cumulative_distance_float32": [20, 24],
                "reset_visible_reserved_tail": [24, 52],
            },
            "local_day_formula": (
                "wrapping_uint32(unix_seconds + sign_extended_timezone_minutes*60) / 86400"
            ),
            "forward_day_comparison": "signed Int32 comparison of stored and computed UInt32 days",
            "resets_only_when_computed_day_increases": True,
            "output_bytes_cleared_on_forward_day": 44,
            "steps": (
                "sum ordered nonnegative Float32 updates; VCVT.S32.F32 truncates/saturates; "
                "copy all 32 result bits"
            ),
            "active_kcal": (
                "sum ordered nonnegative aKcal updates; signed conversion; copy low UInt16"
            ),
            "all_kcal": (
                "sum ordered nonnegative total-kcal updates; signed conversion; copy low UInt16"
            ),
            "nan_inputs_are_rejected": True,
            "positive_infinity_is_accepted": True,
            "positive_infinity_integer_output": 2147483647,
            "production_thumb_fixture_bits": {
                "first": {
                    "steps": "0x3fc00000", "active": "0x3fa00000",
                    "all": "0x40300000", "distance": "0x3a83126e",
                },
                "second": {
                    "steps": "0x40880000", "active": "0x40700000",
                    "all": "0x40c80000", "distance": "0x3b449ba5",
                },
                "next_day": {
                    "steps": "0x40980000", "active": "0x40100000",
                    "all": "0x40b80000", "distance": "0x3b449ba6",
                },
                "unix_zero_timezone_minus_one_computed_day": 49710,
            },
            "hidden_distance": {
                "engine_offset": "0x314",
                "formula_per_update": "nonnegative selected_speed / 3600",
                "multiplies_by_elapsed_seconds": False,
                "copied_to_host_io": False,
                "stock_value": 0.0,
                "distance_unit_is_proven": False,
            },
        },
        "constants": constants,
        "verified_ranges": verified_ranges,
        "direct_branches": branches,
        "safety": {
            "static_read_only": True,
            "health_consent_required_for_captured_values": True,
            "live_sram_reader_exposed": False,
            "vendor_engine_execution_exposed": False,
            "clinical_claims_permitted": False,
            "raw_float_bits_should_be_preserved": True,
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
