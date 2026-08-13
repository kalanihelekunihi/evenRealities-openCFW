#!/usr/bin/env python3
"""Validate the exact R1 wear runtime, charge timers, and sleep-result living bridge."""

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
    (0x0003D0C0, 0x0003D0F4):
        "aabd30f3f7ed457001415489dc9bd3066ae87cf80a623745b5eb09e5353e9af1",
    (0x0003D0FC, 0x0003D150):
        "3ba415db64a38a1cad01c741eb8d12f62b6f4071c5ffec2bae1c8c4c888d8c91",
    (0x0003D150, 0x0003D1A0):
        "1d8bccca275c1d08c9568f6b735312d7b5c40be1dc06f7442687e1fcd418e051",
    (0x0003D1B8, 0x0003D210):
        "62de8d2279d611e630fbdf702a032860f1d1201d8125c6c221fe42256d136e17",
    (0x0004A4B4, 0x0004A524):
        "0c0fca1d88d779468b72c869b33a858a143a120c9e03395c28c23506f19b6089",
    (0x0004A56C, 0x0004A59C):
        "ce9012e61b7beef1a4ce9514f6ee4aad6cbaebc230d00cdb285b2220cf3cb0bc",
    (0x0004A7F4, 0x0004A86C):
        "7fb3ee4ad7e70b5bb7d5e165899382f467e5075078aff7e3ad7cd3eb8272ee0e",
    (0x0004A8BC, 0x0004A8C8):
        "71686482cd48aa2a9d9a0550f42046d05600f56afa4f6c8817263d023d6abdd2",
    (0x0004A8C8, 0x0004A948):
        "ab169aec449896774956f0a8b7a44381932d017afe162f5e2ddf8987af740be5",
    (0x0004A998, 0x0004A9FC):
        "dfde79e1849c5018976339defeeff45af2703406bae098bde9664bf1a21accde",
    (0x0004C3D0, 0x0004C4B0):
        "cc86c0acdad361b64623321ea1522239bc48fbca525353261c7c4ce75cf6f673",
    (0x0004C4B8, 0x0004C564):
        "ab001ccc73af8f0434cbd8d681de9333f0a0d7ba4973ee1696602860974ee96e",
    (0x0004C5C4, 0x0004C60C):
        "d90cfb514008937bebeee5afd0e18f23e36d01f789b0a07d4472ebf9a70ef815",
    (0x0004C64C, 0x0004C66C):
        "4e9607d4e249f9bb6f75efc2d9cc14410d7da83c9a7b5e323a576ee19ea2b7c5",
    (0x0004C6C0, 0x0004C6CC):
        "32f7065bf33b7cf1df4c93e182ce599a7ffa7921d90e26fe1b5544921da0d42d",
    (0x0004C6CC, 0x0004C6D0):
        "e0489918cf497abdd4bd7392ec6004fa401dd2810cb21ea8f98b54515b3e0fab",
    (0x00050618, 0x00050624):
        "36beb0b6526ca40c77376851b6ccd996562df4b6a2c59ad57afa365f043fb49e",
    (0x00050998, 0x000509A4):
        "621c2e0638292b5234448b86181db4e309e2278a0b9938b69d9c4a0d238e3eed",
}

EXPECTED_BRANCHES = {
    0x0003D0C0: [0x0003D16E, 0x0004C530, 0x0004C6CC],
    0x0003D0FC: [0x0004C534, 0x0004C606],
    0x0004A4B4: [0x000423D4, 0x0004A9DC],
    0x0004A7F4: [0x0006C32E, 0x0006C36C],
    0x0004A8BC: [0x00048D5A, 0x00048EDE, 0x00049072, 0x00057628],
    0x0004A8C8: [0x0004A860],
    0x0004C4B8: [0x00042112],
    0x0004C5C4: [0x0004A21E],
    0x0004C6C0: [0x0004A3EC],
    0x00050618: [
        0x00031FD4, 0x0003CD30, 0x000463F6, 0x0004640E, 0x0004641C,
        0x00047F2E, 0x0004C3D2, 0x00062554, 0x0006257E, 0x00091246,
        0x00091258, 0x000912B2, 0x00096AD8, 0x00096CE2, 0x00096D08,
    ],
    0x00050998: [0x0004C5C8],
}

