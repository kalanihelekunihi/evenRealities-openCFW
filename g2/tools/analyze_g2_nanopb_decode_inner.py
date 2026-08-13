#!/usr/bin/env python3
"""Fail-closed source-boundary audit for G2 nanopb ``pb_decode_inner``."""

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
START = 0x0048_FE98
END = 0x0049_0112
STOCK_SHA256 = "13f2b83cd22ed38a6b74d52b0bd4eb6e8577becdcf5a1c8816a4af6aef1eea52"
EXPECTED_CALLERS = (
    (0x0049_0124, "fff7b8fe"),
    (0x0049_051A, "fff7bdfc"),
)
CALLER_ADDRESS_SHA256 = "f8fe3e1175baf06e17d29d81e9daaae0d69d0d54c76bbf230f1514dd18c0523d"
CALLER_RECORD_SHA256 = "e3a0681e6135ae4cb9b80b3ade029425006d12de51fd29f85bcea11a082da015"
CALLER_CONTEXTS = (
    (0x0049_0114, 0x0049_0134,
     "8d1345551bbbd6d048d7f72999887fc6b15d5804216deba69b8af2ed85346018"),
    (0x0049_050A, 0x0049_052A,
     "6833616ea8742c56fd26785ab4757f880d51634855771561986dcfacc0f1a4e6"),
)
EXPECTED_CALLS = (
    (0x0048_FEC0, 0x0043_C0E4, "acf710f9", "memory_fill", "eliminated"),
    (0x0048_FED0, 0x004D_9384, "49f058fa", "pb_field_iter_begin", "stock"),
    (0x0048_FEDE, 0x0048_FDF2, "fff788ff", "pb_message_set_to_defaults", "stock"),
    (0x0048_FF04, 0x004D_93F8, "49f078fa", "pb_field_iter_find", "stock"),
    (0x0048_FF1E, 0x004D_946E, "49f0a6fa", "pb_field_iter_find_extension", "stock"),
    (0x0048_FF4A, 0x0048_FC88, "fff79dfe", "decode_extension", "stock"),
    (0x0048_FF68, 0x0048_F66C, "fff780fb", "pb_decode_tag", "source"),
    (0x0048_FFBE, 0x0048_F6A0, "fff76ffb", "pb_skip_field", "source"),
    (0x0049_0056, 0x0048_FBE4, "fff7c5fd", "decode_field", "stock"),
)
DIAGNOSTICS = (
    (0x0049_05A8, 0x0077_9F7C, "failed to set defaults", (0x0048_FEF0,),
     "5e86e87a4c646c84543cb3bf4144e08c7bdec921392f52933bd65b4f7221c5c3"),
    (0x0049_05B8, 0x0078_B69C, "zero tag", (0x0048_FFAA,),
     "860387257f76b5a2ac0e8cb63ea4c95803f9cebe047c7afec301cda5bf113764"),
    (0x0049_05BC, 0x0075_7668, "wrong size for fixed count field",
     (0x0049_006C, 0x0049_007A),
     "1bc53bcc80aabe75282ae3335c1911aaa9cd42fb4cd9179aa23a4734c623d93e"),
    (0x0049_05C0, 0x0077_9F94, "missing required field",
     (0x0049_00C8, 0x0049_0100),
     "5de35d350d09e78eef018cafe4b4f32c8bea312873d5581d18ad86d62e2dd29e"),
)
UPSTREAM_DEFINITION = (
    32_121, 37_346,
    "01b0015f6b8450e27d38a5f60e57708d9007d005d9ece2ef3fdb287b27ed23f4",
)
EXPECTED_STORED_PATTERNS = (
    (0x006C_1528, 0x0048_FFBC, 0x0048_FFBD, 0xFFBD, 0x0048),
    (0x0065_1962, 0x0049_0000, 0x0049_0000, 0x0000, 0x0049),
    (0x0065_2162, 0x0049_0000, 0x0049_0000, 0x0000, 0x0049),
    (0x0068_7092, 0x0049_0000, 0x0049_0000, 0x0000, 0x0049),
    (0x006C_CC22, 0x0049_0000, 0x0049_0000, 0x0000, 0x0049),
    (0x006C_CCEE, 0x0049_0000, 0x0049_0000, 0x0000, 0x0049),
    (0x006D_0CE2, 0x0049_0000, 0x0049_0000, 0x0000, 0x0049),
    (0x006D_104A, 0x0049_0000, 0x0049_0000, 0x0000, 0x0049),
    (0x006D_14FE, 0x0049_0000, 0x0049_0000, 0x0000, 0x0049),
    (0x0078_607E, 0x0049_0000, 0x0049_0000, 0x0000, 0x0049),
    (0x0064_D71A, 0x0049_000E, 0x0049_000F, 0x000F, 0x0049),
    (0x0064_D646, 0x0049_002A, 0x0049_002B, 0x002B, 0x0049),
    (0x0064_DACA, 0x0049_002C, 0x0049_002C, 0x002C, 0x0049),
    (0x0064_D1C0, 0x0049_0046, 0x0049_0047, 0x0047, 0x0049),
    (0x0065_732E, 0x0049_0048, 0x0049_0048, 0x0048, 0x0049),
    (0x006C_001E, 0x0049_0048, 0x0049_0048, 0x0048, 0x0049),
    (0x006C_061E, 0x0049_0048, 0x0049_0048, 0x0048, 0x0049),
    (0x006C_1CF0, 0x0049_0048, 0x0049_0048, 0x0048, 0x0049),
    (0x0078_F5B6, 0x0049_0054, 0x0049_0055, 0x0055, 0x0049),
)
COLLISION_CONTEXT_SHA256 = "7441bc1937158ceb916197b10d97186f3d9a4c1711a76c7823c110e6e202b70b"
NEIGHBORS = (
    ("predecessor_tail", 0x0048_FE90, START,
     "d346b02b833803cf13a315bb610739ba5ad0a07262d8292e395f1f1215b875c4"),
    ("successor_literal_island", END, 0x0049_0120,
     "b95088852cc654bb1dcb18f627b43c3e2bfa1d60e16947c41e5882e57be3c1e8"),
    ("pb_decode_wrapper", 0x0049_0120, 0x0049_012C,
     "1d40ac115e473a259da469051118af4dbbb416258124b3fa875b458b9929dd98"),
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
        first, second = struct.unpack(
            "<HH", shared.image_slice(blob, site, site + 4)
        )
        if first & 0xF800 == 0x4800:
            target = ((site + 4) & ~3) + (first & 0xFF) * 4
        elif first == 0xF8DF:
            target = ((site + 4) & ~3) + (second & 0x0FFF)
        else:
            target = None
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
        raise AuditError("pb_decode_inner stock body changed")

    ingress = scan_ingress(blob)
    if tuple(ingress["direct"]["bl"]) != EXPECTED_CALLERS:
        raise AuditError(f"pb_decode_inner BL callers changed: {ingress['direct']['bl']!r}")
    if any(ingress["direct"][kind] for kind in ("bw", "conditional", "narrow")):
        raise AuditError("unexpected non-BL entry ingress")
    if ingress["interior"]:
        raise AuditError("pb_decode_inner has alternate branch ingress")
    if tuple(ingress["stored_patterns"]) != EXPECTED_STORED_PATTERNS:
        raise AuditError("pb_decode_inner stored-pattern classification changed")

    address_bytes = b"".join(struct.pack("<I", item[0]) for item in EXPECTED_CALLERS)
    record_bytes = b"".join(struct.pack("<I", address) + bytes.fromhex(encoding)
                            for address, encoding in EXPECTED_CALLERS)
    if sha256(address_bytes) != CALLER_ADDRESS_SHA256 or sha256(record_bytes) != CALLER_RECORD_SHA256:
        raise AuditError("caller topology digest changed")
    for start, end, digest in CALLER_CONTEXTS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError(f"caller context changed at {start:#x}")
    contexts = b"".join(shared.image_slice(blob, address - 8, address + 12)
                        for address, *_ in EXPECTED_STORED_PATTERNS)
    if sha256(contexts) != COLLISION_CONTEXT_SHA256:
        raise AuditError("stored-pattern collision contexts changed")

    outgoing = []
    for site, target, encoding, provider, ownership in EXPECTED_CALLS:
        raw = shared.image_slice(blob, site, site + 4)
        first, second = struct.unpack("<HH", raw)
        if raw.hex() != encoding or shared.thumb_bl_target(site, first, second) != target:
            raise AuditError(f"provider call changed at {site:#x}")
        outgoing.append({"site": site, "target": target, "provider": provider,
                         "ownership": ownership})

    diagnostics = []
    for slot, address, message, expected_loads, digest in DIAGNOSTICS:
        if struct.unpack("<I", shared.image_slice(blob, slot, slot + 4))[0] != address:
            raise AuditError(f"diagnostic pointer changed at {slot:#x}")
        raw = shared.image_slice(blob, address, address + len(message) + 1)
        if raw != message.encode() + b"\0" or sha256(raw) != digest:
            raise AuditError(f"diagnostic changed at {address:#x}")
        if literal_loads(blob, slot) != expected_loads:
            raise AuditError(f"diagnostic loads changed at {slot:#x}")
        diagnostics.append({"slot": slot, "address": address, "text": message,
                            "loads": expected_loads, "sha256": digest})

    source_start, source_end, source_hash = UPSTREAM_DEFINITION
    if sha256(upstream[source_start:source_end]) != source_hash:
        raise AuditError("pb_decode_inner upstream definition changed")
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
        "upstream": {"commit": shared.UPSTREAM_COMMIT,
                     "compatibility_baseline": "nanopb-0.4.9",
                     "compatible_pristine_range": "0.4.7--0.4.9",
                     "definition_start": source_start, "definition_end": source_end,
                     "definition_sha256": source_hash},
        "ingress": ingress,
        "stored_pattern_classification":
            "19 authenticated table/text collisions; no pointer ingress",
        "outgoing": outgoing,
        "diagnostics": diagnostics,
        "neighbors": neighbors,
        "configuration": {"PB_MAX_REQUIRED_FIELDS": 64, "PB_FIELD_32BIT": False,
                          "PB_ENABLE_MALLOC": False, "PB_DECODE_NOINIT": 1,
                          "PB_DECODE_NULLTERMINATED": 4},
        "decision": {
            "production_candidate": True,
            "production_integrated": True,
            "executable_stock_seams": 0,
            "guarded_source_replacement_entries": 7,
            "direct_overlay_bindings": 2,
            "source_dependencies": 8,
            "eliminated_stock_seams": 1,
            "local_diagnostic_bytes": 88,
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
        print(f"nanopb pb_decode_inner: {report['stock']['size']} stock bytes; "
              "production source leaf with zero executable stock seams")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
