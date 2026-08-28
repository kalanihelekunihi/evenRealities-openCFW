#!/usr/bin/env python3
"""Type the largest post-wave-1 Apollo opacity call community.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CORPUS_08 = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-08.c"
CORPUS_11 = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-11.c"
NEMA_PROVENANCE = G2 / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave2/typed_boundaries.tsv"
LOAD_ADDRESS = 0x00438000
OTA_HEADER_BYTES = 32

PINS = {
    CORPUS_08: (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    CORPUS_11: (739_345, "029dbe031730c0d760e1913f8d043119b77f49170725b1464f5a53cc166a1bea"),
    NEMA_PROVENANCE: (24_898, "5a8e427ae337afb78f2901e74ae48d08d8c222944a50ada8adadfbdd98296bfa"),
}

EXPECTED_SELECTED = {
    0x005156B8: (0x00516B34, 5244, 5178, "cb608639b5fa231ec75364637f87de60b2ad7ee804868633d89acd709ae26d84", CORPUS_08),
    0x00514AEC: (0x00514B76, 138, 138, "4e6e3eb54f1dd213f95ef034789c0aa6a377a44d42bdbbb0d522330ef89f1ff4", CORPUS_08),
    0x0051565C: (0x0051566C, 16, 16, "811c18c8482ff8276b719c120d2b08ebcda241d73b34d1ef2dda12f8aaceaab9", CORPUS_08),
    0x00516B34: (0x00516BDE, 170, 170, "ef1cea57e940a19c2500853476a1317238891f46e2ad53af8b868b9383129f50", CORPUS_08),
    0x005179D0: (0x00517E00, 1072, 1072, "f3108554eb4366c8156c87685ebaf71d948b445d07fe9446bdd4528c7e7fa348", CORPUS_08),
    0x0052266E: (0x005226B2, 68, 68, "81a17ea5f0e44a4bc3c52dc289209fd62221cea29413913529893a8d22cdc3b0", CORPUS_08),
    0x005639E8: (0x00563F3C, 1364, 1334, "53c3e14f6e1b224dd13f95dfad6a095c6bb9cddaeaaeef953bd8eeb8ca87d873", CORPUS_11),
}

ROOT = 0x005156B8
ROOT_DIRECT_CALLS = {
    0x004397A8: 3,
    0x0050969C: 1,
    0x00514AEC: 7,
    0x0051565C: 3,
    0x00516B34: 6,
    0x005179D0: 6,
    0x0052266E: 3,
    0x005226B2: 6,
    0x005639E8: 3,
}


class WaveError(RuntimeError):
    """Raised when an authenticated wave-2 invariant changes."""


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
    wave1 = load_module(
        G2 / "tools/analyze_g2_apollo_opacity_wave1.py", "opacity_wave2_wave1"
    )
    wave1_report = wave1.run_audit()
    if wave1_report["after"] != {"functions": 1448, "bytes": 201224}:
        raise WaveError("wave-1 residual drift")

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
        "opacity_wave2_mspi",
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
    wave1_selected = set(wave1.EXPECTED_SELECTED)
    raw_wave1_residual = set(parent_none) - classified - wave1_selected
    raw_wave1_summary = {
        "functions": len(raw_wave1_residual),
        "bytes": sum(
            int(parent_none[entry]["official_opaque_bytes"])
            for entry in raw_wave1_residual
        ),
    }
    if raw_wave1_summary != wave1_report["after"]:
        raise WaveError(f"wave-1 set reconciliation drift: {raw_wave1_summary}")

    iar = load_module(
        G2 / "tools/analyze_g2_iar_runtime.py", "opacity_wave2_iar_runtime"
    ).analyze()
    sqrt = next(segment for segment in iar["segments"] if segment["name"] == "sqrtf")
    if (
        sqrt["start"],
        sqrt["end"],
        sqrt["size"],
        sqrt["sha256"],
        sqrt["state"],
    ) != (
        0x004397A8,
        0x004397C4,
        28,
        "f7003725d19bfa0d3c7727692b5c7016e23a9f109d5d799dcde22e11ac1f7dd8",
        "source_recreated_redirected",
    ):
        raise WaveError("existing IAR sqrtf classification drift")
    if int(parent_none[0x004397A8]["official_opaque_bytes"]) != 0:
        raise WaveError("IAR sqrtf parent accounting drift")

    residual_before = raw_wave1_residual - {0x004397A8}
    before = {
        "functions": len(residual_before),
        "bytes": sum(
            int(parent_none[entry]["official_opaque_bytes"])
            for entry in residual_before
        ),
    }
    if before != {"functions": 1447, "bytes": 201224}:
        raise WaveError(f"wave-2 before accounting drift: {before}")
    largest_before = max(
        (int(parent_none[entry]["official_opaque_bytes"]), entry)
        for entry in residual_before
    )
    if largest_before != (5244, ROOT):
        raise WaveError(f"selected root is no longer largest: {largest_before}")

    local = {path: pinned(path) for path in PINS}
    corpora = {CORPUS_08: local[CORPUS_08].decode(), CORPUS_11: local[CORPUS_11].decode()}
    nema = json.loads(local[NEMA_PROVENANCE])
    resolved_symbols = {
        int(address, 16): symbol
        for address, symbol in nema["stock_evidence"]["resolved_symbols"].items()
    }
    if len(resolved_symbols) != 11 or set(resolved_symbols) & set(EXPECTED_SELECTED):
        raise WaveError("Nema resolved-symbol negative boundary drift")
    if (
        nema["ambiqsuite_candidate"]["versions"]["nemagfx"]["semantic_version"]
        != "1.4.12"
        or nema["ambiqsuite_candidate"]["versions"]["nemavg"]["semantic_version"]
        != "1.1.8"
        or nema["integration_status"]["production_ready"] is not False
        or "not byte-identical archive members"
        not in nema["archive_metadata"]["stock_compiler_relation"]
    ):
        raise WaveError("Nema provider qualification drift")
    remaining_gaps = " ".join(nema["integration_status"]["remaining_gaps"])
    if "original IAR-built NemaGFX/NemaVG archive" not in remaining_gaps:
        raise WaveError("Nema original-provider gap drift")

    selected_rows = tsv_rows(BOUNDARY.read_bytes())
    selected = {int(row["entry"], 16) for row in selected_rows}
    if selected != set(EXPECTED_SELECTED) or not selected <= residual_before:
        raise WaveError("selected boundary membership drift")

    freetype_by_entry = {int(row["entry"], 16): row for row in freetype_rows}
    payload = inherited[wave1.IMAGE][wave1.OTA_HEADER_BYTES:]
    records = []
    root_body = None
    freetype_negative_entries: set[int] = set()
    for row in selected_rows:
        entry = int(row["entry"], 16)
        end, envelope_bytes, corpus_bytes, digest, corpus_path = EXPECTED_SELECTED[entry]
        static = (
            int(row["end_exclusive"], 16),
            int(row["envelope_bytes"]),
            int(row["corpus_body_bytes"]),
            row["body_sha256"],
        )
        if static != (end, envelope_bytes, corpus_bytes, digest):
            raise WaveError(f"0x{entry:08X}: static boundary drift")
        parent_row = parent_none[entry]
        if (
            int(parent_row["body_end_exclusive"], 16) != end
            or int(parent_row["official_opaque_bytes"]) != envelope_bytes
        ):
            raise WaveError(f"0x{entry:08X}: parent boundary drift")
        installed = payload[entry - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if len(installed) != envelope_bytes or sha256(installed) != digest:
            raise WaveError(f"0x{entry:08X}: official body drift")
        body, decoded_bytes, corpus_digest = corpus_function(corpora[corpus_path], entry)
        if (decoded_bytes, corpus_digest) != (corpus_bytes, digest):
            raise WaveError(f"0x{entry:08X}: corpus identity drift")
        ft = freetype_by_entry.get(entry)
        if ft is not None:
            if (
                ft["status"] != "investigation-required"
                or "no FreeType anchor, string, or call-community evidence" not in ft["detail"]
            ):
                raise WaveError(f"0x{entry:08X}: FreeType negative evidence drift")
            freetype_negative_entries.add(entry)
        if row["disposition"] != "typed-external-provider-unavailable":
            raise WaveError(f"0x{entry:08X}: disposition is not fail-closed")
        if entry == ROOT:
            root_body = body
        records.append(
            {
                "entry": row["entry"],
                "end_exclusive": row["end_exclusive"],
                "envelope_bytes": envelope_bytes,
                "corpus_body_bytes": corpus_bytes,
                "body_sha256": digest,
                "role": row["role"],
                "disposition": row["disposition"],
                "evidence": row["evidence"],
                "source_identity_claimed": False,
                "license_claimed": None,
                "callable_implementation_available": False,
            }
        )

    if freetype_negative_entries != set(EXPECTED_SELECTED) - {0x005639E8}:
        raise WaveError("FreeType negative-evidence coverage drift")

    assert root_body is not None
    actual_calls = {
        target: len(re.findall(rf"\bFUN_{target:08x}\(", root_body))
        for target in ROOT_DIRECT_CALLS
    }
    observed_targets = {
        int(match, 16)
        for match in re.findall(r"\bFUN_([0-9a-f]{8})\(", root_body)
        if int(match, 16) != ROOT
    }
    if actual_calls != ROOT_DIRECT_CALLS or observed_targets != set(ROOT_DIRECT_CALLS):
        raise WaveError(
            f"root direct-call topology drift: counts={actual_calls}, targets={observed_targets}"
        )
    direct_partition = {
        "newly_typed": sorted(set(ROOT_DIRECT_CALLS) & (selected - {ROOT})),
        "prior_wave1_typed": [0x005226B2],
        "existing_iar_source_recreated": [0x004397A8],
        "existing_parent_first_party": [0x0050969C],
    }
    if set().union(*(set(values) for values in direct_partition.values())) != set(ROOT_DIRECT_CALLS):
        raise WaveError("root dependency partition is incomplete")
    first_party = parent_by_entry[0x0050969C]
    if (first_party["bucket"], first_party["evidence"], first_party["confidence"]) != (
        "first-party",
        "link-order-sandwich",
        "low",
    ):
        raise WaveError("existing first-party dependency classification drift")

    residual_after = residual_before - selected
    after = {
        "functions": len(residual_after),
        "bytes": sum(
            int(parent_none[entry]["official_opaque_bytes"])
            for entry in residual_after
        ),
    }
    if after != {"functions": 1440, "bytes": 193152}:
        raise WaveError(f"wave-2 after accounting drift: {after}")
    largest_after = max(
        (int(parent_none[entry]["official_opaque_bytes"]), entry)
        for entry in residual_after
    )
    if largest_after != (5224, 0x00517E18):
        raise WaveError(f"next-largest envelope drift: {largest_after}")

    mapping_sha = sha256(
        json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    )
    return {
        "status": "opacity-wave2-typed-boundary-closed",
        "read_only": True,
        "hardware_operations": False,
        "production_routed": False,
        "wave1_residual": raw_wave1_summary,
        "reconciled_since_wave1": {
            "iar_sqrtf": {"functions": 1, "official_opaque_bytes": 0}
        },
        "selected_root_range": {
            "start": "0x005156B8",
            "end_exclusive": "0x00516B34",
        },
        "community_address_hull": {
            "start": "0x00514AEC",
            "end_exclusive": "0x00563F3C",
            "contiguous": False,
        },
        "before": before,
        "newly_typed": {
            "functions": len(selected),
            "bytes": sum(EXPECTED_SELECTED[entry][1] for entry in selected),
        },
        "after": after,
        "largest_remaining": {
            "entry": "0x00517E18",
            "envelope_bytes": 5224,
        },
        "provider": {
            "status": "candidate-family-known-exact-function-unresolved",
            "candidate_context": {
                "nemagfx": "1.4.12 stock lower bound and exact packaged candidate",
                "nemavg": "1.1.8 exact co-packaged candidate",
            },
            "resolved_stock_symbols_checked": len(resolved_symbols),
            "selected_symbols_resolved": 0,
            "claimed_upstream_function_identity": None,
            "license": None,
            "reason": "public GCC package is not the IAR stock generator and the original IAR archive/private source state is unavailable",
        },
        "root_direct_calls": {
            f"0x{entry:08X}": count for entry, count in ROOT_DIRECT_CALLS.items()
        },
        "root_direct_partition": {
            name: [f"0x{entry:08X}" for entry in entries]
            for name, entries in direct_partition.items()
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
