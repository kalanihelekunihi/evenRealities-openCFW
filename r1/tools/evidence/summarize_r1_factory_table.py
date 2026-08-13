#!/usr/bin/env python3
"""Decode the fixed production eAT registration table without executing firmware."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


DEFAULT_BASE = 0x27000
DEFAULT_TABLE = 0xC419C
DEFAULT_COUNT = 37
RECORD_SIZE = 16


def mapped_offset(address: int, base: int, image_size: int) -> int:
    offset = address - base
    if offset < 0 or offset >= image_size:
        raise ValueError(f"address 0x{address:08x} is outside the image")
    return offset


def c_string(image: bytes, address: int, base: int, maximum: int = 128) -> str:
    start = mapped_offset(address, base, len(image))
    end = image.find(b"\0", start, min(len(image), start + maximum + 1))
    if end < 0:
        raise ValueError(f"unterminated string at 0x{address:08x}")
    return image[start:end].decode("ascii")


def summarize(
    image_path: Path,
    base: int,
    table_address: int,
    count: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    table_offset = mapped_offset(table_address, base, len(image))
    table_bytes = count * RECORD_SIZE
    if table_offset + table_bytes > len(image):
        raise ValueError("registration table extends beyond the image")

    entries: list[dict[str, Any]] = []
    for index in range(count):
        address = table_address + index * RECORD_SIZE
        registration_type, name_pointer, handler_pointer, reserved = struct.unpack_from(
            "<IIII", image, table_offset + index * RECORD_SIZE
        )
        name = c_string(image, name_pointer, base)
        if not name.startswith("AT^"):
            raise ValueError(f"entry {index} does not point to an AT command: {name!r}")
        handler_entry = handler_pointer & ~1
        mapped_offset(handler_entry, base, len(image))
        entries.append(
            {
                "index": index,
                "record_address": f"0x{address:08x}",
                "registration_type_raw": registration_type,
                "command": name,
                "command_pointer": f"0x{name_pointer:08x}",
                "handler_thumb_pointer": f"0x{handler_pointer:08x}",
                "handler_entry": f"0x{handler_entry:08x}",
                "thumb_bit_set": bool(handler_pointer & 1),
                "reserved_raw": reserved,
            }
        )

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "table_address": f"0x{table_address:08x}",
        "record_size": RECORD_SIZE,
        "entry_count": count,
        "table_end_exclusive": f"0x{table_address + table_bytes:08x}",
        "all_handlers_are_thumb": all(entry["thumb_bit_set"] for entry in entries),
        "all_reserved_words_are_zero": all(entry["reserved_raw"] == 0 for entry in entries),
        "entries": entries,
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    parser.add_argument("--table-address", type=parse_integer, default=DEFAULT_TABLE)
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    arguments = parser.parse_args()
    if arguments.count <= 0:
        parser.error("--count must be positive")
    print(json.dumps(
        summarize(arguments.image, arguments.base, arguments.table_address, arguments.count),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
