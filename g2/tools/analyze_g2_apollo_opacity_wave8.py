#!/usr/bin/env python3
"""Close Apollo opacity wave 8 with exact FreeType and support-data evidence.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import struct
from collections import Counter, deque
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
DECOMP = G2 / "research/corpus/apollo-main/ghidra/decomp"
FUNCTIONS = DECOMP / "functions.jsonl"
ADMISSION = G2 / "research/admission/apollo_opacity_wave8"
BOUNDARY = ADMISSION / "typed_boundaries.tsv"
ZERO = ADMISSION / "reconciled_zero_opaque.tsv"
FRONTIER = ADMISSION / "reconciled_frontier.tsv"
SHARED = ADMISSION / "shared_data.tsv"
ROOT = 0x005A8D06
LOAD_ADDRESS = 0x00438000

CORPORA = {
    DECOMP / "bundles/apollo-decomp-01.c": (407_422, "32d621ce69e32a5f10cb366221f2ad0b215a5574ec0a698ddf680c92b28e828d"),
    DECOMP / "bundles/apollo-decomp-03.c": (517_608, "4308ad4bffc6d2e39791e117c535a1627842d4cdbac0a22496e8c03b993c0ef6"),
    DECOMP / "bundles/apollo-decomp-08.c": (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    DECOMP / "bundles/apollo-decomp-13.c": (731_098, "2acd0f0f7b1c9f736f6df76ac0800a76c1ad4da71298322ebe4b63b035dcf703"),
}
FT = G2 / "third_party/freetype"
PINS = {
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    FT / "PROVENANCE.json": (102_377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf"),
    FT / "LICENSE": (6_743, "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1"),
    FT / "src/base/ftadvanc.c": (5_605, "fff8d984307e81273fb8926d22c71b894e1bfa7d33e3502ae3c0197c229a4e8f"),
    FT / "src/base/ftcalc.c": (26_784, "4a0b3452e9b911f67c618a29775f4bcfa6367b9b6b3a1d2b3cf62c6113ce2e8b"),
    FT / "src/base/ftfntfmt.c": (1_898, "80d6613d81f0130619f1092e71f231bb44687da8194ad0c7ea5c8deef67f6a56"),
    FT / "src/base/ftlcdfil.c": (10_427, "af6cbadc9970ee2c6e013b8a130a3b892e7c95f3cc7c096e9462905c8548669b"),
    FT / "src/base/ftobjs.c": (150_798, "9f5533b64c0e1926346bbabb1107a319801ca677b19b6f236ffd379456a6e24e"),
    FT / "src/base/ftoutln.c": (29_019, "823b8100b8f9492239d3fcab599342dd5a210294be15b1cdda9e152b71ec0434"),
    FT / "src/base/ftutil.c": (11_028, "17c2e9b087ddb7969a98d734eb6306efc0217dd2831b249b59e4f37bcb115ad9"),
    **CORPORA,
}

# Tokens are deliberately structural, not just symbol names.  The source files
# and G2 bodies are independently SHA-pinned below.
SOURCE_EVIDENCE = {
    0x00524354: ("_ft_face_scale_advances", "src/base/ftadvanc.c", ("FT_LOAD_NO_SCALE", "FT_MulDiv( advances[nn], scale, 64 )")),
    0x00524398: ("FT_Get_Advance", "src/base/ftadvanc.c", ("LOAD_ADVANCE_FAST_CHECK", "FT_Get_Advances( face, gindex, 1")),
    0x00524412: ("FT_Get_Advances", "src/base/ftadvanc.c", ("FT_LOAD_ADVANCE_ONLY", "FT_Load_Glyph( face, start + nn")),
    0x00524506: ("FT_MSB", "src/base/ftcalc.c", ("0xFFFF0000UL", "0x00000002UL")),
    0x0052454A: ("ft_multo64", "src/base/ftcalc.c", ("i1 = x >> 16", "z->hi = hi")),
    0x00524588: ("ft_div64by32", "src/base/ftcalc.c", ("hi >= y", "q |= 1")),
    0x005245E0: ("FT_Add64", "src/base/ftcalc.c", ("lo = x->lo + y->lo", "lo < x->lo")),
    0x00524606: ("FT_MulDiv", "src/base/ftcalc.c", ("129894UL - ( c >> 17 )", "ft_div64by32")),
    0x005246F8: ("FT_MulFix", "src/base/ftcalc.c", ("8190UL", "0x8000UL")),
    0x00524B64: ("FT_Get_Font_Format", "src/base/ftfntfmt.c", ("FT_FACE_FIND_SERVICE", "FONT_FORMAT")),
    0x00524F36: ("ft_lcd_padding", "src/base/ftlcdfil.c", ("*Min -= 21", "*Max += 21")),
    0x005250DE: ("ft_glyphslot_preset_bitmap", "src/base/ftobjs.c", ("FT_Outline_Get_CBox", "FT_PIXEL_MODE_LCD_V")),
    0x005252BC: ("ft_glyphslot_clear", "src/base/ftobjs.c", ("ft_glyphslot_free_bitmap", "slot->linearVertAdvance = 0")),
    0x005254C8: ("ft_glyphslot_grid_fit_metrics", "src/base/ftobjs.c", ("GRID_FIT_METRICS", "metrics->vertAdvance = FT_PIX_ROUND_LONG")),
    0x00525574: ("FT_Load_Glyph", "src/base/ftobjs.c", ("is_light_type1", "FT_Get_Font_Format( face ), \"Type 1\"")),
    0x00526F10: ("FT_Get_Char_Index", "src/base/ftobjs.c", ("face->charmap", "result >= (FT_UInt)face->num_glyphs")),
    0x00527096: ("ft_lookup_glyph_renderer", "src/base/ftobjs.c", ("library->cur_renderer", "result->glyph_format != slot->format")),
    0x00527228: ("FT_Render_Glyph", "src/base/ftobjs.c", ("FT_FACE_LIBRARY", "FT_Render_Glyph_Internal")),
    0x0052798C: ("FT_Outline_Check", "src/base/ftoutln.c", ("n_points == 0 && n_contours == 0", "end != n_points - 1")),
    0x00527ACE: ("FT_Outline_Get_CBox", "src/base/ftoutln.c", ("xMin = xMax = vec->x", "acbox->yMax = yMax")),
    0x00527B2E: ("FT_Outline_Translate", "src/base/ftoutln.c", ("ADD_LONG( vec->x, xOffset )", "ADD_LONG( vec->y, yOffset )")),
    0x00527B60: ("FT_Vector_Transform", "src/base/ftoutln.c", ("FT_MulFix( vector->x, matrix->xx )", "vector->y = yz")),
    0x00527BA0: ("FT_Outline_Transform", "src/base/ftoutln.c", ("vec + outline->n_points", "FT_Vector_Transform( vec, matrix )")),
    0x00529148: ("ft_mem_alloc", "src/base/ftutil.c", ("ft_mem_qalloc", "FT_MEM_ZERO( block, size )")),
    0x00529256: ("ft_mem_free", "src/base/ftutil.c", ("if ( P )", "memory->free( memory, (void*)P )")),
}
FT_SELECTED = set(SOURCE_EVIDENCE) - {0x005252BC, 0x00527096, 0x00527228, 0x00529148, 0x00529256}
EXPECTED_ROLES = {
    ROOT: "unicode-script-glyph-fit-coordinator",
    0x005A6260: "integer-pointer-insertion-sort",
    0x005A8C8A: "glyph-record-insertion-sort",
    0x005ABA26: "four-byte-scratch-allocation-wrapper",
    0x005ABA34: "scratch-allocation-free-wrapper",
    0x005ABA40: "utf8-first-scalar-token-decoder",
    0x005ABAF8: "glyph-advance-query-wrapper",
    0x0044B63A: "strstr-compatible-runtime-helper",
    **{entry: symbol for entry, (symbol, _, _) in SOURCE_EVIDENCE.items() if entry in FT_SELECTED},
}
EXPECTED_SHARED = {
    0x00524F0C: (0x00524F10, "761be36e07b21e0b0a564b9946f0ae92948140179af7daef277263e4bd42d70b", "scalar-u32", "0x0001FB66", "0x00524606"),
    0x00524F14: (0x00524F18, "bb7eaeda2b1c5abcfee05ccab8e0c618b6a680c51797aad5c6c0eb2b55d94e0e", "pointer-u32", "0x0078AA84", "0x00524B64"),
    0x005261A8: (0x005261AC, "1fd63888c300985149e8cc3a0e2d97e6bbd53043781cbf6cf7518e81e1de7a6f", "pointer-u32", "0x0078D634", "0x00525574"),
    0x005A96F8: (0x005A96FC, "95dbf6c89bccfafc0851bc50afa4ae48549b770f13a611349e06973fec7f12c0", "pointer-u32", "0x0069A3A8", "0x005A8D06"),
    0x005A96FC: (0x005A9700, "5c3c42ffaeeb578bc5f1de7bc97417b59786af17a59ba0529ef7d543df3e6e6b", "pointer-u32", "0x006481F8", "0x005A8D06"),
    0x006481F8: (0x00649661, "b5c19e296827e2585e299aef06e0b903859ee1b2143a3c1c47e2036963930ed0", "nul-terminated-utf8-sequence-pool", "length-0x1469", "0x005A8D06"),
    0x0069A3A8: (0x0069A790, "3f4b673bbaa790994fcc4edf5e7d08ea4d7ae60535d56da8586a81cbfb641f9a", "u16-offset-u16-flags-table", "250-records", "0x005A8D06"),
    0x0078AA84: (0x0078AA90, "33a39ec13ff0c2b5559313665c9a8d6cb06275ff60aedc7042251e88f3d3753d", "nul-terminated-ascii", "font-format", "0x00524B64"),
    0x0078D634: (0x0078D63B, "1164f5164453ac4ec4e4623613dccb236d1f1a5bbafe1566cef5b947ebf5ba29", "nul-terminated-ascii", "Type-1", "0x00525574"),
}


class WaveError(RuntimeError):
    """Raised when authenticated wave-8 evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned(path: Path) -> bytes:
    data = path.read_bytes()
    if (len(data), sha256(data)) != PINS[path]:
        raise WaveError(f"pin drift: {path}")
    return data


