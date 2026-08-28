#!/usr/bin/env python3
"""Audit Apollo opacity wave 11's FreeType CFF source closure.

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
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
ADMISSION = G2 / "research/admission/apollo_opacity_wave11"
BOUNDARY = ADMISSION / "source_boundaries.tsv"
FRONTIER = ADMISSION / "reconciled_frontier.tsv"
INTERIORS = ADMISSION / "reconciled_interiors.tsv"
SHARED = ADMISSION / "shared_data.tsv"
ROOT = 0x005AF88C
LOAD_ADDRESS = 0x00438000
OTA_HEADER_BYTES = 32

CORPORA = (
    DECOMP / "bundles/apollo-decomp-01.c",
    DECOMP / "bundles/apollo-decomp-08.c",
    DECOMP / "bundles/apollo-decomp-09.c",
    DECOMP / "bundles/apollo-decomp-13.c",
)
SOURCES = {
    G2 / "third_party/freetype/src/base/ftcalc.c": (26_784, "4a0b3452e9b911f67c618a29775f4bcfa6367b9b6b3a1d2b3cf62c6113ce2e8b"),
    G2 / "third_party/freetype/src/base/ftobjs.c": (150_798, "9f5533b64c0e1926346bbabb1107a319801ca677b19b6f236ffd379456a6e24e"),
    G2 / "third_party/freetype/src/base/ftstream.c": (20_189, "45d3fa82ba502cdb7917a18ca9d26a46d5d6604ad56c691b4b7fd3e973b5cd43"),
    G2 / "third_party/freetype/src/cff/cffparse.c": (46_535, "c8818be29c81cafbdf6f395fea4918610701ac3168a67af8e6887c5145eef4fa"),
    G2 / "third_party/freetype/src/cff/cffload.c": (75_622, "f8ec69b219bfd0ced42da86e57448482d363d533934325fdeb287362f769b232"),
    G2 / "third_party/freetype/src/cff/cffobjs.c": (37_857, "5f36ebf06afbacda76cab4b4913ced754112fe1c35deb96276bd8c8f0cd73d7a"),
    G2 / "third_party/freetype/LICENSE": (6_743, "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1"),
}
PINS = {
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    IMAGE: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    CORPORA[0]: (407_422, "32d621ce69e32a5f10cb366221f2ad0b215a5574ec0a698ddf680c92b28e828d"),
    CORPORA[1]: (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    CORPORA[2]: (439_956, "03672a605bd92ceef591a0f4ca478d48960f71a76a1517cfe9a6fd4b2150b07f"),
    CORPORA[3]: (731_098, "2acd0f0f7b1c9f736f6df76ac0800a76c1ad4da71298322ebe4b63b035dcf703"),
    **SOURCES,
}


class WaveError(RuntimeError):
    """Raised when authenticated wave-11 evidence changes."""


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


def corpus_function(corpus: str, entry: int) -> str:
    match = re.search(rf"/\* FUN 0x{entry:08x} .*?(?=/\* FUN 0x|\Z)", corpus, re.S)
    if match is None:
        raise WaveError(f"0x{entry:08X}: corpus body missing")
    return match.group(0)


def residual_before() -> tuple[dict[int, dict[str, str]], set[int], dict[str, Any]]:
    wave10 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave10.py", "opacity_wave11_wave10")
    report10 = wave10.run_audit()
    if report10["after"] != {"functions": 1352, "bytes": 152498} or report10["largest_remaining"] != {"entry": "0x005AF88C", "envelope_bytes": 1912}:
        raise WaveError("wave-10 residual/root drift")
    wave9, _, wave8, waves, wave1, _, parent_rows = wave10.base_evidence()
    parent_none = {int(row["entry"], 16): row for row in parent_rows if row["bucket"] == "investigation-required-no-evidence"}
    residual = wave8.residual_before(wave1, waves, parent_none)
    residual -= {int(row["entry"], 16) for row in wave8.tsv_rows(wave8.BOUNDARY)}
    residual -= {int(row["entry"], 16) for row in wave8.tsv_rows(wave8.ZERO)}
    residual -= set(wave9.EXPECTED_SELECTED)
    residual -= set(wave10.EXPECTED_SELECTED)
    return parent_none, residual, report10


def run_audit() -> dict[str, Any]:
    parent_none, residual, report10 = residual_before()
    before = {"functions": len(residual), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual)}
    if before != report10["after"] or max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual) != (1912, ROOT):
        raise WaveError("authoritative residual drift")

    local = {path: pinned(path) for path in PINS}
    payload = local[IMAGE][OTA_HEADER_BYTES:]
    functions = {int(row["entry"], 16): row for row in (json.loads(line) for line in local[FUNCTIONS].decode().splitlines())}
    corpus = "\n".join(local[path].decode(errors="ignore") for path in CORPORA)
    rows = tsv_rows(BOUNDARY)
    selected = {int(row["entry"], 16) for row in rows}
    if len(rows) != 43 or ROOT not in selected or not selected <= residual:
        raise WaveError("selected closure membership drift")

    # Re-derive the complete residual-only static closure and minimum depth.
    derived = {ROOT}
    depth = {ROOT: 0}
    queue = deque([ROOT])
    while queue:
        owner = queue.popleft()
        for value in functions[owner]["callees"]:
            target = int(value, 16)
            if target in residual and target not in derived:
                derived.add(target)
                depth[target] = depth[owner] + 1
                queue.append(target)
    if derived != selected:
        raise WaveError(f"residual static closure drift: missing={derived-selected}, extra={selected-derived}")

    source_text = {str(path.relative_to(G2)): local[path].decode(errors="ignore") for path in SOURCES if path.name != "LICENSE"}
    records = []
    source_count = source_bytes = typed_count = typed_bytes = 0
    for row in rows:
        entry = int(row["entry"], 16)
        end = int(row["end_exclusive"], 16)
        envelope = int(row["envelope_bytes"])
        fn = functions[entry]
        ranges = tuple((int(a, 16), int(b, 16) + 1) for a, b in fn["ranges"])
        installed = payload[entry - LOAD_ADDRESS:end - LOAD_ADDRESS]
        parent = parent_none[entry]
        observed = (end, envelope, int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]))
        expected = (int(parent["body_end_exclusive"], 16), int(parent["official_opaque_bytes"]), int(fn["body_bytes"]), fn["body_sha256"], depth[entry])
        if observed != expected or len(ranges) != 1 or ranges[0] != (entry, end) or len(installed) != envelope or sha256(installed) != row["body_sha256"]:
            raise WaveError(f"0x{entry:08X}: body/range/depth drift: observed={observed}, expected={expected}, ranges={ranges}")
        body = corpus_function(corpus, entry)
        if fn["body_sha256"] not in body.splitlines()[0]:
            raise WaveError(f"0x{entry:08X}: corpus marker drift")
        is_source = row["disposition"] == "source-attributed-research-only"
        if is_source:
            path = row["source_path"].removeprefix("g2/")
            if row["provider_identity"] != "FreeType-2.9.1-VER-2-9-1" or row["license_status"] != "FTL" or row["symbol"] not in source_text[path]:
                raise WaveError(f"0x{entry:08X}: upstream source/license identity drift")
            source_count += 1
            source_bytes += envelope
        else:
            if (entry, row["symbol"], row["provider_identity"], row["license_status"], row["disposition"]) != (0x0044B610, "strncmp", "IAR-DLIB-proprietary-runtime", "unavailable", "typed-external-provider-unavailable"):
                raise WaveError("typed runtime boundary drift")
            typed_count += 1
            typed_bytes += envelope
        records.append(dict(row, source_identity_authenticated=is_source))
    root_body = corpus_function(corpus, ROOT)
    for token in ("postscript_cmaps", "psaux", "cff_load", "Regular", "Black"):
        if token not in root_body:
            raise WaveError(f"cff_face_init anchor missing: {token}")

    frontier = tsv_rows(FRONTIER)
    outbound = Counter()
    consumers: dict[int, set[int]] = {}
    for entry in selected:
        for value in functions[entry]["callees"]:
            target = int(value, 16)
            if target not in selected:
                outbound[target] += 1
                consumers.setdefault(target, set()).add(entry)
    if {int(row["entry"], 16): int(row["call_edges"]) for row in frontier} != dict(outbound):
        raise WaveError("terminal static frontier drift")
    if any(int(row["wave11_additional_function_bytes"]) for row in frontier):
        raise WaveError("frontier double counts function bytes")

    shared_rows = tsv_rows(SHARED)
    observed_dat: dict[int, tuple[str, set[int]]] = {}
    for entry in selected:
        body = corpus_function(corpus, entry)
        for symbol, value in re.findall(r"\b((?:PTR_|s_)?(?:DAT|s)_[A-Za-z0-9_]*?([0-9a-f]{8}))\b", body):
            address = int(value, 16)
            old = observed_dat.setdefault(address, (symbol, set()))
            if old[0] != symbol:
                raise WaveError(f"0x{address:08X}: ambiguous data symbol")
            old[1].add(entry)
    if {int(row["address"], 16) for row in shared_rows} != set(observed_dat):
        raise WaveError("direct data graph drift")
    for row in shared_rows:
        address = int(row["address"], 16)
        physical = payload[address - LOAD_ADDRESS:address - LOAD_ADDRESS + 4]
        symbol, owners = observed_dat[address]
        expected_consumers = ",".join(f"0x{entry:08X}" for entry in sorted(owners))
        value = struct.unpack("<I", physical)[0]
        observed = (int(row["size"]), row["bytes_hex"], row["sha256"], row["symbol"], row["value_or_target"], row["consumers"], int(row["wave11_additional_function_bytes"]))
        expected = (4, physical.hex(), sha256(physical), symbol, f"0x{value:08X}", expected_consumers, 0)
        if observed != expected:
            raise WaveError(f"0x{address:08X}: shared data drift")
    # Resolve the most diagnostic pointer targets, not just their pointer cells.
    expected_strings = {0x005B0004: b"pshinter", 0x005B00C8: b"sfnt", 0x005B00CC: b"postscript-cmaps", 0x005B00D0: b"psaux", 0x005B00D4: b"cff-load", 0x005B00E8: b"Regular", 0x005B00EC: b"Bold", 0x005B00F0: b"Black"}
    for cell, value in expected_strings.items():
        target = struct.unpack_from("<I", payload, cell - LOAD_ADDRESS)[0]
        actual = payload[target - LOAD_ADDRESS:target - LOAD_ADDRESS + len(value) + 1]
        if actual != value + b"\0":
            raise WaveError(f"0x{cell:08X}: diagnostic string target drift")

    interior = tsv_rows(INTERIORS)
    if interior != [{"scope": "complete-selected-closure", "functions": "43", "range_count_per_function": "1", "interior_islands": "0", "interior_physical_bytes": "0", "wave11_additional_function_bytes": "0"}]:
        raise WaveError("interior reconciliation drift")

    selected_bytes = sum(int(parent_none[e]["official_opaque_bytes"]) for e in selected)
    if selected_bytes != 10098 or source_count != 42 or source_bytes != 10056 or (typed_count, typed_bytes) != (1, 42):
        raise WaveError("source/typed byte partition drift")
    remaining = residual - selected
    after = {"functions": len(remaining), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in remaining)}
    largest_bytes, largest_entry = max((int(parent_none[e]["official_opaque_bytes"]), e) for e in remaining)
    if after != {"functions": 1309, "bytes": 142400} or (largest_entry, largest_bytes) != (0x004BFED6, 1902):
        raise WaveError("after residual drift")

    canonical = [{key: row[key] for key in ("entry", "symbol", "source_path", "provider_identity", "license_status", "disposition", "body_sha256")} for row in sorted(rows, key=lambda item: int(item["entry"], 16))]
    return {
        "status": "opacity-wave11-freetype-cff-source-closure",
        "wave10_residual": report10["after"],
        "before": before,
        "selected_root_range": {"start": "0x005AF88C", "end_exclusive": "0x005B0004"},
        "actionable_graph": {"positive_functions": 43, "positive_bytes": selected_bytes, "closure_depth_max": max(depth.values()), "terminal_functions": len(frontier), "terminal_edges": sum(outbound.values())},
        "range_partition": {"functions": 43, "contiguous_functions": 43, "interior_islands": 0, "interior_physical_bytes": 0},
        "source_attributed": {"functions": source_count, "bytes": source_bytes, "provider": "FreeType-2.9.1-VER-2-9-1", "license": "FTL"},
        "typed_unavailable": {"functions": typed_count, "bytes": typed_bytes, "provider": "IAR-DLIB-proprietary-runtime"},
        "shared_data": {"direct_cells": len(shared_rows), "physical_bytes": 4 * len(shared_rows), "diagnostic_pointer_targets": len(expected_strings), "additional_function_bytes": 0},
        "after": after,
        "largest_remaining": {"entry": f"0x{largest_entry:08X}", "envelope_bytes": largest_bytes},
        "records": records,
        "frontier_records": frontier,
        "mapping_sha256": sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()),
        "production_routed": False,
        "production_blocker": "missing exact ABI/config plus reviewed dual-profile Cortex-M55 codegen, relocation, link-order, and placement proof",
        "read_only": True,
        "hardware_operations": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
