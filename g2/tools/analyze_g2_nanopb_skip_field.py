#!/usr/bin/env python3
"""Fail-closed source-boundary audit for G2 nanopb ``pb_skip_field``.

The analyzer is read-only. It authenticates the official Apollo-main image,
the complete dispatcher and adjacent bodies, all direct call ingress, outgoing
provider targets, the retained diagnostic-data seam, and the authenticated
nanopb source/configuration baseline. It never signs, flashes, or contacts a
device.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
)
UPSTREAM = ROOT / "third_party/nanopb/pb_decode.c"
CONFIG = ROOT / "third_party/nanopb/g2-config/pb_g2_options.h"

IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x0043_7FE0

DISPATCHER = (
    0x0048_F6A0,
    0x0048_F6EA,
    "36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d",
)
PREDECESSOR = (
    0x0048_F66C,
    0x0048_F6A0,
    "727a94d16ba7b4018c3addee83a6c63e87f0c3f2a3fe6afdb315549d10f53114",
)
SUCCESSOR = (
    0x0048_F6EA,
    0x0048_F7A0,
    "f656ff485fb6f7bdf03970db79daacb677610e99b3829fda110cc034574d4a7c",
)
EXPECTED_CALLERS = {
    0x0048_FB44: "fff7acfd",
    0x0048_FFBE: "fff76ffb",
}
EXPECTED_OUTGOING = {
    0x0048_F6B6: (0x0048_F628, "pb_skip_varint", "fff7b7ff"),
    0x0048_F6C0: (0x0048_F3BE, "pb_read_8", "fff77dfe"),
    0x0048_F6C6: (0x0048_F64C, "pb_skip_string", "fff7c1ff"),
    0x0048_F6D0: (0x0048_F3BE, "pb_read_4", "fff775fe"),
}
ERROR_POINTER_SLOT = 0x0049_0118
ERROR_ADDRESS = 0x0078_17DC
ERROR_BYTES = b"invalid wire_type\0"
ERROR_SHA256 = "6e35ebc2e585a3ca08ee2d60871a7d16749421ae2b6c1a33bb20c50175e1048a"

UPSTREAM_SIZE = 53_845
UPSTREAM_SHA256 = "e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a"
UPSTREAM_DEFINITION = (
    9_043,
    9_458,
    "4f447e98f77d58030aa39bf1d0e936b01253f828440f362336f96a8d7c679be1",
)
UPSTREAM_COMMIT = "98bf4db69897b53434f3d0ba72e0a3ab1a902824"


class AuditError(RuntimeError):
    """Raised when a pinned audit invariant no longer holds."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    if first < 0 or last > len(blob) or first > last:
        raise AuditError(f"runtime span {start:#x}...{end:#x} is outside image")
    return blob[first:last]


def authenticate_span(blob: bytes, record: tuple[int, int, str]) -> None:
    start, end, expected = record
    actual = sha256(image_slice(blob, start, end))
    if actual != expected:
        raise AuditError(
            f"span {start:#010x}...{end:#010x} hash {actual} != {expected}"
        )


