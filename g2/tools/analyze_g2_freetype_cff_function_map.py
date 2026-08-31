#!/usr/bin/env python3
"""Close the complete stock G2 FreeType 2.9.1 CFF physical map.

The earlier CFF admission source-authenticated a useful 38-function engine
subset (and nine base support functions), but did not claim that it covered
the complete stock CFF translation-unit envelope.  This analyzer keeps that
candidate distinct, authenticates all omitted callbacks/private bodies, and
classifies every non-callable byte between the preceding autofit boundary and
the next stock callable.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
GHIDRA = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
SNAPSHOT = G2 / "third_party/freetype"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
WAVE_BOUNDARIES = (
    G2 / "research/admission/apollo_opacity_wave11/source_boundaries.tsv",
    G2 / "research/admission/apollo_opacity_wave14/source_boundaries.tsv",
)
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-function-map.json"

LOAD_BASE = 0x00437FE0
ENVELOPE = (0x005ABEF8, 0x005B0114)
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
GHIDRA_PIN = (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
PROVENANCE_PIN = (102_377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf")
WAVE_PINS = (
    (12_422, "d921788723eef345a04eb40b67724abba0e70aee5a268fa4dbaf87a57e2405b4"),
    (1_695, "8cc4ae11e418c4ce8b7c19a962aa2ae404e3291034de740a0604a669899c13a6"),
)
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"

# Additional one-word slots outside the compact tables checked in-line.  They
# cover the glyph-dictionary, PS-name, TT-cmap, CID, parser-field-handler, and
# private cmap-name callback entries that otherwise look like ordinary code
# gaps in the incomplete Ghidra relation.
CALLBACK_SLOTS = (
    (0x005AC5EC, 0x005ABF51),
    (0x0067F350, 0x005AD1E9),
    (0x0067F388, 0x005AD355),
    (0x0067F414, 0x005AD3AF),
    (0x0067F468, 0x005AD3EB),
    (0x0067F484, 0x005AD431),
    (0x0067F7B0, 0x005AD1E9),
    (0x0067F83C, 0x005AD521),
    (0x0067F858, 0x005AD3AF),
    (0x0067F874, 0x005AD1E9),
    (0x0067F9FC, 0x005AD47B),
    (0x0067FA18, 0x005AD4B3),
    (0x0078A5EC, 0x005AC469),
    (0x0078A5F0, 0x005AC4E5),
    (0x0078A5F4, 0x005AC50B),
    (0x0078D144, 0x005AC141),
    (0x0078D148, 0x005AC1BD),
    (0x0078EEA0, 0x005AC3CF),
    (0x0078EEA4, 0x005AC415),
)

# Complete address/source order for the selected single-object CFF build.
# Boundaries present in the pinned Ghidra relation are rechecked below.  The
# omitted rows are independently entry-anchored by callback/service/parser
# tables; their end is the next source-ordered entry or an explicit pool.
FUNCTIONS = (
    ("cff_cmap_encoding_init", "cffcmap.c", 0x005ABEF8, 0x005ABF0A),
    ("cff_cmap_encoding_done", "cffcmap.c", 0x005ABF0A, 0x005ABF10),
    ("cff_cmap_encoding_char_index", "cffcmap.c", 0x005ABF10, 0x005ABF22),
    ("cff_cmap_encoding_char_next", "cffcmap.c", 0x005ABF22, 0x005ABF50),
    ("cff_sid_to_glyph_name", "cffcmap.c", 0x005ABF50, 0x005ABF66),
    ("cff_cmap_unicode_init", "cffcmap.c", 0x005ABF66, 0x005ABF98),
    ("cff_cmap_unicode_done", "cffcmap.c", 0x005ABF98, 0x005ABFB0),
    ("cff_cmap_unicode_char_index", "cffcmap.c", 0x005ABFB0, 0x005ABFC2),
    ("cff_cmap_unicode_char_next", "cffcmap.c", 0x005ABFC2, 0x005ABFD4),
    ("cff_get_kerning", "cffdrivr.c", 0x005ABFD4, 0x005ABFF2),
    ("cff_glyph_load", "cffdrivr.c", 0x005ABFF2, 0x005AC02A),
    ("cff_get_advances", "cffdrivr.c", 0x005AC02A, 0x005AC140),
    ("cff_get_glyph_name", "cffdrivr.c", 0x005AC140, 0x005AC1BC),
    ("cff_get_name_index", "cffdrivr.c", 0x005AC1BC, 0x005AC26A),
    ("cff_ps_has_glyph_names", "cffdrivr.c", 0x005AC26A, 0x005AC27E),
    ("cff_ps_get_font_info", "cffdrivr.c", 0x005AC27E, 0x005AC30A),
    ("cff_ps_get_font_extra", "cffdrivr.c", 0x005AC30A, 0x005AC3CE),
    ("cff_get_ps_name", "cffdrivr.c", 0x005AC3CE, 0x005AC414),
    ("cff_get_cmap_info", "cffdrivr.c", 0x005AC414, 0x005AC468),
    ("cff_get_ros", "cffdrivr.c", 0x005AC468, 0x005AC4E4),
    ("cff_get_is_cid", "cffdrivr.c", 0x005AC4E4, 0x005AC50A),
    ("cff_get_cid_from_glyph_index", "cffdrivr.c", 0x005AC50A, 0x005AC548),
    ("cff_set_mm_blend", "cffdrivr.c", 0x005AC548, 0x005AC554),
    ("cff_get_mm_blend", "cffdrivr.c", 0x005AC554, 0x005AC560),
    ("cff_get_mm_var", "cffdrivr.c", 0x005AC560, 0x005AC56C),
    ("cff_set_var_design", "cffdrivr.c", 0x005AC56C, 0x005AC578),
    ("cff_get_var_design", "cffdrivr.c", 0x005AC578, 0x005AC584),
    ("cff_set_instance", "cffdrivr.c", 0x005AC584, 0x005AC590),
    ("cff_hadvance_adjust", "cffdrivr.c", 0x005AC590, 0x005AC59C),
    ("cff_metrics_adjust", "cffdrivr.c", 0x005AC59C, 0x005AC5A8),
    ("cff_get_interface", "cffdrivr.c", 0x005AC5A8, 0x005AC5E8),
    ("cff_get_glyph_data", "cffgload.c", 0x005AC5F0, 0x005AC634),
    ("cff_free_glyph_data", "cffgload.c", 0x005AC634, 0x005AC66E),
    ("cff_slot_load", "cffgload.c", 0x005AC66E, 0x005ACD02),
    ("cff_parser_init", "cffparse.c", 0x005ACD08, 0x005ACD72),
    ("cff_parser_done", "cffparse.c", 0x005ACD72, 0x005ACD86),
    ("cff_parse_integer", "cffparse.c", 0x005ACD86, 0x005ACDFE),
    ("cff_parse_real", "cffparse.c", 0x005ACE10, 0x005AD080),
    ("cff_parse_num", "cffparse.c", 0x005AD090, 0x005AD0DA),
    ("do_fixed", "cffparse.c", 0x005AD0DA, 0x005AD150),
    ("cff_parse_fixed", "cffparse.c", 0x005AD150, 0x005AD15A),
    ("cff_parse_fixed_scaled", "cffparse.c", 0x005AD15A, 0x005AD162),
    ("cff_parse_fixed_dynamic", "cffparse.c", 0x005AD162, 0x005AD1E4),
    ("cff_parse_font_matrix", "cffparse.c", 0x005AD1E8, 0x005AD354),
    ("cff_parse_font_bbox", "cffparse.c", 0x005AD354, 0x005AD3AE),
    ("cff_parse_private_dict", "cffparse.c", 0x005AD3AE, 0x005AD3EA),
    ("cff_parse_multiple_master", "cffparse.c", 0x005AD3EA, 0x005AD430),
    ("cff_parse_cid_ros", "cffparse.c", 0x005AD430, 0x005AD47A),
    ("cff_parse_vsindex", "cffparse.c", 0x005AD47A, 0x005AD4B2),
    ("cff_parse_blend", "cffparse.c", 0x005AD4B2, 0x005AD520),
    ("cff_parse_maxstack", "cffparse.c", 0x005AD520, 0x005AD564),
    ("cff_parser_run", "cffparse.c", 0x005AD564, 0x005AD74A),
    ("cff_get_standard_encoding", "cffload.c", 0x005AD74A, 0x005AD760),
    ("cff_index_read_offset", "cffload.c", 0x005AD778, 0x005AD7AC),
    ("cff_index_init", "cffload.c", 0x005AD7AC, 0x005AD8C0),
    ("cff_index_done", "cffload.c", 0x005AD8C0, 0x005AD8F6),
    ("cff_index_load_offsets", "cffload.c", 0x005AD8F6, 0x005AD9FE),
    ("cff_index_get_pointers", "cffload.c", 0x005AD9FE, 0x005ADB46),
    ("cff_index_access_element", "cffload.c", 0x005ADB46, 0x005ADC4E),
    ("cff_index_forget_element", "cffload.c", 0x005ADC4E, 0x005ADC5E),
    ("cff_index_get_name", "cffload.c", 0x005ADC5E, 0x005ADCC6),
    ("cff_index_get_string", "cffload.c", 0x005ADCC6, 0x005ADCDC),
    ("cff_index_get_sid_string", "cffload.c", 0x005ADCDC, 0x005ADD1A),
    ("CFF_Done_FD_Select", "cffload.c", 0x005ADD1A, 0x005ADD3C),
    ("CFF_Load_FD_Select", "cffload.c", 0x005ADD3C, 0x005ADDB8),
    ("cff_fd_select_get", "cffload.c", 0x005ADDB8, 0x005ADE30),
    ("cff_charset_compute_cids", "cffload.c", 0x005ADE30, 0x005ADEA4),
    ("cff_charset_cid_to_gindex", "cffload.c", 0x005ADEA4, 0x005ADEB6),
    ("cff_charset_free_cids", "cffload.c", 0x005ADEB6, 0x005ADECC),
    ("cff_charset_done", "cffload.c", 0x005ADECC, 0x005ADEF0),
    ("cff_charset_load", "cffload.c", 0x005ADEF0, 0x005AE110),
    ("cff_vstore_done", "cffload.c", 0x005AE118, 0x005AE188),
    ("cff_vstore_load", "cffload.c", 0x005AE188, 0x005AE42C),
    ("cff_blend_clear", "cffload.c", 0x005AE42C, 0x005AE43C),
    ("cff_blend_doBlend", "cffload.c", 0x005AE43C, 0x005AE5F0),
    ("cff_blend_build_vector", "cffload.c", 0x005AE5F0, 0x005AE7BC),
    ("cff_blend_check_vector", "cffload.c", 0x005AE7BC, 0x005AE7EA),
    ("cff_get_var_blend", "cffload.c", 0x005AE7EA, 0x005AE7FA),
    ("cff_done_blend", "cffload.c", 0x005AE7FA, 0x005AE80A),
    ("cff_encoding_done", "cffload.c", 0x005AE80A, 0x005AE818),
    ("cff_encoding_load", "cffload.c", 0x005AE818, 0x005AEA90),
    ("cff_load_private_dict", "cffload.c", 0x005AEA90, 0x005AEBE6),
    ("cff_subfont_load", "cffload.c", 0x005AEBF4, 0x005AEE28),
    ("cff_subfont_done", "cffload.c", 0x005AEE28, 0x005AEE7C),
    ("cff_font_load", "cffload.c", 0x005AEE7C, 0x005AF2D8),
    ("cff_font_done", "cffload.c", 0x005AF2D8, 0x005AF3E6),
    ("cff_size_get_globals_funcs", "cffobjs.c", 0x005AF3E6, 0x005AF418),
    ("cff_size_done", "cffobjs.c", 0x005AF420, 0x005AF468),
    ("cff_make_private_dict", "cffobjs.c", 0x005AF468, 0x005AF576),
    ("cff_size_init", "cffobjs.c", 0x005AF576, 0x005AF616),
    ("cff_size_select", "cffobjs.c", 0x005AF616, 0x005AF6A8),
    ("cff_size_request", "cffobjs.c", 0x005AF6A8, 0x005AF766),
    ("cff_slot_done", "cffobjs.c", 0x005AF766, 0x005AF770),
    ("cff_slot_init", "cffobjs.c", 0x005AF770, 0x005AF7A2),
    ("cff_strcpy", "cffobjs.c", 0x005AF7B4, 0x005AF7CC),
    ("remove_subset_prefix", "cffobjs.c", 0x005AF7CC, 0x005AF828),
    ("remove_style", "cffobjs.c", 0x005AF828, 0x005AF88C),
    ("cff_face_init", "cffobjs.c", 0x005AF88C, 0x005B0004),
    ("cff_face_done", "cffobjs.c", 0x005B0008, 0x005B004A),
    ("cff_driver_init", "cffobjs.c", 0x005B004A, 0x005B00C4),
    ("cff_driver_done", "cffobjs.c", 0x005B0110, 0x005B0112),
)

PHYSICAL = (
    (0x005AC5E8, 0x005AC5F0, "literal-pointer-data-pool", "8794af1f195f1191a18e886580673ca9e27009736c4ca7381adf9774b9e400d4"),
    (0x005ACD02, 0x005ACD08, "literal-pointer-data-pool", "bec0b850f2b4fdd32b68f56dab3bbcd13f1ef527c113690eddef7f0fe53842bd"),
    (0x005ACDFE, 0x005ACE10, "literal-pointer-data-pool", "dfaa060b1862c82fb832072db1abb32809fa0bbee2be458568ff2a67e998ae0a"),
    (0x005AD080, 0x005AD090, "literal-pointer-data-pool", "1cd4cdde27ecc08cb44333fa1608793863c07f6de7ee10599ca4ca20d0763919"),
    (0x005AD1E4, 0x005AD1E8, "literal-pointer-data-pool", "9471931ae99ff0cfd3f6af4b4e1f26e547bd64e969836e3bda46345005e73352"),
    (0x005AD760, 0x005AD778, "literal-pointer-data-pool", "d32e5d790d025a61912f4ebc1b452ab2a1ca7c71b0fb1a6bd826d31450c95921"),
    (0x005AE110, 0x005AE118, "literal-pointer-data-pool", "38903642c518e48190623d5c451842a4709987f888b33ece29a4f3c054d384a9"),
    (0x005AEBE6, 0x005AEBF4, "literal-pointer-data-pool", "17e867d77afa602e9e42c18a35e5e725a677a06e21bf241741fd2e7d39565e41"),
    (0x005AF418, 0x005AF420, "literal-pointer-data-pool", "02bcacc3ed57032b14b11544bd64dc72f92d5836996d150e2332a4e10f1b818e"),
    (0x005AF7A2, 0x005AF7B4, "literal-pointer-data-pool", "b1f424b21b7f0bff6a308a074c56a31459c9ed3aedc7f494ccdc585be0226dfc"),
    (0x005B0004, 0x005B0008, "literal-pointer-data-pool", "305a08ebb88f122163cd5ec75ce506fd9bb7c62971f43462dac455db460f35da"),
    (0x005B00C4, 0x005B0110, "literal-pointer-data-pool", "a323d73bccfd7cac164c79ec228b2497645f16664af02aaff2dbd555e48ff04b"),
    (0x005B0112, 0x005B0114, "alignment-padding", "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
)


class MapError(RuntimeError):
    """Raised when a complete-map input or invariant changes."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MapError(message)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    _require((len(data), _sha(data)) == pin, f"input pin drift: {path}")
    return data


