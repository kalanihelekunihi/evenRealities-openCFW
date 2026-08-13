#!/usr/bin/env python3
"""Fail-closed source-boundary audit for G2 nanopb ``pb_dec_submessage``."""

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
START = 0x0049_048C
END = 0x0049_0538
STOCK_SHA256 = "3e28ac2fb953613cff7b8a7c30cfdc91aa6c585ea44769e7f64603be853f6f91"
EXPECTED_CALLERS = ((0x0048_F92C, "00f0aefd"),)
CALLER_ADDRESS_SHA256 = "9cf45d77d33e2071d3a218f916571e367cf613ffc3d8349d615e1aed9b6511d3"
CALLER_RECORD_SHA256 = "e495ed6e8d76d6ffacaf2829a7aafe8a02fa9626a4ba9661f9d61d863e8504e7"
CALLER_CONTEXT = (
    0x0048_F91C,
    0x0048_F93C,
    "a4bbec593191b79816a83c6a24fc8a3f4573d0706b8870dd4f38c2ea9d867ded",
)
EXPECTED_CALLS = (
    (0x0049_049C, 0x0048_F77E, "fff76ff9", "open_cfw_nanopb_make_string_substream", "source"),
    (0x0049_051A, 0x0048_FE98, "fff7bdfc", "open_cfw_nanopb_decode_inner", "stock"),
    (0x0049_0524, 0x0048_F7CA, "fff751f9", "open_cfw_nanopb_close_string_substream", "source"),
)
UPSTREAM_DEFINITION = (
    49_908,
    51_557,
    "94000cbd5547153805c6b687cb80650a6f57cf9a030434cbf179cfde94ae3f4e",
)
DIAGNOSTIC = (
    0x0049_05D8,
    0x0076_F454,
    "invalid field descriptor",
    (0x0049_04B8,),
)
EXPECTED_STORED_PATTERNS = (
    (0x004B_29DF, 0x0049_04FC, 0x0049_04FC, 0x04FC, 0x0049),
)
COLLISION_CONTEXT = (
    0x004B_29D0,
    0x004B_29F2,
    "5fd8bf531f028807afc495f5b09e3d3cc4ac6c6eb438c522e2ad43cbc480c078",
)
NEIGHBORS = (
    ("predecessor_literal_island", 0x0049_0488, START,
     "f7f19bacfc4d8f9f6d541ca42347ee12eb069b9b747b03ab956e69e5d7b146b9"),
    ("successor_literal_island", END, 0x0049_053C,
     "79edc4298bda54d26053f342faa20def41ac5510a2f52928400c004cdb621647"),
    ("pb_dec_fixed_length_bytes", 0x0049_053C, 0x0049_05A8,
     "2f282fbafb16067744bf97e165493de53f4f0a2d1bb6f6e23f1becae7aede9d1"),
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
                address = shared.LOAD_BASE + offset
                low, high = struct.unpack_from("<HH", blob, offset)
                patterns.append((address, target, stored, low, high))
                offset = blob.find(needle, offset + 1)
    return {"direct": direct, "interior": interior, "stored_patterns": patterns}


def literal_loads(blob: bytes, slot: int) -> tuple[int, ...]:
    loads = []
    for site in range(START, END - 1, 2):
        first = struct.unpack("<H", shared.image_slice(blob, site, site + 2))[0]
        target = (((site + 4) & ~3) + (first & 0xFF) * 4
                  if first & 0xF800 == 0x4800 else None)
        if target == slot:
            loads.append(site)
    return tuple(loads)


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != shared.IMAGE_SIZE or sha256(blob) != shared.IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")
    upstream = UPSTREAM.read_bytes()
    if len(upstream) != shared.UPSTREAM_SIZE or sha256(upstream) != shared.UPSTREAM_SHA256:
        raise AuditError("authenticated nanopb source identity mismatch")

    stock = shared.image_slice(blob, START, END)
    if sha256(stock) != STOCK_SHA256:
        raise AuditError("pb_dec_submessage stock body changed")
    ingress = scan_ingress(blob)
    if tuple(ingress["direct"]["bl"]) != EXPECTED_CALLERS:
        raise AuditError(f"pb_dec_submessage BL callers changed: {ingress['direct']['bl']!r}")
    if any(ingress["direct"][kind] for kind in ("bw", "conditional", "narrow")):
        raise AuditError("unexpected non-BL entry ingress")
    if ingress["interior"]:
        raise AuditError("pb_dec_submessage has alternate branch ingress")
    if tuple(ingress["stored_patterns"]) != EXPECTED_STORED_PATTERNS:
        raise AuditError("pb_dec_submessage stored-pattern classification changed")

    address_bytes = b"".join(struct.pack("<I", item[0]) for item in EXPECTED_CALLERS)
    record_bytes = b"".join(struct.pack("<I", address) + bytes.fromhex(encoding)
                            for address, encoding in EXPECTED_CALLERS)
    if sha256(address_bytes) != CALLER_ADDRESS_SHA256 or sha256(record_bytes) != CALLER_RECORD_SHA256:
        raise AuditError("caller topology digest changed")
    context_start, context_end, context_hash = CALLER_CONTEXT
    if sha256(shared.image_slice(blob, context_start, context_end)) != context_hash:
        raise AuditError("decode_static_field caller context changed")
    collision_start, collision_end, collision_hash = COLLISION_CONTEXT
    if sha256(shared.image_slice(blob, collision_start, collision_end)) != collision_hash:
        raise AuditError("unaligned instruction-byte collision context changed")

    outgoing = []
    for site, target, encoding, provider, ownership in EXPECTED_CALLS:
        raw = shared.image_slice(blob, site, site + 4)
        first, second = struct.unpack("<HH", raw)
        if raw.hex() != encoding or shared.thumb_bl_target(site, first, second) != target:
            raise AuditError(f"provider call changed at {site:#x}")
        outgoing.append({"site": site, "target": target, "provider": provider, "ownership": ownership})

    slot, address, text, expected_loads = DIAGNOSTIC
    if struct.unpack("<I", shared.image_slice(blob, slot, slot + 4))[0] != address:
        raise AuditError("diagnostic pointer slot changed")
    if shared.image_slice(blob, address, address + len(text) + 1) != text.encode() + b"\0":
        raise AuditError("diagnostic string changed")
    loads = literal_loads(blob, slot)
    if loads != expected_loads:
        raise AuditError("diagnostic literal load changed")

    source_start, source_end, source_hash = UPSTREAM_DEFINITION
    if sha256(upstream[source_start:source_end]) != source_hash:
        raise AuditError("pb_dec_submessage upstream definition changed")
    neighbors = []
    for name, start, end, digest in NEIGHBORS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError(f"{name} boundary changed")
        neighbors.append({"name": name, "start": start, "end": end, "sha256": digest})

    return {
        "image": {"size": len(blob), "sha256": sha256(blob), "load_base": shared.LOAD_BASE},
        "stock": {"start": START, "end": END, "size": len(stock), "sha256": STOCK_SHA256},
        "upstream": {"commit": shared.UPSTREAM_COMMIT, "compatibility_baseline": "nanopb-0.4.9",
                     "compatible_pristine_range": "0.4.7--0.4.9", "definition_start": source_start,
                     "definition_end": source_end, "definition_sha256": source_hash},
        "ingress": ingress,
        "stored_pattern_classification": "one unaligned instruction-byte collision; no pointer ingress",
        "outgoing": outgoing,
        "dynamic_callback": {"count": 1, "site": 0x0049_04E4, "kind": "message decode callback ABI"},
        "diagnostic": {"slot": slot, "address": address, "text": text, "loads": loads},
        "neighbors": neighbors,
        "configuration": {"PB_DECODE_NOINIT": 1, "pb_size_t_bits": 16, "size_t_bits": 32},
        "decision": {"production_integrated": True, "executable_stock_seams": 1,
                     "stock_data_seams": 0, "dynamic_callback_seams": 1,
                     "closure": "source-owned make/close helpers, local diagnostic, retained stock pb_decode_inner"},
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
        print(f"nanopb pb_dec_submessage: {report['stock']['size']} stock bytes; "
              "production-integrated with one fixed stock seam plus one dynamic callback seam")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
