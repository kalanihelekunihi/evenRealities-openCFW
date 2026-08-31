#!/usr/bin/env python3
"""Build a fail-closed stock G2 FreeType 2.9.1 smooth-renderer map.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
GHIDRA = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
SMOOTH = G2 / "third_party/freetype/src/smooth"
MANIFEST = G2 / "tools/manifests/g2-freetype-smooth-function-map.json"

LOAD_BASE = 0x00437FE0
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
GHIDRA_PIN = (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"

ENVELOPE = (0x005E1594, 0x005E267C)
OUTLINE_TABLE = 0x0077BEE4
RASTER_TABLE = 0x0077BEFC
RENDERER_CLASSES = (
    (0x00718D9C, 0x0078E6BC, b"smooth\0", 0x005E2649, "FT_RENDER_MODE_NORMAL"),
    (0x00718DD8, 0x0078C134, b"smooth-lcd\0", 0x005E2661, "FT_RENDER_MODE_LCD"),
    (0x00718E14, 0x0078C140, b"smooth-lcdv\0", 0x005E266F, "FT_RENDER_MODE_LCD_V"),
)

SOURCE_PINS = {
    "ftgrays.c": (62_239, "bb6433650bf92eb793b80f61acb30c4e9bb92511ddd5ab0f549e955d40af1b66"),
    "ftsmooth.c": (13_467, "ee55810abdce02f0a26353bdb9300915a37b094ec3c72b36992432f79e8c2014"),
    "smooth.c": (1_385, "41af657ea23f99e693dfa8973b759e738b77107d190b17677f4977fd90debcf5"),
}

# Ghidra-recognized whole bodies, assigned by exact 2.9.1 source order and
# corroborated by the raster/outline callback graph.
GHIDRA_IDENTITIES = {
    0x005E1594: ("gray_record_cell", "ftgrays.c", 0x005E1618),
    0x005E1618: ("gray_set_cell", "ftgrays.c", 0x005E1686),
    0x005E1686: ("gray_render_scanline", "ftgrays.c", 0x005E17C2),
    0x005E17C2: ("gray_render_line", "ftgrays.c", 0x005E19EA),
    0x005E19EA: ("gray_split_conic", "ftgrays.c", 0x005E1A3C),
    0x005E1A3C: ("gray_render_conic", "ftgrays.c", 0x005E1B4C),
    0x005E1B4C: ("gray_split_cubic", "ftgrays.c", 0x005E1BDE),
    0x005E1BDE: ("gray_render_cubic", "ftgrays.c", 0x005E1D6C),
    0x005E1DCE: ("gray_hline", "ftgrays.c", 0x005E1E7E),
    0x005E1E7E: ("gray_sweep", "ftgrays.c", 0x005E1F0A),
    0x005E1F0A: ("gray_convert_glyph_inner", "ftgrays.c", 0x005E1F44),
    0x005E1F44: ("gray_convert_glyph", "ftgrays.c", 0x005E2052),
    0x005E2052: ("gray_raster_render", "ftgrays.c", 0x005E2224),
    0x005E2224: ("gray_raster_new", "ftgrays.c", 0x005E2248),
    0x005E2248: ("gray_raster_done", "ftgrays.c", 0x005E2256),
    0x005E22E0: ("ft_smooth_render_generic", "ftsmooth.c", 0x005E2636),
}

# Complete callable bodies omitted by Ghidra's callable relation.
RECOVERED = (
    ("gray_move_to", "ftgrays.c", 0x005E1D6C, 0x005E1D92,
     "be5fe175c4204599d7f37373e4961728922449d24d9e23b7d4dc964c7ac7dcbc"),
    ("gray_line_to", "ftgrays.c", 0x005E1D92, 0x005E1DA8,
     "2a6014fa1924c7143cafa352c92d5f345fada73bb1ce90a042c78f38f14a901a"),
    ("gray_conic_to", "ftgrays.c", 0x005E1DA8, 0x005E1DBA,
     "1a73db8cbbb643c506722c8dccde8995ffec4e0211f885ac72a435632c19e9b0"),
    ("gray_cubic_to", "ftgrays.c", 0x005E1DBA, 0x005E1DCE,
     "4297787dee2d1c34a446980e83bbfdef8e83225126fb5e84e4e9e443f497ddf6"),
    ("gray_raster_reset", "ftgrays.c", 0x005E2256, 0x005E2258,
     "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    ("gray_raster_set_mode", "ftgrays.c", 0x005E2258, 0x005E225C,
     "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4"),
    ("ft_smooth_init", "ftsmooth.c", 0x005E225C, 0x005E2272,
     "831280637b9af853c4beda26040230f61a91f680bfce7a5b010f98b42ca557f9"),
    ("ft_smooth_set_mode", "ftsmooth.c", 0x005E2272, 0x005E2282,
     "f976f9f41815bb7f0ecd1e9a7952494b7afa57be5aa5aebb61f6d1462f7a2056"),
    ("ft_smooth_transform", "ftsmooth.c", 0x005E2282, 0x005E22B8,
     "03640375dfa2f510cff48ab3b5fe0c647bbe895332a683b1c2697035858f952c"),
    ("ft_smooth_get_cbox", "ftsmooth.c", 0x005E22B8, 0x005E22E0,
     "ba6342e15a272906ae87d4281da75bc49523f5f514439258020a855910ebcdec"),
    ("ft_smooth_render", "ftsmooth.c", 0x005E2648, 0x005E2660,
     "92b9d5b71761a49a974bcf6716d7a1982b0cb06f27b5087f19e704741127a97a"),
    ("ft_smooth_render_lcd", "ftsmooth.c", 0x005E2660, 0x005E266E,
     "e1820a351913746cd1815e8b912ecb02ed47e3a24b80bb212717ac04e555169f"),
    ("ft_smooth_render_lcd_v", "ftsmooth.c", 0x005E266E, 0x005E267C,
     "de247243e60840b1df805a0b2cf5f1f5d153e5afff759945b05c494a5b2eb66a"),
)

PHYSICAL = (
    (0x005E2636, 0x005E2638, "alignment-padding",
     "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
    (0x005E2638, 0x005E2648, "literal-constant-pool",
     "3a50ee46dc8cc511147a21734345b66668780791e2b06d86bc6ec9f955495043"),
)


class MapError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MapError(message)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    _require((len(data), _sha(data)) == pin, f"pin drift: {path}")
    return data


def _slice(image: bytes, start: int, end: int) -> bytes:
    _require(LOAD_BASE <= start < end, "invalid image interval")
    body = image[start - LOAD_BASE:end - LOAD_BASE]
    _require(len(body) == end - start,
             f"image interval unavailable: 0x{start:08X}-0x{end:08X}")
    return body


def _words(image: bytes, address: int, count: int) -> tuple[int, ...]:
    return struct.unpack(f"<{count}I", _slice(image, address, address + count * 4))


def _complement(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    cursor = ENVELOPE[0]
    output = []
    for start, end in sorted(intervals):
        _require(ENVELOPE[0] <= start < end <= ENVELOPE[1],
                 "mapped interval escaped smooth envelope")
        _require(start >= cursor, "mapped smooth intervals overlap")
        if start > cursor:
            output.append((cursor, start))
        cursor = end
    if cursor < ENVELOPE[1]:
        output.append((cursor, ENVELOPE[1]))
    return output


def _record(
    image: bytes, symbol: str, module: str, start: int, end: int,
    confidence: str, evidence: list[str], origin: str,
) -> dict[str, Any]:
    body = _slice(image, start, end)
    return {
        "symbol": symbol, "module": module,
        "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
        "bytes": len(body), "body_sha256": _sha(body),
        "confidence": confidence, "evidence": evidence,
        "mapping_origin": origin, "compiler_byte_identity_claimed": False,
    }


def run_audit() -> dict[str, Any]:
    image = _pinned(IMAGE, IMAGE_PIN)
    ghidra_data = _pinned(GHIDRA, GHIDRA_PIN)
    sources = {
        name: _pinned(SMOOTH / name, pin).decode("utf-8")
        for name, pin in SOURCE_PINS.items()
    }
    include_positions = [
        sources["smooth.c"].find(f'#include "{name}"')
        for name in ("ftgrays.c", "ftsmooth.c", "ftspic.c")
    ]
    _require(-1 not in include_positions and include_positions == sorted(include_positions),
             "smooth single-object include order drift")

    outline_words = _words(image, OUTLINE_TABLE, 6)
    raster_words = _words(image, RASTER_TABLE, 6)
    _require(outline_words == (
        0x005E1D6D, 0x005E1D93, 0x005E1DA9, 0x005E1DBB, 0, 0,
    ), "stock smooth outline callback table drift")
    _require(raster_words == (
        0x6F75746C, 0x005E2225, 0x005E2257, 0x005E2259,
        0x005E2053, 0x005E2249,
    ), "stock smooth raster callback table drift")

    pointer_references: dict[int, list[str]] = {}
    for slot, pointer in enumerate(outline_words[:4]):
        pointer_references.setdefault(pointer & ~1, []).append(
            f"0x{OUTLINE_TABLE + slot * 4:08X}"
        )
    for slot, pointer in enumerate(raster_words[1:], 1):
        pointer_references.setdefault(pointer & ~1, []).append(
            f"0x{RASTER_TABLE + slot * 4:08X}"
        )

    class_records = []
    distinct_renderers = set()
    for address, name_address, name, render_pointer, required_mode in RENDERER_CLASSES:
        words = _words(image, address, 15)
        expected = (
            2, 64, name_address, 0x00010000, 0x00020000, 0,
            0x005E225D, 0, 0, 0x6F75746C, render_pointer,
            0x005E2283, 0x005E22B9, 0x005E2273, RASTER_TABLE,
        )
        _require(words == expected, f"smooth renderer class drift: 0x{address:08X}")
        _require(_slice(image, name_address, name_address + len(name)) == name,
                 f"smooth renderer name drift: 0x{name_address:08X}")
        for slot in (6, 10, 11, 12, 13):
            pointer = words[slot]
            pointer_references.setdefault(pointer & ~1, []).append(
                f"0x{address + slot * 4:08X}"
            )
        distinct_renderers.add(render_pointer & ~1)
        class_records.append({
            "class_address": f"0x{address:08X}",
            "name": name[:-1].decode("ascii"),
            "render_callback": f"0x{render_pointer & ~1:08X}",
            "required_mode": required_mode,
            "raster_table": f"0x{RASTER_TABLE:08X}",
        })
    _require(distinct_renderers == {0x005E2648, 0x005E2660, 0x005E266E},
             "smooth renderer modes collapsed")

    all_ghidra: dict[int, dict[str, Any]] = {}
    for line in ghidra_data.splitlines():
        row = json.loads(line)
        start = int(row["entry"], 16)
        all_ghidra[start] = row
    ghidra = {
        start: row for start, row in all_ghidra.items()
        if ENVELOPE[0] <= start < ENVELOPE[1]
    }
    _require(set(ghidra) == set(GHIDRA_IDENTITIES),
             "smooth Ghidra entry set drift")
    _require((len(ghidra), sum(row["body_bytes"] for row in ghidra.values())) ==
             (16, 4_022), "smooth Ghidra accounting drift")
    previous = all_ghidra.get(0x005E14A4)
    following = all_ghidra.get(ENVELOPE[1])
    _require(previous is not None and
             int(previous["body_end_inclusive"], 16) + 1 == ENVELOPE[0] and
             previous["body_sha256"] ==
             "87154e8768f18c278c79dd8bc66f636e3f036b2daccf8a053b465b811690b845",
             "authenticated SFNT/smooth boundary drift")
    _require(following is not None and following["body_bytes"] == 132 and
             following["body_sha256"] ==
             "c664ecc4306b9b6e8b2f1075d0428912ee815e20c5b76aae54a9fbc601279560",
             "authenticated smooth/Cordio boundary drift")

    identities: dict[int, tuple[str, str, int, str]] = {
        start: (symbol, module, end, "pinned-ghidra-source-order")
        for start, (symbol, module, end) in GHIDRA_IDENTITIES.items()
    }
    for symbol, module, start, end, digest in RECOVERED:
        _require(start not in identities, f"duplicate smooth entry: {symbol}")
        _require(_sha(_slice(image, start, end)) == digest,
                 f"recovered smooth body drift: {symbol}")
        identities[start] = (symbol, module, end, "recovered-complete-body")

    expected_source_order = {
        "ftgrays.c": [
            "gray_record_cell", "gray_set_cell", "gray_render_scanline",
            "gray_render_line", "gray_split_conic", "gray_render_conic",
            "gray_split_cubic", "gray_render_cubic", "gray_move_to",
            "gray_line_to", "gray_conic_to", "gray_cubic_to", "gray_hline",
            "gray_sweep", "gray_convert_glyph_inner", "gray_convert_glyph",
            "gray_raster_render", "gray_raster_new", "gray_raster_done",
            "gray_raster_reset", "gray_raster_set_mode",
        ],
        "ftsmooth.c": [
            "ft_smooth_init", "ft_smooth_set_mode", "ft_smooth_transform",
            "ft_smooth_get_cbox", "ft_smooth_render_generic", "ft_smooth_render",
            "ft_smooth_render_lcd", "ft_smooth_render_lcd_v",
        ],
    }
    for module, symbols in expected_source_order.items():
        mapped = [
            identities[start][0] for start in sorted(identities)
            if identities[start][1] == module
        ]
        _require(mapped == symbols, f"smooth mapped source order drift: {module}")
        for symbol in symbols:
            _require(re.search(rf"\b{re.escape(symbol)}\s*\(", sources[module]),
                     f"smooth source definition missing: {module}:{symbol}")

    # Preserve the three wrapper semantics in both source and stock bytes.
    mode_tokens = {
        "ft_smooth_render": "FT_RENDER_MODE_NORMAL",
        "ft_smooth_render_lcd": "FT_RENDER_MODE_LCD",
        "ft_smooth_render_lcd_v": "FT_RENDER_MODE_LCD_V",
    }
    for symbol, token in mode_tokens.items():
        match = re.search(
            rf"{symbol}\s*\([^{{]+\)\s*\{{(?P<body>.*?)\n  \}}",
            sources["ftsmooth.c"], re.DOTALL,
        )
        _require(match is not None and token in match.group("body"),
                 f"smooth render-mode source drift: {symbol}")

    records = []
    for start in sorted(identities):
        symbol, module, end, origin = identities[start]
        if start in ghidra:
            row = ghidra[start]
            _require(int(row["body_end_inclusive"], 16) + 1 == end,
                     f"smooth Ghidra boundary drift: {symbol}")
            _require(row["body_bytes"] == end - start and
                     row["body_sha256"] == _sha(_slice(image, start, end)),
                     f"smooth Ghidra body drift: {symbol}")
            evidence = [
                origin, "pinned-ghidra-whole-body",
                "exact-freetype-2.9.1-definition", "single-object-source-order",
                "raster-render-call-graph",
            ]
        else:
            evidence = [
                origin, "complete-thumb-body-boundary", "whole-body-sha256",
                "exact-freetype-2.9.1-definition", "single-object-source-order",
            ]
        confidence = "high" if start in pointer_references else "medium"
        if confidence == "high":
            evidence.append("stock-renderer-outline-or-raster-table-pointer")
        record = _record(image, symbol, module, start, end, confidence, evidence, origin)
        if start in pointer_references:
            record["pointer_references"] = pointer_references[start]
            record["thumb_pointer"] = f"0x{start | 1:08X}"
        records.append(record)
    _require((len(records), sum(row["bytes"] for row in records)) == (29, 4_310),
             "smooth callable accounting drift")

    physical = []
    for start, end, category, digest in PHYSICAL:
        body = _slice(image, start, end)
        _require(_sha(body) == digest, "smooth physical classification drift")
        physical.append({
            "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
            "bytes": len(body), "body_sha256": digest, "category": category,
            "callable_code": False, "source_identity_claimed": False,
        })
    _require(_words(image, 0x005E2638, 4) ==
             (OUTLINE_TABLE, 0x01000001, 0xFFFF8000, 0x62697473),
             "smooth generic-render literal pool drift")
    intervals = [
        (int(row["start"], 16), int(row["end_exclusive"], 16))
        for row in records + physical
    ]
    _require(_complement(intervals) == [],
             "smooth envelope retains unclassified physical bytes")

    high = [row for row in records if row["confidence"] == "high"]
    medium = [row for row in records if row["confidence"] == "medium"]
    high_total = {"functions": len(high), "bytes": sum(row["bytes"] for row in high)}
    medium_total = {"functions": len(medium), "bytes": sum(row["bytes"] for row in medium)}
    _require(high_total == {"functions": 16, "bytes": 804},
             "smooth high-confidence accounting drift")
    _require(medium_total == {"functions": 13, "bytes": 3_506},
             "smooth medium-confidence accounting drift")
    mapping_sha = _canonical(records + physical + class_records)

    return {
        "schema_version": 1, "status": "fail-closed-smooth-function-map",
        "read_only": True, "selected_module": "smooth-renderer-family",
        "hardware_operations": False,
        "anchors": {
            "image": {
                "path": str(IMAGE.relative_to(G2)), "bytes": IMAGE_PIN[0],
                "sha256": IMAGE_PIN[1], "load_base": f"0x{LOAD_BASE:08X}",
            },
            "ghidra": {
                "path": str(GHIDRA.relative_to(G2)), "bytes": GHIDRA_PIN[0],
                "sha256": GHIDRA_PIN[1],
            },
            "outline_callback_table": f"0x{OUTLINE_TABLE:08X}",
            "raster_callback_table": f"0x{RASTER_TABLE:08X}",
            "previous_provider_end": "sfnt@0x005E1594",
            "next_provider_start": "cordio-smp-sc-act@0x005E267C",
            "freetype_version": "2.9.1", "freetype_commit": UPSTREAM_COMMIT,
        },
        "renderer_classes": class_records,
        "scope": {
            "start": f"0x{ENVELOPE[0]:08X}",
            "end_exclusive": f"0x{ENVELOPE[1]:08X}",
            "bytes": ENVELOPE[1] - ENVELOPE[0],
            "ghidra_recognized": {"functions": 16, "bytes": 4_022},
            "recovered_callable": {"functions": 13, "bytes": 288},
            "residual_physical": {
                "intervals": 2, "bytes": 18,
                "category_bytes": {"alignment-padding": 2, "literal-constant-pool": 16},
                "unclassified_bytes": 0, "unresolved_callable_bytes": 0,
            },
        },
        "confidence": {
            "exact": {"functions": 0, "bytes": 0,
                      "reason": "no original-compiler byte identity proof"},
            "high": high_total, "medium": medium_total,
            "mapped_total": {"functions": 29, "bytes": 4_310},
            "unresolved_code": {
                "functions": 0, "bytes": 0, "source_identities_complete": True,
            },
        },
        "movement": {
            "initial_retained_census": {"functions": 0, "bytes": 0},
            "authenticated_complete_map": {"functions": 29, "bytes": 4_310},
            "newly_classified_physical": {"intervals": 2, "bytes": 18},
        },
        "mapping_sha256": mapping_sha,
        "records": {"smooth": records, "physical_classification": physical},
        "compiler_byte_identity_claimed": False, "binary_overlay_ready": False,
        "production_routed": False,
        "blockers": [
            "original compiler/version/options, ABI details, and LTO state are not recovered",
            "no authenticated stock callsite rewrite or target placement routes this source",
            "no authenticated font payload or face-path configuration was supplied",
            "task stack and worst-case execution time are not qualified",
            "no authorized physical G2 hardware rendering execution was performed",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    report = run_audit()
    if args.write_manifest:
        MANIFEST.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    if args.check_manifest:
        _require(MANIFEST.is_file(), f"manifest missing: {MANIFEST}")
        _require(json.loads(MANIFEST.read_text(encoding="utf-8")) == report,
                 "checked-in smooth function-map manifest drift")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
