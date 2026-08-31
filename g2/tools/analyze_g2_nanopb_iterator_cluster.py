#!/usr/bin/env python3
"""Fail-closed source and topology audit for the G2 nanopb iterator cluster."""

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
UPSTREAM = shared.ROOT / "third_party/nanopb/pb_common.c"
UPSTREAM_SIZE = 12_141
UPSTREAM_SHA256 = "8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516"
LOCAL_SOURCE = shared.ROOT / "components/shared/nanopb/runtime_nanopb_iterator_cluster.c"
LOCAL_SOURCE_SIZE = 14_025
LOCAL_SOURCE_SHA256 = "825238916fc945c521c2f1bce8042c7725c42b82c92b08271dbba529991fa06e"
LOCAL_HEADER = shared.ROOT / "components/shared/nanopb/runtime_nanopb_iterator_cluster.h"
LOCAL_HEADER_SIZE = 2_995
LOCAL_HEADER_SHA256 = "f9664d9eb409a731dbf1a7c664ee91f10b58b3b0f818844eab5f77fbaac8f0b2"
APPLE_OBJECT_SIZE = 4_564
APPLE_OBJECT_SHA256 = "b4049aec70c47ed1b617661d44fc400894e409f00bf472af19b34a0ff69d2ebc"
OVERLAY = shared.ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = shared.ROOT / "manifests/g2-2.2.6.10-core-source.json"
PRODUCTION_FUNCTIONS = (
    "open_cfw_nanopb_load_descriptor_values",
    "open_cfw_nanopb_field_iter_begin",
    "open_cfw_nanopb_field_iter_begin_extension",
    "open_cfw_nanopb_field_iter_next",
    "open_cfw_nanopb_field_iter_find",
    "open_cfw_nanopb_field_iter_find_extension",
    "open_cfw_nanopb_field_iter_begin_const",
    "open_cfw_nanopb_field_iter_begin_extension_const",
    "open_cfw_nanopb_default_field_callback",
)
START = 0x004D_916E
END = 0x004D_9522
STOCK_SHA256 = "067d3a89db02db4ecc9b71e17dc4243c1f61b64ec3c40cfaf90cf07bb1d0b362"

SEGMENTS = (
    ("load_descriptor_values", 0x004D_916E, 0x004D_930A, 412,
     "bdab791c6ac39478ec084abeec451d720a33d0a0267f5156e3fd3a32e790c16e"),
    ("advance_iterator", 0x004D_930A, 0x004D_9384, 122,
     "435d7c084a9772efc6c574a7bd152557f6b7f900f0cbb282a926c0adc69d170e"),
    ("pb_field_iter_begin", 0x004D_9384, 0x004D_93A4, 32,
     "cc5525b596a66b8ba09f2c055d96c08c8ce4a0679efb6f36ce042626a3dc4277"),
    ("pb_field_iter_begin_extension", 0x004D_93A4, 0x004D_93D8, 52,
     "fee54683c36fc5510dace567fdb198ab01b619da62d24244e1ee7461b3f32026"),
    ("pb_field_iter_next", 0x004D_93D8, 0x004D_93F8, 32,
     "fd4a858244f26a7c27bc2b11fbfa49a29ff434037e663491696b821876fc71f7"),
    ("pb_field_iter_find", 0x004D_93F8, 0x004D_946E, 118,
     "08bc6b102be2bef55978dc3504dda4d6e2d5ea42fe1c5dd213608c07754e8005"),
    ("pb_field_iter_find_extension", 0x004D_946E, 0x004D_94B8, 74,
     "6551f77748e3d2271292923b2939c0cf68782df4f731e76a441f30cf531f7bde"),
    ("pb_const_cast", 0x004D_94B8, 0x004D_94BA, 2,
     "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    ("pb_field_iter_begin_const", 0x004D_94BA, 0x004D_94D2, 24,
     "1d71a0692ecf47bbf9b742cf2676484f20ce989b0d3750679a17df23e12a4827"),
    ("pb_field_iter_begin_extension_const", 0x004D_94D2, 0x004D_94E6, 20,
     "f67d2e9c40793f2decfc532705dc3d4719f6d8212f7efef381dd9f42f417758e"),
    ("pb_default_field_callback", 0x004D_94E6, 0x004D_9522, 60,
     "1ec35a15769044d8effbad2c20328d0da966cf4af14b9ba890b6d17850813d03"),
)

