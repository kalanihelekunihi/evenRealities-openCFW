#!/usr/bin/env python3
"""Build a fail-closed stock G2 FreeType 2.9.1 PSNames function map.

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
CORE = G2 / "tools/analyze_g2_cordio_ll_sea_none_source_admission.py"
PSNAMES = G2 / "third_party/freetype/src/psnames"
MANIFEST = G2 / "tools/manifests/g2-freetype-psnames-function-map.json"

LOAD_BASE = 0x00437FE0
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
GHIDRA_PIN = (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
CORE_MAPPING_SHA256 = "6fb586837c60efec60ac5dc603315cfc25bab6809cda67b90fece419658beb56"
CORE_CENSUS_SHA256 = "30cf937e174432946f6edb88764f97523055051b49a74fe95fad70606efbe881"
UPSTREAM_COMMIT = "86bc8a95056c97a810986434a3f268cbe67f2902"

MODULE_CLASS = 0x00758A60
MODULE_NAME = 0x0078E444
INTERFACE = 0x00764290
ENVELOPE = (0x005D94C0, 0x005D9950)

SOURCE_PINS = {
    "psmodule.c": (16_846, "d21c06ed3dee78cd85f1008275cb888f66099b1e3650e8c8dfdcf0406e7f1368"),
    "pstables.h": (268_872, "67a4dee05b7bb71f46e53026fa3fefd23ca26604ba46741accae82bc33fa9627"),
}

# These four complete bodies are absent from the Ghidra callable relation.
# symbol, module, start, end, whole-body SHA-256, evidence origin
RECOVERED = (
    ("compare_uni_maps", "psmodule.c", 0x005D9672, 0x005D96B6,
     "4e201d24f3034668ceb06bc6325811eea6ffe95790004757a6bdc9a894a1bad4",
     "qsort-callback-literal-and-semantic-body"),
    ("ps_get_macintosh_name", "psmodule.c", 0x005D98F6, 0x005D990A,
     "3d4b1c4d348f2acab2e1650e10a8d36dffe666010853d63a5567a84accc2a788",
     "pscmaps-interface-slot-4"),
    ("ps_get_standard_strings", "psmodule.c", 0x005D990A, 0x005D9922,
     "1e638b05487fe18b865433b0d7aef16df7194c0bce663b3f81a359883233d31f",
     "pscmaps-interface-slot-5"),
    ("psnames_get_service", "psmodule.c", 0x005D9922, 0x005D992C,
     "6ef2d615a411eada228ba9c966f43bcc7f9685c1119d8ab43cdebac9e8f4e167",
     "psnames-module-requester-slot"),
)

PHYSICAL = (
    (0x005D992C, 0x005D9950, "literal-pointer-pool",
     "77d908f30b20762cb33ba71ee6947fe520ee61aa88d8cbbaf2ae992ef8145a3f"),
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


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    _require(spec is not None and spec.loader is not None,
             f"analyzer dependency unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
                 "mapped interval escaped PSNames envelope")
        _require(start >= cursor, "mapped PSNames intervals overlap")
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
        "symbol": symbol,
        "module": module,
        "start": f"0x{start:08X}",
        "end_exclusive": f"0x{end:08X}",
        "bytes": len(body),
        "body_sha256": _sha(body),
        "confidence": confidence,
        "evidence": evidence,
        "mapping_origin": origin,
        "compiler_byte_identity_claimed": False,
    }


def run_audit() -> dict[str, Any]:
    image = _pinned(IMAGE, IMAGE_PIN)
    ghidra_data = _pinned(GHIDRA, GHIDRA_PIN)
    sources = {
        name: _pinned(PSNAMES / name, pin).decode("utf-8")
        for name, pin in SOURCE_PINS.items()
    }

    class_words = _words(image, MODULE_CLASS, 9)
    _require(class_words == (
        0, 12, MODULE_NAME, 0x00010000, 0x00020000, INTERFACE,
        0, 0, 0x005D9923,
    ), "stock PSNames module class drift")
    _require(_slice(image, MODULE_NAME, MODULE_NAME + 8) == b"psnames\0",
             "stock PSNames module name drift")
    interface_words = _words(image, INTERFACE, 8)
    _require(interface_words == (
        0x005D9581, 0x005D9717, 0x005D9841, 0x005D9891,
        0x005D98F7, 0x005D990B, 0x006C0550, 0x006C0750,
    ), "stock PSNames service interface drift")

    # The only private callback absent from the service/module tables is
    # independently present in ps_unicodes_init's literal pool as a Thumb
    # function pointer.  The other eight words are data/string/table literals.
    pool_words = _words(image, PHYSICAL[0][0], 9)
    _require(pool_words == (
        0x005FA850, 0x006E4958, 0x0074D23C, 0x0074D214, 0x005D9673,
        0x00657138, 0x006BFD4C, 0x006A33B8, 0x00788430,
    ), "stock PSNames literal pool drift")

    pointer_references: dict[int, list[str]] = {}
    for slot, pointer in enumerate(interface_words[:6]):
        pointer_references.setdefault(pointer & ~1, []).append(
            f"0x{INTERFACE + slot * 4:08X}"
        )
    pointer_references.setdefault(class_words[8] & ~1, []).append(
        f"0x{MODULE_CLASS + 8 * 4:08X}"
    )
    pointer_references.setdefault(pool_words[4] & ~1, []).append(
        f"0x{PHYSICAL[0][0] + 4 * 4:08X}"
    )

    ghidra: dict[int, dict[str, Any]] = {}
    next_callable: dict[str, Any] | None = None
    for line in ghidra_data.splitlines():
        row = json.loads(line)
        start = int(row["entry"], 16)
        if ENVELOPE[0] <= start < ENVELOPE[1]:
            _require(start not in ghidra, f"duplicate Ghidra entry: 0x{start:08X}")
            ghidra[start] = row
        elif start == ENVELOPE[1]:
            next_callable = row
    _require((len(ghidra), sum(row["body_bytes"] for row in ghidra.values())) ==
             (7, 1_010), "PSNames Ghidra envelope drift")
    _require(next_callable is not None and next_callable["body_bytes"] == 112 and
             next_callable["body_sha256"] ==
             "54b3088a7b1661a54833ef9a2fabd1b695afa90788afdf1e708673dbd90f95d2",
             "authenticated post-PSNames SEGGER boundary drift")

    core = _load(CORE, "open_cfw_psnames_core_dependency").run_audit()
    _require(core["census"]["mapping_sha256"] == CORE_MAPPING_SHA256,
             "core source map drift")
    census = [
        row for row in core["census"]["records"]
        if row["provider"] == "freetype-2.9.1-ftl"
        and row["module"] in sources
        and ENVELOPE[0] <= int(row["start"], 16) < ENVELOPE[1]
    ]
    census.sort(key=lambda row: int(row["start"], 16))
    _require(_canonical(census) == CORE_CENSUS_SHA256,
             "PSNames retained census drift")
    _require((len(census), sum(row["bytes"] for row in census)) == (7, 1_010),
             "PSNames retained census accounting drift")
    _require({int(row["start"], 16) for row in census} == set(ghidra),
             "PSNames census/Ghidra entry drift")

    identities = {
        int(row["start"], 16): (
            row["symbol"], row["module"], int(row["end_exclusive"], 16),
            "closed-source-census",
        )
        for row in census
    }
    for symbol, module, start, end, digest, origin in RECOVERED:
        _require(start not in identities, f"duplicate recovered entry: {symbol}")
        _require(_sha(_slice(image, start, end)) == digest,
                 f"recovered body drift: {symbol}")
        identities[start] = (symbol, module, end, origin)

    # Address order is identical to definition order across each exact 2.9.1
    # source file.  This catches plausible-looking symbol swaps.
    source_order: dict[str, list[tuple[int, int]]] = {}
    for start, (symbol, module, _, _) in identities.items():
        matches = list(re.finditer(rf"(?m)^\s*(?:FT_CALLBACK_DEF\([^\n]+\)\s*)?{re.escape(symbol)}\s*\(",
                                   sources[module]))
        _require(matches, f"source definition missing: {module}:{symbol}")
        source_order.setdefault(module, []).append((start, matches[0].start()))
    for module, pairs in source_order.items():
        ordered = sorted(pairs)
        _require([position for _, position in ordered] ==
                 sorted(position for _, position in ordered),
                 f"source/address order drift: {module}")

    records = []
    for start in sorted(identities):
        symbol, module, end, origin = identities[start]
        if start in ghidra:
            row = ghidra[start]
            _require(int(row["body_end_inclusive"], 16) + 1 == end,
                     f"Ghidra boundary drift: {symbol}")
            _require(row["body_bytes"] == end - start and
                     row["body_sha256"] == _sha(_slice(image, start, end)),
                     f"Ghidra whole-body drift: {symbol}")
            evidence = [
                origin, "pinned-ghidra-whole-body",
                "exact-freetype-2.9.1-definition", "authenticated-source-order",
            ]
        else:
            evidence = [
                origin, "complete-thumb-body-boundary", "whole-body-sha256",
                "exact-freetype-2.9.1-definition", "authenticated-source-order",
            ]
        confidence = "high" if start in pointer_references else "medium"
        if confidence == "high":
            evidence.append("stock-interface-module-or-callback-pointer")
        record = _record(image, symbol, module, start, end, confidence, evidence, origin)
        if start in pointer_references:
            record["pointer_references"] = pointer_references[start]
            record["thumb_pointer"] = f"0x{start | 1:08X}"
        records.append(record)

    _require((len(records), sum(row["bytes"] for row in records)) == (11, 1_132),
             "PSNames callable accounting drift")
    physical = []
    for start, end, category, digest in PHYSICAL:
        body = _slice(image, start, end)
        _require(_sha(body) == digest, "PSNames physical classification drift")
        physical.append({
            "start": f"0x{start:08X}", "end_exclusive": f"0x{end:08X}",
            "bytes": len(body), "body_sha256": digest, "category": category,
            "callable_code": False, "source_identity_claimed": False,
        })
    intervals = [
        (int(row["start"], 16), int(row["end_exclusive"], 16))
        for row in records + physical
    ]
    _require(_complement(intervals) == [],
             "PSNames envelope retains unclassified physical bytes")

    high = [row for row in records if row["confidence"] == "high"]
    medium = [row for row in records if row["confidence"] == "medium"]
    high_total = {"functions": len(high), "bytes": sum(row["bytes"] for row in high)}
    medium_total = {"functions": len(medium), "bytes": sum(row["bytes"] for row in medium)}
    _require(high_total == {"functions": 8, "bytes": 844},
             "PSNames high-confidence accounting drift")
    _require(medium_total == {"functions": 3, "bytes": 288},
             "PSNames medium-confidence accounting drift")
    mapping_sha = _canonical(records + physical)

    return {
        "schema_version": 1,
        "status": "fail-closed-psnames-function-map",
        "read_only": True,
        "selected_module": "psnames",
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
            "module_class": f"0x{MODULE_CLASS:08X}",
            "module_name_address": f"0x{MODULE_NAME:08X}",
            "module_interface": f"0x{INTERFACE:08X}",
            "next_foreign_callable": "0x005D9950",
            "next_foreign_provider": "SEGGER-RTT-6.18a",
            "freetype_version": "2.9.1", "freetype_commit": UPSTREAM_COMMIT,
        },
        "scope": {
            "start": f"0x{ENVELOPE[0]:08X}",
            "end_exclusive": f"0x{ENVELOPE[1]:08X}",
            "bytes": ENVELOPE[1] - ENVELOPE[0],
            "ghidra_recognized": {"functions": 7, "bytes": 1_010},
            "recovered_callable": {"functions": 4, "bytes": 122},
            "residual_physical": {
                "intervals": 1, "bytes": 36,
                "category_bytes": {"literal-pointer-pool": 36},
                "unclassified_bytes": 0, "unresolved_callable_bytes": 0,
            },
        },
        "confidence": {
            "exact": {"functions": 0, "bytes": 0,
                      "reason": "no original-compiler byte identity proof"},
            "high": high_total, "medium": medium_total,
            "mapped_total": {"functions": 11, "bytes": 1_132},
            "unresolved_code": {
                "functions": 0, "bytes": 0, "source_identities_complete": True,
            },
        },
        "movement": {
            "initial_retained_census": {"functions": 7, "bytes": 1_010},
            "recovered_outside_ghidra_relation": {"functions": 4, "bytes": 122},
            "newly_classified_physical": {"intervals": 1, "bytes": 36},
        },
        "mapping_sha256": mapping_sha,
        "records": {"psnames": records, "physical_classification": physical},
        "compiler_byte_identity_claimed": False,
        "binary_overlay_ready": False,
        "production_routed": False,
        "blockers": [
            "original compiler/version/options, ABI details, and LTO state are not recovered",
            "no authenticated stock callsite rewrite or target placement routes this source",
            "no authenticated external font payload or face-path configuration was supplied",
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
                 "checked-in PSNames function-map manifest drift")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
