#!/usr/bin/env python3
"""Fail-closed audit for the G2 nanopb field/extension dispatch cluster."""

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
LOCAL_SOURCE = shared.ROOT / "components/shared/nanopb/runtime_nanopb_dispatch_extension.c"
LOCAL_SOURCE_SIZE = 3_804
LOCAL_SOURCE_SHA256 = "b4a6620fdc79fdbb3b3891166d6248176b396cf18b7157cd3d300d66ee15de96"
LOCAL_HEADER = shared.ROOT / "components/shared/nanopb/runtime_nanopb_dispatch_extension.h"
LOCAL_HEADER_SIZE = 1_560
LOCAL_HEADER_SHA256 = "f6918d0d89b223e9ad33601de800931a73a0c9ad5ac66177ea83c435441c2ec8"
OVERLAY = shared.ROOT / "components/apollo_main/core_overlay/overlay.json"
PRODUCTION_FUNCTIONS = (
    "open_cfw_nanopb_decode_field",
    "open_cfw_nanopb_default_extension_decoder",
    "open_cfw_nanopb_decode_extension",
)
START = 0x0048_FBE4
END = 0x0048_FCE2
STOCK_SHA256 = "b1370bf5cda0e85a1ec7aa420a5a184a273e71949459a182ae0d297d18fa3625"

SEGMENTS = (
    ("decode_field", 0x0048_FBE4, 0x0048_FC26, 66,
     "a7e2136d4de19007cab84722398b120c6cf806ec558163447cf11d33064e8479"),
    ("default_extension_decoder", 0x0048_FC26, 0x0048_FC78, 82,
     "dbd41534fcd6ff0fc27f1bf87225f233020ba5c904e4aa4a5c9c85a83bd988d6"),
    ("literal_island", 0x0048_FC78, 0x0048_FC88, 16,
     "1026cb9d3335a6464ffa01ebd4901588496b37013be9aa1bf13a7de1c95c7fe3"),
    ("decode_extension", 0x0048_FC88, 0x0048_FCE2, 90,
     "0f630c1173971762af8df1ec82ed50cff6f292a9b77eafae06e56b9f3b659472"),
)
ENTRIES = (0x0048_FBE4, 0x0048_FC26, 0x0048_FC88)
EXPECTED_CALLERS = {
    0x0048_FBE4: (
        (0x0048_FC70, "fff7b8ff"),
        (0x0048_FE4C, "fff7cafe"),
        (0x0049_0056, "fff7c5fd"),
    ),
    0x0048_FC26: ((0x0048_FCCE, "fff7aaff"),),
    0x0048_FC88: ((0x0048_FF4A, "fff79dfe"),),
}
CALLER_CONTEXTS = (
    (0x0048_FC68, 0x0048_FC7C,
     "ff8a9dafc457c1e38367c08828abb2f0c410db999ed92618beffd4531124e9bc"),
    (0x0048_FE44, 0x0048_FE58,
     "758b34cce8bb1fc72f411f1adc326ffed4b5f4b6ae40427e7a3017623670ea76"),
    (0x0049_004E, 0x0049_0062,
     "af7f0868fd0d07c4b3497a5755d92d935b8da58675c207c0e146f1afbda03735"),
    (0x0048_FCC6, 0x0048_FCDA,
     "a7e88abf4639c911803c006a68adf8e401a69f77552899d1807eecc660d6ac4e"),
    (0x0048_FF42, 0x0048_FF56,
     "5f85f2e50a4ac69ab4f512affa172a973a6452b45439294a39eb30a9204b48c5"),
)
EXPECTED_CALLS = (
    (0x0048_FBFC, 0x0048_F968, "fff7b4fe", "decode_static_field", "stock"),
    (0x0048_FC04, 0x0048_FB1C, "fff78aff", "decode_pointer_field", "stock"),
    (0x0048_FC0C, 0x0048_FB30, "fff790ff", "decode_callback_field", "stock"),
    (0x0048_FC36, 0x004D_93A4, "49f0b5fb", "pb_field_iter_begin_extension", "source"),
    (0x0048_FC70, 0x0048_FBE4, "fff7b8ff", "decode_field", "internal"),
    (0x0048_FCCE, 0x0048_FC26, "fff7aaff", "default_extension_decoder", "internal"),
)
DYNAMIC_CALLBACK = (
    0x0048_FCB8,
    "d4f800c0dcf800c0e047",
    "extension->type->decode",
)
DIAGNOSTICS = (
    (0x0049_0488, 0x0078_17F0, "invalid field type", (0x0048_FC1C,),
     "6a8abe1a00cdabc842420e076e863e2b2fb23c5982f5a7cda7a2b29aea70f521"),
    (0x0049_05B4, 0x0078_1818, "invalid extension", (0x0048_FC48,),
     "00cb39165079aa30025e126d2c619e8460de55b101e8acf0d114742383d30faf"),
)
UPSTREAM_DEFINITIONS = (
    ("decode_field", 26_221, 27_053, 832,
     "1c6111be8313e278c2b1753401a701245c1baa7c90acd085f18c1eb277d7e42d"),
    ("default_extension_decoder", 27_227, 27_659, 432,
     "175e06435cc0c7e7f0bf3d44aa6b2d3e0f5f9bc8384ce52d28c80bf21777a691"),
    ("decode_extension", 27_810, 28_413, 603,
     "3229a97ca148e192ca3b1d0fd33df3a1654b6405bd247e0b6f6320041460f7da"),
)
PRISTINE_RELEASE_MATRIX = (
    ("0.4.4", "2b48a361786dfb1f63d229840217a93aae064667"),
    ("0.4.5", "c9124132a604047d0ef97a09c0e99cd9bed2c818"),
    ("0.4.6", "afc499f9a410fc9bbf6c9c48cdd8d8b199d49eb4"),
    ("0.4.7", "b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba"),
    ("0.4.8", "6cfe48d6f1593f8fa5c0f90437f5e6522587745e"),
    ("0.4.9", "98bf4db69897b53434f3d0ba72e0a3ab1a902824"),
    ("0.4.9.1", "cad3c18ef15a663e30e3e43e3a752b66378adec1"),
)
NEIGHBORS = (
    ("decode_callback_field_tail", 0x0048_FBDC, START,
     "77aac65b9e7439ec4c84c0049d5e08404ad40c0c646161ad130a28c4323371b9"),
    ("pb_field_set_to_default_head", END, 0x0048_FCEA,
     "61d0cd249076393c47c1946d78d9a34b3efb59937596ecb0273c59c0ac4af0d4"),
)


