#!/usr/bin/env python3
"""Fail-closed source-boundary audit for G2 nanopb ``pb_dec_varint``."""

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
START = 0x0049_01D6
END = 0x0049_0352
STOCK_SHA256 = "ccae20aa7dff8515a5a2b6ad4a05248a865dfaa8c912fd38c8c5f77c3a6a8e0a"
EXPECTED_CALLERS = ((0x0048_F872, "00f0b0fc"),)
CALLER_ADDRESS_SHA256 = "1caf8859fd83af820c48f63d9cb9373bad8f74b56f1ef11a3c19517a6920f0b5"
CALLER_RECORD_SHA256 = "915f92293b0a44e365f929a5c3e1512239d00d7a67ca0de69122848a588e68b6"
EXPECTED_CALLS = (
    (0x0049_01EC, 0x0048_F5B8, "fff7e4f9", "open_cfw_nanopb_decode_varint"),
    (0x0049_0290, 0x0049_0150, "fff75eff", "open_cfw_nanopb_decode_svarint"),
    (0x0049_02A0, 0x0048_F5B8, "fff78af9", "open_cfw_nanopb_decode_varint"),
)
UPSTREAM_DEFINITION = (
    44_845,
    47_571,
    "be9044f37413d5f5ccacf8b94473552824d913037aa23ff853c59bd77c111b93",
)
LITERAL_SLOTS = (
    (0x0049_05C4, 0x0078_182C, "invalid data_size"),
    (0x0049_05C8, 0x0078_1840, "integer too large"),
)
LITERAL_LOADS = {
    0x0049_05C4: (0x0049_026A, 0x0049_033C),
    0x0049_05C8: (0x0049_0274, 0x0049_0344),
}
NEIGHBORS = (
    ("pb_dec_bool", 0x0049_01CC, START,
     "572c2ada01c7ee81d56e65766e4e7219783592d34f3399ee6bc761b7c494f3e7"),
    ("boundary_literal_island", END, 0x0049_0358,
     "21ce7bac3d5f13a0ceb363b9740d84e8d0a487bb76e9e2c509528038f2a683b8"),
    ("pb_dec_bytes", 0x0049_0358, 0x0049_03EA,
     "c7543cf3079885d044833361ff8331ac10403760377ba3448419255ccae74c37"),
)


class AuditError(RuntimeError):
    """Raised when an authenticated boundary invariant changes."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def wide_branch_target(
    address: int, first: int, second: int, *, link: bool
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = (
        sign << 24
        | (1 ^ (j1 ^ sign)) << 23
        | (1 ^ (j2 ^ sign)) << 22
        | (first & 0x03FF) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def wide_conditional_target(address: int, first: int, second: int) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if (first >> 6) & 0x0F >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        sign << 20
        | ((second >> 11) & 1) << 19
        | ((second >> 13) & 1) << 18
        | (first & 0x003F) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 21
    return address + 4 + immediate


def narrow_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if halfword & 0xF000 == 0xD000 and (halfword >> 8) & 0x0F < 0x0E:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return (address + 4 + immediate * 2,)
    return ()


def scan_ingress(blob: bytes) -> dict[str, Any]:
    direct = {"bl": [], "bw": [], "conditional": [], "narrow": []}
    interior = []
    for offset in range(0, len(blob) - 3, 2):
        address = shared.LOAD_BASE + offset
        first, second = struct.unpack_from("<HH", blob, offset)
        encoding = blob[offset:offset + 4].hex()
        for name, target in (
            ("bl", wide_branch_target(address, first, second, link=True)),
            ("bw", wide_branch_target(address, first, second, link=False)),
            ("conditional", wide_conditional_target(address, first, second)),
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
        for target in narrow_targets(address, halfword):
            if target == START:
                direct["narrow"].append((address, f"{halfword:04x}"))
            elif START < target < END:
                interior.append(("narrow", address, target, f"{halfword:04x}"))

    pointers = []
    for target in range(START, END, 2):
        for stored in (target, target | 1):
            needle = struct.pack("<I", stored)
            offset = blob.find(needle)
            while offset >= 0:
                pointers.append((shared.LOAD_BASE + offset, target, stored))
                offset = blob.find(needle, offset + 1)
    return {"direct": direct, "interior": interior, "pointers": pointers}


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != shared.IMAGE_SIZE or sha256(blob) != shared.IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")
    upstream = UPSTREAM.read_bytes()
    if len(upstream) != shared.UPSTREAM_SIZE or sha256(upstream) != shared.UPSTREAM_SHA256:
        raise AuditError("authenticated nanopb source identity mismatch")

    stock = shared.image_slice(blob, START, END)
    if sha256(stock) != STOCK_SHA256:
        raise AuditError("pb_dec_varint stock body changed")
    ingress = scan_ingress(blob)
    if tuple(ingress["direct"]["bl"]) != EXPECTED_CALLERS:
        raise AuditError(f"pb_dec_varint BL callers changed: {ingress['direct']['bl']!r}")
    if any(ingress["direct"][kind] for kind in ("bw", "conditional", "narrow")):
        raise AuditError("unexpected non-BL entry ingress")
    if ingress["interior"] or ingress["pointers"]:
        raise AuditError("pb_dec_varint has alternate interior ingress")
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
        slot_bytes = shared.image_slice(blob, slot, slot + 4)
        if struct.unpack("<I", slot_bytes)[0] != address:
            raise AuditError(f"diagnostic pointer slot changed at {slot:#x}")
        string = shared.image_slice(blob, address, address + len(text) + 1)
        if string != text.encode("ascii") + b"\0":
            raise AuditError(f"diagnostic string changed at {address:#x}")
        loads = []
        for site in range(START, END - 3, 2):
            first, second = struct.unpack("<HH", shared.image_slice(blob, site, site + 4))
            wide_target = (
                ((site + 4) & ~3) + (second & 0x0FFF)
                if first == 0xF8DF
                else None
            )
            narrow_target = (
                ((site + 4) & ~3) + (first & 0x00FF) * 4
                if first & 0xF800 == 0x4800
                else None
            )
            if slot in (wide_target, narrow_target):
                loads.append(site)
        if tuple(loads) != LITERAL_LOADS[slot]:
            raise AuditError(f"diagnostic loads changed for slot {slot:#x}")
        diagnostics.append({"slot": slot, "address": address, "text": text, "loads": loads})

    source_start, source_end, source_hash = UPSTREAM_DEFINITION
    definition = upstream[source_start:source_end]
    if sha256(definition) != source_hash:
        raise AuditError("pb_dec_varint upstream definition changed")
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
        "decision": {
            "production_integrated": True,
            "executable_stock_seams": 0,
            "stock_data_seams": 0,
            "closure": "source-owned pb_decode_varint, pb_decode_svarint, and local diagnostics",
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
            f"nanopb pb_dec_varint: {report['stock']['size']} stock bytes; "
            "status=production-integrated for apple-clang; linux-clang pending"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
