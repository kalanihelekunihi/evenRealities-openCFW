#!/usr/bin/env python3
"""Pin the destructive production semantics of system removeRingNotify (0x82).

This analyzer reads only the supplied image. It never sends the command, opens BLE, reads or writes
ring storage, changes pairing state, or contacts physical hardware.
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
    (0x000844B0, 0x000844EC, "f8b2bef36bb1513d08526279dae8a2b188315db51169191dba3658094d4db9e3",
     "removeRingNotify handler"),
    (0x00073834, 0x00073864, "18434d69194f14c10acb0fc9b74ca9e34cb39f59d4c4bfac41b002e5f5d007a6",
     "glasses-connected flag setter"),
    (0x000738A8, 0x000738EC, "6dc2ff34388aa88c5b8888d90905dd91cd23723bc39aac3543d4660b9fcabd97",
     "two-peer-slot setter"),
    (0x00082BD4, 0x00082BE6, "1f0181948d602c0210ecae853b284d17e6b01d0e14a901c8b6548d03d81c9dac",
     "payload-presence helper"),
]
HANDLER_START = 0x000844B0
HANDLER_END = 0x000844EC
REGISTRATION_ADDRESS = 0x0009A55C
REGISTRATION_BYTES = bytes.fromhex("82000000b1440800")
RESPONSE_HELPER = 0x0008287C
FLAG_SETTER = 0x00073834
PEER_SETTER = 0x000738A8
PAYLOAD_HELPER = 0x00082BD4
EXPECTED_FLAG_SETTER_BRANCHES = [0x0004538E, 0x00046040, 0x000844D4]
EXPECTED_PEER_SETTER_BRANCHES = [0x00046052, 0x0004D9E2, 0x000844E6]
EXPECTED_PAYLOAD_HELPER_BRANCHES = [
    0x00083D0C, 0x00083FC6, 0x00084154, 0x000842D0, 0x000842F4, 0x000843D0,
    0x000844B8, 0x000844F4, 0x000845C2, 0x000846EE, 0x0008487A, 0x00084A1A,
]


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
    verified = [
        checked_range(image, base, start, end, sha, label)
        for start, end, sha, label in RANGES
    ]
    registration = flash_bytes(
        image, base, REGISTRATION_ADDRESS, REGISTRATION_ADDRESS + len(REGISTRATION_BYTES)
    )
    if registration != REGISTRATION_BYTES:
        raise ValueError(f"unexpected remove-ring registration: {registration.hex()}")
    if branch_addresses(image, base, FLAG_SETTER) != EXPECTED_FLAG_SETTER_BRANCHES:
        raise ValueError("unexpected glasses-flag setter callers")
    if branch_addresses(image, base, PEER_SETTER) != EXPECTED_PEER_SETTER_BRANCHES:
        raise ValueError("unexpected peer-slot setter callers")
    if branch_addresses(image, base, PAYLOAD_HELPER) != EXPECTED_PAYLOAD_HELPER_BRANCHES:
        raise ValueError("unexpected payload-helper callers")
    if direct_thumb_branches_to(image, base, HANDLER_START):
        raise ValueError("table-dispatched remove-ring handler acquired a direct branch")
    handler_response_calls = [
        address for address in branch_addresses(image, base, RESPONSE_HELPER)
        if HANDLER_START <= address < HANDLER_END
    ]
    if handler_response_calls != [0x000844CE]:
        raise ValueError(f"unexpected remove-ring response calls: {handler_response_calls}")
    marker = flash_bytes(image, base, 0x000738F0, 0x000738F4)
    if marker != b"CAMH":
        raise ValueError(f"unexpected peer marker: {marker!r}")

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": verified,
        "registration": {
            "address": f"0x{REGISTRATION_ADDRESS:08x}",
            "system_subcommand": "0x82",
            "handler_thumb": "0x000844b1",
            "raw_hex": registration.hex(),
        },
        "payload_gate": {
            "declared_frame_length_offset": 8,
            "header_bytes": 12,
            "only_non_destructive_declared_length": 12,
            "every_other_declared_length_is_treated_as_payload_present": True,
            "minimum_payload_length_checked": False,
            "payload_contents_read": False,
        },
        "accepted_route_order": [
            "emit empty success response for system 0x82 with request serial",
            "clear dev_info settings bit 2 and synchronously store the class snapshot",
            "replace both six-byte peer slots with FF and marker with CAMH",
            "synchronously store the class snapshot again",
        ],
        "state_effect": {
            "settings_flag_mask_cleared": "0x04",
            "peer_slot_a_hex": "ffffffffffff",
            "peer_slot_b_hex": "ffffffffffff",
            "peer_marker_ascii": "CAMH",
            "synchronized_snapshot_writes": 2,
            "response_precedes_state_changes": True,
            "setter_results_observed_by_handler": False,
        },
        "classification": {
            "read_only": False,
            "identity_and_pairing_metadata_destructive": True,
            "safe_live_sender_should_be_exposed": False,
        },
        "complete_direct_branch_sets": {
            "flag_setter": [f"0x{value:08x}" for value in EXPECTED_FLAG_SETTER_BRANCHES],
            "peer_setter": [f"0x{value:08x}" for value in EXPECTED_PEER_SETTER_BRANCHES],
            "payload_helper": [f"0x{value:08x}" for value in EXPECTED_PAYLOAD_HELPER_BRANCHES],
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "flash_access": False,
            "pairing_state_mutation": False,
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
