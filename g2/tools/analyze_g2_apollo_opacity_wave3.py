#!/usr/bin/env python3
"""Close the full unresolved call graph of Apollo opacity wave 3.

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
CORPUS = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-08.c"
NEMA_PROVENANCE = G2 / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave3/typed_boundaries.tsv"
LOAD_ADDRESS = 0x00438000

PINS = {
    CORPUS: (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    NEMA_PROVENANCE: (24_898, "5a8e427ae337afb78f2901e74ae48d08d8c222944a50ada8adadfbdd98296bfa"),
}

ROOT = 0x00517E18
EXPECTED_SELECTED = {
    0x00517E18: (0x00519280, 5224, 5170, "6dc530a49a2708b76b2d07accb0c43dd7f79b64c29fa46ee8083cd3da6408370", 0),
    0x005177A4: (0x00517850, 172, 172, "09fab9518945ffdf3e8644d137a1b0464660a97459426c64e9370a7757aaeb2e", 1),
    0x0051785C: (0x005179D0, 372, 372, "996bc50f76c32ab90a0e522a24122f3c6cceebf7bcfe5372baee39fee74b9f6a", 1),
    0x00522622: (0x0052262E, 12, 12, "1cd7d7e0efeb722f8bafd7a39fd68edc0f96241cb8317c20c81362b1301064f2", 1),
    0x00522F50: (0x00522FB4, 100, 100, "4d1d7c8496a4711553aebdaf916df218f2ee4389f9ff1c2fb05f0783199dfe23", 1),
    0x00522FB4: (0x00523280, 716, 716, "f3eb7d43880d4c3f318d95339e3bc95d78ce4a6dc9941a0ffa21fe5a0694ab47", 1),
    0x00523284: (0x005232C2, 62, 62, "1a9c120174b97a5dcefa1305de4452c0ea611407d7a5ef8e1a60959e55786429", 1),
    0x00524218: (0x00524258, 64, 64, "c0197264d2b600e455097d534a68ad28d774c60e68f8a850a13f52f1fbcf17f1", 1),
    0x00514D2C: (0x00514D92, 102, 102, "9d168de3d061b1341db50849ba8162c226ce49d7622d3d23557961b46a787020", 2),
    0x005242CC: (0x005242E2, 22, 22, "4077cb0139505930ac63ea7f27b5fce9732ef372925d8a247f9da18d445328ba", 2),
    0x00514504: (0x005147B0, 684, 684, "f93c897c48573e17a793ef8bfd015d52150e53812bc0fddd9492558bf8e61af7", 3),
    0x00514070: (0x005140C6, 86, 86, "d9beae1fc551852d210f2cb11e3bd58e873e219da4092e9dd74f3184b0a99dd4", 4),
    0x0051416C: (0x00514178, 12, 12, "888b1d4507fb20a1b9d9d9a3bb7dc8b40c330c690bd0df172e4367219dc2aa77", 4),
    0x00514178: (0x00514184, 12, 12, "6bc561ef9feaf8c8f327bb904b93da1a391b244ea3321319207f26b0c1b786c4", 4),
    0x00514050: (0x00514070, 32, 32, "9ea14c05d38180b70a4375535ad95003861ad83728c38133641b5ed3964a26e3", 5),
}

EXPECTED_CALLS = {
    0x00517E18: {0x004397A8: 7, 0x0051565C: 3, 0x00516B34: 14, 0x005177A4: 8,
                 0x0051785C: 8, 0x00522622: 4, 0x0052266E: 9, 0x005226B2: 8,
                 0x00522F50: 6, 0x00522FB4: 2, 0x00523284: 2, 0x00524218: 2,
                 0x005639E8: 2},
    0x005177A4: {},
    0x0051785C: {},
    0x00522622: {},
    0x00522F50: {},
    0x00522FB4: {0x00514AEC: 4, 0x00514D2C: 1, 0x005242CC: 7},
    0x00523284: {0x00522FB4: 1},
    0x00524218: {},
    0x00514D2C: {0x004B127C: 2, 0x00514504: 1},
    0x005242CC: {},
    0x00514504: {0x004B127C: 6, 0x00514070: 2, 0x0051416C: 1, 0x00514178: 1},
    0x00514070: {0x00439C04: 1, 0x00484180: 1, 0x004841D8: 2, 0x00514050: 1},
    0x0051416C: {0x00484180: 1},
    0x00514178: {0x0048429E: 1},
    0x00514050: {},
}

FRONTIER_PARTITION = {
    "prior_wave1_typed": {0x005226B2},
    "prior_wave2_typed": {0x00514AEC, 0x0051565C, 0x00516B34, 0x0052266E, 0x005639E8},
    "existing_iar_source_recreated": {0x004397A8, 0x00439C04},
    "parent_classified_lvgl": {0x004B127C},
    "parent_zero_opaque_heap": {0x00484180, 0x004841D8, 0x0048429E},
}


class WaveError(RuntimeError):
    """Raised when an authenticated wave-3 invariant changes."""


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
    wave2 = load_module(
        G2 / "tools/analyze_g2_apollo_opacity_wave2.py", "opacity_wave3_wave2"
    )
    wave2_report = wave2.run_audit()
    if wave2_report["after"] != {"functions": 1440, "bytes": 193152}:
        raise WaveError("wave-2 residual drift")
    wave1 = load_module(
        G2 / "tools/analyze_g2_apollo_opacity_wave1.py", "opacity_wave3_wave1"
    )
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
        G2 / "tools/analyze_g2_apollo510_mspi_triplet_candidate.py", "opacity_wave3_mspi"
    ).run_audit()
    classified = (
        {int(row["entry"], 16) for row in cordio_rows}
        | {int(row["entry"], 16) for row in freetype_rows if row["status"] != "investigation-required"}
        | {int(row["entry"], 16) for row in liblc3_rows if row["status"] != "investigation-required"}
        | {int(entry, 16) for entry in mspi["triplet"]}
    )
    raw_wave2_residual = (
        set(parent_none)
        - classified
        - set(wave1.EXPECTED_SELECTED)
        - set(wave2.EXPECTED_SELECTED)
        - {0x004397A8}
    )
    raw_wave2_summary = {
        "functions": len(raw_wave2_residual),
        "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in raw_wave2_residual),
    }
    if raw_wave2_summary != wave2_report["after"]:
        raise WaveError(f"wave-2 set reconciliation drift: {raw_wave2_summary}")

    iar = load_module(G2 / "tools/analyze_g2_iar_runtime.py", "opacity_wave3_iar").analyze()
    memcpy = next(segment for segment in iar["segments"] if segment["name"] == "__aeabi_memcpy")
    if (memcpy["start"], memcpy["end"], memcpy["size"], memcpy["state"]) != (
        0x00439BE4, 0x00439C8A, 166, "source_recreated_redirected"
    ):
        raise WaveError("existing IAR memcpy classification drift")
    memcpy_entry = parent_none[0x00439C04]
    if (
        int(memcpy_entry["official_opaque_bytes"]) != 0
        or not (memcpy["start"] <= 0x00439C04 < memcpy["end"])
    ):
        raise WaveError("IAR aligned-memcpy parent accounting drift")
    residual_before = raw_wave2_residual - {0x00439C04}
    before = {
        "functions": len(residual_before),
        "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_before),
    }
    if before != {"functions": 1439, "bytes": 193152}:
        raise WaveError(f"wave-3 before accounting drift: {before}")
    largest_before = max(
        (int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_before
    )
    if largest_before != (5224, ROOT):
        raise WaveError(f"selected root is no longer largest: {largest_before}")

    local = {path: pinned(path) for path in PINS}
    corpus = local[CORPUS].decode()
    nema = json.loads(local[NEMA_PROVENANCE])
    resolved_symbols = {
        int(address, 16): symbol
        for address, symbol in nema["stock_evidence"]["resolved_symbols"].items()
    }
    if len(resolved_symbols) != 11 or set(resolved_symbols) & set(EXPECTED_SELECTED):
        raise WaveError("Nema resolved-symbol negative boundary drift")
    if (
        nema["ambiqsuite_candidate"]["versions"]["nemagfx"]["semantic_version"] != "1.4.12"
        or nema["ambiqsuite_candidate"]["versions"]["nemavg"]["semantic_version"] != "1.1.8"
        or nema["integration_status"]["production_ready"] is not False
        or "not byte-identical archive members" not in nema["archive_metadata"]["stock_compiler_relation"]
    ):
        raise WaveError("Nema provider qualification drift")
    if "original IAR-built NemaGFX/NemaVG archive" not in " ".join(
        nema["integration_status"]["remaining_gaps"]
    ):
        raise WaveError("Nema original-provider gap drift")

    selected_rows = tsv_rows(BOUNDARY.read_bytes())
    selected = {int(row["entry"], 16) for row in selected_rows}
    if selected != set(EXPECTED_SELECTED) or not selected <= residual_before:
        raise WaveError("selected boundary membership drift")
    freetype_by_entry = {int(row["entry"], 16): row for row in freetype_rows}
    payload = inherited[wave1.IMAGE][wave1.OTA_HEADER_BYTES:]
    records: list[dict[str, Any]] = []
    observed_calls: dict[int, dict[int, int]] = {}
    for row in selected_rows:
        entry = int(row["entry"], 16)
        end, envelope_bytes, corpus_bytes, digest, depth = EXPECTED_SELECTED[entry]
        if (
            int(row["end_exclusive"], 16), int(row["envelope_bytes"]),
            int(row["corpus_body_bytes"]), row["body_sha256"], int(row["closure_depth"]),
        ) != (end, envelope_bytes, corpus_bytes, digest, depth):
            raise WaveError(f"0x{entry:08X}: static boundary drift")
        parent = parent_none[entry]
        if (
            int(parent["body_end_exclusive"], 16) != end
            or int(parent["official_opaque_bytes"]) != envelope_bytes
        ):
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
            raise WaveError(f"0x{entry:08X}: call topology drift: {observed_calls[entry]}")
        ft = freetype_by_entry[entry]
        if (
            ft["status"] != "investigation-required"
            or "no FreeType anchor, string, or call-community evidence" not in ft["detail"]
        ):
            raise WaveError(f"0x{entry:08X}: FreeType negative evidence drift")
        if row["disposition"] != "typed-external-provider-unavailable":
            raise WaveError(f"0x{entry:08X}: disposition is not fail-closed")
        records.append({
            "entry": row["entry"], "end_exclusive": row["end_exclusive"],
            "envelope_bytes": envelope_bytes, "corpus_body_bytes": corpus_bytes,
            "body_sha256": digest, "closure_depth": depth, "role": row["role"],
            "disposition": row["disposition"], "source_identity_claimed": False,
            "license_claimed": None, "callable_implementation_available": False,
        })

    # Prove that following every actionable no-evidence edge reaches exactly
    # the static table at the recorded shortest depth.
    depths = {ROOT: 0}
    frontier = {ROOT}
    while frontier:
        following = {
            target
            for entry in frontier
            for target in observed_calls[entry]
            if target in residual_before and target not in depths
        }
        for target in following:
            depths[target] = depths[next(
                entry for entry in frontier if target in observed_calls[entry]
            )] + 1
        frontier = following
    expected_depths = {entry: facts[4] for entry, facts in EXPECTED_SELECTED.items()}
    if depths != expected_depths:
        raise WaveError(f"unresolved closure drift: {depths}")

    all_targets = {target for calls in observed_calls.values() for target in calls}
    external_targets = all_targets - selected
    partition_union: set[int] = set()
    for name, entries in FRONTIER_PARTITION.items():
        if partition_union & entries:
            raise WaveError(f"frontier partition overlap: {name}")
        partition_union |= entries
    if external_targets != partition_union:
        raise WaveError(f"terminal frontier drift: {external_targets ^ partition_union}")
    if parent_by_entry[0x004B127C]["bucket"] != "lvgl":
        raise WaveError("LVGL terminal classification drift")
    for entry in FRONTIER_PARTITION["parent_zero_opaque_heap"]:
        if int(parent_by_entry[entry]["official_opaque_bytes"]) != 0:
            raise WaveError(f"0x{entry:08X}: heap terminal is no longer zero-opaque")

    residual_after = residual_before - selected
    after = {
        "functions": len(residual_after),
        "bytes": sum(int(parent_none[e]["official_opaque_bytes"]) for e in residual_after),
    }
    if after != {"functions": 1424, "bytes": 185480}:
        raise WaveError(f"wave-3 after accounting drift: {after}")
    largest_after = max(
        (int(parent_none[e]["official_opaque_bytes"]), e) for e in residual_after
    )
    if largest_after != (5076, 0x0043A698):
        raise WaveError(f"next-largest envelope drift: {largest_after}")
    depth_summary = {
        str(depth): {
            "functions": sum(1 for value in depths.values() if value == depth),
            "bytes": sum(EXPECTED_SELECTED[e][1] for e, value in depths.items() if value == depth),
        }
        for depth in sorted(set(depths.values()))
    }
    mapping_sha = sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode())
    return {
        "status": "opacity-wave3-full-call-closure-typed",
        "read_only": True, "hardware_operations": False, "production_routed": False,
        "wave2_residual": raw_wave2_summary,
        "reconciled_since_wave2": {
            "iar_aligned_memcpy": {"functions": 1, "official_opaque_bytes": 0}
        },
        "selected_root_range": {"start": "0x00517E18", "end_exclusive": "0x00519280"},
        "before": before,
        "newly_typed": {"functions": len(selected), "bytes": sum(v[1] for v in EXPECTED_SELECTED.values())},
        "closure_depths": depth_summary,
        "after": after,
        "largest_remaining": {"entry": "0x0043A698", "envelope_bytes": 5076},
        "provider": {
            "status": "candidate-family-known-exact-function-unresolved",
            "candidate_context": {
                "nemagfx": "1.4.12 stock lower bound and exact packaged candidate",
                "nemavg": "1.1.8 exact co-packaged candidate",
            },
            "resolved_stock_symbols_checked": len(resolved_symbols),
            "selected_symbols_resolved": 0,
            "claimed_upstream_function_identity": None, "license": None,
            "reason": "public GCC package is not the IAR stock generator and the original IAR archive/private source state is unavailable",
        },
        "terminal_partition": {
            name: [f"0x{entry:08X}" for entry in sorted(entries)]
            for name, entries in FRONTIER_PARTITION.items()
        },
        "mapping_sha256": mapping_sha,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
