#!/usr/bin/env python3
"""Close the complete stock G2 FreeType 2.9.1 base physical map.

The older base admission deliberately covered a 90-function reachable/source
candidate.  This analyzer retains that evidence tier, corrects one Ghidra
internal-basic-block false positive, recovers five complete callable bodies
that Ghidra did not promote, and accounts for every byte in the surrounding
stock base envelope.  It is read-only and makes no placement, routing,
compiler-byte-identity, font-payload, or hardware claim.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SNAPSHOT = G2 / "third_party/freetype"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
LICENSE = SNAPSHOT / "LICENSE"
DECOMP = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles"
OLD_ANALYZER = G2 / "research/candidates/freetype/analyze_base_cluster_candidate.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-base-function-map.json"

LOAD_BASE = 0x00437FE0
ENVELOPE = (0x005242FC, 0x005293C0)
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
PROVENANCE_PIN = (102_377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf")
LICENSE_PIN = (6_743, "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1")
OLD_ANALYZER_PIN = (27_655, "2ef89ebbc425bb2293b0eaa75e93f5ce6923d222fbd40dfa4637382df84d2003")
DECOMP_PINS = {
    "apollo-decomp-08.c": (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    "apollo-decomp-09.c": (439_956, "03672a605bd92ceef591a0f4ca478d48960f71a76a1517cfe9a6fd4b2150b07f"),
}
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"


class MapError(RuntimeError):
    """Raised when any authenticated input or complete-map invariant drifts."""


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


def _words(image: bytes, start: int, count: int) -> tuple[int, ...]:
    return struct.unpack(f"<{count}I", _slice(image, start, start + 4 * count))


def _load_old_analyzer() -> Any:
    _pinned(OLD_ANALYZER, OLD_ANALYZER_PIN)
    spec = importlib.util.spec_from_file_location("open_cfw_freetype_base_old", OLD_ANALYZER)
    _require(spec is not None and spec.loader is not None, "old base analyzer unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# The ten documented high-confidence anchors already counted by the old
# 83-function base cluster but intentionally not duplicated in its source map.
BASELINE = {
    0x005242FC: ("FT_Add_Default_Modules", "src/base/ftinit.c"),
    0x0052431C: ("FT_Init_FreeType", "src/base/ftinit.c"),
    0x005258A8: ("destroy_face", "src/base/ftobjs.c"),
    0x005259BE: ("open_face", "src/base/ftobjs.c"),
    0x005264A6: ("FT_Open_Face", "src/base/ftobjs.c"),
    0x00526814: ("FT_Done_Face", "src/base/ftobjs.c"),
    0x0052729C: ("FT_Add_Module", "src/base/ftobjs.c"),
    0x005274B2: ("FT_New_Library", "src/base/ftobjs.c"),
    0x00527F0A: ("ps_property_set", "src/base/ftpsprop.c"),
    0x00527FF2: ("ps_property_get", "src/base/ftpsprop.c"),
}


# Functions outside the older 90-function candidate.  Each ordinary row is
# bounded by the pinned Ghidra function header and authenticated image bytes;
# RECOVERED overrides the six exceptional physical boundaries below.
ADDITIONS = {
    0x00524354: ("_ft_face_scale_advances", "src/base/ftadvanc.c"),
    0x00524398: ("FT_Get_Advance", "src/base/ftadvanc.c"),
    0x00524412: ("FT_Get_Advances", "src/base/ftadvanc.c"),
    0x005244EE: ("FT_RoundFix", "src/base/ftcalc.c"),
    0x00524506: ("FT_MSB", "src/base/ftcalc.c"),
    0x0052453C: ("FT_Hypot", "src/base/ftcalc.c"),
    0x0052454A: ("ft_multo64", "src/base/ftcalc.c"),
    0x00524588: ("ft_div64by32", "src/base/ftcalc.c"),
    0x005245E0: ("FT_Add64", "src/base/ftcalc.c"),
    0x00524606: ("FT_MulDiv", "src/base/ftcalc.c"),
    0x00524690: ("FT_MulDiv_No_Round", "src/base/ftcalc.c"),
    0x005246F8: ("FT_MulFix", "src/base/ftcalc.c"),
    0x00524754: ("FT_DivFix", "src/base/ftcalc.c"),
    0x005247C6: ("FT_Matrix_Invert", "src/base/ftcalc.c"),
    0x00524820: ("FT_Matrix_Multiply_Scaled", "src/base/ftcalc.c"),
    0x005248AE: ("FT_Vector_Transform_Scaled", "src/base/ftcalc.c"),
    0x00524902: ("FT_Vector_NormLen", "src/base/ftcalc.c"),
    0x00524A30: ("ft_corner_orientation", "src/base/ftcalc.c"),
    0x00524AD6: ("ft_corner_is_flat", "src/base/ftcalc.c"),
    0x00524B64: ("FT_Get_Font_Format", "src/base/ftfntfmt.c"),
    0x00524EC6: ("hash_lookup", "src/base/fthash.c"),
    0x00524F18: ("ft_hash_str_lookup", "src/base/fthash.c"),
    0x00524F2E: ("ft_hash_num_lookup", "src/base/fthash.c"),
    0x00524F36: ("ft_lcd_padding", "src/base/ftlcdfil.c"),
    0x00524F44: ("ft_service_list_lookup", "src/base/ftobjs.c"),
    0x00524F70: ("ft_validator_init", "src/base/ftobjs.c"),
    0x00524F84: ("ft_validator_run", "src/base/ftobjs.c"),
    0x00524F96: ("FT_Stream_New", "src/base/ftobjs.c"),
    0x005250DE: ("ft_glyphslot_preset_bitmap", "src/base/ftobjs.c"),
    0x00525444: ("FT_Set_Transform", "src/base/ftobjs.c"),
    0x005254C8: ("ft_glyphslot_grid_fit_metrics", "src/base/ftobjs.c"),
    0x00525574: ("FT_Load_Glyph", "src/base/ftobjs.c"),
    0x00526944: ("FT_Match_Size", "src/base/ftobjs.c"),
    0x00526A02: ("ft_synthesize_vertical_metrics", "src/base/ftobjs.c"),
    0x00526A4E: ("ft_recompute_scaled_metrics", "src/base/ftobjs.c"),
    0x00526A9C: ("FT_Select_Metrics", "src/base/ftobjs.c"),
    0x00526B04: ("FT_Request_Metrics", "src/base/ftobjs.c"),
    0x00526CA8: ("FT_Select_Size", "src/base/ftobjs.c"),
    0x00526CE4: ("FT_Request_Size", "src/base/ftobjs.c"),
    0x00526D54: ("FT_Set_Pixel_Sizes", "src/base/ftobjs.c"),
    0x00526DEE: ("FT_Set_Charmap", "src/base/ftobjs.c"),
    0x00526F10: ("FT_Get_Char_Index", "src/base/ftobjs.c"),
    0x00526F32: ("FT_Get_First_Char", "src/base/ftobjs.c"),
    0x00526F74: ("FT_Get_Next_Char", "src/base/ftobjs.c"),
    0x0052700A: ("FT_Get_CMap_Format", "src/base/ftobjs.c"),
    0x00527406: ("ft_module_get_service", "src/base/ftobjs.c"),
    0x00527508: ("FT_Outline_Decompose", "src/base/ftoutln.c"),
    0x005278C2: ("FT_Outline_New_Internal", "src/base/ftoutln.c"),
    0x0052797A: ("FT_Outline_New", "src/base/ftoutln.c"),
    0x0052798C: ("FT_Outline_Check", "src/base/ftoutln.c"),
    0x005279E0: ("FT_Outline_Copy", "src/base/ftoutln.c"),
    0x00527A70: ("FT_Outline_Done_Internal", "src/base/ftoutln.c"),
    0x00527ABC: ("FT_Outline_Done", "src/base/ftoutln.c"),
    0x00527ACE: ("FT_Outline_Get_CBox", "src/base/ftoutln.c"),
    0x00527B2E: ("FT_Outline_Translate", "src/base/ftoutln.c"),
    0x00527B60: ("FT_Vector_Transform", "src/base/ftoutln.c"),
    0x00527BA0: ("FT_Outline_Transform", "src/base/ftoutln.c"),
    0x00527BCA: ("FT_Outline_Embolden", "src/base/ftoutln.c"),
    0x00527BD6: ("FT_Outline_EmboldenXY", "src/base/ftoutln.c"),
    0x00527E0A: ("FT_Outline_Get_Orientation", "src/base/ftoutln.c"),
    0x00528064: ("FT_Raccess_Get_HeaderInfo", "src/base/ftrfork.c"),
    0x00528272: ("ft_raccess_sort_ref_by_id", "src/base/ftrfork.c"),
    0x00528298: ("FT_Raccess_Get_DataOffsets", "src/base/ftrfork.c"),
    0x005284DE: ("raccess_get_rule_type_from_rule_index", "src/base/ftrfork.c"),
    0x005284F4: ("ft_raccess_rule_by_darwin_vfs", "src/base/ftrfork.c"),
    0x00528540: ("raccess_guess_darwin_ufs_export", "src/base/ftrfork.c"),
    0x0052857E: ("raccess_guess_darwin_hfsplus", "src/base/ftrfork.c"),
    0x00528650: ("raccess_guess_linux_cap", "src/base/ftrfork.c"),
    0x00528674: ("raccess_guess_linux_double", "src/base/ftrfork.c"),
    0x005286B2: ("raccess_guess_linux_netatalk", "src/base/ftrfork.c"),
    0x00528802: ("raccess_guess_linux_double_from_file_name", "src/base/ftrfork.c"),
    0x00528928: ("FT_Stream_Read", "src/base/ftstream.c"),
    0x00528936: ("FT_Stream_ReadAt", "src/base/ftstream.c"),
    0x00528A86: ("FT_Stream_GetChar", "src/base/ftstream.c"),
    0x00528AA0: ("FT_Stream_GetUShort", "src/base/ftstream.c"),
    0x00528AC6: ("FT_Stream_GetULong", "src/base/ftstream.c"),
    0x00528AFA: ("FT_Stream_ReadChar", "src/base/ftstream.c"),
    0x00528DB8: ("ft_trig_downscale", "src/base/fttrigon.c"),
    0x00528E18: ("ft_trig_prenorm", "src/base/fttrigon.c"),
    0x00528E5A: ("ft_trig_pseudo_rotate", "src/base/fttrigon.c"),
    0x00528EE4: ("ft_trig_pseudo_polarize", "src/base/fttrigon.c"),
    0x00528F8C: ("FT_Cos", "src/base/fttrigon.c"),
    0x00528F9A: ("FT_Sin", "src/base/fttrigon.c"),
    0x00528FA8: ("FT_Tan", "src/base/fttrigon.c"),
    0x00528FBC: ("FT_Atan2", "src/base/fttrigon.c"),
    0x00528FDE: ("FT_Vector_Unit", "src/base/fttrigon.c"),
    0x00529006: ("FT_Vector_Rotate", "src/base/fttrigon.c"),
    0x00529086: ("FT_Vector_Length", "src/base/fttrigon.c"),
    0x005290FA: ("FT_Vector_From_Polar", "src/base/fttrigon.c"),
    0x0052910E: ("FT_Angle_Diff", "src/base/fttrigon.c"),
    0x005292BC: ("ft_mem_strcpyn", "src/base/ftutil.c"),
    0x00529348: ("FT_List_Iterate", "src/base/ftutil.c"),
}


# Boundaries absent from, or misrepresented by, the Ghidra function list.
# `ft_mem_strcpyn` is one source body with a branch-to-test layout; Ghidra
# emitted a two-byte thunk and a false function at its internal 0x5292C8
# basic block.  The other five are complete leaf/callback bodies recovered
# from source order, callback-table reachability, and Thumb semantics.
RECOVERED = {
    0x00528272: (0x00528298, "4d1bcbcca39e6e307d64a938bf5dd61526fe56bc5b6ef121b91fd205100fa774",
                 "qsort-comparator-slot-and-thumb-semantics"),
    0x0052857E: (0x005285D4, "a53af9d3af70814b35ec15799149f8d14b569aac7382edf0cbd056eba56fa3a7",
                 "rule-table-slot-and-hfsplus-rsrc-literal"),
    0x00528650: (0x00528674, "432a6644b3559c74473877159cab704ef99d75026a9230a5e668c9f87366f7b6",
                 "rule-table-slot-and-resource-directory-literal"),
    0x00528674: (0x005286B2, "b66e6e6f8a2031c4c4666b7089a9da1a7d255424145901d628ccdd4c58a6a574",
                 "rule-table-slot-and-linux-double-call-edge"),
    0x005286B2: (0x005286F2, "c186f5372ea2de945803c5b55bd4c1d015ea96609b85e031df27a16f96f89478",
                 "rule-table-slot-and-netatalk-call-edge"),
    0x005292BC: (0x005292E6, "636228852e6081f96f63b841ff29a9ab3af9419ce3e8c3c3c027cbe71544bd43",
                 "split-entry-thumb-control-flow-and-source-semantics"),
}


PHYSICAL = (
    (0x00524318, 0x0052431C, "literal-pointer-data-pool", "2f4a50e2973c7cca8eda3ce58dbc9c21d2e38213adc4c011b65fc2c859ab59d1"),
    (0x00524F0A, 0x00524F18, "literal-pointer-data-pool", "dc282ada0265807fc4746a9f3b79d92cc1ff63e867ee33714be0ac0f3ec98ed3"),
    (0x0052609C, 0x005260A4, "literal-pointer-data-pool", "f291c4b5a7f832c7f22b36fbf7f393eb95eb39d8739206ad55d6067b4ec84600"),
    (0x005261A8, 0x005261AC, "literal-pointer-data-pool", "1fd63888c300985149e8cc3a0e2d97e6bbd53043781cbf6cf7518e81e1de7a6f"),
    (0x0052628A, 0x005262AC, "literal-pointer-data-pool", "5248a624b1d675a51fbeabc5bc990a54c27731430aa57c95de3f32ee2b307368"),
    (0x005267EE, 0x00526814, "literal-pointer-data-pool", "5292b8ff4bcd5176c79564c4ed620e5185363f480a482b67c6afe0b34f987a42"),
    (0x005273B2, 0x005273B8, "literal-pointer-data-pool", "0622277a5ae20710b2aa066c7258dbb0dc8659e3fe738c4297ab11ae16c7c637"),
    (0x005274F6, 0x00527508, "literal-pointer-data-pool", "91b51634ac2950b3d93e426e419174029469ee70fa6ca88f75ac87552d96ad1c"),
    (0x00527B5A, 0x00527B60, "literal-pointer-data-pool", "69d157fc739c14fe3d459c892ca53d87f614169689ef7862e21de73bb6a9a4f3"),
    (0x00527E08, 0x00527E0A, "alignment-padding", "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
    (0x005286F2, 0x00528720, "literal-pointer-data-pool", "6917e154e24de20b60aecef5d6425b304701f0a1ac8e3b483f8c5d0641ecb510"),
    (0x00528ED4, 0x00528EE4, "literal-pointer-data-pool", "50c58b1ae9a15584060720ac17e0745879da92af4cc60845998b6807280b5913"),
    (0x00528F86, 0x00528F8C, "literal-pointer-data-pool", "30f5aafc5d6ff0d6254600ef6aa0673db9742510e1463d6635de38a959ac335a"),
    (0x0052912A, 0x00529148, "literal-pointer-data-pool", "98ea9141911cd7feb98c40655a725ffc2222c8a508f7acc3ffe70e96bfd7fedb"),
    (0x005293BE, 0x005293C0, "alignment-padding", "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
)


def _corpus_rows() -> dict[int, dict[str, Any]]:
    marker = re.compile(
        r"/\* FUN 0x([0-9a-f]{8}) ([^ ]+) bytes=(\d+) sha256=([0-9a-f]{64}) \*/"
    )
    result: dict[int, dict[str, Any]] = {}
    for name, pin in DECOMP_PINS.items():
        text = _pinned(DECOMP / name, pin).decode("utf-8", errors="replace")
        for address, recovered_name, size, digest in marker.findall(text):
            start = int(address, 16)
            _require(start not in result, f"duplicate Ghidra entry: 0x{start:08X}")
            result[start] = {
                "ghidra_name": recovered_name,
                "bytes": int(size),
                "body_sha256": digest,
            }
    return result


def _source_inventory(mapping: dict[int, dict[str, str]]) -> dict[str, str]:
    provenance = json.loads(_pinned(PROVENANCE, PROVENANCE_PIN))
    _pinned(LICENSE, LICENSE_PIN)
    _require(provenance["upstream"]["peeled_commit"] == UPSTREAM_COMMIT,
             "FreeType commit drift")
    by_path = {row["local_path"]: row for row in provenance["files"]}
    inventory: dict[str, str] = {}
    source_text: dict[str, str] = {}
    for record in mapping.values():
        source = record["source"]
        if source in inventory:
            continue
        _require(source in by_path, f"source missing from provenance: {source}")
        data = (SNAPSHOT / source).read_bytes()
        _require((len(data), _sha(data)) ==
                 (by_path[source]["size"], by_path[source]["sha256"]),
                 f"source identity drift: {source}")
        inventory[source] = by_path[source]["sha256"]
        source_text[source] = data.decode("utf-8", errors="replace")
    for record in mapping.values():
        symbol = record["symbol"]
        _require(re.search(rf"\b{re.escape(symbol)}\s*\(", source_text[record["source"]]),
                 f"source definition missing: {symbol}")
    return dict(sorted(inventory.items()))


def run_audit() -> dict[str, Any]:
    image = _pinned(IMAGE, IMAGE_PIN)
    old = _load_old_analyzer()
    old_report = old.analyze()
    _require(old_report["admitted_cluster"] == {"functions": 83, "bytes": 7_874},
             "old base cluster drift")
    _require(old_report["fallback_policy"]["mechanics_functions"] == 7 and
             old_report["fallback_policy"]["mechanics_bytes"] == 1_862,
             "old base fallback drift")

    mapping: dict[int, dict[str, str]] = {}

    def add(start: int, symbol: str, source: str, confidence: str, origin: str) -> None:
        _require(start not in mapping, f"duplicate mapped start: 0x{start:08X}")
        mapping[start] = {
            "symbol": symbol,
            "source": source,
            "confidence": confidence,
            "mapping_origin": origin,
        }

    for start, values in old.DIRECT_SOURCE.items():
        add(start, values[2], values[3], "high", "existing-direct-source-semantic-pin")
    for start, values in old.INDIRECT_SOURCE.items():
        add(start, values[2], values[3], "medium", "existing-indirect-source-semantic-pin")
    for start, values in old.UPSTREAM_FALLBACK_MECHANICS.items():
        add(start, values[2], "src/base/ftobjs.c", "high", "existing-fallback-source-semantic-pin")
    for start, (symbol, source) in BASELINE.items():
        add(start, symbol, source, "high", "existing-documented-api-or-string-anchor")
    _require((len(mapping), sum(
        old.DIRECT_SOURCE.get(start, old.INDIRECT_SOURCE.get(
            start, old.UPSTREAM_FALLBACK_MECHANICS.get(start, (0,))))[0]
        if start not in BASELINE else 0 for start in mapping
    )) == (90, 7_584), "old base source map shape drift")
    for start, (symbol, source) in ADDITIONS.items():
        add(start, symbol, source, "high", "complete-source-order-call-string-identity")
    _require(len(ADDITIONS) == 92 and len(mapping) == 182,
             "complete base function census drift")

    inventory = _source_inventory(mapping)
    corpus = _corpus_rows()
    corpus_starts = {start for start in corpus if ENVELOPE[0] <= start < ENVELOPE[1]}
    recovered_absent = set(RECOVERED) - {0x005292BC}
    _require((corpus_starts - {0x005292C8}) | recovered_absent == set(mapping),
             "Ghidra/recovered callable census drift")
    _require(corpus[0x005292BC]["bytes"] == 2 and
             corpus[0x005292C8]["bytes"] == 40,
             "ft_mem_strcpyn split-body evidence drift")
    _require(corpus[0x005293C0] == {
        "ghidra_name": "FUN_005293c0", "bytes": 70,
        "body_sha256": "89a495472cc0fa9e3b6b987fb52bed9185acc5026b933f79b01f9a3e5414ccf9",
    }, "base trailing boundary drift")
    _require(_words(image, 0x006FAC7C, 18) == (
        0x00528509, 0,
        0x00528525, 1,
        0x00528541, 2,
        0x005285D5, 3,
        0x0052857F, 4,
        0x0052862D, 5,
        0x00528651, 6,
        0x00528675, 7,
        0x005286B3, 8,
    ), "resource-fork rule callback table drift")
    _require(_words(image, 0x00528710, 4) == (
        0x00528273, 0x006FAC7C, 0x00051607, 0x00051600,
    ), "resource-fork comparator/table literal evidence drift")
    _require(_slice(image, 0x005292BC, 0x005292BE) == b"\x04\xE0",
             "ft_mem_strcpyn branch-to-test entry drift")

    records: list[dict[str, Any]] = []
    intervals: list[tuple[int, int]] = []
    for start, identity in sorted(mapping.items()):
        if start in RECOVERED:
            end, digest, boundary_evidence = RECOVERED[start]
            origin = f"recovered-{boundary_evidence}"
        else:
            row = corpus.get(start)
            _require(row is not None, f"missing Ghidra body: 0x{start:08X}")
            end = start + row["bytes"]
            digest = row["body_sha256"]
            origin = identity["mapping_origin"]
        body = _slice(image, start, end)
        _require(_sha(body) == digest, f"official body drift: {identity['symbol']}")
        intervals.append((start, end))
        records.append({
            "symbol": identity["symbol"],
            "source": identity["source"],
            "start": f"0x{start:08X}",
            "end_exclusive": f"0x{end:08X}",
            "bytes": end - start,
            "body_sha256": digest,
            "confidence": identity["confidence"],
            "mapping_origin": origin,
            "identity_corroboration": [
                "exact-official-body-hash",
                "pinned-freetype-2.9.1-definition",
                "source-order-and-call-or-string-semantics",
            ],
            "compiler_byte_identity_claimed": False,
        })

    physical_records: list[dict[str, Any]] = []
    category_bytes: dict[str, int] = {}
    for start, end, category, digest in PHYSICAL:
        _require(_sha(_slice(image, start, end)) == digest,
                 f"base physical residue drift: 0x{start:08X}")
        intervals.append((start, end))
        category_bytes[category] = category_bytes.get(category, 0) + end - start
        physical_records.append({
            "start": f"0x{start:08X}",
            "end_exclusive": f"0x{end:08X}",
            "bytes": end - start,
            "category": category,
            "sha256": digest,
            "callable": False,
        })

    cursor = ENVELOPE[0]
    for start, end in sorted(intervals):
        _require(start == cursor,
                 f"unmapped or overlapping base byte at 0x{cursor:08X} (next 0x{start:08X})")
        cursor = end
    _require(cursor == ENVELOPE[1], "base physical envelope incomplete")

    callable_bytes = sum(row["bytes"] for row in records)
    high = [row for row in records if row["confidence"] == "high"]
    medium = [row for row in records if row["confidence"] == "medium"]
    _require((len(records), callable_bytes) == (182, 20_442),
             "complete base callable accounting drift")
    _require((len(high), sum(row["bytes"] for row in high)) == (126, 16_014),
             "base high-confidence accounting drift")
    _require((len(medium), sum(row["bytes"] for row in medium)) == (56, 4_428),
             "base medium-confidence accounting drift")
    _require((len(physical_records), sum(row["bytes"] for row in physical_records)) ==
             (15, 234), "base residual accounting drift")

    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-base-callable-physical-closure",
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
            "module": "base",
            "envelope_start": f"0x{ENVELOPE[0]:08X}",
            "envelope_end_exclusive": f"0x{ENVELOPE[1]:08X}",
            "physical_bytes": ENVELOPE[1] - ENVELOPE[0],
            "callable_bytes": callable_bytes,
            "residual_physical": {
                "intervals": len(physical_records), "bytes": 234,
                "category_bytes": category_bytes,
                "unclassified_bytes": 0,
                "unresolved_callable_bytes": 0,
            },
        },
        "candidate_distinction": {
            "existing_candidate_functions": 90,
            "existing_candidate_bytes": 9_736,
            "newly_mapped_functions": 92,
            "newly_mapped_callable_bytes": 10_706,
            "existing_candidate_scope":
                "83-function reachable base cluster plus seven Mac-resource mechanics; not a complete physical map",
            "this_scope": "complete stock base callable and physical envelope",
        },
        "boundary_corrections": {
            "ghidra_internal_basic_block_removed": "0x005292C8",
            "corrected_source_body": {
                "symbol": "ft_mem_strcpyn", "start": "0x005292BC",
                "end_exclusive": "0x005292E6", "bytes": 42,
            },
            "ghidra_missed_complete_callables": 5,
        },
        "authenticated_tables": {
            "resource_fork_rule_callbacks": "0x006FAC7C",
            "resource_fork_comparator_literal": "0x00528710",
        },
        "source_inventory": {
            "files": len(inventory),
            "sha256_by_path": inventory,
            "inventory_sha256": _canonical(inventory),
        },
        "confidence": {
            "high": {"functions": len(high), "bytes": sum(row["bytes"] for row in high)},
            "medium": {"functions": len(medium), "bytes": sum(row["bytes"] for row in medium)},
            "mapped_total": {"functions": len(records), "bytes": callable_bytes},
            "unresolved_code": {"functions": 0, "bytes": 0, "source_identities_complete": True},
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
        "envelope": list(ENVELOPE),
        "functions": records,
        "physical_residue": physical_records,
        "boundary_corrections": result["boundary_corrections"],
        "authenticated_tables": result["authenticated_tables"],
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    report = run_audit()
    text = json.dumps(report, indent=2 if args.pretty else None, sort_keys=True)
    if args.write_manifest:
        MANIFEST.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
