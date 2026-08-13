#!/usr/bin/env python3
"""Emit the exact RTC-device/provider boundary census.

This parser is static and read-only. It identifies one Nordic SDK provider
body, one fixed R1 registry-binding wrapper, and seven still-unattributed RTC
device bodies without exposing a live clock setter or callback surface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


RTC_DEVICE_FUNCTIONS = [
    {
        "entry": 0x00056274, "end_exclusive": 0x000562E0,
        "symbol": "rtc_device_tick_and_calendar_callback_candidate",
        "role": "one_second_tick_and_calendar_callback_dispatch",
        "provider_family": "unknown_rtc_device_provider_candidate",
        "sha256": "8a1b73a478bd2ff45e5972e38d52805663cfb03e7f1ca04fae10e6f7e13ff1ae",
    },
    {
        "entry": 0x000562E0, "end_exclusive": 0x00056316,
        "symbol": "rtc_device_epoch_to_calendar_adapter_candidate",
        "role": "epoch_to_eight_field_calendar_conversion",
        "provider_family": "unknown_rtc_device_provider_candidate",
        "sha256": "b5011a6953f32e66a68740e5cdb90e3c1053295e987aefd092ffee261a7cd079",
    },
    {
        "entry": 0x00056318, "end_exclusive": 0x0005638E,
        "symbol": "rtc_device_open_by_name_candidate",
        "role": "named_record_lookup_and_nordic_rtc_start",
        "provider_family": "unknown_rtc_device_provider_candidate",
        "sha256": "95ca03552a9003269e1ad0a674e5c7c1f68920739fdef30397177e0a5b6edd7a",
    },
    {
        "entry": 0x0005639C, "end_exclusive": 0x000563C0,
        "symbol": "rtc_device_snapshot_candidate",
        "role": "epoch_and_subsecond_snapshot",
        "provider_family": "unknown_rtc_device_provider_candidate",
        "sha256": "bbd995708260fb66db08b75e522438c01bf9e8e87e549a29ea1f7c4225ba53e7",
    },
    {
        "entry": 0x000563C4, "end_exclusive": 0x000563F0,
        "symbol": "r1_rtc_device_binding_configuration",
        "role": "fixed_record_and_operation_table_registration",
        "provider_family": "r1_device_registry_configuration_adapter",
        "sha256": "326a0d5459a4e96e5268022d312c74c4a883fd3d4bca55c0a41cfd2dfd177a01",
    },
    {
        "entry": 0x000563F8, "end_exclusive": 0x00056440,
        "symbol": "rtc_device_calendar_record_write_candidate",
        "role": "named_calendar_record_copy",
        "provider_family": "unknown_rtc_device_provider_candidate",
        "sha256": "594512cd814903ab4af9a568a0dc12d87d9998e0bd490bd052be8debcaefa1fb",
    },
    {
        "entry": 0x00056444, "end_exclusive": 0x00056498,
        "symbol": "rtc_device_callback_binding_candidate",
        "role": "named_callback_binding",
        "provider_family": "unknown_rtc_device_provider_candidate",
        "sha256": "7c3f66da7e37614b28e3a998d9337ea797368f82483c64e4e9dac6ed1e0f6af9",
    },
    {
        "entry": 0x0005649C, "end_exclusive": 0x00056502,
        "symbol": "rtc_device_epoch_initialize_candidate",
        "role": "named_record_epoch_and_tick_divider_initialize",
        "provider_family": "unknown_rtc_device_provider_candidate",
        "sha256": "4fec74079f1b3e200dcc43ff283194db3385ade44833763d44f55e3d157824f0",
    },
    {
        "entry": 0x0007AD6C, "end_exclusive": 0x0007AE20,
        "symbol": "nrfx_rtc_init",
        "role": "Nordic_RTC_provider_initialize",
        "provider_family": "nordic_nrf5_sdk_17_1_0",
        "sha256": "1cb25319f2b719d139365c25f49e56d6eb78b4265e86096d0e92c255908d1d40",
    },
]

for _item in RTC_DEVICE_FUNCTIONS:
    _item["size"] = int(_item["end_exclusive"]) - int(_item["entry"])


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")

    functions = []
    for function in RTC_DEVICE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"RTC-device boundary changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    counts: dict[str, int] = {}
    for function in functions:
        family = str(function["provider_family"])
        counts[family] = counts.get(family, 0) + 1
    return {
        "analysis": "R1 RTC-device/provider boundary census",
        "image": str(image_path),
        "image_sha256": image_digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "provider_counts": counts,
        "functions": functions,
        "source_lineage": {
            "nrfx_rtc_init": "Nordic nRF5 SDK 17.1.0",
            "rtc_device_layer": "unidentified provider candidate",
            "local_rtc_provider_implementation_authorized": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_clock_mutation": False,
            "callback_registration_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
