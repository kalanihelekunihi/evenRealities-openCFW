#!/usr/bin/env python3
"""Validate and summarize the R1 log.bin writer and composite export backend.

This is a static, read-only parser for application 2.2.6.0009. It never connects to a ring,
exports potentially sensitive logs, or exposes flash write/erase operations.
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


PARTITION_RECORD = 0x0009C3D0
PARTITION_OFFSET = 0x00018000
PARTITION_BYTES = 0xC000
SECTOR_BYTES = 0x1000
SECTOR_COUNT = 12
EP_PREFIX_BYTES = 0x2000
STATE_RUNTIME = 0x20006904
DESCRIPTOR_RUNTIME = 0x20006918
GENERIC_EXPORT_RUNTIME = 0x20006C28

FUNCTION_SIGNATURES = {
    0x00058D54: "02490020887005f041b9000004690020",  # export stop callback
    0x00058D64: "10b538f0c1fbc00703d138f0bdfb4007",  # export start callback
    0x00058DE4: "2de9fe4f040003d0894d287818b104e0",  # compose file info/checksum
    0x0005908C: "0348806808b1806b000bc0b270470000",  # partition page count
    0x000590A0: "0148807870470000046900202de9fc47",  # export-active query
    0x000590AC: "2de9fc473fa00af04df84149414a3f4c",  # initialize/scan log pages
    0x000592BC: "2de9f04f144605468b488c4a87b0a0eb",  # composite virtual-file reader
    0x00059670: "2de9f34f954c83b00e46207808b9fff7",  # circular page writer
    0x0005DFF8: "2de9f04100f0fcf918b900f011f90028",  # EP magic-presence scan
    0x0005E086: "2de9f041070022d000f0b3f918b900f0",  # checksum complete EP pages
    0x00091490: "b0f73abc0149487070470000ec680020",  # live-cache available count
    0x000914A0: "10b5c7f7fdfd00281ad14ff480542246",  # periodic 4096-byte persistence
    0x0004E740: "2de9f04f87b0834600920f464b780a78",  # generic file-export state machine
    0x00032408: "2de9f74fc0b014468b464ff000093eaa",  # uncommanded fragmenter
    0x00032598: "2de9ff4fbfb08b464ff000091c463eaa",  # commanded fragmenter
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
    if partition[:4] != b"01PE" or partition[4:12] != b"log.bin\0":
        raise ValueError("unexpected log.bin FAL record")
    if partition[0x1C:0x29] != b"device_flash\0":
        raise ValueError("unexpected log.bin device name")
    partition_offset, partition_length, reserved = struct.unpack_from("<III", partition, 0x34)
    if (partition_offset, partition_length, reserved) != (
        PARTITION_OFFSET, PARTITION_BYTES, 0,
    ):
        raise ValueError("unexpected log.bin partition geometry")

    state_words = [
        runtime_word(runtime, scatter_runtime, STATE_RUNTIME + offset)
        for offset in range(0, 0x34, 4)
    ]
    expected_state_words = [
        0x0000FF00, 0, 0, 0, 0, 1, 0, 0,
        0x00058DE5, 0x000592BD, 0x00058D65, 0x00058D55, 0x20006905,
    ]
    if state_words != expected_state_words:
        raise ValueError("unexpected log writer/export scatter state")

    generic_words = [
        runtime_word(runtime, scatter_runtime, GENERIC_EXPORT_RUNTIME + offset)
        for offset in range(0, 0x10, 4)
    ]
    if generic_words[:2] != [0, DESCRIPTOR_RUNTIME]:
        raise ValueError("generic export state does not reference the log descriptor")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "partition": {
            "name": "log.bin",
            "device_name": "device_flash",
            "relative_offset_bytes": partition_offset,
            "length_bytes": partition_length,
            "sector_bytes": SECTOR_BYTES,
            "sector_count": SECTOR_COUNT,
            "erased_probe_word_offset": 4,
            "initialization_function": "0x000590ac",
            "writer_function": "0x00059670",
        },
        "writer": {
            "maximum_input_bytes": SECTOR_BYTES,
            "normal_persisted_input_bytes": SECTOR_BYTES,
            "periodic_persistence_function": "0x000914a0",
            "periodic_gate_raw": 10000,
            "periodic_gate_unit_resolved": False,
            "first_word_ff_is_not_the_probe": True,
            "page_is_erased_when_second_word_is_ffffffff": True,
            "advance_before_write_when_chunk_would_cross_page": True,
            "erase_selected_nonempty_page": True,
            "preerase_next_nonempty_page_after_write": True,
            "full_partition_initialization_fallback_sector": 0,
        },
        "virtual_export": {
            "wire_file_type_byte": 1,
            "logical_dart_enum_index": 0,
            "descriptor_runtime_address": f"0x{DESCRIPTOR_RUNTIME:08x}",
            "generic_state_runtime_address": f"0x{GENERIC_EXPORT_RUNTIME:08x}",
            "file_info_callback": "0x00058de4",
            "read_callback": "0x000592bc",
            "start_callback": "0x00058d64",
            "stop_callback": "0x00058d54",
            "maximum_chunk_bytes": SECTOR_BYTES,
            "segment_order": [
                {"name": "ep.bin", "bytes": EP_PREFIX_BYTES, "always_if_export_succeeds": True},
                {"name": "non-erased log.bin sectors", "bytes_each": SECTOR_BYTES,
                 "order": "cyclic, starting after the first erased sector"},
                {"name": "current live RTT cache", "length_type": "UInt16"},
                {"name": "valid crash C string", "nul_included": False, "optional": True},
            ],
            "eligibility": "at least one non-erased log sector or one EP magic-A record",
            "cache_or_crash_alone_is_not_eligible": True,
            "checksum": {
                "function": "0x0005d8a4",
                "polynomial": "0x1edc6f41",
                "reflected": False,
                "initial": 0,
                "final_xor": 0,
                "covers_exact_concatenated_virtual_file": True,
            },
            "known_reader_edge": (
                "arbitrary reads crossing physical sector 11 to 0 are not segmented by the "
                "callback; normal 4096-byte aligned transfer chunks avoid this"
            ),
        },
        "transport": {
            "generic_handler": "0x0004e740",
            "accepted_phone_commands": ["start=0", "data_ack=1"],
            "ring_commands": ["start=0", "data_marker=1", "raw=2", "check=3"],
            "retry_response": "dataCRCError=2 resets current virtual offset to zero",
            "commanded_fragmenter": "0x00032598",
            "fragment_payload_bytes": 238,
            "fragment_prefix": [
                "descending serial UInt8", "payload CRC UInt32LE", "command UInt8",
            ],
            "crc_excludes_inserted_command_byte": True,
            "serial_starts_at_integer_quotient_payload_length_div_238": True,
            "exact_multiple_emits_terminal_empty_serial_zero_fragment": True,
        },
        "coordination": {
            "export_blocks_flash_log_writers": True,
            "start_sets_log_export_and_ep_flush_guards": True,
            "stop_clears_both_guards": True,
            "stop_posts_ep_flush_event_0x2003": True,
        },
        "safety": {
            "static_parser_only": True,
            "log_content_may_include_bonding_key_material": True,
            "live_export_sender_exposed": False,
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
