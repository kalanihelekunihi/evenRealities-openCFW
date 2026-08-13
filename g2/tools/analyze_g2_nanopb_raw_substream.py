#!/usr/bin/env python3
"""Fail-closed boundary audit for nanopb read_raw_value and substream creation."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Sequence

import analyze_g2_nanopb_skip_field as shared


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = shared.DEFAULT_IMAGE
UPSTREAM = shared.UPSTREAM
LOAD_BASE = shared.LOAD_BASE

FUNCTIONS = {
    "read_raw_value": (
        0x0048_F6EA,
        0x0048_F77E,
        "1e970a9b198943e309550811010fc1ba4008d671d023abfc5c893b965fee2bc9",
    ),
    "pb_make_string_substream": (
        0x0048_F77E,
        0x0048_F7CA,
        "db925e0c532bac2f2e38f398c7b7d99669afe4d41e6690b08116e9f06ec7d88d",
    ),
}
EXPECTED_CALLERS = {
    "read_raw_value": {0x0048_FBBE: "fff794fd"},
    "pb_make_string_substream": {
        0x0048_F9DA: "fff7d0fe",
        0x0048_FB56: "fff712fe",
        0x0049_049C: "fff76ff9",
    },
}
EXPECTED_CALLS = {
    "read_raw_value": {
        0x0048_F71A: (0x0048_F3BE, "open_cfw_nanopb_read"),
        0x0048_F754: (0x0048_F3BE, "open_cfw_nanopb_read"),
        0x0048_F764: (0x0048_F3BE, "open_cfw_nanopb_read"),
    },
    "pb_make_string_substream": {
        0x0048_F788: (0x0048_F5AE, "open_cfw_nanopb_decode_varint32"),
        0x0048_F79A: (0x0043_9C04, "retained___aeabi_memcpy"),
    },
}
ERRORS = {
    "varint_overflow": (
        0x0048_FC84,
        0x0078_7C80,
        b"varint overflow\0",
        "e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d",
    ),
    "invalid_wire_type": (
        0x0049_0118,
        0x0078_17DC,
        b"invalid wire_type\0",
        "6e35ebc2e585a3ca08ee2d60871a7d16749421ae2b6c1a33bb20c50175e1048a",
    ),
    "parent_stream_too_short": (
        0x0049_011C,
        0x0077_9F64,
        b"parent stream too short\0",
        "ad56a096e4d8599a2d1ab4eddf3012ca093e63ef13a6d99cabde7680d4ae0401",
    ),
}
UPSTREAM_DEFINITIONS = {
    "read_raw_value": (
        9_612,
        10_656,
        "a4c975f632934b80ee707520096f428a670516d4dc7368ac6c9a5959da83ded6",
    ),
    "pb_make_string_substream": (
        10_811,
        11_222,
        "2a7f4dcaef603858918bcc6eac47039308e336ee74d439af6abc257ddcd9a0d8",
    ),
}
MEMCPY_PROVIDER = (
    0x0043_9BE4,
    0x0043_9C8A,
    "8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd",
)
SUBSTREAM_COPY_CALL_WINDOW = (
    0x0048_F794,
    0x0048_F79E,
    "addbebce1de320dc5ebfd1dd97eea54a4b1e6b2678ef52db109c9015f2c03022",
)


class AuditError(RuntimeError):
    """Raised when an authenticated boundary changes."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return shared.image_slice(blob, start, end)


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != shared.IMAGE_SIZE or sha256(blob) != shared.IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")

    upstream = UPSTREAM.read_bytes()
    if len(upstream) != shared.UPSTREAM_SIZE or sha256(upstream) != shared.UPSTREAM_SHA256:
        raise AuditError("authenticated nanopb source identity mismatch")

    functions: dict[str, Any] = {}
    for name, (start, end, digest) in FUNCTIONS.items():
        body = image_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"{name} stock body changed")
        callers = shared.scan_direct_callers(blob, start)
        if callers != EXPECTED_CALLERS[name]:
            raise AuditError(f"{name} caller topology changed: {callers!r}")
        calls = []
        for site, (target, provider) in EXPECTED_CALLS[name].items():
            raw = image_slice(blob, site, site + 4)
            first, second = struct.unpack("<HH", raw)
            if shared.thumb_bl_target(site, first, second) != target:
                raise AuditError(f"{name} provider call changed at {site:#x}")
            calls.append(
                {
                    "address": site,
                    "target": target,
                    "provider": provider,
                    "encoding": raw.hex(),
                }
            )
        source_start, source_end, source_digest = UPSTREAM_DEFINITIONS[name]
        definition = upstream[source_start:source_end]
        if sha256(definition) != source_digest:
            raise AuditError(f"{name} authenticated upstream definition changed")
        functions[name] = {
            "stock": {
                "start": start,
                "end": end,
                "size": len(body),
                "sha256": digest,
                "callers": [
                    {"address": address, "encoding": encoding}
                    for address, encoding in callers.items()
                ],
                "outgoing": calls,
            },
            "upstream": {
                "start": source_start,
                "end": source_end,
                "size": len(definition),
                "sha256": source_digest,
            },
        }

    errors = {}
    for name, (slot, address, expected, digest) in ERRORS.items():
        pointer = struct.unpack("<I", image_slice(blob, slot, slot + 4))[0]
        data = image_slice(blob, address, address + len(expected))
        if pointer != address or data != expected or sha256(data) != digest:
            raise AuditError(f"{name} diagnostic seam changed")
        errors[name] = {
            "pointer_slot": slot,
            "address": address,
            "size": len(data),
            "sha256": digest,
        }

    memcpy_start, memcpy_end, memcpy_digest = MEMCPY_PROVIDER
    memcpy_body = image_slice(blob, memcpy_start, memcpy_end)
    if sha256(memcpy_body) != memcpy_digest:
        raise AuditError("authenticated __aeabi_memcpy provider changed")
    copy_start, copy_end, copy_digest = SUBSTREAM_COPY_CALL_WINDOW
    copy_window = image_slice(blob, copy_start, copy_end)
    if sha256(copy_window) != copy_digest:
        raise AuditError("pb_make_string_substream copy call setup changed")

    return {
        "image": {
            "path": str(image),
            "size": len(blob),
            "sha256": sha256(blob),
            "load_base": LOAD_BASE,
        },
        "upstream": {
            "selected_commit": shared.UPSTREAM_COMMIT,
            "compatibility_baseline": "nanopb-0.4.9",
        },
        "functions": functions,
        "diagnostics": errors,
        "stock_copy_seam": {
            "provider": "__aeabi_memcpy",
            "provider_start": memcpy_start,
            "provider_end": memcpy_end,
            "provider_size": len(memcpy_body),
            "provider_sha256": memcpy_digest,
            "aligned_interior_entry": 0x0043_9C04,
            "call_site": 0x0048_F79A,
            "call_window_start": copy_start,
            "call_window_end": copy_end,
            "call_window_sha256": copy_digest,
            "destination": "substream",
            "source": "parent stream",
            "count": 16,
            "candidate_policy": (
                "four named 32-bit ABI-field assignments; no compiler-runtime "
                "provider retained"
            ),
        },
        "decision": {
            "read_raw_value": "source-recreated over source-owned pb_read plus local rodata",
            "pb_make_string_substream": (
                "source-recreated with explicit four-field ABI copy"
            ),
            "production_integrated": True,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        report = analyze(arguments.image)
    except (AuditError, shared.AuditError, OSError) as error:
        parser.exit(1, f"error: {error}\n")
    if arguments.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        raw = report["functions"]["read_raw_value"]["stock"]
        sub = report["functions"]["pb_make_string_substream"]["stock"]
        print(
            f"nanopb next boundaries: read_raw_value={raw['size']} bytes, "
            f"pb_make_string_substream={sub['size']} bytes"
        )
        print(
            "status=read_raw_value and pb_make_string_substream "
            "production-integrated for apple-clang; "
            "no hardware operation"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
