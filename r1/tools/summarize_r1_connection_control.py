#!/usr/bin/env python3
"""Pin production pairAuth and two-target advStart connection-control routes.

This analyzer reads only the supplied firmware image. It does not open BLE, pair, disconnect,
change advertising, access live role state, or contact a physical ring or glasses.
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
        0x000842EC,
        0x0008436C,
        "bf7918d4f64b7964ffe167052b255f875718da3489deea003063b60aac099141",
        "pairAuth handler",
    ),
    (
        0x00083D04,
        0x00083D5A,
        "435f50237fe6a1501c14ba62cab220e522d4820e706a6302b721ffcdb3dbfb95",
        "advStart handler",
    ),
    (
        0x00082BD4,
        0x00082BE6,
        "1f0181948d602c0210ecae853b284d17e6b01d0e14a901c8b6548d03d81c9dac",
        "payload-presence helper",
    ),
    (
        0x0004DA28,
        0x0004DBD6,
        "51bdbf6412fad98d89416e28326a3735035b9d2e1b8c30d8d2c2edec3c93230e",
        "phone-role connection assignment",
    ),
    (
        0x00033850,
        0x00033982,
        "034f58f9537b96a7c9f0c0ff0c78924bb810dd8a5984bca8d51c82b17b25ecdf",
        "BLE-thread event allocator and enqueue",
    ),
    (
        0x00045184,
        0x00045B16,
        "084b42ae5e9f0fd5e5c7942052086d26ab67b547a666b87c7fcf8982858bcac1",
        "BLE-thread pairAuth and advStart consumer",
    ),
    (
        0x0004D9B0,
        0x0004DA10,
        "b25b8d7adb24dc28f89701c9d66e5b176719c8972acb1c8398be7c6efaa6541a",
        "two-target glasses runtime and persistent address store",
    ),
    (
        0x000738A8,
        0x000738EC,
        "6dc2ff34388aa88c5b8888d90905dd91cd23723bc39aac3543d4660b9fcabd97",
        "dev_info two-target address setter",
    ),
    (
        0x0008287C,
        0x000828AE,
        "88936f6150f4b97dc7fc7a941ec07edc96ab5e8c933d4ad27167386862f1ba2f",
        "empty response builder",
    ),
    (
        0x00084C5E,
        0x00084C74,
        "e8b83041e691d1f113fbd84c9a87aefeba0d24c49a92ac93ae4d9578bea15da2",
        "payload response wrapper",
    ),
]

# Ghidra's executable-byte census excludes the literal/string islands embedded in
# the enclosing 0x45184..0x45b16 range.  Keep both measurements explicit: the
# complete range hash prevents silent evidence drift while the 1,736-byte value is
# the function-body amount removed from the ownership frontier.
R1_CONNECTION_CONTROL_FUNCTIONS = (
    {
        "entry": 0x00045184,
        "end_exclusive": 0x00045B16,
        "size": 1736,
        "extent_bytes": 0x00045B16 - 0x00045184,
        "symbol": "r1_ble_connection_control_event_consumer",
        "sha256": "084b42ae5e9f0fd5e5c7942052086d26ab67b547a666b87c7fcf8982858bcac1",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
)

PAIR_HANDLER = 0x000842EC
ADV_HANDLER = 0x00083D04
PAYLOAD_HELPER = 0x00082BD4
ROLE_SETTER = 0x0004DA28
EVENT_ENQUEUE = 0x00033850
EVENT_CONSUMER = 0x00045184
TARGET_STORE = 0x0004D9B0
PEER_SLOT_SETTER = 0x000738A8
EMPTY_RESPONSE = 0x0008287C
PAYLOAD_RESPONSE = 0x00084C5E
PEER_MANAGER_SECURE = 0x0007F294
FAST_ADVERTISE = 0x0004C81C
STOP_ADVERTISE = 0x0004C8F8
DISCONNECT = 0x0004E21C

PAIR_REGISTRATION = 0x0009A4FC
PAIR_REGISTRATION_BYTES = bytes.fromhex("08000000ed420800")
ADV_REGISTRATION = 0x0009A50C
ADV_REGISTRATION_BYTES = bytes.fromhex("0a000000053d0800")

EXPECTED_BRANCHES = {
    EVENT_CONSUMER: [0x00091FD2],
    ROLE_SETTER: [0x00084340],
    TARGET_STORE: [0x00045970, 0x00045ABE],
    PEER_SLOT_SETTER: [0x00046052, 0x0004D9E2, 0x000844E6],
    PEER_MANAGER_SECURE: [0x0003E040, 0x0004530E],
    DISCONNECT: [0x00045450, 0x000458FE],
    FAST_ADVERTISE: [0x000459FA, 0x0007F5EE, 0x00092006],
    STOP_ADVERTISE: [0x00045280, 0x00045A24, 0x0007F438, 0x00091FDA],
}


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


def checked_bytes(
    image: bytes,
    base: int,
    address: int,
    expected: bytes,
    label: str,
) -> str:
    actual = flash_bytes(image, base, address, address + len(expected))
    if actual != expected:
        raise ValueError(
            f"unexpected {label} at 0x{address:08x}: "
            f"{actual.hex()} != {expected.hex()}"
        )
    return actual.hex()


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    verified = [
        checked_range(image, base, start, end, sha, label)
        for start, end, sha, label in RANGES
    ]
    branches: dict[str, list[str]] = {}
    for target, expected in EXPECTED_BRANCHES.items():
        actual = branch_addresses(image, base, target)
        if actual != expected:
            raise ValueError(
                f"unexpected complete branch set for 0x{target:08x}: {actual}"
            )
        branches[f"0x{target:08x}"] = [
            f"0x{address:08x}" for address in actual
        ]

    payload_calls = branch_addresses(image, base, PAYLOAD_HELPER)
    pair_payload_calls = [
        address for address in payload_calls if PAIR_HANDLER <= address < 0x0008436C
    ]
    adv_payload_calls = [
        address for address in payload_calls if ADV_HANDLER <= address < 0x00083D5A
    ]
    if pair_payload_calls != [0x000842F4] or adv_payload_calls != [0x00083D0C]:
        raise ValueError("unexpected pairAuth/advStart payload-helper calls")
    enqueue_calls = branch_addresses(image, base, EVENT_ENQUEUE)
    if 0x0008434C not in enqueue_calls:
        raise ValueError("pairAuth no longer enqueues BLE event type 2")
    if branch_addresses(image, base, PAIR_HANDLER):
        raise ValueError("table-dispatched pairAuth handler acquired a direct branch")
    if branch_addresses(image, base, ADV_HANDLER):
        raise ValueError("table-dispatched advStart handler acquired a direct branch")

    registrations = [
        {
            "address": f"0x{PAIR_REGISTRATION:08x}",
            "system_subcommand": "0x08",
            "handler_thumb": "0x000842ed",
            "raw_hex": checked_bytes(
                image,
                base,
                PAIR_REGISTRATION,
                PAIR_REGISTRATION_BYTES,
                "pairAuth registration",
            ),
        },
        {
            "address": f"0x{ADV_REGISTRATION:08x}",
            "system_subcommand": "0x0a",
            "handler_thumb": "0x00083d05",
            "raw_hex": checked_bytes(
                image,
                base,
                ADV_REGISTRATION,
                ADV_REGISTRATION_BYTES,
                "advStart registration",
            ),
        },
    ]

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "ownership_closure": {
            "function_count": len(R1_CONNECTION_CONTROL_FUNCTIONS),
            "function_bytes": sum(
                int(item["size"]) for item in R1_CONNECTION_CONTROL_FUNCTIONS
            ),
            "extent_bytes": sum(
                int(item["extent_bytes"])
                for item in R1_CONNECTION_CONTROL_FUNCTIONS
            ),
            "functions": [
                {
                    **item,
                    "entry": f"0x{int(item['entry']):08x}",
                    "end_exclusive": f"0x{int(item['end_exclusive']):08x}",
                }
                for item in R1_CONNECTION_CONTROL_FUNCTIONS
            ],
        },
        "verified_ranges": verified,
        "registrations": registrations,
        "complete_direct_branch_sets": branches,
        "pair_auth": {
            "protocol_header_bytes": 12,
            "payload_present_rule": "declared frame length != 12",
            "minimum_payload_length_checked": False,
            "phone_type": 1,
            "handler_order": [
                "assign/check incoming session as phone role",
                "enqueue event type 2 with one-byte payload",
                "reply on incoming session with one zero byte",
            ],
            "glasses_role_conflict": "500-unit delay followed by assertion/fatal path",
            "handler_performs_cryptographic_challenge": False,
            "consumer_requests_peer_manager_security_when_not_encrypted": True,
            "peer_manager_tolerated_results": [0, 0x11],
            "unencrypted_timer": {"context": 1, "delay_raw": 0x3C00},
            "already_encrypted_timers": [
                {"context": 0, "delay_raw": 0x66},
                {"context": 0, "delay_raw": 0x800},
            ],
        },
        "advertise_start": {
            "protocol_header_bytes": 12,
            "required_payload_bytes": 12,
            "target_address_bytes_each": 6,
            "rejected_declared_lengths": list(range(12, 24)),
            "malformed_declared_lengths_accepted_by_uint16_wrap": list(range(0, 12)),
            "success_response_precedes_current_session_lookup_and_event_queue": True,
            "event_type": 0x200,
            "event_session_source": "current EUS session, not incoming session",
            "queue_or_allocation_failure_reflected_in_response": False,
            "consumer": {
                "connected_peer_matches_either_target": True,
                "mismatch_disconnect_delay_raw": 0x5000,
                "targets_stored_even_after_mismatch": True,
                "targets_persisted_to_dev_info_offsets": [8, 14],
                "persistent_target_bytes_each": 6,
                "persistent_setter": f"0x{PEER_SLOT_SETTER:08x}",
                "persistent_setter_complete_callers": {
                    "erase_both_during_connection_reset": "0x00046052",
                    "store_both_advStart_targets": "0x0004d9e2",
                    "erase_both_during_removeRingNotify": "0x000844e6",
                },
                "official_target_store_contains_phone_address": False,
                "firmware_assigns_right_left_semantics": False,
                "missing_phone_or_glasses_starts_fast_advertising_mode": 3,
                "both_connected_and_not_mismatched_stops_advertising": True,
            },
        },
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "pairing_or_role_mutation": False,
            "advertising_or_disconnect_mutation": False,
            "live_address_access": False,
        },
        "source_boundary": {
            "event_consumer": "r1_product_specific clean_room_behavior_only",
            "nordic_provider_calls": [
                "pm_conn_secure",
                "nrf_log_frontend_std_0",
                "nrf_log_frontend_std_1",
                "nrf_log_frontend_std_3",
            ],
            "rtos_provider_calls": ["osMessageQueueGet", "vPortFree"],
            "unclassified_callees_absorbed": False,
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
