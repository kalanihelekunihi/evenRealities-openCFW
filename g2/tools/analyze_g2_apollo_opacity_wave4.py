#!/usr/bin/env python3
"""Close the orientation/calibration numerical opacity graph.

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
CORPUS = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-00.c"
FUNCTIONS = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
NPMX_PROVIDER = G2 / "tools/manifests/g2-npmx-main-driver-provider-map.tsv"
LIBLC3_MAP = G2 / "tools/manifests/g2-liblc3-ltpf-bits-cluster-map.tsv"
LIBLC3_SUMMARY = G2 / "tools/manifests/g2-liblc3-ltpf-bits-cluster-summary.json"
IAR_PROVIDER = G2 / "tools/manifests/g2-onboarding-news-page-provider-map.tsv"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave4/typed_boundaries.tsv"
ZERO_BOUNDARY = G2 / "research/admission/apollo_opacity_wave4/reconciled_zero_opaque.tsv"
LOAD_ADDRESS = 0x00438000

PINS = {
    CORPUS: (512_871, "faa0467aaec00c0db0dc77c7ad70a10c1f00968a6c4ead677d6018552a3e070b"),
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    NPMX_PROVIDER: (1_717, "a0874b41f52caa1b48854068cf47cd82b2665af05d03245ad248edb2c154cb44"),
    LIBLC3_MAP: (8_491, "1fb77fe46932939a608410b9055d8a9ec0e5b6032afbd937ee8149da18160237"),
    LIBLC3_SUMMARY: (2_633, "93384bc02c6dbd4f91f6b652fe045ed5dc0f156e2bbd93f83f8b319ff1b35493"),
    IAR_PROVIDER: (2_131, "597175c92ddb66d560072cf7773052e7f8a796eafe467c503d799bf35e4b2ab8"),
}

ROOT = 0x0043A698
EXPECTED_SELECTED = {
    0x0043A698: (0x0043BA6C, 5076, 4952, "301ca2b8bbbe07bc5ceda41d9234c3b6b953372cc6b19367eb76a8e4610c7e11", 0),
    0x00439CE0: (0x00439E7E, 414, 414, "4aac05ddd121150afde1c527fbd3dbfc0a97cb3e4be538198383572d1d685e52", 1),
    0x00439E90: (0x00439E9C, 12, 12, "6f346ef9c2e2f8e361b9c3e090cf7f8fc194b23dfda2a233baeec822a94026f9", 1),
    0x00439E9C: (0x00439EFC, 96, 96, "99c13fff7dbb002a4916693cfeb66c4a5dc95184afae4f457d94cd099028a376", 1),
    0x00439EFC: (0x00439F24, 40, 40, "1ab10543294b0387fe944447b77c0f56d78db95e8032c8c24f63eccf8e3116f7", 1),
    0x00439F24: (0x00439F86, 98, 98, "f17d7e6e816cb4af3dbe13ab0e1c96d0977b60962d71b51b3af8b7031702bd6c", 1),
    0x00439F88: (0x00439FB4, 44, 44, "b52cab9d9bda2ed98cc548c755e5fb877844011709926c371de1721ef9b09922", 1),
    0x00439FB4: (0x00439FE4, 48, 48, "faf22290dcef45e5b4841067180972213d66a9d32bf062b18a01fe6bd18020c5", 1),
    0x00439FE4: (0x0043A0EE, 266, 266, "f91ec9ce03d64317ef0fcc1b8cf87db9437c5fcde4ddcd2658b289f0596a9519", 1),
    0x0043A0F4: (0x0043A10E, 26, 26, "d709bf2348b65012a420c3ea108c30d266dbf26b7ea3c6fc7c2f11602480e858", 1),
    0x0043A110: (0x0043A11E, 14, 14, "aea8784b66f355be4df946b1dc5801da1265391e1f37497bb51352ff7ffcf145", 1),
    0x0043A5DC: (0x0043A690, 180, 180, "e6c24e45d7b55e023a349aabc2de035c63a1e3b85670e37a7f80e1134b68bc4a", 1),
    0x0043BA6C: (0x0043BA96, 42, 42, "3790fd9ea5bf31db3c5a55e3c20204e524f621f721d8ce1d3d850079b4aad8a1", 1),
    0x0043BA98: (0x0043C08E, 1526, 276, "7b4b38522a01117fd89ea74441d7ad4a0ea9e5f042044d74911a03cd47e2b22f", 1),
    0x0043A19C: (0x0043A1B0, 20, 20, "5dd89c8cd4e82e68ba7815fd537ec87765005b07b3de4c8b312227dc53b93610", 2),
    0x0043A5A0: (0x0043A5B0, 16, 16, "da866fc4fccf0259dd93fd26bc7447b0f0335ec8275f5cd31b4849a8f6de046b", 2),
    0x0043C0B0: (0x0043C0E4, 52, 52, "f477d157e5470add8ec143ce6102542cd5c77ef7e185f09bbd80f3113d6b813d", 2),
    0x0043C0E4: (0x0043C0EC, 8, 8, "d228ee6e554e7763e9cd764cd9f07d3074feac13e9fd05250611ffa1079041fc", 2),
    0x0043A5B0: (0x0043A5DC, 44, 44, "ba53107c41d7b78d37fea9f4c52330599640f8dab9d4be1bc94e05c8c932d234", 3),
    0x0043C0EC: (0x0043C14A, 94, 94, "de6af19826a3eebd3415d6f983375b833af22ec7667f9cbbde6cc35b00c6bf5b", 3),
}

EXPECTED_ZERO = {
    0x00439BE4: (0x00439C8A, 166, 104, "8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd", 2),
    0x0043BAF4: (0x0043BB00, 12, 12, "52ad55cec64f5c1e5b80cecc8ac256e5ee19428ba612eef4c0b8efcbc3c9a573", 1),
    0x0043BB00: (0x0043BB14, 20, 20, "da7dc069a9d88cfb2b99c7911d06ce8c9732fa3e5905c0f575145a72094cc661", 1),
    0x0043BB14: (0x0043BC54, 320, 320, "1b0d4f5522467e1ca48b61051e88750acf15f899c5098653ae773d1f5c1823de", 1),
    0x0043BC58: (0x0043BC82, 42, 42, "74e0b8617973479d493caf7611d076365754f8f659189a86a0fba8bf82a61e27", 1),
    0x0043BC84: (0x0043BE14, 400, 400, "d9aa27adda4dedb70d08720212d85bd8b79ae729fdf5954899d1bb9e1a8a36e0", 1),
    0x0043BE18: (0x0043BFA8, 400, 400, "a69dca174bcbc6d333582dae100308ef46202d037ea362c7a693bb611a7145c0", 1),
    0x0043BFAC: (0x0043BFCE, 34, 34, "d487d2db8bfc9cc251e1b19c01f67fdb31804395f30093ff939c938cfce5544f", 1),
}

EXPECTED_CALLS = {
    0x0043A698: {0x004397A8: 1, 0x00439CE0: 1, 0x00439E90: 2, 0x00439E9C: 1,
                 0x00439EFC: 6, 0x00439F24: 1, 0x00439F88: 6, 0x00439FB4: 3,
                 0x00439FE4: 1, 0x0043A0F4: 11, 0x0043A110: 2, 0x0043A5DC: 2,
                 0x0043BA6C: 1, 0x0043BA98: 2, 0x0043BAF4: 2, 0x0043BB00: 1,
                 0x0043BB14: 3, 0x0043BC58: 2, 0x0043BC84: 1, 0x0043BE18: 1,
                 0x0043BFAC: 1},
    0x00439CE0: {0x00439E90: 2, 0x00439E9C: 1, 0x00439EFC: 1, 0x00439F24: 1,
                 0x00439F88: 1, 0x00439FB4: 1, 0x00439FE4: 1},
    0x00439E90: {0x00439BE4: 1},
    0x00439E9C: {0x0043A0F4: 3},
    0x00439EFC: {},
    0x00439F24: {0x0043A0F4: 3},
    0x00439F88: {},
    0x00439FB4: {},
    0x00439FE4: {0x0043A0F4: 2},
    0x0043A0F4: {0x0043A110: 1, 0x0043A19C: 1},
    0x0043A110: {},
    0x0043A5DC: {0x0043A0F4: 2},
    0x0043BA6C: {},
    0x0043BA98: {},
    0x0043A19C: {},
    0x0043A5A0: {0x0043A5B0: 1},
    0x0043C0B0: {},
    0x0043C0E4: {},
    0x0043A5B0: {},
    0x0043C0EC: {},
    0x00439BE4: {},
    0x0043BAF4: {0x0043C0B0: 1},
    0x0043BB00: {0x0043C0E4: 1},
    0x0043BB14: {0x00439E90: 1, 0x0043BB00: 2},
    0x0043BC58: {},
    0x0043BC84: {0x0043A0F4: 1, 0x0043A5A0: 1},
    0x0043BE18: {0x0043A0F4: 1, 0x0043A5A0: 1},
    0x0043BFAC: {},
}

PROVIDER_COMPANION = {0x0043C0E4: {0x0043C0EC}}


class WaveError(RuntimeError):
    """Raised when an authenticated wave-4 invariant changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned(path: Path) -> bytes:
    data = path.read_bytes()
    if (len(data), sha256(data)) != PINS[path]:
        raise WaveError(f"pin drift: {path}")
    return data