def thumb_bl_target(address: int, first: int, second: int) -> int | None:
    """Decode one Thumb-2 BL immediate, returning its even code address."""

    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ (((second >> 13) & 1) ^ sign)
    i2 = 1 ^ (((second >> 11) & 1) ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((first & 0x03FF) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def scan_direct_callers(blob: bytes, target: int) -> dict[int, str]:
    callers: dict[int, str] = {}
    for offset in range(0, len(blob) - 3, 2):
        first, second = struct.unpack_from("<HH", blob, offset)
        address = LOAD_BASE + offset
        if thumb_bl_target(address, first, second) == target:
            callers[address] = blob[offset : offset + 4].hex()
    return callers


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")

    for record in (PREDECESSOR, DISPATCHER, SUCCESSOR):
        authenticate_span(blob, record)

    callers = scan_direct_callers(blob, DISPATCHER[0])
    if callers != EXPECTED_CALLERS:
        raise AuditError(f"pb_skip_field caller topology changed: {callers!r}")

    outgoing: list[dict[str, Any]] = []
    for address, (target, name, encoding) in EXPECTED_OUTGOING.items():
        raw = image_slice(blob, address, address + 4)
        if raw.hex() != encoding:
            raise AuditError(f"outgoing call encoding changed at {address:#010x}")
        first, second = struct.unpack("<HH", raw)
        actual = thumb_bl_target(address, first, second)
        if actual != target:
            raise AuditError(
                f"outgoing call at {address:#010x} targets {actual!r}, not {target:#x}"
            )
        outgoing.append({"address": address, "target": target, "provider": name})

    pointer = struct.unpack(
        "<I", image_slice(blob, ERROR_POINTER_SLOT, ERROR_POINTER_SLOT + 4)
    )[0]
    if pointer != ERROR_ADDRESS:
        raise AuditError("invalid-wire-type literal slot changed")
    error = image_slice(blob, ERROR_ADDRESS, ERROR_ADDRESS + len(ERROR_BYTES))
    if error != ERROR_BYTES or sha256(error) != ERROR_SHA256:
        raise AuditError("invalid-wire-type diagnostic bytes changed")

    upstream = UPSTREAM.read_bytes()
    if len(upstream) != UPSTREAM_SIZE or sha256(upstream) != UPSTREAM_SHA256:
        raise AuditError("authenticated nanopb source identity mismatch")
    source_start, source_end, source_hash = UPSTREAM_DEFINITION
    definition = upstream[source_start:source_end]
    if sha256(definition) != source_hash:
        raise AuditError("authenticated pb_skip_field definition mismatch")
    required_source_tokens = (
        b"case PB_WT_VARINT: return pb_skip_varint(stream);",
        b"case PB_WT_64BIT: return pb_read(stream, NULL, 8);",
        b"case PB_WT_STRING: return pb_skip_string(stream);",
        b"case PB_WT_32BIT: return pb_read(stream, NULL, 4);",
        b'PB_RETURN_ERROR(stream, "invalid wire_type")',
    )
    if not all(token in definition for token in required_source_tokens):
        raise AuditError("pb_skip_field upstream behavior tokens changed")

    config = CONFIG.read_bytes()
    if (
        b"defined(PB_NO_ERRMSG)" not in config
        or b"retains runtime error strings" not in config
    ):
        raise AuditError("G2 nanopb error-string configuration pin is missing")

    return {
        "image": {
            "path": str(image),
            "size": len(blob),
            "sha256": sha256(blob),
            "load_base": LOAD_BASE,
        },
        "stock": {
            "name": "pb_skip_field",
            "start": DISPATCHER[0],
            "end": DISPATCHER[1],
            "size": DISPATCHER[1] - DISPATCHER[0],
            "sha256": DISPATCHER[2],
            "callers": [
                {"address": address, "encoding": encoding}
                for address, encoding in callers.items()
            ],
            "outgoing": outgoing,
            "error_pointer_slot": ERROR_POINTER_SLOT,
            "error_address": ERROR_ADDRESS,
            "error_sha256": ERROR_SHA256,
        },
        "upstream": {
            "selected_commit": UPSTREAM_COMMIT,
            "compatibility_range": "0.4.7--0.4.9",
            "definition_start": source_start,
            "definition_end": source_end,
            "definition_size": len(definition),
            "definition_sha256": source_hash,
        },
        "decision": {
            "status": "production-integrated for apple-clang",
            "ready_for_promotion": False,
            "remaining_gate": (
                "reproduce target object, placement, and aggregates with the "
                "reviewed Homebrew Clang 22.1.8 profile"
            ),
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        report = analyze(arguments.image)
    except (AuditError, OSError) as error:
        parser.exit(1, f"error: {error}\n")

    if arguments.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        stock = report["stock"]
        upstream = report["upstream"]
        print(
            f"authenticated pb_skip_field {stock['start']:#010x}..."
            f"{stock['end']:#010x} ({stock['size']} bytes)"
        )
        print(
            f"callers={len(stock['callers'])} outgoing={len(stock['outgoing'])} "
            f"nanopb={upstream['compatibility_range']} selected="
            f"{upstream['selected_commit']}"
        )
        print("status=production-integrated for apple-clang; linux-clang pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
