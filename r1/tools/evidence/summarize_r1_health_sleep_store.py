#!/usr/bin/env python3
"""Validate and summarize the R1 health.db and sleep.db physical formats.

This is a static, read-only firmware parser for application 2.2.6.0009. It never reads a ring,
formats a database, or emits biometric values from a capture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset


PARTITION_TABLE = 0x0009C250
PARTITION_RECORD_BYTES = 0x40
HEALTH_PARTITION_INDEX = 1
SLEEP_PARTITION_INDEX = 2

FUNCTION_SIGNATURES = {
    0x00070030: "2de9f0410021824a88b0084602eb0013",  # health TSDB init
    0x0005DCE8: "2de9f04f87b0c4b233f0fcfbc0074ff0",  # hourly body append
    0x00063694: "10b5040009d00c292dd2dfe801f0172d",  # TSDB control
    0x00063814: "2de9f0419cb00446dde922704ff00008",  # TSDB init wrapper
    0x00063A28: "70b50446007e0d4670b1e2690ab12046",  # TSDB append wrapper
    0x00063AB8: "10b5c169044601b1884720462ff0b0fe",  # destructive format wrapper
    0x00063AD8: "2de9ff4f9fb04ff000090646cdf86890",  # time-range query
    0x00087C24: "2de9f0419ab0984614000f4605464ff0",  # read sector header
    0x00087E14: "30b589b00c460546c96820236a46b7f7",  # read TSL index
    0x000895F4: "2de9f05fd1f804a0dde90b799b461646",  # sector iterator
    0x00093744: "7cb50446406d0e46804705467068a16d",  # FlashDB append
    0x00093828: "30b58db00446002512482346cde90050",  # format all sectors
    0x0005B0F8: "2de9f04123a008f027f82649264a244c",  # sleep partition init
    0x0005B23C: "10b500f075f8040001d000f057f836f0",  # sleep erase all
    0x0005B2F8: "2de9f04134f08afd05460024084e4ff4",  # sleep sector erase loop
    0x0005B32C: "2de9f04387b034f06ffd814618216846",  # sleep record counter
    0x0005B39C: "2de9f74f754a764894b0101ac0080122",  # sleep record iterator
    0x0005B6F4: "2de9f047374b384a88b09a1ad2080123",  # sync-marker writer
    0x0005B890: "2de9f047814645488846464a01784448",  # sleep append wrapper
    0x0008FC6C: "2de9ff4100f0d0f807460020461e0090",  # erase-oldest selector
    0x0008FE14: "0348406808b1806b000bc0b270470000",  # sector count
    0x0008FE28: "2de9ff41fff7f2ff0546002000900190",  # writable-sector finder
    0x0008FE98: "2de9f74fdff8f49107468a46d9f80400",  # record writer
    0x000901E4: "2de9f0432e4e8fb04ff0000871684546",  # full-sector marker
    0x0008F728: "f0b5064690f9005000204ff0ff330446",  # compact stage RLE
    0x0008DA24: "2de9ff4f867f044606eb4600203083b0",  # phone-stage expander
    0x0005D87C: "30b503464ff6ff700022064c07e09d5c",  # CRC-16/MODBUS
}

HEALTH_DESCRIPTORS = (
    (0, 3, 0x00070649, 0x000706A5, 0x0007062D, "heart_rate"),
    (1, 3, 0x00090DF1, 0x00090E4D, 0x00090DD5, "blood_oxygen"),
    (2, 3, 0x00091919, 0x00091955, 0x000918DF, "temperature"),
    (3, 3, 0x0009113F, 0x00091159, 0x00091125, "stress"),
    (4, 24, 0x000482A9, 0x0004832D, 0x00048289, "activity"),
    (5, 6, 0x000706D9, 0x0007073D, 0x000706BF, "heart_rate_variability"),
)


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


def word(image: bytes, base: int, address: int) -> int:
    return struct.unpack("<I", flash_bytes(image, base, address, 4))[0]


def bounded_c_string(block: bytes, offset: int, maximum: int) -> str:
    end = block.find(b"\0", offset, offset + maximum)
    if end < 0:
        raise ValueError(f"unterminated string at +0x{offset:x}")
    return block[offset:end].decode("ascii")


def partition_record(image: bytes, base: int, index: int) -> tuple[str, str, int, int]:
    record = flash_bytes(
        image,
        base,
        PARTITION_TABLE + index * PARTITION_RECORD_BYTES,
        PARTITION_RECORD_BYTES,
    )
    if record[:4] != b"01PE":
        raise ValueError(f"unexpected partition magic at index {index}")
    name = bounded_c_string(record, 4, 24)
    device = bounded_c_string(record, 0x1C, 24)
    offset, length, reserved = struct.unpack_from("<III", record, 0x34)
    if device != "device_flash" or reserved != 0:
        raise ValueError(f"unexpected partition metadata at index {index}")
    return name, device, offset, length


def crc16_modbus(data: bytes) -> int:
    value = 0xFFFF
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0xA001 if value & 1 else 0)
    return value


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    for address, prefix in FUNCTION_SIGNATURES.items():
        require_prefix(image, base, address, prefix)

    health_partition = partition_record(image, base, HEALTH_PARTITION_INDEX)
    sleep_partition = partition_record(image, base, SLEEP_PARTITION_INDEX)
    if health_partition != ("health.db", "device_flash", 0x02000, 0x06000):
        raise ValueError("unexpected health.db FAL geometry")
    if sleep_partition != ("sleep.db", "device_flash", 0x08000, 0x02000):
        raise ValueError("unexpected sleep.db FAL geometry")

    descriptor_block = flash_bytes(image, base, 0x00099BF4, 16 * 6)
    descriptors = []
    for index, expected in enumerate(HEALTH_DESCRIPTORS):
        metric, length, getter, setter, resetter, name = expected
        actual = struct.unpack_from("<BBHIII", descriptor_block, index * 16)
        if actual != (metric, length, 0, getter, setter, resetter):
            raise ValueError(f"unexpected health descriptor {index}: {actual!r}")
        descriptors.append({
            "metric_raw": metric,
            "name": name,
            "serialized_bytes": length,
            "callbacks_thumb": [
                f"0x{getter:08x}", f"0x{setter:08x}", f"0x{resetter:08x}",
            ],
        })
    if sum(item[1] for item in HEALTH_DESCRIPTORS) + 8 != 50:
        raise ValueError("unexpected health payload populated length")

    constants = {
        "sleep_full_state_word0": word(image, base, 0x0008FE90),
        "sleep_full_state_word1": word(image, base, 0x0008FE94),
        "sleep_synchronized_marker": word(image, base, 0x0005B61C),
        "sleep_sector_closer_word0": word(image, base, 0x000902A8),
        "sleep_sector_closer_word1": word(image, base, 0x000902AC),
    }
    expected_constants = {
        "sleep_full_state_word0": 0xCCFFAABB,
        "sleep_full_state_word1": 0x66889977,
        "sleep_synchronized_marker": 0x11223344,
        "sleep_sector_closer_word0": 0xCCFFAABB,
        "sleep_sector_closer_word1": 0x66889977,
    }
    if constants != expected_constants:
        raise ValueError(f"unexpected sleep storage constants: {constants!r}")
    if crc16_modbus(b"123456789") != 0x4B37:
        raise ValueError("internal CRC-16/MODBUS implementation check failed")

    required_strings = (
        b"..\\..\\..\\third_party\\DB\\FlashDB\\src\\fdb_tsdb.c\0",
        b"sleep storage iter crc error, offset: %08X\0",
        b"sleep storage write synchronize to head fail:%d\0",
        b"sleep storage writable sector: %d\0",
    )
    for value in required_strings:
        if value not in image:
            raise ValueError(f"missing expected diagnostic {value[:-1]!r}")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "health_database": {
            "partition_name": "health.db",
            "relative_offset_bytes": 0x02000,
            "partition_bytes": 0x06000,
            "sector_bytes": 0x1000,
            "sector_count": 6,
            "implementation": "FlashDB TSDB layout matching upstream tag 2.0.0",
            "write_granularity_bits": 32,
            "sector_magic_ascii": "TSL0",
            "sector_magic_word_little_endian": "0x304c5354",
            "sector_header_bytes": 80,
            "index_bytes": 32,
            "payload_bytes": 128,
            "populated_payload_bytes": 50,
            "maximum_records_per_sector": 25,
            "maximum_physical_records": 150,
            "per_record_checksum_present": False,
            "sector_header": [
                "store status table[12] @0", "magic UInt32LE @12",
                "start timestamp UInt32LE @16",
                "end slot 0: timestamp @20, index @24, status table[20] @28",
                "end slot 1: timestamp @48, index @52, status table[20] @56",
                "reserved UInt32LE @76",
            ],
            "index": [
                "TSL status table[20] @0", "timestamp UInt32LE @20",
                "payload length UInt32LE @24", "payload offset UInt32LE @28",
            ],
            "body": [
                "signed UTC offset minutes Int16LE @0", "reserved UInt16LE @2",
                "local-day start timestamp UInt32LE @4",
                "HR avg/max/min UInt8 @8", "SpO2 avg/max/min UInt8 @11",
                "temperature offset-from-250 avg/max/min UInt8 @14",
                "stress avg/max/min UInt8 @17",
                "six activity UInt32LE buckets @20: steps[11:0], active-kcal[21:12], all-kcal[31:22]",
                "HRV avg/max/min UInt16LE @44", "reserved tail[78] @50",
            ],
            "metric_descriptors": descriptors,
            "public_query_window_seconds": 259_200,
            "production_recovery": {
                "bad_sector_header_can_format_whole_partition_on_startup": True,
                "append_timestamp_error_3_formats_whole_partition_then_retries": True,
            },
        },
        "sleep_database": {
            "partition_name": "sleep.db",
            "relative_offset_bytes": 0x08000,
            "partition_bytes": 0x02000,
            "implementation": "ring-specific circular journal, not FlashDB TSDB",
            "sector_bytes": 0x1000,
            "sector_count": 2,
            "sector_header_bytes": 16,
            "record_header_bytes": 24,
            "records_per_sector": 8,
            "maximum_physical_records": 16,
            "data_start_offset": "0x00d0",
            "payload_alignment_bytes": 4,
            "synchronizable_maximum_payload_bytes": 232,
            "writer_maximum_payload_bytes": 3888,
            "full_state_words": ["0xccffaabb", "0x66889977"],
            "synchronized_marker": "0x11223344",
            "sector_header": [
                "full state word 0 UInt32LE @0", "full state word 1 UInt32LE @4",
                "close sequence UInt32LE @8", "reserved UInt32LE @12",
            ],
            "record_header": [
                "aligned payload bytes UInt16LE @0", "sector-relative payload offset UInt16LE @2",
                "reserved UInt16LE @4", "copied signed UTC offset minutes Int16LE @6",
                "copied start timestamp UInt32LE @8", "copied end timestamp UInt32LE @12",
                "reserved UInt16LE @16", "CRC-16/MODBUS UInt16LE @18",
                "phone synchronization marker UInt32LE @20",
            ],
            "payload": {
                "logical_header_bytes": 32,
                "header_matches_phone_session_fields": True,
                "physical_stage_bytes": "count bytes at @32; low 2 bits type, high 6 bits 30-second run",
                "phone_expansion": "merge adjacent same-type chunks and emit type UInt8 + half-minutes UInt16LE",
                "crc_coverage": "entire four-byte-aligned stored body including padding",
            },
            "rollover": {
                "full_sector_marked_after_eighth_record_or body exhaustion": True,
                "close_sequence_is_monotonic_across_full_sectors": True,
                "oldest_full_sector_with_lowest_sequence_is_erased": True,
            },
        },
        "safety": {
            "static_parser_only": True,
            "captured_biometric_values_emitted": False,
            "typed_capture_decoders_require_explicit_sensitive_data_policy": True,
            "health_payload_integrity_limit": "structural validation only; FlashDB stores no record checksum",
            "sleep_payload_integrity": "range, CRC, logical length, and duplicate metadata checks",
            "production_destructive_recovery_not_reproduced": True,
            "live_raw_partition_access_exposed": False,
            "live_write_erase_or_format_sender_exposed": False,
        },
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    arguments = parser.parse_args()
    print(json.dumps(
        summarize(arguments.image, arguments.base),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
