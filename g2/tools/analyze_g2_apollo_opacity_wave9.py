#!/usr/bin/env python3
"""Close Apollo opacity wave 9 with call, interior, and data reconciliation.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
from collections import Counter, deque
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
DECOMP = G2 / "research/corpus/apollo-main/ghidra/decomp"
FUNCTIONS = DECOMP / "functions.jsonl"
CORPORA = {
    DECOMP / "bundles/apollo-decomp-08.c": (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    DECOMP / "bundles/apollo-decomp-11.c": (739_345, "029dbe031730c0d760e1913f8d043119b77f49170725b1464f5a53cc166a1bea"),
}
NEMA = G2 / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
ADMISSION = G2 / "research/admission/apollo_opacity_wave9"
BOUNDARY = ADMISSION / "typed_boundaries.tsv"
FRONTIER = ADMISSION / "reconciled_frontier.tsv"
INTERIORS = ADMISSION / "reconciled_interiors.tsv"
SHARED = ADMISSION / "shared_data.tsv"
ROOT = 0x0051A8EC
LOAD_ADDRESS = 0x00438000

PINS = {
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    NEMA: (24_898, "5a8e427ae337afb78f2901e74ae48d08d8c222944a50ada8adadfbdd98296bfa"),
    **CORPORA,
}
EXPECTED_SELECTED = {
    0x0051A8EC: (0x0051B116, 2090, 2078, "6b4dfe55bd486de7bc5e71122cff6983b20125d594471f549419398994effce3", 0, "elliptical-arc-and-stroke-geometry-coordinator", "unresolved-linked-vector-path-provider", "unavailable"),
    0x0051A694: (0x0051A8D6, 578, 578, "65dea6d70e22bb773826cc7db9ab0efb8e9c5ecee313b9f44a45f584264c710f", 1, "elliptical-arc-quarter-cubic-segment-builder", "unresolved-linked-vector-path-provider", "unavailable"),
    0x00516CF8: (0x00516E0A, 274, 274, "3a55aac902d5ff02b1d723f6ed28c0a8af772efc4d581d96b13bde2704be1451", 2, "cubic-segment-command-emitter", "unresolved-linked-vector-path-provider", "unavailable"),
    0x00563F40: (0x005640AE, 366, 366, "2110e9d1ad355aeee41199e505a4faf4553da2c7564ad32ca85ad00d771ac246", 2, "tanf-compatible-runtime-helper", "IAR-DLIB-family-exact-release-unavailable", "proprietary-runtime-source-unavailable"),
}
EXPECTED_CALLS = {
    0x0051A8EC: {0x004397A8: 3, 0x0050968C: 1, 0x00509690: 1, 0x0050969C: 4, 0x00514AEC: 2, 0x0051565C: 3, 0x00516B34: 2, 0x005179D0: 2, 0x0051A694: 2, 0x0052266E: 1, 0x005226B2: 2},
    0x0051A694: {0x0050968C: 3, 0x00509690: 3, 0x0051565C: 1, 0x00516CF8: 1, 0x00563F40: 1},
    0x00516CF8: {0x00514AEC: 1, 0x00517E18: 2},
    0x00563F40: {},
}
EXPECTED_RANGES = {
    0x0051A8EC: ((0x0051A8EC, 0x0051AC54), (0x0051AC58, 0x0051AE80), (0x0051AE84, 0x0051AFF2), (0x0051AFF4, 0x0051B072), (0x0051B074, 0x0051B116)),
    0x0051A694: ((0x0051A694, 0x0051A8D6),),
    0x00516CF8: ((0x00516CF8, 0x00516E0A),),
    0x00563F40: ((0x00563F40, 0x005640AE),),
}
EXPECTED_DAT = {
    0x0051A8EC: {0x0051AC54: 3, 0x0051AE80: 2, 0x0051B118: 1, 0x0051B11C: 1, 0x0051B120: 3, 0x0051B124: 2, 0x0051B128: 2, 0x0051B12C: 1, 0x0051B130: 1, 0x0051B134: 2, 0x0051B138: 4, 0x0051B13C: 2},
    0x0051A694: {0x0051A8D8: 2, 0x0051A8DC: 1, 0x0051A8E0: 1, 0x0051A8E4: 1, 0x0051A8E8: 2, 0x0051B134: 1},
    0x00516CF8: {0x005171EC: 2, 0x005171F0: 1, 0x00517850: 1},
    0x00563F40: {0x005640B0: 1, 0x005640B4: 1, 0x005640B8: 2, 0x005640BC: 2, 0x005640C0: 2, 0x005640C4: 2, 0x005640C8: 2, 0x005640CC: 1, 0x005640D0: 1, 0x005640D4: 1, 0x005640D8: 1, 0x005640DC: 1, 0x005640E0: 1},
}
EXPECTED_INTERIORS = {
    0x0051AC54: (0x0051AC58, "adc52737", "dc7a1fd57bc52c70f6764ff0f1d444d3da17a66f4d1844caa7ec96ace9473940", 0x0051A8EC, "0x0051AC54", "epsilon-float-literal-0x3727c5ad", "0x0051A8EC"),
    0x0051AE80: (0x0051AE84, "cecc4c3d", "520785396915dc5fee16200fa20d2f34b406e13bbd762dad4b925abb2a37f3b9", 0x0051A8EC, "0x0051AE80", "stroke-threshold-float-literal-0x3d4cccce", "0x0051A8EC"),
    0x0051AFF2: (0x0051AFF4, "00bf", "b35429818002e6e8ced180b98b8273bd2fc11f8ed0b0ff54eade7a5920a15ed4", 0x0051A8EC, "-", "thumb-nop-padding", "-"),
    0x0051B072: (0x0051B074, "00bf", "b35429818002e6e8ced180b98b8273bd2fc11f8ed0b0ff54eade7a5920a15ed4", 0x0051A8EC, "-", "thumb-nop-padding", "-"),
}
EXPECTED_SHARED = {
    0x0051A8D8: (0x0051A8EC, "35fa8e3cabaaaa3f00003443db0f494000000000", "d00b7fe18b8a43cf1dfa3ae2579eec01eaa6ae85a122b0744be75052191c23b4", "arc-helper-angle-and-scale-constants", "0x0051A694"),
    0x0051B118: (0x0051B140, "35fa8e3c00000000e12e65420000b443000034430000b4420000b4c2044f0720fc4e0720000100ff", "796a6d0281912861b3665dd63eaef6d58e0bb76a8472eec9365c2397fea85005", "arc-root-angle-context-and-command-constants", "0x0051A694,0x0051A8EC"),
    0x005171EC: (0x005171F4, "fc4e0720000100ff", "acb2bd0fc95fab04a0c86b10bdff4b2168eabe4ac84301852668afa3e47f8f6d", "command-context-pointer-and-flags", "0x00516CF8"),
    0x00517850: (0x00517854, "044f0720", "48b4654f2567d2b59ecbe37e6f96190282388ca5bbd42e18a0f7bae12fc58b2d", "command-context-pointer", "0x00516CF8"),
    0x005640B0: (0x005640E4, "83f9223f0000004f0000c9c600a0fdc00020a2ba000034b30030c2aeffffff7f00008038000080396d161f3c1eb5dbbe8329c4bd", "e4efe7c010b89201c2e6fad69366e30c1606549dbadbac2e34ea054c684e4724", "tanf-range-reduction-and-polynomial-table", "0x00563F40"),
}
EXPECTED_CALLERS = {
    0x0051A8EC: (0x00516E0C, 0x005171F8, 0x0051D2E0, 0x0051F798),
    0x0051A694: (0x0051A8EC,),
    0x00516CF8: (0x005171F8, 0x0051A694),
    0x00563F40: (0x00514F3C, 0x0051A694, 0x005657D8),
}
EXPECTED_FRONTIER = {
    0x004397A8: ("existing-iar-source-recreated", "sqrtf", "IAR-runtime", "openCFW-clean-room-runtime", "MIT", "prior-source-recreated"),
    0x0050968C: ("existing-parent-first-party", "cosf-compatible-math-entry", "parent-census", "unresolved-first-party-math-provider", "unavailable", "parent-first-party-reconciled"),
    0x00509690: ("existing-parent-first-party", "sinf-compatible-shared-interior-entry", "parent-census", "unresolved-first-party-math-provider", "unavailable", "parent-first-party-reconciled"),
    0x0050969C: ("existing-parent-first-party", "atan2f-compatible-math-entry", "parent-census", "unresolved-first-party-math-provider", "unavailable", "parent-first-party-reconciled"),
    0x00514AEC: ("prior-typed", "command-record-allocation-helper", "apollo-opacity-wave2", "unresolved-linked-vector-path-provider", "unavailable", "prior-typed-external-provider-unavailable"),
    0x0051565C: ("prior-typed", "state-bit-helper", "apollo-opacity-wave2", "unresolved-linked-vector-path-provider", "unavailable", "prior-typed-external-provider-unavailable"),
    0x00516B34: ("prior-typed", "command-record-builder", "apollo-opacity-wave2", "unresolved-linked-vector-path-provider", "unavailable", "prior-typed-external-provider-unavailable"),
    0x005179D0: ("prior-typed", "vector-geometry-helper", "apollo-opacity-wave2", "unresolved-linked-vector-path-provider", "unavailable", "prior-typed-external-provider-unavailable"),
    0x00517E18: ("prior-typed", "vector-path-command-interpreter", "apollo-opacity-wave3", "unresolved-linked-vector-path-provider", "unavailable", "prior-typed-external-provider-unavailable"),
    0x0052266E: ("prior-typed", "command-state-mask-helper", "apollo-opacity-wave2", "unresolved-linked-vector-path-provider", "unavailable", "prior-typed-external-provider-unavailable"),
    0x005226B2: ("prior-typed", "state-leaf", "apollo-opacity-wave1", "unresolved-linked-vector-path-provider", "unavailable", "prior-typed-external-provider-unavailable"),
}


class WaveError(RuntimeError):
    """Raised when authenticated wave-9 evidence changes."""


_BASE_CACHE: tuple[Any, dict[str, Any], dict[int, Any], Any, dict[Path, bytes], list[dict[str, str]]] | None = None


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


def corpus_function(corpora: dict[Path, str], entry: int) -> tuple[str, int, str, str]:
    hits = []
    for path, corpus in corpora.items():
        marker = re.search(rf"/\* FUN 0x{entry:08x} .*? bytes=(\d+) sha256=([0-9a-f]{{64}}) \*/", corpus)
        if marker is None:
            continue
        end = corpus.find("/* FUN 0x", marker.end())
        if end < 0:
            end = len(corpus)
        hits.append((corpus[marker.start():end], int(marker.group(1)), marker.group(2), path.name))
    if len(hits) != 1:
        raise WaveError(f"0x{entry:08X}: expected one corpus body, found {len(hits)}")
    return hits[0]


def base_evidence() -> tuple[Any, dict[str, Any], dict[int, Any], Any, dict[Path, bytes], list[dict[str, str]]]:
    """Cache immutable inherited waves within one analyzer process.

    Mutation tests intentionally swap only wave-9 tables; re-running all eight
    inherited audits for each such swap adds no evidence and obscures failures.
    A new CLI process still reauthenticates the complete inherited chain.
    """
    global _BASE_CACHE
    if _BASE_CACHE is not None:
        return _BASE_CACHE
    wave8 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave8.py", "opacity_wave9_wave8")
    wave8_report = wave8.run_audit()
    if wave8_report["after"] != {"functions": 1357, "bytes": 157768} or wave8_report["largest_remaining"] != {"entry": "0x0051A8EC", "envelope_bytes": 2090}:
        raise WaveError("wave-8 residual/root drift")

    waves = {i: load_module(G2 / f"tools/analyze_g2_apollo_opacity_wave{i}.py", f"opacity_wave9_wave{i}") for i in range(1, 8)}
    wave1 = waves[1]
    inherited = {path: wave1.pinned(path) for path in wave1.PINS}
    parent_rows = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"])
    _BASE_CACHE = (wave8, wave8_report, waves, wave1, inherited, parent_rows)
    return _BASE_CACHE


def run_audit() -> dict[str, Any]:
    wave8, wave8_report, waves, wave1, inherited, parent_rows = base_evidence()
    parent_by_entry = {int(row["entry"], 16): row for row in parent_rows}
    parent_none = {entry: row for entry, row in parent_by_entry.items() if row["bucket"] == "investigation-required-no-evidence"}
    residual = wave8.residual_before(wave1, waves, parent_none)
    residual -= {int(row["entry"], 16) for row in wave8.tsv_rows(wave8.BOUNDARY)}
    residual -= {int(row["entry"], 16) for row in wave8.tsv_rows(wave8.ZERO)}
    before = {"functions": len(residual), "bytes": sum(int(parent_none[entry]["official_opaque_bytes"]) for entry in residual)}
    if before != wave8_report["after"] or max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual) != (2090, ROOT):
        raise WaveError(f"authoritative residual drift: {before}")

    local = {path: pinned(path) for path in PINS}
    corpora = {path: local[path].decode() for path in CORPORA}
    function_rows = [json.loads(line) for line in local[FUNCTIONS].decode().splitlines()]
    functions = {int(row["entry"], 16): row for row in function_rows}
    payload = inherited[wave1.IMAGE][wave1.OTA_HEADER_BYTES:]
    boundary_rows = tsv_rows(BOUNDARY)
    selected = {int(row["entry"], 16) for row in boundary_rows}

    depths = {ROOT: 0}
    bodies: dict[int, str] = {}
    calls: dict[int, dict[int, int]] = {}
    queue = deque([ROOT])
    while queue:
        entry = queue.popleft()
        body, _, _, _ = corpus_function(corpora, entry)
        bodies[entry] = body
        observed = Counter(int(value, 16) for value in re.findall(r"\bFUN_([0-9a-f]{8})\(", body))
        observed.pop(entry, None)
        calls[entry] = dict(observed)
        for target in observed:
            if target in residual and target not in depths:
                depths[target] = depths[entry] + 1
                queue.append(target)
    if selected != set(EXPECTED_SELECTED) or selected != set(depths) or not selected <= residual:
        raise WaveError(f"complete actionable closure drift: {depths}")

    records = []
    observed_dat: dict[int, dict[int, int]] = {}
    range_gaps: set[tuple[int, int, int]] = set()
    for row in boundary_rows:
        entry = int(row["entry"], 16)
        end, envelope, corpus_bytes, digest, depth, role, provider, license_status = EXPECTED_SELECTED[entry]
        static = (int(row["end_exclusive"], 16), int(row["envelope_bytes"]), int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]), row["role"], row["provider_identity"], row["license_status"], row["disposition"])
        if static != (end, envelope, corpus_bytes, digest, depth, role, provider, license_status, "typed-external-provider-unavailable"):
            raise WaveError(f"0x{entry:08X}: typed boundary drift")
        parent = parent_none[entry]
        body, observed_bytes, observed_digest, bundle = corpus_function(corpora, entry)
        ranges = tuple((int(start, 16), int(end_i, 16) + 1) for start, end_i in functions[entry]["ranges"])
        installed = payload[entry - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if int(parent["body_end_exclusive"], 16) != end or int(parent["official_opaque_bytes"]) != envelope:
            raise WaveError(f"0x{entry:08X}: parent envelope drift")
        if (observed_bytes, observed_digest, ranges, functions[entry]["body_sha256"]) != (corpus_bytes, digest, EXPECTED_RANGES[entry], digest):
            raise WaveError(f"0x{entry:08X}: corpus/range drift")
        if len(installed) != envelope or sha256(installed) != digest or calls[entry] != EXPECTED_CALLS[entry] or depths[entry] != depth:
            raise WaveError(f"0x{entry:08X}: installed body or topology drift")
        for (_, previous_end), (next_start, _) in zip(ranges, ranges[1:]):
            range_gaps.add((previous_end, next_start, entry))
        dat = dict(Counter(int(value, 16) for value in re.findall(r"\bDAT_([0-9a-f]{8})", body)))
        if dat != EXPECTED_DAT[entry]:
            raise WaveError(f"0x{entry:08X}: direct data graph drift")
        observed_dat[entry] = dat
        records.append({"entry": row["entry"], "end_exclusive": row["end_exclusive"], "envelope_bytes": envelope, "corpus_body_bytes": corpus_bytes, "body_sha256": digest, "corpus_bundle": bundle, "closure_depth": depth, "role": role, "provider_identity": provider, "license_status": license_status, "disposition": row["disposition"], "source_identity_authenticated": False, "production_routed": False})

    if not ("1.0 / fVar25 + -0.25" in bodies[ROOT] and "FUN_0051a694" in bodies[ROOT] and "FUN_0050969c" in bodies[ROOT]):
        raise WaveError("root elliptical-arc behavioral evidence drift")
    if not ("fVar7 * 0.25" in bodies[0x0051A694] and "FUN_00563f40" in bodies[0x0051A694] and "FUN_00516cf8" in bodies[0x0051A694]):
        raise WaveError("arc-to-cubic behavioral evidence drift")
    if not ("puVar2[0x10]" in bodies[0x00516CF8] and "puVar2[0x11]" in bodies[0x00516CF8] and "FUN_00517e18" in bodies[0x00516CF8]):
        raise WaveError("cubic command emitter behavioral evidence drift")
    if not ("return -1.0 / param_1" in bodies[0x00563F40] and "param_1 = param_1 / fVar2" in bodies[0x00563F40]):
        raise WaveError("tanf-compatible behavioral evidence drift")

    terminal = {target for entry in selected for target in calls[entry] if target not in selected}
    frontier_rows = tsv_rows(FRONTIER)
    if terminal != set(EXPECTED_FRONTIER) or {int(row["entry"], 16) for row in frontier_rows} != terminal:
        raise WaveError(f"terminal frontier drift: {terminal}")
    prior_tables = {
        "apollo-opacity-wave1": {int(row["entry"], 16) for row in wave1.tsv_rows(wave1.BOUNDARY.read_bytes())},
        "apollo-opacity-wave2": {int(row["entry"], 16) for row in wave1.tsv_rows((G2 / "research/admission/apollo_opacity_wave2/typed_boundaries.tsv").read_bytes())},
        "apollo-opacity-wave3": {int(row["entry"], 16) for row in wave1.tsv_rows((G2 / "research/admission/apollo_opacity_wave3/typed_boundaries.tsv").read_bytes())},
    }
    frontier_records = []
    for row in frontier_rows:
        entry = int(row["entry"], 16)
        observed = (row["classification"], row["role"], row["source_wave"], row["provider_identity"], row["license_status"], row["disposition"])
        if observed != EXPECTED_FRONTIER[entry] or int(row["wave9_additional_function_bytes"]) != 0:
            raise WaveError(f"0x{entry:08X}: frontier row drift")
        if row["classification"] == "prior-typed" and entry not in prior_tables[row["source_wave"]]:
            raise WaveError(f"0x{entry:08X}: prior wave proof drift")
        if row["classification"] == "existing-parent-first-party":
            parent = parent_by_entry[entry]
            if (parent["bucket"], parent["evidence"], parent["confidence"]) != ("first-party", "link-order-sandwich", "low"):
                raise WaveError(f"0x{entry:08X}: parent first-party proof drift")
        frontier_records.append(dict(row))

    iar = load_module(G2 / "tools/analyze_g2_iar_runtime.py", "opacity_wave9_iar").analyze()
    sqrt = next(segment for segment in iar["segments"] if segment["name"] == "sqrtf")
    if sqrt["start"] != 0x004397A8 or sqrt["state"] != "source_recreated_redirected" or iar["identity"]["exact_release_proven"] is not False:
        raise WaveError("IAR runtime boundary drift")

    interior_rows = tsv_rows(INTERIORS)
    if {int(row["start"], 16) for row in interior_rows} != set(EXPECTED_INTERIORS):
        raise WaveError("interior partition membership drift")
    interior_records = []
    for row in interior_rows:
        start = int(row["start"], 16)
        end, bytes_hex, digest, owner, data_address, kind, consumers = EXPECTED_INTERIORS[start]
        physical = payload[start - LOAD_ADDRESS:end - LOAD_ADDRESS]
        observed = (int(row["end_exclusive"], 16), int(row["size"]), row["bytes_hex"], row["sha256"], int(row["envelope_owner"], 16), row["data_address"], row["kind"], row["consumers"], int(row["wave9_additional_bytes"]))
        if observed != (end, end - start, bytes_hex, digest, owner, data_address, kind, consumers, 0) or physical.hex() != bytes_hex or sha256(physical) != digest:
            raise WaveError(f"0x{start:08X}: interior evidence drift")
        interior_records.append(dict(row))
    table_gaps = {(int(row["start"], 16), int(row["end_exclusive"], 16), int(row["envelope_owner"], 16)) for row in interior_rows}
    if table_gaps != range_gaps or sum(end - start for start, end, _ in table_gaps) != 12:
        raise WaveError("interior gap accounting drift")

    shared_rows = tsv_rows(SHARED)
    if {int(row["start"], 16) for row in shared_rows} != set(EXPECTED_SHARED):
        raise WaveError("shared-data membership drift")
    shared_records = []
    for row in shared_rows:
        start = int(row["start"], 16)
        end, bytes_hex, digest, kind, consumers = EXPECTED_SHARED[start]
        physical = payload[start - LOAD_ADDRESS:end - LOAD_ADDRESS]
        observed = (int(row["end_exclusive"], 16), int(row["size"]), row["bytes_hex"], row["sha256"], row["kind"], row["consumers"], int(row["wave9_additional_function_bytes"]))
        if observed != (end, end - start, bytes_hex, digest, kind, consumers, 0) or physical.hex() != bytes_hex or sha256(physical) != digest:
            raise WaveError(f"0x{start:08X}: shared-data evidence drift")
        shared_records.append(dict(row))
    all_dat = {address for values in observed_dat.values() for address in values}
    covered_dat = {address for address in all_dat if any(start <= address < values[0] for start, values in EXPECTED_SHARED.items()) or any(start <= address < values[0] for start, values in EXPECTED_INTERIORS.items())}
    interior_dat = {int(row["data_address"], 16) for row in interior_rows if row["data_address"] != "-"}
    if covered_dat != all_dat or len(all_dat) != 33 or len(all_dat - interior_dat) != 31:
        raise WaveError("direct data cells are not exhaustively partitioned")

    callers = {entry: tuple(sorted(int(row["entry"], 16) for row in function_rows if f"{entry:08x}" in row.get("callees", []))) for entry in selected}
    if callers != EXPECTED_CALLERS:
        raise WaveError(f"caller topology drift: {callers}")
    nema = json.loads(local[NEMA])
    resolved = {int(address, 16) for address in nema["stock_evidence"]["resolved_symbols"]}
    vector_entries = selected - {0x00563F40}
    if vector_entries & resolved or nema["integration_status"]["production_ready"] is not False or "not byte-identical archive members" not in nema["archive_metadata"]["stock_compiler_relation"]:
        raise WaveError("Nema exact-provider boundary drift")

    residual_after = residual - selected
    after = {"functions": len(residual_after), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_after)}
    if after != {"functions": 1353, "bytes": 154460}:
        raise WaveError(f"wave-9 after accounting drift: {after}")
    next_size, next_entry = max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_after)
    if (next_size, next_entry) != (1962, 0x0051B140):
        raise WaveError(f"next-largest envelope drift: 0x{next_entry:08X}/{next_size}")

    call_edges = [{"caller": f"0x{caller:08X}", "callee": f"0x{callee:08X}", "count": count} for caller in sorted(calls) for callee, count in sorted(calls[caller].items())]
    mapping_sha = sha256(json.dumps({"typed": records, "frontier": frontier_records, "interiors": interior_records, "shared": shared_records, "calls": call_edges}, sort_keys=True, separators=(",", ":")).encode())
    return {
        "status": "opacity-wave9-elliptical-arc-and-runtime-closure-typed",
        "read_only": True, "hardware_operations": False, "production_routed": False,
        "wave8_residual": wave8_report["after"], "before": before,
        "selected_root_range": {"start": "0x0051A8EC", "end_exclusive": "0x0051B116"},
        "actionable_graph": {"positive_functions": 4, "positive_bytes": 3308, "terminal_functions": 11, "call_edges": len(call_edges), "static_callsites": sum(sum(values.values()) for values in calls.values())},
        "closure_depths": {
            "0": {"typed_functions": 1, "typed_bytes": 2090},
            "1": {"typed_functions": 1, "typed_bytes": 578},
            "2": {"typed_functions": 2, "typed_bytes": 640},
        },
        "typed_unavailable": {"vector_path_functions": 3, "vector_path_bytes": 2942, "iar_runtime_functions": 1, "iar_runtime_bytes": 366},
        "source_attributed": {"functions": 0, "bytes": 0},
        "provider": {
            "vector_family_context": "NemaGFX/NemaVG candidate only",
            "authenticated_function_identities": [], "authenticated_vector_provider": None, "authenticated_vector_license": None,
            "iar_semantic_identity": "tanf-compatible", "iar_exact_release": None, "iar_source_license": None,
            "negative_evidence": ["selected vector rows are absent from the eleven authenticated stock Nema symbols", "public Apollo5 Nema archive is GCC and not byte-identical to IAR stock", "exact IAR DLIB release and maintained tanf implementation source are unavailable"],
        },
        "range_partition": {"functions": 4, "interior_islands": 4, "interior_physical_bytes": 12, "additional_function_bytes": 0},
        "shared_data": {"islands": 5, "physical_bytes": 124, "direct_dat_cells": 33, "out_of_envelope_direct_dat_cells": 31, "additional_function_bytes": 0},
        "callers": {f"0x{entry:08X}": [f"0x{caller:08X}" for caller in values] for entry, values in callers.items()},
        "after": after, "largest_remaining": {"entry": f"0x{next_entry:08X}", "envelope_bytes": next_size},
        "records": records, "frontier_records": frontier_records, "interior_records": interior_records, "shared_records": shared_records, "call_edges": call_edges, "mapping_sha256": mapping_sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