def _slice(image: bytes, start: int, end: int) -> bytes:
    data = image[start - LOAD_BASE:end - LOAD_BASE]
    _require(len(data) == end - start, f"unavailable image interval: 0x{start:08X}")
    return data


def _words(image: bytes, address: int, count: int) -> tuple[int, ...]:
    return struct.unpack(f"<{count}I", _slice(image, address, address + 4 * count))


def _narrow_candidate() -> tuple[set[int], int]:
    starts: set[int] = set()
    total = 0
    for path, pin in zip(WAVE_BOUNDARIES, WAVE_PINS):
        text = _pinned(path, pin).decode("utf-8")
        lines = [line for line in text.splitlines() if not line.startswith("#")]
        for row in csv.DictReader(lines, delimiter="\t"):
            if row["license_status"] == "FTL" and "/src/cff/" in row["source_path"]:
                starts.add(int(row["entry"], 16))
                total += int(row["envelope_bytes"])
    _require((len(starts), total) == (38, 11_326), "narrow CFF candidate drift")
    return starts, total


def run_audit() -> dict[str, Any]:
    image = _pinned(IMAGE, IMAGE_PIN)
    ghidra_data = _pinned(GHIDRA, GHIDRA_PIN)
    provenance = json.loads(_pinned(PROVENANCE, PROVENANCE_PIN))
    _require(provenance["upstream"]["peeled_commit"] == UPSTREAM_COMMIT,
             "FreeType source commit drift")

    translation = (SNAPSHOT / "src/cff/cff.c").read_text(encoding="utf-8")
    include_order = (
        "cffcmap.c", "cffdrivr.c", "cffgload.c", "cffparse.c",
        "cffpic.c", "cffload.c", "cffobjs.c",
    )
    positions = [translation.find(f'#include "{name}"') for name in include_order]
    _require(-1 not in positions and positions == sorted(positions),
             "CFF single-object include order drift")

    # Exact tables independently fix all otherwise-Ghidra-missed public,
    # service, variation, parser-handler, and lifecycle entry points.
    _require(_words(image, 0x0074805C, 20) == (
        0x14, 0x005ABEF9, 0x005ABF0B, 0x005ABF11, 0x005ABF23,
        0, 0, 0, 0, 0, 0x18, 0x005ABF67, 0x005ABF99,
        0x005ABFB1, 0x005ABFC3, 0, 0, 0, 0, 0,
    ), "CFF cmap class tables drift")
    _require(_words(image, 0x006DCB74, 24) == (
        0xD01, 0x48, 0x0078EE9C, 0x10000, 0x20000, 0,
        0x005B004B, 0x005B0111, 0x005AC5A9, 0x340, 0x30, 0xAC,
        0x005AF88D, 0x005B0009, 0x005AF577, 0x005AF421,
        0x005AF771, 0x005AF767, 0x005ABFF3, 0x005ABFD5, 0,
        0x005AC02B, 0x005AF6A9, 0x005AF617,
    ), "CFF driver class drift")
    _require(_words(image, 0x0077E848, 10) == (
        0x005AC27F, 0x005AC30B, 0x005AC26B, 0, 0,
        0x005AD74B, 0x005AEA91, 0x005ADDB9, 0x005AE7BD, 0x005AE5F1,
    ), "CFF PS-info/CFF-load service tables drift")
    _require(_words(image, 0x007480B0, 9) == (
        0, 0x005AC549, 0x005AC555, 0x005AC561, 0x005AC56D,
        0x005AC579, 0x005AC585, 0x005AE7EB, 0x005AE7FB,
    ), "CFF multiple-masters service table drift")
    _require(_words(image, 0x0075E5AC, 9) == (
        0x6E6F, 0x005AC591, 0, 0, 0, 0, 0, 0, 0x005AC59D,
    ), "CFF metrics-variations service table drift")
    for slot, pointer in CALLBACK_SLOTS:
        _require(_words(image, slot, 1) == (pointer,),
                 f"CFF callback/parser slot drift: 0x{slot:08X}")

    ghidra: dict[int, dict[str, Any]] = {}
    trailing: dict[str, Any] | None = None
    for line in ghidra_data.splitlines():
        row = json.loads(line)
        start = int(row["entry"], 16)
        if ENVELOPE[0] <= start < ENVELOPE[1]:
            _require(start not in ghidra, f"duplicate Ghidra entry: 0x{start:08X}")
            ghidra[start] = row
        elif start == ENVELOPE[1]:
            trailing = row
    mapped_starts = {start for _, _, start, _ in FUNCTIONS}
    _require(set(ghidra).issubset(mapped_starts), "unmapped Ghidra CFF callable")
    _require(trailing is not None and trailing["body_bytes"] == 8,
             "post-CFF callable boundary drift")

    by_path = {row["local_path"]: row for row in provenance["files"]}
    source_text: dict[str, str] = {}
    inventory: dict[str, str] = {}
    for module in sorted({module for _, module, _, _ in FUNCTIONS}):
        local = f"src/cff/{module}"
        _require(local in by_path, f"unproven CFF source: {local}")
        data = (SNAPSHOT / local).read_bytes()
        upstream = by_path[local]
        _require((len(data), _sha(data)) == (upstream["size"], upstream["sha256"]),
                 f"CFF source identity drift: {local}")
        source_text[module] = data.decode("utf-8", errors="replace")
        inventory[local] = upstream["sha256"]

    # Definition/address order is stable inside each upstream implementation.
    source_order: dict[str, list[tuple[int, int]]] = {}
    candidate_starts, candidate_bytes = _narrow_candidate()
    records: list[dict[str, Any]] = []
    intervals: list[tuple[int, int]] = []
    for symbol, module, start, end in FUNCTIONS:
        matches = list(re.finditer(rf"(?m)^\s*{re.escape(symbol)}\s*\(", source_text[module]))
        _require(matches, f"CFF source definition missing: {module}:{symbol}")
        source_order.setdefault(module, []).append((start, matches[0].start()))
        body = _slice(image, start, end)
        if start in ghidra:
            row = ghidra[start]
            _require(int(row["body_end_inclusive"], 16) + 1 == end and
                     row["body_bytes"] == end - start and
                     row["body_sha256"] == _sha(body),
                     f"Ghidra whole-body drift: {symbol}")
            origin = "pinned-ghidra-source-order-call-semantics"
        else:
            origin = "authenticated-table-source-order-thumb-boundary"
        intervals.append((start, end))
        records.append({
            "symbol": symbol,
            "module": module,
            "start": f"0x{start:08X}",
            "end_exclusive": f"0x{end:08X}",
            "bytes": end - start,
            "body_sha256": _sha(body),
            "confidence": "high",
            "mapping_origin": origin,
            "identity_corroboration": [
                "exact-official-body-hash",
                "pinned-freetype-2.9.1-definition-and-source-order",
                "call-service-parser-table-or-thumb-semantics",
            ],
            "present_in_narrow_candidate": start in candidate_starts,
            "compiler_byte_identity_claimed": False,
        })
    for module, pairs in source_order.items():
        ordered = sorted(pairs)
        _require([position for _, position in ordered] ==
                 sorted(position for _, position in ordered),
                 f"CFF source/address order drift: {module}")

    physical_records: list[dict[str, Any]] = []
    category_bytes: dict[str, int] = {}
    for start, end, category, digest in PHYSICAL:
        _require(_sha(_slice(image, start, end)) == digest,
                 f"CFF physical residue drift: 0x{start:08X}")
        intervals.append((start, end))
        category_bytes[category] = category_bytes.get(category, 0) + end - start
        physical_records.append({
            "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
            "bytes": end - start, "category": category, "sha256": digest,
            "callable": False,
        })

    cursor = ENVELOPE[0]
    for start, end in sorted(intervals):
        _require(start == cursor,
                 f"unmapped or overlapping CFF byte at 0x{cursor:08X}")
        cursor = end
    _require(cursor == ENVELOPE[1], "CFF physical envelope incomplete")

    callable_bytes = sum(row["bytes"] for row in records)
    _require((len(records), callable_bytes) == (101, 16_718),
             "complete CFF callable accounting drift")
    _require((len(physical_records), sum(row["bytes"] for row in physical_records)) ==
             (13, 206), "CFF physical residue accounting drift")
    _require(sum(row["bytes"] for row in records if row["present_in_narrow_candidate"]) ==
             candidate_bytes, "narrow candidate no longer a complete subset")

    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-cff-callable-physical-closure",
        "analysis_mode": "read-only; no hardware or flash operation",
        "image": {
            "bytes": IMAGE_PIN[0], "sha256": IMAGE_PIN[1],
            "run_address_rule": "run = file_offset + 0x00437FE0",
        },
        "upstream": {
            "version": "2.9.1", "tag": "VER-2-9-1",
            "commit": UPSTREAM_COMMIT, "license": "FTL",
        },
        "scope": {
            "module": "cff",
            "envelope_start": f"0x{ENVELOPE[0]:08X}",
            "envelope_end_exclusive": f"0x{ENVELOPE[1]:08X}",
            "physical_bytes": ENVELOPE[1] - ENVELOPE[0],
            "callable_bytes": callable_bytes,
            "residual_physical": {
                "intervals": len(physical_records), "bytes": 206,
                "category_bytes": category_bytes,
                "unclassified_bytes": 0, "unresolved_callable_bytes": 0,
            },
        },
        "candidate_distinction": {
            "existing_cff_candidate_functions": len(candidate_starts),
            "existing_cff_candidate_bytes": candidate_bytes,
            "existing_base_support_functions": 9,
            "existing_base_support_bytes": 736,
            "newly_mapped_cff_functions": len(records) - len(candidate_starts),
            "newly_mapped_cff_callable_bytes": callable_bytes - candidate_bytes,
            "existing_candidate_scope": (
                "two retained source-identity waves plus base support; not a complete CFF physical map"
            ),
            "this_scope": "complete stock CFF callable and physical envelope",
        },
        "authenticated_tables": {
            "cmap_classes": "0x0074805C",
            "driver_class": "0x006DCB74",
            "ps_info_and_cff_load_services": "0x0077E848",
            "multiple_masters_service": "0x007480B0",
            "metrics_variations_service": "0x0075E5AC",
            "additional_callback_and_parser_slots": len(CALLBACK_SLOTS),
        },
        "source_inventory": {
            "files": len(inventory),
            "sha256_by_path": dict(sorted(inventory.items())),
            "inventory_sha256": _canonical(dict(sorted(inventory.items()))),
        },
        "confidence": {
            "high": {"functions": len(records), "bytes": callable_bytes},
            "medium": {"functions": 0, "bytes": 0},
            "mapped_total": {"functions": len(records), "bytes": callable_bytes},
            "unresolved_code": {
                "functions": 0, "bytes": 0, "source_identities_complete": True,
            },
        },
        "functions": records,
        "physical_residue": physical_records,
        "evidence_bounds": {
            "compiler_byte_identity_claimed": False,
            "production_routing_claimed": False,
            "authenticated_target_placement": False,
            "font_payload_authenticated": False,
            "stack_or_wcet_qualified": False,
            "hardware_validation_performed": False,
        },
    }
    result["mapping_sha256"] = _canonical({
        "envelope": list(ENVELOPE), "functions": records,
        "physical_residue": physical_records,
        "authenticated_tables": result["authenticated_tables"],
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    try:
        report = run_audit()
        if args.write_manifest:
            MANIFEST.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8")
        if args.check_manifest:
            _require(MANIFEST.is_file() and
                     json.loads(MANIFEST.read_text(encoding="utf-8")) == report,
                     "checked-in CFF function-map manifest drift")
    except (MapError, KeyError, OSError, ValueError) as error:
        print(f"G2 FreeType CFF map failed: {error}")
        return 1
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
