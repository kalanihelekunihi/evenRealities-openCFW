#!/usr/bin/env python3
"""Reconstruct the R1 internal-flash device and complete seven-partition FAL layout.

This parser is static and read-only. It never reads, writes or erases a physical ring.
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
    c_string,
    decompress_scatter,
    mapped_offset,
)


FLASH_DESCRIPTOR = 0x20006F98
FLASH_RECORD_BYTES = 0x2C
FLASH_OPERATIONS = 0x20006FC4
FLASH_REGISTER = 0x00054A8C
FLASH_LOOKUP_AND_FAL_INIT = 0x00071054
PARTITION_TABLE = 0x0009C250
PARTITION_RECORD_BYTES = 0x40
PARTITION_COUNT = 7
PARTITION_MAGIC_BYTES = b"01PE"
TARGET_PAGE_BYTES = 4096
FDS_INITIALIZER = 0x00063EB8

INTERNAL_FLASH_FUNCTIONS = {
    0x00054970: (24, "56204fd422647f465077ab12c708e8fbc8d03f8b4b04efb18331342360a93e1f"),
    0x0005498C: (90, "b9cda39e0bc0f03ea42a6e1e44e1d5bac07fb8f3db369d0839e9acf0f4c27261"),
    0x000549F0: (78, "77bc303edd609c87f797eee0a4ef4fa0a8cff8f6e91c834c07e953a37fd422ad"),
    0x00054A4C: (58, "566a087bf156d6362d518587719aa2228e6eb0bd6a2e424be8d9334a3a46faf1"),
    0x00054A8C: (20, "723ed3bf811013e4c869ba673706de2eded7250fa726541ff9bad3b1faaec8bc"),
    0x00054AA4: (72, "d2491fed88741679c5f672f2f06b984e2d436a2265ff78069e5034f04b2bc5d4"),
    0x0005C40C: (80, "438c1250404d0cfc64595bb8156b3203ad789425ef37e59300903a0d619a01e2"),
    0x0005C464: (24, "be5ff8a2ea57450c7d923fb100739955f6f731a6c30290dec76307733304bfcc"),
    0x0005C480: (62, "8979301e314a9fb7aa1a97517eaef0d953c8b93efa791b115050eaa29ed795bc"),
    0x00071054: (50, "d824c106b0c0f9734ddb41629fd6031a074aa9183fff47a94eac25f5b555d2af"),
}

EXPECTED_PARTITIONS = (
    ("kv.bin", 0x00000, 0x02000, "key-value store"),
    ("health.db", 0x02000, 0x06000, "health database"),
    ("sleep.db", 0x08000, 0x02000, "sleep database"),
    ("pKey.bin", 0x0A000, 0x01000, "persistent-key store"),
    ("reserve", 0x0B000, 0x0B000, "compiled reserve partition; no recovered consumer"),
    ("ep.bin", 0x16000, 0x02000, "firmware-named EP store"),
    ("log.bin", 0x18000, 0x0C000, "ring log store"),
)


def word(block: bytes, offset: int) -> int:
    return struct.unpack_from("<I", block, offset)[0]


def runtime_slice(runtime: bytes, runtime_base: int, address: int, length: int) -> bytes:
    offset = address - runtime_base
    if offset < 0 or offset + length > len(runtime):
        raise ValueError(f"runtime range 0x{address:08x}+0x{length:x} is outside scatter image")
    return runtime[offset:offset + length]


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


def bounded_c_string(block: bytes, offset: int, maximum: int) -> str:
    end = block.find(b"\0", offset, offset + maximum)
    if end < 0:
        raise ValueError(f"unterminated partition string at +0x{offset:x}")
    return block[offset:end].decode("ascii")


def string_occurrence_count(image: bytes, value: str) -> int:
    needle = value.encode() + b"\x00"
    count = 0
    start = 0
    while True:
        offset = image.find(needle, start)
        if offset < 0:
            return count
        count += 1
        start = offset + 1


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
    uicr_path: Path | None = None,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)

    function_evidence = []
    for address, (length, expected_digest) in INTERNAL_FLASH_FUNCTIONS.items():
        body = flash_bytes(image, base, address, length)
        actual_digest = hashlib.sha256(body).hexdigest()
        if actual_digest != expected_digest:
            raise ValueError(f"internal-flash function changed at 0x{address:08x}")
        function_evidence.append({
            "entry": f"0x{address:08x}",
            "bytes": length,
            "sha256": actual_digest,
        })

    signatures = {
        FLASH_REGISTER: "04480168416100f12c018161143031f0",
        FLASH_LOOKUP_AND_FAL_INIT: "10b50ca014f042fe0e4c206014f052fe",
        0x00054970: "41b105480a7802724a68c26089680161",
        0x0005498C: "70b5164d287920b129b1012915d01920",
        0x000549F0: "2de9f041124e307910b10020bde8f081",
        0x00054A4C: "70b514000ed00d4d287968b1287a68b1",
        0x00054AA4: "70b5140010d0104d287978b1287a88b1",
        0x00063150: "70b50f4d0646287808b100240ee00d4a",
        0x000631C0: "10b5074c207840b906480721c4e90101",
        0x000631E8: "2de9f047984691460e46040013d0b9f1",
        0x00063358: "2de9f047984691460e46040013d0b9f1",
    }
    for address, prefix in signatures.items():
        require_prefix(image, base, address, prefix)

    descriptor = runtime_slice(
        runtime, scatter_runtime, FLASH_DESCRIPTOR, FLASH_RECORD_BYTES,
    )
    if c_string(image, word(descriptor, 0), base) != "device_flash":
        raise ValueError("unexpected internal-flash descriptor name")
    if any(descriptor[offset] for offset in range(4, FLASH_RECORD_BYTES)):
        raise ValueError("unexpected nonzero initialized internal-flash record")
    operations = [
        word(runtime_slice(runtime, scatter_runtime, FLASH_OPERATIONS, 0x24), offset)
        for offset in range(0, 0x24, 4)
    ]
    expected_operations = [
        0x000549F1, 0, 0, 0, 0x00054A4D, 0x00054AA5,
        0x0005498D, 0x00054971, 0,
    ]
    if operations != expected_operations:
        raise ValueError(f"unexpected flash operations {[hex(value) for value in operations]}")

    table = flash_bytes(
        image, base, PARTITION_TABLE, PARTITION_COUNT * PARTITION_RECORD_BYTES,
    )
    partitions: list[dict[str, Any]] = []
    expected_next_offset = 0
    for index, (expected_name, expected_offset, expected_length, role) in enumerate(
        EXPECTED_PARTITIONS
    ):
        record = table[
            index * PARTITION_RECORD_BYTES:(index + 1) * PARTITION_RECORD_BYTES
        ]
        if record[:4] != PARTITION_MAGIC_BYTES:
            raise ValueError(f"unexpected partition magic at index {index}: {record[:4].hex()}")
        name = bounded_c_string(record, 4, 24)
        device = bounded_c_string(record, 0x1C, 24)
        offset = word(record, 0x34)
        length = word(record, 0x38)
        reserved = word(record, 0x3C)
        if (name, device, offset, length, reserved) != (
            expected_name, "device_flash", expected_offset, expected_length, 0,
        ):
            raise ValueError(f"unexpected partition record {index}")
        if offset != expected_next_offset or offset % TARGET_PAGE_BYTES != 0:
            raise ValueError(f"partition {name} is not contiguous/page-aligned")
        if length == 0 or length % TARGET_PAGE_BYTES != 0:
            raise ValueError(f"partition {name} length is not page-aligned")
        expected_next_offset = offset + length
        partitions.append({
            "index": index,
            "magic_bytes_ascii": "01PE",
            "magic_word_little_endian": "0x45503130",
            "name": name,
            "device_name": device,
            "offset_bytes": offset,
            "length_bytes": length,
            "page_count": length // TARGET_PAGE_BYTES,
            "end_offset_exclusive": offset + length,
            "reserved_raw": reserved,
            "role": role,
            "compiled_name_occurrences": string_occurrence_count(image, name),
            "has_recovered_consumer": name != "reserve",
        })

    if expected_next_offset != 0x24000:
        raise ValueError(f"unexpected partition endpoint 0x{expected_next_offset:x}")

    fds_body = flash_bytes(image, base, FDS_INITIALIZER, 204)
    if hashlib.sha256(fds_body).hexdigest() != \
            "9fa3e325b3955765dcda42a277d30292ba377611d54ef89d2a5032b71695abd7":
        raise ValueError("FDS initializer changed")
    if bytes.fromhex("a1f51031") not in fds_body or \
            bytes.fromhex("a1f54051") not in fds_body:
        raise ValueError("FDS 36-page reservation or three-page extent changed")

    installed_layout: dict[str, Any] | None = None
    if uicr_path is not None:
        uicr = uicr_path.read_bytes()
        if len(uicr) < 0x1C:
            raise ValueError("UICR evidence is too short")
        bootloader_start, parameter_page = struct.unpack_from("<II", uicr, 0x14)
        if bootloader_start == 0xFFFFFFFF:
            raise ValueError("UICR evidence has no installed bootloader boundary")
        device_start = bootloader_start - 36 * TARGET_PAGE_BYTES
        fds_start = device_start - 3 * TARGET_PAGE_BYTES
        installed_layout = {
            "uicr_path": str(uicr_path),
            "uicr_bytes": len(uicr),
            "uicr_sha256": hashlib.sha256(uicr).hexdigest(),
            "bootloader_start": f"0x{bootloader_start:08x}",
            "mbr_parameter_page": f"0x{parameter_page:08x}",
            "device_flash_start": f"0x{device_start:08x}",
            "device_flash_end_exclusive": f"0x{bootloader_start:08x}",
            "fds_start": f"0x{fds_start:08x}",
            "fds_end_exclusive": f"0x{device_start:08x}",
            "maximum_application_end_exclusive": f"0x{fds_start:08x}",
        }

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "scatter_output_bytes": len(runtime),
        "flash_device": {
            "name": "device_flash",
            "descriptor_address": f"0x{FLASH_DESCRIPTOR:08x}",
            "record_bytes": FLASH_RECORD_BYTES,
            "registration_function": f"0x{FLASH_REGISTER:08x}",
            "lookup_and_fal_init_function": f"0x{FLASH_LOOKUP_AND_FAL_INIT:08x}",
            "page_size_source": "FICR.CODEPAGESIZE",
            "target_page_size_bytes": TARGET_PAGE_BYTES,
            "flash_page_count_source": "FICR.CODESIZE",
            "bootloader_boundary_source": "UICR.BOOTLOADERADDR",
            "erased_bootloader_boundary_fallback": "FICR.CODEPAGESIZE * FICR.CODESIZE",
            "region_start_formula": "bootloader_start - page_size * 36",
            "region_end_exclusive_formula": "bootloader_start",
            "region_page_count": 36,
            "region_bytes": expected_next_offset,
            "operations": {
                "address": f"0x{FLASH_OPERATIONS:08x}",
                "open_initialize": "0x000549f1",
                "read": "0x00054a4d",
                "write": "0x00054aa5",
                "erase_or_query": "0x0005498d",
                "configure_callbacks": "0x00054971",
                "trailing_reserved_raw": 0,
            },
            "byte_pinned_adapter_functions": function_evidence,
        },
        "fds_separation": {
            "initializer": f"0x{FDS_INITIALIZER:08x}",
            "initializer_bytes": len(fds_body),
            "initializer_sha256": hashlib.sha256(fds_body).hexdigest(),
            "reserved_pages_below_bootloader": 36,
            "fds_pages": 3,
            "relationship": "FDS occupies the three pages immediately below device_flash",
        },
        "installed_layout": installed_layout,
        "partition_table": {
            "address": f"0x{PARTITION_TABLE:08x}",
            "record_bytes": PARTITION_RECORD_BYTES,
            "count": PARTITION_COUNT,
            "partitions": partitions,
            "all_contiguous": True,
            "total_pages": sum(item["page_count"] for item in partitions),
            "total_bytes": sum(item["length_bytes"] for item in partitions),
            "unconsumed_partition_names": [
                item["name"] for item in partitions if not item["has_recovered_consumer"]
            ],
        },
        "safety": {
            "static_parser_only": True,
            "live_raw_flash_access": False,
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
    parser.add_argument("--uicr", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(summarize(
        arguments.image,
        arguments.base,
        arguments.scatter_source,
        arguments.scatter_runtime,
        arguments.scatter_length,
        arguments.uicr,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
