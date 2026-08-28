#!/usr/bin/env python3
"""Audit the closure-hop-2 tranche of the corrected Apollo 0x5D census.

The census edge class is only a reachability hypothesis.  Authenticated body
semantics, exact function order, ABI layouts, and FreeType error constants
identify most of this tranche as the vendored Adobe CFF implementation.  The
rest remains a typed, fail-closed external boundary.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CENSUS = ROOT / "tools/manifests/g2-cordio-ll-sea-census.tsv"
GHIDRA_LOG = ROOT / "research/corpus/apollo-main/ghidra/full64-j64-auth/logs/apollo-30.log"
CANDIDATE = ROOT / "research/candidates/cordio_ll_sea_hop2/runtime_cordio_ll_sea_hop2_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
PSAUX = ROOT / "third_party/freetype/src/psaux"

FILE_PINS = {
    IMAGE: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    CENSUS: (61_831, "84d4e94b8a4f85b46c426b89379cc21c07b247f488aa14fdf5b0c3298f4712e6"),
    GHIDRA_LOG: (399_186, "6ce2cec7688130ec2fe32ed33d7eb68097c3508d527f2e2f9389827496d44b4c"),
    PSAUX / "psobjs.c": (75_816, "6054c46ea381596e3eec22f0c13f8aaff8a6390fa33bad619dadaae7c0cf578e"),
    PSAUX / "psarrst.c": (7_501, "6bf2ad6c0562003b5f4c81193f64a6a25a10a25eafe9c837aa70773917eaa957"),
    PSAUX / "psft.c": (26_591, "20c152003634042eee20ffa17ab4a1280743bd6f9117725aee5534662a1a9e3f"),
    PSAUX / "psintrp.c": (106_309, "b4b467017145c4d29b2563bd623dd1e7d2372cfa214301e52b8dfeb6d66b3d2d"),
    PSAUX / "psread.c": (4_438, "3ac1fd966968d0747f05838d440dcecdacaecc7d4e0c29a656e49e613ed53873"),
    PSAUX / "psstack.c": (10_015, "74949d248614ab126214895be3eb0ec738ba162db7dc9217b0238e878e2763de"),
}
LOAD_BASE = 0x00437FE0

# Exact source identities, established by authenticated body semantics and
# ordered-family alignment.  Values are (upstream module, upstream function).
SOURCE_IDENTITIES = {
    0x005D1D1C: ("psobjs.c", "cff_random"),
    0x005D22F2: ("psarrst.c", "cf2_arrstack_init"),
    0x005D230E: ("psarrst.c", "cf2_arrstack_finalize"),
    0x005D2390: ("psarrst.c", "cf2_arrstack_setCount"),
    0x005D23AC: ("psarrst.c", "cf2_arrstack_clear"),
    0x005D23B2: ("psarrst.c", "cf2_arrstack_size"),
    0x005D23B6: ("psarrst.c", "cf2_arrstack_getBuffer"),
    0x005D23BA: ("psarrst.c", "cf2_arrstack_getPointer"),
    0x005D2EA8: ("psft.c", "cf2_checkTransform"),
    0x005D2EE4: ("psft.c", "cf2_setGlyphWidth"),
    0x005D2FEE: ("psft.c", "cf2_outline_init"),
    0x005D3018: ("psft.c", "cf2_getScaleAndHintFlag"),
    0x005D3060: ("psft.c", "cf2_getUnitsPerEm"),
    0x005D3248: ("psft.c", "cf2_getMaxstack"),
    0x005D328A: ("psft.c", "cf2_getBlueMetrics"),
    0x005D32C0: ("psft.c", "cf2_getBlueValues"),
    0x005D32D4: ("psft.c", "cf2_getOtherBlues"),
    0x005D32E8: ("psft.c", "cf2_getFamilyBlues"),
    0x005D32FE: ("psft.c", "cf2_getFamilyOtherBlues"),
    0x005D3314: ("psft.c", "cf2_getLanguageGroup"),
    0x005D331E: ("psft.c", "cf2_initGlobalRegionBuffer"),
    0x005D3362: ("psft.c", "cf2_getSeacComponent"),
    0x005D33BE: ("psft.c", "cf2_freeSeacComponent"),
    0x005D33D4: ("psft.c", "cf2_getT1SeacComponent"),
    0x005D3434: ("psft.c", "cf2_freeT1SeacComponent"),
    0x005D3466: ("psft.c", "cf2_initLocalRegionBuffer"),
    0x005D34F4: ("psft.c", "cf2_getDefaultWidthX"),
    0x005D3500: ("psft.c", "cf2_getNominalWidthX"),
    0x005D4AFE: ("psintrp.c", "cf2_hintmask_init"),
    0x005D4B14: ("psintrp.c", "cf2_hintmask_isValid"),
    0x005D4B4C: ("psintrp.c", "cf2_hintmask_read"),
    0x005D6D98: ("psread.c", "cf2_buf_readByte"),
    0x005D6DB8: ("psread.c", "cf2_buf_isEnd"),
    0x005D6DCA: ("psstack.c", "cf2_stack_init"),
    0x005D6E22: ("psstack.c", "cf2_stack_free"),
    0x005D6E44: ("psstack.c", "cf2_stack_count"),
    0x005D6E50: ("psstack.c", "cf2_stack_pushInt"),
    0x005D6E7C: ("psstack.c", "cf2_stack_pushFixed"),
    0x005D6EA8: ("psstack.c", "cf2_stack_popInt"),
    0x005D6EE0: ("psstack.c", "cf2_stack_popFixed"),
    0x005D6F38: ("psstack.c", "cf2_stack_getReal"),
    0x005D6F9E: ("psstack.c", "cf2_stack_setReal"),
    0x005D6FCC: ("psstack.c", "cf2_stack_pop"),
    0x005D6FF2: ("psstack.c", "cf2_stack_roll"),
    0x005D709C: ("psstack.c", "cf2_stack_clear"),
}

FAMILY_ORDER = {
    "psarrst.c": [
        "cf2_arrstack_init", "cf2_arrstack_finalize", "cf2_arrstack_setCount",
        "cf2_arrstack_clear", "cf2_arrstack_size", "cf2_arrstack_getBuffer",
        "cf2_arrstack_getPointer",
    ],
    "psft.c": [
        "cf2_checkTransform", "cf2_setGlyphWidth", "cf2_outline_init",
        "cf2_getScaleAndHintFlag", "cf2_getUnitsPerEm", "cf2_getMaxstack",
        "cf2_getBlueMetrics", "cf2_getBlueValues", "cf2_getOtherBlues",
        "cf2_getFamilyBlues", "cf2_getFamilyOtherBlues", "cf2_getLanguageGroup",
        "cf2_initGlobalRegionBuffer", "cf2_getSeacComponent",
        "cf2_freeSeacComponent", "cf2_getT1SeacComponent",
        "cf2_freeT1SeacComponent", "cf2_initLocalRegionBuffer",
        "cf2_getDefaultWidthX", "cf2_getNominalWidthX",
    ],
    "psintrp.c": ["cf2_hintmask_init", "cf2_hintmask_isValid", "cf2_hintmask_read"],
    "psread.c": ["cf2_buf_readByte", "cf2_buf_isEnd"],
    "psstack.c": [
        "cf2_stack_init", "cf2_stack_free", "cf2_stack_count",
        "cf2_stack_pushInt", "cf2_stack_pushFixed", "cf2_stack_popInt",
        "cf2_stack_popFixed", "cf2_stack_getReal", "cf2_stack_setReal",
        "cf2_stack_pop", "cf2_stack_roll", "cf2_stack_clear",
    ],
}

# These mechanically distinctive tokens guard the semantic anchors for each
# ordered source family.  Source-order alignment closes the intervening leaves.
DECOMP_SIGNATURES = {
    0x005D1D1C: ("param_1 ^ param_1 << 0xd", "param_1 >> 0x11", "param_1 << 5"),
    0x005D22F2: ("param_1[4] = 10", "param_1[7] = 0"),
    0x005D23BA: ("param_1 + 0x14", "param_1 + 8", "* param_2", "0x82"),
    0x005D2EA8: ("0x7d00000", "param_2 << 0x10", "0xa4"),
    0x005D2FEE: ("param_1,0x20,0", "DAT_005d3228", "DAT_005d3230"),
    0x005D328A: ("0x3e80000", "+ 0x180", "+ 0x188"),
    0x005D331E: ("param_1 + 0x238", "param_1 + 0x230", "param_1 + 0x240", "0x10,0"),
    0x005D3466: ("FUN_005d3466",),
    0x005D4AFE: ("param_1,0x1c,0", "*param_1 = param_2"),
    0x005D4B4C: ("FUN_005d6d98", "param_1 + uVar3 + 0x10"),
    0x005D6D98: ("param_1[3] < (uint)param_1[2]", "0x55"),
    0x005D6DCA: ("param_1,0x14", "param_1,8", "puVar1[4] = param_3"),
    0x005D6EA8: ("0xa1", "== '\\x02'", "+ -8"),
    0x005D6FF2: ("param_3 / (int)param_2", "iVar3 < (int)param_2", "+ iVar9 * 8", "+ iVar10 * 8"),
    0x005D709C: ("param_1 + 0xc", "param_1 + 8"),
}

BEGIN_RE = re.compile(r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+)", re.I)
END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)", re.I)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path) -> bytes:
    data = path.read_bytes()
    actual = len(data), sha256(data)
    if actual != FILE_PINS[path]:
        raise AuditError(f"{path}: identity drift: {actual} != {FILE_PINS[path]}")
    return data


def parse_census(text: str) -> dict[int, dict[str, str]]:
    lines = [line for line in text.splitlines() if line and not line.startswith("#")]
    return {int(row["entry"], 16): row for row in csv.DictReader(lines, delimiter="\t")}


def parse_decompilations(text: str) -> dict[int, str]:
    result: dict[int, str] = {}
    current: int | None = None
    lines: list[str] = []
    for line in text.splitlines():
        begin = BEGIN_RE.search(line)
        if begin:
            current = int(begin.group(1), 16)
            lines = [line]
            continue
        if current is not None:
            lines.append(line)
            end = END_RE.search(line)
            if end:
                if int(end.group(1), 16) != current:
                    raise AuditError("unbalanced Ghidra function markers")
                result[current] = "\n".join(lines)
                current = None
    if current is not None:
        raise AuditError("unterminated Ghidra function")
    return result


def definition_offset(source: str, function: str) -> int:
    match = re.search(rf"(?m)^  {re.escape(function)}\s*\(", source)
    if match is None:
        raise AuditError(f"upstream definition missing: {function}")
    return match.start()


def run_audit() -> dict[str, Any]:
    inputs = {path: authenticate(path) for path in FILE_PINS}
    image = inputs[IMAGE]
    census = parse_census(inputs[CENSUS].decode("utf-8"))
    decomp = parse_decompilations(inputs[GHIDRA_LOG].decode("utf-8"))
    candidate = CANDIDATE.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    combined = candidate + "\n" + header
    if combined.count("SPDX-License-Identifier: Apache-2.0") != 2:
        raise AuditError("adapter must retain both Apache-2.0 declarations")
    if "neither copies nor relicenses" not in candidate:
        raise AuditError("upstream license boundary statement missing")

    hop2 = {
        address: row for address, row in census.items()
        if row["evidence"] == "cordio-closure-hop-2" and row["hop"] == "2"
    }
    if len(hop2) != 59 or sum(int(row["official_opaque_bytes"]) for row in hop2.values()) != 5_006:
        raise AuditError("closure-hop-2 census partition drift")
    if not set(SOURCE_IDENTITIES).issubset(hop2):
        raise AuditError("source identity outside hop-2 partition")

    # Confirm definitions and their family order in the pinned upstream files.
    for module, functions in FAMILY_ORDER.items():
        source = inputs[PSAUX / module].decode("utf-8")
        if "FreeType Project License" not in source or "Adobe Systems Incorporated" not in source:
            raise AuditError(f"{module}: retained upstream license header missing")
        offsets = [definition_offset(source, function) for function in functions]
        if offsets != sorted(offsets) or len(offsets) != len(set(offsets)):
            raise AuditError(f"{module}: ordered source identity drift")
    psobjs = inputs[PSAUX / "psobjs.c"].decode("utf-8")
    definition_offset(psobjs, "cff_random")

    for address, tokens in DECOMP_SIGNATURES.items():
        body = decomp.get(address, "")
        if any(token not in body for token in tokens):
            raise AuditError(f"0x{address:08x}: semantic signature drift")

    records: dict[str, Any] = {}
    source_bytes = external_bytes = 0
    for address, row in sorted(hop2.items()):
        end = int(row["body_end_exclusive"], 16)
        size = int(row["official_opaque_bytes"])
        body = image[address - LOAD_BASE:end - LOAD_BASE]
        if len(body) != size:
            raise AuditError(f"0x{address:08x}: image range drift")
        address_literal = f"0x{address:08X}u"
        if len(re.findall(rf"\{{ {address_literal},", candidate)) != 1:
            raise AuditError(f"0x{address:08x}: adapter evidence row missing or duplicated")
        identity = SOURCE_IDENTITIES.get(address)
        if identity is None:
            disposition = "typed_external"
            external_bytes += size
            if not re.search(rf"\{{ {address_literal},[^\n]+ EXT \}}", candidate):
                raise AuditError(f"0x{address:08x}: external row is not fail-closed")
            module = function = license_name = None
        else:
            disposition = "upstream_freetype_source"
            source_bytes += size
            module, function = identity
            license_name = "FreeType Project License plus retained Adobe patent grant"
            if f'FT("{module}", "{function}")' not in candidate:
                raise AuditError(f"0x{address:08x}: source adapter identity missing")
        records[f"0x{address:08X}"] = {
            "end_exclusive": end,
            "bytes": size,
            "sha256": sha256(body),
            "disposition": disposition,
            "upstream_module": module,
            "upstream_function": function,
            "upstream_license": license_name,
        }

    if (len(SOURCE_IDENTITIES), source_bytes, 59 - len(SOURCE_IDENTITIES), external_bytes) != (45, 1_844, 14, 3_162):
        raise AuditError("hop-2 source/external partition drift")
    return {
        "status": "candidate-qualified-hop2",
        "read_only": True,
        "hardware_operations": False,
        "topology_correction": {
            "census_label": "Cordio/LL closure hop 2",
            "per_function_owner": "FreeType Adobe CFF engine where positively identified",
            "lvgl_attribution": False,
            "reason": "census call edges did not distinguish address-like data references from calls",
        },
        "hop2_tranche": {
            "functions": 59,
            "bytes": 5_006,
            "upstream_freetype_source": {"functions": 45, "bytes": source_bytes},
            "typed_external": {"functions": 14, "bytes": external_bytes},
            "records": records,
        },
        "unsupported_remainder": {
            "before": {"functions": 288, "bytes": 43_446},
            "source_recovered": {"functions": 45, "bytes": 1_844},
            "after": {"functions": 243, "bytes": 41_602},
            "after_unselected_only": {"functions": 229, "bytes": 38_440},
            "selected_typed_external": {"functions": 14, "bytes": 3_162},
        },
        "adapter": {
            "license": "Apache-2.0",
            "upstream_implementation_license_retained": True,
            "source": str(CANDIDATE.relative_to(ROOT)),
            "header": str(HEADER.relative_to(ROOT)),
            "production_routed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    result = run_audit()
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