EXPECTED_CALLERS = {
    0x004D_916E: ((0x004D_939E, "fff7e6fe"), (0x004D_93E4, "fff7c3fe"),
                  (0x004D_9440, "fff795fe"), (0x004D_9466, "fff782fe"),
                  (0x004D_94A8, "fff761fe"), (0x004D_94B0, "fff75dfe")),
    0x004D_930A: ((0x004D_93DE, "fff794ff"), (0x004D_9424, "fff771ff"),
                  (0x004D_9484, "fff741ff")),
    0x004D_9384: ((0x0048_FACC, "49f05afc"), (0x0048_FD98, "49f0f4fa"),
                  (0x0048_FED0, "49f058fa"), (0x0049_09A6, "48f0edfc"),
                  (0x004D_93C0, "fff7e0ff"), (0x004D_93CA, "fff7dbff"),
                  (0x004D_94CC, "fff75aff")),
    0x004D_93A4: ((0x0048_FC36, "49f0b5fb"), (0x0048_FD04, "49f04efb"),
                  (0x004D_94E0, "fff760ff")),
    0x004D_93D8: ((0x0048_FE74, "49f0b0fa"), (0x0049_09BA, "48f00dfd"),
                  (0x0049_0C70, "48f0b2fb")),
    0x004D_93F8: ((0x0048_FF04, "49f078fa"),),
    0x004D_946E: ((0x0048_FF1E, "49f0a6fa"),),
    0x004D_94B8: ((0x004D_94C2, "fff7f9ff"), (0x004D_94D8, "fff7eeff")),
    0x004D_94BA: ((0x0049_0C3A, "48f03efc"),),
    0x004D_94D2: ((0x0049_0BD0, "48f07ffc"),),
    0x004D_94E6: (),
}

EXPECTED_CALLS = (
    (0x004D_9394, 0x0043_C0E4, "62f7a6fe", "memory_fill", "eliminated"),
    (0x004D_939E, 0x004D_916E, "fff7e6fe", "load_descriptor_values", "internal"),
    (0x004D_93C0, 0x004D_9384, "fff7e0ff", "pb_field_iter_begin", "internal"),
    (0x004D_93CA, 0x004D_9384, "fff7dbff", "pb_field_iter_begin", "internal"),
    (0x004D_93DE, 0x004D_930A, "fff794ff", "advance_iterator", "internal"),
    (0x004D_93E4, 0x004D_916E, "fff7c3fe", "load_descriptor_values", "internal"),
    (0x004D_9424, 0x004D_930A, "fff771ff", "advance_iterator", "internal"),
    (0x004D_9440, 0x004D_916E, "fff795fe", "load_descriptor_values", "internal"),
    (0x004D_9466, 0x004D_916E, "fff782fe", "load_descriptor_values", "internal"),
    (0x004D_9484, 0x004D_930A, "fff741ff", "advance_iterator", "internal"),
    (0x004D_94A8, 0x004D_916E, "fff761fe", "load_descriptor_values", "internal"),
    (0x004D_94B0, 0x004D_916E, "fff75dfe", "load_descriptor_values", "internal"),
    (0x004D_94C2, 0x004D_94B8, "fff7f9ff", "pb_const_cast", "internal"),
    (0x004D_94CC, 0x004D_9384, "fff75aff", "pb_field_iter_begin", "internal"),
    (0x004D_94D8, 0x004D_94B8, "fff7eeff", "pb_const_cast", "internal"),
    (0x004D_94E0, 0x004D_93A4, "fff760ff", "pb_field_iter_begin_extension", "internal"),
)

EXPECTED_DYNAMIC_CALLBACKS = ((0x004D_9506, "9847"), (0x004D_951A, "9847"))
CLASSIFIED_DATA_BRANCH_COLLISION = (
    "narrow", 0x004D_9118, 0x004D_9174, "dc2c"
)
DATA_ISLAND = (0x004D_910A, 0x004D_914C,
               "3d67da729d7ee705ec6ac8f775e52beba3fdec564a2ca88280136ef0986b2496")
PREDECESSOR = (0x004D_914C, START,
               "b0eaecb9c4970d61ba662726c82e216b28ce4023456f6eb14df651c1def4dbb5")
SUCCESSOR = (END, 0x004D_9530,
             "12611160fc8e6ee3552e451f338ef1a611ad59ddf77254c51b5a1685d9d7c7f9")
STORED_POINTERS = ((0x0049_10BC, 0x004D_94E6, 0x004D_94E7),)