def tsv_rows(data: bytes) -> list[dict[str, str]]:
    lines = [line for line in data.decode().splitlines() if not line.startswith("#")]
    if not lines:
        raise WaveError("empty TSV")
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


def run_audit() -> dict[str, Any]:
    wave3 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave3.py", "opacity_wave4_wave3")
    wave3_report = wave3.run_audit()
    if wave3_report["after"] != {"functions": 1424, "bytes": 185480}:
        raise WaveError("wave-3 residual drift")
    wave2 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave2.py", "opacity_wave4_wave2")
    wave1 = load_module(G2 / "tools/analyze_g2_apollo_opacity_wave1.py", "opacity_wave4_wave1")
    inherited = {path: wave1.pinned(path) for path in wave1.PINS}
    parent_rows = wave1.tsv_rows(
        inherited[wave1.MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"]
    )
    cordio_rows = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-cordio-ll-sea-census.tsv"])
    freetype_rows = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-freetype-engine-census.tsv"])
    liblc3_rows = wave1.tsv_rows(inherited[wave1.MANIFESTS / "g2-liblc3-encoder-internals-map.tsv"])
    parent_by_entry = {int(row["entry"], 16): row for row in parent_rows}
    parent_none = {
        entry: row for entry, row in parent_by_entry.items()
        if row["bucket"] == "investigation-required-no-evidence"
    }
    mspi = load_module(
        G2 / "tools/analyze_g2_apollo510_mspi_triplet_candidate.py", "opacity_wave4_mspi"
    ).run_audit()
    classified = (
        {int(row["entry"], 16) for row in cordio_rows}
        | {int(row["entry"], 16) for row in freetype_rows if row["status"] != "investigation-required"}
        | {int(row["entry"], 16) for row in liblc3_rows if row["status"] != "investigation-required"}
        | {int(entry, 16) for entry in mspi["triplet"]}
    )
    raw_wave3_residual = (
        set(parent_none) - classified - set(wave1.EXPECTED_SELECTED)
        - set(wave2.EXPECTED_SELECTED) - set(wave3.EXPECTED_SELECTED)
        - {0x004397A8, 0x00439C04}
    )
    raw_summary = {
        "functions": len(raw_wave3_residual),
        "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in raw_wave3_residual),
    }
    if raw_summary != wave3_report["after"]:
        raise WaveError(f"wave-3 set reconciliation drift: {raw_summary}")

    local = {path: pinned(path) for path in PINS}
    corpus = local[CORPUS].decode()
    payload = inherited[wave1.IMAGE][wave1.OTA_HEADER_BYTES:]

    # Positive ingress: the sole caller is the first-party orientation seam.
    function_rows = [json.loads(line) for line in local[FUNCTIONS].decode().splitlines()]
    callers = sorted(
        int(row["entry"], 16) for row in function_rows
        if f"{ROOT:08x}" in row.get("callees", [])
    )
    if callers != [0x0055F848]:
        raise WaveError(f"root ingress drift: {callers}")
    npmx = load_module(G2 / "tools/analyze_g2_npmx_main_driver.py", "opacity_wave4_npmx").analyze()
    if (
        npmx["provider_boundary"]["first_party_orientation_calls"] != 8
        or npmx["identity"]["embedded_third_party_definitions"] != []
        or npmx["production"]["production_routed"] is not False
    ):
        raise WaveError("nPMX orientation-provider boundary drift")
    provider_rows = tsv_rows(local[NPMX_PROVIDER])
    orientation = next(row for row in provider_rows if row["provider"] == "G2 orientation and calibration provider")
    if (
        "0x0055F848" not in orientation["stock_targets"]
        or orientation["origin"] != "Even Realities first-party algorithm seam"
        or "not part of Nordic nPMX" not in orientation["qualification"]
    ):
        raise WaveError("orientation-provider evidence drift")

    ltpf_map = tsv_rows(local[LIBLC3_MAP])
    ltpf_summary = json.loads(local[LIBLC3_SUMMARY])
    if (
        set(EXPECTED_SELECTED) & {int(row["entry"], 16) for row in ltpf_map}
        or ltpf_summary["reconciliation"]["island_frontier_remainder"] != 44
    ):
        raise WaveError("liblc3 negative boundary drift")
    peripheral = wave1.tsv_rows(
        inherited[wave1.MANIFESTS / "g2-peripheral-register-cluster-map.tsv"]
    )
    peripheral_by_entry = {int(row["entry"], 16): row for row in peripheral}
    sibling = peripheral_by_entry[0x0043A1B0]
    if sibling["evidence"] != "no-register-evidence" or "constant collision" not in sibling["detail"]:
        raise WaveError("nearby peripheral false-positive boundary drift")
    iar_provider = next(
        row for row in tsv_rows(local[IAR_PROVIDER])
        if row["provider"] == "IAR DLIB memory string and format primitives"
    )
    if (
        "0x0043C0E4" not in iar_provider["stock_targets"]
        or iar_provider["origin"] != "IAR proprietary compiler runtime"
    ):
        raise WaveError("IAR memset provider identity drift")

    iar = load_module(G2 / "tools/analyze_g2_iar_runtime.py", "opacity_wave4_iar").analyze()
    memcpy = next(segment for segment in iar["segments"] if segment["name"] == "__aeabi_memcpy")
    if (memcpy["start"], memcpy["end"], memcpy["state"]) != (
        0x00439BE4, 0x00439C8A, "source_recreated_redirected"
    ):
        raise WaveError("source-recreated IAR memcpy drift")

    zero_rows = tsv_rows(ZERO_BOUNDARY.read_bytes())
    zero_entries = {int(row["entry"], 16) for row in zero_rows}
    if zero_entries != set(EXPECTED_ZERO) or not zero_entries <= raw_wave3_residual:
        raise WaveError("zero-opaque reconciliation membership drift")
    residual_before = raw_wave3_residual - zero_entries
    before = {
        "functions": len(residual_before),
        "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_before),
    }
    if before != {"functions": 1416, "bytes": 185480}:
        raise WaveError(f"wave-4 before accounting drift: {before}")
    if max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_before) != (5076, ROOT):
        raise WaveError("wave-4 root is no longer largest")

    selected_rows = tsv_rows(BOUNDARY.read_bytes())
    selected = {int(row["entry"], 16) for row in selected_rows}
    if selected != set(EXPECTED_SELECTED) or not selected <= residual_before:
        raise WaveError("selected boundary membership drift")

    observed_calls: dict[int, dict[int, int]] = {}
    records: list[dict[str, Any]] = []
    for row in selected_rows:
        entry = int(row["entry"], 16)
        end, envelope_bytes, corpus_bytes, digest, depth = EXPECTED_SELECTED[entry]
        if (
            int(row["end_exclusive"], 16), int(row["envelope_bytes"]),
            int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]),
        ) != (end, envelope_bytes, corpus_bytes, digest, depth):
            raise WaveError(f"0x{entry:08X}: static boundary drift")
        parent = parent_none[entry]
        if int(parent["body_end_exclusive"], 16) != end or int(parent["official_opaque_bytes"]) != envelope_bytes:
            raise WaveError(f"0x{entry:08X}: parent boundary drift")
        installed = payload[entry - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if len(installed) != envelope_bytes or sha256(installed) != digest:
            raise WaveError(f"0x{entry:08X}: official body drift")
        body, decoded_bytes, corpus_digest = corpus_function(corpus, entry)
        if (decoded_bytes, corpus_digest) != (corpus_bytes, digest):
            raise WaveError(f"0x{entry:08X}: corpus identity drift")
        calls = Counter(int(match, 16) for match in re.findall(r"\bFUN_([0-9a-f]{8})\(", body))
        calls.pop(entry, None)
        observed_calls[entry] = dict(calls)
        if observed_calls[entry] != EXPECTED_CALLS[entry]:
            raise WaveError(f"0x{entry:08X}: call topology drift")
        is_iar = entry in {0x0043C0E4, 0x0043C0EC}
        expected_disposition = (
            "typed-external-iar-dlib-source-unavailable" if is_iar
            else "typed-external-provider-unavailable"
        )
        if row["disposition"] != expected_disposition:
            raise WaveError(f"0x{entry:08X}: disposition drift")
        if is_iar:
            if row["provider_identity"] != "IAR-DLIB-memset-family" or row["license_status"] != "proprietary-source-unavailable":
                raise WaveError(f"0x{entry:08X}: IAR provider/license drift")
        elif row["license_status"] != "unavailable":
            raise WaveError(f"0x{entry:08X}: speculative license claim")
        records.append({
            "entry": row["entry"], "end_exclusive": row["end_exclusive"],
            "envelope_bytes": envelope_bytes, "corpus_body_bytes": corpus_bytes,
            "body_sha256": digest, "closure_depth": depth, "role": row["role"],
            "provider_identity": row["provider_identity"],
            "license_status": row["license_status"], "disposition": row["disposition"],
            "callable_implementation_available": False,
        })

    zero_records: list[dict[str, Any]] = []
    for row in zero_rows:
        entry = int(row["entry"], 16)
        end, envelope_bytes, corpus_bytes, digest, depth = EXPECTED_ZERO[entry]
        if (
            int(row["end_exclusive"], 16), int(row["envelope_bytes"]),
            int(row["official_opaque_bytes"]), int(row["corpus_body_bytes"]),
            row["body_sha256"], int(row["closure_depth"]),
        ) != (end, envelope_bytes, 0, corpus_bytes, digest, depth):
            raise WaveError(f"0x{entry:08X}: zero-boundary drift")
        parent = parent_none[entry]
        if int(parent["official_opaque_bytes"]) != 0:
            raise WaveError(f"0x{entry:08X}: no longer zero opaque")
        installed = payload[entry - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if len(installed) != envelope_bytes or sha256(installed) != digest:
            raise WaveError(f"0x{entry:08X}: zero-row physical drift")
        body, decoded_bytes, corpus_digest = corpus_function(corpus, entry)
        if (decoded_bytes, corpus_digest) != (corpus_bytes, digest):
            raise WaveError(f"0x{entry:08X}: zero-row corpus drift")
        calls = Counter(int(match, 16) for match in re.findall(r"\bFUN_([0-9a-f]{8})\(", body))
        calls.pop(entry, None)
        observed_calls[entry] = dict(calls)
        if observed_calls[entry] != EXPECTED_CALLS[entry]:
            raise WaveError(f"0x{entry:08X}: zero-row topology drift")
        if entry != 0x00439BE4 and not (0x0043BA98 <= entry < 0x0043C08E):
            raise WaveError(f"0x{entry:08X}: zero interior escaped enclosing envelope")
        zero_records.append({
            "entry": row["entry"], "end_exclusive": row["end_exclusive"],
            "envelope_bytes": envelope_bytes, "official_opaque_bytes": 0,
            "corpus_body_bytes": corpus_bytes, "body_sha256": digest,
            "closure_depth": depth, "reconciliation": row["reconciliation"],
        })

    # The released memory-fill entry is split by the corpus at 0x43C0EC.
    memset_span = payload[0x0043C0E4 - LOAD_ADDRESS:0x0043C14A - LOAD_ADDRESS]
    if len(memset_span) != 102 or sha256(memset_span) != "34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a":
        raise WaveError("complete IAR memset span drift")

    graph_entries = selected | zero_entries
    depths = {ROOT: 0}
    frontier = {ROOT}
    while frontier:
        following = {
            target
            for entry in frontier
            for target in set(observed_calls[entry]) | PROVIDER_COMPANION.get(entry, set())
            if target in raw_wave3_residual and target not in depths
        }
        current_depth = depths[next(iter(frontier))]
        for target in following:
            depths[target] = current_depth + 1
        frontier = following
    expected_depths = {
        **{entry: facts[4] for entry, facts in EXPECTED_SELECTED.items()},
        **{entry: facts[4] for entry, facts in EXPECTED_ZERO.items()},
    }
    if depths != expected_depths or set(depths) != graph_entries:
        raise WaveError(f"complete graph closure drift: {depths}")
    all_targets = {
        target for entry in graph_entries
        for target in set(observed_calls[entry]) | PROVIDER_COMPANION.get(entry, set())
    }
    if all_targets - graph_entries != {0x004397A8}:
        raise WaveError(f"terminal partition drift: {all_targets - graph_entries}")

    residual_after = residual_before - selected
    after = {
        "functions": len(residual_after),
        "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_after),
    }
    if after != {"functions": 1396, "bytes": 177364}:
        raise WaveError(f"wave-4 after accounting drift: {after}")
    if max((int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_after) != (5056, 0x00519290):
        raise WaveError("next-largest envelope drift")
    depth_summary = {
        str(depth): {
            "typed_functions": sum(1 for e, value in depths.items() if value == depth and e in selected),
            "typed_bytes": sum(EXPECTED_SELECTED[e][1] for e, value in depths.items() if value == depth and e in selected),
            "zero_opaque_rows": sum(1 for e, value in depths.items() if value == depth and e in zero_entries),
        }
        for depth in sorted(set(depths.values()))
    }
    mapping_sha = sha256(json.dumps(
        {"typed": records, "zero": zero_records}, sort_keys=True, separators=(",", ":")
    ).encode())
    return {
        "status": "opacity-wave4-orientation-calibration-closure-typed",
        "read_only": True, "hardware_operations": False, "production_routed": False,
        "wave3_residual": raw_summary,
        "reconciled_zero_opaque": {"functions": len(zero_entries), "bytes": 0},
        "selected_root_range": {"start": "0x0043A698", "end_exclusive": "0x0043BA6C"},
        "before": before,
        "newly_typed": {"functions": len(selected), "bytes": sum(v[1] for v in EXPECTED_SELECTED.values())},
        "closure_depths": depth_summary,
        "after": after,
        "largest_remaining": {"entry": "0x00519290", "envelope_bytes": 5056},
        "provider": {
            "ingress": "sole caller 0x0055F848; authenticated Even first-party orientation/calibration seam",
            "npmx_relation": "explicitly not part of Nordic nPMX",
            "algorithm_identity": None, "algorithm_license": None,
            "iar_exception": {
                "span": "0x0043C0E4-0x0043C14A", "identity": "IAR DLIB memset family",
                "license_status": "proprietary-source-unavailable",
            },
        },
        "terminal_partition": {"existing_iar_sqrtf": ["0x004397A8"]},
        "mapping_sha256": mapping_sha, "records": records,
        "zero_opaque_records": zero_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
