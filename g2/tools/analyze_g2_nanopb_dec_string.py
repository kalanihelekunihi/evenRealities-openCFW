#!/usr/bin/env python3
"""Fail-closed source-boundary audit for G2 nanopb ``pb_dec_string``."""

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
START = 0x0049_03EA
END = 0x0049_0488
STOCK_SHA256 = "8be0060c8134054cbe4964c682b8b2c22aa6dc170bdf235d3fee97220aaded2f"
EXPECTED_CALLERS = ((0x0048_F90A, "00f06efd"),)
CALLER_ADDRESS_SHA256 = "a47c2c2f311117ed8061190f3e8f5f0fac13fb4ef98b7d32db420b11bee96299"
CALLER_RECORD_SHA256 = "2805361f141a407619453f9c99d5d62ee49b37e5d02a5fbf05efa63913b03cc1"
CALLER_CONTEXT = (
    0x0048_F8FA,
    0x0048_F91A,
    "18266aa7fd75c47de34fe4107856c38bae9c17305ccd97ce1ab90ca2ece74ad8",
)
EXPECTED_CALLS = (
    (0x0049_03F6, 0x0048_F5AE, "fff7daf8", "open_cfw_nanopb_decode_varint32"),
    (0x0049_0478, 0x0048_F3BE, "fef7a1ff", "open_cfw_nanopb_read"),
)
UPSTREAM_DEFINITION = (
    48_677,
    49_908,
    "73375d35f4938cd170ac34eb6f32668fcdf253c9b850955524e3a8e5357f8646",
)
LITERAL_SLOTS = (
    (0x0049_05AC, 0x0078_1804, "no malloc support"),
    (0x0049_05D0, 0x0078_7C90, "size too large"),
    (0x0049_05D4, 0x0078_7CE0, "string overflow"),
)
LITERAL_LOADS = {
    0x0049_05AC: (0x0049_044C,),
    0x0049_05D0: (0x0049_0414, 0x0049_0430),
    0x0049_05D4: (0x0049_0464,),
}
NEIGHBORS = (
    ("pb_dec_bytes", 0x0049_0358, START,
     "c7543cf3079885d044833361ff8331ac10403760377ba3448419255ccae74c37"),
    ("successor_literal_island", END, 0x0049_048C,
     "f7f19bacfc4d8f9f6d541ca42347ee12eb069b9b747b03ab956e69e5d7b146b9"),
    ("pb_dec_submessage", 0x0049_048C, 0x0049_0538,
     "3e28ac2fb953613cff7b8a7c30cfdc91aa6c585ea44769e7f64603be853f6f91"),
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
        target = (
            ((site + 4) & ~3) + (first & 0x00FF) * 4
            if first & 0xF800 == 0x4800 else None
        )
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
        raise AuditError("pb_dec_string stock body changed")
    ingress = scan_ingress(blob)
    if tuple(ingress["direct"]["bl"]) != EXPECTED_CALLERS:
        raise AuditError(f"pb_dec_string BL callers changed: {ingress['direct']['bl']!r}")
    if any(ingress["direct"][kind] for kind in ("bw", "conditional", "narrow")):
        raise AuditError("unexpected non-BL entry ingress")
    if ingress["interior"]:
        raise AuditError("pb_dec_string has alternate branch ingress")
    if ingress["stored_patterns"]:
        raise AuditError("pb_dec_string has stored entry/interior address patterns")

    address_bytes = b"".join(struct.pack("<I", item[0]) for item in EXPECTED_CALLERS)
    record_bytes = b"".join(
        struct.pack("<I", address) + bytes.fromhex(encoding)
        for address, encoding in EXPECTED_CALLERS
    )
    if sha256(address_bytes) != CALLER_ADDRESS_SHA256 or sha256(record_bytes) != CALLER_RECORD_SHA256:
        raise AuditError("caller topology digest changed")
    context_start, context_end, context_hash = CALLER_CONTEXT
    if sha256(shared.image_slice(blob, context_start, context_end)) != context_hash:
        raise AuditError("decode_static_field caller context changed")

    outgoing = []
    for site, target, encoding, provider in EXPECTED_CALLS:
        raw = shared.image_slice(blob, site, site + 4)
        first, second = struct.unpack("<HH", raw)
        if raw.hex() != encoding or shared.thumb_bl_target(site, first, second) != target:
            raise AuditError(f"provider call changed at {site:#x}")
        outgoing.append({"site": site, "target": target, "provider": provider})

    diagnostics = []
    for slot, address, text in LITERAL_SLOTS:
        if struct.unpack("<I", shared.image_slice(blob, slot, slot + 4))[0] != address:
            raise AuditError(f"diagnostic pointer slot changed at {slot:#x}")
        string = shared.image_slice(blob, address, address + len(text) + 1)
        if string != text.encode("ascii") + b"\0":
            raise AuditError(f"diagnostic string changed at {address:#x}")
        loads = literal_loads(blob, slot)
        if loads != LITERAL_LOADS[slot]:
            raise AuditError(f"diagnostic loads changed for slot {slot:#x}")
        diagnostics.append({"slot": slot, "address": address, "text": text, "loads": loads})

    source_start, source_end, source_hash = UPSTREAM_DEFINITION
    if sha256(upstream[source_start:source_end]) != source_hash:
        raise AuditError("pb_dec_string upstream definition changed")
    neighbors = []
    for name, start, end, digest in NEIGHBORS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError(f"{name} boundary changed")
        neighbors.append({"name": name, "start": start, "end": end, "sha256": digest})

    return {
        "image": {"size": len(blob), "sha256": sha256(blob), "load_base": shared.LOAD_BASE},
        "stock": {"start": START, "end": END, "size": len(stock), "sha256": STOCK_SHA256},
        "upstream": {
            "commit": shared.UPSTREAM_COMMIT,
            "compatibility_baseline": "nanopb-0.4.9",
            "compatible_pristine_range": "0.4.7--0.4.9",
            "definition_start": source_start,
            "definition_end": source_end,
            "definition_sha256": source_hash,
        },
        "ingress": ingress,
        "outgoing": outgoing,
        "diagnostics": diagnostics,
        "neighbors": neighbors,
        "configuration": {
            "PB_ENABLE_MALLOC": False,
            "PB_VALIDATE_UTF8": False,
            "pb_size_t_bits": 16,
            "size_t_bits": 32,
        },
        "decision": {
            "production_integrated": True,
            "executable_stock_seams": 0,
            "stock_data_seams": 0,
            "closure": "source-owned pb_decode_varint32, pb_read, and local diagnostics",
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
        print(
            f"nanopb pb_dec_string: {report['stock']['size']} stock bytes; "
            "production-integrated for apple-clang; linux-clang pending"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
