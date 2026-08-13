#!/usr/bin/env python3
"""Validate and summarize the R1 kv.bin snapshot store and registered KV classes.

This is a static, read-only parser for application 2.2.6.0009. It never reads or mutates a ring,
and it reports only compiled class metadata rather than identity, health, or configuration values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import (
    DEFAULT_BASE,
    DEFAULT_SCATTER_LENGTH,
    DEFAULT_SCATTER_RUNTIME,
    DEFAULT_SCATTER_SOURCE,
    decompress_scatter,
    mapped_offset,
)


PARTITION_RECORD = 0x0009C250
PARTITION_BYTES = 0x2000
SECTOR_BYTES = 0x1000
SLOT_BYTES = 0x800
SLOT_COUNT = 4
CLASS_BLOCK_BYTES = 0x100
CLASS_HEADER_BYTES = 0x18
MAXIMUM_CLASSES = 8
PARTITION_MAGIC = 0x45503130
FALLBACK_MAGIC = 0xA5A5A5A5
STATE_RUNTIME = 0x20006978
CLASS_POINTER_TABLE_RUNTIME = 0x20007DE8

FUNCTION_SIGNATURES = {
    0x00094E3C: "feb5544c206818b95348e8f746fb2060",  # partition/wrapper init
    0x00057D0C: "70b588b0182101a8cff749fd234da868",  # startup sector scrub
    0x00064B24: "2de9f0433249334a3048891ac9088478",  # latest valid slot scan
    0x00095168: "2de9f04706463c48904688b042688a46",  # read latest snapshot
    0x00095304: "2de9f84f474c8146924660688b46b0b1",  # write current snapshot
    0x000731A0: "2de9f8431b4d281d00f0bcfb68680068",  # KV core/class init
    0x00073220: "2de9f84f6c4f1ef061f9c00703d11ef0",  # restore all classes
    0x000734E8: "2de9f8432248234f07e00168897cc907",  # synchronized snapshot store
    0x00091780: "70b50e460446818a1b4d1830ccf776f8",  # one-class record writer
    0x0005D87C: "30b503464ff6ff700022064c07e09d5c",  # CRC-16/MODBUS
    0x0005D8CC: "30b5044683230020024603e0a55c521c",  # hash131
    0x000735E0: "3eb504000bd006480c226946006800f0",  # health payload getter
    0x00073604: "3eb5040010d0094d0c226946286800f0",  # health payload setter
    0x00073694: "10b58eb0040009d00548342269460068",  # device power-state getter
    0x00073710: "30b58db0040017d00c4d342269462868",  # device power-state setter
    0x00073750: "10b5044607488eb034226946006800f0",  # device software-DCDC getter
    0x00073778: "00b506488db034226946006800f0d4f8",  # device glasses flag getter
    0x00073798: "30b5054609488db00c46342269460068",  # device health-setting getter
    0x00073800: "30b50b4d8db0044634226946286800f0",  # device software-DCDC setter
    0x00073834: "30b50b4d8db0044634226946286800f0",  # device glasses flag setter
    0x00073868: "70b50e4d8eb00e460446342269462868",  # device health-setting setter
    0x000738A8: "70b5104e8eb00c460546342269463068",  # two peer-slot setter
    0x000738F4: "002805d0014603481822406800f016b8",  # hsync getter
    0x0007390C: "002805d0014603481822406800f026b8",  # hsync setter
    0x0006ABF8: "3eb5040046d0684608f0eefc9df80000",  # health -> GoMore float profile
    0x0006C640: "01780a290ed964290cd24178012909d8",  # demographic validator
    0x0006C66C: "70b5002818d0002916d005460c460846",  # profile change/store path
    0x0007B634: "70b5040075487649a2b0a0eb01004fea",  # NV recovery record builder
    0x0007BB44: "08b50448042269460068f7f7effe9df8",  # power battery-type getter
    0x0007BB7C: "08b50448042269460068f7f7d3febdf9",  # power compensation getter
    0x0007BAC4: "08b50448012269468068f7f72fff9df8",  # ring-size getter
}

HSYNC_DIAGNOSTICS = {
    0x0008BE48: "[RING]activity_sync: last_sync(%u) > now(%u), self-heal clamp",
    0x0008C4A8: "[RING]hr_sync: last_sync(%u) > now(%u), self-heal clamp",
    0x0008CAA8: "[RING]hrv_sync: last_sync(%u) > now(%u), self-heal clamp",
    0x0008D0B8: "[RING]spo2_sync: last_sync(%u) > now(%u), self-heal clamp",
}

CLASS_METADATA = [
    (0, 0x200069A8, "dev_info", 52, 1, 0, True),
    (1, 0x200069F4, "ble_mult", 90, 1, 0, True),
    (2, 0x20006A68, "health", 12, 1, 0, True),
    (3, 0x20006A8C, "hsync", 24, 1, 0, True),
    (4, 0x20006ABC, "power", 4, 1, 2, False),
    (5, 0x20006AD8, "nv_r1", 124, 1, 2, True),
    (6, 0x20006B6C, "r_size", 1, 1, 2, False),
]


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


def flash_cstring(image: bytes, base: int, address: int) -> str:
    offset = mapped_offset(address, base, len(image))
    end = image.find(b"\0", offset)
    if end < 0:
        raise ValueError(f"unterminated string at 0x{address:08x}")
    return image[offset:end].decode("ascii")


def runtime_bytes(runtime: bytes, runtime_base: int, address: int, length: int) -> bytes:
    offset = address - runtime_base
    if offset < 0 or offset + length > len(runtime):
        raise ValueError(f"runtime range at 0x{address:08x} is outside scatter image")
    return runtime[offset:offset + length]


def runtime_word(runtime: bytes, runtime_base: int, address: int) -> int:
    return struct.unpack("<I", runtime_bytes(runtime, runtime_base, address, 4))[0]


def hash131(data: bytes) -> int:
    value = 0
    for byte in data:
        value = (value * 0x83 + byte) & 0xFFFFFFFF
    return value


def crc16_modbus(data: bytes) -> int:
    value = 0xFFFF
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0xA001 if value & 1 else 0)
    return value


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    for address, prefix in FUNCTION_SIGNATURES.items():
        require_prefix(image, base, address, prefix)
    for address, expected in HSYNC_DIAGNOSTICS.items():
        actual = flash_cstring(image, base, address)
        if actual != expected:
            raise ValueError(
                f"unexpected hsync diagnostic at 0x{address:08x}: {actual!r}"
            )

    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)

    partition = flash_bytes(image, base, PARTITION_RECORD, 0x40)
    if partition[:4] != b"01PE" or partition[4:11] != b"kv.bin\0":
        raise ValueError("unexpected kv.bin FAL record")
    if partition[0x1C:0x29] != b"device_flash\0":
        raise ValueError("unexpected kv.bin device name")
    partition_offset, partition_length, reserved = struct.unpack_from("<III", partition, 0x34)
    if (partition_offset, partition_length, reserved) != (0, PARTITION_BYTES, 0):
        raise ValueError("unexpected kv.bin partition geometry")

    state_words = [
        runtime_word(runtime, scatter_runtime, STATE_RUNTIME + offset)
        for offset in range(0, 0x28, 4)
    ]
    expected_state_words = [
        0, 0, 0,
        0x00094E3D, 0x00094E2D, 0x00095165, 0x00094DF1,
        0x00095169, 0x00095305, 0x00094DF5,
    ]
    if state_words != expected_state_words:
        raise ValueError("unexpected KV wrapper scatter state/operation table")

    pointers = [
        runtime_word(runtime, scatter_runtime, CLASS_POINTER_TABLE_RUNTIME + index * 4)
        for index in range(len(CLASS_METADATA))
    ]
    expected_pointers = [item[1] for item in CLASS_METADATA]
    if pointers != expected_pointers:
        raise ValueError("unexpected KV class pointer table")

    classes = []
    for index, address, name, payload_length, state, flags, sensitive in CLASS_METADATA:
        header = runtime_bytes(runtime, scatter_runtime, address, CLASS_HEADER_BYTES)
        fixed_name = name.encode().ljust(8, b"\0")
        if header[:4] != b"\0" * 4 or header[4:12] != fixed_name:
            raise ValueError(f"unexpected class identity at 0x{address:08x}")
        magic, initial_state, initial_flags, length, crc = struct.unpack_from("<IHHHH", header, 12)
        if (magic, initial_state, initial_flags, length, crc) != (
            0, state, flags, payload_length, 0,
        ):
            raise ValueError(f"unexpected class header at 0x{address:08x}")
        classes.append({
            "block_index": index,
            "runtime_address": f"0x{address:08x}",
            "name": name,
            "fixed_name_hex": fixed_name.hex(),
            "hash131": f"0x{hash131(fixed_name):08x}",
            "payload_bytes": payload_length,
            "initial_state_raw": state,
            "initial_flags_raw": flags,
            "contains_potentially_sensitive_data": sensitive,
        })

    payload_addresses = {
        name: address + CLASS_HEADER_BYTES
        for _, address, name, _, _, _, _ in CLASS_METADATA
    }
    compiled_defaults = {
        "dev_info": bytes.fromhex(
            "0000000000000000ffffffffffffffffffffffff43414d48"
            "01000000000000000000000000000000000000001900000000000000"
        ),
        "ble_mult": bytes(90),
        "health": bytes.fromhex("1400af41c8003200c8000000"),
        "hsync": bytes(24),
        "power": bytes(4),
        "nv_r1": bytes.fromhex(
            "ff" * 74 + "0000" + "ff" * 36 + "5a0000000000000000000000"
        ),
        "r_size": bytes(1),
    }
    for _, _, name, payload_length, _, _, _ in CLASS_METADATA:
        expected = compiled_defaults[name]
        if len(expected) != payload_length:
            raise ValueError(f"internal compiled default length mismatch for {name}")
        actual = runtime_bytes(
            runtime, scatter_runtime, payload_addresses[name], payload_length
        )
        if actual != expected:
            raise ValueError(f"unexpected compiled default payload for {name}")

    if crc16_modbus(b"123456789") != 0x4B37:
        raise ValueError("internal CRC-16/MODBUS implementation check failed")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "partition": {
            "name": "kv.bin",
            "device_name": "device_flash",
            "relative_offset_bytes": partition_offset,
            "length_bytes": partition_length,
            "sector_bytes": SECTOR_BYTES,
            "sector_count": 2,
            "slot_bytes": SLOT_BYTES,
            "slot_count": SLOT_COUNT,
            "slots_per_sector": 2,
            "partition_magic_word_little_endian": f"0x{PARTITION_MAGIC:08x}",
            "missing_partition_fallback_magic": f"0x{FALLBACK_MAGIC:08x}",
        },
        "class_record": {
            "block_bytes": CLASS_BLOCK_BYTES,
            "blocks_per_slot": MAXIMUM_CLASSES,
            "registered_blocks": len(classes),
            "unused_block_index": 7,
            "header_bytes": CLASS_HEADER_BYTES,
            "maximum_payload_bytes": 231,
            "fields": [
                "name hash131 UInt32LE @0", "fixed name[8] @4", "partition magic UInt32LE @12",
                "state raw UInt16LE @16", "flags/index UInt16LE @18",
                "stored payload length UInt16LE @20", "payload CRC-16/MODBUS UInt16LE @22",
                "payload @24",
            ],
            "flags_low_bit_is_dirty": True,
            "flags_bit1_meaning_resolved": False,
            "flags_upper_14_bits_are_block_index": True,
            "payload_crc_parameters": {
                "function": "0x0005d87c",
                "polynomial_reflected": "0xa001",
                "initial": "0xffff",
                "final_xor": 0,
                "check_123456789": "0x4b37",
            },
            "name_hash": {
                "function": "0x0005d8cc",
                "formula": "wrapping UInt32 hash = hash * 0x83 + byte over all 8 name bytes",
            },
        },
        "classes": classes,
        "payload_schemas": {
            "dev_info": {
                "payload_bytes": 52,
                "fields": [
                    "unresolved[8] @0", "sensitive peer address slot A[6] @8",
                    "sensitive peer address slot B[6] @14", "peer marker UInt32LE @20",
                    "settings flags UInt8 @24: health bit0, software-DCDC bit1, glasses bit2",
                    "reserved[7] @25", "health settings timestamp UInt32LE @32",
                    "power recovery timestamp UInt32LE @36",
                    "power recovery action low2/configuration high30 UInt32LE @40",
                    "unresolved[8] @44",
                ],
                "compiled_peer_slots_erased": True,
                "compiled_peer_marker_word": "0x484d4143",
                "compiled_settings_flags": 1,
                "compiled_tail_word_at_44": 25,
                "accessors": [
                    "0x00073694", "0x00073710", "0x00073750", "0x00073778",
                    "0x00073798", "0x00073800", "0x00073834", "0x00073868",
                    "0x000738a8",
                ],
            },
            "ble_mult": {
                "payload_bytes": 90,
                "compiled_default_is_all_zero": True,
                "dedicated_accessor_proven": False,
                "classification": "registered/restored dormant multi-peer placeholder",
            },
            "health": {
                "payload_bytes": 12,
                "fields": [
                    "age years UInt8 @0", "binary sex UInt8 @1", "height cm UInt8 @2",
                    "weight kg UInt8 @3", "unlabeled GoMore Int16LE parameter A @4",
                    "unlabeled GoMore Int16LE parameter B @6",
                    "unlabeled GoMore Int16LE parameter C @8", "unresolved[2] @10",
                ],
                "compiled_defaults": {
                    "age_years": 20, "binary_sex": 0, "height_cm": 175,
                    "weight_kg": 65, "algorithm_parameters": [200, 50, 200],
                },
                "production_valid_ranges": {
                    "age_years": [11, 99], "binary_sex": [0, 1],
                    "height_cm": [101, 219], "weight_kg": [31, 149],
                },
                "significant_change_thresholds": {
                    "age_years": 2, "height_cm": 9, "weight_kg": 9,
                    "binary_sex": "any change",
                },
                "accessors": ["0x000735e0", "0x00073604"],
                "validator": "0x0006c640",
                "algorithm_conversion": "0x0006abf8 converts demographics and three Int16 values to Float32; zero Int16 becomes -1",
            },
            "hsync": {
                "payload_bytes": 24,
                "fields": [
                    "heart-rate timestamp UInt32LE @0", "SpO2 timestamp UInt32LE @4",
                    "unresolved UInt32LE @8", "HRV timestamp UInt32LE @12",
                    "activity timestamp UInt32LE @16", "unresolved UInt32LE @20",
                ],
                "compiled_default_is_all_zero": True,
                "accessors": ["0x000738f4", "0x0007390c"],
                "unreferenced_offsets_in_this_version": [8, 20],
            },
            "power": {
                "payload_bytes": 4,
                "fields": [
                    "battery type UInt8 @0", "reserved UInt8 @1",
                    "signed voltage compensation Int16LE @2",
                ],
                "compiled_default_is_all_zero": True,
                "getters": ["0x0007bb44", "0x0007bb7c"],
            },
            "nv_r1": {
                "payload_bytes": 124,
                "decoder": "R1PersistentConfigurationDecoder",
                "recovery_builder": "0x0007b634",
                "recovery_body_copies_nv_prefix_bytes": 74,
                "remaining_fields": "identity lengths, temperature/accelerometer calibration, capacitive divider, operating mode and factory-aging state",
            },
            "r_size": {
                "payload_bytes": 1,
                "field": "ring size UInt8 @0",
                "compiled_default": 0,
                "getter": "0x0007bac4",
            },
        },
        "lifecycle": {
            "initialization_function": "0x00094e3c",
            "startup_sector_scrub_function": "0x00057d0c",
            "latest_slot_scan_function": "0x00064b24",
            "read_function": "0x00095168",
            "write_function": "0x00095304",
            "core_initialization_function": "0x000731a0",
            "core_restore_function": "0x00073220",
            "synchronized_store_function": "0x000734e8",
            "one_class_store_function": "0x00091780",
            "sector_scrub_checks_only_first_slot_first_class_magic": True,
            "latest_slot_selection_checks_only_first_class_magic": True,
            "latest_slot_scan_order": [3, 2, 1, 0],
            "next_write_slot": "latest valid slot + 1, or 0 when none",
            "full_store_erases_both_sectors_before_reusing_slot_zero": True,
            "any_dirty_class_causes_all_seven_classes_to_be_written": True,
            "snapshot_wide_checksum_present": False,
            "restore_matches_name_hash_and_fixed_name": True,
            "restore_crc_uses_descriptor_expected_length": True,
            "restore_checks_stored_length_field": False,
            "restore_checks_each_nonfirst_class_magic": False,
            "partial_latest_snapshot_can_leave_individual_classes_at_defaults": True,
        },
        "safety": {
            "static_parser_only": True,
            "compiled_default_payloads_emitted": False,
            "captured_payloads_emitted": False,
            "typed_capture_decoder_requires_hash_name_magic_length_index_and_crc": True,
            "sensitive_typed_payloads_require_explicit_policy": True,
            "live_raw_partition_access_exposed": False,
            "live_write_or_erase_sender_exposed": False,
        },
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    parser.add_argument("--scatter-source", type=parse_integer, default=DEFAULT_SCATTER_SOURCE)
    parser.add_argument("--scatter-runtime", type=parse_integer, default=DEFAULT_SCATTER_RUNTIME)
    parser.add_argument("--scatter-length", type=parse_integer, default=DEFAULT_SCATTER_LENGTH)
    arguments = parser.parse_args()
    print(json.dumps(summarize(
        arguments.image,
        arguments.base,
        arguments.scatter_source,
        arguments.scatter_runtime,
        arguments.scatter_length,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