def tsv_rows(path: Path) -> list[dict[str, str]]:
    lines = [line for line in path.read_text().splitlines() if not line.startswith("#")]
    if not lines:
        raise WaveError(f"empty TSV: {path}")
    return list(csv.DictReader(lines, delimiter="\t"))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise WaveError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def corpus_function(corpora: dict[Path, str], entry: int) -> tuple[str, int, str, str]:
    hits = []
    for path, corpus in corpora.items():
        marker = re.search(rf"/\* FUN 0x{entry:08x} .*? bytes=(\d+) sha256=([0-9a-f]{{64}}) \*/", corpus)
        if marker is None:
            continue
        end = corpus.find("/* FUN 0x", marker.end())
        if end < 0:
            end = len(corpus)
        hits.append((corpus[marker.start():end], int(marker.group(1)), marker.group(2), path.name))
    if len(hits) != 1:
        raise WaveError(f"0x{entry:08X}: expected one corpus body, found {len(hits)}")
    return hits[0]


def residual_before(wave1, waves: dict[int, Any], parent_none: dict[int, dict[str, str]]) -> set[int]:
    inherited = {path: wave1.pinned(path) for path in wave1.PINS}
    cordio = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-cordio-ll-sea-census.tsv"])
    freetype = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-freetype-engine-census.tsv"])
    liblc3 = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-liblc3-encoder-internals-map.tsv"])
    mspi = load_module(G2 / "tools/analyze_g2_apollo510_mspi_triplet_candidate.py", "opacity_wave8_mspi").run_audit()
    classified = (
        {int(row["entry"], 16) for row in cordio}
        | {int(row["entry"], 16) for row in freetype if row["status"] != "investigation-required"}
        | {int(row["entry"], 16) for row in liblc3 if row["status"] != "investigation-required"}
        | {int(entry, 16) for entry in mspi["triplet"]}
    )
    return (
        set(parent_none) - classified - set(wave1.EXPECTED_SELECTED)
        - set(waves[2].EXPECTED_SELECTED) - set(waves[3].EXPECTED_SELECTED)
        - set(waves[4].EXPECTED_SELECTED) - set(waves[4].EXPECTED_ZERO)
        - set(waves[5].EXPECTED_SELECTED) - set(waves[6].EXPECTED_SELECTED)
        - set(waves[7].EXPECTED_SELECTED) - {0x004397A8, 0x00439C04}
    )


