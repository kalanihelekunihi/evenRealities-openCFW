#!/usr/bin/env python3
"""Build a fail-closed stock G2 FreeType 2.9.1 autofit function map.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
GHIDRA = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
AUTOFIT = G2 / "third_party/freetype/src/autofit"
MANIFEST = G2 / "tools/manifests/g2-freetype-autofit-function-map.json"

LOAD_BASE = 0x00437FE0
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
GHIDRA_PIN = (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"
ENVELOPE = (0x005A6260, 0x005ABEF8)
CLASS_ADDRESS = 0x00752520
INTERFACE_ADDRESS = 0x00785380
WRITING_SYSTEM_TABLE = 0x0075E310

# Whole bodies recognized by the authenticated Ghidra corpus.  Identities
# follow the exact 2.9.1 single-object include/source order and are checked
# against writing-system, module, interface, and local call edges below.
GHIDRA_IDENTITIES = (
    (0x005A6260, "af_sort_pos", "afangles.c"),
    (0x005A62A2, "af_sort_and_quantize_widths", "afangles.c"),
    (0x005A63C8, "af_cjk_metrics_init_widths", "afcjk.c"),
    (0x005A65DE, "af_cjk_metrics_init_blues", "afcjk.c"),
    (0x005A6856, "af_cjk_metrics_check_digits", "afcjk.c"),
    (0x005A6A80, "af_cjk_hints_compute_segments", "afcjk.c"),
    (0x005A6AE8, "af_cjk_hints_link_segments", "afcjk.c"),
    (0x005A6D10, "af_cjk_hints_compute_edges", "afcjk.c"),
    (0x005A6FB2, "af_cjk_hints_detect_features", "afcjk.c"),
    (0x005A6FDC, "af_cjk_hints_compute_blue_edges", "afcjk.c"),
    (0x005A710A, "af_cjk_hints_init", "afcjk.c"),
    (0x005A719E, "af_cjk_snap_width", "afcjk.c"),
    (0x005A71EC, "af_cjk_compute_stem_width", "afcjk.c"),
    (0x005A731E, "af_cjk_align_linked_edge", "afcjk.c"),
    (0x005A733E, "af_cjk_align_serif_edge", "afcjk.c"),
    (0x005A734C, "af_hint_normal_stem", "afcjk.c"),
    (0x005A74AA, "af_cjk_hint_edges", "afcjk.c"),
    (0x005A77C4, "af_cjk_align_edge_points", "afcjk.c"),
    (0x005A7896, "af_cjk_hints_apply", "afcjk.c"),
    (0x005A798C, "af_dummy_hints_init", "afdummy.c"),
    (0x005A79CE, "af_face_globals_compute_style_coverage", "afglobal.c"),
    (0x005A7C2A, "af_face_globals_new", "afglobal.c"),
    (0x005A7CA4, "af_face_globals_free", "afglobal.c"),
    (0x005A7D02, "af_face_globals_get_metrics", "afglobal.c"),
    (0x005A7DC0, "af_face_globals_is_digit", "afglobal.c"),
    (0x005A7DCE, "af_axis_hints_new_segment", "afhints.c"),
    (0x005A7E86, "af_axis_hints_new_edge", "afhints.c"),
    (0x005A7FB4, "af_direction_compute", "afhints.c"),
    (0x005A7FFA, "af_glyph_hints_init", "afhints.c"),
    (0x005A8012, "af_glyph_hints_done", "afhints.c"),
    (0x005A80BA, "af_glyph_hints_rescale", "afhints.c"),
    (0x005A80C6, "af_glyph_hints_reload", "afhints.c"),
    (0x005A85BC, "af_glyph_hints_save", "afhints.c"),
    (0x005A8602, "af_glyph_hints_align_edge_points", "afhints.c"),
    (0x005A8672, "af_glyph_hints_align_strong_points", "afhints.c"),
    (0x005A87F0, "af_iup_shift", "afhints.c"),
    (0x005A8820, "af_iup_interp", "afhints.c"),
    (0x005A88B8, "af_glyph_hints_align_weak_points", "afhints.c"),
    (0x005A89BE, "af_glyph_hints_scale_dim", "afhints.c"),
    (0x005A8A78, "af_latin_metrics_init_widths", "aflatin.c"),
    (0x005A8C8A, "af_latin_sort_blue", "aflatin.c"),
    (0x005A8D06, "af_latin_metrics_init_blues", "aflatin.c"),
    (0x005A9628, "af_latin_metrics_check_digits", "aflatin.c"),
    (0x005A9700, "af_latin_metrics_scale_dim", "aflatin.c"),
    (0x005A99E8, "af_latin_hints_compute_segments", "aflatin.c"),
    (0x005A9F98, "af_latin_hints_link_segments", "aflatin.c"),
    (0x005AA0E2, "af_latin_hints_compute_edges", "aflatin.c"),
    (0x005AA3FC, "af_latin_hints_detect_features", "aflatin.c"),
    (0x005AA42E, "af_latin_hints_compute_blue_edges", "aflatin.c"),
    (0x005AA582, "af_latin_hints_init", "aflatin.c"),
    (0x005AA62E, "af_latin_snap_width", "aflatin.c"),
    (0x005AA67C, "af_latin_compute_stem_width", "aflatin.c"),
    (0x005AA80A, "af_latin_align_linked_edge", "aflatin.c"),
    (0x005AA832, "af_latin_align_serif_edge", "aflatin.c"),
    (0x005AA840, "af_latin_hint_edges", "aflatin.c"),
    (0x005AAE7C, "af_latin_hints_apply", "aflatin.c"),
    (0x005AAF8C, "af_loader_init", "afloader.c"),
    (0x005AAFA2, "af_loader_reset", "afloader.c"),
    (0x005AAFDE, "af_loader_embolden_glyph_in_slot", "afloader.c"),
    (0x005AB148, "af_loader_load_glyph", "afloader.c"),
    (0x005AB58E, "af_loader_compute_darkening", "afloader.c"),
    (0x005AB71E, "af_property_get_face_globals", "afmodule.c"),
    (0x005AB758, "af_property_set", "afmodule.c"),
    (0x005AB896, "af_property_get", "afmodule.c"),
    (0x005AB98C, "af_get_interface", "afmodule.c"),
    (0x005ABA26, "af_shaper_buf_create", "afshaper.c"),
    (0x005ABA34, "af_shaper_buf_destroy", "afshaper.c"),
    (0x005ABA40, "af_shaper_get_cluster", "afshaper.c"),
    (0x005ABAF8, "af_shaper_get_elem", "afshaper.c"),
    (0x005ABB1C, "af_warper_compute_line_best", "afwarp.c"),
    (0x005ABC64, "af_warper_compute", "afwarp.c"),
)

# Bodies missed or split by Ghidra.  Every interval has an exact callback
# pointer or is the sole source-ordered leaf between two independently
# authenticated bodies.
RECOVERED = (
    ("af_cjk_metrics_init", "afcjk.c", 0x005A68DE, 0x005A6A42, "62ca7c5cdd501940aab26dd2034a67522d9d1ad33faecbb19892544683bbe884"),
    ("af_cjk_metrics_scale", "afcjk.c", 0x005A6A42, 0x005A6A68, "8fd3f6c84ebcf2b63adecdd6011757ae880d013093013717cc27160a4aa71b42"),
    ("af_cjk_get_standard_widths", "afcjk.c", 0x005A6A68, 0x005A6A80, "9d0d67f313c212b7c29176b5f5725089d766c21f1719dc21e4ba97c1f73e568d"),
    ("af_dummy_hints_apply", "afdummy.c", 0x005A79AE, 0x005A79CE, "89d1ecf7ed1a946ab2d044b461e7074be5754410aa8e82c0f90d0b293ddadccc"),
    ("af_indic_metrics_init", "afindic.c", 0x005A8A04, 0x005A8A48, "4304f52f8d2f8f50539e41becbaefe5c0818abd56064a46d183fc9dd4c6cdddc"),
    ("af_indic_metrics_scale", "afindic.c", 0x005A8A48, 0x005A8A50, "99ee7648a72c18ce88e763b358b5e2054332321ded1a030c1b89cf06b1c87fbc"),
    ("af_indic_hints_init", "afindic.c", 0x005A8A50, 0x005A8A58, "2536609a94323369c81441f943c5eba06024d9bb94928fe443200562a3d885f1"),
    ("af_indic_hints_apply", "afindic.c", 0x005A8A58, 0x005A8A60, "c4e70fcf9cf7bfca52ac874b4784b8e4007e5f501013727b4f9c7cc14a09eef9"),
    ("af_indic_get_standard_widths", "afindic.c", 0x005A8A60, 0x005A8A78, "9d0d67f313c212b7c29176b5f5725089d766c21f1719dc21e4ba97c1f73e568d"),
    ("af_latin_metrics_init", "aflatin.c", 0x005A96B2, 0x005A9700, "8f3b1e313aa8c553631a04fa19bd3261096276ddb296aa8c7369a825df5aa543"),
    ("af_latin_metrics_scale", "aflatin.c", 0x005A99A8, 0x005A99D0, "e8e6769351538431615c4339550d019529def6c05500d08592f0c2b1a6ef6691"),
    ("af_latin_get_standard_widths", "aflatin.c", 0x005A99D0, 0x005A99E8, "16167dc618055872e284ee93788bf6a80651435a6ed6564bd2af6e9bb6e02626"),
    ("af_loader_done", "afloader.c", 0x005AAFD0, 0x005AAFDE, "85f70c6bbffd82fd0f7349d91ea89c0999bc2cd574ad7ac1cac34ce05b23ddba"),
    ("af_autofitter_init", "afmodule.c", 0x005AB996, 0x005AB9D4, "dc98b716ffdb7213cf0290cbb947048cf0d225e2d3f83f266aa0ec61abf92a41"),
    ("af_autofitter_done", "afmodule.c", 0x005AB9D4, 0x005AB9D6, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    ("af_autofitter_load_glyph", "afmodule.c", 0x005AB9D6, 0x005ABA26, "7d43b362e7c83003d4b6daa8227fac331234fbc452a27cc3be7d167f04764453"),
)

PHYSICAL = (
    (0x005A7FA4, 0x005A7FB4, "literal-constant-pool", "7473e27cd4187144d7100cb66af0b15cb7fc436b5a9129956db4b68a4e0bc5c9"),
    (0x005A9F92, 0x005A9F98, "literal-constant-pool", "ca5743c4af61d6f19b97ea785b82621387d8a5afbf38bc280af0fb76eb0d35c9"),
    (0x005AA3F4, 0x005AA3FC, "literal-constant-pool", "5bbb0c1302e2ee5d630b9fd3f71875337c7c2cf12fd941ed88c4ded6ef8d9ea3"),
    (0x005AB144, 0x005AB148, "literal-constant-pool", "2619291cce412ba9adda11ae95594c4025f7377d2fe0aa9ccc82b4f60b39a91d"),
    (0x005ABC2A, 0x005ABC64, "literal-constant-pool", "75966ba0c79cfa36f120d2332ad79adf025484b09e185b9c3f5a9e5a0a0c461d"),
)

HIGH_STARTS = {
    0x005A6260, 0x005A62A2, 0x005A68DE, 0x005A6A42, 0x005A6A68,
    0x005A710A, 0x005A7896, 0x005A798C, 0x005A79AE, 0x005A8A04,
    0x005A8A48, 0x005A8A50, 0x005A8A58, 0x005A8A60, 0x005A96B2,
    0x005A99A8, 0x005A99D0, 0x005AA582, 0x005AAE7C, 0x005AB98C,
    0x005AB996, 0x005AB9D4, 0x005AB9D6, 0x005ABA26, 0x005ABA34,
    0x005ABA40, 0x005ABAF8, 0x005ABB1C, 0x005ABC64,
}


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
    body = image[start - LOAD_BASE:end - LOAD_BASE]
    _require(len(body) == end - start, f"unavailable interval 0x{start:08X}")
    return body


def _words(image: bytes, address: int, count: int) -> tuple[int, ...]:
    return struct.unpack(f"<{count}I", _slice(image, address, address + count * 4))


def run_audit() -> dict[str, Any]:
    image = _pinned(IMAGE, IMAGE_PIN)
    ghidra_data = _pinned(GHIDRA, GHIDRA_PIN)
    sources = {path.name: path.read_text(encoding="utf-8") for path in AUTOFIT.glob("*.c")}
    include_order = [
        "afangles.c", "afblue.c", "afcjk.c", "afdummy.c", "afglobal.c",
        "afhints.c", "afindic.c", "aflatin.c", "aflatin2.c", "afloader.c",
        "afmodule.c", "afpic.c", "afranges.c", "afshaper.c", "afwarp.c",
    ]
    translation = sources["autofit.c"]
    positions = [translation.find(f'#include "{name}"') for name in include_order]
    _require(-1 not in positions and positions == sorted(positions), "autofit include order drift")

    module_words = _words(image, CLASS_ADDRESS, 9)
    _require(module_words == (4, 0x38, 0x0078A52C, 0x10000, 0x20000,
                              INTERFACE_ADDRESS, 0x005AB997, 0x005AB9D5,
                              0x005AB98D), "autofitter module class drift")
    _require(_slice(image, 0x0078A52C, 0x0078A537) == b"autofitter\0",
             "autofitter class name drift")
    _require(_words(image, INTERFACE_ADDRESS, 4) == (0, 0, 0, 0x005AB9D7),
             "autofitter interface drift")
    _require(_words(image, WRITING_SYSTEM_TABLE, 32) == (
        2, 0x38DC, 0x005A68DF, 0x005A6A43, 0, 0x005A6A69, 0x005A710B, 0x005A7897,
        0, 0x28, 0, 0, 0, 0, 0x005A798D, 0x005A79AF,
        3, 0x38DC, 0x005A8A05, 0x005A8A49, 0, 0x005A8A61, 0x005A8A51, 0x005A8A59,
        1, 0x488C, 0x005A96B3, 0x005A99A9, 0, 0x005A99D1, 0x005AA583, 0x005AAE7D,
    ), "autofit writing-system callback table drift")

    all_rows = {int(row["entry"], 16): row for row in map(json.loads, ghidra_data.splitlines())}
    rows = {start: row for start, row in all_rows.items() if ENVELOPE[0] <= start < ENVELOPE[1]}
    expected_starts = {start for start, _, _ in GHIDRA_IDENTITIES}
    _require(set(rows) == expected_starts, "autofit Ghidra entry set drift")
    _require((len(rows), sum(row["body_bytes"] for row in rows.values())) == (71, 22_746),
             "autofit Ghidra accounting drift")
    previous = all_rows.get(0x005A6170)
    _require(previous and int(previous["body_end_inclusive"], 16) + 1 == 0x005A6258,
             "autofit leading boundary drift")
    _require(_sha(_slice(image, ENVELOPE[1], ENVELOPE[1] + 18)) ==
             "9c4437493fc6c5bf38ae374498345c89cca4d24aeb44c033d698936354843f21",
             "autofit trailing boundary drift")
    _require((_words(image, 0x00748060, 1)[0] & ~1) == ENVELOPE[1],
             "separate post-autofit callable boundary drift")

    identity_by_start = {start: (symbol, module) for start, symbol, module in GHIDRA_IDENTITIES}
    intervals: list[tuple[int, int]] = []
    records = []
    for start, row in sorted(rows.items()):
        symbol, module = identity_by_start[start]
        _require(symbol in sources[module], f"source identity drift: {symbol}")
        end = int(row["body_end_inclusive"], 16) + 1
        intervals.append((start, end))
        confidence = "high" if start in HIGH_STARTS else "medium"
        records.append({
            "symbol": symbol, "module": module, "start": f"0x{start:08X}",
            "end_exclusive": f"0x{end:08X}", "bytes": end - start,
            "body_sha256": row["body_sha256"], "confidence": confidence,
            "mapping_origin": "pinned-ghidra-source-order-call-graph",
            "compiler_byte_identity_claimed": False,
        })
    recovered_starts = set()
    for symbol, module, start, end, digest in RECOVERED:
        _require(symbol in sources[module], f"recovered source identity drift: {symbol}")
        _require(_sha(_slice(image, start, end)) == digest, f"recovered body drift: {symbol}")
        recovered_starts.add(start)
        intervals.append((start, end))
        confidence = "high" if start in HIGH_STARTS else "medium"
        records.append({
            "symbol": symbol, "module": module, "start": f"0x{start:08X}",
            "end_exclusive": f"0x{end:08X}", "bytes": end - start,
            "body_sha256": digest, "confidence": confidence,
            "mapping_origin": "recovered-callback-or-source-ordered-leaf",
            "compiler_byte_identity_claimed": False,
        })
    _require(HIGH_STARTS <= (set(rows) | recovered_starts), "high-confidence row missing")

    physical_records = []
    for start, end, category, digest in PHYSICAL:
        _require(_sha(_slice(image, start, end)) == digest, "autofit physical residue drift")
        intervals.append((start, end))
        physical_records.append({
            "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
            "bytes": end - start, "category": category, "sha256": digest,
            "callable": False,
        })
    cursor = ENVELOPE[0]
    for start, end in sorted(intervals):
        _require(start == cursor, f"unmapped/overlapping autofit byte at 0x{cursor:08X}")
        cursor = end
    _require(cursor == ENVELOPE[1], "autofit physical envelope incomplete")

    records.sort(key=lambda row: row["start"])
    high = [row for row in records if row["confidence"] == "high"]
    medium = [row for row in records if row["confidence"] == "medium"]
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-autofit-callable-physical-closure",
        "analysis_mode": "read-only; no hardware or flash operation",
        "image": {"bytes": IMAGE_PIN[0], "sha256": IMAGE_PIN[1],
                  "run_address_rule": "run = file_offset + 0x00437FE0"},
        "upstream": {"version": "2.9.1", "tag": "VER-2-9-1",
                     "commit": UPSTREAM_COMMIT, "license": "FTL"},
        "scope": {
            "module": "autofit", "envelope_start": f"0x{ENVELOPE[0]:08X}",
            "envelope_end_exclusive": f"0x{ENVELOPE[1]:08X}",
            "physical_bytes": ENVELOPE[1] - ENVELOPE[0],
            "callable_bytes": sum(row["bytes"] for row in records),
            "residual_physical": {"intervals": len(physical_records), "bytes": 92,
                                  "category_bytes": {"literal-constant-pool": 92},
                                  "unclassified_bytes": 0, "unresolved_callable_bytes": 0},
        },
        "authenticated_tables": {
            "module_class": f"0x{CLASS_ADDRESS:08X}",
            "autohinter_interface": f"0x{INTERFACE_ADDRESS:08X}",
            "writing_system_classes": f"0x{WRITING_SYSTEM_TABLE:08X}",
            "writing_systems": ["cjk", "dummy", "indic", "latin"],
        },
        "confidence": {
            "high": {"functions": len(high), "bytes": sum(row["bytes"] for row in high)},
            "medium": {"functions": len(medium), "bytes": sum(row["bytes"] for row in medium)},
            "mapped_total": {"functions": len(records), "bytes": sum(row["bytes"] for row in records)},
            "unresolved_code": {"functions": 0, "bytes": 0, "source_identities_complete": True},
        },
        "functions": records,
        "physical_residue": physical_records,
        "evidence_bounds": {
            "compiler_byte_identity_claimed": False,
            "production_routing_claimed": False,
            "authenticated_target_placement": False,
            "hardware_validation_performed": False,
        },
    }
    result["mapping_sha256"] = _canonical({
        "envelope": [*ENVELOPE], "functions": records,
        "physical_residue": physical_records,
        "tables": result["authenticated_tables"],
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
