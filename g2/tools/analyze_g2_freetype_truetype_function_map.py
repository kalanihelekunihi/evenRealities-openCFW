#!/usr/bin/env python3
"""Close the complete stock G2 FreeType 2.9.1 TrueType physical map.

This promotes the existing reachable-driver source candidate into a distinct
whole-envelope map.  It does not change the existing candidate or claim
compiler-byte identity, placement, or hardware behavior.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
GHIDRA = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
SNAPSHOT = G2 / "third_party/freetype"
TRUETYPE = SNAPSHOT / "src/truetype"
CANDIDATE_ANALYZER = G2 / "research/candidates/freetype/analyze_truetype_candidate.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-truetype-function-map.json"

LOAD_BASE = 0x00437FE0
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
GHIDRA_PIN = (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
CANDIDATE_PIN = (43_758, "459556e042afcb10a5dc9d445e44a3be2c8923f07588d437b13eaf45ba70ed53")
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"
ENVELOPE = (0x005EF0B0, 0x005F958C)

# Whole bodies present in the Ghidra corpus but intentionally outside the
# earlier 248-function reachable-driver candidate.
GHIDRA_ADDITIONS = (
    ("TT_Access_Glyph_Frame", "ttgload.c", 0x005EF4F8, 0x005EF532,
     "188671bb014c3247fd449e9a7ba1f6739369fe33ac14372c327aea6b9f10fa8a"),
    ("TT_Forget_Glyph_Frame", "ttgload.c", 0x005EF532, 0x005EF53C,
     "574d5d3387258a4d13210f31f43aafc22c98a02d6b45eb1b737b4cc9863fb493"),
    ("TT_Load_Simple_Glyph", "ttgload.c", 0x005EF5B0, 0x005EF8D6,
     "30597b7be95b9a2d4c87f73bdfa344fa765a9ee5cb5ef9d439fc32890b19b4b8"),
    ("TT_Load_Composite_Glyph", "ttgload.c", 0x005EF8D6, 0x005EFAD0,
     "afbb537ca7e65a5f48d83837a45b922f81dd0267b66bd741319a0acb40dc6290"),
    ("ft_var_load_delta_set_index_mapping", "ttgxvar.c", 0x005F1908, 0x005F1A32,
     "f6cef355c9241b566ab8ea20ecf774acf48542ea3ce57bd44a631fd3d6732f18"),
    ("ft_var_load_hvvar", "ttgxvar.c", 0x005F1A32, 0x005F1BA0,
     "65e7114f30f306fa5dcc4dfab7c5ff5a4b4a405e2670c8b0fdb95a97fc1b023f"),
    ("tt_hvadvance_adjust", "ttgxvar.c", 0x005F1D02, 0x005F1DD0,
     "454adfd020e75339fc3a1dfc6f4334fb53117abfc96c6e55fb905af3f1aea9d1"),
    ("tt_size_reset_iterator", "ttgxvar.c", 0x005F2250, 0x005F225E,
     "4d232836d7b7c61eb5217aba6c56b54a919996e7a7265048ede781976daeb77b"),
    ("tt_get_var_blend", "ttgxvar.c", 0x005F3FF0, 0x005F404E,
     "75f3d6f8aaff54433f9f8bbd64ac333a557e4913e5093c15eddd2f8bbcf85bb3"),
)

# Ghidra-missed complete bodies.  Boundaries are independently fixed by
# service/callback pointer slots or by the sole source-ordered leaf between
# two whole bodies.
RECOVERED = (
    ("tt_property_set", "ttdriver.c", 0x005EF0B0, 0x005EF0DE,
     "80331dce3cdff8477c6e80b5b31961f624f3e02c2515ef56d54dced3cdb599ff"),
    ("tt_property_get", "ttdriver.c", 0x005EF0DE, 0x005EF100,
     "1a1f3061e55b3389bbb8f65e240869327471c1dab1102cf6ab057d139fed4f1e"),
    ("TT_Load_Glyph_Header", "ttgload.c", 0x005EF53C, 0x005EF5B0,
     "79a1e6bd585b7f11eb15a704874da002d270d2a6485ff8fe0a8769d4c7c0933d"),
    ("tt_hadvance_adjust", "ttgxvar.c", 0x005F1DD0, 0x005F1DDA,
     "f635e62965138ae4d61d6b9f923e10aa860ad19b57c2f68d0791c4591cf565f3"),
    ("tt_vadvance_adjust", "ttgxvar.c", 0x005F1DDA, 0x005F1DE4,
     "26cc4298368be36515f518a291e71a934a49089a54c4679cfb07bd2f2e5432f2"),
    ("TT_Set_MM_Blend", "ttgxvar.c", 0x005F2FE4, 0x005F3012,
     "b94ec5c08863e5d0f01f9b0aaecde7a96bf2412764a93bc3de4a0eab3c053658"),
    ("TT_Get_MM_Blend", "ttgxvar.c", 0x005F3012, 0x005F309E,
     "6594cef5f77ededc7d11192c5ce47710cb8c0091ad8082bbd3fda8f5ff8bdef7"),
    ("TT_Get_Var_Design", "ttgxvar.c", 0x005F3240, 0x005F32CC,
     "e15e819d8e45447833b7daa53a6f3bf88af61a7896b465ea29ce683a9a4b9346"),
)

PHYSICAL = (
    (0x005EFAFA, 0x005EFB04, "literal-pointer-data-pool", "ab0cf96a0530dac980878502aade1af6d83b24317ff162364c50e8c3341d7d52"),
    (0x005EFF30, 0x005EFF4C, "literal-pointer-data-pool", "9edfdeb2a84577460b6b656373b4b99920f75e627e1228555a4db39f837b5df3"),
    (0x005F0B22, 0x005F0B28, "literal-pointer-data-pool", "bec0b850f2b4fdd32b68f56dab3bbcd13f1ef527c113690eddef7f0fe53842bd"),
    (0x005F0FAC, 0x005F0FB4, "literal-pointer-data-pool", "1f87d127c567e5fd131aa0577454a8b784bd1633d4fb4f184104b00ff7bcad4f"),
    (0x005F1556, 0x005F1564, "literal-pointer-data-pool", "a597c9a1874b2853d404753ad834270f9507c25b333808ba8c9145e687e2c695"),
    (0x005F1BA0, 0x005F1BAC, "literal-pointer-data-pool", "05e75451e76dd0a7f92465d58c7c01a54c3ce90ec8fa34014f40ebf243cfe1e0"),
    (0x005F2092, 0x005F2098, "literal-pointer-data-pool", "bc6e7a953fc9cb475a3c90a8876685be6be3f11ffa2deddb3d1b96e643196f22"),
    (0x005F2524, 0x005F2560, "literal-pointer-data-pool", "9b06355a9c7561c2779cceb76e0368048cdf984c148a9bea4661fc59bb5825a4"),
    (0x005F2D8E, 0x005F2D94, "literal-pointer-data-pool", "dd81083188045eb9f8f5f7362a2a4823a5cb1fed6953f358a73812fb735e45c4"),
    (0x005F2FD8, 0x005F2FE4, "literal-pointer-data-pool", "d7e46ae17c98727c1c2fa9a62c8d023b38d749b199ee7c7ed97088a76da56f2b"),
    (0x005F3234, 0x005F3240, "literal-pointer-data-pool", "80d6b74f3546e4706ae0d56e998371667de64acc36fe31958d845cdbea6fcbf4"),
    (0x005F3716, 0x005F3748, "literal-pointer-data-pool", "b0128356818e0d8419ee1ede3fcfd2661342457a6c8b567d1b4b8149190f5ae2"),
    (0x005F52FE, 0x005F5338, "literal-pointer-data-pool", "4ffd66a58f5e92c67aaf908c9d5b796a3d8e5e3ff3e2a87b5345b7aa013d9b9f"),
    (0x005F5AE2, 0x005F5AEC, "literal-pointer-data-pool", "81557e31848846328ed6715afc34562e29272115e1e1cba46f4ec4af204e85ad"),
    (0x005F5AFA, 0x005F5B00, "literal-pointer-data-pool", "d73d18cdff5e1e2bf989458c00cd0ac82c0c3283ef8f4d2cfde97a74be8724ba"),
    (0x005F5B0E, 0x005F5B14, "literal-pointer-data-pool", "c005e81fd312f79bbc74891ddd725fd2da448012f6a7acc76816652899132bdc"),
    (0x005F5B7A, 0x005F5BA0, "literal-pointer-data-pool", "6ba78cd03d41d16251b8dfd7bfc7cfa63e8abb1cf86ef55848bcd671aff5d9c0"),
    (0x005F8544, 0x005F8568, "literal-pointer-data-pool", "b573bd2cd988c6b23267bd1177e9f924935353f61b7eb55f7805aeee4670a927"),
    (0x005F8766, 0x005F876C, "literal-pointer-data-pool", "1315fa5544573bb1c106d38bdca4a974e4a47768f50bc23b07f790df9645d92c"),
    (0x005F8F04, 0x005F8F08, "literal-pointer-data-pool", "f78a6210c76716dc97250dea11e231ef99592d121e51c58333cbb98d9b024b5f"),
    (0x005F9194, 0x005F919C, "literal-pointer-data-pool", "c59f56b3797941d055b117552722c7caeb50cd17e8ddaf5cd52d3dc2dd0ce115"),
    (0x005F9352, 0x005F935C, "literal-pointer-data-pool", "7579d32741a804a8a96dd464fa266f1c4f1712e09fdecb1d781e10f7a7c79fa0"),
    (0x005F93A0, 0x005F93A4, "literal-pointer-data-pool", "98df1ac03276802313c18db41d90244e91cacc8017cb9a4a97804474d99a84b9"),
    (0x005F94EC, 0x005F952C, "literal-pointer-data-pool", "daaa1ed638db16a18313c58a07c8a8257013cba47b7c044255296e5c9ed102c2"),
    (0x005F958A, 0x005F958C, "alignment-padding", "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
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
    body = image[start - LOAD_BASE:end - LOAD_BASE]
    _require(len(body) == end - start, f"unavailable interval: 0x{start:08X}")
    return body


def _words(image: bytes, address: int, count: int) -> tuple[int, ...]:
    return struct.unpack(f"<{count}I", _slice(image, address, address + count * 4))


def _load_candidate():
    _pinned(CANDIDATE_ANALYZER, CANDIDATE_PIN)
    spec = importlib.util.spec_from_file_location("open_cfw_truetype_graph_candidate", CANDIDATE_ANALYZER)
    _require(spec is not None and spec.loader is not None, "TrueType candidate unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_audit() -> dict[str, Any]:
    image = _pinned(IMAGE, IMAGE_PIN)
    ghidra_data = _pinned(GHIDRA, GHIDRA_PIN)
    candidate = _load_candidate().analyze()
    _require(candidate["admitted_driver_graph"] == {"functions": 248, "bytes": 38_828},
             "existing TrueType candidate graph drift")
    _require(candidate["private_frontier"] == [] and
             candidate["interpreter_dispatch"]["unresolved_dispatch_targets"] == [],
             "existing candidate dispatch frontier reopened")

    sources = {path.name: path.read_text(encoding="utf-8") for path in TRUETYPE.glob("*.c")}
    translation = sources["truetype.c"]
    include_order = ("ttdriver.c", "ttgload.c", "ttgxvar.c", "ttinterp.c",
                     "ttobjs.c", "ttpic.c", "ttpload.c", "ttsubpix.c")
    positions = [translation.find(f'#include "{name}"') for name in include_order]
    _require(-1 not in positions and positions == sorted(positions), "TrueType include order drift")

    _require(_words(image, 0x0078ECB4, 2) == (0x005EF0B1, 0x005EF0DF),
             "TrueType property service table drift")
    _require(_words(image, 0x007505A8, 9) == (
        0, 0x005F2FE5, 0x005F3013, 0x005F289F, 0x005F309F,
        0x005F3241, 0x005F32CD, 0x005F3FF1, 0x005F40D7,
    ), "TrueType multi-masters service table drift")
    _require(_words(image, 0x00767290, 4) == (0x005F1DD1, 0, 0, 0x005F1DDB),
             "TrueType metric-variation service table drift")
    _require(_words(image, 0x006DED34, 24)[2] == 0x0078C7E8,
             "TrueType driver class name pointer drift")
    _require(_slice(image, 0x0078C7E8, 0x0078C7F1) == b"truetype\0",
             "TrueType driver name drift")

    ghidra_rows = {int(row["entry"], 16): row for row in map(json.loads, ghidra_data.splitlines())}
    expected_additions = {start for _, _, start, _, _ in GHIDRA_ADDITIONS}
    for symbol, module, start, end, digest in GHIDRA_ADDITIONS:
        row = ghidra_rows.get(start)
        _require(row is not None and int(row["body_end_inclusive"], 16) + 1 == end and
                 row["body_sha256"] == digest, f"Ghidra addition drift: {symbol}")
        _require(symbol in sources[module], f"source identity drift: {symbol}")
    _require(0x005F958C in ghidra_rows and ghidra_rows[0x005F958C]["body_sha256"] ==
             "4e196cf085fd48c54bb65acfc14ef1b55f185f598ade74be448e663b1be2945a",
             "TrueType trailing boundary drift")

    existing_groups = (
        (candidate["callbacks"], "high", "existing-driver-class-callback"),
        (candidate["helpers"], "medium", "existing-reachable-private-helper"),
        (candidate["interpreter_dispatch"]["opcode_bodies"], "medium", "existing-interpreter-opcode"),
        (candidate["interpreter_dispatch"]["support_bodies"], "medium", "existing-interpreter-support"),
        (candidate["interpreter_dispatch"]["callback_bodies"], "high", "existing-indirect-callback"),
    )
    records = []
    intervals: list[tuple[int, int]] = []
    for rows, confidence, origin in existing_groups:
        for row in rows:
            start = int(row["entry"], 16)
            end = start + row["bytes"]
            body = _slice(image, start, end)
            intervals.append((start, end))
            records.append({
                "symbol": row["symbol"], "module": Path(row["source"]).name,
                "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
                "bytes": end - start, "body_sha256": _sha(body),
                "confidence": confidence, "mapping_origin": origin,
                "compiler_byte_identity_claimed": False,
            })
    for origin, rows in (("new-pinned-ghidra-source-identity", GHIDRA_ADDITIONS),
                         ("recovered-service-or-source-ordered-body", RECOVERED)):
        for symbol, module, start, end, digest in rows:
            _require(_sha(_slice(image, start, end)) == digest, f"body drift: {symbol}")
            _require(symbol in sources[module], f"source identity drift: {symbol}")
            intervals.append((start, end))
            records.append({
                "symbol": symbol, "module": module, "start": f"0x{start:08X}",
                "end_exclusive": f"0x{end:08X}", "bytes": end - start,
                "body_sha256": digest, "confidence": "high",
                "mapping_origin": origin, "compiler_byte_identity_claimed": False,
            })

    physical_records = []
    category_bytes: dict[str, int] = {}
    for start, end, category, digest in PHYSICAL:
        _require(_sha(_slice(image, start, end)) == digest, "TrueType physical residue drift")
        intervals.append((start, end))
        category_bytes[category] = category_bytes.get(category, 0) + end - start
        physical_records.append({
            "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
            "bytes": end - start, "category": category, "sha256": digest,
            "callable": False,
        })

    cursor = ENVELOPE[0]
    for start, end in sorted(intervals):
        _require(start == cursor, f"unmapped/overlapping TrueType byte at 0x{cursor:08X}")
        cursor = end
    _require(cursor == ENVELOPE[1], "TrueType physical envelope incomplete")
    records.sort(key=lambda row: row["start"])
    _require(len({row["start"] for row in records}) == len(records), "duplicate callable row")
    high = [row for row in records if row["confidence"] == "high"]
    medium = [row for row in records if row["confidence"] == "medium"]
    _require((len(records), sum(row["bytes"] for row in records)) == (265, 41_728),
             "complete TrueType callable accounting drift")
    _require((len(high), sum(row["bytes"] for row in high)) == (56, 5_294),
             "TrueType high-confidence accounting drift")

    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-truetype-callable-physical-closure",
        "analysis_mode": "read-only; no hardware or flash operation",
        "image": {"bytes": IMAGE_PIN[0], "sha256": IMAGE_PIN[1],
                  "run_address_rule": "run = file_offset + 0x00437FE0"},
        "upstream": {"version": "2.9.1", "tag": "VER-2-9-1",
                     "commit": UPSTREAM_COMMIT, "license": "FTL"},
        "scope": {
            "module": "truetype", "envelope_start": f"0x{ENVELOPE[0]:08X}",
            "envelope_end_exclusive": f"0x{ENVELOPE[1]:08X}",
            "physical_bytes": ENVELOPE[1] - ENVELOPE[0],
            "callable_bytes": sum(row["bytes"] for row in records),
            "residual_physical": {"intervals": len(physical_records), "bytes": 476,
                                  "category_bytes": category_bytes,
                                  "unclassified_bytes": 0, "unresolved_callable_bytes": 0},
        },
        "candidate_distinction": {
            "existing_candidate_functions": 248,
            "existing_candidate_bytes": 38_828,
            "newly_mapped_functions": 17,
            "newly_mapped_callable_bytes": 2_900,
            "existing_candidate_scope": "reachable driver/interpreter graph; not a complete physical map",
            "this_scope": "complete stock TrueType callable and physical envelope",
        },
        "authenticated_tables": {
            "driver_class": "0x006DED34", "property_service": "0x0078ECB4",
            "multi_masters_service": "0x007505A8",
            "metrics_variations_service": "0x00767290",
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
            "font_payload_authenticated": False,
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
