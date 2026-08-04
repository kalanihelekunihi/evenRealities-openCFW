#!/usr/bin/env python3
"""Verify the integrated TLSF vendor snapshot and recovered G2 constants."""

from __future__ import annotations

import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
OPENCFW_ROOT = HERE.parents[1]

EXPECTED_FILES = {
    "tlsf.c": "2a0f8cfc9cfe6114ccdc6cf22339059440b16f1149b5107bead4ae4c3a0d50e2",
    "tlsf.h": "f7f73c48810ba60203095667c226e5a600a6ea0f69afba48efff6efbaa628d4f",
}

STOCK_IMAGE = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
STOCK_LOAD_ADDRESS = 0x00438000
STOCK_PAYLOAD_OFFSET = 0x20
STOCK_TLSF_START = 0x004CFD18
STOCK_TLSF_END_EXCLUSIVE = 0x004D09B4
STOCK_TLSF_SHA256 = (
    "007d8ac1f0e118281a07f6bde1049256800894d9684dff16e1d316f1ea4a7f9d"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"TLSF snapshot verification failed: {message}")


def verify_upstream_files() -> str:
    for name, expected_hash in EXPECTED_FILES.items():
        data = (HERE / name).read_bytes()
        require(
            sha256(data) == expected_hash,
            f"{name} differs from the selected upstream blob",
        )
        require(b"\r\n" in data, f"{name} lost its upstream CRLF line endings")
        require(
            b"\n" not in data.replace(b"\r\n", b""),
            f"{name} contains non-upstream bare LF line endings",
        )

    header = (HERE / "tlsf.h").read_text(encoding="ascii")
    for license_fragment in (
        "Copyright (c) 2006-2016, Matthew Conte",
        "Redistribution and use in source and binary forms",
        "Neither the name of the copyright holder",
        'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"',
    ):
        require(
            license_fragment in header,
            f"tlsf.h is missing license fragment {license_fragment!r}",
        )

    return (HERE / "tlsf.c").read_text(encoding="ascii")


def inspect_g2_configuration(source: str) -> None:
    expected_source_fragments = (
        "SL_INDEX_COUNT_LOG2 = 5,",
        "ALIGN_SIZE_LOG2 = 2,",
        "FL_INDEX_MAX = 30,",
        "SL_INDEX_COUNT = (1 << SL_INDEX_COUNT_LOG2),",
        "FL_INDEX_SHIFT = (SL_INDEX_COUNT_LOG2 + ALIGN_SIZE_LOG2),",
        "FL_INDEX_COUNT = (FL_INDEX_MAX - FL_INDEX_SHIFT + 1),",
        "SMALL_BLOCK_SIZE = (1 << FL_INDEX_SHIFT),",
        "static const size_t block_header_overhead = sizeof(size_t);",
        "sizeof(block_header_t) - sizeof(block_header_t*);",
        "static const size_t block_size_max = tlsf_cast(size_t, 1) << FL_INDEX_MAX;",
        "block_header_t* blocks[FL_INDEX_COUNT][SL_INDEX_COUNT];",
        "typedef ptrdiff_t tlsfptr_t;",
    )
    for fragment in expected_source_fragments:
        require(fragment in source, f"tlsf.c is missing {fragment!r}")

    pointer_size = 4
    size_t_size = 4
    sl_index_count_log2 = 5
    align_size_log2 = 2
    fl_index_max = 30

    align_size = 1 << align_size_log2
    sl_index_count = 1 << sl_index_count_log2
    fl_index_shift = sl_index_count_log2 + align_size_log2
    fl_index_count = fl_index_max - fl_index_shift + 1
    small_block_size = 1 << fl_index_shift
    block_header_size = pointer_size + size_t_size + pointer_size + pointer_size
    block_size_min = block_header_size - pointer_size
    block_size_max = 1 << fl_index_max
    block_header_overhead = size_t_size
    pool_overhead = 2 * block_header_overhead
    control_size = (
        block_header_size
        + 4
        + fl_index_count * 4
        + fl_index_count * sl_index_count * pointer_size
    )

    recovered = {
        "alignment": align_size,
        "second-level lists": sl_index_count,
        "first-level lists": fl_index_count,
        "small-block threshold": small_block_size,
        "block header": block_header_size,
        "minimum block": block_size_min,
        "maximum block": block_size_max,
        "allocation overhead": block_header_overhead,
        "pool overhead": pool_overhead,
        "control size": control_size,
    }
    expected = {
        "alignment": 4,
        "second-level lists": 32,
        "first-level lists": 24,
        "small-block threshold": 128,
        "block header": 16,
        "minimum block": 12,
        "maximum block": 0x40000000,
        "allocation overhead": 4,
        "pool overhead": 8,
        "control size": 0xC74,
    }
    require(recovered == expected, f"recovered configuration changed: {recovered}")


def verify_stock_span() -> bool:
    if not STOCK_IMAGE.is_file():
        return False

    image = STOCK_IMAGE.read_bytes()
    start = STOCK_PAYLOAD_OFFSET + STOCK_TLSF_START - STOCK_LOAD_ADDRESS
    end = STOCK_PAYLOAD_OFFSET + STOCK_TLSF_END_EXCLUSIVE - STOCK_LOAD_ADDRESS
    require(0 <= start < end <= len(image), "stock TLSF span is outside OTA image")
    stock_tlsf = image[start:end]
    require(len(stock_tlsf) == 3228, "stock TLSF span length changed")
    require(
        sha256(stock_tlsf) == STOCK_TLSF_SHA256,
        "stock TLSF code-and-literal span hash changed",
    )
    return True


def main() -> None:
    source = verify_upstream_files()
    inspect_g2_configuration(source)
    stock_checked = verify_stock_span()
    suffix = " and stock G2 span" if stock_checked else ""
    print(f"TLSF upstream snapshot, BSD-3-Clause notice, G2 config{suffix}: OK")


if __name__ == "__main__":
    main()
