#!/usr/bin/env python3
"""Build a fail-closed stock G2 FreeType 2.9.1 PSHinter function map.

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
SOURCE_ADMISSION = G2 / "tools/analyze_g2_cordio_ll_sea_none_source_admission.py"
PSHINTER = G2 / "third_party/freetype/src/pshinter"

LOAD_BASE = 0x00437FE0
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
GHIDRA_PIN = (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
SOURCE_MAPPING_SHA256 = "6fb586837c60efec60ac5dc603315cfc25bab6809cda67b90fece419658beb56"
PSHINTER_CENSUS_SHA256 = "2d7ebdb55894f8c585fb12b074b8526ca2b8e3e7c09abb6d94ff1ffb5de7dff3"

MODULE_CLASS = 0x00758A3C
MODULE_NAME = 0x0078BCD8
INTERFACE = 0x0078BCE4
FUNCTION_TABLE = 0x005D948C
ENVELOPE = (0x005D70A4, 0x005D94C0)

SOURCE_PINS = {
    "pshinter.c": (1_424, "c4271cc6b5ad7303e64dcc7f18be5602051bc5ade76069f86e47e795b4f87bc1"),
    "pshalgo.c": (59_738, "cbede1f596434c2348711a1ed12c60448ed14759b52a48c31cf1898564d69842"),
    "pshglob.c": (23_053, "0f22b4d604c977c377f0eb96c5b460fd74bf70c5a196aabc33ae1b94cdd99cbe"),
    "pshmod.c": (3_559, "478fab214d080cb14a7ea7551879c6a9ecd7c7d81d5e117221dc11aa6a3479d9"),
    "pshpic.c": (2_748, "1c1c244cf2310d6cc8427d40fa3f5395d76c9936ad662528dc3cd8e8d4d16ece"),
    "pshrec.c": (32_058, "0a639419fb8051eca8836be0eb1c1c9b7d9910ed4907670dde26de166bb33378"),
}

# symbol, module, start, end, body SHA-256, pointer reference, dispatch owner,
# slot, source signature.  Six rows overlap the closed Ghidra/source census;
# twelve rows recover complete bodies omitted by that callable relation.
DIRECT_SPECS = (
    ("ps_hints_apply", "pshalgo.c", 0x005D82C8, 0x005D843A,
     "a5525fb2f6233ece4ebbac772224753d3de0d0ae6fb43069e21710229a0eb7d6",
     0x005D94AC, "psh-globals-t1-table", 8,
     "FT_Error ( PS_Hints ps_hints, FT_Outline* outline, PSH_Globals globals, FT_Render_Mode hint_mode )"),
    ("psh_globals_destroy", "pshglob.c", 0x005D88D4, 0x005D8908,
     "49ecc2240359f80aa1d763801a2e38e436c975dbcbd4cb7951a751fc728f2bf3",
     0x005D9494, "psh-globals-table", 2, "void ( PSH_Globals globals )"),
    ("psh_globals_new", "pshglob.c", 0x005D8908, 0x005D8A48,
     "a06f5654c8da09df4594adb0640337110be76bcc802406ef175a8465ae7aae47",
     0x005D948C, "psh-globals-table", 0,
     "FT_Error ( FT_Memory memory, T1_Private* priv, PSH_Globals* aglobals )"),
    ("psh_globals_set_scale", "pshglob.c", 0x005D8A48, 0x005D8AA4,
     "987d62bf2aa1cc80a9ca912b70236c5d4a9adecfbce4187c158abd13de9cefa9",
     0x005D9490, "psh-globals-table", 1,
     "void ( PSH_Globals globals, FT_Fixed x_scale, FT_Fixed y_scale, FT_Fixed x_delta, FT_Fixed y_delta )"),
    ("ps_hinter_done", "pshmod.c", 0x005D8ABC, 0x005D8AD0,
     "8aeb17ad8be1a04ee071b6dfe087db59176d406829e0d169e3609ca203750f23",
     0x00758A58, "pshinter-module-class", 7, "void ( PS_Hinter_Module module )"),
    ("ps_hinter_init", "pshmod.c", 0x005D8AD0, 0x005D8B04,
     "c7cc1d291afefcef540ed8611a4fb41a00d71e79338a2043c99c34630602b703",
     0x00758A54, "pshinter-module-class", 6, "FT_Error ( PS_Hinter_Module module )"),
    ("pshinter_get_globals_funcs", "pshmod.c", 0x005D8B04, 0x005D8B08,
     "bb032f155683c89edf09051c3d3462ec154b68b40628e75fe8849a7b51ed70e8",
     0x0078BCE4, "pshinter-interface", 0, "PSH_Globals_Funcs ( FT_Module module )"),
    ("pshinter_get_t1_funcs", "pshmod.c", 0x005D8B08, 0x005D8B0C,
     "b609703ba7d531d83958f2d45c33b0129c2f3d08c6820f614a1f8e8194326f3a",
     0x0078BCE8, "pshinter-interface", 1, "T1_Hints_Funcs ( FT_Module module )"),
    ("pshinter_get_t2_funcs", "pshmod.c", 0x005D8B0C, 0x005D8B10,
     "320edee8f7d52a9466a5d7e8d684ce743e05cccdc681163409c9e996e4ff6098",
     0x0078BCEC, "pshinter-interface", 2, "T2_Hints_Funcs ( FT_Module module )"),
    ("ps_hints_t1stem3", "pshrec.c", 0x005D91BC, 0x005D9254,
     "da6a7feb5bb5f4e0b566e778608472142079b0e0c91b5c5dfa1c38fc45c76a59",
     0x005D94A4, "t1-hints-table", 6, "void ( T1_Hints hints, FT_Int dimension, FT_Fixed* coords )"),
    ("ps_hints_t1reset", "pshrec.c", 0x005D9254, 0x005D9296,
     "80d9852bbdc9c7f581f5b8628b9eb128d14144934d59e67d1b8b72112d610581",
     0x005D94A8, "t1-hints-table", 7, "void ( T1_Hints hints, FT_UInt end_point )"),
    ("ps_hints_t2mask", "pshrec.c", 0x005D9296, 0x005D92F0,
     "41536f89dd4e4b3ee0eaefba69ba763028d12fd8b8cc0eb8633200dd96d785ec",
     0x005D94B8, "t2-hints-table", 11,
     "void ( T2_Hints hints, FT_UInt end_point, FT_UInt bit_count, const FT_Byte* bytes )"),
    ("ps_hints_t2counter", "pshrec.c", 0x005D92F0, 0x005D934A,
     "b7810059d4914210dd5bec49d3062d96ba4bdd8c81cae3759c9e14b1bd8cee36",
     0x005D94BC, "t2-hints-table", 12,
     "void ( T2_Hints hints, FT_UInt bit_count, const FT_Byte* bytes )"),
    ("ps_hints_close", "pshrec.c", 0x005D934A, 0x005D9378,
     "62d7e020602db2cfd9267cdc5c9f7f7c06151a0900b5293c1a09e584028d4945",
     0x005D949C, "t1-hints-table", 4, "FT_Error ( PS_Hints hints, FT_UInt end_point )"),
    ("t1_hints_open", "pshrec.c", 0x005D9378, 0x005D9382,
     "60314bec35332200cfe6f3ea1ea156c11fb4338fee7f1446427e3bf22aff3705",
     0x005D9498, "t1-hints-table", 3, "void ( T1_Hints hints )"),
    ("t1_hints_stem", "pshrec.c", 0x005D9382, 0x005D93AC,
     "57ba9dd06f719688aeddfcc8d3b5de6653475c4fc051b114fb09f797e5b0a378",
     0x005D94A0, "t1-hints-table", 5,
     "void ( T1_Hints hints, FT_Int dimension, FT_Fixed* coords )"),
    ("t2_hints_open", "pshrec.c", 0x005D93D6, 0x005D93E0,
     "7905eaa529326f65aa366aebd9fc0ba0a4b7f973ae78cbe4eacddbc32173d408",
     0x005D94B0, "t2-hints-table", 9, "void ( T2_Hints hints )"),
    ("t2_hints_stems", "pshrec.c", 0x005D93E0, 0x005D9462,
     "6a0e297d368ddfd262a0b29398d5ea2da9c19244bbbc6b56bfb8029c138da6d4",
     0x005D94B4, "t2-hints-table", 10,
     "void ( T2_Hints hints, FT_UInt dimension, FT_UInt count, FT_Fixed* coords )"),
)

PHYSICAL_SPECS = (
    (0x005D8AB8, 0x005D8ABC, "literal-constant-pool", "psh-globals-init-literal"),
    (0x005D948C, 0x005D94C0, "function-pointer-table", "globals-t1-t2-dispatch-table"),
)


class MapError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    if (len(data), _sha(data)) != pin:
        raise MapError(f"pin drift: {path}")
    return data


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise MapError(f"analyzer dependency unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _slice(image: bytes, start: int, end: int) -> bytes:
    if not (LOAD_BASE <= start < end):
        raise MapError("invalid image interval")
    body = image[start - LOAD_BASE:end - LOAD_BASE]
    if len(body) != end - start:
        raise MapError(f"image interval unavailable: 0x{start:08X}-0x{end:08X}")
    return body


def _u32(image: bytes, address: int) -> int:
    return struct.unpack("<I", _slice(image, address, address + 4))[0]


def _record(
    image: bytes, symbol: str, module: str, start: int, end: int,
    confidence: str, evidence: list[str], span_kind: str,
) -> dict[str, Any]:
    body = _slice(image, start, end)
    return {
        "symbol": symbol,
        "module": module,
        "start": f"0x{start:08X}",
        "end_exclusive": f"0x{end:08X}",
        "bytes": len(body),
        "body_sha256": _sha(body),
        "confidence": confidence,
        "evidence": evidence,
        "span_kind": span_kind,
        "compiler_byte_identity_claimed": False,
    }


def _complement(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if start < ENVELOPE[0] or end > ENVELOPE[1] or start >= end:
            raise MapError("mapped interval escaped PSHinter envelope")
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            if start < merged[-1][1]:
                raise MapError("mapped function intervals overlap")
            merged[-1][1] = end
    output = []
    cursor = ENVELOPE[0]
    for start, end in merged:
        if start > cursor:
            output.append((cursor, start))
        cursor = end
    if cursor < ENVELOPE[1]:
        output.append((cursor, ENVELOPE[1]))
    return output


def run_audit() -> dict[str, Any]:
    image = _pinned(IMAGE, IMAGE_PIN)
    ghidra_data = _pinned(GHIDRA, GHIDRA_PIN)
    source = {
        name: _pinned(PSHINTER / name, pin).decode("utf-8")
        for name, pin in SOURCE_PINS.items()
    }
    include_positions = [
        source["pshinter.c"].find(f'#include "{name}"')
        for name in ("pshalgo.c", "pshglob.c", "pshmod.c", "pshpic.c", "pshrec.c")
    ]
    if -1 in include_positions or include_positions != sorted(include_positions):
        raise MapError("PSHinter single-object include order drift")

    class_words = struct.unpack("<9I", _slice(image, MODULE_CLASS, MODULE_CLASS + 36))
    expected_class = (0, 168, MODULE_NAME, 0x00010000, 0x00020000, INTERFACE,
                      0x005D8AD1, 0x005D8ABD, 0)
    if class_words != expected_class or _slice(image, MODULE_NAME, MODULE_NAME + 9) != b"pshinter\0":
        raise MapError("stock PSHinter module class/string drift")
    if struct.unpack("<3I", _slice(image, INTERFACE, INTERFACE + 12)) != (
        0x005D8B05, 0x005D8B09, 0x005D8B0D
    ):
        raise MapError("stock PSHinter interface drift")
    expected_function_table = tuple(start | 1 for start in (
        0x005D8908, 0x005D8A48, 0x005D88D4,
        0x005D9378, 0x005D934A, 0x005D9382, 0x005D91BC, 0x005D9254,
        0x005D82C8, 0x005D93D6, 0x005D93E0, 0x005D9296, 0x005D92F0,
    ))
    if struct.unpack("<13I", _slice(image, FUNCTION_TABLE, FUNCTION_TABLE + 52)) != expected_function_table:
        raise MapError("stock PSHinter nested dispatch table drift")

    ghidra_rows = {}
    for line in ghidra_data.splitlines():
        row = json.loads(line)
        entry = int(row["entry"], 16)
        if entry in ghidra_rows:
            raise MapError(f"duplicate Ghidra entry: 0x{entry:08X}")
        ghidra_rows[entry] = row
    ghidra_scope = {
        entry: row for entry, row in ghidra_rows.items()
        if ENVELOPE[0] <= entry < ENVELOPE[1]
    }
    if (len(ghidra_scope), sum(row["body_bytes"] for row in ghidra_scope.values())) != (67, 8_480):
        raise MapError("PSHinter Ghidra scope accounting drift")

    source_report = _load(SOURCE_ADMISSION, "open_cfw_pshinter_source_dependency").run_audit()
    if source_report["census"]["mapping_sha256"] != SOURCE_MAPPING_SHA256:
        raise MapError("closed source-admission mapping drift")
    psh_modules = {"pshalgo.c", "pshglob.c", "pshrec.c"}
    census = [
        row for row in source_report["census"]["records"]
        if row["provider"] == "freetype-2.9.1-ftl" and row["module"] in psh_modules
    ]
    census.sort(key=lambda row: int(row["start"], 16))
    if _sha(json.dumps(census, sort_keys=True, separators=(",", ":")).encode()) != PSHINTER_CENSUS_SHA256:
        raise MapError("PSHinter census mapping drift")
    if (len(census), sum(row["bytes"] for row in census)) != (67, 8_480):
        raise MapError("PSHinter retained source accounting drift")
    census_by_start = {int(row["start"], 16): row for row in census}
    if set(census_by_start) != set(ghidra_scope):
        raise MapError("PSHinter source/Ghidra entry set drift")

    direct_starts = {row[2] for row in DIRECT_SPECS}
    high = []
    source_order: dict[str, list[tuple[int, int]]] = {}
    for symbol, module, start, end, digest, reference, owner, slot, signature in DIRECT_SPECS:
        definitions = list(re.finditer(rf"(?m)^  {re.escape(symbol)}\s*\(", source[module]))
        if not definitions:
            raise MapError(f"{module}:{symbol}: definition missing")
        source_order.setdefault(module, []).append((start, definitions[-1].start()))
        body = _slice(image, start, end)
        if _sha(body) != digest or _u32(image, reference) != start | 1:
            raise MapError(f"{symbol}: direct pointer/body boundary drift")
        evidence = [
            "stock-module-interface-or-nested-table-pointer",
            "exact-freetype-2.9.1-definition",
            "exact-freetype-2.9.1-single-object-order",
            "complete-thumb-body-boundary",
            "whole-body-sha256",
        ]
        census_row = census_by_start.get(start)
        if census_row is not None:
            ghidra = ghidra_scope[start]
            if (int(census_row["end_exclusive"], 16), census_row["body_sha256"]) != (end, digest):
                raise MapError(f"{symbol}: census boundary/hash drift")
            if ghidra["body_sha256"] != digest:
                raise MapError(f"{symbol}: Ghidra boundary/hash drift")
            evidence.extend(("closed-source-admission-census", "pinned-ghidra-body"))
            origin = "retained-census-promoted-by-direct-pointer"
        else:
            if start in ghidra_scope:
                raise MapError(f"{symbol}: unexpected harvested callable row")
            evidence.append("recovered-outside-harvested-callable-relation")
            origin = "recovered-direct-dispatch-callback"
        record = _record(image, symbol, module, start, end, "high", evidence,
                         "direct-dispatch-callable-body")
        record.update({
            "mapping_origin": origin,
            "source_signature": signature,
            "dispatch_owner": owner,
            "dispatch_slot": slot,
            "pointer_reference": f"0x{reference:08X}",
            "thumb_pointer": f"0x{start | 1:08X}",
        })
        high.append(record)
    for module, pairs in source_order.items():
        if [position for _, position in sorted(pairs)] != sorted(position for _, position in pairs):
            raise MapError(f"{module}: direct callback source/address order drift")

    medium = []
    for row in census:
        start = int(row["start"], 16)
        if start in direct_starts:
            continue
        end = int(row["end_exclusive"], 16)
        ghidra = ghidra_scope[start]
        if ghidra["body_sha256"] != row["body_sha256"] or ghidra["body_bytes"] != row["bytes"]:
            raise MapError(f"{row['symbol']}: census/Ghidra body drift")
        medium.append(_record(
            image, row["symbol"], row["module"], start, end, "medium",
            ["closed-source-admission-census", "pinned-ghidra-body",
             "exact-freetype-2.9.1-single-object-order"],
            "ghidra-body",
        ))

    high.sort(key=lambda row: int(row["start"], 16))
    medium.sort(key=lambda row: int(row["start"], 16))
    if (len(high), sum(row["bytes"] for row in high)) != (18, 1_554):
        raise MapError("high-confidence PSHinter accounting drift")
    if (len(medium), sum(row["bytes"] for row in medium)) != (61, 7_634):
        raise MapError("medium-confidence PSHinter accounting drift")
    mapped = high + medium
    if len({row["start"] for row in mapped}) != len(mapped):
        raise MapError("duplicate mapped PSHinter entry")

    residual_pairs = _complement([
        (int(row["start"], 16), int(row["end_exclusive"], 16)) for row in mapped
    ])
    if residual_pairs != [(row[0], row[1]) for row in PHYSICAL_SPECS]:
        raise MapError("PSHinter physical complement drift")
    physical = []
    for start, end, category, evidence in PHYSICAL_SPECS:
        body = _slice(image, start, end)
        physical.append({
            "start": f"0x{start:08X}",
            "end_exclusive": f"0x{end:08X}",
            "bytes": len(body),
            "body_sha256": _sha(body),
            "category": category,
            "evidence": evidence,
            "source_identity_claimed": False,
        })
    if physical[0]["body_sha256"] != "7aaea5068f591b342f3b6b6b49e7e3fe8ad0df905f724bfc960fd2bc99db034f":
        raise MapError("PSHinter literal hash drift")
    if physical[1]["body_sha256"] != "0738155f116f8218bc35038319ce48facdd8fd8d25967d83d13c9cad23023dfa":
        raise MapError("PSHinter dispatch table hash drift")

    high_total = {"functions": len(high), "bytes": sum(row["bytes"] for row in high)}
    medium_total = {"functions": len(medium), "bytes": sum(row["bytes"] for row in medium)}
    mapping_sha = _sha(json.dumps(high + medium + physical, sort_keys=True,
                                  separators=(",", ":")).encode())
    return {
        "status": "fail-closed-pshinter-function-map",
        "read_only": True,
        "hardware_operations": False,
        "production_routed": False,
        "binary_overlay_ready": False,
        "compiler_byte_identity_claimed": False,
        "selected_module": "pshinter",
        "selection": {
            "method": "largest authenticated remaining FreeType retained-source module",
            "candidates": [
                {"module": "pshinter", "source_backed_functions": 67, "source_backed_bytes": 8_480, "direct_callback_targets": 18},
                {"module": "psaux", "source_backed_functions": 57, "source_backed_bytes": 7_114, "direct_callback_targets": None},
                {"module": "psnames", "source_backed_functions": 7, "source_backed_bytes": 1_010, "direct_callback_targets": None},
                {"module": "smooth-raster", "source_backed_functions": 0, "source_backed_bytes": 0, "direct_callback_targets": 7},
            ],
        },
        "anchors": {
            "image": {"path": str(IMAGE.relative_to(G2)), "bytes": IMAGE_PIN[0], "sha256": IMAGE_PIN[1], "load_base": f"0x{LOAD_BASE:08X}"},
            "ghidra": {"path": str(GHIDRA.relative_to(G2)), "bytes": GHIDRA_PIN[0], "sha256": GHIDRA_PIN[1]},
            "module_class": f"0x{MODULE_CLASS:08X}",
            "module_name": "pshinter",
            "module_name_address": f"0x{MODULE_NAME:08X}",
            "module_interface": f"0x{INTERFACE:08X}",
            "nested_function_table": f"0x{FUNCTION_TABLE:08X}",
            "freetype_version": "2.9.1",
            "freetype_commit": "86bc8a95056c97a810986434a3f268cbe67f2902",
        },
        "scope": {
            "start": f"0x{ENVELOPE[0]:08X}",
            "end_exclusive": f"0x{ENVELOPE[1]:08X}",
            "bytes": ENVELOPE[1] - ENVELOPE[0],
            "ghidra_recognized": {"functions": 67, "bytes": 8_480, "unmapped_functions": 0},
            "residual_physical": {
                "intervals": 2,
                "bytes": 56,
                "category_bytes": {"literal-constant-pool": 4, "function-pointer-table": 52},
                "unclassified_bytes": 0,
                "callable_code_bytes": 0,
            },
        },
        "confidence": {
            "exact": {"functions": 0, "bytes": 0, "reason": "no compiler-byte identity proof"},
            "high": high_total,
            "medium": medium_total,
            "mapped_total": {"functions": len(mapped), "bytes": sum(row["bytes"] for row in mapped)},
            "unresolved_code": {"functions": 0, "bytes": 0, "source_identities_complete": True},
        },
        "movement": {
            "retained_census_promoted_to_high": {"functions": 6, "bytes": 846},
            "retained_census_medium": medium_total,
            "recovered_direct_callbacks": {"functions": 12, "bytes": 708},
            "new_beyond_closed_census": {"functions": 12, "bytes": 708},
        },
        "mapping_sha256": mapping_sha,
        "records": {"high": high, "medium": medium, "physical_classification": physical},
        "source_pins": {name: {"bytes": pin[0], "sha256": pin[1]} for name, pin in SOURCE_PINS.items()},
        "blockers": [
            "original compiler/version/options, ABI details, and LTO state are not recovered",
            "no authenticated stock callsite rewrite or target placement routes this map",
            "no live hardware execution was performed",
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
