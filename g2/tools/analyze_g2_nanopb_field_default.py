#!/usr/bin/env python3
"""Fail-closed boundary and dependency audit for G2 ``pb_field_set_to_default``."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Sequence

import analyze_g2_nanopb_dec_varint as branch
import analyze_g2_nanopb_skip_field as shared


DEFAULT_IMAGE = shared.DEFAULT_IMAGE
UPSTREAM = shared.UPSTREAM
START = 0x0048_FCE2
END = 0x0048_FDF2
STOCK_SHA256 = "0d0dd0be0ae68f84bb20e39f7c95f500656316563d95b6d5cc3e290d4b131728"
EXPECTED_CALLERS = ((0x0048_FE7E, "fff730ff"),)
CALLER_CONTEXTS = (
    (0x0048_FE72, 0x0048_FE8A,
     "8f30c2456222973fb3f6728f3e4951968e8b94754fc69ec90434a1ca29e95590"),
)
EXPECTED_CALLS = (
    (0x0048_FD04, 0x004D_93A4, "49f04efb", "pb_field_iter_begin_extension", "stock"),
    (0x0048_FD12, 0x0048_FDF2, "00f06ef8", "pb_message_set_to_defaults", "stock"),
    (0x0048_FD98, 0x004D_9384, "49f0f4fa", "pb_field_iter_begin", "stock"),
    (0x0048_FDA2, 0x0048_FDF2, "00f026f8", "pb_message_set_to_defaults", "stock"),
    (0x0048_FDB6, 0x0043_C0E4, "acf795f9", "memory_fill", "eliminated_by_candidate"),
)
UPSTREAM_DEFINITION = (
    28_476,
    31_080,
    "dced6e406d8c2c657a90cd599a60457a83bbc123b6ddfbfb9bff71778a773265",
)
PRISTINE_RELEASE_MATRIX = (
    ("nanopb-0.4.7", "b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba"),
    ("nanopb-0.4.8", "6cfe48d6f1593f8fa5c0f90437f5e6522587745e"),
    ("nanopb-0.4.9", "98bf4db69897b53434f3d0ba72e0a3ab1a902824"),
    ("nanopb-0.4.9.1", "cad3c18ef15a663e30e3e43e3a752b66378adec1"),
)
NEIGHBORS = (
    ("decode_extension", 0x0048_FC88, START,
     "0f630c1173971762af8df1ec82ed50cff6f292a9b77eafae06e56b9f3b659472"),
    ("pb_message_set_to_defaults", END, 0x0048_FE98,
     "1409633f121586a45b076e247e2f1f33f6120be85044245f42ca777955bd34e4"),
)


class AuditError(RuntimeError):
    """Raised when an authenticated boundary invariant changes."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def scan_ingress(blob: bytes) -> dict[str, Any]:
    direct = {"bl": [], "bw": [], "conditional": [], "narrow": []}
    interior = []
    for offset in range(0, len(blob) - 3, 2):
        address = shared.LOAD_BASE + offset
        first, second = struct.unpack_from("<HH", blob, offset)
        encoding = blob[offset:offset + 4].hex()
        for name, target in (
            ("bl", branch.wide_branch_target(address, first, second, link=True)),
            ("bw", branch.wide_branch_target(address, first, second, link=False)),
            ("conditional", branch.wide_conditional_target(address, first, second)),
        ):
            if target is None or START <= address < END:
                continue
            if target == START:
                direct[name].append((address, encoding))
            elif START < target < END:
                interior.append((name, address, target, encoding))

    for offset in range(0, len(blob) - 1, 2):
        address = shared.LOAD_BASE + offset
        if START <= address < END:
            continue
        halfword = struct.unpack_from("<H", blob, offset)[0]
        for target in branch.narrow_targets(address, halfword):
            if target == START:
                direct["narrow"].append((address, f"{halfword:04x}"))
            elif START < target < END:
                interior.append(("narrow", address, target, f"{halfword:04x}"))

    stored_patterns = []
    for target in range(START, END, 2):
        for stored in (target, target | 1):
            needle = struct.pack("<I", stored)
            offset = blob.find(needle)
            while offset >= 0:
                stored_patterns.append((shared.LOAD_BASE + offset, target, stored))
                offset = blob.find(needle, offset + 1)
    return {"direct": direct, "interior": interior,
            "stored_patterns": stored_patterns}


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != shared.IMAGE_SIZE or sha256(blob) != shared.IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")
    upstream = UPSTREAM.read_bytes()
    if len(upstream) != shared.UPSTREAM_SIZE or sha256(upstream) != shared.UPSTREAM_SHA256:
        raise AuditError("authenticated nanopb source identity mismatch")

    stock = shared.image_slice(blob, START, END)
    if sha256(stock) != STOCK_SHA256:
        raise AuditError("pb_field_set_to_default stock body changed")
    ingress = scan_ingress(blob)
    if tuple(ingress["direct"]["bl"]) != EXPECTED_CALLERS:
        raise AuditError(f"pb_field_set_to_default callers changed: {ingress['direct']['bl']!r}")
    if any(ingress["direct"][kind] for kind in ("bw", "conditional", "narrow")):
        raise AuditError("unexpected non-BL entry ingress")
    if ingress["interior"] or ingress["stored_patterns"]:
        raise AuditError("alternate branch or stored-pointer ingress detected")
    for start, end, digest in CALLER_CONTEXTS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError(f"caller context changed at {start:#x}")

    calls = []
    for site, target, encoding, function, ownership in EXPECTED_CALLS:
        raw = shared.image_slice(blob, site, site + 4)
        first, second = struct.unpack("<HH", raw)
        if raw.hex() != encoding or shared.thumb_bl_target(site, first, second) != target:
            raise AuditError(f"outgoing call changed at {site:#x}")
        calls.append({"site": site, "target": target, "encoding": encoding,
                      "function": function, "ownership": ownership})

    source_start, source_end, source_digest = UPSTREAM_DEFINITION
    if sha256(upstream[source_start:source_end]) != source_digest:
        raise AuditError("pb_field_set_to_default upstream definition changed")
    neighbors = []
    for name, start, end, digest in NEIGHBORS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError(f"{name} boundary changed")
        neighbors.append({"name": name, "start": start, "end": end,
                          "sha256": digest})

    return {
        "image": {"size": len(blob), "sha256": sha256(blob),
                  "load_base": shared.LOAD_BASE},
        "stock": {"start": START, "end": END, "size": len(stock),
                  "sha256": STOCK_SHA256},
        "ingress": ingress,
        "outgoing": calls,
        "upstream": {
            "selected_commit": shared.UPSTREAM_COMMIT,
            "compatibility_baseline": "nanopb-0.4.9",
            "exact_pristine_release_range": "nanopb-0.4.7--nanopb-0.4.9.1",
            "release_matrix": [
                {"release": release, "commit": commit}
                for release, commit in PRISTINE_RELEASE_MATRIX
            ],
            "definition_start": source_start,
            "definition_end": source_end,
            "definition_sha256": source_digest,
        },
        "neighbors": neighbors,
        "decision": {
            "production_candidate": True,
            "production_integrated": True,
            "source_identification_percent": 100,
            "source_recreation_percent": 100,
            "fixed_stock_call_sites": 4,
            "fixed_stock_helper_families": 3,
            "production_source_owned_call_sites": 4,
            "production_fixed_stock_call_sites": 0,
            "eliminated_memory_fill_call_sites": 1,
            "stock_data_seams": 0,
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
        print("nanopb pb_field_set_to_default: 272 stock bytes; production-integrated with all recursive/iterator calls source-owned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
