#!/usr/bin/env python3
"""Audit Apollo opacity Wave 15's paired round-cap vector coordinator.

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
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
NEMA = G2 / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
ADMISSION = G2 / "research/admission/apollo_opacity_wave15"
BOUNDARY = ADMISSION / "typed_boundaries.tsv"
FRONTIER = ADMISSION / "reconciled_frontier.tsv"
INTERIORS = ADMISSION / "reconciled_interiors.tsv"
SHARED = ADMISSION / "shared_data.tsv"
CALLOTHER = ADMISSION / "reconciled_callother.tsv"
ROOT = 0x0051B8F0
LOAD_ADDRESS = 0x00438000
OTA_HEADER_BYTES = 32

PINS = {
    CORPUS: (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    IMAGE: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    NEMA: (24_898, "5a8e427ae337afb78f2901e74ae48d08d8c222944a50ada8adadfbdd98296bfa"),
}
EXPECTED_CALLS = {
    0x00516B34: 2,
    0x0052266E: 6,
    0x005226B2: 1,
    0x00522A24: 2,
    0x00522F1C: 2,
    0x00523A34: 2,
    0x0052405C: 2,
    0x00524130: 2,
    0x00524218: 1,
}
EXPECTED_OWNERS = {
    0x00516B34: (2, "command-record-builder"),
    0x0052266E: (2, "command-state-mask-helper"),
    0x005226B2: (1, "state-leaf"),
    0x00522A24: (6, "six-coordinate-command-record-builder"),
    0x00522F1C: (6, "tessellation-segment-count-clamp-align-helper"),
    0x00523A34: (6, "guarded-polyline-record-entry"),
    0x0052405C: (6, "periodic-trigonometric-polynomial-helper-a"),
    0x00524130: (6, "periodic-trigonometric-polynomial-helper-b"),
    0x00524218: (3, "scalar-square-root-helper"),
}
EXPECTED_BL_SITES = {
    0x0051B9AC: 0x0052266E,
    0x0051B9D2: 0x00516B34,
    0x0051B9D8: 0x005226B2,
    0x0051BA42: 0x00524218,
    0x0051BAD4: 0x0052266E,
    0x0051BAFA: 0x00516B34,
    0x0051BB98: 0x00522F1C,
    0x0051BBB8: 0x00524130,
    0x0051BBC4: 0x0052405C,
    0x0051BCF8: 0x0052266E,
    0x0051BD04: 0x00523A34,
    0x0051BD28: 0x0052266E,
    0x0051BD56: 0x00522A24,
    0x0051BDA6: 0x00522F1C,
    0x0051BDC6: 0x00524130,
    0x0051BDD2: 0x0052405C,
    0x0051BF04: 0x0052266E,
    0x0051BF10: 0x00523A34,
    0x0051BF30: 0x0052266E,
    0x0051BF5E: 0x00522A24,
}
EXPECTED_CALLOTHER = {
    0x00D69C2C,
    0x00D2AC5C,
    0x01169CE0,
    0x00D2AD84,
    0x00D69E38,
    0x00D2AE68,
    0x01169EEC,
    0x00D2AF90,
}


class WaveError(RuntimeError):
    """Raised when authenticated Wave-15 evidence changes."""


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
    marker = re.search(
        rf"/\* FUN 0x{entry:08x} .*? bytes=(\d+) sha256=([0-9a-f]{{64}}) \*/",
        corpus,
    )
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
    immediate = (
        sign << 24
        | (1 ^ (j1 ^ sign)) << 23
        | (1 ^ (j2 ^ sign)) << 22
        | (first & 0x03FF) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def residual_before() -> tuple[dict[int, dict[str, str]], set[int], dict[str, Any]]:
    wave14 = load_module(
        G2 / "tools/analyze_g2_apollo_opacity_wave14.py", "opacity_wave15_wave14"
    )
    report = wave14.run_audit()
    if report["after"] != {"functions": 1292, "bytes": 134476} or report[
        "largest_remaining"
    ] != {"entry": "0x0051B8F0", "envelope_bytes": 1668}:
        raise WaveError("wave-14 residual drift")
    parent, residual, _ = wave14.residual_before()
    residual -= wave14.EXPECTED_SELECTED
    return parent, residual, report


def run_audit() -> dict[str, Any]:
    parent, residual, report14 = residual_before()
    before = {
        "functions": len(residual),
        "bytes": sum(int(parent[entry]["official_opaque_bytes"]) for entry in residual),
    }
    if before != report14["after"] or max(
        (int(parent[entry]["official_opaque_bytes"]), entry) for entry in residual
    ) != (1668, ROOT):
        raise WaveError("authoritative residual/root drift")

    local = {path: pinned(path) for path in PINS}
    corpus = local[CORPUS].decode(errors="ignore")
    function_rows = [json.loads(line) for line in local[FUNCTIONS].decode().splitlines()]
    functions = {int(row["entry"], 16): row for row in function_rows}
    payload = local[IMAGE][OTA_HEADER_BYTES:]
    boundary_rows = tsv_rows(BOUNDARY)
    if len(boundary_rows) != 1 or int(boundary_rows[0]["entry"], 16) != ROOT:
        raise WaveError("selected boundary membership drift")
    row = boundary_rows[0]
    function = functions[ROOT]
    expected_boundary = (
        0x0051BF74,
        1668,
        1664,
        "549fd3c4e21f1074d6f2b04309e72283b3f85b575f41bd31fc4718f7a63e3382",
        0,
        "round-stroke-cap-fan-tessellation-coordinator",
        "unresolved-linked-vector-path-provider",
        "unavailable",
        "typed-external-provider-unavailable",
    )
    observed_boundary = (
        int(row["end_exclusive"], 16),
        int(row["envelope_bytes"]),
        int(row["corpus_body_bytes"]),
        row["body_sha256"],
        int(row["closure_depth"]),
        row["role"],
        row["provider_identity"],
        row["license_status"],
        row["disposition"],
    )
    if observed_boundary != expected_boundary:
        raise WaveError("typed boundary drift")
    if (
        int(parent[ROOT]["body_end_exclusive"], 16),
        int(parent[ROOT]["official_opaque_bytes"]),
        int(function["body_bytes"]),
        function["body_sha256"],
    ) != expected_boundary[:4]:
        raise WaveError("parent/corpus body accounting drift")
    ranges = tuple(
        (int(start, 16), int(stop, 16) + 1) for start, stop in function["ranges"]
    )
    if ranges != ((0x0051B8F0, 0x0051BD1C), (0x0051BD20, 0x0051BF74)):
        raise WaveError("root decoded ranges drift")
    body, body_bytes, body_digest = corpus_function(corpus, ROOT)
    installed = payload[ROOT - LOAD_ADDRESS : 0x0051BF74 - LOAD_ADDRESS]
    if (body_bytes, body_digest, len(installed), sha256(installed)) != (
        1664,
        expected_boundary[3],
        1668,
        expected_boundary[3],
    ):
        raise WaveError("installed/corpus root identity drift")

    observed_calls = Counter(
        int(value, 16) for value in re.findall(r"\bFUN_([0-9a-f]{8})\(", body)
    )
    observed_calls.pop(ROOT, None)
    if dict(observed_calls) != EXPECTED_CALLS or {
        int(value, 16) for value in function["callees"]
    } != set(EXPECTED_CALLS):
        raise WaveError("decompiler call topology drift")
    if set(EXPECTED_CALLS) & residual:
        raise WaveError("root has an unreconciled positive-byte static callee")

    bl_sites: dict[int, int] = {}
    bw_sites: dict[int, int] = {}
    register_blx_sites = []
    for offset in range(0, len(installed) - 3, 2):
        address = ROOT + offset
        first, second = struct.unpack_from("<HH", installed, offset)
        for link, sites in ((True, bl_sites), (False, bw_sites)):
            target = wide_branch_target(address, first, second, link=link)
            if target is not None:
                sites[address] = target
    for offset in range(0, len(installed) - 1, 2):
        halfword = struct.unpack_from("<H", installed, offset)[0]
        if halfword & 0xFF80 == 0x4780:
            register_blx_sites.append(ROOT + offset)
    if (
        bl_sites != EXPECTED_BL_SITES
        or bw_sites
        or register_blx_sites
        or dict(Counter(bl_sites.values())) != EXPECTED_CALLS
    ):
        raise WaveError("installed Thumb call closure drift")

    owner_modules = {
        number: load_module(
            G2 / f"tools/analyze_g2_apollo_opacity_wave{number}.py",
            f"opacity_wave15_wave{number}",
        )
        for number in (1, 2, 3, 6)
    }
    frontier_rows = tsv_rows(FRONTIER)
    if {int(item["entry"], 16) for item in frontier_rows} != set(EXPECTED_CALLS):
        raise WaveError("frontier membership drift")
    frontier_records = []
    for item in frontier_rows:
        entry = int(item["entry"], 16)
        owner, role = EXPECTED_OWNERS[entry]
        if entry not in set(owner_modules[owner].EXPECTED_SELECTED):
            raise WaveError(f"0x{entry:08X}: prior owner drift")
        observed = (
            item["classification"],
            item["role"],
            item["source_wave"],
            item["provider_identity"],
            item["license_status"],
            item["disposition"],
            int(item["call_sites"]),
            int(item["wave15_additional_function_bytes"]),
        )
        expected = (
            "prior-typed",
            role,
            f"apollo-opacity-wave{owner}",
            "unresolved-linked-vector-path-provider",
            "unavailable",
            "prior-typed-external-provider-unavailable",
            EXPECTED_CALLS[entry],
            0,
        )
        if observed != expected:
            raise WaveError(f"0x{entry:08X}: frontier record drift")
        frontier_records.append(dict(item))

    pseudo = Counter(
        int(value, 16) for value in re.findall(r"\bfunc_0x([0-9a-f]{8})\(", body)
    )
    callother_rows = tsv_rows(CALLOTHER)
    if (
        set(pseudo) != EXPECTED_CALLOTHER
        or any(count != 1 for count in pseudo.values())
        or {int(item["pseudo_identifier"], 16) for item in callother_rows}
        != EXPECTED_CALLOTHER
    ):
        raise WaveError("MVE callother membership drift")
    for item in callother_rows:
        if (
            int(item["occurrences"]),
            int(item["machine_branch_sites"]),
            item["classification"],
            item["disposition"],
            int(item["wave15_additional_function_bytes"]),
        ) != (1, 0, "ghidra-callother-artifact", "not-a-static-call-boundary", 0):
            raise WaveError("MVE callother record drift")

    interior_rows = tsv_rows(INTERIORS)
    if len(interior_rows) != 1:
        raise WaveError("interior partition membership drift")
    interior = interior_rows[0]
    interior_bytes = payload[0x0051BD1C - LOAD_ADDRESS : 0x0051BD20 - LOAD_ADDRESS]
    if (
        interior["bytes_hex"],
        interior["sha256"],
        int(interior["wave15_additional_bytes"]),
        interior_bytes.hex(),
        sha256(interior_bytes),
    ) != (
        "00003443",
        "21b9ff9cf99927e92d16d0fcc3190c14680a24c02dad89f9777d5107fdeb5db1",
        0,
        "00003443",
        "21b9ff9cf99927e92d16d0fcc3190c14680a24c02dad89f9777d5107fdeb5db1",
    ):
        raise WaveError("interior literal drift")

    direct_data = Counter(
        int(value, 16) for value in re.findall(r"\bDAT_([0-9a-f]{8})", body)
    )
    if dict(direct_data) != {0x0051BF74: 2, 0x0051BD1C: 1, 0x0051BF78: 1}:
        raise WaveError("direct data topology drift")
    shared_rows = tsv_rows(SHARED)
    shared_expected = {
        0x0051BF74: ("044f0720", "48b4654f2567d2b59ecbe37e6f96190282388ca5bbd42e18a0f7bae12fc58b2d", "apollo-opacity-wave10"),
        0x0051BF78: ("00003443", "21b9ff9cf99927e92d16d0fcc3190c14680a24c02dad89f9777d5107fdeb5db1", "none"),
    }
    if {int(item["start"], 16) for item in shared_rows} != set(shared_expected):
        raise WaveError("shared data membership drift")
    for item in shared_rows:
        start = int(item["start"], 16)
        physical = payload[start - LOAD_ADDRESS : start - LOAD_ADDRESS + 4]
        expected_hex, expected_digest, prior_owner = shared_expected[start]
        if (
            item["bytes_hex"],
            item["sha256"],
            item["prior_owner"],
            int(item["wave15_additional_function_bytes"]),
            physical.hex(),
            sha256(physical),
        ) != (expected_hex, expected_digest, prior_owner, 0, expected_hex, expected_digest):
            raise WaveError("shared data record drift")
    if struct.unpack("<I", payload[0x0051BF74 - LOAD_ADDRESS : 0x0051BF78 - LOAD_ADDRESS])[0] != 0x20074F04:
        raise WaveError("shared context pointer value drift")

    callers = tuple(
        sorted(
            int(item["entry"], 16)
            for item in function_rows
            if f"{ROOT:08x}" in item.get("callees", [])
        )
    )
    if callers != (0x0051D2E0, 0x005639E8):
        raise WaveError("root ingress topology drift")
    nema = json.loads(local[NEMA])
    resolved = {int(address, 16) for address in nema["stock_evidence"]["resolved_symbols"]}
    if (
        ROOT in resolved
        or nema["integration_status"]["production_ready"] is not False
        or "not byte-identical archive members"
        not in nema["archive_metadata"]["stock_compiler_relation"]
    ):
        raise WaveError("Nema provider-negative evidence drift")

    remaining = residual - {ROOT}
    after = {
        "functions": len(remaining),
        "bytes": sum(int(parent[entry]["official_opaque_bytes"]) for entry in remaining),
    }
    next_bytes, next_entry = max(
        (int(parent[entry]["official_opaque_bytes"]), entry) for entry in remaining
    )
    if after != {"functions": 1291, "bytes": 132808} or (
        next_entry,
        next_bytes,
    ) != (0x0051BF7C, 1640):
        raise WaveError(f"after/next residual drift: {after}, 0x{next_entry:08X}/{next_bytes}")

    record = {
        "entry": row["entry"],
        "end_exclusive": row["end_exclusive"],
        "envelope_bytes": 1668,
        "corpus_body_bytes": 1664,
        "body_sha256": row["body_sha256"],
        "role": row["role"],
        "provider_identity": row["provider_identity"],
        "license_status": row["license_status"],
        "disposition": row["disposition"],
        "source_identity_authenticated": False,
        "production_routed": False,
    }
    branches = [
        {"site": f"0x{site:08X}", "target": f"0x{target:08X}"}
        for site, target in sorted(bl_sites.items())
    ]
    canonical = {
        "typed": [record],
        "frontier": frontier_records,
        "interiors": interior_rows,
        "shared": shared_rows,
        "callother": callother_rows,
        "branches": branches,
    }
    return {
        "status": "opacity-wave15-round-cap-mve-closure-typed",
        "wave14_residual": report14["after"],
        "before": before,
        "selected_root_range": {"start": "0x0051B8F0", "end_exclusive": "0x0051BF74"},
        "actionable_graph": {
            "positive_functions": 1,
            "positive_bytes": 1668,
            "terminal_functions": 9,
            "static_callsites": 20,
        },
        "machine_branch_closure": {
            "direct_bl_sites": 20,
            "wide_nonlink_sites": 0,
            "register_blx_sites": 0,
            "targets": 9,
        },
        "callother_reconciliation": {
            "artifacts": 8,
            "occurrences": 8,
            "machine_branch_sites": 0,
            "additional_function_bytes": 0,
        },
        "range_partition": {
            "functions": 1,
            "interior_islands": 1,
            "interior_physical_bytes": 4,
            "additional_function_bytes": 0,
        },
        "shared_data": {
            "islands": 2,
            "physical_bytes": 8,
            "prior_reconciled_bytes": 4,
            "direct_dat_cells": 3,
            "additional_function_bytes": 0,
        },
        "typed_unavailable": {"functions": 1, "bytes": 1668},
        "source_attributed": {"functions": 0, "bytes": 0},
        "provider": {
            "family_context": "NemaGFX/NemaVG vector-path candidate only",
            "authenticated_function_identity": None,
            "authenticated_provider": None,
            "authenticated_license": None,
            "negative_evidence": [
                "root absent from authenticated stock Nema symbols",
                "available Apollo5 archive is GCC and not byte-identical to IAR stock",
                "paired Wave-10 topology proves a behavior family, not maintained source identity",
            ],
        },
        "ingress": {"callers": ["0x0051D2E0", "0x005639E8"]},
        "after": after,
        "largest_remaining": {"entry": f"0x{next_entry:08X}", "envelope_bytes": next_bytes},
        "records": [record],
        "frontier_records": frontier_records,
        "branch_records": branches,
        "mapping_sha256": sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
        ),
        "production_routed": False,
        "production_blocker": "maintained implementation source, license, ABI/configuration, and reviewed dual-profile placement proof are unavailable",
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
