#!/usr/bin/env python3
"""Pin the exact production systemTime handler and its phone-mediated follow-ups.

This analyzer reads only a supplied firmware image. It does not set a clock, publish internal
events, access BLE, request or apply NV recovery, read live identifiers, or contact hardware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


RANGES = [
    (
        0x000846DC,
        0x000847BC,
        "22a7633d2fe70732510b3dbe1605dbc469f07a7e27f9a182454ce6c3be9c4baf",
        "complete systemTime handler",
    ),
    (
        0x00082BD4,
        0x00082BE6,
        "1f0181948d602c0210ecae853b284d17e6b01d0e14a901c8b6548d03d81c9dac",
        "payload-presence helper",
    ),
    (
        0x00065D64,
        0x00065E48,
        "75633aa478660597d6d07d0d344b854aabfc4bc9073b27531d2a0055e3f6d29c",
        "delayed-callback cancellation helper",
    ),
    (
        0x0008ADB4,
        0x0008ADBC,
        "602c8c71b053148eff399239231d18cc077a6d08376289d9e4b489579c05cbcb",
        "signed timezone accessor",
    ),
    (
        0x0008ADA4,
        0x0008ADAE,
        "571d07446347362a5115a6a056aecaeef7c5098efd08f2c2aa54a5b85fe8c63f",
        "Unix-seconds accessor",
    ),
    (
        0x0008D8FC,
        0x0008D9C6,
        "dda68ce96d537f40a139557653a7c7c90c7ed366f37ec3f67deed27fa818a2e3",
        "internal event publisher",
    ),
    (
        0x0008287C,
        0x000828AE,
        "88936f6150f4b97dc7fc7a941ec07edc96ab5e8c933d4ad27167386862f1ba2f",
        "empty response builder",
    ),
    (
        0x00082B54,
        0x00082B8E,
        "e113d0aa4ff0b9aaf0b9b2c3f693c7dbf1de2c16f5171418d3b8d758c250243d",
        "empty notification builder",
    ),
    (
        0x0007BB20,
        0x0007BB40,
        "add7cc3f218a23eb7a0ef6d9f6e591e6081f5a417e9fef989dfad1d10f560dea",
        "NV validity classifier",
    ),
    (
        0x00083C86,
        0x00083CA6,
        "166e7c2d37d08393aa6297244c2420b9bb07da134fa55544fb6197e2878d3fa4",
        "NV recovery request builder",
    ),
    (
        0x0007BBE8,
        0x0007BC94,
        "7716a9fd04a7fee988e1a492e37432310126c69602c23dbbd0884417cd9d1074",
        "NV recovery report builder",
    ),
]

SYSTEM_TIME_HANDLER = 0x000846DC
PAYLOAD_HELPER = 0x00082BD4
CANCEL_CALLBACK = 0x00065D64
TIMEZONE_ACCESSOR = 0x0008ADB4
TIME_ACCESSOR = 0x0008ADA4
EVENT_PUBLISHER = 0x0008D8FC
EMPTY_RESPONSE = 0x0008287C
EMPTY_NOTIFICATION = 0x00082B54
NV_VALIDITY = 0x0007BB20
NV_REQUEST = 0x00083C86
NV_REPORT = 0x0007BBE8

REGISTRATION_ADDRESS = 0x0009A4EC
REGISTRATION_BYTES = bytes.fromhex("05000000dd460800")
AUTH_CALLBACK_POINTER_ADDRESS = 0x000847BC
AUTH_CALLBACK_THUMB = 0x00084C83

HANDLER_CALLS = {
    CANCEL_CALLBACK: [0x000846E8],
    PAYLOAD_HELPER: [0x000846EE],
    TIMEZONE_ACCESSOR: [0x000846F6],
    TIME_ACCESSOR: [0x000846FE],
    EVENT_PUBLISHER: [0x00084716],
    EMPTY_RESPONSE: [0x00084728],
    EMPTY_NOTIFICATION: [0x0008473A],
    NV_VALIDITY: [0x0008473E],
    NV_REQUEST: [0x0008475E],
    NV_REPORT: [0x0008478A],
}

COMPLETE_BRANCH_SETS = {
    NV_VALIDITY: [0x0008473E],
    NV_REQUEST: [0x0008475E],
    NV_REPORT: [0x0007C4B6, 0x0008478A],
}

DIAGNOSTICS = (
    b"[RING]nv data lose, request nv recover\0",
    b"[RING]nv data valid, report nv recover\0",
)


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


def checked_range(
    image: bytes,
    base: int,
    start: int,
    end: int,
    expected: str,
    label: str,
) -> dict[str, str]:
    actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
    if actual != expected:
        raise ValueError(f"unexpected {label} range: {actual}")
    return {
        "label": label,
        "start": f"0x{start:08x}",
        "end_exclusive": f"0x{end:08x}",
        "sha256": actual,
    }


def branch_addresses(image: bytes, base: int, target: int) -> list[int]:
    return [address for address, _ in direct_thumb_branches_to(image, base, target)]


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    ranges = [
        checked_range(image, base, start, end, expected, label)
        for start, end, expected, label in RANGES
    ]
    registration = flash_bytes(
        image,
        base,
        REGISTRATION_ADDRESS,
        REGISTRATION_ADDRESS + len(REGISTRATION_BYTES),
    )
    if registration != REGISTRATION_BYTES:
        raise ValueError(f"unexpected systemTime registration: {registration.hex()}")
    callback = int.from_bytes(
        flash_bytes(
            image,
            base,
            AUTH_CALLBACK_POINTER_ADDRESS,
            AUTH_CALLBACK_POINTER_ADDRESS + 4,
        ),
        "little",
    )
    if callback != AUTH_CALLBACK_THUMB:
        raise ValueError(f"unexpected authentication callback pointer: 0x{callback:08x}")

    handler_calls: dict[str, list[str]] = {}
    for target, expected in HANDLER_CALLS.items():
        actual = [
            address
            for address in branch_addresses(image, base, target)
            if SYSTEM_TIME_HANDLER <= address < 0x000847BC
        ]
        if actual != expected:
            raise ValueError(
                f"unexpected systemTime calls to 0x{target:08x}: {actual}"
            )
        handler_calls[f"0x{target:08x}"] = [
            f"0x{address:08x}" for address in actual
        ]
    complete: dict[str, list[str]] = {}
    for target, expected in COMPLETE_BRANCH_SETS.items():
        actual = branch_addresses(image, base, target)
        if actual != expected:
            raise ValueError(
                f"unexpected complete branch set to 0x{target:08x}: {actual}"
            )
        complete[f"0x{target:08x}"] = [
            f"0x{address:08x}" for address in actual
        ]
    for diagnostic in DIAGNOSTICS:
        if diagnostic not in image:
            raise ValueError(f"missing diagnostic: {diagnostic[:-1]!r}")

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "registration": {
            "address": f"0x{REGISTRATION_ADDRESS:08x}",
            "system_subcommand": "0x05",
            "handler_thumb": "0x000846dd",
            "raw_hex": registration.hex(),
        },
        "authentication_callback": {
            "pointer_address": f"0x{AUTH_CALLBACK_POINTER_ADDRESS:08x}",
            "thumb": f"0x{callback:08x}",
            "cancelled_before_payload_check": True,
            "context_filter": 0,
        },
        "handler_call_sites": handler_calls,
        "complete_direct_branch_sets": complete,
        "payload": {
            "protocol_header_bytes": 12,
            "payload_present_rule": "declared frame length != 12",
            "minimum_payload_length_checked": False,
            "meaningful_payload_bytes": 6,
            "official_controller_payload_bytes": 12,
            "layout": [
                "requested signed timezone minutes Int16LE @0",
                "requested Unix seconds UInt32LE @2",
                "six ignored reserved bytes @6 in the official controller shape",
            ],
        },
        "accepted_order": [
            "cancel authentication callback 0x84c83 for every context",
            "read old signed timezone and Unix seconds",
            "publish internal event 3 with old/new 12-byte transition",
            "emit empty successful systemTime response on incoming session",
            "emit empty type-2 system/userInfo request on incoming session",
            "classify NV validity",
            "request phone NV recovery through current EUS when raw state is 0 or 0xff",
            "otherwise report the local 116-byte CRC-gated NV recovery body",
        ],
        "internal_time_event": {
            "identifier": 3,
            "bytes": 12,
            "layout": [
                "old signed timezone minutes Int16LE @0",
                "new signed timezone minutes Int16LE @2",
                "old Unix seconds UInt32LE @4",
                "new Unix seconds UInt32LE @8",
            ],
            "publisher_result_checked": False,
        },
        "phone_mediation": {
            "user_info_header_hex": "0201000400000000",
            "nv_request_header_hex": "0001001100000000",
            "nv_report_header_hex": "0201001100000000",
            "nv_report_nested_payload_bytes": 121,
            "nv_report_body_bytes": 116,
            "nv_report_contains_identifiers_and_calibration": True,
        },
        "safety": {
            "physical_device_access": False,
            "clock_mutation": False,
            "ble_access": False,
            "internal_event_publish": False,
            "nv_recovery_read_or_write": False,
            "identifier_or_calibration_output": False,
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
