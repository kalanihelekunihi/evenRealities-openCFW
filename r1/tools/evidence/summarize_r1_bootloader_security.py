#!/usr/bin/env python3
"""Report version-pinned R1 bootloader signature and boot-validation evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import zlib
from pathlib import Path
from typing import Any


PROFILES: dict[str, dict[str, Any]] = {
    "566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b": {
        "name": "B210_live_retail_normal_2026-08-10",
        "image_bytes": 24_576,
        "public_key_offset": 0x5868,
        "public_key_source_literal_offset": 0x26EC,
        "boot_validation_offset": 0x3B76,
        "prevalidation_offset": 0x3D68,
        "signature_check_offset": 0x3DB0,
        "settings_merge_offset": 0x3A2E,
        "adv_name_valid_offset": 0x3930,
        "gap_params_offset": 0x2B04,
        "advertising_init_offset": 0x1CAC,
        "boot_mode": "normal_application_or_dfu",
        "application_start_reachable": True,
    },
    "e049131a92c203e1c1f0abb067653e046c6955157e522914556004402f29ac60": {
        "name": "B210_BL_DFU_NO_v2.0.3.0004",
        "image_bytes": 24_420,
        "public_key_offset": 0x5868,
        "public_key_source_literal_offset": 0x26EC,
        "boot_validation_offset": 0x3B76,
        "prevalidation_offset": 0x3D68,
        "signature_check_offset": 0x3DB0,
        "settings_merge_offset": 0x3A2E,
        "adv_name_valid_offset": 0x3930,
        "gap_params_offset": 0x2B04,
        "advertising_init_offset": 0x1CAC,
        "boot_mode": "normal_application_or_dfu",
        "application_start_reachable": True,
    },
    "67cc2e9d3f70ea00e8246fe5715fd48067d6825a11425fa2a3c73bc9fc383714": {
        "name": "B210_ALWAY_BL_DFU_NO",
        "image_bytes": 24_180,
        "public_key_offset": 0x577C,
        "boot_validation_offset": 0x3A8A,
        "prevalidation_offset": 0x3C7C,
        "signature_check_offset": 0x3CC4,
        "settings_merge_offset": 0x3942,
        "adv_name_valid_offset": 0x3844,
        "gap_params_offset": 0x2AF8,
        "advertising_init_offset": 0x1CAC,
        "boot_mode": "always_dfu_service_or_recovery",
        "application_start_reachable": False,
    },
}

# Raw little-endian X || Y bytes embedded in both recovered bootloaders. This is
# a public verification key, not secret material.
EXPECTED_R1_PUBLIC_KEY = bytes.fromhex(
    "9d1156448bb5b73f5e36c6dcacb549918b82f9bd8981171033de5eb904e37d7a"
    "98a30f9fc447d76df6f195633c7f3e81301a5084815be517a4a604dfc9423455"
)

# Public key shipped in SDK 17's explicitly insecure/debug Secure DFU example.
SDK17_INSECURE_EXAMPLE_PUBLIC_KEY = bytes.fromhex(
    "357f66a396f29bde409081f2bf6f2a6b511a41bc612f73be16e6dcab207aabf8"
    "8392b8c447e763b9848330e8505e399674d89c3e1e881d1859d90d2b4713b21e"
)

# nrf_dfu_validation_boot_validate() through the CRC call. The relative BL itself
# differs between linked variants, so the call instruction is deliberately omitted.
BOOT_VALIDATION_PREFIX = bytes.fromhex(
    "38b5144602780b466ab1012a04d0022a0bd0032a19d110e0d0f80150002221461846"
)
BOOT_VALIDATION_UNCONDITIONAL_SUCCESS = bytes.fromhex("012038bd")

# nrf_dfu_validation_prevalidate() has no firmware-type/signature-required branch:
# it prepares either the signed-command fields or zero/null defaults, then calls the
# signature checker and requires its return value to equal success (1).
PREVALIDATION_PREFIX = bytes.fromhex(
    "38b50f4c251d002094f86c31014602463bb194f8d802b4f8da2204f5b87504f53771"
)
PREVALIDATION_AFTER_SIGNATURE_CALL = bytes.fromhex("012804d1")

# Beginning of nrf_dfu_validation_signature_check(). This includes the two explicit
# rejection branches: null signature -> 0x13 and non-ECDSA type -> 0x16.
SIGNATURE_CHECK_PREFIX = bytes.fromhex(
    "2de9f041ccb0064620200d464a901f461446ddf848817c212ba8"
)
SIGNATURE_CHECK_REJECTIONS = bytes.fromhex("25b12eb11620")

# nrf_bootloader_debug_port_disable() in nRF5 SDK 17 references these absolute
# UICR addresses when compiled for nRF52840. Their absence is version-pinned
# supporting evidence that NRF_BL_DEBUG_PORT_DISABLE was disabled. A physical
# device may still have APPROTECT provisioned by a separate manufacturing step.
UICR_DEBUG_ADDRESSES = {
    "uicr_base": 0x10001000,
    "approtect": 0x10001208,
    "debugctrl": 0x10001210,
}

# Exact compiled settings merge used by all recovered variants. The two BL
# instructions differ after linking, so they are checked around rather than as
# part of the signatures. These copies restore [0x04, 0x58) and
# [0x5c, 0x324) from the protected backup page. In particular they cover the
# write offset at 0x30, DFU progress at 0x38, and stored init command at 0x5c.
SETTINGS_MERGE_PREFIX = bytes.fromhex("5422311d281d")
SETTINGS_MERGE_SUFFIX = bytes.fromhex("4ff4327206f15c0105f15c00")

# nrf_dfu_settings_adv_name_is_valid() computes CRC32 across the fixed 24-byte
# name-plus-length body and compares it with the stored CRC. The four-byte BL
# between these fragments is link-dependent. There is no comparison of the
# trailing uint32_t length with the 20-byte name array.
ADV_NAME_VALID_PREFIX = bytes.fromhex("10b5064c00221821201d")
ADV_NAME_VALID_SUFFIX = bytes.fromhex("2168814201d1012010bd002010bd")

# gap_params_init() selects m_adv_name.len directly when the application-set
# advertising-name flag is present. The tail converts it to the SoftDevice's
# uint16_t ABI and invokes sd_ble_gap_device_name_set (SVC 0x7c), with no cap
# between the load and call. advertising_init() independently supplies a
# 22-byte output buffer to sd_ble_gap_device_name_get (SVC 0x7d).
ADV_NAME_LEN_LOAD = bytes.fromhex("007a800701d5a569")
ADV_NAME_SET_SVC = bytes.fromhex("aab2414602a87cdf")
ADV_NAME_GET_22_BYTE_PREFIX = bytes.fromhex(
    "70b588b005461620adf800000e4601a86ddf"
)


def _matches(image: bytes, offset: int, expected: bytes) -> bool:
    return image[offset : offset + len(expected)] == expected


def _reverse_coordinates(public_key: bytes) -> bytes:
    return public_key[:32][::-1] + public_key[32:][::-1]


def _read_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while offset < len(data) and shift < 70:
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte & 0x80 == 0:
            return value, offset
        shift += 7
    raise ValueError("truncated or oversized protobuf varint")


def _protobuf_fields(data: bytes) -> dict[int, list[int | bytes]]:
    fields: dict[int, list[int | bytes]] = {}
    offset = 0
    while offset < len(data):
        key, offset = _read_varint(data, offset)
        number = key >> 3
        wire_type = key & 7
        if number == 0:
            raise ValueError("protobuf field zero is invalid")
        if wire_type == 0:
            value, offset = _read_varint(data, offset)
        elif wire_type == 2:
            length, offset = _read_varint(data, offset)
            end = offset + length
            if end > len(data):
                raise ValueError("truncated protobuf field")
            value = data[offset:end]
            offset = end
        else:
            raise ValueError(f"unsupported protobuf wire type {wire_type}")
        fields.setdefault(number, []).append(value)
    return fields


def _bytes_field(fields: dict[int, list[int | bytes]], number: int) -> bytes:
    values = fields.get(number, [])
    if not values or not isinstance(values[0], bytes):
        raise ValueError(f"missing byte field {number}")
    return values[0]


def _int_field(fields: dict[int, list[int | bytes]], number: int) -> int:
    values = fields.get(number, [])
    if not values or not isinstance(values[0], int):
        raise ValueError(f"missing integer field {number}")
    return values[0]


def _optional_int_field(
    fields: dict[int, list[int | bytes]], number: int
) -> int | None:
    values = fields.get(number, [])
    if not values:
        return None
    if not isinstance(values[0], int):
        raise ValueError(f"field {number} is not an integer")
    return values[0]


def verify_init_packet(path: Path, public_key: bytes) -> dict[str, Any]:
    """Verify a Nordic signed init command with the recovered public key."""
    packet_data = path.read_bytes()
    packet = _protobuf_fields(packet_data)
    signed_command = _protobuf_fields(_bytes_field(packet, 2))
    command = _protobuf_fields(_bytes_field(signed_command, 1))
    init_command = _bytes_field(command, 2)
    init_fields = _protobuf_fields(init_command)
    signature = _bytes_field(signed_command, 3)
    signature_type = _int_field(signed_command, 2)
    debug_value = _optional_int_field(init_fields, 9)
    result: dict[str, Any] = {
        "init_packet": str(path),
        "init_packet_sha256": hashlib.sha256(packet_data).hexdigest(),
        "init_command_sha256": hashlib.sha256(init_command).hexdigest(),
        "firmware_version": _optional_int_field(init_fields, 1),
        "hardware_version": _optional_int_field(init_fields, 2),
        "firmware_type": _optional_int_field(init_fields, 4),
        "debug_field_present": debug_value is not None,
        "debug": bool(debug_value) if debug_value is not None else False,
        "signature_type": signature_type,
        "signature_bytes": len(signature),
        "verification_key_sha256": hashlib.sha256(public_key).hexdigest(),
    }
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec, utils
    except ImportError:
        result["ecdsa_p256_sha256_verified"] = None
        result["verification_error"] = "Python package 'cryptography' is unavailable"
        return result

    if len(public_key) != 64 or len(signature) != 64 or signature_type != 0:
        result["ecdsa_p256_sha256_verified"] = False
        result["verification_error"] = "unexpected key, signature length, or signature type"
        return result

    x = int.from_bytes(public_key[:32], "little")
    y = int.from_bytes(public_key[32:], "little")
    r = int.from_bytes(signature[:32], "little")
    s = int.from_bytes(signature[32:], "little")
    try:
        verifier = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()
    except ValueError as error:
        result["ecdsa_p256_sha256_verified"] = False
        result["verification_error"] = f"invalid P-256 public key: {error}"
        return result
    der_signature = utils.encode_dss_signature(r, s)
    try:
        verifier.verify(der_signature, init_command, ec.ECDSA(hashes.SHA256()))
        result["ecdsa_p256_sha256_verified"] = True
    except InvalidSignature:
        result["ecdsa_p256_sha256_verified"] = False
    return result


def summarize_settings(path: Path) -> dict[str, Any]:
    """Validate the security-bearing prefix of an SDK 17 DFU settings page."""
    data = path.read_bytes()
    if len(data) < 0x380:
        raise ValueError(f"settings capture {path} is shorter than 0x380 bytes")

    def word(offset: int) -> int:
        return int.from_bytes(data[offset : offset + 4], "little")

    settings_crc = zlib.crc32(data[0x04:0x5C]) & 0xFFFFFFFF
    boot_validation_crc = zlib.crc32(data[0x260:0x323]) & 0xFFFFFFFF
    settings_crc_valid = word(0x00) == settings_crc
    boot_validation_crc_valid = word(0x25C) == boot_validation_crc
    return {
        "image": str(path),
        "image_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "settings_structure_sha256": hashlib.sha256(data[:0x380]).hexdigest(),
        "settings_version": word(0x04),
        "application_version": word(0x08),
        "bootloader_version": word(0x0C),
        "bank_0_code": f"0x{word(0x20):08x}",
        "bank_1_code": f"0x{word(0x2C):08x}",
        "write_offset": f"0x{word(0x30):08x}",
        "stored_settings_crc": f"0x{word(0x00):08x}",
        "calculated_settings_crc": f"0x{settings_crc:08x}",
        "settings_crc_valid": settings_crc_valid,
        "stored_boot_validation_crc": f"0x{word(0x25C):08x}",
        "calculated_boot_validation_crc": f"0x{boot_validation_crc:08x}",
        "boot_validation_crc_valid": boot_validation_crc_valid,
        "protected_settings_state_valid": (
            settings_crc_valid and boot_validation_crc_valid
        ),
    }


def summarize(path: Path) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    profile = PROFILES.get(digest)
    result: dict[str, Any] = {
        "image": str(path),
        "image_bytes": len(image),
        "sha256": digest,
        "known_r1_bootloader": profile is not None,
    }
    if profile is None:
        result["conclusion"] = "unknown image; version-pinned checks were not applied"
        return result

    boot_offset = profile["boot_validation_offset"]
    prevalidation_offset = profile["prevalidation_offset"]
    signature_offset = profile["signature_check_offset"]
    settings_merge_offset = profile["settings_merge_offset"]
    adv_name_valid_offset = profile["adv_name_valid_offset"]
    gap_params_offset = profile["gap_params_offset"]
    advertising_init_offset = profile["advertising_init_offset"]
    public_key_offset = profile["public_key_offset"]
    public_key = image[public_key_offset : public_key_offset + 64]
    public_key_source_literal_offset = profile.get("public_key_source_literal_offset")
    crc_call_end = boot_offset + len(BOOT_VALIDATION_PREFIX) + 4
    prevalidation_call_end = prevalidation_offset + 0x2A + 4

    crc_path_computes_then_accepts = (
        _matches(image, boot_offset, BOOT_VALIDATION_PREFIX)
        and _matches(
            image,
            crc_call_end,
            BOOT_VALIDATION_UNCONDITIONAL_SUCCESS,
        )
    )
    signature_prevalidation_unconditional = (
        _matches(image, prevalidation_offset, PREVALIDATION_PREFIX)
        and _matches(
            image,
            prevalidation_call_end,
            PREVALIDATION_AFTER_SIGNATURE_CALL,
        )
    )
    missing_or_wrong_signature_rejected = (
        _matches(image, signature_offset, SIGNATURE_CHECK_PREFIX)
        and _matches(
            image,
            signature_offset + 0x2A,
            SIGNATURE_CHECK_REJECTIONS,
        )
    )
    protected_settings_merge = (
        _matches(image, settings_merge_offset, SETTINGS_MERGE_PREFIX)
        and _matches(image, settings_merge_offset + 10, SETTINGS_MERGE_SUFFIX)
    )
    adv_name_crc_without_length_bound = (
        _matches(image, adv_name_valid_offset, ADV_NAME_VALID_PREFIX)
        and _matches(image, adv_name_valid_offset + 14, ADV_NAME_VALID_SUFFIX)
    )
    adv_name_len_reaches_softdevice_uncapped = (
        _matches(image, gap_params_offset + 0x3C, ADV_NAME_LEN_LOAD)
        and _matches(image, gap_params_offset + 0xC0, ADV_NAME_SET_SVC)
    )
    advertising_get_uses_22_byte_buffer = _matches(
        image, advertising_init_offset, ADV_NAME_GET_22_BYTE_PREFIX
    )
    uicr_debug_address_literals = {
        name: image.find(address.to_bytes(4, "little")) >= 0
        for name, address in UICR_DEBUG_ADDRESSES.items()
    }
    # The prevalidation gate is `cmp r0, #1; bne reject`. On the recovered
    # normal image the conditional branch begins at +0x30. Flipping only the
    # low condition bit changes BNE (0xd1) to BEQ (0xd0). That is a one-way
    # 1->0 flash transition, but the containing bootloader page is ACL-protected
    # before the application runs; this is a theoretical patch descriptor, not
    # a write primitive.
    signature_gate_offset = prevalidation_offset + 0x30
    signature_gate_address = 0xF8000 + signature_gate_offset
    signature_gate_original = image[signature_gate_offset : signature_gate_offset + 2]
    signature_gate_fail_open = bytes([signature_gate_original[0], signature_gate_original[1] & 0xFE])
    signature_gate_word_offset = signature_gate_offset & ~3
    signature_gate_original_word = int.from_bytes(
        image[signature_gate_word_offset : signature_gate_word_offset + 4], "little"
    )
    signature_gate_fail_open_word = signature_gate_original_word & ~(1 << 8)

    trust_root_substitution: dict[str, Any] | None = None
    if public_key_source_literal_offset is not None:
        public_key_source_pointer = int.from_bytes(
            image[
                public_key_source_literal_offset : public_key_source_literal_offset + 4
            ],
            "little",
        )
        public_key_source_literal_address = 0xF8000 + public_key_source_literal_offset
        trust_root_substitution = {
            "initializer_function": "0x000fa6b8",
            "source_literal_address": f"0x{public_key_source_literal_address:08x}",
            "source_literal_value": f"0x{public_key_source_pointer:08x}",
            "source_points_to_embedded_key": (
                public_key_source_pointer == 0xF8000 + public_key_offset
            ),
            "runtime_key_object": "0x20008cc4",
            "fp_ctrl_reset": "0x00000260",
            "instruction_comparators": 6,
            "literal_comparators": 2,
            "literal_comparator": 6,
            "fp_comp6_address": "0xe0002020",
            "fp_comp6_value": f"0x{public_key_source_literal_address | 1:08x}",
            "retained_remap_base": "0x2003c000",
            "remap_table_entry": "0x2003c018",
            "replacement_key_address": "0x2003c040",
            "direct_runtime_object_seeding_survives_startup": False,
            "hardware_retention_tested": False,
        }

    result.update(
        {
            "profile": profile["name"],
            "boot_mode": profile["boot_mode"],
            "application_start_reachable": profile["application_start_reachable"],
            "expected_image_bytes": profile["image_bytes"],
            "expected_size": len(image) == profile["image_bytes"],
            "embedded_public_key_address": f"0x{0xF8000 + public_key_offset:08x}",
            "embedded_public_key_sha256": hashlib.sha256(public_key).hexdigest(),
            "embedded_public_key_matches_expected_r1_key": (
                public_key == EXPECTED_R1_PUBLIC_KEY
            ),
            "matches_sdk17_insecure_example_public_key": public_key
            in {
                SDK17_INSECURE_EXAMPLE_PUBLIC_KEY,
                _reverse_coordinates(SDK17_INSECURE_EXAMPLE_PUBLIC_KEY),
            },
            "boot_validation_function": f"0x{0xF8000 + boot_offset:08x}",
            "crc_path_computes_then_returns_true_without_comparison": (
                crc_path_computes_then_accepts
            ),
            "nrf_dfu_debug_behavior_present": crc_path_computes_then_accepts,
            "prevalidation_function": f"0x{0xF8000 + prevalidation_offset:08x}",
            "signature_check_is_unconditional_in_prevalidation": (
                signature_prevalidation_unconditional
            ),
            "missing_or_wrong_signature_has_explicit_rejection_paths": (
                missing_or_wrong_signature_rejected
            ),
            "settings_backup_merge": {
                "function_address": f"0x{0xF8000 + settings_merge_offset - 0x56:08x}",
                "protected_copy_ranges": ["0x04..0x57", "0x5c..0x323"],
                "write_offset_0x30_restored_from_backup": protected_settings_merge,
                "dfu_progress_0x38_restored_from_backup": protected_settings_merge,
                "stored_init_command_0x5c_restored_from_backup": protected_settings_merge,
                "application_controlled_enter_buttonless_0x58_only": protected_settings_merge,
                "ace_resume_state_poisoning_blocked": protected_settings_merge,
                "valid_primary_with_invalid_backup_is_accepted_without_merge": True,
                "conditional_backup_fault_can_seed_protected_bank_state": True,
                "application_acl_blocks_direct_backup_invalidation": True,
                "software_only_backup_fault_chain_found": False,
            },
            "application_controlled_advertising_name": {
                "settings_offset": "0x364",
                "record_layout": "crc32 + name[20] + uint32_len",
                "validity_function": f"0x{0xF8000 + adv_name_valid_offset:08x}",
                "crc_validity_has_no_len_le_20_check": adv_name_crc_without_length_bound,
                "gap_params_function": f"0x{0xF8000 + gap_params_offset:08x}",
                "unchecked_len_reaches_device_name_set": (
                    adv_name_len_reaches_softdevice_uncapped
                ),
                "advertising_get_output_capacity": 22,
                "advertising_get_capacity_confirmed": advertising_get_uses_22_byte_buffer,
                "maximum_advertisable_oob_read_bytes": 2,
                "direct_write_or_control_flow_primitive": False,
                "signing_bypass_chain_found": False,
            },
            "theoretical_signature_gate_patch": {
                "branch_address": f"0x{signature_gate_address:08x}",
                "branch_original_bytes": signature_gate_original.hex(),
                "branch_fail_open_bytes": signature_gate_fail_open.hex(),
                "byte_address": f"0x{signature_gate_address + 1:08x}",
                "byte_transition": (
                    f"0x{signature_gate_original[1]:02x}->"
                    f"0x{signature_gate_fail_open[1]:02x}"
                ),
                "aligned_word_address": f"0x{0xF8000 + signature_gate_word_offset:08x}",
                "aligned_word_original": f"0x{signature_gate_original_word:08x}",
                "aligned_word_fail_open": f"0x{signature_gate_fail_open_word:08x}",
                "only_clears_flash_bits": (
                    signature_gate_fail_open_word & signature_gate_original_word
                ) == signature_gate_fail_open_word,
                "normal_application_acl_blocks_programming": True,
            },
            "theoretical_trust_root_substitution": trust_root_substitution,
            "unsigned_secure_dfu_bypass_found": False,
            # These conclusions are tied to the exact hashes above and were
            # recovered by matching/decompiling the corresponding SDK paths.
            "dfu_ble_transport_requires_bond": False,
            "signed_debug_init_skips_compatibility_checks": True,
            "non_debug_application_downgrade_prevention": True,
            "non_debug_application_same_version_accepted": True,
            "uicr_debug_address_literals_present": uicr_debug_address_literals,
            "bootloader_debug_port_disable_sequence_observed": all(
                uicr_debug_address_literals[name]
                for name in ("approtect", "debugctrl")
            ),
            "physical_approtect_state_determined_from_image": False,
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument(
        "--init-packet",
        action="append",
        default=[],
        type=Path,
        help="also verify a recovered Nordic .dat init packet (repeatable)",
    )
    parser.add_argument(
        "--settings-backup",
        type=Path,
        help="also validate a complete or security-prefix DFU settings backup capture",
    )
    parser.add_argument(
        "--settings-primary",
        type=Path,
        help="also validate a complete or security-prefix primary DFU settings capture",
    )
    args = parser.parse_args()
    image_summaries = [summarize(path) for path in args.images]
    result: dict[str, Any] = {"bootloaders": image_summaries}
    if args.init_packet:
        known_keys = {
            image[profile["public_key_offset"] : profile["public_key_offset"] + 64]
            for path in args.images
            if (profile := PROFILES.get(hashlib.sha256((image := path.read_bytes())).hexdigest()))
        }
        if not known_keys:
            raise SystemExit("no known R1 bootloader was supplied as a verification key source")
        if len(known_keys) != 1:
            raise SystemExit("supplied bootloaders do not contain the same verification key")
        public_key = known_keys.pop()
        result["init_packets"] = [
            verify_init_packet(path, public_key) for path in args.init_packet
        ]
    settings: dict[str, Any] = {}
    if args.settings_backup:
        settings["backup"] = summarize_settings(args.settings_backup)
    if args.settings_primary:
        settings["primary"] = summarize_settings(args.settings_primary)
    if "backup" in settings and "primary" in settings:
        backup = args.settings_backup.read_bytes()[:0x380]
        primary = args.settings_primary.read_bytes()[:0x380]
        settings["full_settings_structures_equal"] = backup == primary
        settings["conditional_invalid_backup_prerequisite_present"] = not bool(
            settings["backup"]["protected_settings_state_valid"]
        )
    if settings:
        result["live_settings"] = settings
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
