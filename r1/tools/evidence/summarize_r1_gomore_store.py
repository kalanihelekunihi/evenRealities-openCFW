#!/usr/bin/env python3
"""Reconstruct the R1 GoMore persistent-key and previous-state flash contracts.

This parser is static and read-only. It validates the production application image and never
reads a physical ring or exposes persistent key material.
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


PARTITION_RECORD = 0x0009C310
PARTITION_BYTES = 0x1000
CHECKSUM_TABLE = 0x000997A8
CHECKSUM_POLYNOMIAL = 0x1EDC6F41
KEY_BYTES = 0x40
KEY_HEADER_BYTES = 8
SYSTEM_COMMAND_ENTRY = 0x0009A51C
STORAGE_EVENT_DISPATCH_BASE = 0x200066FC

FUNCTION_SIGNATURES = {
    0x0005D8A4: "70b50023074e146807e0c55c5b1c85ea",  # checksum update
    0x0006AD80: "2de9fe43454d07460e46287808b900f0",  # key read/verify
    0x0006AFB0: "2de9fe4f9a4693460c46fff7e1fe0028",  # previous-state restore
    0x0006B724: "2de9fe4380467148714a0e46101a0121",  # key write
    0x0006BA68: "2de9f04123a0f7f76ffb2649264a244c",  # partition init
    0x0006BBB0: "2de9f34fcc4c8fb08946207808b9fff7",  # previous-state append
    0x000844EC: "f8b506460d460846fef76efb040011d0",  # setAlgoKey EUS handler
    0x00042B20: "38b504464ef0e2fcc00703d14ef0defc",  # length-prefix storage thunk
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


def checksum_table() -> tuple[int, ...]:
    values: list[int] = []
    for index in range(256):
        value = index << 24
        for _ in range(8):
            value = ((value << 1) ^ CHECKSUM_POLYNOMIAL) & 0xFFFFFFFF \
                if value & 0x80000000 else (value << 1) & 0xFFFFFFFF
        values.append(value)
    return tuple(values)


def checksum(data: bytes, seed: int = 0) -> int:
    table = checksum_table()
    value = seed & 0xFFFFFFFF
    for byte in data:
        value = table[byte ^ (value >> 24)] ^ ((value << 8) & 0xFFFFFFFF)
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

    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)

    compiled_table = struct.unpack(
        "<256I", flash_bytes(image, base, CHECKSUM_TABLE, 256 * 4),
    )
    generated_table = checksum_table()
    if compiled_table != generated_table:
        raise ValueError("compiled GoMore key checksum table does not match polynomial")

    partition = flash_bytes(image, base, PARTITION_RECORD, 0x40)
    if partition[:4] != b"01PE" or partition[4:13] != b"pKey.bin\0":
        raise ValueError("unexpected pKey.bin FAL record")
    if partition[0x1C:0x29] != b"device_flash\0":
        raise ValueError("unexpected pKey.bin device name")
    partition_offset, partition_length, reserved = struct.unpack_from("<III", partition, 0x34)
    if (partition_offset, partition_length, reserved) != (0x0A000, PARTITION_BYTES, 0):
        raise ValueError("unexpected pKey.bin partition geometry")

    command_identifier, command_handler = struct.unpack(
        "<II", flash_bytes(image, base, SYSTEM_COMMAND_ENTRY, 8),
    )
    if (command_identifier, command_handler) != (0x000C, 0x000844ED):
        raise ValueError("unexpected setAlgoKey registration")

    storage_dispatch_words = [
        runtime_word(runtime, scatter_runtime, STORAGE_EVENT_DISPATCH_BASE + index * 4)
        for index in range(8)
    ]
    if storage_dispatch_words != [
        0, 0x00042BC7, 0x00042BCB, 0x00042BC3,
        0x00042BB1, 0x00042B21, 0x00042BBF, 0,
    ]:
        raise ValueError("unexpected storage event dispatch table")
    # Storage dispatch adds one word to the literal base before indexing eventID - 0x2000.
    set_key_slot = 1 + (0x2004 - 0x2000)
    if storage_dispatch_words[set_key_slot] != 0x00042B21:
        raise ValueError("raw event 0x2004 does not resolve to the pKey storage thunk")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "partition": {
            "name": "pKey.bin",
            "device_name": "device_flash",
            "relative_offset_bytes": partition_offset,
            "length_bytes": partition_length,
            "page_count": 1,
        },
        "key_record": {
            "header_bytes": KEY_HEADER_BYTES,
            "declared_length_offset": 0,
            "checksum_offset": 4,
            "key_offset": 8,
            "required_key_bytes": KEY_BYTES,
            "total_record_bytes": KEY_HEADER_BYTES + KEY_BYTES,
            "checksum": {
                "function": "0x0005d8a4",
                "table_address": f"0x{CHECKSUM_TABLE:08x}",
                "width": 32,
                "polynomial": f"0x{CHECKSUM_POLYNOMIAL:08x}",
                "initial_value": 0,
                "input_reflected": False,
                "output_reflected": False,
                "final_xor": 0,
                "check_123456789": f"0x{checksum(b'123456789'):08x}",
            },
            "reader_function": "0x0006ad80",
            "writer_function": "0x0006b724",
            "writer_erases_page_when_stored_checksum_word_is_not_erased": True,
            "writer_replacement_discards_previous_state_slots": True,
        },
        "previous_state": {
            "append_function": "0x0006bbb0",
            "restore_function": "0x0006afb0",
            "alignment_bytes": 4,
            "slot_header_bytes": 8,
            "slot_header_fields": ["length_u32le", "reserved_zero_u32le"],
            "writer_slot_indices": [0, 1, 2],
            "restore_probe_indices_newest_first": [3, 2, 1, 0],
            "compaction_trigger_slot_index": 2,
            "compaction_preserves_key_record_bytes": 72,
            "maximum_accepted_unaligned_data_bytes": 944,
            "slot_offset_formula": "72 + index * (align4(data_length) + 8)",
            "checksum_present": False,
        },
        "protocol_ingress": {
            "system_subcommand": "0x0c",
            "registration_entry": f"0x{SYSTEM_COMMAND_ENTRY:08x}",
            "handler": "0x000844ec",
            "queued_record_identifier_raw": "0x2004",
            "payload_form": "length_u8 followed by key bytes",
            "acknowledgement_is_queued_before_persistence": True,
            "length_prefix_storage_thunk": "0x00042b20",
            "storage_dispatch_base_runtime_address":
                f"0x{STORAGE_EVENT_DISPATCH_BASE:08x}",
            "storage_dispatch_base_is_leading_null_sentinel": True,
            "resolved_storage_handler_thumb": "0x00042b21",
            "storage_dispatch_words": [
                f"0x{value:08x}" for value in storage_dispatch_words
            ],
        },
        "safety": {
            "static_parser_only": True,
            "key_material_emitted": False,
            "raw_flash_sender_exposed": False,
            "provisioning_sender_exposed": False,
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
