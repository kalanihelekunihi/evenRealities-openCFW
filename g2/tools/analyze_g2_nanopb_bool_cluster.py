#!/usr/bin/env python3
"""Fail-closed boundary audit for the G2 nanopb Boolean decoder pair."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Sequence

import analyze_g2_nanopb_skip_field as shared


DEFAULT_IMAGE = shared.DEFAULT_IMAGE
UPSTREAM = shared.UPSTREAM

FUNCTIONS = {
    "pb_decode_bool": (
        0x0049_012C,
        0x0049_0150,
        "946ebcb7df90360a19f331bbe5c3962deade8c0525ce4c3ef2d1698263e94b1e",
    ),
    "pb_dec_bool": (
        0x0049_01CC,
        0x0049_01D6,
        "572c2ada01c7ee81d56e65766e4e7219783592d34f3399ee6bc761b7c494f3e7",
    ),
}
EXPECTED_CALLERS = {
    "pb_decode_bool": {0x0049_01D0: "fff7acff"},
    "pb_dec_bool": {0x0048_F848: "00f0c0fc"},
}
EXPECTED_CALLS = {
    "pb_decode_bool": {
        0x0049_0132: (0x0048_F5AE, "open_cfw_nanopb_decode_varint32"),
    },
    "pb_dec_bool": {
        0x0049_01D0: (0x0049_012C, "open_cfw_nanopb_decode_bool"),
    },
}
UPSTREAM_DEFINITIONS = {
    "pb_decode_bool": (
        42_715,
        42_911,
        "5db66c94774daecd96a5daf5d83ff441462e4793a76638ef096f82d1c3a9c38f",
    ),
    "pb_dec_bool": (
        44_696,
        44_844,
        "e3e930719ed531df7d647cdf9ecd002c522c2d4d55e6f8299c258532713f6e6c",
    ),
}
NEIGHBORS = {
    "public_predecessor": (
        0x0049_00F0,
        0x0049_012C,
        "9803e737c4077072806ee8daa8563e132962a454c7960ce8db3acebdd2baf55e",
    ),
    "public_successor": (
        0x0049_0150,
        0x0049_0190,
        "80b24be422cf924f3ae1b79669312535dc0d5a56dd88be8a6b9e4ee5ff064048",
    ),
    "adapter_predecessor": (
        0x0049_01AC,
        0x0049_01CC,
        "96228dfbdfe30665d79281ba0fd5ba3b3af38701396671cd20b77623ffd82d54",
    ),
    "adapter_successor_head": (
        0x0049_01D6,
        0x0049_01EE,
        "b4b3e37793905de1f5396e19335b5b4b4252efba88146d34791706bfabbbe2fd",
    ),
}


class AuditError(RuntimeError):
    """Raised when an authenticated Boolean-cluster invariant changes."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != shared.IMAGE_SIZE or sha256(blob) != shared.IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")

    upstream = UPSTREAM.read_bytes()
    if len(upstream) != shared.UPSTREAM_SIZE or sha256(upstream) != shared.UPSTREAM_SHA256:
        raise AuditError("authenticated nanopb source identity mismatch")

    neighbors: dict[str, Any] = {}
    for name, (start, end, digest) in NEIGHBORS.items():
        body = shared.image_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"{name} boundary changed")
        neighbors[name] = {"start": start, "end": end, "sha256": digest}

    functions: dict[str, Any] = {}
    for name, (start, end, digest) in FUNCTIONS.items():
        body = shared.image_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"{name} stock body changed")
        callers = shared.scan_direct_callers(blob, start)
        if callers != EXPECTED_CALLERS[name]:
            raise AuditError(f"{name} direct caller topology changed: {callers!r}")

        outgoing = []
        for site, (target, provider) in EXPECTED_CALLS[name].items():
            raw = shared.image_slice(blob, site, site + 4)
            first, second = struct.unpack("<HH", raw)
            if shared.thumb_bl_target(site, first, second) != target:
                raise AuditError(f"{name} provider call changed at {site:#x}")
            outgoing.append(
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
            raise AuditError(f"{name} upstream definition changed")

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
                "outgoing": outgoing,
            },
            "upstream": {
                "start": source_start,
                "end": source_end,
                "size": len(definition),
                "sha256": source_digest,
            },
        }

    return {
        "image": {
            "path": str(image),
            "size": len(blob),
            "sha256": sha256(blob),
            "load_base": shared.LOAD_BASE,
        },
        "upstream": {
            "selected_commit": shared.UPSTREAM_COMMIT,
            "compatibility_baseline": "nanopb-0.4.9",
            "compatible_pristine_range": "0.4.7--0.4.9",
        },
        "functions": functions,
        "neighbors": neighbors,
        "decision": {
            "closure": (
                "pb_decode_bool over source-owned pb_decode_varint32; "
                "pb_dec_bool over source-owned pb_decode_bool"
            ),
            "stock_data_seams": 0,
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
        public = report["functions"]["pb_decode_bool"]["stock"]
        adapter = report["functions"]["pb_dec_bool"]["stock"]
        print(
            f"nanopb Boolean pair: pb_decode_bool={public['size']} bytes, "
            f"pb_dec_bool={adapter['size']} bytes"
        )
        print("status=production-integrated for apple-clang; linux-clang pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
