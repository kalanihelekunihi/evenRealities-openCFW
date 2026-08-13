#!/usr/bin/env python3
"""Locate the unchecked ST25 mailbox reader across archived R1 applications.

This is an offline binary-pattern audit. It does not construct NFC messages or access hardware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


IMAGE_BASE = 0x27000
HANDLER_PREFIX = bytes.fromhex("10b586b0044600208df804008df80000")
OBJECT_LITERAL_OFFSET = 0x6C
HANDLER_WINDOW = 0x70


def locate_handler(image: bytes) -> tuple[int, int]:
    candidates: list[tuple[int, int]] = []
    cursor = 0
    while True:
        offset = image.find(HANDLER_PREFIX, cursor)
        if offset < 0:
            break
        window = image[offset : offset + HANDLER_WINDOW]
        if bytes.fromhex("8528") in window and bytes.fromhex("1421") in window:
            object_base = struct.unpack_from("<I", image, offset + OBJECT_LITERAL_OFFSET)[0]
            candidates.append((IMAGE_BASE + offset, object_base))
        cursor = offset + 1
    if len(candidates) != 1:
        raise ValueError(f"expected one ST25 mailbox handler, found {len(candidates)}")
    return candidates[0]


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    handler, object_base = locate_handler(image)
    destination = object_base + 0x38
    return {
        "version": path.parent.name,
        "path": str(path),
        "sha256": hashlib.sha256(image).hexdigest(),
        "size": len(image),
        "handler": f"0x{handler:08x}",
        "object_base": f"0x{object_base:08x}",
        "destination": f"0x{destination:08x}",
        "intended_bytes": 20,
        "maximum_driver_copy": 256,
        "maximum_overflow": 236,
        "maximum_end_inclusive": f"0x{destination + 255:08x}",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root",
        type=Path,
        help="directory containing VERSION/application.bin R1 archives",
    )
    arguments = parser.parse_args()
    applications = sorted(arguments.root.glob("*/application.bin"))
    if not applications:
        raise SystemExit(f"no VERSION/application.bin files under {arguments.root}")
    print(json.dumps([summarize(path) for path in applications], indent=2))


if __name__ == "__main__":
    main()
