#!/usr/bin/env python3
"""Validate the R1 public user-profile command and GoMore profile transition path.

The parser is static and read-only. It reports the production gender-map/validation mismatch,
acknowledgment ordering, uninitialized internal tail, persistence thresholds, and first-party AOT
sender shape without sending a profile or exposing a state-changing command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset


SYSTEM_TABLE_ENTRY = 0x0009A4E4
EXPECTED_IDENTIFIER = 0x0004
EXPECTED_HANDLER_THUMB = 0x00084A11

FUNCTION_SIGNATURES = {
    0x00082BD4: "01890c390904090c01d00c3070470020",  # payload pointer iff frame != 12 bytes
    0x00084A10: "70b5064686b00d460846fef7dbf8040004d0",  # public userInfo handler
    0x000425B0: "f0b587b00c297dd1044603a831f010f8",  # exact-12 internal event consumer
    0x0006C640: (
        "01780a290ed964290cd24178012909d88178642906d9dc2904d2c0781e2801d9962801d3"
        "0020704701207047"
    ),
    0x0006C66C: "70b5002818d0002916d005460c460846fff7e0ff00280fd00c2221462846bbf7c6f8",
    0x0006C53C: "10b5002200283fd000293dd00b7804781b1b9b1c042b00d901224b784478a34200d00122",
    0x000735E0: "3eb504000bd006480c226946006800f09ff9",  # read old 12-byte profile
    0x00073604: "3eb5040010d0094d0c226946286800f08df9",  # persist new 12-byte profile
    0x0004C37C: "0b4810b590f84000c00703d000210420fdf740f8",  # reinitialize GoMore engine
}

CALLSITE_SIGNATURES = {
    # ACK success, map gender 0->1/nonzero->2, truncate UInt16 height/weight to low bytes,
    # initialize three Int16 parameters to -1, leave event bytes 10...11 untouched, publish 12.
    0x00084A8A: (
        "00200090b5f80330012204213046fdf7f0fe60788df80c002078b8b102208df80d00"
        "a0788df80e0020798df80f004ff0ff30adf81000adf81200adf814000c2203a941f20a"
        "0008f014ffb3e7"
    ),
    # Internal consumer passes old/new records into the validated persistence transition.
    0x00042704: "214603a829f0b0ff",
    # Valid and changed records persist before the significance/reinitialization tail call.
    0x0006C692: "204606f0b6ff21462846bde87040fff74cbf",
    # Significant demographic changes tail into the GoMore reinitializer.
    0x0006C5B0: "032101eb004015a10df002fabde81040dff7dcbe",
}


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def require_prefix(image: bytes, base: int, address: int, expected_hex: str) -> None:
    expected = bytes.fromhex(expected_hex)
    actual = flash_bytes(image, base, address, len(expected))
    if actual != expected:
        raise ValueError(
            f"unexpected bytes at 0x{address:08x}: {actual.hex()} != {expected.hex()}"
        )


def audit_first_party(root: Path | None) -> dict[str, Any]:
    if root is None:
        return {"audited": False}
    variants = []
    for corpus in ("blutter_output_2.2.0", "blutter_output"):
        base = root / "firmware" / corpus / "asm"
        serializer = base / "even_connect/ring1/models/system/ble_ring1_system_user_info.dart"
        sender = base / "even_connect/ring1/ble_ring1_cmd_proto.dart"
        home = base / "even/pages/main_screen/tab_page/home/home_controller.dart"
        if not serializer.is_file() or not sender.is_file() or not home.is_file():
            raise ValueError(f"missing first-party user-profile evidence in {corpus}")
        serializer_text = serializer.read_text(errors="replace")
        sender_text = sender.read_text(errors="replace")
        home_text = home.read_text(errors="replace")
        required_serializer_markers = (
            "r4 = 24",
            "strb",
            "strh",
            "BleRing1SystemUserInfo::toBytes",
        )
        if not all(marker in serializer_text for marker in required_serializer_markers):
            raise ValueError(f"unexpected first-party serializer shape in {corpus}")
        if "_ setUserInfo" not in sender_text or "BleRing1SystemUserInfo()" not in sender_text:
            raise ValueError(f"missing first-party typed sender in {corpus}")
        if "HomeCtlPublicExt.updateRing1UserInfo" not in home_text:
            raise ValueError(f"missing first-party profile synchronization in {corpus}")
        variants.append({
            "corpus": corpus,
            "typed_sender_found": True,
            # Dart AOT stores Smis shifted left by one. The literal text `r4 = 24` passed to
            # AllocateUint8Array therefore represents 12 elements, not 24.
            "canonical_payload_bytes": 12,
            "public_gender_codes": [0, 1, 2],
            "trailing_algorithm_words_zero": True,
        })
    return {
        "audited": True,
        "typed_sender_found_in_all_variants": True,
        "variants": variants,
    }


def summarize(image_path: Path, base: int, first_party_root: Path | None) -> dict[str, Any]:
    image = image_path.read_bytes()
    identifier, handler_thumb = struct.unpack(
        "<II", flash_bytes(image, base, SYSTEM_TABLE_ENTRY, 8)
    )
    if identifier != EXPECTED_IDENTIFIER or handler_thumb != EXPECTED_HANDLER_THUMB:
        raise ValueError(
            f"unexpected userInfo registration: 0x{identifier:04x}/0x{handler_thumb:08x}"
        )
    for address, signature in FUNCTION_SIGNATURES.items():
        require_prefix(image, base, address, signature)
    for address, signature in CALLSITE_SIGNATURES.items():
        require_prefix(image, base, address, signature)

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "public_command": {
            "module": "0x01",
            "command": "0x00",
            "subcommand": "0x04",
            "registration_entry": f"0x{SYSTEM_TABLE_ENTRY:08x}",
            "handler": f"0x{EXPECTED_HANDLER_THUMB & ~1:08x}",
            "canonical_first_party_payload_bytes": 12,
            "minimum_memory_safe_payload_bytes": 6,
            "zero_payload_returns_failure_ack": True,
            "one_through_five_payload_bytes_are_not_rejected_before_field_reads": True,
            "trailing_payload_bytes_ignored": True,
            "ack_success_sent_before_internal_validation_and_persistence": True,
            "ack_success_proves_persistence": False,
        },
        "public_to_internal_mapping": {
            "public_fields": [
                "gender U8 @0", "age U8 @1", "height UInt16LE @2", "weight UInt16LE @4",
            ],
            "internal_event": "0x100a",
            "internal_event_bytes": 12,
            "internal_fields": [
                "age U8 @0", "binary sex U8 @1", "height low byte @2", "weight low byte @3",
                "algorithm parameter A Int16LE=-1 @4", "parameter B=-1 @6",
                "parameter C=-1 @8", "uninitialized stack tail @10...11",
            ],
            "public_gender_zero_maps_to_internal_sex": 1,
            "every_nonzero_public_gender_maps_to_internal_sex": 2,
            "height_and_weight_are_truncated_to_low_byte": True,
            "internal_tail_bytes_initialized_by_public_handler": False,
        },
        "internal_validation": {
            "age_years_inclusive": [11, 99],
            "accepted_internal_sex_values": [0, 1],
            "height_centimeters_inclusive": [101, 219],
            "weight_kilograms_inclusive": [31, 149],
            "only_public_gender_zero_maps_to_an_accepted_internal_sex": True,
            "invalid_internal_record_is_silently_not_persisted_after_success_ack": True,
        },
        "persistence_and_reinitialization": {
            "full_record_bytes_compared": 12,
            "persist_only_when_valid_and_full_record_differs": True,
            "reinitialize_only_when_algorithm_is_initialized": True,
            "age_absolute_delta_threshold_exclusive": 2,
            "height_absolute_delta_threshold_exclusive": 9,
            "weight_absolute_delta_threshold_exclusive": 9,
            "any_internal_sex_change_is_significant": True,
            "profile_persistence_precedes_reinitialization": True,
        },
        "first_party_aot": audit_first_party(first_party_root),
        "safety": {
            "health_consent_required": True,
            "live_profile_sender_exposed": False,
            "private_event_sender_exposed": False,
            "static_parser_only": True,
        },
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    parser.add_argument("--first-party-root", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(summarize(
        arguments.image,
        arguments.base,
        arguments.first_party_root,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
