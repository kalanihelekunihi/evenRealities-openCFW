#!/usr/bin/env python3
"""Validate the production public activity daily/all-day route.

This parser is static and read-only. It does not connect to a ring, publish an internal event,
invoke BLE, read health data, or mutate firmware.
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
from summarize_r1_gomore_input_abi import IMAGE_SHA256


RANGES = {
    (0x82C10, 0x82C44): "38b7a30aaa28b66ced1d8db8098441027418b61c60a271b7d735b3061588bed3",
    (0x82C44, 0x82C8A): "5e2461720215c94cc77eed9e32ff388a9cce6995c3682fd0999e68c7717c1187",
    (0x8BA48, 0x8BA6E): "843ba5c0db6ec92767b369c4cf5ee0688ac5f60e44823040d95d70efa8e2ac31",
    (0x42108, 0x4210C): "f112adca674a4537dc031080ca6fc585abab6e8536742c35d256346ac53be7b7",
    (0x49068, 0x49164): "a5436baeea82dcfdcd92ffa967adab36803e28864c6d6f0e32d3989ba3dcdbde",
    (0x42788, 0x42840): "6d8909d67d308277bf68743129b3b6b39e557101b86f10a24596c5715f1e3687",
    (0x83930, 0x83972): "e8525e642988dccd5218353948d9b90e269a42698ff6f0a049c94dd5bea50b35",
    (0x83972, 0x839B4): "5be0afbd7a6296c529e0df91825c13c8fb1645af137828d82eafdbad04a16741",
    (0x2E8D0, 0x2E8E8): "906578a95c2b5749235125867351b0f7f94d209c629cd2722baba2677a96b30e",
}

BRANCHES = {
    0x49068: [0x42108],
    0x8A7F4: [0x427EE],
    0x5AA14: [0x8A7FA],
    0x8BAEC: [0x8B170, 0x8BA58],
    0x82844: [0x82C68, 0x82CAE, 0x82CF2, 0x82D38, 0x82D7E, 0x82DE0, 0x82E1C],
    0x83930: [0x8B994],
    0x83972: [0x8BA42],
}

DAILY_REGISTRATION_ADDRESS = 0x9A49C
ALL_DAY_REGISTRATION_ADDRESS = 0x9A4A4
DAILY_REGISTRATION = bytes.fromhex("01050000452c0800")
ALL_DAY_REGISTRATION = bytes.fromhex("02050000112c0800")


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


def movw_immediate_sites(image: bytes, base: int, wanted: int) -> list[dict[str, Any]]:
    """Decode aligned Thumb-2 MOVW T3 instructions with the requested immediate."""
    sites: list[dict[str, Any]] = []
    for offset in range(0, len(image) - 3, 2):
        first, second = struct.unpack_from("<HH", image, offset)
        if first & 0xFBF0 != 0xF240:
            continue
        immediate = (
            (first & 0xF) << 12
            | ((first >> 10) & 1) << 11
            | ((second >> 12) & 0x7) << 8
            | (second & 0xFF)
        )
        if immediate != wanted:
            continue
        sites.append({
            "address": f"0x{base + offset:08x}",
            "destination_register": (second >> 8) & 0xF,
            "raw_hex": image[offset : offset + 4].hex(),
        })
    return sites


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image sha256: {digest}")

    ranges = []
    for (start, end), wanted in RANGES.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != wanted:
            raise ValueError(f"range 0x{start:x}...0x{end:x}: {actual}")
        ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual,
        })

    registrations = {
        "daily": flash_bytes(
            image,
            base,
            DAILY_REGISTRATION_ADDRESS,
            DAILY_REGISTRATION_ADDRESS + len(DAILY_REGISTRATION),
        ),
        "all_day": flash_bytes(
            image,
            base,
            ALL_DAY_REGISTRATION_ADDRESS,
            ALL_DAY_REGISTRATION_ADDRESS + len(ALL_DAY_REGISTRATION),
        ),
    }
    if registrations["daily"] != DAILY_REGISTRATION:
        raise ValueError(f"daily registration changed: {registrations['daily'].hex()}")
    if registrations["all_day"] != ALL_DAY_REGISTRATION:
        raise ValueError(f"all-day registration changed: {registrations['all_day'].hex()}")

    branches: dict[str, list[str]] = {}
    for target, wanted in BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != wanted:
            raise ValueError(f"branches to 0x{target:x}: {actual}")
        branches[f"0x{target:08x}"] = [f"0x{address:08x}" for address in actual]

    all_day_movw = movw_immediate_sites(image, base, 0x0502)
    expected_movw = [{
        "address": "0x0002e8d0",
        "destination_register": 0,
        "raw_hex": "40f20250",
    }]
    if all_day_movw != expected_movw:
        raise ValueError(f"unexpected MOVW #0x0502 sites: {all_day_movw}")
    if direct_thumb_branches_to(image, base, 0x2E8D0):
        raise ValueError("the sole MOVW #0x0502 helper unexpectedly acquired a direct caller")

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "registrations": {
            "daily": {
                "address": f"0x{DAILY_REGISTRATION_ADDRESS:08x}",
                "packed_identifier": "0x0501",
                "handler_thumb": "0x00082c45",
                "raw_hex": registrations["daily"].hex(),
            },
            "all_day": {
                "address": f"0x{ALL_DAY_REGISTRATION_ADDRESS:08x}",
                "packed_identifier": "0x0502",
                "handler_thumb": "0x00082c11",
                "raw_hex": registrations["all_day"].hex(),
            },
        },
        "direct_branches": branches,
        "daily_route": {
            "accepted_status_mask_must_be_zero": "0x03",
            "immediate_response": {
                "packed_identifier": "0x0501",
                "type": 2,
                "payload_bytes": 0,
                "request_serial_preserved": True,
            },
            "event_14_record": "[4, 1, serial U16LE, context U32LE]",
            "consumer_action": "tail-call 0x0008baec(serial)",
        },
        "all_day_route": {
            "accepted_status_mask_must_be_zero": "0x03",
            "immediate_response": None,
            "event_14_record": "[4, 0, serial U16LE, context U32LE]",
            "consumer_action": "publish system event 0x1009 with null payload",
            "system_handler": "0x00042108 -> 0x00049068",
            "resulting_internal_event": "0x000b activity delta when counters advanced",
            "request_serial_reaches_accumulator": False,
            "direct_0x0502_response_sender_on_route": False,
        },
        "response_sender_negative_evidence": {
            "sole_aligned_movw_0x0502_site": all_day_movw,
            "site_has_direct_caller": False,
            "site_semantic": "unrelated 0x2b0b8/0x2b0dc configuration helper",
            "known_point_response_wrappers": [
                {"address": "0x00083930", "packed_identifier": "0x0102", "payload_bytes": 8},
                {"address": "0x00083972", "packed_identifier": "0x0402", "payload_bytes": 9},
            ],
        },
        "first_party_cross_version_parser": {
            "guard_bytes": 12,
            "minimum_successful_bytes": 14,
            "fields": [
                "context Int16LE at 0",
                "timestamp Int32LE at 2",
                "steps Int32LE at 6",
                "reserved/skipped UInt16LE at 10",
                "all_kcal Int16LE at 12",
            ],
            "source_is_firmware_image": False,
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
