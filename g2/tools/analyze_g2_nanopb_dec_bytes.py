#!/usr/bin/env python3
"""Fail-closed source-boundary audit for G2 nanopb ``pb_dec_bytes``."""

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
START = 0x0049_0358
END = 0x0049_03EA
STOCK_SHA256 = "c7543cf3079885d044833361ff8331ac10403760377ba3448419255ccae74c37"
EXPECTED_CALLERS = ((0x0048_F8E8, "00f036fd"),)
CALLER_ADDRESS_SHA256 = "c682d51419d5c10c414ad0bb61bfea223b4a238ebf78817a7125b5c215b2a6cb"
CALLER_RECORD_SHA256 = "199a78e75f8c403796b8f557ffddcb017009a0ddd6159f290b51823f560e6055"
EXPECTED_CALLS = (
    (0x0049_0362, 0x0048_F5AE, "fff724f9", "open_cfw_nanopb_decode_varint32"),
    (0x0049_03E4, 0x0048_F3BE, "fef7ebff", "open_cfw_nanopb_read"),
)
UPSTREAM_DEFINITION = (
    47_571,
    48_677,
    "343c9c20cbd27012513eac9e7950d3c7d03733bb318d608be2f2538c44705374",
)
LITERAL_SLOTS = (
    (0x0049_05AC, 0x0078_1804, "no malloc support"),
    (0x0049_05CC, 0x0078_7CD0, "bytes overflow"),
    (0x0049_05D0, 0x0078_7C90, "size too large"),
)
LITERAL_LOADS = {
    0x0049_05AC: (0x0049_03B8,),
    0x0049_05CC: (0x0049_0380, 0x0049_03D0),
    0x0049_05D0: (0x0049_039C,),
}
NEIGHBORS = (
    ("boundary_literal_island", 0x0049_0352, START,
     "21ce7bac3d5f13a0ceb363b9740d84e8d0a487bb76e9e2c509528038f2a683b8"),
    ("pb_dec_string", END, 0x0049_0488,
     "8be0060c8134054cbe4964c682b8b2c22aa6dc170bdf235d3fee97220aaded2f"),
)
EXPECTED_DATA_COLLISIONS = (
    (0x0064_D2E0, 0x0049_0380, 0x0049_0381, 0x0381, 0x0049),
    (0x0064_E164, 0x0049_03B6, 0x0049_03B7, 0x03B7, 0x0049),
)
COLLISION_CONTEXTS = (
    (0x0064_D2D0, 0x0064_D300,
     "43481a9e88704a7562acdd0074e0bc075e2c058d213bf4a62fa4d96cbfe7de8d"),
    (0x0064_E154, 0x0064_E184,
     "f46c33eb6145c25296a8bd40d6bce35519fdc06a5569727ed1c7a7c973e7918a"),
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
    for site in range(START, END - 3, 2):
        first, second = struct.unpack("<HH", shared.image_slice(blob, site, site + 4))
        wide_target = (
            ((site + 4) & ~3) + (second & 0x0FFF)
            if first == 0xF8DF else None
        )
        narrow_target = (
            ((site + 4) & ~3) + (first & 0x00FF) * 4
            if first & 0xF800 == 0x4800 else None
        )
        if slot in (wide_target, narrow_target):
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
        raise AuditError("pb_dec_bytes stock body changed")
    ingress = scan_ingress(blob)
    if tuple(ingress["direct"]["bl"]) != EXPECTED_CALLERS:
        raise AuditError(f"pb_dec_bytes BL callers changed: {ingress['direct']['bl']!r}")
    if any(ingress["direct"][kind] for kind in ("bw", "conditional", "narrow")):
        raise AuditError("unexpected non-BL entry ingress")
    if ingress["interior"]:
        raise AuditError("pb_dec_bytes has alternate branch ingress")
    if tuple(ingress["stored_patterns"]) != EXPECTED_DATA_COLLISIONS:
        raise AuditError("stored interior-address pattern census changed")
    for start, end, digest in COLLISION_CONTEXTS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError("16-bit collision-table context changed")

    address_bytes = b"".join(struct.pack("<I", item[0]) for item in EXPECTED_CALLERS)
    record_bytes = b"".join(
        struct.pack("<I", address) + bytes.fromhex(encoding)
        for address, encoding in EXPECTED_CALLERS
    )
    if sha256(address_bytes) != CALLER_ADDRESS_SHA256 or sha256(record_bytes) != CALLER_RECORD_SHA256:
        raise AuditError("caller topology digest changed")

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
    definition = upstream[source_start:source_end]
    if sha256(definition) != source_hash:
        raise AuditError("pb_dec_bytes upstream definition changed")
    neighbors = []
    for name, start, end, digest in NEIGHBORS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError(f"{name} boundary changed")
        neighbors.append({"name": name, "start": start, "end": end, "sha256": digest})

    collisions = [
        {
            "address": item[0], "interior_even_value": item[1],
            "stored_thumb_value": item[2], "uint16_pair": [item[3], item[4]],
            "classification": "non-pointer 16-bit data-pair record",
        }
        for item in EXPECTED_DATA_COLLISIONS
    ]
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
        "ingress": {**ingress, "classified_data_collisions": collisions},
        "outgoing": outgoing,
        "diagnostics": diagnostics,
        "neighbors": neighbors,
        "configuration": {"PB_ENABLE_MALLOC": False, "pb_size_t_bits": 16},
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
            f"nanopb pb_dec_bytes: {report['stock']['size']} stock bytes; "
            "production-integrated for apple-clang; linux-clang pending; "
            "two classified non-pointer data collisions"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