def run_audit() -> dict[str, Any]:
    waves = {i: load_module(G2 / f"tools/analyze_g2_apollo_opacity_wave{i}.py", f"opacity_wave8_wave{i}") for i in range(1, 8)}
    wave1 = waves[1]
    wave7_report = waves[7].run_audit()
    if wave7_report["after"] != {"functions": 1386, "bytes": 163138}:
        raise WaveError("wave-7 residual drift")
    inherited = {path: wave1.pinned(path) for path in wave1.PINS}
    parent_rows = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"])
    parent_by_entry = {int(row["entry"], 16): row for row in parent_rows}
    parent_none = {entry: row for entry, row in parent_by_entry.items() if row["bucket"] == "investigation-required-no-evidence"}
    residual = residual_before(wave1, waves, parent_none)
    before = {"functions": len(residual), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual)}
    if before != wave7_report["after"] or max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual) != (2338, ROOT):
        raise WaveError(f"wave-8 residual/root drift: {before}")

    local = {path: pinned(path) for path in PINS}
    corpora = {path: local[path].decode() for path in CORPORA}
    function_rows = [json.loads(line) for line in local[FUNCTIONS].decode().splitlines()]
    functions = {int(row["entry"], 16): row for row in function_rows}
    payload = inherited[wave1.IMAGE][wave1.OTA_HEADER_BYTES:]
    ft_rows = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-freetype-engine-census.tsv"])
    ft_by_entry = {int(row["entry"], 16): row for row in ft_rows}

    boundary_rows = tsv_rows(BOUNDARY)
    zero_rows = tsv_rows(ZERO)
    boundary_entries = {int(row["entry"], 16) for row in boundary_rows}
    zero_entries = {int(row["entry"], 16) for row in zero_rows}
    if ROOT not in boundary_entries or boundary_entries & zero_entries:
        raise WaveError("boundary root/partition drift")

    # Walk every static call edge whose target remains in the wave-7 residual.
    depths = {ROOT: 0}
    bodies: dict[int, str] = {}
    calls: dict[int, dict[int, int]] = {}
    queue = deque([ROOT])
    while queue:
        entry = queue.popleft()
        body, _, _, _ = corpus_function(corpora, entry)
        bodies[entry] = body
        observed = Counter(int(value, 16) for value in re.findall(r"\bFUN_([0-9a-f]{8})\(", body))
        observed.pop(entry, None)
        calls[entry] = dict(observed)
        for target in observed:
            if target in residual and target not in depths:
                depths[target] = depths[entry] + 1
                queue.append(target)
    derived_positive = {entry for entry in depths if int(parent_none[entry]["official_opaque_bytes"]) > 0}
    derived_zero = set(depths) - derived_positive
    if boundary_entries != derived_positive or zero_entries != derived_zero:
        raise WaveError(f"complete actionable graph drift: positive={derived_positive}, zero={derived_zero}")
    if len(derived_positive) != 28 or sum(int(parent_none[e]["official_opaque_bytes"]) for e in derived_positive) != 5370:
        raise WaveError("positive closure accounting drift")

    records = []
    direct_dat_consumers: dict[int, set[int]] = {}
    range_gap_bytes = 0
    for row in boundary_rows:
        entry = int(row["entry"], 16)
        parent = parent_none[entry]
        end = int(parent["body_end_exclusive"], 16)
        envelope = int(parent["official_opaque_bytes"])
        body, corpus_bytes, corpus_digest, bundle = corpus_function(corpora, entry)
        fn = functions[entry]
        ranges = tuple((int(start, 16), int(end_i, 16) + 1) for start, end_i in fn["ranges"])
        gaps = sum(next_start - previous_end for (_, previous_end), (next_start, _) in zip(ranges, ranges[1:]))
        range_gap_bytes += gaps
        installed = payload[entry - LOAD_ADDRESS:end - LOAD_ADDRESS]
        expected_role = EXPECTED_ROLES[entry]
        static = (int(row["end_exclusive"], 16), int(row["envelope_bytes"]), int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]), row["role"])
        observed = (end, envelope, corpus_bytes, corpus_digest, depths[entry], expected_role)
        if static != observed or len(installed) != envelope or sha256(installed) != corpus_digest:
            raise WaveError(f"0x{entry:08X}: body/boundary drift")
        if ranges != ((entry, end),) or corpus_bytes != envelope or gaps != 0 or fn["body_sha256"] != corpus_digest:
            raise WaveError(f"0x{entry:08X}: non-contiguous or mismatched function range")
        if entry in FT_SELECTED:
            symbol, source_rel, tokens = SOURCE_EVIDENCE[entry]
            if (row["provider_identity"], row["license_status"], row["disposition"], row["source_path"]) != (
                "FreeType-2.9.1-authenticated-upstream", "FTL", "source-attributed-research-candidate", f"third_party/freetype/{source_rel}"
            ):
                raise WaveError(f"0x{entry:08X}: FreeType admission fields drift")
            source = local[FT / source_rel].decode()
            if symbol != row["role"] or symbol not in source or not all(token in source for token in tokens):
                raise WaveError(f"0x{entry:08X}: upstream source evidence drift")
            source_identity = True
        else:
            expected_provider = "IAR-DLIB-family-exact-release-unavailable" if entry == 0x0044B63A else "unresolved-product-font-sequence-provider"
            expected_license = "proprietary-runtime-source-unavailable" if entry == 0x0044B63A else "unavailable"
            if (row["provider_identity"], row["license_status"], row["disposition"], row["source_path"]) != (
                expected_provider, expected_license, "typed-external-provider-unavailable", "-"
            ):
                raise WaveError(f"0x{entry:08X}: unavailable boundary fields drift")
            source_identity = False
        for address in set(int(value, 16) for value in re.findall(r"\bDAT_([0-9a-f]{8})", body)):
            direct_dat_consumers.setdefault(address, set()).add(entry)
        records.append({
            "entry": row["entry"], "end_exclusive": row["end_exclusive"], "envelope_bytes": envelope,
            "corpus_body_bytes": corpus_bytes, "body_sha256": corpus_digest, "corpus_bundle": bundle,
            "closure_depth": depths[entry], "role": row["role"], "provider_identity": row["provider_identity"],
            "license_status": row["license_status"], "disposition": row["disposition"],
            "source_path": row["source_path"], "source_identity_authenticated": source_identity,
            "production_routed": False,
        })

    zero_records = []
    for row in zero_rows:
        entry = int(row["entry"], 16)
        body, body_bytes, digest, bundle = corpus_function(corpora, entry)
        parent = parent_none[entry]
        fn = functions[entry]
        if (
            int(row["end_exclusive"], 16) != int(parent["body_end_exclusive"], 16)
            or int(row["official_opaque_bytes"]) != 0 or int(row["physical_body_bytes"]) != body_bytes
            or row["body_sha256"] != digest or int(row["closure_depth"]) != depths[entry]
            or row["role"] != "strchr-compatible-runtime-helper"
            or row["provider_identity"] != "IAR-DLIB-family-exact-release-unavailable"
            or row["license_status"] != "proprietary-runtime-source-unavailable"
            or row["disposition"] != "zero-opaque-typed-external-provider-unavailable"
            or fn["body_sha256"] != digest or tuple(tuple(value) for value in fn["ranges"]) != (("00481818", "0048182d"),)
            or "cVar1 != param_2" not in body
        ):
            raise WaveError("zero-opaque runtime-helper reconciliation drift")
        bodies[entry] = body
        zero_records.append({"entry": row["entry"], "physical_body_bytes": body_bytes, "official_opaque_bytes": 0, "body_sha256": digest, "corpus_bundle": bundle, "closure_depth": depths[entry], "role": row["role"], "disposition": row["disposition"]})

    # Complete static terminal frontier after all actionable residual callees.
    closure_entries = boundary_entries | zero_entries
    terminal = {target for entry in closure_entries for target in calls[entry] if target not in closure_entries}
    frontier_rows = tsv_rows(FRONTIER)
    frontier_entries = {int(row["entry"], 16) for row in frontier_rows}
    if terminal != frontier_entries or len(terminal) != 6:
        raise WaveError(f"terminal frontier drift: {terminal}")
    frontier_records = []
    for row in frontier_rows:
        entry = int(row["entry"], 16)
        if entry == 0x00439C04:
            if row != {
                "entry": "0x00439C04", "classification": "existing-iar-source-recreated", "symbol": "memcpy", "source_path": "-",
                "provider_identity": "openCFW-clean-room-runtime", "license_status": "MIT", "disposition": "prior-source-recreated",
            } or 0x00439C04 not in waves[3].FRONTIER_PARTITION["existing_iar_source_recreated"]:
                raise WaveError("IAR source-recreated frontier drift")
        else:
            symbol, source_rel, tokens = SOURCE_EVIDENCE[entry]
            source = local[FT / source_rel].decode()
            census = ft_by_entry[entry]
            if (
                row["classification"] != "existing-freetype-family-classified" or row["symbol"] != symbol
                or row["source_path"] != f"third_party/freetype/{source_rel}"
                or row["provider_identity"] != "FreeType-2.9.1-authenticated-upstream" or row["license_status"] != "FTL"
                or row["disposition"] != "exact-source-identity-reconciled" or census["status"] != "cluster"
                or symbol not in source or not all(token in source for token in tokens)
            ):
                raise WaveError(f"0x{entry:08X}: FreeType frontier drift")
        frontier_records.append(dict(row))

    # The direct DAT graph has five cells; four rows below are their targets.
    expected_consumers = {
        0x00524F0C: {0x00524606}, 0x00524F14: {0x00524B64}, 0x005261A8: {0x00525574},
        0x005A96F8: {ROOT}, 0x005A96FC: {ROOT},
    }
    if direct_dat_consumers != expected_consumers:
        raise WaveError(f"direct shared-data graph drift: {direct_dat_consumers}")
    shared_rows = tsv_rows(SHARED)
    if {int(row["start"], 16) for row in shared_rows} != set(EXPECTED_SHARED):
        raise WaveError("shared-data membership drift")
    shared_records = []
    for row in shared_rows:
        start = int(row["start"], 16)
        end, digest, kind, value, consumers = EXPECTED_SHARED[start]
        physical = payload[start - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if (
            int(row["end_exclusive"], 16) != end or int(row["size"]) != end - start or row["sha256"] != digest
            or row["kind"] != kind or row["value_or_target"] != value or row["consumers"] != consumers
            or int(row["wave8_additional_function_bytes"]) != 0 or len(physical) != end - start or sha256(physical) != digest
        ):
            raise WaveError(f"0x{start:08X}: shared-data record drift")
        shared_records.append(dict(row))
    if int.from_bytes(payload[0x00524F0C - LOAD_ADDRESS:0x00524F10 - LOAD_ADDRESS], "little") != 129894:
        raise WaveError("FT_MulDiv scalar discriminator drift")
    for cell, target in ((0x00524F14, 0x0078AA84), (0x005261A8, 0x0078D634), (0x005A96F8, 0x0069A3A8), (0x005A96FC, 0x006481F8)):
        if int.from_bytes(payload[cell - LOAD_ADDRESS:cell + 4 - LOAD_ADDRESS], "little") != target:
            raise WaveError(f"0x{cell:08X}: pointer target drift")
    if payload[0x0078AA84 - LOAD_ADDRESS:0x0078AA90 - LOAD_ADDRESS] != b"font-format\0" or payload[0x0078D634 - LOAD_ADDRESS:0x0078D63B - LOAD_ADDRESS] != b"Type 1\0":
        raise WaveError("FreeType anchor string drift")
    table = payload[0x0069A3A8 - LOAD_ADDRESS:0x0069A790 - LOAD_ADDRESS]
    pool = payload[0x006481F8 - LOAD_ADDRESS:0x00649661 - LOAD_ADDRESS]
    table_records = list(struct.iter_unpack("<HH", table))
    offsets = [offset for offset, _ in table_records if offset != len(pool)]
    string_ends = []
    for offset in set(offsets):
        try:
            end = pool.index(0, offset) + 1
            pool[offset:end - 1].decode("utf-8")
        except (ValueError, UnicodeDecodeError) as error:
            raise WaveError(f"Unicode pool offset 0x{offset:X} invalid") from error
        string_ends.append(end)
    table_stats = {
        "records": len(table_records), "sentinel": len(pool),
        "sentinel_records": sum(offset == len(pool) for offset, _ in table_records),
        "unique_non_sentinel_offsets": len(set(offsets)), "maximum_offset": max(offsets),
        "flag_values": sorted(set(flags for _, flags in table_records)), "maximum_string_end": max(string_ends),
    }
    if table_stats != {"records": 250, "sentinel": 0x1469, "sentinel_records": 53, "unique_non_sentinel_offsets": 186, "maximum_offset": 0x139F, "flag_values": [0, 1, 2, 4, 9, 13, 17], "maximum_string_end": 0x1469}:
        raise WaveError(f"Unicode table/pool closure drift: {table_stats}")

    provenance = json.loads(local[FT / "PROVENANCE.json"])
    if (
        provenance["license"] != "FTL" or provenance["upstream"]["selected_tag"] != "VER-2-9-1"
        or provenance["upstream"]["peeled_commit"] != "86bc8a95056c97a810986434a3f268cbe67f2902"
        or provenance["selection"]["exact_g2_checkout_proven"] is not False
        or "not production-configured" not in provenance["selection"]["integration_status"]
        or b"The FreeType Project LICENSE" not in local[FT / "LICENSE"]
    ):
        raise WaveError("FreeType provenance/license boundary drift")

    residual_after = residual - boundary_entries - zero_entries
    after = {"functions": len(residual_after), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_after)}
    if after != {"functions": 1357, "bytes": 157768}:
        raise WaveError(f"wave-8 after accounting drift: {after}")
    next_size, next_entry = max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_after)
    if (next_size, next_entry) != (2090, 0x0051A8EC):
        raise WaveError(f"next-largest envelope drift: 0x{next_entry:08X}/{next_size}")

    depths_report = {}
    for depth in sorted(set(depths.values())):
        positive = [entry for entry in boundary_entries if depths[entry] == depth]
        zero_at_depth = [entry for entry in zero_entries if depths[entry] == depth]
        depths_report[str(depth)] = {
            "positive_functions": len(positive), "positive_bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in positive),
            "zero_opaque_functions": len(zero_at_depth),
        }
    call_edges = [
        {"caller": f"0x{caller:08X}", "callee": f"0x{callee:08X}", "count": count}
        for caller in sorted(calls) for callee, count in sorted(calls[caller].items())
    ]
    mapping_sha = sha256(json.dumps({"typed": records, "zero": zero_records, "frontier": frontier_records, "shared": shared_records, "calls": call_edges, "table_stats": table_stats}, sort_keys=True, separators=(",", ":")).encode())
    source_rows = [row for row in records if row["source_identity_authenticated"]]
    unavailable_rows = [row for row in records if not row["source_identity_authenticated"]]
    return {
        "status": "opacity-wave8-font-sequence-and-freetype-closure-reconciled",
        "read_only": True, "hardware_operations": False, "production_routed": False,
        "wave7_residual": wave7_report["after"], "before": before,
        "selected_root_range": {"start": "0x005A8D06", "end_exclusive": "0x005A9628"},
        "actionable_graph": {"positive_functions": 28, "positive_bytes": 5370, "zero_opaque_functions": 1, "terminal_functions": 6, "call_edges": len(call_edges)},
        "closure_depths": depths_report, "range_partition": {"functions": 29, "interior_gap_bytes": range_gap_bytes},
        "source_attributed": {"functions": len(source_rows), "bytes": sum(row["envelope_bytes"] for row in source_rows), "provider": "FreeType 2.9.1", "license": "FTL", "production_codegen_exact": False},
        "typed_unavailable": {"positive_functions": len(unavailable_rows), "positive_bytes": sum(row["envelope_bytes"] for row in unavailable_rows), "zero_opaque_functions": 1},
        "shared_data": {"records": len(shared_records), "physical_bytes": sum(int(row["size"]) for row in shared_records), "additional_function_bytes": 0, "direct_dat_cells": 5, "table_pool": table_stats},
        "after": after, "largest_remaining": {"entry": f"0x{next_entry:08X}", "envelope_bytes": next_size},
        "records": records, "zero_records": zero_records, "frontier_records": frontier_records,
        "shared_records": shared_records, "call_edges": call_edges, "mapping_sha256": mapping_sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
