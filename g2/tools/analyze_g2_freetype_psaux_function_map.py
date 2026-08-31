#!/usr/bin/env python3
"""Build a fail-closed stock G2 FreeType 2.9.1 PSAux function map.

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
GHIDRA = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
PROVENANCE = G2 / "third_party/freetype/PROVENANCE.json"
PSAUX = G2 / "third_party/freetype/src/psaux"
CORE = G2 / "tools/analyze_g2_cordio_ll_sea_none_source_admission.py"
HOP2 = G2 / "tools/analyze_g2_cordio_ll_sea_hop2_candidate.py"
HOP3 = G2 / "tools/analyze_g2_cordio_ll_sea_anchor_hop3_candidate.py"
HOP4 = G2 / "tools/analyze_g2_cordio_ll_sea_hop4_residue_candidate.py"

LOAD_BASE = 0x00437FE0
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
GHIDRA_PIN = (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
PROVENANCE_PIN = (102_377, "2be8717625bceddee3aa95663186c0629247304c951c4790bc26cd372e3794bf")
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"

MODULE_CLASS = 0x00758A18
MODULE_NAME = 0x0078E424
INTERFACE = 0x00741F70
ENVELOPE = (0x005CF8E4, 0x005D70A4)

DEPENDENCY_PINS = {
    "core": "6fb586837c60efec60ac5dc603315cfc25bab6809cda67b90fece419658beb56",
    "hop2": "2aa75013fe4893f78266ae45c14addbbd1da217c85d5217d1658fb802958c79b",
    "hop3": "39260ef5dd0fea7f804d732248f2ccd08908d3fb3f5914d442fe3b24114301d0",
    "hop4": "21bdb2fd7bd4498e2c0a115220cce5af828263270c0dcd09475cfb6a8c845848",
}

AFM_IDENTITIES = {
    0x005CF8E4: "afm_stream_skip_spaces",
    0x005CF938: "afm_stream_read_one",
    0x005CF99A: "afm_stream_read_string",
    0x005CF9E8: "afm_parser_read_vals",
    0x005CFAF4: "afm_parser_next_key",
    0x005CFB62: "afm_tokenize",
    0x005CFBB4: "afm_parser_init",
    0x005CFBF2: "afm_parser_done",
    0x005CFC04: "afm_parser_read_int",
    0x005CFC26: "afm_parse_track_kern",
    0x005CFD38: "afm_parse_kern_pairs",
    0x005CFE54: "afm_parse_kern_data",
    0x005CFEAA: "afm_parser_skip_section",
    0x005CFEFA: "afm_parser_parse",
}

# Bodies omitted by the harvested callable relation.  Each interval is a
# complete Thumb function, corroborated by source order and either a stock
# dispatch pointer or a semantic call edge.
RECOVERED = (
    ("afm_compare_kern_pairs", "afmparse.c", 0x005CFD12, 0x005CFD38),
    ("ps_table_release", "psobjs.c", 0x005D06C6, 0x005D06FE),
    ("ps_parser_to_fixed", "psobjs.c", 0x005D121A, 0x005D1232),
    ("ps_parser_to_coord_array", "psobjs.c", 0x005D1232, 0x005D124E),
    ("ps_parser_to_fixed_array", "psobjs.c", 0x005D124E, 0x005D126E),
    ("ps_parser_init", "psobjs.c", 0x005D126E, 0x005D128A),
    ("ps_parser_done", "psobjs.c", 0x005D128A, 0x005D128C),
    ("t1_builder_close_contour", "psobjs.c", 0x005D1460, 0x005D1512),
    ("cff_builder_done", "psobjs.c", 0x005D159A, 0x005D15B0),
    ("cff_builder_close_contour", "psobjs.c", 0x005D16D0, 0x005D176A),
    ("ps_builder_done", "psobjs.c", 0x005D1848, 0x005D185E),
    ("t1_make_subfont", "psobjs.c", 0x005D1B4A, 0x005D1D02),
    ("t1_decrypt", "psobjs.c", 0x005D1D02, 0x005D1D1C),
    ("t1_cmap_std_done", "t1cmap.c", 0x005D1D52, 0x005D1D64),
    ("t1_cmap_standard_init", "t1cmap.c", 0x005D1DD4, 0x005D1DE0),
    ("t1_cmap_expert_init", "t1cmap.c", 0x005D1DE0, 0x005D1DEC),
    ("t1_cmap_custom_init", "t1cmap.c", 0x005D1DEC, 0x005D1E06),
    ("t1_cmap_custom_done", "t1cmap.c", 0x005D1E06, 0x005D1E14),
    ("t1_cmap_custom_char_index", "t1cmap.c", 0x005D1E14, 0x005D1E34),
    ("t1_cmap_custom_char_next", "t1cmap.c", 0x005D1E34, 0x005D1E68),
    ("psaux_get_glyph_name", "t1cmap.c", 0x005D1E68, 0x005D1E72),
    ("t1_cmap_unicode_init", "t1cmap.c", 0x005D1E72, 0x005D1E92),
    ("t1_cmap_unicode_done", "t1cmap.c", 0x005D1E9C, 0x005D1EB4),
    ("t1_decoder_done", "t1decode.c", 0x005D2140, 0x005D2170),
    ("cf2_builder_lineTo", "psft.c", 0x005D2F34, 0x005D2F80),
    ("cf2_builder_cubeTo", "psft.c", 0x005D2F80, 0x005D2FEE),
)

PHYSICAL = (
    (0x005D0570, 0x005D0574, "literal-pool", "1caf3298af304d0615bf5510daf4aca8cd3a86555222573eda9a243941a3451a"),
    (0x005D06FE, 0x005D071C, "literal-pool", "643198ebec19d232382b83e583cff356bb2965e73e66c08f16e58285a9cb4e2a"),
    (0x005D1E92, 0x005D1E9C, "literal-pool", "fc664bc6523373f1290d2dcfdef8f8fd13f528d663afbf9a930ced0f544c1a49"),
    (0x005D2138, 0x005D2140, "literal-pool", "ea90c98c2a94ceebb544eb45d6ed5431ffa6660b0f35c9925e1041574fe64ac2"),
    (0x005D280E, 0x005D2828, "literal-pool", "ed21e19e4e22ec253dc7b3df7575b0638674499fed2d284cef2f25ee04542e66"),
    (0x005D3014, 0x005D3018, "literal-pool", "89c694881c85cbb7f7762b65477029d1723f46e6bcc735bf38e6bea52d6e4da5"),
    (0x005D3228, 0x005D3238, "function-pointer-table", "83de8ace0b032aeb6351bd64157e664fbb844755a0f183cd145a6381b098a545"),
    (0x005D474A, 0x005D4754, "literal-pool", "46d151aed1b6287a7f4f8dc3ea0dc9910c94e3fc7e8064ff1bf7ac0c4e2c83fd"),
    (0x005D4ECE, 0x005D4ED0, "alignment-padding", "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
    (0x005D5B86, 0x005D5BA0, "literal-pointer-string-pool", "1bacd7b8bad04513f83e1dc6352b861e26949285a6005f0002b89bbfc6802d14"),
    (0x005D7096, 0x005D709C, "literal-pool", "2f5edf396e6017c00685514de3bef93e7ca65f79992a85d64610b324047dcc7f"),
    (0x005D70A2, 0x005D70A4, "alignment-padding", "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
)

FOREIGN = {
    0x005D2BAE: (0x005D2E0C, "Cordio dm_conn.c path-anchored body"),
    0x005D2E0C: (0x005D2EA8, "Cordio connection-establishment wrapper"),
}


class MapError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MapError(message)


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    _require((len(data), _sha(data)) == pin, f"pin drift: {path}")
    return data


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise MapError(f"dependency unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _slice(image: bytes, start: int, end: int) -> bytes:
    _require(LOAD_BASE <= start < end, "invalid image interval")
    data = image[start - LOAD_BASE:end - LOAD_BASE]
    _require(len(data) == end - start, f"image interval unavailable: 0x{start:08X}")
    return data


def _words(image: bytes, address: int, count: int) -> tuple[int, ...]:
    return struct.unpack(f"<{count}I", _slice(image, address, address + count * 4))


def _record(image: bytes, symbol: str, module: str, start: int, end: int,
            confidence: str, evidence: list[str], origin: str) -> dict[str, Any]:
    body = _slice(image, start, end)
    return {
        "symbol": symbol, "module": module,
        "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
        "bytes": len(body), "body_sha256": _sha(body),
        "confidence": confidence, "evidence": evidence,
        "mapping_origin": origin, "compiler_byte_identity_claimed": False,
    }


def _complement(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    cursor = ENVELOPE[0]
    output = []
    for start, end in sorted(intervals):
        _require(ENVELOPE[0] <= start < end <= ENVELOPE[1], "interval escaped PSAux envelope")
        _require(start >= cursor, "PSAux physical intervals overlap")
        if start > cursor:
            output.append((cursor, start))
        cursor = end
    if cursor < ENVELOPE[1]:
        output.append((cursor, ENVELOPE[1]))
    return output


def run_audit() -> dict[str, Any]:
    image = _pinned(IMAGE, IMAGE_PIN)
    ghidra_data = _pinned(GHIDRA, GHIDRA_PIN)
    provenance = json.loads(_pinned(PROVENANCE, PROVENANCE_PIN))
    _require(provenance["upstream"]["peeled_commit"] == UPSTREAM_COMMIT, "FreeType commit drift")

    inventory = [row for row in provenance["files"] if row["local_path"].startswith("src/psaux/")
                 and Path(row["local_path"]).suffix in {".c", ".h"}]
    sources: dict[str, str] = {}
    for row in inventory:
        data = (PROVENANCE.parent / row["local_path"]).read_bytes()
        _require((len(data), _sha(data)) == (row["size"], row["sha256"]),
                 f"PSAux source drift: {row['local_path']}")
        sources[Path(row["local_path"]).name] = data.decode("utf-8")
    _require((len(inventory), sum(row["size"] for row in inventory)) == (37, 625_815),
             "PSAux inventory drift")
    includes = re.findall(r'^#include "([^"]+\.c)"', sources["psaux.c"], re.MULTILINE)
    _require(includes == ["afmparse.c", "psauxmod.c", "psconv.c", "psobjs.c", "t1cmap.c",
                          "t1decode.c", "cffdecode.c", "psarrst.c", "psblues.c", "pserror.c",
                          "psfont.c", "psft.c", "pshints.c", "psintrp.c", "psread.c", "psstack.c"],
             "PSAux single-object source order drift")

    _require(_words(image, MODULE_CLASS, 9) ==
             (0, 12, MODULE_NAME, 0x20000, 0x20000, INTERFACE, 0, 0, 0),
             "stock PSAux module class drift")
    _require(_slice(image, MODULE_NAME, MODULE_NAME + 6) == b"psaux\0", "stock PSAux name drift")
    interface_words = _words(image, INTERFACE, 11)
    _require(interface_words == (0x788400, 0x72C3DC, 0x764250, 0x788410,
                                  0x5D1D03, 0x5D1D1D, 0x5D1A39, 0x5D1B4B,
                                  0x788420, 0x78BC90, 0x78BC9C),
             "stock PSAux interface drift")

    tables = {
        0x788400: (0x5D04E9, 0x5D0683, 0x5D05E7, 0x5D06C7),
        0x72C3DC: (0x5D126F, 0x5D128B, 0x5D0A69, 0x5D08F7, 0x5D1191, 0x5D121B,
                    0x5D11A5, 0x5D1233, 0x5D124F, 0x5D0A73, 0x5D0B7D, 0x5D0DE1, 0x5D10C5),
        0x764250: (0x5D128D, 0x5D1307, 0x5D131D, 0x5D1349, 0x5D139F, 0x5D13C5,
                    0x5D142F, 0x5D1461),
        0x764270: (0x5D1513, 0x5D159B, 0x5D15B1, 0x5D15DD, 0x5D161B, 0x5D1641,
                    0x5D16A3, 0x5D16D1),
        0x788410: (0x5D20BD, 0x5D2141, 0x5D1F27, 0x5D3069),
        0x78E434: (0x5D176B, 0x5D1849),
        0x78BC90: (0x5CFBB5, 0x5CFBF3, 0x5CFEFB),
        0x78BC9C: (0x5D21E5, 0x5D2251, 0x5D3069),
        0x5D3228: (0x5D2F23, 0x5D2F35, 0x5D2F81, 0x5D2EFF),
    }
    pointer_references: dict[int, list[str]] = {}
    for address, expected in tables.items():
        _require(_words(image, address, len(expected)) == expected,
                 f"stock PSAux table drift: 0x{address:08X}")
        for slot, pointer in enumerate(expected):
            target = pointer & ~1
            if ENVELOPE[0] <= target < ENVELOPE[1]:
                pointer_references.setdefault(target, []).append(f"0x{address + slot * 4:08X}")
    for slot, pointer in enumerate(interface_words[4:8], 4):
        pointer_references.setdefault(pointer & ~1, []).append(f"0x{INTERFACE + slot * 4:08X}")

    cmap_class_addresses = _words(image, 0x788420, 4)
    _require(cmap_class_addresses == (0x74D174, 0x74D19C, 0x74D1C4, 0x74D1EC),
             "PSAux cmap class list drift")
    cmap_classes = (
        (0x20, 0x5D1DD5, 0x5D1D53, 0x5D1D65, 0x5D1DAB, 0, 0, 0, 0, 0),
        (0x20, 0x5D1DE1, 0x5D1D53, 0x5D1D65, 0x5D1DAB, 0, 0, 0, 0, 0),
        (0x1C, 0x5D1DED, 0x5D1E07, 0x5D1E15, 0x5D1E35, 0, 0, 0, 0, 0),
        (0x18, 0x5D1E73, 0x5D1E9D, 0x5D1EB5, 0x5D1EC3, 0, 0, 0, 0, 0),
    )
    for address, expected in zip(cmap_class_addresses, cmap_classes):
        _require(_words(image, address, 10) == expected, "PSAux cmap class drift")
        for slot, pointer in enumerate(expected[1:5], 1):
            pointer_references.setdefault(pointer & ~1, []).append(f"0x{address + slot * 4:08X}")

    ghidra = {}
    for line in ghidra_data.splitlines():
        row = json.loads(line)
        start = int(row["entry"], 16)
        if ENVELOPE[0] <= start < ENVELOPE[1]:
            ghidra[start] = row
    _require((len(ghidra), sum(row["body_bytes"] for row in ghidra.values())) == (175, 28_996),
             "PSAux Ghidra envelope drift")

    core = _load(CORE, "open_cfw_psaux_core_dependency").run_audit()
    _require(core["census"]["mapping_sha256"] == DEPENDENCY_PINS["core"], "core map drift")
    psaux_modules = set(sources)
    identities: dict[int, tuple[str, str, str]] = {
        address: ("afmparse.c", symbol, "authenticated-afm-source-order")
        for address, symbol in AFM_IDENTITIES.items()
    }
    for row in core["census"]["records"]:
        if row["provider"] == "freetype-2.9.1-ftl" and row["module"] in psaux_modules:
            identities[int(row["start"], 16)] = (row["module"], row["symbol"], "closed-source-census")
    identities[0x005D0414] = ("psconv.c", "PS_Conv_ASCIIHexDecode", "semantic-correction")
    identities[0x005D049E] = ("psconv.c", "PS_Conv_EexecDecode", "semantic-correction")
    identities[0x005D04E8] = ("psobjs.c", "ps_table_new", "direct-table-correction")

    dependencies = ((HOP2, "hop2", "hop2_tranche"),
                    (HOP3, "hop3", "source_attribution"),
                    (HOP4, "hop4", "source_attribution"))
    for path, name, key in dependencies:
        output = _load(path, f"open_cfw_psaux_{name}_dependency").run_audit()[key]["records"]
        _require(_canonical(output) == DEPENDENCY_PINS[name], f"{name} mapping drift")
        for address_text, row in output.items():
            if row.get("disposition", "upstream_freetype_source") != "upstream_freetype_source":
                continue
            address = int(address_text, 16)
            identity = (row["upstream_module"], row["upstream_function"], f"authenticated-{name}-mapping")
            _require(address not in identities or identities[address][:2] == identity[:2],
                     f"conflicting source identity: 0x{address:08X}")
            identities[address] = identity

    _require((len(identities), set(ghidra) - set(identities)) == (173, set(FOREIGN)),
             "PSAux source/Ghidra partition drift")

    recovered_by_start = {row[2]: row for row in RECOVERED}
    recovered_source_order: dict[str, list[tuple[int, int]]] = {}
    for symbol, module, start, _ in RECOVERED:
        matches = list(re.finditer(rf"(?m)^  {re.escape(symbol)}\s*\(", sources[module]))
        _require(matches, f"recovered definition missing: {module}:{symbol}")
        recovered_source_order.setdefault(module, []).append((start, matches[-1].start()))
    for module, pairs in recovered_source_order.items():
        ordered = sorted(pairs)
        _require([position for _, position in ordered] == sorted(position for _, position in ordered),
                 f"recovered source/address order drift: {module}")
    all_identities = dict(identities)
    for symbol, module, start, _ in RECOVERED:
        _require(start not in all_identities, f"duplicate recovered entry: {symbol}")
        all_identities[start] = (module, symbol, "recovered-complete-body")

    records = []
    for start in sorted(all_identities):
        module, symbol, origin = all_identities[start]
        _require(module in sources and re.search(rf"\b{re.escape(symbol)}\s*\(", sources[module]),
                 f"source definition missing: {module}:{symbol}")
        if start in ghidra:
            row = ghidra[start]
            end = int(row["body_end_inclusive"], 16) + 1
            ranges = [(int(left, 16), int(right, 16) + 1) for left, right in row["ranges"]]
            body = b"".join(_slice(image, left, right) for left, right in ranges)
            _require(_sha(_slice(image, start, end)) == row["body_sha256"] and
                     len(body) == row["body_bytes"],
                     f"Ghidra body drift: 0x{start:08X}")
            evidence = [origin, "pinned-ghidra-whole-body", "exact-freetype-2.9.1-definition"]
        else:
            _, _, _, end = recovered_by_start[start]
            evidence = [origin, "complete-thumb-body-boundary", "whole-body-sha256",
                        "exact-freetype-2.9.1-definition", "source-order-and-semantic-call-evidence"]
        confidence = "high" if start in pointer_references else "medium"
        if confidence == "high":
            evidence.append("stock-interface-or-function-table-pointer")
        if start in ghidra and len(ranges) > 1:
            record = {
                "symbol": symbol, "module": module,
                "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
                "bytes": len(body), "body_sha256": row["body_sha256"],
                "range_bytes_sha256": _sha(body),
                "ranges": [[f"0x{left:08X}", f"0x{right:08X}"] for left, right in ranges],
                "confidence": confidence, "evidence": evidence,
                "mapping_origin": origin, "compiler_byte_identity_claimed": False,
            }
        else:
            record = _record(image, symbol, module, start, end, confidence, evidence, origin)
        if start in pointer_references:
            record["pointer_references"] = pointer_references[start]
            record["thumb_pointer"] = f"0x{start | 1:08X}"
        records.append(record)

    _require((len(records), sum(row["bytes"] for row in records)) == (199, 29_750),
             "PSAux callable accounting drift")
    foreign = []
    for start, (end, identity) in FOREIGN.items():
        row = ghidra[start]
        _require(int(row["body_end_inclusive"], 16) + 1 == end, "foreign boundary drift")
        foreign.append({
            "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
            "bytes": end - start, "body_sha256": row["body_sha256"],
            "category": "authenticated-foreign-callable-code", "identity": identity,
            "psaux_source_identity_claimed": False,
        })
    _require(sum(row["bytes"] for row in foreign) == 762, "foreign callable accounting drift")

    physical = []
    for start, end, category, digest in PHYSICAL:
        body = _slice(image, start, end)
        _require(_sha(body) == digest, f"physical classification drift: 0x{start:08X}")
        physical.append({
            "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
            "bytes": len(body), "body_sha256": digest, "category": category,
            "callable_code": False, "source_identity_claimed": False,
        })
    intervals = []
    for row in records + foreign + physical:
        intervals.extend(
            [(int(left, 16), int(right, 16)) for left, right in row["ranges"]]
            if "ranges" in row else
            [(int(row["start"], 16), int(row["end_exclusive"], 16))]
        )
    _require(_complement(intervals) == [], "PSAux envelope retains unclassified physical bytes")

    high = [row for row in records if row["confidence"] == "high"]
    medium = [row for row in records if row["confidence"] == "medium"]
    high_total = {"functions": len(high), "bytes": sum(row["bytes"] for row in high)}
    medium_total = {"functions": len(medium), "bytes": sum(row["bytes"] for row in medium)}
    mapping_sha = _canonical(records + foreign + physical)
    categories: dict[str, int] = {}
    for row in physical:
        categories[row["category"]] = categories.get(row["category"], 0) + row["bytes"]

    return {
        "status": "fail-closed-psaux-function-map", "read_only": True,
        "selected_module": "psaux", "hardware_operations": False,
        "anchors": {
            "image": {"path": str(IMAGE.relative_to(G2)), "bytes": IMAGE_PIN[0], "sha256": IMAGE_PIN[1],
                      "load_base": f"0x{LOAD_BASE:08X}"},
            "ghidra": {"path": str(GHIDRA.relative_to(G2)), "bytes": GHIDRA_PIN[0], "sha256": GHIDRA_PIN[1]},
            "module_class": f"0x{MODULE_CLASS:08X}", "module_name_address": f"0x{MODULE_NAME:08X}",
            "module_interface": f"0x{INTERFACE:08X}", "freetype_version": "2.9.1",
            "freetype_commit": UPSTREAM_COMMIT,
        },
        "scope": {
            "start": f"0x{ENVELOPE[0]:08X}", "end_exclusive": f"0x{ENVELOPE[1]:08X}",
            "bytes": ENVELOPE[1] - ENVELOPE[0],
            "ghidra_recognized": {"functions": 175, "bytes": 28_996},
            "psaux_ghidra_source_backed": {"functions": 173, "bytes": 28_234},
            "recovered_psaux_callable": {"functions": len(RECOVERED), "bytes": 1_516},
            "foreign_callable": {"functions": 2, "bytes": 762},
            "residual_physical": {"intervals": len(physical), "bytes": sum(row["bytes"] for row in physical),
                                  "category_bytes": categories, "unclassified_bytes": 0,
                                  "unresolved_callable_bytes": 0},
        },
        "confidence": {
            "exact": {"functions": 0, "bytes": 0, "reason": "no compiler-byte identity proof"},
            "high": high_total, "medium": medium_total,
            "mapped_total": {"functions": len(records), "bytes": sum(row["bytes"] for row in records)},
            "unresolved_code": {"functions": 0, "bytes": 0, "source_identities_complete": True},
        },
        "movement": {
            "initial_retained_census": {"functions": 57, "bytes": 7_114},
            "additional_authenticated_ghidra_source": {"functions": 116, "bytes": 21_120},
            "recovered_outside_ghidra_relation": {"functions": len(RECOVERED), "bytes": 1_516},
            "corrected_prior_source_identities": {"functions": 3, "bytes": 348},
        },
        "mapping_sha256": mapping_sha,
        "records": {"psaux": records, "foreign_callable": foreign, "physical_classification": physical},
        "compiler_byte_identity_claimed": False, "binary_overlay_ready": False,
        "production_routed": False,
        "blockers": [
            "original compiler/version/options, ABI details, and LTO state are not recovered",
            "no authenticated stock callsite rewrite or target placement routes this map",
            "no live hardware rendering execution was performed",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
