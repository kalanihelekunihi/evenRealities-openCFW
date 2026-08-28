#!/usr/bin/env python3
"""Close the largest remaining cubic-vector-path Apollo opacity envelope.

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
FUNCTIONS = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
NEMA_PROVENANCE = G2 / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave5/typed_boundaries.tsv"
RECONCILED = G2 / "research/admission/apollo_opacity_wave5/reconciled_graph.tsv"
LOAD_ADDRESS = 0x00438000

PINS = {
    CORPUS: (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    NEMA_PROVENANCE: (24_898, "5a8e427ae337afb78f2901e74ae48d08d8c222944a50ada8adadfbdd98296bfa"),
}

ROOT = 0x00519290
EXPECTED_SELECTED = {
    ROOT: (
        0x0051A650,
        5056,
        4998,
        "48ef98e94015af6eaac62bfaf88469032b41ab98021cc4d097c8cd54d8c737b1",
        0,
    ),
}
EXPECTED_CALLS = {
    ROOT: {
        0x004397A8: 7,
        0x0051565C: 3,
        0x00516B34: 14,
        0x005177A4: 8,
        0x0051785C: 8,
        0x00522622: 4,
        0x0052266E: 9,
        0x005226B2: 7,
        0x00522F50: 6,
        0x00522FB4: 2,
        0x00523284: 2,
        0x00524218: 2,
        0x005639E8: 2,
    }
}
EXPECTED_RECONCILED = {
    0x004397A8: (7, "existing-source-recreated-zero-opaque", "IAR-DLIB-sqrtf", 0),
    0x0051565C: (3, "prior-typed", "apollo-opacity-wave2", 16),
    0x00516B34: (14, "prior-typed", "apollo-opacity-wave2", 170),
    0x005177A4: (8, "prior-typed", "apollo-opacity-wave3", 172),
    0x0051785C: (8, "prior-typed", "apollo-opacity-wave3", 372),
    0x00522622: (4, "prior-typed", "apollo-opacity-wave3", 12),
    0x0052266E: (9, "prior-typed", "apollo-opacity-wave2", 68),
    0x005226B2: (7, "prior-typed", "apollo-opacity-wave1", 36),
    0x00522F50: (6, "prior-typed", "apollo-opacity-wave3", 100),
    0x00522FB4: (2, "prior-typed", "apollo-opacity-wave3", 716),
    0x00523284: (2, "prior-typed", "apollo-opacity-wave3", 62),
    0x00524218: (2, "prior-typed", "apollo-opacity-wave3", 64),
    0x005639E8: (2, "prior-typed", "apollo-opacity-wave2", 1364),
}
EXPECTED_CALLERS = {0x005171F8, 0x0051D2E0, 0x0051F798}


class WaveError(RuntimeError):
    """Raised when an authenticated wave-5 invariant changes."""


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
    wave4 = load_module(
        G2 / "tools/analyze_g2_apollo_opacity_wave4.py", "opacity_wave5_wave4"
    )
    wave4_report = wave4.run_audit()
    if wave4_report["after"] != {"functions": 1396, "bytes": 177364}:
        raise WaveError("wave-4 residual drift")
    if wave4_report["terminal_partition"] != {
        "existing_iar_sqrtf": ["0x004397A8"]
    }:
        raise WaveError("source-recreated sqrtf classification drift")

    wave1 = load_module(
        G2 / "tools/analyze_g2_apollo_opacity_wave1.py", "opacity_wave5_wave1"
    )
    wave2 = load_module(
        G2 / "tools/analyze_g2_apollo_opacity_wave2.py", "opacity_wave5_wave2"
    )
    wave3 = load_module(
        G2 / "tools/analyze_g2_apollo_opacity_wave3.py", "opacity_wave5_wave3"
    )
    inherited = {path: wave1.pinned(path) for path in wave1.PINS}
    parent_rows = wave1.tsv_rows(
        inherited[wave1.MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"]
    )
    cordio_rows = wave1.tsv_rows(
        inherited[wave1.MANIFESTS / "g2-cordio-ll-sea-census.tsv"]
    )
    freetype_rows = wave1.tsv_rows(
        inherited[wave1.MANIFESTS / "g2-freetype-engine-census.tsv"]
    )
    liblc3_rows = wave1.tsv_rows(
        inherited[wave1.MANIFESTS / "g2-liblc3-encoder-internals-map.tsv"]
    )
    parent_by_entry = {int(row["entry"], 16): row for row in parent_rows}
    parent_none = {
        entry: row
        for entry, row in parent_by_entry.items()
        if row["bucket"] == "investigation-required-no-evidence"
    }
    mspi = load_module(
        G2 / "tools/analyze_g2_apollo510_mspi_triplet_candidate.py",
        "opacity_wave5_mspi",
    ).run_audit()
    classified = (
        {int(row["entry"], 16) for row in cordio_rows}
        | {
            int(row["entry"], 16)
            for row in freetype_rows
            if row["status"] != "investigation-required"
        }
        | {
            int(row["entry"], 16)
            for row in liblc3_rows
            if row["status"] != "investigation-required"
        }
        | {int(entry, 16) for entry in mspi["triplet"]}
    )
    residual_before = (
        set(parent_none)
        - classified
        - set(wave1.EXPECTED_SELECTED)
        - set(wave2.EXPECTED_SELECTED)
        - set(wave3.EXPECTED_SELECTED)
        - set(wave4.EXPECTED_SELECTED)
        - set(wave4.EXPECTED_ZERO)
        - {0x004397A8, 0x00439C04}
    )
    before = {
        "functions": len(residual_before),
        "bytes": sum(
            int(parent_none[entry]["official_opaque_bytes"])
            for entry in residual_before
        ),
    }
    if before != wave4_report["after"]:
        raise WaveError(f"wave-4 set reconciliation drift: {before}")
    if max(
        (int(parent_none[entry]["official_opaque_bytes"]), entry)
        for entry in residual_before
    ) != (5056, ROOT):
        raise WaveError("wave-5 root is no longer largest")
    if ROOT not in residual_before:
        raise WaveError("wave-5 root escaped the actionable residual")

    local = {path: pinned(path) for path in PINS}
    corpus = local[CORPUS].decode()
    payload = inherited[wave1.IMAGE][wave1.OTA_HEADER_BYTES :]
    selected_rows = tsv_rows(BOUNDARY.read_bytes())
    if {int(row["entry"], 16) for row in selected_rows} != {ROOT}:
        raise WaveError("selected boundary membership drift")
    row = selected_rows[0]
    end, envelope_bytes, corpus_bytes, digest, depth = EXPECTED_SELECTED[ROOT]
    if (
        int(row["end_exclusive"], 16),
        int(row["envelope_bytes"]),
        int(row["corpus_body_bytes"]),
        row["body_sha256"],
        int(row["closure_depth"]),
    ) != (end, envelope_bytes, corpus_bytes, digest, depth):
        raise WaveError("root static boundary drift")
    if row["role"] != "cubic-vector-path-subdivision-and-stroke-root":
        raise WaveError("root bounded-role drift")
    parent = parent_none[ROOT]
    if (
        int(parent["body_end_exclusive"], 16) != end
        or int(parent["official_opaque_bytes"]) != envelope_bytes
    ):
        raise WaveError("root parent boundary drift")
    installed = payload[ROOT - LOAD_ADDRESS : end - LOAD_ADDRESS]
    if len(installed) != envelope_bytes or sha256(installed) != digest:
        raise WaveError("root official body drift")
    body, decoded_bytes, corpus_digest = corpus_function(corpus, ROOT)
    if (decoded_bytes, corpus_digest) != (corpus_bytes, digest):
        raise WaveError("root corpus identity drift")
    calls = Counter(int(match, 16) for match in re.findall(r"\bFUN_([0-9a-f]{8})\(", body))
    calls.pop(ROOT, None)
    if dict(calls) != EXPECTED_CALLS[ROOT]:
        raise WaveError(f"root call topology drift: {dict(calls)}")

    # Reconcile the complete direct frontier before assigning any new bytes.
    reconciled_rows = tsv_rows(RECONCILED.read_bytes())
    if {int(item["entry"], 16) for item in reconciled_rows} != set(EXPECTED_RECONCILED):
        raise WaveError("reconciled frontier membership drift")
    prior_sets = {
        "apollo-opacity-wave1": set(wave1.EXPECTED_SELECTED),
        "apollo-opacity-wave2": set(wave2.EXPECTED_SELECTED),
        "apollo-opacity-wave3": set(wave3.EXPECTED_SELECTED),
    }
    reconciled_records: list[dict[str, Any]] = []
    for item in reconciled_rows:
        entry = int(item["entry"], 16)
        call_count, state, owner, parent_bytes = EXPECTED_RECONCILED[entry]
        if (
            int(item["call_count"]),
            int(item["closure_depth"]),
            item["accounting_state"],
            item["owner"],
            int(item["parent_official_opaque_bytes"]),
            int(item["wave5_new_opaque_bytes"]),
        ) != (call_count, 1, state, owner, parent_bytes, 0):
            raise WaveError(f"0x{entry:08X}: reconciled record drift")
        expected_evidence = (
            "IAR runtime analyzer source_recreated_redirected span"
            if owner == "IAR-DLIB-sqrtf"
            else f"wave-{owner[-1]} authenticated body and boundary"
        )
        if item["evidence"] != expected_evidence:
            raise WaveError(f"0x{entry:08X}: reconciliation evidence drift")
        if calls[entry] != call_count:
            raise WaveError(f"0x{entry:08X}: reconciled call-count drift")
        if owner.startswith("apollo-opacity-wave") and entry not in prior_sets[owner]:
            raise WaveError(f"0x{entry:08X}: prior owner drift")
        if owner == "IAR-DLIB-sqrtf":
            if entry != 0x004397A8 or int(parent_none[entry]["official_opaque_bytes"]) != 0:
                raise WaveError("IAR sqrtf zero-opaque accounting drift")
        elif int(parent_none[entry]["official_opaque_bytes"]) != parent_bytes:
            raise WaveError(f"0x{entry:08X}: prior opaque-byte accounting drift")
        reconciled_records.append(
            {
                "entry": item["entry"],
                "call_count": call_count,
                "closure_depth": 1,
                "accounting_state": state,
                "owner": owner,
                "parent_official_opaque_bytes": parent_bytes,
                "wave5_new_opaque_bytes": 0,
            }
        )
    if set(calls) != set(EXPECTED_RECONCILED):
        raise WaveError("direct frontier is not exhaustively reconciled")
    if set(calls) & residual_before:
        raise WaveError("actionable callee escaped the frontier reconciliation")

    # Caller topology is context, not provider provenance.
    function_rows = [
        json.loads(line) for line in local[FUNCTIONS].decode().splitlines()
    ]
    callers = {
        int(item["entry"], 16)
        for item in function_rows
        if f"{ROOT:08x}" in item.get("callees", [])
    }
    if callers != EXPECTED_CALLERS:
        raise WaveError(f"root caller drift: {callers}")
    for entry in callers:
        caller = parent_by_entry[entry]
        if (
            caller["bucket"] != "first-party"
            or caller["evidence"] != "call-topology-single-family"
            or caller["confidence"] != "medium"
        ):
            raise WaveError(f"0x{entry:08X}: caller context drift")

    freetype = {int(item["entry"], 16): item for item in freetype_rows}[ROOT]
    if (
        freetype["status"] != "investigation-required"
        or "no FreeType anchor, string, or call-community evidence" not in freetype["detail"]
    ):
        raise WaveError("FreeType negative evidence drift")
    nema = json.loads(local[NEMA_PROVENANCE])
    resolved_symbols = {
        int(address, 16)
        for address in nema["stock_evidence"]["resolved_symbols"]
    }
    if ROOT in resolved_symbols:
        raise WaveError("root unexpectedly gained an authenticated Nema symbol")
    if (
        nema["ambiqsuite_candidate"]["versions"]["nemagfx"]["semantic_version"]
        != "1.4.12"
        or nema["ambiqsuite_candidate"]["versions"]["nemavg"]["semantic_version"]
        != "1.1.8"
        or nema["integration_status"]["production_ready"] is not False
        or "not byte-identical archive members"
        not in nema["archive_metadata"]["stock_compiler_relation"]
    ):
        raise WaveError("Nema candidate/provider qualification drift")
    if (
        row["provider_identity"] != "unresolved-linked-vector-path-provider"
        or row["license_status"] != "unavailable"
        or row["disposition"] != "typed-external-provider-unavailable"
    ):
        raise WaveError("fail-closed provider or license disposition drift")

    residual_after = residual_before - {ROOT}
    after = {
        "functions": len(residual_after),
        "bytes": sum(
            int(parent_none[entry]["official_opaque_bytes"])
            for entry in residual_after
        ),
    }
    if after != {"functions": 1395, "bytes": 172308}:
        raise WaveError(f"wave-5 after accounting drift: {after}")
    if max(
        (int(parent_none[entry]["official_opaque_bytes"]), entry)
        for entry in residual_after
    ) != (3306, 0x0051C5EC):
        raise WaveError("next-largest envelope drift")

    record = {
        "entry": row["entry"],
        "end_exclusive": row["end_exclusive"],
        "envelope_bytes": envelope_bytes,
        "corpus_body_bytes": corpus_bytes,
        "body_sha256": digest,
        "closure_depth": depth,
        "role": row["role"],
        "provider_identity": row["provider_identity"],
        "license_status": row["license_status"],
        "disposition": row["disposition"],
        "callable_implementation_available": False,
    }
    mapping_sha = sha256(
        json.dumps(
            {"typed": [record], "reconciled": reconciled_records},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    )
    return {
        "status": "opacity-wave5-cubic-vector-path-root-typed",
        "read_only": True,
        "hardware_operations": False,
        "production_routed": False,
        "wave4_residual": wave4_report["after"],
        "before": before,
        "selected_root_range": {
            "start": "0x00519290",
            "end_exclusive": "0x0051A650",
        },
        "newly_typed": {"functions": 1, "bytes": 5056},
        "closure_depths": {
            "0": {"typed_functions": 1, "typed_bytes": 5056},
            "1": {
                "prior_typed_functions": 12,
                "source_owned_zero_opaque_rows": 1,
                "wave5_new_bytes": 0,
            },
        },
        "reconciled_frontier": {
            "functions": len(reconciled_records),
            "prior_typed_functions": 12,
            "source_owned_zero_opaque_rows": 1,
            "new_bytes": 0,
        },
        "provider": {
            "family_context": "NemaGFX/NemaVG vector-path community candidate",
            "authenticated_function_identity": None,
            "authenticated_provider": None,
            "authenticated_license": None,
            "callers": [f"0x{entry:08X}" for entry in sorted(callers)],
            "caller_qualification": (
                "medium-confidence call-topology first-party context only; "
                "not source/provider provenance"
            ),
            "negative_evidence": [
                "root absent from the eleven authenticated stock Nema symbols",
                "public GCC Nema archive is not byte-identical to IAR-generated stock",
                "FreeType census records no anchor, string, or call-community evidence",
            ],
        },
        "after": after,
        "largest_remaining": {"entry": "0x0051C5EC", "envelope_bytes": 3306},
        "mapping_sha256": mapping_sha,
        "records": [record],
        "reconciled_records": reconciled_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