UPSTREAM_CLUSTER = (
    145, 10_196, 10_051,
    "cfd4ae8e8dac527ba9332809e3038c101199a26d271fd51ae0bc154c927469e8",
)
PRISTINE_RELEASES = (
    ("0.4.4", "2b48a361786dfb1f63d229840217a93aae064667"),
    ("0.4.5", "c9124132a604047d0ef97a09c0e99cd9bed2c818"),
    ("0.4.6", "afc499f9a410fc9bbf6c9c48cdd8d8b199d49eb4"),
    ("0.4.7", "b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba"),
    ("0.4.8", "6cfe48d6f1593f8fa5c0f90437f5e6522587745e"),
    ("0.4.9", "98bf4db69897b53434f3d0ba72e0a3ab1a902824"),
    ("0.4.9.1", "cad3c18ef15a663e30e3e43e3a752b66378adec1"),
)


class AuditError(RuntimeError):
    """Raised when an authenticated iterator invariant changes."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def scan_topology(blob: bytes) -> dict[str, Any]:
    entries = {item[1] for item in SEGMENTS}
    callers = {entry: [] for entry in entries}
    interior_bl = []
    alternate = []
    for offset in range(0, len(blob) - 3, 2):
        address = shared.LOAD_BASE + offset
        first, second = struct.unpack_from("<HH", blob, offset)
        encoding = blob[offset:offset + 4].hex()
        target = branch.wide_branch_target(address, first, second, link=True)
        if target in entries:
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
    for target in range(START, END, 2):
        for value in (target, target | 1):
            needle = struct.pack("<I", value)
            offset = blob.find(needle)
            while offset >= 0:
                stored.append((shared.LOAD_BASE + offset, target, value))
                offset = blob.find(needle, offset + 1)
    return {"callers": callers, "interior_bl": interior_bl,
            "alternate": alternate, "stored_pointers": stored}


def authenticate_span(blob: bytes, record: tuple[int, int, str], label: str) -> None:
    start, end, digest = record
    if sha256(shared.image_slice(blob, start, end)) != digest:
        raise AuditError(f"{label} span changed")


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != shared.IMAGE_SIZE or sha256(blob) != shared.IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")
    upstream = UPSTREAM.read_bytes()
    if len(upstream) != UPSTREAM_SIZE or sha256(upstream) != UPSTREAM_SHA256:
        raise AuditError("authenticated pb_common.c identity mismatch")
    local_source = LOCAL_SOURCE.read_bytes()
    local_header = LOCAL_HEADER.read_bytes()
    if len(local_source) != LOCAL_SOURCE_SIZE or sha256(local_source) != LOCAL_SOURCE_SHA256:
        raise AuditError("iterator candidate source identity mismatch")
    if len(local_header) != LOCAL_HEADER_SIZE or sha256(local_header) != LOCAL_HEADER_SHA256:
        raise AuditError("iterator candidate header identity mismatch")
    stock = shared.image_slice(blob, START, END)
    if len(stock) != 948 or sha256(stock) != STOCK_SHA256:
        raise AuditError("iterator cluster body changed")

    segments = []
    for name, start, end, size, digest in SEGMENTS:
        body = shared.image_slice(blob, start, end)
        if len(body) != size or sha256(body) != digest:
            raise AuditError(f"{name} boundary changed")
        segments.append({"name": name, "start": start, "end": end,
                         "size": size, "sha256": digest})

    topology = scan_topology(blob)
    if topology["interior_bl"]:
        raise AuditError(f"unexpected BL interior ingress: {topology['interior_bl']!r}")
    for entry, expected in EXPECTED_CALLERS.items():
        if tuple(topology["callers"][entry]) != expected:
            raise AuditError(f"callers changed for {entry:#x}: {topology['callers'][entry]!r}")
    if topology["alternate"] != [CLASSIFIED_DATA_BRANCH_COLLISION]:
        raise AuditError(f"alternate ingress changed: {topology['alternate']!r}")
    if tuple(topology["stored_pointers"]) != STORED_POINTERS:
        raise AuditError(f"stored pointers changed: {topology['stored_pointers']!r}")

    calls = []
    for site, target, encoding, function, ownership in EXPECTED_CALLS:
        raw = shared.image_slice(blob, site, site + 4)
        first, second = struct.unpack("<HH", raw)
        if raw.hex() != encoding or shared.thumb_bl_target(site, first, second) != target:
            raise AuditError(f"outgoing call changed at {site:#x}")
        calls.append({"site": site, "target": target, "encoding": encoding,
                      "function": function, "ownership": ownership})
    for site, encoding in EXPECTED_DYNAMIC_CALLBACKS:
        if shared.image_slice(blob, site, site + 2).hex() != encoding:
            raise AuditError(f"dynamic callback changed at {site:#x}")

    authenticate_span(blob, DATA_ISLAND, "classified predecessor data island")
    authenticate_span(blob, PREDECESSOR, "predecessor shift helper")
    authenticate_span(blob, SUCCESSOR, "successor TinyFrame wrapper")
    source_start, source_end, source_size, source_digest = UPSTREAM_CLUSTER
    source = upstream[source_start:source_end]
    if len(source) != source_size or sha256(source) != source_digest:
        raise AuditError("upstream iterator definition cluster changed")

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    production_leaves = [
        item for item in overlay.get("relocated_leaves", [])
        if item.get("function") in PRODUCTION_FUNCTIONS
    ]
    if tuple(item.get("function") for item in production_leaves) != PRODUCTION_FUNCTIONS:
        raise AuditError("production iterator leaf set or order changed")
    production_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") in PRODUCTION_FUNCTIONS
    ]
    if len(production_patches) != 8:
        raise AuditError("production iterator patch set changed")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    regions = manifest["component_overrides"]["apollo_main"]["regions"]
    by_name = {item["name"]: item for item in regions}
    source_regions = [
        item for name, item in by_name.items()
        if name.startswith("apollo_nanopb_")
        and ("field_iter" in name or "iterator_provider" in name
             or "default_field_callback" in name)
    ]
    if len(source_regions) != 14:
        raise AuditError("production iterator source-region set changed")

    return {
        "image": {"size": len(blob), "sha256": sha256(blob),
                  "load_base": shared.LOAD_BASE},
        "stock": {"start": START, "end": END, "size": len(stock),
                  "sha256": STOCK_SHA256, "segments": segments},
        "topology": {
            "callers": topology["callers"],
            "interior_bl": topology["interior_bl"],
            "classified_data_branch_collision": CLASSIFIED_DATA_BRANCH_COLLISION,
            "unexpected_alternate": [],
            "stored_pointers": topology["stored_pointers"],
        },
        "outgoing": calls,
        "dynamic_callbacks": [
            {"site": site, "encoding": encoding, "classification": "schema/application ABI"}
            for site, encoding in EXPECTED_DYNAMIC_CALLBACKS
        ],
        "upstream": {
            "selected_commit": shared.UPSTREAM_COMMIT,
            "selected_baseline": "nanopb-0.4.9",
            "pb_common_size": UPSTREAM_SIZE,
            "pb_common_sha256": UPSTREAM_SHA256,
            "definition_start": source_start,
            "definition_end": source_end,
            "definition_size": source_size,
            "definition_sha256": source_digest,
            "exact_pb_common_release_range": "0.4.4--0.4.9.1",
            "release_matrix": [
                {"release": release, "commit": commit}
                for release, commit in PRISTINE_RELEASES
            ],
            "vendor_point_release_proven": False,
        },
        "source_recreation": {
            "source": str(LOCAL_SOURCE.relative_to(shared.ROOT)),
            "source_size": LOCAL_SOURCE_SIZE,
            "source_sha256": LOCAL_SOURCE_SHA256,
            "header": str(LOCAL_HEADER.relative_to(shared.ROOT)),
            "header_size": LOCAL_HEADER_SIZE,
            "header_sha256": LOCAL_HEADER_SHA256,
            "apple_clang_object_size": APPLE_OBJECT_SIZE,
            "apple_clang_object_sha256": APPLE_OBJECT_SHA256,
            "undefined_symbol_count": 0,
        },
        "production_integration": {
            "relocated_leaf_count": len(production_leaves),
            "entry_patch_count": len(production_patches),
            "manifest_source_and_alignment_region_count": len(source_regions),
            "source_owned_overlay_bytes": 1132,
            "generated_alignment_bytes": 10,
            "replaced_stock_entry_bytes": 412,
            "unowned_unreachable_stock_bytes": 536,
        },
        "decision": {
            "production_candidate": False,
            "source_identification_percent": 100,
            "source_recreation_percent": 100,
            "reviewed_target_compilation_percent": 100,
            "production_integration_percent": 100,
            "public_entry_count": 8,
            "private_helper_count": 3,
            "fixed_stock_call_sites_after_recreation": 0,
            "eliminated_memory_fill_call_sites": 1,
            "dynamic_callback_abi_sites": 2,
            "stock_data_seams": 0,
            "decoder_defaults_call_sites_closed": 6,
            "decoder_defaults_unique_entries_closed": 5,
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
        print("nanopb iterator cluster: 948 stock bytes; eight live entries production-integrated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