EXPECTED_LITERALS = {
    0x0003D0EC: 0x20006E94,
    0x0003D0F4: 0x2001E454,
    0x0003D134: 0x20006E94,
    0x0003D138: 0x0003D0F9,
    0x0003D14C: 0x0004C64D,
    0x0003D19C: 0x20006E94,
    0x0003D1A0: 0x2001E454,
    0x0003D1A4: 0x0003CE1D,
    0x0003D1B4: 0x0004C6CD,
    0x0003D210: 0x20006E94,
    0x0003D640: 0x20006E94,
    0x0004A524: 0x20006ED4,
    0x0004A568: 0x0004A56D,
    0x0004A598: 0x20006ED4,
    0x0004A8B8: 0x20006ED4,
    0x0004A8C4: 0x20006ED4,
    0x0004A948: 0x20006ED4,
    0x0004A94C: 0x0004A999,
    0x0004AA60: 0x20006ED4,
    0x0004C4B0: 0x2001E454,
    0x0004C4B4: 0x20006E94,
    0x0004C564: 0x2001E454,
    0x0004C5B0: 0x20006E94,
    0x0004C5B4: 0x0004C3D1,
    0x0004C60C: 0x0003D151,
    0x0004C610: 0x20006E94,
    0x0004C614: 0x0003CD81,
    0x0004C624: 0x2001E454,
    0x0004C628: 0x20006610,
    0x0004C62C: 0x00043789,
    0x0004C630: 0x0003D1B9,
    0x0004C66C: 0x20006E94,
    0x0004C6C8: 0x20006E94,
    0x000509A0: 0x200076C4,
}

EXPECTED_STRINGS = {
    0x0003D0F0: b"adt\x00",
    0x0003D13C: b"wearled\x00",
    0x0003D144: b"raw_hr\x00",
    0x0003D1A8: b"algo\x00",
    0x0003D1B0: b"adt\x00",
    0x0003D648: b"algo\x00",
    0x0003D650: b"wear\x00",
    0x0004C618: b"algo\x00",
    0x0004C620: b"acc\x00",
    0x0004C670: b"raw_hr\x00",
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

    strings: dict[str, str] = {}
    for address, expected in EXPECTED_STRINGS.items():
        actual = flash_bytes(image, base, address, address + len(expected))
        if actual != expected:
            raise ValueError(f"unexpected string at 0x{address:08x}: {actual!r}")
        strings[f"0x{address:08x}"] = expected[:-1].decode("ascii")

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "topic_strings": strings,
        "wear_runtime": {
            "address": "0x20006e94",
            "bytes": 32,
            "layout": {
                "0x00": "wearled topic status",
                "0x01": "sleep-result status mirrored by callback 3",
                "0x02": "living-confirmed-during-sleep flag",
                "0x03": "reserved",
                "0x04": "acc subscription handle",
                "0x08": "adt subscription handle",
                "0x0c": "wear/living-object subscription handle",
                "0x10": "adt seven-second timeout handle",
                "0x14": "charge sixty-second check handle",
                "0x18": "raw_hr readiness subscription handle",
                "0x1c": "raw_hr three-second timeout handle",
            },
            "topics": {
                "motion": ["acc", "algo"],
                "optical_history": ["adt", "algo"],
                "living_object": ["wear", "algo"],
                "raw_readiness": ["raw_hr", "wearled"],
            },
            "timeouts_ms": {
                "adt": 7_000,
                "raw_hr_readiness": 3_000,
                "charge_check": 60_000,
            },
            "charge": {
                "normalized_states_10_11_12": 1,
                "normalized_state_13": 2,
                "all_other_normalized_states": 0,
                "callback_status_1": "stop ADT, start raw_hr readiness, report not-worn",
                "timeout_only_clears": "stored status 1 and normalized hardware status 0",
            },
        },
        "sleep_result_bridge": {
            "address": "0x20006ed4",
            "bytes": 12,
            "layout": {
                "0x00": "sleep-result status",
                "0x01": "GoMore authorization mode-5 return byte",
                "0x02...0x03": "reserved",
                "0x04": "forced-awake delayed-history timeout handle",
                "0x08": "vivo-probe timeout handle",
            },
            "status_one_transition_from_zero": {
                "confirmed_internal_wear_state_2": "skip probe",
                "other_state": "request GoMore mode 5 and start five-second timeout",
            },
            "five_second_timeout": {
                "internal_wear_state_0": "force status zero and finalize sleep",
                "internal_wear_state_nonzero": "do not force awake",
                "always": "disable successful mode-5 request and clear probe timer",
            },
            "forced_awake_delay_ms": 3_000,
            "delayed_history_event": [6, 1, 0, 0, "context UInt32LE"],
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
