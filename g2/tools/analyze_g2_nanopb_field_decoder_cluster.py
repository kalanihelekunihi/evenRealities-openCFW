#!/usr/bin/env python3
"""Fail-closed audit for the G2 nanopb field decoder promotion unit."""

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
LOCAL_SOURCE = shared.ROOT / "components/shared/nanopb/runtime_nanopb_field_decoder_cluster.c"
LOCAL_HEADER = shared.ROOT / "components/shared/nanopb/runtime_nanopb_field_decoder_cluster.h"
OVERLAY = shared.ROOT / "components/apollo_main/core_overlay/overlay.json"
PRODUCTION_FUNCTIONS = (
    "open_cfw_nanopb_dec_fixed_length_bytes",
    "open_cfw_nanopb_decode_basic_field",
    "open_cfw_nanopb_decode_static_field",
    "open_cfw_nanopb_decode_pointer_field",
    "open_cfw_nanopb_decode_callback_field",
)
PRODUCTION_OFFSETS = (128_924, 129_144, 129_392, 129_840, 129_884)
PRODUCTION_PATCH_SITES = (0x0049_053C, 0x0048_F7F4, 0x0048_F968, 0x0048_FB1C, 0x0048_FB30)
LOCAL_SOURCE_PIN = (
    14_752,
    "f22074cfc9c5a8ecea62c059d747414c391e7822c5868bbed08df3fa60197326",
)
LOCAL_HEADER_PIN = (
    888,
    "812560e152e879f3181bcb20a2b65b0a6c81673aa4bebe46ff3bb6c99de1a8ac",
)

SEGMENTS = (
    ("decode_basic_field", 0x0048_F7F4, 0x0048_F968, 372,
     "2b1bf389327c0f6ccde636bbb51e36cd0bab3eccc811db9aa0efd3dbfef9e445"),
    ("decode_static_field", 0x0048_F968, 0x0048_FB1C, 436,
     "58eeda598e1b8e418e41323c1749fa1cd7270a38afb93f0e092bec2a8cfa19f1"),
    ("decode_pointer_field", 0x0048_FB1C, 0x0048_FB30, 20,
     "05dac50e007fa534e74598ebbf096b7de8143dee0738977e91b36bfa420cdc83"),
    ("decode_callback_field", 0x0048_FB30, 0x0048_FBE4, 180,
     "8e278f306b51ccd2cabc176f7674d17665ca0647facb310c2fe99cfd00a62379"),
    ("pb_dec_fixed_length_bytes", 0x0049_053C, 0x0049_05A8, 108,
     "2f282fbafb16067744bf97e165493de53f4f0a2d1bb6f6e23f1becae7aede9d1"),
)
FIELD_CLUSTER = (
    0x0048_F7F4,
    0x0048_FBE4,
    1_008,
    "ac71748abf2908adf7850dd7fe339f1c8befcee4fbe416250f80aa3159d37098",
)
EXPECTED_CALLERS = {
    0x0048_F7F4: (
        (0x0048_F992, "fff72fff"),
        (0x0048_F9AC, "fff722ff"),
        (0x0048_FA08, "fff7f4fe"),
        (0x0048_FA7C, "fff7bafe"),
        (0x0048_FB00, "fff778fe"),
    ),
    0x0048_F968: ((0x0048_FBFC, "fff7b4fe"),),
    0x0048_FB1C: ((0x0048_FC04, "fff78aff"),),
    0x0048_FB30: ((0x0048_FC0C, "fff790ff"),),
    0x0049_053C: ((0x0048_F94E, "00f0f5fd"),),
}
EXPECTED_ALTERNATE = (
    ("bl", 0x0063_1CD4, 0x0048_FADC, "5df602ff"),
    ("narrow", 0x0048_F374, 0x0048_F870, "e27c"),
)
ALTERNATE_CONTEXTS = (
    (0x0063_1CC4, 0x0063_1CE4,
     "d82501e292dc1013d8d93ed431a0b4d0583e795e83eb2f1cb7a20102ff023ffd"),
    (0x0048_F364, 0x0048_F384,
     "0fe6e51be4b04f0d576a73d636c7e6a4884d5a34f844de10cc8f42811b10fbad"),
)
STORED_PATTERN_COUNT = 47
STORED_PATTERN_SHA256 = "44039be2f8edfbc80b5452fb6e2a26737351eb3731012e4b4367bdfc3d43a7e2"

