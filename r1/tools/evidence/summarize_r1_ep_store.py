#!/usr/bin/env python3
"""Validate and summarize the R1 firmware-named EP queue and flash journal.

This is a static, read-only parser for application 2.2.6.0009. It does not read a physical ring,
expand the unresolved name "EP", export private logs, or expose flash write/erase operations.
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


PARTITION_RECORD = 0x0009C390
PARTITION_OFFSET = 0x00016000
PARTITION_BYTES = 0x2000
PAGE_BYTES = 0x1000
RECORD_BYTES = 8
RECORDS_PER_PAGE = PAGE_BYTES // RECORD_BYTES
RECORD_COUNT = PARTITION_BYTES // RECORD_BYTES
QUEUE_CAPACITY = 16
QUEUE_MAXIMUM_BUFFERED = 15
STORAGE_EVENT_DISPATCH_BASE = 0x200066FC
STORAGE_EVENT_IDENTIFIER = 0x2003

FUNCTION_SIGNATURES = {
    0x0005E0DE: "0020e0f728be0120e0f725be000010b5",  # guarded flush worker
    0x0005E0EC: "10b5094ca06818b9012039f0f2fca060",  # lazy initialization
    0x0005E118: "1cb59df8004024f00f040a3460f30514",  # pack/enqueue producer
    0x0005E1FC: "094910b50a780ab1022801d3002010bd",  # erase one page
    0x0005E228: "2de9f843394c207810b10120bde8f883",  # partition initialization
    0x0005E404: "38b514461b4a054610784042084225d0002c23d02819b0f5005f21d933f064f8",
    0x0005E4D8: "38b514461b4a054610784042084225d0002c23d02819b0f5005f21d932f0faff",
    0x0003EC78: "2de9fc5fdff8849057f038f899f80000",  # drain queue to flash
    0x0003ED0C: "38b5ff2104468df80010000301226946",  # erase page unless byte 0 is FF
    0x0003EE34: "2de9f84f4ff4805046f0b0fb06003e48",  # scan/recover cursor
    0x00042BB0: "10b54ef075fcbde810401bf090ba39f0",  # event 0x2003 thunk
    0x0004CB08: "064900200b894ff6ff72934200d00120",  # two-slot availability count
    0x00091264: "014890f82d007047",                  # unresolved 2-bit snapshot source
    0x00091270: "10b5eaf7d7fb552801d1a0f7a9fe0348",  # unresolved 7-bit context source
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


def runtime_word(runtime: bytes, runtime_base: int, address: int) -> int:
    offset = address - runtime_base
    if offset < 0 or offset + 4 > len(runtime):
        raise ValueError(f"runtime word 0x{address:08x} is outside scatter image")
    return struct.unpack_from("<I", runtime, offset)[0]


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

    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)

    partition = flash_bytes(image, base, PARTITION_RECORD, 0x40)
    if partition[:4] != b"01PE" or partition[4:11] != b"ep.bin\0":
        raise ValueError("unexpected ep.bin FAL record")
    if partition[0x1C:0x29] != b"device_flash\0":
        raise ValueError("unexpected ep.bin device name")
    partition_offset, partition_length, reserved = struct.unpack_from("<III", partition, 0x34)
    if (partition_offset, partition_length, reserved) != (
        PARTITION_OFFSET, PARTITION_BYTES, 0,
    ):
        raise ValueError("unexpected ep.bin partition geometry")

    dispatch_words = [
        runtime_word(runtime, scatter_runtime, STORAGE_EVENT_DISPATCH_BASE + index * 4)
        for index in range(8)
    ]
    expected_dispatch_words = [
        0, 0x00042BC7, 0x00042BCB, 0x00042BC3,
        0x00042BB1, 0x00042B21, 0x00042BBF, 0,
    ]
    if dispatch_words != expected_dispatch_words:
        raise ValueError("unexpected storage dispatch words")
    # Storage dispatch adds one word to the literal base, then indexes ID - 0x2000.
    event_slot = 1 + (STORAGE_EVENT_IDENTIFIER - 0x2000)
    if dispatch_words[event_slot] != 0x00042BB1:
        raise ValueError("raw event 0x2003 does not resolve to the EP flush thunk")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "partition": {
            "name": "ep.bin",
            "name_expansion_resolved": False,
            "device_name": "device_flash",
            "relative_offset_bytes": partition_offset,
            "length_bytes": partition_length,
            "page_bytes": PAGE_BYTES,
            "page_count": 2,
            "initialization_function": "0x0005e228",
            "read_wrapper": "0x0005e404",
            "write_wrapper": "0x0005e4d8",
            "erase_page_wrapper": "0x0005e1fc",
        },
        "record": {
            "bytes": RECORD_BYTES,
            "count": RECORD_COUNT,
            "records_per_page": RECORDS_PER_PAGE,
            "packed_u32le_fields": [
                "magic_0xa:4", "producer_field_0:2", "producer_field_1:6",
                "producer_field_2:6", "producer_field_3:3",
                "snapshot_field:2", "two_slot_availability_count:2",
                "context_field:7",
            ],
            "timestamp_u32le_offset": 4,
            "checksum_present": False,
            "producer_function": "0x0005e118",
        },
        "ram_queue": {
            "physical_slots": QUEUE_CAPACITY,
            "maximum_buffered_records": QUEUE_MAXIMUM_BUFFERED,
            "index_mask": "0x0f",
            "drop_policy": "drop incoming record when next tail equals head",
            "drop_counter": "wrapping UInt16",
        },
        "flash_journal": {
            "drain_function": "0x0003ec78",
            "cursor_scan_function": "0x0003ee34",
            "cursor_slots": RECORD_COUNT,
            "cursor_mask": "0x03ff",
            "page_formula": "cursor >> 9",
            "slot_formula": "cursor & 0x01ff",
            "offset_formula": "page * 4096 + slot * 8",
            "page_start_erases_when_first_byte_is_not_ff": True,
            "page_end_pre_erases_opposite_page": True,
            "scan_first_free_rule": "first record whose low nibble is not 0xA",
            "scan_latest_rule":
                "greatest nonzero timestamp among magic records; later equal timestamp wins",
            "all_magic_cursor_rule": "(latest timestamp index + 1) & 0x03ff",
            "magic_record_with_zero_timestamp_is_not_latest_or_free": True,
        },
        "internal_dispatch": {
            "queued_record_identifier_raw": "0x2003",
            "storage_dispatch_base_runtime_address":
                f"0x{STORAGE_EVENT_DISPATCH_BASE:08x}",
            "dispatch_base_is_leading_null_sentinel": True,
            "resolved_handler_thumb": "0x00042bb1",
            "resolved_handler_entry": "0x00042bb0",
        },
        "coordination": {
            "lazy_initialization_function": "0x0005e0ec",
            "guarded_flush_worker": "0x0005e0de",
            "export_guard_timeout_raw": "0x0004b000",
            "export_guard_timeout_unit_resolved": False,
            "synchronization_take_timeout_raw": "0x00000400",
            "synchronization_timeout_unit_resolved": False,
        },
        "safety": {
            "static_parser_only": True,
            "raw_partition_export_exposed": False,
            "raw_flash_sender_exposed": False,
            "write_or_erase_sender_exposed": False,
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
