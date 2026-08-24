#!/usr/bin/env python3
"""Create the hardware-testable openCFW 2.2.6.0 EVENOTA release image.

The reviewed source base identifies itself as 2.2.6.10.  A custom firmware
derived from that base uses 2.2.6.0.  The G2 exposes its version through two
independent Apollo-main paths: the normal settings response and product-test
command 0x24 used by the recovery case.  Both must agree with the outer
EVENOTA package identity.

This transform is deliberately fixed-layout and fail-closed.  It changes no
component sizes and accepts only the reviewed source and target identities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import open_cfw


SOURCE_PACKAGE_VERSION = "s200_v2.2.6.10"
RELEASE_PACKAGE_VERSION = "s200_v2.2.6.0"
SOURCE_RUNTIME_FIELD = b"2.2.6.10\0"
RELEASE_RUNTIME_FIELD = b"2.2.6.0\0\0"
MAIN_FILENAME = "ota/s200_firmware_ota.bin"

# These are Apollo-main payload offsets, not EVENOTA package offsets.  They
# were independently confirmed against the stock 2.2.6.10 settings response
# and product-test command 0x24 response used by the USB recovery case.
RUNTIME_VERSION_FIELDS = {
    "settings": 0x003537DC,
    "product_test_0x24": 0x00353D64,
}


@dataclass(frozen=True)
class ParsedEntry:
    index: int
    entry_id: int
    toc_offset: int
    body_offset: int
    body_size: int
    payload_offset: int
    payload_size: int
    filename: str
    checksum: int


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse_entries(image: bytes) -> list[ParsedEntry]:
    if len(image) < open_cfw.EVENOTA_TOC_OFFSET or image[:8] != open_cfw.EVENOTA_MAGIC:
        raise open_cfw.OpenCFWError("release input lacks EVENOTA magic")
    count = open_cfw.u32le(image, 8)
    if not 1 <= count <= 32:
        raise open_cfw.OpenCFWError("release input has an invalid entry count")
    toc_end = (
        open_cfw.EVENOTA_TOC_OFFSET
        + count * open_cfw.EVENOTA_TOC_ENTRY_SIZE
    )
    trailer_end = toc_end + len(open_cfw.EVENOTA_TOC_TRAILER)
    if image[toc_end:trailer_end] != open_cfw.EVENOTA_TOC_TRAILER:
        raise open_cfw.OpenCFWError("release input has an invalid TOC trailer")

    entries: list[ParsedEntry] = []
    expected_body_offset = trailer_end
    for index in range(count):
        toc_offset = open_cfw.EVENOTA_TOC_OFFSET + index * open_cfw.EVENOTA_TOC_ENTRY_SIZE
        entry_id, body_offset, body_size, checksum = struct.unpack_from(
            "<IIII", image, toc_offset
        )
        if body_offset != expected_body_offset:
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} is not contiguous"
            )
        body_end = body_offset + body_size
        if body_size < open_cfw.EVENOTA_COMPONENT_HEADER_SIZE or body_end > len(image):
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} exceeds the package"
            )
        header = image[body_offset:body_offset + open_cfw.EVENOTA_COMPONENT_HEADER_SIZE]
        payload_offset = body_offset + open_cfw.EVENOTA_COMPONENT_HEADER_SIZE
        payload = image[payload_offset:body_end]
        if open_cfw.u32le(header, 8) != len(payload):
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} payload size is invalid"
            )
        if open_cfw.u32le(header, 12) != checksum:
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} checksum copies disagree"
            )
        if open_cfw.crc32c_msb(payload) != checksum:
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} CRC-32C is invalid"
            )
        if open_cfw.u32le(header, 0x14) != open_cfw.EVENOTA_COMPONENT_MAGIC:
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} component magic is invalid"
            )
        filename = open_cfw.c_string(header, 0x30, 0x80)
        entries.append(
            ParsedEntry(
                index=index,
                entry_id=entry_id,
                toc_offset=toc_offset,
                body_offset=body_offset,
                body_size=body_size,
                payload_offset=payload_offset,
                payload_size=len(payload),
                filename=filename,
                checksum=checksum,
            )
        )
        expected_body_offset = body_end
    if expected_body_offset != len(image):
        raise open_cfw.OpenCFWError("release entries do not close at EOF")
    return entries


def _package_version(image: bytes) -> str:
    return open_cfw.c_string(image, 0x30, 0x40)


def _main_entry(entries: list[ParsedEntry]) -> ParsedEntry:
    matches = [entry for entry in entries if entry.filename == MAIN_FILENAME]
    if len(matches) != 1:
        raise open_cfw.OpenCFWError(
            f"release input contains {len(matches)} Apollo-main components"
        )
    return matches[0]


def transform(image: bytes) -> tuple[bytes, dict[str, Any]]:
    """Return the 2.2.6.0 package and an auditable transformation report."""
    if _package_version(image) != SOURCE_PACKAGE_VERSION:
        raise open_cfw.OpenCFWError(
            f"release input version must be {SOURCE_PACKAGE_VERSION}"
        )
    entries = _parse_entries(image)
    main = _main_entry(entries)
    main_before = image[
        main.payload_offset:main.payload_offset + main.payload_size
    ]
    open_cfw.validate_apollo_main(main_before)
    for label, relative_offset in RUNTIME_VERSION_FIELDS.items():
        actual = main_before[relative_offset:relative_offset + len(SOURCE_RUNTIME_FIELD)]
        if actual != SOURCE_RUNTIME_FIELD:
            raise open_cfw.OpenCFWError(
                f"{label} version field changed at Apollo offset 0x{relative_offset:08X}"
            )

    released = bytearray(image)
    released[0x30:0x40] = open_cfw.fixed_ascii(
        RELEASE_PACKAGE_VERSION, 16, "release package version"
    )
    absolute_fields: dict[str, int] = {}
    for label, relative_offset in RUNTIME_VERSION_FIELDS.items():
        absolute_offset = main.payload_offset + relative_offset
        absolute_fields[label] = absolute_offset
        released[
            absolute_offset:absolute_offset + len(RELEASE_RUNTIME_FIELD)
        ] = RELEASE_RUNTIME_FIELD

    main_after = released[
        main.payload_offset:main.payload_offset + main.payload_size
    ]
    nested_crc = zlib.crc32(main_after[8:]) & 0xFFFFFFFF
    struct.pack_into("<I", released, main.payload_offset + 4, nested_crc)
    main_after = released[
        main.payload_offset:main.payload_offset + main.payload_size
    ]
    component_crc = open_cfw.crc32c_msb(main_after)
    struct.pack_into("<I", released, main.toc_offset + 12, component_crc)
    struct.pack_into("<I", released, main.body_offset + 12, component_crc)

    result = bytes(released)
    if len(result) != len(image) or _package_version(result) != RELEASE_PACKAGE_VERSION:
        raise open_cfw.OpenCFWError("release transform changed package layout")
    reparsed = _parse_entries(result)
    reparsed_main = _main_entry(reparsed)
    released_main = result[
        reparsed_main.payload_offset:reparsed_main.payload_offset + reparsed_main.payload_size
    ]
    open_cfw.validate_apollo_main(released_main)
    for label, relative_offset in RUNTIME_VERSION_FIELDS.items():
        actual = released_main[
            relative_offset:relative_offset + len(RELEASE_RUNTIME_FIELD)
        ]
        if actual != RELEASE_RUNTIME_FIELD:
            raise open_cfw.OpenCFWError(f"{label} release version verification failed")

    report: dict[str, Any] = {
        "schema_version": 1,
        "source": {
            "version": SOURCE_PACKAGE_VERSION,
            "size": len(image),
            "sha256": sha256(image),
        },
        "release": {
            "version": RELEASE_PACKAGE_VERSION,
            "runtime_version": "2.2.6.0",
            "size": len(result),
            "sha256": sha256(result),
        },
        "apollo_main": {
            "payload_offset": main.payload_offset,
            "payload_size": main.payload_size,
            "source_sha256": sha256(main_before),
            "release_sha256": sha256(released_main),
            "nested_crc32": f"0x{nested_crc:08X}",
            "component_crc32c_msb": f"0x{component_crc:08X}",
            "runtime_version_fields": {
                label: {
                    "payload_offset": RUNTIME_VERSION_FIELDS[label],
                    "package_offset": absolute_fields[label],
                }
                for label in RUNTIME_VERSION_FIELDS
            },
        },
    }
    return result, report


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)

    result, report = transform(args.input.read_bytes())
    _atomic_write(args.output, result)
    if args.report is not None:
        _atomic_write(
            args.report,
            (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
    print(f"Built {args.output}")
    print(f"  size: {len(result)} bytes")
    print(f"  sha256: {report['release']['sha256']}")
    print("  runtime version: 2.2.6.0 (settings and product-test 0x24)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