class AuditError(RuntimeError):
    """Raised when an authenticated dispatch invariant changes."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def scan_topology(blob: bytes) -> dict[str, Any]:
    callers = {entry: [] for entry in ENTRIES}
    interior_bl = []
    alternate = []
    for offset in range(0, len(blob) - 3, 2):
        address = shared.LOAD_BASE + offset
        first, second = struct.unpack_from("<HH", blob, offset)
        encoding = blob[offset:offset + 4].hex()
        target = branch.wide_branch_target(address, first, second, link=True)
        if target in callers:
            callers[target].append((address, encoding))
        elif target is not None and START < target < END:
            interior_bl.append((address, target, encoding))
        if not START <= address < END:
            for kind, candidate in (
                ("bw", branch.wide_branch_target(address, first, second, link=False)),
                ("conditional", branch.wide_conditional_target(address, first, second)),
            ):
                if candidate is not None and START <= candidate < END:
                    alternate.append((kind, address, candidate, encoding))
    for offset in range(0, len(blob) - 1, 2):
        address = shared.LOAD_BASE + offset
        if START <= address < END:
            continue
        halfword = struct.unpack_from("<H", blob, offset)[0]
        for target in branch.narrow_targets(address, halfword):
            if START <= target < END:
                alternate.append(("narrow", address, target, f"{halfword:04x}"))

    stored = []
    for entry in ENTRIES:
        for value in (entry, entry | 1):
            needle = struct.pack("<I", value)
            offset = blob.find(needle)
            while offset >= 0:
                stored.append((shared.LOAD_BASE + offset, entry, value))
                offset = blob.find(needle, offset + 1)
    return {"callers": callers, "interior_bl": interior_bl,
            "alternate": alternate, "stored_pointers": stored}


def literal_loads(blob: bytes, slot: int) -> tuple[int, ...]:
    loads = []
    for site in range(START, END - 3, 2):
        first, second = struct.unpack("<HH", shared.image_slice(blob, site, site + 4))
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
    local_source = LOCAL_SOURCE.read_bytes()
    local_header = LOCAL_HEADER.read_bytes()
    if len(local_source) != LOCAL_SOURCE_SIZE or sha256(local_source) != LOCAL_SOURCE_SHA256:
        raise AuditError("dispatch/extension production source identity mismatch")
    if len(local_header) != LOCAL_HEADER_SIZE or sha256(local_header) != LOCAL_HEADER_SHA256:
        raise AuditError("dispatch/extension production header identity mismatch")

    stock = shared.image_slice(blob, START, END)
    if len(stock) != 254 or sha256(stock) != STOCK_SHA256:
        raise AuditError("field/extension dispatch cluster changed")
    segments = []
    for name, start, end, size, digest in SEGMENTS:
        body = shared.image_slice(blob, start, end)
        if len(body) != size or sha256(body) != digest:
            raise AuditError(f"{name} boundary changed")
        segments.append({"name": name, "start": start, "end": end,
                         "size": size, "sha256": digest})

    topology = scan_topology(blob)
    for entry, expected in EXPECTED_CALLERS.items():
        if tuple(topology["callers"][entry]) != expected:
            raise AuditError(f"callers changed for {entry:#x}: {topology['callers'][entry]!r}")
    if topology["interior_bl"] or topology["alternate"] or topology["stored_pointers"]:
        raise AuditError("alternate or stored-pointer ingress detected")
    for start, end, digest in CALLER_CONTEXTS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError(f"caller context changed at {start:#x}")

    outgoing = []
    for site, target, encoding, function, ownership in EXPECTED_CALLS:
        raw = shared.image_slice(blob, site, site + 4)
        first, second = struct.unpack("<HH", raw)
        if raw.hex() != encoding or shared.thumb_bl_target(site, first, second) != target:
            raise AuditError(f"outgoing call changed at {site:#x}")
        outgoing.append({"site": site, "target": target, "function": function,
                         "ownership": ownership})
    callback_site, callback_encoding, callback_name = DYNAMIC_CALLBACK
    callback = shared.image_slice(
        blob, callback_site, callback_site + len(bytes.fromhex(callback_encoding))
    )
    if callback.hex() != callback_encoding:
        raise AuditError("dynamic extension callback sequence changed")

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

    definitions = []
    for name, start, end, size, digest in UPSTREAM_DEFINITIONS:
        definition = upstream[start:end]
        if len(definition) != size or sha256(definition) != digest:
            raise AuditError(f"{name} upstream definition changed")
        definitions.append({"name": name, "start": start, "end": end,
                            "size": size, "sha256": digest})
    required_tokens = (
        b"case PB_ATYPE_STATIC:", b"return decode_pointer_field(",
        b"return decode_callback_field(", b"pb_field_iter_begin_extension(&iter, extension)",
        b"extension->found = true;", b"if (extension->type->decode)",
        b"status = default_extension_decoder(", b"extension = extension->next;",
    )
    if not all(token in upstream[UPSTREAM_DEFINITIONS[0][1]:UPSTREAM_DEFINITIONS[-1][2]]
               for token in required_tokens):
        raise AuditError("dispatch source behavior tokens changed")

    neighbors = []
    for name, start, end, digest in NEIGHBORS:
        if sha256(shared.image_slice(blob, start, end)) != digest:
            raise AuditError(f"{name} boundary changed")
        neighbors.append({"name": name, "start": start, "end": end,
                          "sha256": digest})

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    production_leaves = [
        item for item in overlay.get("relocated_leaves", [])
        if item.get("function") in PRODUCTION_FUNCTIONS
    ]
    if tuple(item.get("function") for item in production_leaves) != PRODUCTION_FUNCTIONS:
        raise AuditError("production dispatch/extension leaf set or order changed")
    production_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") in PRODUCTION_FUNCTIONS
    ]
    if tuple(item.get("target_function") for item in production_patches) != PRODUCTION_FUNCTIONS:
        raise AuditError("production dispatch/extension patch set or order changed")
    if tuple(item["expected"]["offset"] for item in production_leaves) != (
        128_680, 128_752, 128_844
    ):
        raise AuditError("production dispatch/extension placement changed")

    return {
        "image": {"size": len(blob), "sha256": sha256(blob),
                  "load_base": shared.LOAD_BASE},
        "stock": {"start": START, "end": END, "size": len(stock),
                  "sha256": STOCK_SHA256, "segments": segments},
        "topology": topology,
        "outgoing": outgoing,
        "dynamic_callback": {"site": callback_site, "encoding": callback_encoding,
                             "function": callback_name},
        "diagnostics": diagnostics,
        "upstream": {
            "selected_commit": shared.UPSTREAM_COMMIT,
            "compatibility_baseline": "nanopb-0.4.9",
            "exact_definition_range": "0.4.4--0.4.9.1",
            "release_matrix": [
                {"release": release, "commit": commit}
                for release, commit in PRISTINE_RELEASE_MATRIX
            ],
            "definitions": definitions,
        },
        "neighbors": neighbors,
        "production": {
            "source": {"size": len(local_source), "sha256": sha256(local_source)},
            "header": {"size": len(local_header), "sha256": sha256(local_header)},
            "functions": PRODUCTION_FUNCTIONS,
            "leaf_offsets": tuple(
                item["expected"]["offset"] for item in production_leaves
            ),
            "patch_sites": tuple(
                item["runtime_address"] for item in production_patches
            ),
        },
        "decision": {
            "source_identification_percent": 100,
            "source_recreation_percent": 100,
            "production_candidate": True,
            "production_integrated": True,
            "fixed_stock_call_sites": 3,
            "source_owned_call_sites": 1,
            "internal_call_sites": 2,
            "dynamic_callback_sites": 1,
            "remaining_stock_helper_families": 3,
            "production_fixed_stock_call_sites": 3,
            "address_correction": {
                "default_extension_decoder": 0x0048_FC26,
                "decode_extension": 0x0048_FC88,
            },
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
        print("nanopb dispatch/extension cluster: 254 stock bytes; production-integrated with three adjacent field-decoder seams")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