EXPECTED_CALLS = (
    (0x0048_F848, 0x0049_01CC, "00f0c0fc", "pb_dec_bool", "source"),
    (0x0048_F872, 0x0049_01D6, "00f0b0fc", "pb_dec_varint", "source"),
    (0x0048_F89C, 0x0049_0190, "00f078fc", "pb_decode_fixed32", "source"),
    (0x0048_F8C6, 0x0049_01AC, "00f071fc", "pb_decode_fixed64", "source"),
    (0x0048_F8E8, 0x0049_0358, "00f036fd", "pb_dec_bytes", "source"),
    (0x0048_F90A, 0x0049_03EA, "00f06efd", "pb_dec_string", "source"),
    (0x0048_F92C, 0x0049_048C, "00f0aefd", "pb_dec_submessage", "source"),
    (0x0048_F94E, 0x0049_053C, "00f0f5fd", "pb_dec_fixed_length_bytes", "unit"),
    (0x0048_F992, 0x0048_F7F4, "fff72fff", "decode_basic_field", "unit"),
    (0x0048_F9AC, 0x0048_F7F4, "fff722ff", "decode_basic_field", "unit"),
    (0x0048_F9DA, 0x0048_F77E, "fff7d0fe", "pb_make_string_substream", "source"),
    (0x0048_FA08, 0x0048_F7F4, "fff7f4fe", "decode_basic_field", "unit"),
    (0x0048_FA30, 0x0048_F7CA, "fff7cbfe", "pb_close_string_substream", "source"),
    (0x0048_FA7C, 0x0048_F7F4, "fff7bafe", "decode_basic_field", "unit"),
    (0x0048_FAA8, 0x0043_C0E4, "acf71cfb", "memory_fill", "eliminated_local"),
    (0x0048_FACC, 0x004D_9384, "49f05afc", "pb_field_iter_begin", "source"),
    (0x0048_FAD6, 0x0048_FDF2, "00f08cf9", "pb_message_set_to_defaults", "source"),
    (0x0048_FB00, 0x0048_F7F4, "fff778fe", "decode_basic_field", "unit"),
    (0x0048_FB44, 0x0048_F6A0, "fff7acfd", "pb_skip_field", "source"),
    (0x0048_FB56, 0x0048_F77E, "fff712fe", "pb_make_string_substream", "source"),
    (0x0048_FBA2, 0x0048_F7CA, "fff712fe", "pb_close_string_substream", "source"),
    (0x0048_FBBE, 0x0048_F6EA, "fff794fd", "read_raw_value", "source"),
    (0x0048_FBD0, 0x0048_F49C, "fff764fc", "pb_istream_from_buffer", "source"),
    (0x0049_0546, 0x0048_F5AE, "fff732f8", "pb_decode_varint32", "source"),
    (0x0049_057A, 0x0043_C0E4, "abf7b3fd", "memory_fill", "eliminated_local"),
    (0x0049_05A2, 0x0048_F3BE, "fef70cff", "pb_read", "source"),
)
DYNAMIC_CALLBACKS = (
    (0x0048_FB74, 0x0048_FB82, "01a82b68db6898470028f0d1e068"),
    (0x0048_FBD8, 0x0048_FBE2, "08a82b68db6898470cb0"),
)
DIAGNOSTICS = (
    (0x0049_0354, 0x0078_7CA0, "wrong wire type",
     (0x0048_F83C, 0x0048_F866, 0x0048_F890, 0x0048_F8BA,
      0x0048_F8DC, 0x0048_F8FE, 0x0048_F920, 0x0048_F942),
     "555abdfc0ae25418e26918d07c625f6cbafea5c663a5a401926eb44072583195"),
    (0x0049_0488, 0x0078_17F0, "invalid field type",
     (0x0048_F95E, 0x0048_FB10),
     "6a8abe1a00cdabc842420e076e863e2b2fb23c5982f5a7cda7a2b29aea70f521"),
    (0x0049_0538, 0x0078_7CB0, "array overflow",
     (0x0048_FA22, 0x0048_FA6A),
     "5f6007ad027d3075463e5944efc5e912975cb40c4431ace6ae50d9f8de5df0e9"),
    (0x0049_05A8, 0x0077_9F7C, "failed to set defaults", (0x0048_FAE8,),
     "5e86e87a4c646c84543cb3bf4144e08c7bdec921392f52933bd65b4f7221c5c3"),
    (0x0049_05AC, 0x0078_1804, "no malloc support", (0x0048_FB26,),
     "e705709ad6abcd871539a705be730e31d3f3dbeae13cc98d29f55ff9fe53821d"),
    (0x0049_05B0, 0x0078_7CC0, "callback failed", (0x0048_FB94,),
     "a4c47562bf9a1305f50185a22c0a83a4f448e619015580e7c6d11a63135f3d80"),
    (0x0049_05CC, 0x0078_7CD0, "bytes overflow", (0x0049_0564,),
     "cb73119bb4c707530fbc832813809996c5502502008fdb625963f30b48b7d37d"),
    (0x0049_05DC, 0x0075_768C, "incorrect fixed length bytes size", (0x0049_0594,),
     "229a4396e51a13736cfbb5ceeba76437b7bfa9d1ea285b5a5ee5057b5396e550"),
)
UPSTREAM_DEFINITIONS = (
    ("decode_basic_field", 11_653, 13_922,
     "c4465869ffee60864637b4710e393a7bb5c60c00a847e6f28137f4b480c5af71"),
    ("decode_static_field", 13_922, 17_541,
     "64eb9ced4f650be17dbb7db6fa58f45ccdb9036460ae6d7aa355c3cfb8bcb24e"),
    ("decode_pointer_field", 19_783, 24_704,
     "06f716c1f96bb2c77c5651b26a9ec5e465958258395e687c1d87dfbd01d70477"),
    ("decode_callback_field", 24_704, 26_221,
     "45c67a796415dd023421f9108696478250e175837956c48fe8f960e3535afa24"),
    ("pb_dec_fixed_length_bytes", 51_557, 52_223,
     "3ede65e67d2d4dd729e53b5ef5a55d109e7479368ada22bf87760b072563e6ce"),
)


