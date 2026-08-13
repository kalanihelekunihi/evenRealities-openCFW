#!/usr/bin/env python3
"""Fail-closed review of Apollo source paths missed by Ghidra correlation.

This reads and authenticates the official image and the immutable 64-shard
corpus.  It does not alter either.  Recovery is deliberately limited to
reviewed function bounds with call/table evidence independent of path
adjacency; all other code-referenced paths remain candidates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import analyze_apollo_embedded_source_paths as baseline


EXPECTED_UNANCHORED = 43
EXPECTED_POINTER_CELLS = 46
EXPECTED_LITERAL_REFERENCES = 273
EXPECTED_UNANCHORED_PATHS_SHA256 = (
    "4f2cc94985e063733f6761bfb1aca31aa9774b08898fe4c6011cb5ec6accc2a7"
)

# Half-open, authenticated raw bounds.  Each entry has an independent inbound
# call or stored Thumb-pointer witness.  The adjacency-only 0x0043c450 body is
# intentionally excluded.  WsfTimerInit at 0x0052a474 is admitted by its
# direct initialization caller, not by adjacency to the timer cluster.
RECOVERED = {
    r"app\gui\AgingTest\aging_test.c": [
        (0x0043C400, 0x0043C450, "196c010e567f93022aaa4ceb88bd17e3f54e23d014b2f5577e901eb14b982819", [0x006A44B4], []),
        (0x0043C496, 0x0043C5F6, "40e792bff86aff637c37cec61f6c50849c6b7a985293c3fa186a49450e736af6", [0x006A44B8], []),
        (0x0043C5F6, 0x0043C6CE, "bbe50cd9dd87e83b9febc05bf41669ab4894e9592cdb01c75a40a2ee670ee49a", [], [0x0043C5C8, 0x0043C6DA]),
        (0x0043C6CE, 0x0043C758, "5e86a8180c8315576a3a0fd847536949b67aff772d98429e6f7f484c62918efb", [], [0x0043C5EC]),
    ],
    r"third_party\cordio\wsf\sources\port\freertos\wsf_timer.c": [
        (0x0052A474, 0x0052A4B8, "e5a91cf26e8c063a07fd7571bc0b4bb2f0fe4990c5e5f6aacb0069d0a43153fd", [], [0x004B7F6A]),
        (0x0052A51A, 0x0052A542, "482d2cf4e1ef251d51309b8b6235f691c618f037d30a2bf172b2e22f4cd86c4b", [], [0x0052A59A]),
        (0x0052A542, 0x0052A574, "30e6992250bdfe0b6bad728ae0a8f1b114fe7f435981e50d8ffd551fb113435f", [], [0x0052BA32]),
        (0x0052A574, 0x0052A614, "cf614de8167182c5bb63b000714586fda2b2f639abcd3793967a1ab871533d5e", [], [0x0052B9D4, 0x0052BA96]),
    ],
}


def _u16(blob: bytes, address: int) -> int:
    offset = address - baseline.LOAD_BASE
    if offset < 0 or offset + 2 > len(blob):
        raise baseline.AuditError(f"address outside image: 0x{address:08x}")
    return struct.unpack_from("<H", blob, offset)[0]


def _thumb_bl_target(blob: bytes, address: int) -> int | None:
    """Decode the immediate Thumb-2 BL form used by this image."""
    first, second = _u16(blob, address), _u16(blob, address + 2)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    s = (first >> 10) & 1
    j1, j2 = (second >> 13) & 1, (second >> 11) & 1
    i1, i2 = int(not (j1 ^ s)), int(not (j2 ^ s))
    value = (s << 24) | (i1 << 23) | (i2 << 22) | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    if value & (1 << 24):
        value -= 1 << 25
    return address + 4 + value


def literal_references(blob: bytes, cell: int) -> list[int]:
    """Return exact positive-offset Thumb LDR-literal references to *cell*."""
    found: set[int] = set()
    start = max(baseline.LOAD_BASE, cell - 4099)
    for address in range(start + (start & 1), cell, 2):
        first = _u16(blob, address)
        target = None
        if first & 0xF800 == 0x4800:  # 16-bit LDR Rt,[PC,#imm8*4]
            target = ((address + 4) & ~3) + ((first & 0xFF) << 2)
        elif first == 0xF8DF:  # 32-bit LDR.W Rt,[PC,#imm12]
            second = _u16(blob, address + 2)
            target = ((address + 4) & ~3) + (second & 0xFFF)
        if target == cell:
            found.add(address)
    return sorted(found)


def recover(image: Path, corpus_root: Path) -> dict[str, Any]:
    report = baseline.analyze(image, corpus_root)
    blob = image.read_bytes()
    unanchored = sorted(
        (record for record in report["paths"] if not record["function_references"]),
        key=lambda record: record["relative"],
    )
    digest = hashlib.sha256(
        ("\n".join(record["relative"] for record in unanchored) + "\n").encode()
    ).hexdigest()
    if len(unanchored) != EXPECTED_UNANCHORED or digest != EXPECTED_UNANCHORED_PATHS_SHA256:
        raise baseline.AuditError("baseline unanchored path set changed")
    if sum(len(record["pointer_cells"]) for record in unanchored) != EXPECTED_POINTER_CELLS:
        raise baseline.AuditError("unanchored pointer-cell census changed")

    classifications = []
    reference_count = 0
    recovered_entries: set[int] = set()
    for record in unanchored:
        references = {cell: literal_references(blob, cell) for cell in record["pointer_cells"]}
        if any(not sites for sites in references.values()):
            raise baseline.AuditError(f"path pointer cell has no Thumb literal reference: {record['relative']}")
        reference_count += sum(len(sites) for sites in references.values())
        functions = []
        for entry, end, expected_hash, pointer_witnesses, call_witnesses in RECOVERED.get(record["relative"], []):
            if entry in recovered_entries or not entry < end:
                raise baseline.AuditError("duplicate or invalid recovered function bounds")
            recovered_entries.add(entry)
            body = blob[entry - baseline.LOAD_BASE : end - baseline.LOAD_BASE]
            if hashlib.sha256(body).hexdigest() != expected_hash:
                raise baseline.AuditError(f"recovered body changed at 0x{entry:08x}")
            for cell in pointer_witnesses:
                offset = cell - baseline.LOAD_BASE
                if offset < 0 or offset + 4 > len(blob) or struct.unpack_from("<I", blob, offset)[0] != entry | 1:
                    raise baseline.AuditError(f"Thumb-pointer witness changed at 0x{cell:08x}")
            for call in call_witnesses:
                if _thumb_bl_target(blob, call) != entry:
                    raise baseline.AuditError(f"call witness changed at 0x{call:08x}")
            functions.append({
                "entry": entry,
                "end_exclusive": end,
                "size": end - entry,
                "sha256": expected_hash,
                "stored_thumb_pointer_cells": pointer_witnesses,
                "direct_call_sites": call_witnesses,
            })
        state = "recovered_function" if functions else "missed_code_candidate"
        classifications.append({
            "relative": record["relative"],
            "path_run": record["run"],
            "path_pointer_cells": record["pointer_cells"],
            "state": state,
            "literal_reference_sites": [site for sites in references.values() for site in sites],
            "recovered_functions": functions,
        })
    if reference_count != EXPECTED_LITERAL_REFERENCES or len(recovered_entries) != 8:
        raise baseline.AuditError("reviewed recovery census changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no hardware or flash operation",
        "image_sha256": report["image"]["sha256"],
        "corpus_sha256sums_sha256": report["ghidra_correlation"]["corpus"]["sha256sums_sha256"],
        "baseline": {"paths": 357, "function_anchored": 314, "unanchored": 43, "ghidra_functions": 7370},
        "recovery": {
            "state_counts": {
                "baseline_function_anchored_paths": 314,
                "confirmed_path_only_data": 0,
                "missed_code_candidate": 41,
                "recovered_function": 2,
            },
            "literal_pointer_cells": 46,
            "raw_thumb_ldr_decode_sites": reference_count,
            "recovered_functions": len(recovered_entries),
            "effective_function_count": 7370 + len(recovered_entries),
        },
        "limitations": [
            "the 273 halfword-aligned LDR decodes resolve exactly to retained path cells, but only the eight call/table-backed entries are promoted as recovered functions",
            "the other 41 paths remain missed-code candidates rather than proven function boundaries",
            "zero confirmed path-only-data records does not mean every raw decode site is independently proven reachable",
            "no recovered function is production-eligible until its private ABI, locking, caller, relocation, and behavior closure is complete",
        ],
        "paths": classifications,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=baseline.DEFAULT_IMAGE)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = recover(args.image, args.ghidra_corpus)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        recovery = result["recovery"]
        print("Apollo embedded source-path recovery")
        print(f"  baseline unanchored paths: {result['baseline']['unanchored']}")
        print(f"  raw Thumb LDR decode sites: {recovery['raw_thumb_ldr_decode_sites']}")
        print(f"  recovered paths/functions: {recovery['state_counts']['recovered_function']}/{recovery['recovered_functions']}")
        print(f"  missed-code candidates: {recovery['state_counts']['missed_code_candidate']}")
        print("  confirmed path-only data: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
