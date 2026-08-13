#!/usr/bin/env python3
"""Validate the exact higher R1 wear-fusion state machine and public mapping boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


EXPECTED_RANGES = {
    (0x0003CD80, 0x0003CE14):
        "bc589b15d97a3bb37513067bfae52699c34a875a25db66d5e7d552685e02de3c",
    (0x0003CE1C, 0x0003CE40):
        "d18576349aeb0054258b21a50509c1750ba53bb0d99b24067db248e848fc0e11",
    (0x0003CE44, 0x0003CEA4):
        "28c3fdc29fbf07a838d0309718375aa1bcd0fc25ca3316b277130f97296bb53b",
    (0x0003CEEC, 0x0003D06C):
        "0d81dcb757a115460cd17dd1882b04418f63dd19c0279cc54e7566ad3a54ed3e",
    (0x0003D06C, 0x0003D0B4):
        "57d87392bb9452ec09f0fcb09a403ca8588c64ba5768ca6336c47157408995d1",
    (0x0003D0C0, 0x0003D0F4):
        "aabd30f3f7ed457001415489dc9bd3066ae87cf80a623745b5eb09e5353e9af1",
    (0x0003D0FC, 0x0003D150):
        "3ba415db64a38a1cad01c741eb8d12f62b6f4071c5ffec2bae1c8c4c888d8c91",
    (0x0003D150, 0x0003D1A0):
        "1d8bccca275c1d08c9568f6b735312d7b5c40be1dc06f7442687e1fcd418e051",
    (0x0003D1B8, 0x0003D210):
        "62de8d2279d611e630fbdf702a032860f1d1201d8125c6c221fe42256d136e17",
    (0x0003D268, 0x0003D39C):
        "ba44d31b3ae2e9fd384bbf5526176ba2d8e9ee2e6be55c2a6213c234fa4842e9",
    (0x0003D45C, 0x0003D63C):
        "8511cd323737b80efcc86f314395b7f4a89f0b29710947b9b1276243e40efac9",
    (0x00043788, 0x000437F4):
        "7e098492d3ec0120cec17273cf5e525fedf39c25197741be5728780803f4dce7",
    (0x0004C3D0, 0x0004C4B0):
        "cc86c0acdad361b64623321ea1522239bc48fbca525353261c7c4ce75cf6f673",
    (0x0004C4B8, 0x0004C564):
        "ab001ccc73af8f0434cbd8d681de9333f0a0d7ba4973ee1696602860974ee96e",
    (0x0004C5B8, 0x0004C5C0):
        "1067a0bdcf3149a9042ab3fe414cc4ad4c999b48a760b1847b20abfdb05a99fa",
    (0x0004C5C4, 0x0004C60C):
        "d90cfb514008937bebeee5afd0e18f23e36d01f789b0a07d4472ebf9a70ef815",
    (0x0004C634, 0x0004C648):
        "bb9e511c5ebd46dd5151b0c5e4679a058fe6c74e9c0316e386e73c199bd42ee1",
    (0x0004C678, 0x0004C6BC):
        "6780bbe91d384a39de17dccd23840eb2145d7492a7c6d782a1f42e0ab4809541",
    (0x00084B24, 0x00084BD4):
        "726d04d491f23726e2a262d4e978d1556232689192991bf1685c57428f95617c",
    (0x00096A40, 0x00096A48):
        "626fa7d084aadb896d97e65ffc715ab280a31e48dbb466b9209071997c25245c",
}

EXPECTED_BRANCHES = {
    0x0003CEEC: [0x0003CDBC],
    0x0003D06C: [0x0003D28C],
    0x0003D0C0: [0x0003D16E, 0x0004C530, 0x0004C6CC],
    0x0003D0FC: [0x0004C534, 0x0004C606],
    0x0003D268: [0x0003CE0C],
    0x0003D45C: [0x0003CDCA],
    0x0004C4B8: [0x00042112],
    0x0004C5B8: [
        0x00048EEA, 0x0004907E, 0x00049AEA, 0x00049F42, 0x0004A99C,
        0x0004AF46, 0x0004BBF2, 0x0004FA62, 0x0006ACEC, 0x00084B2C,
        0x00084B32,
    ],
    0x0004C634: [
        0x00048D62, 0x00048EF0, 0x00049084, 0x00049A4A, 0x00049BBA,
        0x0004A302, 0x0004A8D2, 0x0004AC68, 0x0004AE20, 0x0004B536,
    ],
    0x0004C678: [0x000437EC, 0x000453EA],
    0x00096A40: [0x0003CD96, 0x0003CDD4, 0x0004C426, 0x0004C51C, 0x0004C53A],
}

EXPECTED_LITERALS = {
    0x0003CE14: 0x2001E454,
    0x0003CE40: 0x2001E454,
    0x0003CEA4: 0x2001E454,
    0x0003D0B4: 0x2001E454,
    0x0003D0F4: 0x2001E454,
    0x0003D1A0: 0x2001E454,
    0x0003D39C: 0x2001E454,
    0x0003D63C: 0x2001E454,
    0x0003D640: 0x20006E94,
    0x0003D660: 9_050_000,
    0x0003D664: 0x42200000,
    0x0003D668: 0xBB8CFFFF,
    0x0003D66C: 0x00137FFF,
    0x000437F4: 0x2001E454,
    0x0004C4B0: 0x2001E454,
    0x0004C564: 0x2001E454,
    0x0004C5C0: 0x2001E454,
    0x0004C624: 0x2001E454,
    0x0004C648: 0x2001E454,
    0x0004C6BC: 0x2001E454,
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + end - start]


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    ranges = []
    for (start, end), expected in EXPECTED_RANGES.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != expected:
            raise ValueError(f"unexpected range 0x{start:08x}...0x{end:08x}: {actual}")
        ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual,
        })

    branches: dict[str, list[str]] = {}
    for target, expected in EXPECTED_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected:
            raise ValueError(f"unexpected branches to 0x{target:08x}: {actual}")
        branches[f"0x{target:08x}"] = [f"0x{address:08x}" for address in actual]

    literals: dict[str, str] = {}
    for address, expected in EXPECTED_LITERALS.items():
        actual = struct.unpack("<I", flash_bytes(image, base, address, address + 4))[0]
        if actual != expected:
            raise ValueError(f"unexpected literal at 0x{address:08x}: 0x{actual:08x}")
        literals[f"0x{address:08x}"] = f"0x{actual:08x}"

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "state": {
            "address": "0x2001e454",
            "bytes": 41,
            "layout": {
                "0x00...0x13": "five UInt32 IR-history slots",
                "0x14": "declared IR-history count",
                "0x15...0x17": "reserved",
                "0x18...0x1b": "previous history-last UInt32",
                "0x1c": "living-object status",
                "0x1d...0x1f": "reserved",
                "0x20...0x23": "living-object callback tick",
                "0x24": "internal wear state 0/1/2",
                "0x25": "policy; production initializes 2",
                "0x26": "charge status; 1 blocks detection",
                "0x27": "low-IR decision counter",
                "0x28": "stationary-table decision counter",
            },
        },
        "fusion": {
            "minimum_motion_samples": 10,
            "states": {
                "0": "not worn",
                "1": "suspected worn",
                "2": "living-confirmed worn",
            },
            "wear_on": {
                "IR_history_range_minimum": 100_000,
                "IR_latest_strictly_above": 9_050_000,
                "motion_any_variance_strictly_above": 2_000.0,
            },
            "living_confirmation": {
                "window_ticks_inclusive": 0x800,
                "status_0": "not worn",
                "status_1": "living-confirmed worn",
            },
            "wear_off": {
                "IR_latest_strictly_below": 9_050_000,
                "IR_consecutive_decisions": 5,
                "absolute_mean_y_float32_bits": "strictly (972.0, 1076.0)",
                "all_motion_variances_strictly_below": 40.0,
                "stationary_consecutive_decisions": 60,
                "sleep_status_1":
                    "preserves suspected-worn instead of clearing",
            },
        },
        "public_mapping": {
            "notification": {"0": "notWear(1)", "nonzero": "wear(2)"},
            "explicit_query": {"0": "notWear(1)", "1": "wear(2)", "2_or_other": "unknown(0)"},
            "confirmed_wear_query_inconsistency": True,
            "health_algorithm_eligibility_requires_exact_state_2": True,
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
            "health_store_access": False,
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