class AuditError(RuntimeError):
    """Raised when an authenticated field-decoder invariant changes."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def segment_for(target: int) -> tuple[str, int, int] | None:
    for name, start, end, _size, _digest in SEGMENTS:
        if start <= target < end:
            return name, start, end
    return None


def scan_ingress(blob: bytes) -> dict[str, Any]:
    direct = {entry: {kind: [] for kind in ("bl", "bw", "conditional", "narrow")}
              for entry in EXPECTED_CALLERS}
    alternate = []
    for offset in range(0, len(blob) - 3, 2):
        address = shared.LOAD_BASE + offset
        first, second = struct.unpack_from("<HH", blob, offset)
        encoding = blob[offset:offset + 4].hex()
        for kind, target in (
            ("bl", branch.wide_branch_target(address, first, second, link=True)),
            ("bw", branch.wide_branch_target(address, first, second, link=False)),
            ("conditional", branch.wide_conditional_target(address, first, second)),
        ):
            target_segment = segment_for(target) if target is not None else None
            if target_segment is None or target_segment[1] <= address < target_segment[2]:
                continue
            if target == target_segment[1]:
                direct[target][kind].append((address, encoding))
            else:
                alternate.append((kind, address, target, encoding))
    for offset in range(0, len(blob) - 1, 2):
        address = shared.LOAD_BASE + offset
        halfword = struct.unpack_from("<H", blob, offset)[0]
        for target in branch.narrow_targets(address, halfword):
            target_segment = segment_for(target)
            if target_segment is None or target_segment[1] <= address < target_segment[2]:
                continue
            if target == target_segment[1]:
                direct[target]["narrow"].append((address, f"{halfword:04x}"))
            else:
                alternate.append(("narrow", address, target, f"{halfword:04x}"))
    return {"direct": direct, "alternate": alternate}


def stored_pattern_digest(blob: bytes) -> tuple[int, str]:
    records = []
    for _name, start, end, _size, _digest in SEGMENTS:
        for target in range(start, end, 2):
            for stored in (target, target | 1):
                needle = struct.pack("<I", stored)
                offset = blob.find(needle)
                while offset >= 0:
                    address = shared.LOAD_BASE + offset
                    low, high = struct.unpack_from("<HH", blob, offset)
                    if high != 0x0048 or low & 0xF800 != 0xF800:
                        raise AuditError("stored-pattern match is not the pinned Thumb-2 collision class")
                    records.append((address, target, stored, low, high))
                    offset = blob.find(needle, offset + 1)
    encoded = b"".join(struct.pack("<IIIII", *record) for record in records)
    return len(records), sha256(encoded)


def literal_loads(blob: bytes, slot: int) -> tuple[int, ...]:
    loads = []
    for _name, start, end, _size, _digest in SEGMENTS:
        for site in range(start, end - 3, 2):
            first, second = struct.unpack("<HH", shared.image_slice(blob, site, site + 4))
            candidates = []
            if first & 0xF800 == 0x4800:
                candidates.append(((site + 4) & ~3) + (first & 0xFF) * 4)
            if first == 0xF8DF:
                candidates.append(((site + 4) & ~3) + (second & 0x0FFF))
            if slot in candidates:
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
    if (len(local_source), sha256(local_source)) != LOCAL_SOURCE_PIN:
        raise AuditError("field-decoder production source identity mismatch")
    if (len(local_header), sha256(local_header)) != LOCAL_HEADER_PIN:
        raise AuditError("field-decoder production header identity mismatch")

    segments = []
    for name, start, end, size, digest in SEGMENTS:
        body = shared.image_slice(blob, start, end)
        if len(body) != size or sha256(body) != digest:
            raise AuditError(f"{name} stock boundary changed")
        segments.append({"name": name, "start": start, "end": end,
                         "size": size, "sha256": digest})
    cluster_start, cluster_end, cluster_size, cluster_hash = FIELD_CLUSTER
    cluster = shared.image_slice(blob, cluster_start, cluster_end)
    if len(cluster) != cluster_size or sha256(cluster) != cluster_hash:
        raise AuditError("contiguous field-decoder cluster changed")

    ingress = scan_ingress(blob)
    for entry, expected in EXPECTED_CALLERS.items():
        if tuple(ingress["direct"][entry]["bl"]) != expected:
            raise AuditError(f"BL callers changed for {entry:#x}")
        if any(ingress["direct"][entry][kind]
               for kind in ("bw", "conditional", "narrow")):
            raise AuditError(f"non-BL entry ingress detected for {entry:#x}")
    if tuple(ingress["alternate"]) != EXPECTED_ALTERNATE:
        raise AuditError(f"alternate ingress collision set changed: {ingress['alternate']!r}")
    for context_start, context_end, context_hash in ALTERNATE_CONTEXTS:
        if sha256(shared.image_slice(blob, context_start, context_end)) != context_hash:
            raise AuditError("alternate-ingress data collision context changed")
    stored_count, stored_hash = stored_pattern_digest(blob)
    if (stored_count, stored_hash) != (STORED_PATTERN_COUNT, STORED_PATTERN_SHA256):
        raise AuditError("stored-pointer collision census changed")

    outgoing = []
    for site, target, encoding, provider, ownership in EXPECTED_CALLS:
        raw = shared.image_slice(blob, site, site + 4)
        first, second = struct.unpack("<HH", raw)
        if raw.hex() != encoding or shared.thumb_bl_target(site, first, second) != target:
            raise AuditError(f"outgoing call changed at {site:#x}")
        outgoing.append({"site": site, "target": target, "provider": provider,
                         "ownership": ownership})
    callbacks = []
    for start, end, encoding in DYNAMIC_CALLBACKS:
        if shared.image_slice(blob, start, end).hex() != encoding:
            raise AuditError(f"dynamic callback sequence changed at {start:#x}")
        callbacks.append({"start": start, "end": end, "encoding": encoding})

    diagnostics = []
    for slot, address, text, expected_loads, digest in DIAGNOSTICS:
        if struct.unpack("<I", shared.image_slice(blob, slot, slot + 4))[0] != address:
            raise AuditError(f"diagnostic pointer changed at {slot:#x}")
        raw = shared.image_slice(blob, address, address + len(text) + 1)
        if raw != text.encode() + b"\0" or sha256(raw) != digest:
            raise AuditError(f"diagnostic changed at {address:#x}")
        loads = literal_loads(blob, slot)
        if loads != expected_loads:
            raise AuditError(f"diagnostic loads changed for {text!r}")
        diagnostics.append({"slot": slot, "address": address, "text": text,
                            "loads": loads, "sha256": digest})

    definitions = []
    for name, start, end, digest in UPSTREAM_DEFINITIONS:
        definition = upstream[start:end]
        if sha256(definition) != digest:
            raise AuditError(f"{name} upstream definition changed")
        definitions.append({"name": name, "start": start, "end": end,
                            "size": len(definition), "sha256": digest})

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    production_leaves = [
        item for item in overlay.get("relocated_leaves", [])
        if item.get("function") in PRODUCTION_FUNCTIONS
    ]
    if tuple(item.get("function") for item in production_leaves) != PRODUCTION_FUNCTIONS:
        raise AuditError("production field-decoder leaf set or order changed")
    if tuple(item.get("expected", {}).get("offset") for item in production_leaves) != PRODUCTION_OFFSETS:
        raise AuditError("production field-decoder placement changed")
    production_patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("target_function") in PRODUCTION_FUNCTIONS
    ]
    if tuple(item.get("target_function") for item in production_patches) != PRODUCTION_FUNCTIONS:
        raise AuditError("production field-decoder patch set or order changed")
    if tuple(item.get("runtime_address") for item in production_patches) != PRODUCTION_PATCH_SITES:
        raise AuditError("production field-decoder patch sites changed")

    return {
        "image": {"size": len(blob), "sha256": sha256(blob),
                  "load_base": shared.LOAD_BASE},
        "stock": {"segments": segments, "field_cluster": {
            "start": cluster_start, "end": cluster_end,
            "size": cluster_size, "sha256": cluster_hash,
        }},
        "ingress": ingress,
        "stored_patterns": {
            "count": stored_count,
            "sha256": stored_hash,
            "classification": "Thumb-2 instruction-halfword collisions; no exact entry pointers",
        },
        "outgoing": outgoing,
        "dynamic_callbacks": callbacks,
        "diagnostics": diagnostics,
        "upstream": {
            "commit": shared.UPSTREAM_COMMIT,
            "compatibility_baseline": "nanopb-0.4.9",
            "compatible_pristine_range": "0.4.6--0.4.9.1",
            "definitions": definitions,
        },
        "production_candidate": {
            "source": {"size": len(local_source), "sha256": sha256(local_source)},
            "header": {"size": len(local_header), "sha256": sha256(local_header)},
            "functions": PRODUCTION_FUNCTIONS,
            "leaf_offsets": PRODUCTION_OFFSETS,
            "patch_sites": PRODUCTION_PATCH_SITES,
        },
        "decision": {
            "source_identification_percent": 100,
            "semantic_recovery_percent": 100,
            "source_recreation_percent": 100,
            "production_candidate": True,
            "production_integrated": True,
            "fixed_stock_seams_in_candidate": 0,
            "dynamic_callback_seams": 2,
            "stored_pointer_ingress": 0,
            "alternate_executable_ingress": 0,
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
            "nanopb field decoder promotion unit: "
            f"{sum(item['size'] for item in report['stock']['segments'])} stock bytes; "
            "source candidate closed with zero fixed stock seams"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
