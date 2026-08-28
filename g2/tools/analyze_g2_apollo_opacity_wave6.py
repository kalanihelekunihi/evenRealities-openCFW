#!/usr/bin/env python3
"""Close Apollo opacity wave 6 and its guarded continuation.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
BOUNDARY = G2 / "research/admission/apollo_opacity_wave6/typed_boundaries.tsv"
RECONCILED = G2 / "research/admission/apollo_opacity_wave6/reconciled_frontier.tsv"
ROOT = 0x0051C5EC
LOAD_ADDRESS = 0x00438000

EXPECTED_SELECTED = {
    0x0051C5EC: (0x0051D2D6, 3306, 3298, "7487038aa5bf05ee5c13296625a2ddf2c7ea592f5dc975661b7f6e0c7a3c1c27", 0, "vector-stroke-cap-and-join-coordinator"),
    0x00522A24: (0x00522AE0, 188, 188, "327db00a0e6454567bf77265834f19ea1c27fe46a181247cc9a1837985c1a392", 1, "six-coordinate-command-record-builder"),
    0x00522F1C: (0x00522F4E, 50, 50, "4d114bb5d97b3fd756073d3455a50966bbb859acfe750da9d7f04c6d43d11009", 1, "tessellation-segment-count-clamp-align-helper"),
    0x00523A34: (0x00523A3A, 6, 6, "b6cf70e970ae335da6d6e7ccae5dfd27bf71d27e0c27d830d7d9eab66429c9dc", 1, "guarded-polyline-record-entry"),
    0x0052405C: (0x00524126, 202, 202, "c5bb99c0cb615464e5f66070b71a6200c8310de5406d7e83f5508e222ab67859", 1, "periodic-trigonometric-polynomial-helper-a"),
    0x00524130: (0x005241F6, 198, 198, "38408e2e2a76236f3d66e95b1e8fde1b1f0c0b6c2959a431557bfefc41b6d1ee", 1, "periodic-trigonometric-polynomial-helper-b"),
    0x00523A3A: (0x00523BEE, 436, 436, "88fb75f73ff38a7f30960c2b12adbf2b18749c994c1c42aae9a01ec9cf06bd45", 2, "polyline-command-record-body"),
}
EXPECTED_CALLS = {
    0x0051C5EC: {0x0052266E: 12, 0x00516B34: 4, 0x00524218: 2, 0x00522F1C: 4, 0x00524130: 4, 0x0052405C: 4, 0x00523A34: 4, 0x00522A24: 4, 0x005226B2: 2, 0x0051565C: 1},
    0x00522A24: {0x005242CC: 6, 0x00514AEC: 1},
    0x00522F1C: {},
    # Ghidra repeats the semantic continuation in this guarded-entry decompile.
    0x00523A34: {0x005242CC: 10, 0x00514AEC: 3},
    0x0052405C: {},
    0x00524130: {},
    0x00523A3A: {0x005242CC: 10, 0x00514AEC: 3},
}
COMPANION_EDGES = {0x00523A34: {0x00523A3A}}
EXPECTED_RECONCILED = {
    0x00514AEC: (2, "apollo-opacity-wave2", 138, "0x00522A24,0x00523A3A"),
    0x0051565C: (1, "apollo-opacity-wave2", 16, "0x0051C5EC"),
    0x00516B34: (1, "apollo-opacity-wave2", 170, "0x0051C5EC"),
    0x0052266E: (1, "apollo-opacity-wave2", 68, "0x0051C5EC"),
    0x005226B2: (1, "apollo-opacity-wave1", 36, "0x0051C5EC"),
    0x00524218: (1, "apollo-opacity-wave3", 64, "0x0051C5EC"),
    0x005242CC: (2, "apollo-opacity-wave3", 22, "0x00522A24,0x00523A3A"),
}


class WaveError(RuntimeError):
    """Raised when authenticated wave-6 evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def run_audit() -> dict[str, Any]:
    wave5 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave5.py", "opacity_wave6_wave5")
    wave5_report = wave5.run_audit()
    if wave5_report["after"] != {"functions": 1395, "bytes": 172308}:
        raise WaveError("wave-5 residual drift")
    wave1 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave1.py", "opacity_wave6_wave1")
    wave2 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave2.py", "opacity_wave6_wave2")
    wave3 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave3.py", "opacity_wave6_wave3")
    wave4 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave4.py", "opacity_wave6_wave4")
    inherited = {path: wave1.pinned(path) for path in wave1.PINS}
    parent_rows = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"])
    parent_by_entry = {int(row["entry"], 16): row for row in parent_rows}
    parent_none = {entry: row for entry, row in parent_by_entry.items() if row["bucket"] == "investigation-required-no-evidence"}
    cordio = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-cordio-ll-sea-census.tsv"])
    freetype = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-freetype-engine-census.tsv"])
    liblc3 = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-liblc3-encoder-internals-map.tsv"])
    mspi = load_module(G2 / "tools/analyze_g2_apollo510_mspi_triplet_candidate.py", "opacity_wave6_mspi").run_audit()
    classified = (
        {int(row["entry"], 16) for row in cordio}
        | {int(row["entry"], 16) for row in freetype if row["status"] != "investigation-required"}
        | {int(row["entry"], 16) for row in liblc3 if row["status"] != "investigation-required"}
        | {int(entry, 16) for entry in mspi["triplet"]}
    )
    residual_before = (
        set(parent_none) - classified - set(wave1.EXPECTED_SELECTED)
        - set(wave2.EXPECTED_SELECTED) - set(wave3.EXPECTED_SELECTED)
        - set(wave4.EXPECTED_SELECTED) - set(wave4.EXPECTED_ZERO)
        - set(wave5.EXPECTED_SELECTED) - {0x004397A8, 0x00439C04}
    )
    before = {"functions": len(residual_before), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_before)}
    if before != wave5_report["after"]:
        raise WaveError(f"wave-5 set reconciliation drift: {before}")
    if max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_before) != (3306, ROOT):
        raise WaveError("wave-6 root is no longer largest")

    corpus = wave5.pinned(wave5.CORPUS).decode()
    payload = inherited[wave1.IMAGE][wave1.OTA_HEADER_BYTES:]
    rows = tsv_rows(BOUNDARY)
    selected = {int(row["entry"], 16) for row in rows}
    if selected != set(EXPECTED_SELECTED) or not selected <= residual_before:
        raise WaveError("selected actionable closure membership drift")
    observed_calls: dict[int, dict[int, int]] = {}
    records: list[dict[str, Any]] = []
    for row in rows:
        entry = int(row["entry"], 16)
        end, envelope_bytes, corpus_bytes, digest, depth, role = EXPECTED_SELECTED[entry]
        if (int(row["end_exclusive"], 16), int(row["envelope_bytes"]), int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]), row["role"]) != (end, envelope_bytes, corpus_bytes, digest, depth, role):
            raise WaveError(f"0x{entry:08X}: static boundary drift")
        parent = parent_none[entry]
        if int(parent["body_end_exclusive"], 16) != end or int(parent["official_opaque_bytes"]) != envelope_bytes:
            raise WaveError(f"0x{entry:08X}: parent boundary drift")
        body_bytes = payload[entry - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if len(body_bytes) != envelope_bytes or sha256(body_bytes) != digest:
            raise WaveError(f"0x{entry:08X}: official body drift")
        body, decoded_bytes, corpus_digest = wave5.corpus_function(corpus, entry)
        if (decoded_bytes, corpus_digest) != (corpus_bytes, digest):
            raise WaveError(f"0x{entry:08X}: corpus identity drift")
        calls = Counter(int(match, 16) for match in re.findall(r"\bFUN_([0-9a-f]{8})\(", body))
        calls.pop(entry, None)
        observed_calls[entry] = dict(calls)
        if observed_calls[entry] != EXPECTED_CALLS[entry]:
            raise WaveError(f"0x{entry:08X}: call-topology drift")
        if row["provider_identity"] != "unresolved-linked-vector-path-provider" or row["license_status"] != "unavailable" or row["disposition"] != "typed-external-provider-unavailable":
            raise WaveError(f"0x{entry:08X}: fail-closed disposition drift")
        records.append({
            "entry": row["entry"], "end_exclusive": row["end_exclusive"],
            "envelope_bytes": envelope_bytes, "corpus_body_bytes": corpus_bytes,
            "body_sha256": digest, "closure_depth": depth, "role": role,
            "provider_identity": row["provider_identity"], "license_status": row["license_status"],
            "disposition": row["disposition"], "callable_implementation_available": False,
        })

    # The six-byte prefix is cmp/bge/bx-lr and the taken edge enters 0x523A3A.
    guard = payload[0x00523A34 - LOAD_ADDRESS:0x00523A3A - LOAD_ADDRESS]
    if guard.hex() != "032900da7047":
        raise WaveError("guarded continuation instruction bytes drift")
    depths = {ROOT: 0}
    frontier = {ROOT}
    while frontier:
        next_frontier: set[int] = set()
        for entry in frontier:
            for target in set(observed_calls[entry]) | COMPANION_EDGES.get(entry, set()):
                if target in residual_before and target not in depths:
                    depths[target] = depths[entry] + 1
                    next_frontier.add(target)
        frontier = next_frontier
    if depths != {entry: values[4] for entry, values in EXPECTED_SELECTED.items()}:
        raise WaveError(f"complete actionable closure drift: {depths}")

    reconciled_rows = tsv_rows(RECONCILED)
    if {int(row["entry"], 16) for row in reconciled_rows} != set(EXPECTED_RECONCILED):
        raise WaveError("terminal frontier membership drift")
    prior_sets = {"apollo-opacity-wave1": set(wave1.EXPECTED_SELECTED), "apollo-opacity-wave2": set(wave2.EXPECTED_SELECTED), "apollo-opacity-wave3": set(wave3.EXPECTED_SELECTED)}
    reconciled_records: list[dict[str, Any]] = []
    for row in reconciled_rows:
        entry = int(row["entry"], 16)
        depth, owner, opaque_bytes, sources = EXPECTED_RECONCILED[entry]
        evidence = f"wave-{owner[-1]} authenticated body and boundary"
        if (int(row["closure_depth"]), row["accounting_state"], row["owner"], int(row["parent_official_opaque_bytes"]), int(row["wave6_new_opaque_bytes"]), row["edge_sources"], row["evidence"]) != (depth, "prior-typed", owner, opaque_bytes, 0, sources, evidence):
            raise WaveError(f"0x{entry:08X}: terminal reconciliation drift")
        if entry not in prior_sets[owner] or int(parent_none[entry]["official_opaque_bytes"]) != opaque_bytes:
            raise WaveError(f"0x{entry:08X}: prior ownership drift")
        reconciled_records.append({"entry": row["entry"], "closure_depth": depth, "owner": owner, "parent_official_opaque_bytes": opaque_bytes, "wave6_new_opaque_bytes": 0, "edge_sources": sources.split(",")})
    all_targets = {target for entry in selected for target in set(observed_calls[entry]) | COMPANION_EDGES.get(entry, set())}
    if all_targets - selected != set(EXPECTED_RECONCILED) or set(EXPECTED_RECONCILED) & residual_before:
        raise WaveError("terminal partition is not exhaustive")

    ft_by_entry = {int(row["entry"], 16): row for row in freetype}
    for entry in selected:
        ft = ft_by_entry[entry]
        if ft["status"] != "investigation-required" or "no FreeType anchor, string, or call-community evidence" not in ft["detail"]:
            raise WaveError(f"0x{entry:08X}: FreeType negative evidence drift")
    nema = json.loads(wave5.pinned(wave5.NEMA_PROVENANCE))
    resolved = {int(address, 16) for address in nema["stock_evidence"]["resolved_symbols"]}
    if selected & resolved or nema["integration_status"]["production_ready"] is not False or "not byte-identical archive members" not in nema["archive_metadata"]["stock_compiler_relation"]:
        raise WaveError("Nema exact-provider negative boundary drift")

    residual_after = residual_before - selected
    after = {"functions": len(residual_after), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_after)}
    if after != {"functions": 1388, "bytes": 167922}:
        raise WaveError(f"wave-6 after accounting drift: {after}")
    if max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_after) != (2598, 0x00564974):
        raise WaveError("next-largest envelope drift")
    depth_summary = {str(depth): {"typed_functions": sum(v == depth for v in depths.values()), "typed_bytes": sum(EXPECTED_SELECTED[e][1] for e, v in depths.items() if v == depth)} for depth in sorted(set(depths.values()))}
    mapping_sha = sha256(json.dumps({"typed": records, "reconciled": reconciled_records}, sort_keys=True, separators=(",", ":")).encode())
    return {
        "status": "opacity-wave6-vector-stroke-closure-typed", "read_only": True,
        "hardware_operations": False, "production_routed": False,
        "wave5_residual": wave5_report["after"], "before": before,
        "selected_root_range": {"start": "0x0051C5EC", "end_exclusive": "0x0051D2D6"},
        "newly_typed": {"functions": len(selected), "bytes": sum(v[1] for v in EXPECTED_SELECTED.values())},
        "closure_depths": depth_summary,
        "guarded_continuation": {"entry": "0x00523A34", "target": "0x00523A3A", "instruction_bytes": guard.hex(), "accounted": True},
        "reconciled_frontier": {"functions": len(reconciled_records), "new_bytes": 0},
        "provider": {
            "family_context": "NemaGFX/NemaVG vector-path community candidate",
            "authenticated_function_identities": [], "authenticated_provider": None,
            "authenticated_license": None,
            "negative_evidence": [
                "all seven rows absent from the eleven authenticated stock Nema symbols",
                "public GCC Nema archive is not byte-identical to IAR-generated stock",
                "all seven FreeType rows lack anchor, string, and call-community evidence",
            ],
        },
        "after": after, "largest_remaining": {"entry": "0x00564974", "envelope_bytes": 2598},
        "mapping_sha256": mapping_sha, "records": records, "reconciled_records": reconciled_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
