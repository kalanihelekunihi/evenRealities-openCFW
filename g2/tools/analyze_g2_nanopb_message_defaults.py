#!/usr/bin/env python3
"""Fail-closed boundary and dependency audit for G2 ``pb_message_set_to_defaults``."""

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
START = 0x0048_FDF2
END = 0x0048_FE98
STOCK_SHA256 = "1409633f121586a45b076e247e2f1f33f6120be85044245f42ca777955bd34e4"
EXPECTED_CALLERS = (
    (0x0048_FAD6, "00f08cf9"),
    (0x0048_FD12, "00f06ef8"),
    (0x0048_FDA2, "00f026f8"),
    (0x0048_FEDE, "fff788ff"),
)
CALLER_CONTEXTS = (
    (0x0048_FACA, 0x0048_FAE2, "c705b7ba6429c978f4f95dcae4056e3927fd184615216ec1f638187d7f3bcd9b"),
    (0x0048_FD06, 0x0048_FD1E, "9acfdc783f3d36de9c15774ce456fcbcbba122841bb38b198636bfcec79b830a"),
    (0x0048_FD96, 0x0048_FDAE, "3a9995f3f88f01efece026433380fdc356d19370e47b86a679026256aa96d730"),
    (0x0048_FED2, 0x0048_FEEA, "8a32e955323b76ffad002275f7cc1633fa95a58bd938b44a4a706776f17dd706"),
)
EXPECTED_CALLS = (
    (0x0048_FDFC, 0x0048_949C, "f9f74efb", "pb_istream_from_buffer", "source"),
    (0x0048_FE1C, 0x0048_F49C, "fff73efb", "pb_istream_from_buffer", "source"),
    (0x0048_FE2A, 0x0048_F66C, "fff71ffc", "pb_decode_tag", "source"),
    (0x0048_FE4C, 0x0048_FBE4, "fff7cafe", "decode_field", "stock"),
    (0x0048_FE5E, 0x0048_F66C, "fff705fc", "pb_decode_tag", "source"),
    (0x0048_FE74, 0x004D_93D8, "49f0b0fa", "pb_field_iter_next", "stock"),
    (0x0048_FE7E, 0x0048_FCE2, "fff730ff", "pb_field_set_to_default", "stock"),
)
UPSTREAM_DEFINITION = (
    31_080,
    32_048,
    "b907b8141e8f0376e9d5e86bf58efde7465d2a16ca3d30ece27ffda16d3afe9e",
)
NEIGHBORS = (
    ("pb_field_set_to_default", 0x0048_FCE2, START,
     "0d0dd0be0ae68f84bb20e39f7c95f500656316563d95b6d5cc3e290d4b131728"),
    ("pb_decode_inner", END, 0x0049_0112,
     "13f2b83cd22ed38a6b74d52b0bd4eb6e8577becdcf5a1c8816a4af6aef1eea52"),
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
        raise AuditError("pb_message_set_to_defaults stock body changed")
    ingress = scan_ingress(blob)
    if tuple(ingress["direct"]["bl"]) != EXPECTED_CALLERS:
        raise AuditError(f"pb_message_set_to_defaults callers changed: {ingress['direct']['bl']!r}")
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
        raise AuditError("pb_message_set_to_defaults upstream definition changed")
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
        "upstream": {"commit": shared.UPSTREAM_COMMIT,
                     "compatibility_baseline": "nanopb-0.4.9",
                     "compatible_pristine_range": "0.4.7--0.4.9",
                     "definition_start": source_start,
                     "definition_end": source_end,
                     "definition_sha256": source_digest},
        "neighbors": neighbors,
        "decision": {"production_candidate": True,
                     "production_integrated": True,
                     "source_identification_percent": 100,
                     "source_recreation_percent": 100,
                     "source_owned_call_sites": 4,
                     "fixed_stock_call_sites": 3,
                     "fixed_stock_helper_families": 3,
                     "production_source_owned_call_sites": 5,
                     "production_fixed_stock_call_sites": 1,
                     "production_fixed_stock_helper_families": 1,
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
        print("nanopb pb_message_set_to_defaults: 166 stock bytes; production-integrated with one fixed decode_field seam")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
