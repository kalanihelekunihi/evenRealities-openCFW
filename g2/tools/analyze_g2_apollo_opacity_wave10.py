#!/usr/bin/env python3
"""Close Apollo opacity wave 10 and distinguish MVE callother artifacts.

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
from collections import Counter
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
DECOMP = G2 / "research/corpus/apollo-main/ghidra/decomp"
CORPUS = DECOMP / "bundles/apollo-decomp-08.c"
FUNCTIONS = DECOMP / "functions.jsonl"
NEMA = G2 / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
ADMISSION = G2 / "research/admission/apollo_opacity_wave10"
BOUNDARY = ADMISSION / "typed_boundaries.tsv"
FRONTIER = ADMISSION / "reconciled_frontier.tsv"
INTERIORS = ADMISSION / "reconciled_interiors.tsv"
SHARED = ADMISSION / "shared_data.tsv"
CALLOTHER = ADMISSION / "reconciled_callother.tsv"
ROOT = 0x0051B140
LOAD_ADDRESS = 0x00438000

PINS = {
    CORPUS: (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    NEMA: (24_898, "5a8e427ae337afb78f2901e74ae48d08d8c222944a50ada8adadfbdd98296bfa"),
}
EXPECTED_SELECTED = {
    ROOT: (0x0051B8EA, 1962, 1958, "fa9bcce3b5a20a109a535ad6a1bdcc439e2bfa78c36e8e5aeaef145c1ae5af8c", 0, "round-stroke-join-fan-tessellation-coordinator"),
}
EXPECTED_RANGES = ((0x0051B140, 0x0051B4EC), (0x0051B4F0, 0x0051B8EA))
EXPECTED_CALLS = {
    0x0052266E: 8,
    0x005226B2: 1,
    0x00522A24: 1,
    0x00522F1C: 4,
    0x00523A34: 4,
    0x0052405C: 4,
    0x00524130: 4,
}
EXPECTED_BL_SITES = {
    0x0051B1DA: 0x00522F1C, 0x0051B1FA: 0x00524130, 0x0051B206: 0x0052405C,
    0x0051B338: 0x0052266E, 0x0051B344: 0x00523A34, 0x0051B364: 0x0052266E,
    0x0051B36A: 0x00522F1C, 0x0051B38A: 0x00524130, 0x0051B396: 0x0052405C,
    0x0051B4C8: 0x0052266E, 0x0051B4D4: 0x00523A34, 0x0051B4F8: 0x0052266E,
    0x0051B548: 0x00522F1C, 0x0051B568: 0x00524130, 0x0051B574: 0x0052405C,
    0x0051B6A8: 0x0052266E, 0x0051B6B4: 0x00523A34, 0x0051B6D4: 0x0052266E,
    0x0051B71E: 0x00522F1C, 0x0051B73E: 0x00524130, 0x0051B74A: 0x0052405C,
    0x0051B87C: 0x0052266E, 0x0051B888: 0x00523A34, 0x0051B8A8: 0x0052266E,
    0x0051B8D6: 0x00522A24, 0x0051B8DC: 0x005226B2,
}
EXPECTED_DAT = {0x0051B4EC: 2, 0x0051B8EC: 2, 0x0051BF74: 2}
EXPECTED_FRONTIER = {
    0x0052266E: ("command-state-mask-helper", "apollo-opacity-wave2", 8),
    0x005226B2: ("state-leaf", "apollo-opacity-wave1", 1),
    0x00522A24: ("six-coordinate-command-record-builder", "apollo-opacity-wave6", 1),
    0x00522F1C: ("tessellation-segment-count-clamp-align-helper", "apollo-opacity-wave6", 4),
    0x00523A34: ("guarded-polyline-record-entry", "apollo-opacity-wave6", 4),
    0x0052405C: ("periodic-trigonometric-polynomial-helper-a", "apollo-opacity-wave6", 4),
    0x00524130: ("periodic-trigonometric-polynomial-helper-b", "apollo-opacity-wave6", 4),
}
EXPECTED_INTERIORS = {
    0x0051B4EC: (0x0051B4F0, "00003443", "21b9ff9cf99927e92d16d0fcc3190c14680a24c02dad89f9777d5107fdeb5db1", 0x0051B140, "0x0051B4EC", "angle-step-float-180", "0x0051B140"),
}
EXPECTED_SHARED = {
    0x0051B8EA: (0x0051B8F0, "000000003443", "ddb3603acdcf098ea7bf86c995adfb80dcf58626a73fbd1d64b37fefa83998cf", "0x0051B8EC", "thumb-zero-padding-plus-angle-step-float-180", "0x0051B140"),
    0x0051BF74: (0x0051BF78, "044f0720", "48b4654f2567d2b59ecbe37e6f96190282388ca5bbd42e18a0f7bae12fc58b2d", "0x0051BF74", "shared-command-context-pointer-0x20074f04", "0x0051B140,0x0051B8F0"),
}
EXPECTED_CALLOTHER = {
    0x00D2A29C, 0x00D2A3C4, 0x00D2A42C, 0x00D2A554,
    0x00D2A60C, 0x00D2A734, 0x00D2A7E0, 0x00D2A908,
    0x00D6926C, 0x00D693FC, 0x00D695DC, 0x00D697B0,
    0x01169320, 0x011694B0, 0x01169690, 0x01169864,
}


class WaveError(RuntimeError):
    """Raised when authenticated wave-10 evidence changes."""


_BASE_CACHE: tuple[Any, dict[str, Any], Any, dict[int, Any], Any, dict[Path, bytes], list[dict[str, str]]] | None = None


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


def corpus_function(corpus: str, entry: int) -> tuple[str, int, str]:
    marker = re.search(rf"/\* FUN 0x{entry:08x} .*? bytes=(\d+) sha256=([0-9a-f]{{64}}) \*/", corpus)
    if marker is None:
        raise WaveError(f"0x{entry:08X}: corpus marker missing")
    end = corpus.find("/* FUN 0x", marker.end())
    if end < 0:
        end = len(corpus)
    return corpus[marker.start():end], int(marker.group(1)), marker.group(2)


def wide_branch_target(address: int, first: int, second: int, *, link: bool) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = sign << 24 | (1 ^ (j1 ^ sign)) << 23 | (1 ^ (j2 ^ sign)) << 22 | (first & 0x03FF) << 12 | (second & 0x07FF) << 1
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def base_evidence() -> tuple[Any, dict[str, Any], Any, dict[int, Any], Any, dict[Path, bytes], list[dict[str, str]]]:
    global _BASE_CACHE
    if _BASE_CACHE is not None:
        return _BASE_CACHE
    wave9 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave9.py", "opacity_wave10_wave9")
    wave9_report = wave9.run_audit()
    if wave9_report["after"] != {"functions": 1353, "bytes": 154460} or wave9_report["largest_remaining"] != {"entry": "0x0051B140", "envelope_bytes": 1962}:
        raise WaveError("wave-9 residual/root drift")
    wave8, _, waves, wave1, inherited, parent_rows = wave9.base_evidence()
    _BASE_CACHE = (wave9, wave9_report, wave8, waves, wave1, inherited, parent_rows)
    return _BASE_CACHE


def run_audit() -> dict[str, Any]:
    wave9, wave9_report, wave8, waves, wave1, inherited, parent_rows = base_evidence()
    parent_by_entry = {int(row["entry"], 16): row for row in parent_rows}
    parent_none = {entry: row for entry, row in parent_by_entry.items() if row["bucket"] == "investigation-required-no-evidence"}
    residual = wave8.residual_before(wave1, waves, parent_none)
    residual -= {int(row["entry"], 16) for row in wave8.tsv_rows(wave8.BOUNDARY)}
    residual -= {int(row["entry"], 16) for row in wave8.tsv_rows(wave8.ZERO)}
    residual -= set(wave9.EXPECTED_SELECTED)
    before = {"functions": len(residual), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual)}
    if before != wave9_report["after"] or max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual) != (1962, ROOT):
        raise WaveError(f"authoritative residual drift: {before}")

    local = {path: pinned(path) for path in PINS}
    corpus = local[CORPUS].decode()
    function_rows = [json.loads(line) for line in local[FUNCTIONS].decode().splitlines()]
    functions = {int(row["entry"], 16): row for row in function_rows}
    payload = inherited[wave1.IMAGE][wave1.OTA_HEADER_BYTES:]
    rows = tsv_rows(BOUNDARY)
    if {int(row["entry"], 16) for row in rows} != {ROOT} or ROOT not in residual:
        raise WaveError("selected actionable closure drift")
    row = rows[0]
    end, envelope, corpus_bytes, digest, depth, role = EXPECTED_SELECTED[ROOT]
    static = (int(row["end_exclusive"], 16), int(row["envelope_bytes"]), int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]), row["role"], row["provider_identity"], row["license_status"], row["disposition"])
    if static != (end, envelope, corpus_bytes, digest, depth, role, "unresolved-linked-vector-path-provider", "unavailable", "typed-external-provider-unavailable"):
        raise WaveError("typed boundary drift")
    parent = parent_none[ROOT]
    body, decoded_bytes, corpus_digest = corpus_function(corpus, ROOT)
    installed = payload[ROOT - LOAD_ADDRESS:end - LOAD_ADDRESS]
    ranges = tuple((int(start, 16), int(end_i, 16) + 1) for start, end_i in functions[ROOT]["ranges"])
    if int(parent["body_end_exclusive"], 16) != end or int(parent["official_opaque_bytes"]) != envelope:
        raise WaveError("parent envelope drift")
    if (decoded_bytes, corpus_digest, functions[ROOT]["body_sha256"], ranges) != (corpus_bytes, digest, digest, EXPECTED_RANGES):
        raise WaveError("corpus/range identity drift")
    if len(installed) != envelope or sha256(installed) != digest:
        raise WaveError("installed body identity drift")

    observed_calls = dict(Counter(int(value, 16) for value in re.findall(r"\bFUN_([0-9a-f]{8})\(", body)))
    observed_calls.pop(ROOT, None)
    if observed_calls != EXPECTED_CALLS or set(functions[ROOT]["callees"]) != {f"{entry:08x}" for entry in EXPECTED_CALLS}:
        raise WaveError(f"decompiler real-call topology drift: {observed_calls}")
    bl_sites: dict[int, int] = {}
    bw_sites: dict[int, int] = {}
    register_blx_sites = []
    for offset in range(0, len(installed) - 3, 2):
        address = ROOT + offset
        first, second = struct.unpack_from("<HH", installed, offset)
        for link, target_map in ((True, bl_sites), (False, bw_sites)):
            target = wide_branch_target(address, first, second, link=link)
            if target is not None:
                target_map[address] = target
    for offset in range(0, len(installed) - 1, 2):
        halfword = struct.unpack_from("<H", installed, offset)[0]
        if halfword & 0xFF80 == 0x4780:
            register_blx_sites.append(ROOT + offset)
    if bl_sites != EXPECTED_BL_SITES or bw_sites or register_blx_sites or dict(Counter(bl_sites.values())) != EXPECTED_CALLS:
        raise WaveError("installed Thumb branch closure drift")

    pseudo = Counter(int(value, 16) for value in re.findall(r"\bfunc_0x([0-9a-f]{8})\(", body))
    callother_rows = tsv_rows(CALLOTHER)
    if set(pseudo) != EXPECTED_CALLOTHER or any(count != 1 for count in pseudo.values()) or {int(row["pseudo_identifier"], 16) for row in callother_rows} != EXPECTED_CALLOTHER:
        raise WaveError("Ghidra callother membership drift")
    callother_records = []
    for artifact in callother_rows:
        entry = int(artifact["pseudo_identifier"], 16)
        observed = (int(artifact["occurrences"]), int(artifact["machine_branch_sites"]), artifact["classification"], artifact["disposition"], int(artifact["wave10_additional_function_bytes"]))
        if observed != (1, 0, "ghidra-callother-artifact", "not-a-static-call-boundary", 0) or entry in bl_sites.values():
            raise WaveError(f"0x{entry:08X}: callother reconciliation drift")
        callother_records.append(dict(artifact))

    frontier_rows = tsv_rows(FRONTIER)
    if {int(frontier["entry"], 16) for frontier in frontier_rows} != set(EXPECTED_FRONTIER):
        raise WaveError("terminal frontier membership drift")
    prior_modules = {1: waves[1], 2: waves[2], 6: load_module(G2 / "tools/analyze_g2_apollo_opacity_wave6.py", "opacity_wave10_wave6")}
    prior_sets = {f"apollo-opacity-wave{number}": set(module.EXPECTED_SELECTED) for number, module in prior_modules.items()}
    frontier_records = []
    for frontier in frontier_rows:
        entry = int(frontier["entry"], 16)
        expected_role, owner, sites = EXPECTED_FRONTIER[entry]
        observed = (frontier["classification"], frontier["role"], frontier["source_wave"], frontier["provider_identity"], frontier["license_status"], frontier["disposition"], int(frontier["call_sites"]), int(frontier["wave10_additional_function_bytes"]))
        if observed != ("prior-typed", expected_role, owner, "unresolved-linked-vector-path-provider", "unavailable", "prior-typed-external-provider-unavailable", sites, 0) or entry not in prior_sets[owner]:
            raise WaveError(f"0x{entry:08X}: prior frontier drift")
        frontier_records.append(dict(frontier))
    if set(observed_calls) != set(EXPECTED_FRONTIER) or set(observed_calls) & residual:
        raise WaveError("real terminal frontier is not exhaustive")

    dat = dict(Counter(int(value, 16) for value in re.findall(r"\bDAT_([0-9a-f]{8})", body)))
    if dat != EXPECTED_DAT:
        raise WaveError(f"direct data graph drift: {dat}")
    interior_rows = tsv_rows(INTERIORS)
    if {int(value["start"], 16) for value in interior_rows} != set(EXPECTED_INTERIORS):
        raise WaveError("interior membership drift")
    interior_records = []
    for interior in interior_rows:
        start = int(interior["start"], 16)
        stop, bytes_hex, data_digest, owner, data_address, kind, consumers = EXPECTED_INTERIORS[start]
        physical = payload[start - LOAD_ADDRESS:stop - LOAD_ADDRESS]
        observed = (int(interior["end_exclusive"], 16), int(interior["size"]), interior["bytes_hex"], interior["sha256"], int(interior["envelope_owner"], 16), interior["data_address"], interior["kind"], interior["consumers"], int(interior["wave10_additional_bytes"]))
        if observed != (stop, stop - start, bytes_hex, data_digest, owner, data_address, kind, consumers, 0) or physical.hex() != bytes_hex or sha256(physical) != data_digest:
            raise WaveError("interior physical evidence drift")
        interior_records.append(dict(interior))
    derived_gaps = {(previous_end, next_start, ROOT) for (_, previous_end), (next_start, _) in zip(ranges, ranges[1:])}
    table_gaps = {(int(value["start"], 16), int(value["end_exclusive"], 16), int(value["envelope_owner"], 16)) for value in interior_rows}
    if derived_gaps != table_gaps or sum(stop - start for start, stop, _ in table_gaps) != 4:
        raise WaveError("interior range-gap partition drift")

    shared_rows = tsv_rows(SHARED)
    if {int(value["start"], 16) for value in shared_rows} != set(EXPECTED_SHARED):
        raise WaveError("shared-data membership drift")
    shared_records = []
    for shared in shared_rows:
        start = int(shared["start"], 16)
        stop, bytes_hex, data_digest, addresses, kind, consumers = EXPECTED_SHARED[start]
        physical = payload[start - LOAD_ADDRESS:stop - LOAD_ADDRESS]
        observed = (int(shared["end_exclusive"], 16), int(shared["size"]), shared["bytes_hex"], shared["sha256"], shared["data_addresses"], shared["kind"], shared["consumers"], int(shared["wave10_additional_function_bytes"]))
        if observed != (stop, stop - start, bytes_hex, data_digest, addresses, kind, consumers, 0) or physical.hex() != bytes_hex or sha256(physical) != data_digest:
            raise WaveError(f"0x{start:08X}: shared physical evidence drift")
        shared_records.append(dict(shared))
    if int(parent_none[0x0051B8F0]["body_start"], 16) != 0x0051B8F0 or EXPECTED_SELECTED[ROOT][0] != 0x0051B8EA:
        raise WaveError("post-envelope census gap drift")
    next_body, _, _ = corpus_function(corpus, 0x0051B8F0)
    if next_body.count("DAT_0051bf74") != 2 or int.from_bytes(payload[0x0051BF74 - LOAD_ADDRESS:0x0051BF78 - LOAD_ADDRESS], "little") != 0x20074F04:
        raise WaveError("shared command-context pointer closure drift")
    all_data_cells = set(dat)
    covered = {0x0051B4EC, 0x0051B8EC, 0x0051BF74}
    if all_data_cells != covered:
        raise WaveError("direct data cells are not exhaustively partitioned")

    callers = tuple(sorted(int(value["entry"], 16) for value in function_rows if f"{ROOT:08x}" in value.get("callees", [])))
    if callers != (0x0051F798,) or (parent_by_entry[0x0051F798]["bucket"], parent_by_entry[0x0051F798]["evidence"], parent_by_entry[0x0051F798]["confidence"]) != ("first-party", "call-topology-single-family", "medium"):
        raise WaveError("first-party ingress topology drift")
    ft_rows = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-freetype-engine-census.tsv"])
    ft = next(value for value in ft_rows if int(value["entry"], 16) == ROOT)
    if ft["status"] != "investigation-required" or "no FreeType anchor, string, or call-community evidence" not in ft["detail"]:
        raise WaveError("FreeType negative evidence drift")
    nema = json.loads(local[NEMA])
    resolved = {int(address, 16) for address in nema["stock_evidence"]["resolved_symbols"]}
    if ROOT in resolved or nema["integration_status"]["production_ready"] is not False or "not byte-identical archive members" not in nema["archive_metadata"]["stock_compiler_relation"]:
        raise WaveError("Nema exact-provider boundary drift")

    residual_after = residual - {ROOT}
    after = {"functions": len(residual_after), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_after)}
    if after != {"functions": 1352, "bytes": 152498}:
        raise WaveError(f"wave-10 after accounting drift: {after}")
    next_size, next_entry = max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_after)
    if (next_size, next_entry) != (1912, 0x005AF88C):
        raise WaveError(f"next-largest envelope drift: 0x{next_entry:08X}/{next_size}")

    record = {"entry": row["entry"], "end_exclusive": row["end_exclusive"], "envelope_bytes": envelope, "corpus_body_bytes": corpus_bytes, "body_sha256": digest, "closure_depth": depth, "role": role, "provider_identity": row["provider_identity"], "license_status": row["license_status"], "disposition": row["disposition"], "source_identity_authenticated": False, "production_routed": False}
    branches = [{"site": f"0x{site:08X}", "target": f"0x{target:08X}"} for site, target in sorted(bl_sites.items())]
    mapping_sha = sha256(json.dumps({"typed": [record], "frontier": frontier_records, "interiors": interior_records, "shared": shared_records, "callother": callother_records, "branches": branches}, sort_keys=True, separators=(",", ":")).encode())
    return {
        "status": "opacity-wave10-round-join-mve-closure-typed",
        "read_only": True, "hardware_operations": False, "production_routed": False,
        "wave9_residual": wave9_report["after"], "before": before,
        "selected_root_range": {"start": "0x0051B140", "end_exclusive": "0x0051B8EA"},
        "actionable_graph": {"positive_functions": 1, "positive_bytes": 1962, "terminal_functions": 7, "call_edges": 7, "static_callsites": 26},
        "machine_branch_closure": {"direct_bl_sites": 26, "wide_nonlink_sites": 0, "register_blx_sites": 0, "targets": 7},
        "callother_reconciliation": {"artifacts": 16, "occurrences": 16, "machine_branch_sites": 0, "additional_function_bytes": 0},
        "range_partition": {"functions": 1, "interior_islands": 1, "interior_physical_bytes": 4, "additional_function_bytes": 0},
        "shared_data": {"islands": 2, "physical_bytes": 10, "direct_dat_cells": 3, "out_of_envelope_direct_dat_cells": 2, "additional_function_bytes": 0},
        "typed_unavailable": {"functions": 1, "bytes": 1962}, "source_attributed": {"functions": 0, "bytes": 0},
        "provider": {"family_context": "NemaGFX/NemaVG vector-path candidate only", "authenticated_function_identity": None, "authenticated_provider": None, "authenticated_license": None, "negative_evidence": ["root absent from the eleven authenticated stock Nema symbols", "public Apollo5 Nema archive is GCC and not byte-identical to IAR stock", "single first-party caller and vector-helper topology do not prove maintained source identity"]},
        "ingress": {"callers": ["0x0051F798"], "classification": "first-party", "confidence": "medium"},
        "after": after, "largest_remaining": {"entry": f"0x{next_entry:08X}", "envelope_bytes": next_size},
        "records": [record], "frontier_records": frontier_records, "interior_records": interior_records, "shared_records": shared_records, "callother_records": callother_records, "branch_records": branches, "mapping_sha256": mapping_sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
