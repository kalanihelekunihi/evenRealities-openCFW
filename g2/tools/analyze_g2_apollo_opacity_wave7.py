#!/usr/bin/env python3
"""Close Apollo opacity wave 7 and reconcile embedded shared literals.

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
CORPUS = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-11.c"
FUNCTIONS = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
NEMA = G2 / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave7/typed_boundaries.tsv"
INTERIORS = G2 / "research/admission/apollo_opacity_wave7/reconciled_interiors.tsv"
ROOT = 0x00564974
LOAD_ADDRESS = 0x00438000

PINS = {
    CORPUS: (739_345, "029dbe031730c0d760e1913f8d043119b77f49170725b1464f5a53cc166a1bea"),
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    NEMA: (24_898, "5a8e427ae337afb78f2901e74ae48d08d8c222944a50ada8adadfbdd98296bfa"),
}
EXPECTED_SELECTED = {
    0x00564974: (0x0056539A, 2598, 2588, "090a3aed24263501971e8c995c6cea0cd8e28cbf831a1ac08323efd755af6c96", 0, "clipped-segment-and-state-buffer-coordinator"),
    0x005640E4: (0x0056496E, 2186, 2174, "dfa5a3b0d34c1e852871286e49229c1db5fc271ed0801db96090d9561a386b87", 1, "segment-rectangle-intersection-collector"),
}
EXPECTED_CALLS = {0x00564974: {0x005640E4: 3}, 0x005640E4: {}}
EXPECTED_RANGES = {
    0x005640E4: ((0x005640E4, 0x00564156), (0x0056415C, 0x00564556), (0x0056455C, 0x0056496E)),
    0x00564974: ((0x00564974, 0x00564A3E), (0x00564A44, 0x00564F5C), (0x00564F60, 0x0056539A)),
}
EXPECTED_INTERIORS = {
    0x00564156: (0x0056415C, "00bf0100803f", "c55b1af97c7d8e322025678712caf47c822a6a6eb2b1faafd21d5b6182035bff", 0x005640E4, 0x00564158, "nop-plus-near-one-float-literal-0x3f800001", "0x005640E4"),
    0x00564556: (0x0056455C, "00bfacc52737", "35979e56975744dc7e09f1361d5f4e26f80361cb11321cc99413b933f26cd77b", 0x005640E4, 0x00564558, "nop-plus-epsilon-float-literal-0x3727c5ac", "0x005640E4"),
    0x00564A3E: (0x00564A44, "00bf044f0720", "507ae878b86a0071d5b9ac1f58c19572fa6d3ad1b3ad52397c0aaa15003a707a", 0x00564974, 0x00564A40, "nop-plus-shared-context-pointer-0x20074f04", "0x005640E4,0x00564974"),
    0x00564F5C: (0x00564F60, "acc52737", "e6540c5b3269d9a6e3646dd482c2a7fe6b58e101e80007556892bb770099a68c", 0x00564974, 0x00564F5C, "epsilon-float-literal-0x3727c5ac", "0x00564974"),
}
EXPECTED_REFERENCES = {
    0x005640E4: {0x00564158: 3, 0x00564558: 10, 0x00564A40: 1, 0x00564F5C: 0},
    0x00564974: {0x00564158: 0, 0x00564558: 0, 0x00564A40: 2, 0x00564F5C: 2},
}


class WaveError(RuntimeError):
    """Raised when authenticated wave-7 evidence changes."""


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


def run_audit() -> dict[str, Any]:
    wave6 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave6.py", "opacity_wave7_wave6")
    wave6_report = wave6.run_audit()
    if wave6_report["after"] != {"functions": 1388, "bytes": 167922}:
        raise WaveError("wave-6 residual drift")
    modules = {
        i: load_module(G2 / f"tools/analyze_g2_apollo_opacity_wave{i}.py", f"opacity_wave7_wave{i}")
        for i in range(1, 6)
    }
    wave1, wave2, wave3, wave4, wave5 = (modules[i] for i in range(1, 6))
    inherited = {path: wave1.pinned(path) for path in wave1.PINS}
    parent_rows = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"])
    parent_by_entry = {int(row["entry"], 16): row for row in parent_rows}
    parent_none = {entry: row for entry, row in parent_by_entry.items() if row["bucket"] == "investigation-required-no-evidence"}
    cordio = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-cordio-ll-sea-census.tsv"])
    freetype = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-freetype-engine-census.tsv"])
    liblc3 = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-liblc3-encoder-internals-map.tsv"])
    mspi = load_module(G2 / "tools/analyze_g2_apollo510_mspi_triplet_candidate.py", "opacity_wave7_mspi").run_audit()
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
        - set(wave5.EXPECTED_SELECTED) - set(wave6.EXPECTED_SELECTED)
        - {0x004397A8, 0x00439C04}
    )
    before = {"functions": len(residual_before), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_before)}
    if before != wave6_report["after"]:
        raise WaveError(f"wave-6 set reconciliation drift: {before}")
    if max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_before) != (2598, ROOT):
        raise WaveError("wave-7 root is no longer largest")

    local = {path: pinned(path) for path in PINS}
    corpus = local[CORPUS].decode()
    function_rows = [json.loads(line) for line in local[FUNCTIONS].decode().splitlines()]
    functions = {int(row["entry"], 16): row for row in function_rows}
    payload = inherited[wave1.IMAGE][wave1.OTA_HEADER_BYTES:]
    rows = tsv_rows(BOUNDARY)
    selected = {int(row["entry"], 16) for row in rows}
    if selected != set(EXPECTED_SELECTED) or not selected <= residual_before:
        raise WaveError("selected actionable closure membership drift")
    observed_calls: dict[int, dict[int, int]] = {}
    bodies: dict[int, str] = {}
    records: list[dict[str, Any]] = []
    for row in rows:
        entry = int(row["entry"], 16)
        end, envelope_bytes, corpus_bytes, digest, depth, role = EXPECTED_SELECTED[entry]
        if (int(row["end_exclusive"], 16), int(row["envelope_bytes"]), int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]), row["role"]) != (end, envelope_bytes, corpus_bytes, digest, depth, role):
            raise WaveError(f"0x{entry:08X}: static boundary drift")
        parent = parent_none[entry]
        if int(parent["body_end_exclusive"], 16) != end or int(parent["official_opaque_bytes"]) != envelope_bytes:
            raise WaveError(f"0x{entry:08X}: parent boundary drift")
        installed = payload[entry - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if len(installed) != envelope_bytes or sha256(installed) != digest:
            raise WaveError(f"0x{entry:08X}: official envelope drift")
        body, decoded_bytes, corpus_digest = corpus_function(corpus, entry)
        bodies[entry] = body
        if (decoded_bytes, corpus_digest) != (corpus_bytes, digest):
            raise WaveError(f"0x{entry:08X}: corpus identity drift")
        calls = Counter(int(match, 16) for match in re.findall(r"\bFUN_([0-9a-f]{8})\(", body))
        calls.pop(entry, None)
        observed_calls[entry] = dict(calls)
        if observed_calls[entry] != EXPECTED_CALLS[entry]:
            raise WaveError(f"0x{entry:08X}: call topology drift")
        ranges = tuple((int(start, 16), int(end_inclusive, 16) + 1) for start, end_inclusive in functions[entry]["ranges"])
        if ranges != EXPECTED_RANGES[entry] or sum(end_i - start_i for start_i, end_i in ranges) != corpus_bytes:
            raise WaveError(f"0x{entry:08X}: decoded range partition drift")
        if row["provider_identity"] != "unresolved-linked-vector-clipping-provider" or row["license_status"] != "unavailable" or row["disposition"] != "typed-external-provider-unavailable":
            raise WaveError(f"0x{entry:08X}: fail-closed disposition drift")
        records.append({"entry": row["entry"], "end_exclusive": row["end_exclusive"], "envelope_bytes": envelope_bytes, "corpus_body_bytes": corpus_bytes, "body_sha256": digest, "closure_depth": depth, "role": role, "provider_identity": row["provider_identity"], "license_status": row["license_status"], "disposition": row["disposition"], "callable_implementation_available": False})

    depths = {ROOT: 0}
    frontier = {ROOT}
    while frontier:
        following = {target for entry in frontier for target in observed_calls[entry] if target in residual_before and target not in depths}
        for target in following:
            depths[target] = depths[next(iter(frontier))] + 1
        frontier = following
    if depths != {entry: values[4] for entry, values in EXPECTED_SELECTED.items()}:
        raise WaveError(f"complete actionable graph drift: {depths}")
    if {target for calls in observed_calls.values() for target in calls} - selected:
        raise WaveError("terminal frontier unexpectedly nonempty")

    interior_rows = tsv_rows(INTERIORS)
    if {int(row["start"], 16) for row in interior_rows} != set(EXPECTED_INTERIORS):
        raise WaveError("interior island membership drift")
    interior_records: list[dict[str, Any]] = []
    for row in interior_rows:
        start = int(row["start"], 16)
        end, bytes_hex, digest, owner, data_address, kind, consumers = EXPECTED_INTERIORS[start]
        installed = payload[start - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if (int(row["end_exclusive"], 16), int(row["size"]), row["bytes_hex"], row["sha256"], int(row["envelope_owner"], 16), int(row["data_address"], 16), row["kind"], row["consumers"], int(row["wave7_additional_bytes"])) != (end, end - start, bytes_hex, digest, owner, data_address, kind, consumers, 0):
            raise WaveError(f"0x{start:08X}: interior record drift")
        if installed.hex() != bytes_hex or sha256(installed) != digest or not (owner <= start < EXPECTED_SELECTED[owner][0]):
            raise WaveError(f"0x{start:08X}: interior physical evidence drift")
        interior_records.append({"start": row["start"], "end_exclusive": row["end_exclusive"], "size": end - start, "bytes_hex": bytes_hex, "sha256": digest, "envelope_owner": row["envelope_owner"], "data_address": row["data_address"], "kind": kind, "consumers": consumers.split(","), "wave7_additional_bytes": 0})
    derived_gaps = set()
    for entry, ranges in EXPECTED_RANGES.items():
        for (_, previous_end), (next_start, _) in zip(ranges, ranges[1:]):
            derived_gaps.add((previous_end, next_start, entry))
    table_gaps = {(int(row["start"], 16), int(row["end_exclusive"], 16), int(row["envelope_owner"], 16)) for row in interior_rows}
    if derived_gaps != table_gaps or sum(end - start for start, end, _ in table_gaps) != 22:
        raise WaveError("interior range-gap partition is not exhaustive")
    for entry, expected in EXPECTED_REFERENCES.items():
        observed = {address: len(re.findall(rf"DAT_{address:08x}", bodies[entry])) for address in expected}
        if observed != expected:
            raise WaveError(f"0x{entry:08X}: shared literal reference drift")

    nema = json.loads(local[NEMA])
    resolved = {int(address, 16) for address in nema["stock_evidence"]["resolved_symbols"]}
    if selected & resolved or nema["integration_status"]["production_ready"] is not False or "not byte-identical archive members" not in nema["archive_metadata"]["stock_compiler_relation"]:
        raise WaveError("exact Nema provider boundary drift")
    callers = {entry: sorted(int(row["entry"], 16) for row in function_rows if f"{entry:08x}" in row.get("callees", [])) for entry in selected}
    if callers != {0x005640E4: [0x00564974], 0x00564974: [0x005653A0, 0x005657D8]}:
        raise WaveError(f"caller topology drift: {callers}")
    if parent_by_entry[0x005657D8]["bucket"] != "first-party" or parent_by_entry[0x005653A0]["bucket"] != "investigation-required-no-evidence":
        raise WaveError("mixed ingress classification drift")

    residual_after = residual_before - selected
    after = {"functions": len(residual_after), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_after)}
    if after != {"functions": 1386, "bytes": 163138}:
        raise WaveError(f"wave-7 after accounting drift: {after}")
    if max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_after) != (2338, 0x005A8D06):
        raise WaveError("next-largest envelope drift")
    mapping_sha = sha256(json.dumps({"typed": records, "interiors": interior_records}, sort_keys=True, separators=(",", ":")).encode())
    return {
        "status": "opacity-wave7-vector-clipping-closure-typed", "read_only": True,
        "hardware_operations": False, "production_routed": False,
        "wave6_residual": wave6_report["after"], "before": before,
        "selected_root_range": {"start": "0x00564974", "end_exclusive": "0x0056539A"},
        "newly_typed": {"functions": 2, "bytes": 4784},
        "closure_depths": {"0": {"typed_functions": 1, "typed_bytes": 2598}, "1": {"typed_functions": 1, "typed_bytes": 2186}},
        "terminal_frontier": {"functions": 0},
        "reconciled_interiors": {"islands": 4, "physical_bytes": 22, "additional_bytes": 0, "shared_pointer_cell": "0x00564A40"},
        "provider": {"family_context": "NemaGFX/NemaVG vector-clipping community candidate", "authenticated_function_identities": [], "authenticated_provider": None, "authenticated_license": None, "callers": {f"0x{entry:08X}": [f"0x{caller:08X}" for caller in values] for entry, values in callers.items()}, "negative_evidence": ["both rows absent from the eleven authenticated stock Nema symbols", "public GCC Nema archive is not byte-identical to IAR-generated stock", "mixed first-party and still-unresolved ingress is topology context only"]},
        "after": after, "largest_remaining": {"entry": "0x005A8D06", "envelope_bytes": 2338},
        "mapping_sha256": mapping_sha, "records": records, "interior_records": interior_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
