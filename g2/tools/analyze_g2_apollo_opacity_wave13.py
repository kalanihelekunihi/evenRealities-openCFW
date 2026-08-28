#!/usr/bin/env python3
"""Audit Apollo opacity wave 13's liblc3 LTPF source closure.

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
CORPUS = DECOMP / "bundles/apollo-decomp-00.c"
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "third_party/liblc3/src/ltpf.c"
PROVENANCE = G2 / "third_party/liblc3/PROVENANCE.json"
LICENSE = G2 / "third_party/liblc3/LICENSE"
ADMISSION = G2 / "research/admission/apollo_opacity_wave13"
BOUNDARY = ADMISSION / "source_boundaries.tsv"
FRONTIER = ADMISSION / "reconciled_frontier.tsv"
INDIRECT = ADMISSION / "reconciled_indirect_frontier.tsv"
NON_CORPUS = ADMISSION / "non_corpus_boundaries.tsv"
INTERIORS = ADMISSION / "reconciled_interiors.tsv"
SHARED = ADMISSION / "shared_data.tsv"
PROVIDER = ADMISSION / "source_provider.json"
COMPONENT = G2 / "components/shared/liblc3"
LTPF_PROVIDER_C = COMPONENT / "runtime_liblc3_ltpf_provider.c"
LTPF_PROVIDER_H = COMPONENT / "runtime_liblc3_ltpf_provider.h"
LTPF_ADMISSION = COMPONENT / "ltpf_source_admission.json"
OVERLAY_COMPONENT = G2 / "components/apollo_main/liblc3_ltpf"
OVERLAY_SOURCE = OVERLAY_COMPONENT / "liblc3_ltpf_overlay.c"
OVERLAY_CONFIG = OVERLAY_COMPONENT / "overlay.json"
OVERLAY_BUILDER = OVERLAY_COMPONENT / "build_component.py"
ROOT = 0x00438FB8
LOAD_ADDRESS = 0x00438000
OTA_HEADER_BYTES = 32

PINS = {
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    CORPUS: (512_871, "faa0467aaec00c0db0dc77c7ad70a10c1f00968a6c4ead677d6018552a3e070b"),
    IMAGE: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    SOURCE: (31_944, "810c6f862a649b9a27b33dc7c1e1c8f64a339b5a4aa6fef8027eafbcf8f7e80e"),
    PROVENANCE: (10_822, "91b5daf8383c6985807ffda06ed9918ec11e17a805a384948fa66a09ef7a56b3"),
    LICENSE: (11_358, "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"),
    LTPF_PROVIDER_C: (5_230, "16d1a5e8c46f3b0c3f7946773e7c692b86f6ad964ede8b2afeaf3decf4139831"),
    LTPF_PROVIDER_H: (1_507, "ce42c28108875a33dcf4fbbb524cee98812e9cc3912f11b08471adc1e34bde8f"),
    LTPF_ADMISSION: (2_013, "b90e801d1900212793ae0e17c27f8bda257e04d6c9376526e7781fa1f73e61dd"),
    OVERLAY_SOURCE: (2_390, "d0e51e059a9e965053f271902e29ee19ae527a312bd37cb763f9b7360eb138f3"),
    OVERLAY_CONFIG: (2_767, "1b351b8d55f01867916875e0b9241dc7f8cd4025f35fd5f962e029c1f12874bd"),
    OVERLAY_BUILDER: (23_575, "972045063944d06b1916ebe93222b818a167dc8701ef10f89f2e2d337d22a439"),
}

STATIC_SELECTED = {ROOT, 0x00438770, 0x004387B0, 0x00438924, 0x00438EF0, 0x00439710}
DISPATCH_SELECTED = {0x00438D8A, 0x00438504, 0x00438EBA, 0x00438ED4}
EXPECTED_SELECTED = STATIC_SELECTED | DISPATCH_SELECTED | {0x00438BF0}
DISPATCH_TARGETS = (0x00438D8A, 0x00438400, 0x00438EBA, 0x00438504, 0x00438604, 0x00438604, 0x00438ED4)
PROVIDER_ID = "google-liblc3-v1.1.3-compatible-96a3af0beb5487aca3b98a4b992a539a1f6d80d1"


class WaveError(RuntimeError):
    """Raised when authenticated wave-13 evidence changes."""


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
    wave12 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave12.py", "opacity_wave13_wave12")
    report12 = wave12.run_audit()
    if report12["after"] != {"functions": 1308, "bytes": 140498} or report12["largest_remaining"] != {"entry": "0x00438FB8", "envelope_bytes": 1710}:
        raise WaveError("wave-12 residual/root drift")
    parent_none, residual, _ = wave12.residual_before()
    residual -= {int(row["entry"], 16) for row in wave12.tsv_rows(wave12.BOUNDARY)}
    return parent_none, residual, report12


def parse_i16_array(source: str, name: str) -> bytes:
    match = re.search(rf"static const int16_t {name}\[[^=]+\] = \{{(.*?)\n\}};", source, re.S)
    if match is None:
        raise WaveError(f"missing upstream array {name}")
    values = [int(value) for value in re.findall(r"-?\d+", match.group(1))]
    return struct.pack("<" + "h" * len(values), *values)


def parse_h4_float(source: str) -> bytes:
    block = source[source.index("static const float h4[][8]"):source.index("const float *h = h4")]
    values: list[float] = []
    for row in re.findall(r"\{([^{}]+)\}", block):
        parsed = [float(value) for value in re.findall(r"[+-]?\d+\.\d+e[+-]\d+", row)]
        values.extend(parsed + [0.0] * (8 - len(parsed)))
    if len(values) != 32:
        raise WaveError("upstream h4 float table shape drift")
    return struct.pack("<32f", *values)


def run_audit() -> dict[str, Any]:
    parent_none, residual, report12 = residual_before()
    before = {"functions": len(residual), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual)}
    if before != report12["after"] or max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual) != (1710, ROOT):
        raise WaveError("authoritative residual drift")

    local = {path: pinned(path) for path in PINS}
    payload = local[IMAGE][OTA_HEADER_BYTES:]
    functions = {int(row["entry"], 16): row for row in (json.loads(line) for line in local[FUNCTIONS].decode().splitlines())}
    corpus = local[CORPUS].decode(errors="ignore")
    source = local[SOURCE].decode()
    rows = tsv_rows(BOUNDARY)
    selected = {int(row["entry"], 16) for row in rows}
    if selected != EXPECTED_SELECTED or not selected <= residual:
        raise WaveError("selected closure membership drift")

    # Re-derive static closure first, then add all residual dispatch targets and
    # their residual-only static closure. Non-corpus targets are typed below.
    derived = {ROOT}
    depth = {ROOT: 0}
    edge_class = {ROOT: "root"}
    queue = deque([ROOT])
    while queue:
        owner = queue.popleft()
        for value in functions[owner]["callees"]:
            target = int(value, 16)
            if target in residual and target not in derived:
                derived.add(target); depth[target] = depth[owner] + 1; edge_class[target] = "static"; queue.append(target)
    if derived != STATIC_SELECTED:
        raise WaveError("root static residual closure drift")
    for target in DISPATCH_SELECTED:
        derived.add(target); depth[target] = 1; edge_class[target] = "indirect-dispatch"; queue.append(target)
    while queue:
        owner = queue.popleft()
        for value in functions[owner]["callees"]:
            target = int(value, 16)
            if target in residual and target not in derived:
                derived.add(target); depth[target] = depth[owner] + 1; edge_class[target] = "static-from-indirect"; queue.append(target)
    if derived != selected:
        raise WaveError(f"complete actionable closure drift: {derived ^ selected}")

    records = []
    source_functions = source_bytes = zero_functions = 0
    expected_symbols = {"dot", "correlate", "interpolate", "interpolate_corr", "resample_x192k_12k8", "resample_8k_12k8", "resample_24k_12k8", "resample_32k_12k8", "resample_96k_12k8", "lc3_ltpf_analyse"}
    for row in rows:
        entry = int(row["entry"], 16); fn = functions[entry]; parent = parent_none[entry]
        end = int(row["end_exclusive"], 16); envelope = int(row["envelope_bytes"])
        observed = (end, envelope, int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]), row["edge_class"])
        expected = (int(parent["body_end_exclusive"], 16), int(parent["official_opaque_bytes"]), int(fn["body_bytes"]), fn["body_sha256"], depth[entry], edge_class[entry])
        if observed != expected:
            raise WaveError(f"0x{entry:08X}: body/depth/edge drift")
        body = corpus_function(corpus, entry)
        if fn["body_sha256"] not in body.splitlines()[0]:
            raise WaveError(f"0x{entry:08X}: corpus marker drift")
        if envelope:
            if row["symbol"].split(" ")[0] not in expected_symbols or row["source_path"] != "g2/third_party/liblc3/src/ltpf.c" or row["provider_identity"] != PROVIDER_ID or row["license_status"] != "Apache-2.0" or row["disposition"] != "source-attributed-compatible-baseline-research-only":
                raise WaveError(f"0x{entry:08X}: source/provider/license drift")
            source_functions += 1; source_bytes += envelope
        else:
            if (entry, row["symbol"], row["provider_identity"], row["disposition"]) != (0x00439710, "memmove", "IAR-DLIB-proprietary-runtime", "prior-reconciled-zero-opaque"):
                raise WaveError("zero-byte runtime reconciliation drift")
            zero_functions += 1
        records.append(dict(row, source_identity_authenticated=bool(envelope), exact_generating_checkout_proven=False))

    provenance = json.loads(local[PROVENANCE])
    provider = json.loads(PROVIDER.read_text())
    if provenance["license"] != "Apache-2.0" or provenance["upstream"]["selected_commit"] != "96a3af0beb5487aca3b98a4b992a539a1f6d80d1" or provenance["selection"]["exact_public_source_candidate"] or "Apache License" not in local[LICENSE].decode():
        raise WaveError("upstream provenance/license qualification drift")
    if provider["selected_commit"] != provenance["upstream"]["selected_commit"] or provider["license"] != "Apache-2.0" or provider["exact_public_source_candidate"] or provider["exact_private_checkout_proven"] or not provider["production_routed"] or provider["production_component"] != "g2/components/apollo_main/liblc3_ltpf" or provider["historical_individual_bodies_routed"]:
        raise WaveError("research source-provider qualification drift")
    for symbol in provider["source_symbols"]:
        if symbol not in source:
            raise WaveError(f"upstream symbol missing: {symbol}")
    source_admission = json.loads(local[LTPF_ADMISSION])
    provider_c = local[LTPF_PROVIDER_C].decode()
    provider_h = local[LTPF_PROVIDER_H].decode()
    if (not source_admission["production_capable_source"] or
        not source_admission["source_provider_supports_all_dispatch_slots"] or
        source_admission["individual_historical_body_routing"] or
        not source_admission["overlay_routed"] or
        source_admission["overlay_component"] != "g2/components/apollo_main/liblc3_ltpf" or
        source_admission["allowed_external_relocations"]["production_overlay"] != [] or
        source_admission["history_samples_by_srate"] != [9, 19, 29, 39, 59, 59, 119] or
        source_admission["allowed_external_relocations"]["ltpf_analysis"] != ["memmove", "sqrtf"] or
        "sizeof(lc3_ltpf_analysis_t) == 0x488U" not in provider_c or
        "open_cfw_liblc3_ltpf_analyse_bounded" not in provider_h):
        raise WaveError("production-capable LTPF source-provider contract drift")
    overlay_config = json.loads(local[OVERLAY_CONFIG])
    expected_profiles = {
        "apple-clang": {"source_owned_bytes": 7576, "sha256": "8261449f203ff0a33a0b6f22eee57076216491b2a03f6c359b98b98aa6ba0d24"},
        "linux-clang": {"source_owned_bytes": 7596, "sha256": "3ba3bb1a790b236ab82f59e965715e9730658058cfc20b7d6a7fb7ec8e75d8d3"},
    }
    if (source_admission["reviewed_profiles"] != expected_profiles or
        provider["production_profiles"] != expected_profiles or
        overlay_config["patch_site"] != {"name":"lc3_encode_ltpf_analysis","runtime_address":0x0059145C,"expected_hex":"a7f6acfd","target_function":"lc3_ltpf_analyse"} or
        {name:{"source_owned_bytes": item["overlay"]["size"], "sha256":item["overlay"]["sha256"]} for name,item in overlay_config["profiles"].items()} != expected_profiles or
        "EXPECTED_DISPATCH_SYMBOLS" not in local[OVERLAY_BUILDER].decode() or
        "open_cfw_liblc3_memmove" not in local[OVERLAY_SOURCE].decode() or
        "open_cfw_liblc3_sqrtf_nonnegative" not in local[OVERLAY_SOURCE].decode()):
        raise WaveError("production placement/link receipt drift")

    # Seven exact Thumb table cells prove the indirect graph.
    dispatch = struct.unpack_from("<7I", payload, 0x00439680 - LOAD_ADDRESS)
    if tuple(value & ~1 for value in dispatch) != DISPATCH_TARGETS or any(not value & 1 for value in dispatch):
        raise WaveError("resample_12k8 dispatch table drift")
    indirect = tsv_rows(INDIRECT)
    if tuple(int(row["target"], 16) for row in indirect) != DISPATCH_TARGETS or sum(int(row["wave13_additional_function_bytes"]) for row in indirect) != 612:
        raise WaveError("indirect frontier accounting drift")

    # Non-corpus entries are bounded and hashed but intentionally not promoted
    # to exact complete functions or official opaque bytes.
    non_corpus = tsv_rows(NON_CORPUS)
    if {int(row["entry"], 16) for row in non_corpus} != {0x00438400, 0x00438604}:
        raise WaveError("non-corpus boundary membership drift")
    for row in non_corpus:
        start = int(row["entry"], 16); end = int(row["bounded_end_exclusive"], 16)
        physical = payload[start - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if (len(physical), sha256(physical), int(row["bounded_physical_bytes"]), row["bounded_sha256"], int(row["wave13_additional_function_bytes"])) != (len(physical), sha256(physical), end-start, sha256(physical), 0):
            raise WaveError("non-corpus SHA/bound drift")
        if row["disposition"] != "sha-pinned-bounded-source-compatible-boundary" or "not exact body proof" not in row["completeness_reason"]:
            raise WaveError("non-corpus fail-closed disposition drift")

    # Derive every omitted range inside official selected envelopes.
    derived_gaps: dict[tuple[int, int, int], bytes] = {}
    for entry in selected:
        fn = functions[entry]; end = int(fn["body_end_inclusive"], 16) + 1; cursor = entry
        for a_text, b_text in fn["ranges"]:
            a, b = int(a_text, 16), int(b_text, 16) + 1
            if cursor < a:
                derived_gaps[(entry, cursor, a)] = payload[cursor-LOAD_ADDRESS:a-LOAD_ADDRESS]
            cursor = b
        if cursor < end:
            derived_gaps[(entry, cursor, end)] = payload[cursor-LOAD_ADDRESS:end-LOAD_ADDRESS]
    interiors = tsv_rows(INTERIORS)
    if {(int(row["owner"],16), int(row["start"],16), int(row["end_exclusive"],16)) for row in interiors} != set(derived_gaps):
        raise WaveError("interior range partition drift")
    for row in interiors:
        key = (int(row["owner"],16), int(row["start"],16), int(row["end_exclusive"],16)); physical = derived_gaps[key]
        if (int(row["size"]), row["bytes_hex"], row["sha256"], int(row["wave13_additional_function_bytes"])) != (len(physical), physical.hex(), sha256(physical), 0):
            raise WaveError("interior physical byte drift")

    # Close every direct data label and authenticate all private LC3 tables.
    shared = tsv_rows(SHARED)
    shared_spans = [(int(row["address"],16), int(row["address"],16)+int(row["size"])) for row in shared]
    direct_labels = set()
    for entry in selected:
        body = corpus_function(corpus, entry)
        direct_labels |= {int(value,16) for value in re.findall(r"\bDAT_([0-9a-f]{8})", body)}
    if not all(any(a <= label < b for a,b in shared_spans) for label in direct_labels) or 0x00439680 not in {a for a,_ in shared_spans}:
        raise WaveError("direct data graph coverage drift")
    for row in shared:
        address = int(row["address"],16); size = int(row["size"]); physical = payload[address-LOAD_ADDRESS:address-LOAD_ADDRESS+size]
        if row["sha256"] != sha256(physical) or int(row["wave13_additional_function_bytes"]):
            raise WaveError(f"0x{address:08X}: shared data drift")
    table_targets = {
        "h_48k_12k8_q15": 0x006C1120, "h_24k_12k8_q15": 0x006C1300, "h_96k_12k8_q15": 0x006C14E0,
        "h_16k_12k8_q15": 0x006D2F98, "h_32k_12k8_q15": 0x006D3038, "h_8k_12k8_q15": 0x006D30D8,
    }
    for name, address in table_targets.items():
        expected_table = parse_i16_array(source, name)
        if payload[address-LOAD_ADDRESS:address-LOAD_ADDRESS+len(expected_table)] != expected_table:
            raise WaveError(f"{name}: installed/upstream table mismatch")
    h4_q15_block = source[source.index("static const int16_t h4_q15"):source.index("const int16_t *h = h4_q15")]
    h4_q15_values = [int(value) for row in re.findall(r"\{([^{}]+)\}", h4_q15_block) for value in re.findall(r"-?\d+", row)]
    h4_q15 = struct.pack("<16h", *h4_q15_values)
    if payload[0x00438BD0-LOAD_ADDRESS:0x00438BF0-LOAD_ADDRESS] != h4_q15 or payload[0x006D54D8-LOAD_ADDRESS:0x006D5558-LOAD_ADDRESS] != parse_h4_float(source):
        raise WaveError("interpolation table identity drift")

    frontier = tsv_rows(FRONTIER)
    outbound = Counter()
    for entry in selected:
        for value in functions[entry]["callees"]:
            target = int(value, 16)
            if target not in selected:
                outbound[target] += 1
    if dict(outbound) != {0x004397A8: 1} or frontier != [{"entry":"0x004397A8","call_relations":"1","direct_call_sites":"3","role":"sqrtf-runtime-helper","source_owner":"ltpf-bits-cluster-census","provider_identity":"IAR-DLIB-proprietary-runtime","license_status":"unavailable","disposition":"prior-typed-external-provider-unavailable","wave13_additional_function_bytes":"0"}]:
        raise WaveError("static terminal frontier drift")
    if corpus_function(corpus, ROOT).count("FUN_004397a8(") != 3:
        raise WaveError("sqrtf direct call-site count drift")

    selected_bytes = sum(int(parent_none[e]["official_opaque_bytes"]) for e in selected)
    if selected_bytes != 4016 or (source_functions, source_bytes, zero_functions) != (10, 4016, 1):
        raise WaveError("source/zero-byte partition drift")
    remaining = residual - selected
    after = {"functions": len(remaining), "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in remaining)}
    largest_bytes, largest_entry = max((int(parent_none[e]["official_opaque_bytes"]), e) for e in remaining)
    if after != {"functions": 1297, "bytes": 136482} or (largest_entry, largest_bytes) != (0x005AC66E, 1684):
        raise WaveError(f"after residual drift: {after}, 0x{largest_entry:08X}/{largest_bytes}")

    canonical = [{key: row[key] for key in ("entry","symbol","source_path","provider_identity","license_status","disposition","body_sha256")} for row in sorted(rows,key=lambda item:int(item["entry"],16))]
    return {
        "status": "opacity-wave13-liblc3-ltpf-source-closure",
        "wave12_residual": report12["after"], "before": before,
        "selected_root_range": {"start":"0x00438FB8","end_exclusive":"0x00439666"},
        "actionable_graph": {"selected_functions":11,"official_bytes":4016,"static_root_closure_functions":6,"indirect_residual_functions":4,"shared_indirect_callee_functions":1,"static_terminal_relations":1,"indirect_slots":7},
        "source_attributed": {"functions":10,"bytes":4016,"provider":PROVIDER_ID,"license":"Apache-2.0","exact_generating_checkout_proven":False},
        "reconciled_zero_opaque": {"functions":1,"bytes":0,"provider":"IAR-DLIB-proprietary-runtime"},
        "non_corpus_boundaries": {"entries":2,"bounded_physical_bytes":624,"official_bytes":0,"complete_body_proven":False},
        "range_partition": {"functions_with_interiors":2,"interior_islands":len(interiors),"interior_physical_bytes":sum(int(row["size"]) for row in interiors),"additional_function_bytes":0},
        "shared_data": {"spans":len(shared),"physical_bytes":sum(int(row["size"]) for row in shared),"byte_exact_upstream_tables":8,"additional_function_bytes":0},
        "after":after,"largest_remaining":{"entry":f"0x{largest_entry:08X}","envelope_bytes":largest_bytes},
        "records":records,
        "mapping_sha256":sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()),
        "production_capable_source":{"available":True,"provider_entry":"open_cfw_liblc3_ltpf_analyse_bounded","dispatch_slots":7,"historical_individual_bodies_routed":False},
        "production_routed":True,
        "production_route":{"callsite":"0x0059145C","profiles":expected_profiles,"unresolved_runtime_symbols":0,"historical_individual_bodies_routed":False},
        "production_blocker":"no software placement/link blocker for the bounded LTPF analysis route; device qualification is deferred by project direction",
        "read_only":True,"hardware_operations":False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--pretty", action="store_true"); args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
