#!/usr/bin/env python3
"""Fail-closed source-boundary and short-enum ABI audit for G2 ``pb_decode_tag``."""

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
START = 0x0048_F66C
END = 0x0048_F6A0
STOCK_SHA256 = "727a94d16ba7b4018c3addee83a6c63e87f0c3f2a3fe6afdb315549d10f53114"
EXPECTED_CALLERS = (
    (0x0048_FE2A, "fff71ffc"),
    (0x0048_FE5E, "fff705fc"),
    (0x0048_FF68, "fff780fb"),
)
CALLER_CONTEXTS = (
    (0x0048_FE1E, 0x0048_FE36, "d422a51f8fe44545d3fb046a1c81d6b750465cbe731c932fa0d446822be78f2e"),
    (0x0048_FE52, 0x0048_FE6A, "35263a54c7095bada0fc499aac205fa2ae77adb7fd1622e63c2816148d255c4e"),
    (0x0048_FF5C, 0x0048_FF74, "dfcfc277e3191ec34bf664f1b71acd4738e1aeb3333cf26fe84168c28d4c8846"),
)
EXPECTED_CALL = (
    0x0048_F682,
    0x0048_F4B8,
    "fff719ff",
    "open_cfw_nanopb_decode_varint32_eof",
)
UPSTREAM_DEFINITION = (
    8_663,
    9_043,
    "6cb0e89f976070f9d561474343e0ef46414107bbf64cbb17302be46dba412cfb",
)
NEIGHBORS = (
    ("pb_skip_string", 0x0048_F64C, START,
     "03afe2d60436676fffba342c7b8c9504992fa903d7cba768396fd1de2c6c66cd"),
    ("pb_skip_field", END, 0x0048_F6EA,
     "36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d"),
)
SHORT_ENUM_STORES = (
    (0x0048_F674, "1970", "eof false byte store"),
    (0x0048_F678, "2170", "wire type zero byte store"),
    (0x0048_F69A, "2070", "decoded wire type byte store"),
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

    patterns = []
    for target in range(START, END, 2):
        for stored in (target, target | 1):
            needle = struct.pack("<I", stored)
            offset = blob.find(needle)
            while offset >= 0:
                patterns.append((shared.LOAD_BASE + offset, target, stored))
                offset = blob.find(needle, offset + 1)
    return {"direct": direct, "interior": interior, "stored_patterns": patterns}


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != shared.IMAGE_SIZE or sha256(blob) != shared.IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")
    upstream = UPSTREAM.read_bytes()
    if len(upstream) != shared.UPSTREAM_SIZE or sha256(upstream) != shared.UPSTREAM_SHA256:
        raise AuditError("authenticated nanopb source identity mismatch")
    stock = shared.image_slice(blob, START, END)
    if sha256(stock) != STOCK_SHA256:
        raise AuditError("pb_decode_tag stock body changed")

    ingress = scan_ingress(blob)
    if tuple(ingress["direct"]["bl"]) != EXPECTED_CALLERS:
        raise AuditError(f"pb_decode_tag callers changed: {ingress['direct']['bl']!r}")
    if any(ingress["direct"][kind] for kind in ("bw", "conditional", "narrow")):
        raise AuditError("unexpected non-BL entry ingress")
    if ingress["interior"] or ingress["stored_patterns"]:
        raise AuditError("alternate branch or stored-pointer ingress detected")
    for start, end, digest in CALLER_CONTEXTS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError(f"caller context changed at {start:#x}")

    site, target, encoding, provider = EXPECTED_CALL
    raw = shared.image_slice(blob, site, site + 4)
    first, second = struct.unpack("<HH", raw)
    if raw.hex() != encoding or shared.thumb_bl_target(site, first, second) != target:
        raise AuditError("varint32/eof provider call changed")
    for address, encoding, _meaning in SHORT_ENUM_STORES:
        if shared.image_slice(blob, address, address + 2).hex() != encoding:
            raise AuditError(f"short-enum store changed at {address:#x}")

    source_start, source_end, source_digest = UPSTREAM_DEFINITION
    definition = upstream[source_start:source_end]
    if sha256(definition) != source_digest:
        raise AuditError("pb_decode_tag upstream definition changed")
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
        "outgoing": {"site": site, "target": target, "provider": provider,
                     "ownership": "source"},
        "short_enum_abi": {"pb_wire_type_t_bits": 8,
                           "stores": SHORT_ENUM_STORES},
        "upstream": {"commit": shared.UPSTREAM_COMMIT,
                     "compatibility_baseline": "nanopb-0.4.9",
                     "compatible_pristine_range": "0.4.7--0.4.9",
                     "definition_start": source_start, "definition_end": source_end,
                     "definition_sha256": source_digest},
        "neighbors": neighbors,
        "decision": {"production_candidate": True,
                     "fixed_stock_executable_seams": 0,
                     "stock_data_seams": 0},
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
        print("nanopb pb_decode_tag: 52 stock bytes; source candidate with one source-owned provider")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
