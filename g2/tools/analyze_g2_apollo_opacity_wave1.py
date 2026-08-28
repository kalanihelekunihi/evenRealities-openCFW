#!/usr/bin/env python3
"""Reconcile Apollo family waves and type the next unavailable-provider cluster.

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
CORPUS = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-08.c"
MANIFESTS = G2 / "tools/manifests"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave1/typed_boundaries.tsv"
LOAD_ADDRESS = 0x00438000
OTA_HEADER_BYTES = 32

PINS = {
    IMAGE: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    CORPUS: (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    MANIFESTS / "g2-apollo-unanchored-census-functions.tsv": (649_606, "a36c51c0084e51b6e64fc902ab58be16fa76f2c3b361c3ae543f378a8c1f7b96"),
    MANIFESTS / "g2-cordio-ll-sea-census.tsv": (61_831, "84d4e94b8a4f85b46c426b89379cc21c07b247f488aa14fdf5b0c3298f4712e6"),
    MANIFESTS / "g2-freetype-engine-census.tsv": (90_563, "f04628f816912cf5a69b4f256372d2aef3931ab381d469badecde47f528f50fd"),
    MANIFESTS / "g2-liblc3-encoder-internals-map.tsv": (17_179, "7bac3be803e1d3964cedfb75a73b8f94ec63b065e8a3eb5213e82f7882c05e83"),
    MANIFESTS / "g2-peripheral-register-cluster-map.tsv": (13_158, "ca3160e92c8c540eb51fd8ebf606a202958c401b7f4d7388e945ed4c21523df7"),
}

EXPECTED_SELECTED = {
    0x005202EC: (0x005223A2, 8374, 8300, "95db31afd7f15370eb52a769548b4f649dd47b05e6c4c2fbfb69807955e9345d"),
    0x0052262E: (0x0052264E, 32, 32, "febf143780cb665d1db87e417928c93964d02b70166ab5d928ca1caaa72e5ab3"),
    0x0052264E: (0x0052266E, 32, 32, "cc78612cbec66588bb12e0b4e47cb6177b72038d6232242f79ce29fceed80636"),
    0x005226B2: (0x005226D6, 36, 36, "96431b0363591daf67017c7076be194ee48b524c1414eacd16e1604c1894caf9"),
    0x005226E8: (0x00522848, 352, 352, "8f3348a5fb7af704e72d88d7e58cd81ee7cf28bdc89c878006545156da7d84ca"),
    0x005228B0: (0x00522916, 102, 102, "ca0c3c944a392ba1f48e08bd1955c286d515a6d63110d99eda4543678a95417d"),
    0x00522920: (0x0052294C, 44, 44, "3228442b34bcf52d54c8b7da3f0a264cb7711d247f9c739e07fd1b5900217be9"),
    0x0052294C: (0x00522956, 10, 10, "f227809feced82f14acda32b25b32a161f27301314e02f04746458cb3e43d47d"),
    0x00522956: (0x00522960, 10, 10, "13ce8f8c8e8f184901114f9b50d4fcba06ef1cfaa8f340af4e8a34d4bdf0ff10"),
    0x00522A16: (0x00522A20, 10, 10, "1fa2df446335cccdbc67f68d7b33ca7095bf3226532b07fbba739948114a44eb"),
}
ROOT_DIRECT_CALLS = {
    0x0052262E: 2,
    0x0052264E: 2,
    0x005226B2: 2,
    0x005226E8: 4,
    0x005228B0: 1,
    0x00522920: 4,
    0x0052294C: 4,
    0x00522956: 4,
    0x00522A16: 3,
}


class WaveError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned(path: Path) -> bytes:
    data = path.read_bytes()
    if (len(data), sha256(data)) != PINS[path]:
        raise WaveError(f"pin drift: {path}")
    return data


def tsv_rows(data: bytes) -> list[dict[str, str]]:
    lines = data.decode().splitlines()
    lines = [line for line in lines if not line.startswith("#")]
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
    authenticated = {path: pinned(path) for path in PINS}
    parent = tsv_rows(authenticated[MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"])
    cordio = tsv_rows(authenticated[MANIFESTS / "g2-cordio-ll-sea-census.tsv"])
    freetype = tsv_rows(authenticated[MANIFESTS / "g2-freetype-engine-census.tsv"])
    liblc3 = tsv_rows(authenticated[MANIFESTS / "g2-liblc3-encoder-internals-map.tsv"])
    peripheral = tsv_rows(authenticated[MANIFESTS / "g2-peripheral-register-cluster-map.tsv"])
    corpus = authenticated[CORPUS].decode()
    payload = authenticated[IMAGE][OTA_HEADER_BYTES:]

    parent_none = {
        int(row["entry"], 16): row
        for row in parent
        if row["bucket"] == "investigation-required-no-evidence"
    }
    if (len(parent_none), sum(int(row["official_opaque_bytes"]) for row in parent_none.values())) != (1873, 290704):
        raise WaveError("parent no-evidence frontier drift")

    none_admission = load_module(
        G2 / "tools/analyze_g2_cordio_ll_sea_none_source_admission.py",
        "opacity_wave_none_admission",
    ).run_audit()
    if none_admission["census"]["functions"] != 198:
        raise WaveError("closed 0x5D none admission drift")
    cordio_entries = {int(row["entry"], 16) for row in cordio}
    if len(cordio_entries) != 300:
        raise WaveError("Cordio sea census drift")
    none_entries = {int(row["start"], 16) for row in none_admission["census"]["records"]}
    attributed_cordio = {int(row["entry"], 16) for row in cordio if row["evidence"] != "none"}
    if len(attributed_cordio) != 102 or attributed_cordio | none_entries != cordio_entries:
        raise WaveError("Cordio classified partition drift")

    base_report = load_module(
        G2 / "research/candidates/freetype/analyze_base_cluster_candidate.py",
        "opacity_wave_freetype_base",
    ).analyze()
    if base_report["admitted_cluster"] != {"functions": 83, "bytes": 7874}:
        raise WaveError("FreeType base admission drift")
    freetype_entries = {
        int(row["entry"], 16)
        for row in freetype
        if row["status"] != "investigation-required"
    }
    if len(freetype_entries) != 83:
        raise WaveError("FreeType family partition drift")

    liblc3_entries = {
        int(row["entry"], 16)
        for row in liblc3
        if row["status"] != "investigation-required"
    }
    if len(liblc3_entries) != 41:
        raise WaveError("liblc3 family partition drift")

    mspi_report = load_module(
        G2 / "tools/analyze_g2_apollo510_mspi_triplet_candidate.py",
        "opacity_wave_mspi_triplet",
    ).run_audit()
    if mspi_report["status"] != "candidate-qualified":
        raise WaveError("MSPI triplet admission drift")
    mspi_entries = {int(entry, 16) for entry in mspi_report["triplet"]}

    classified_sets = {
        "cordio_ll_sea": cordio_entries & parent_none.keys(),
        "freetype_base": freetype_entries & parent_none.keys(),
        "liblc3_attributed": liblc3_entries & parent_none.keys(),
        "apollo510_mspi_triplet": mspi_entries & parent_none.keys(),
    }
    combined: set[int] = set()
    for name, entries in classified_sets.items():
        if combined & entries:
            raise WaveError(f"classified wave overlap: {name}")
        combined |= entries
    classified_summary = {
        name: {
            "functions": len(entries),
            "bytes": sum(int(parent_none[entry]["official_opaque_bytes"]) for entry in entries),
        }
        for name, entries in classified_sets.items()
    }
    expected_summary = {
        "cordio_ll_sea": {"functions": 300, "bytes": 52866},
        "freetype_base": {"functions": 81, "bytes": 6928},
        "liblc3_attributed": {"functions": 31, "bytes": 14434},
        "apollo510_mspi_triplet": {"functions": 3, "bytes": 6250},
    }
    if classified_summary != expected_summary:
        raise WaveError(f"classified reconciliation drift: {classified_summary}")

    residual_before = set(parent_none) - combined
    before = {
        "functions": len(residual_before),
        "bytes": sum(int(parent_none[entry]["official_opaque_bytes"]) for entry in residual_before),
    }
    if before != {"functions": 1458, "bytes": 210226}:
        raise WaveError(f"before accounting drift: {before}")

    typed = tsv_rows(BOUNDARY.read_bytes())
    selected = {int(row["entry"], 16) for row in typed}
    if selected != set(EXPECTED_SELECTED) or not selected <= residual_before:
        raise WaveError("selected boundary membership drift")
    peripheral_by_entry = {int(row["entry"], 16): row for row in peripheral}
    if peripheral_by_entry[0x005202EC]["evidence"] != "call-topology-into-cluster":
        raise WaveError("root peripheral false-positive evidence drift")
    if "constant collision" not in peripheral_by_entry[0x005202EC]["detail"]:
        raise WaveError("root constant-collision guard drift")

    result_rows = []
    root_body = None
    for row in typed:
        entry = int(row["entry"], 16)
        end, envelope_bytes, corpus_bytes, digest = EXPECTED_SELECTED[entry]
        if (
            int(row["end_exclusive"], 16),
            int(row["envelope_bytes"]),
            int(row["corpus_body_bytes"]),
            row["body_sha256"],
        ) != (end, envelope_bytes, corpus_bytes, digest):
            raise WaveError(f"0x{entry:08X}: static boundary drift")
        parent_row = parent_none[entry]
        if int(parent_row["body_end_exclusive"], 16) != end or int(parent_row["official_opaque_bytes"]) != envelope_bytes:
            raise WaveError(f"0x{entry:08X}: parent boundary drift")
        installed = payload[entry - LOAD_ADDRESS:end - LOAD_ADDRESS]
        if len(installed) != envelope_bytes or sha256(installed) != digest:
            raise WaveError(f"0x{entry:08X}: official body drift")
        body, decoded_bytes, corpus_digest = corpus_function(corpus, entry)
        if (decoded_bytes, corpus_digest) != (corpus_bytes, digest):
            raise WaveError(f"0x{entry:08X}: corpus identity drift")
        if row["disposition"] != "typed-external-provider-unavailable":
            raise WaveError(f"0x{entry:08X}: disposition is not fail-closed")
        if entry == 0x005202EC:
            root_body = body
        result_rows.append({
            "entry": row["entry"],
            "end_exclusive": row["end_exclusive"],
            "envelope_bytes": envelope_bytes,
            "corpus_body_bytes": corpus_bytes,
            "body_sha256": digest,
            "role": row["role"],
            "disposition": row["disposition"],
            "source_identity_claimed": False,
            "callable_implementation_available": False,
        })
    assert root_body is not None
    actual_calls = {
        entry: len(re.findall(rf"\bFUN_{entry:08x}\(", root_body))
        for entry in ROOT_DIRECT_CALLS
    }
    if actual_calls != ROOT_DIRECT_CALLS:
        raise WaveError(f"root direct-call topology drift: {actual_calls}")

    largest_before = max(
        (int(parent_none[entry]["official_opaque_bytes"]), entry)
        for entry in residual_before
    )
    if largest_before != (8374, 0x005202EC):
        raise WaveError(f"selected root is no longer largest: {largest_before}")
    residual_after = residual_before - selected
    after = {
        "functions": len(residual_after),
        "bytes": sum(int(parent_none[entry]["official_opaque_bytes"]) for entry in residual_after),
    }
    if after != {"functions": 1448, "bytes": 201224}:
        raise WaveError(f"after accounting drift: {after}")

    mapping_sha = sha256(json.dumps(result_rows, sort_keys=True, separators=(",", ":")).encode())
    return {
        "status": "opacity-wave1-typed-boundary-closed",
        "read_only": True,
        "hardware_operations": False,
        "production_routed": False,
        "parent_no_evidence": {"functions": 1873, "bytes": 290704},
        "reconciled_existing_boundaries": classified_summary,
        "typed_non_census_boundaries_observed": none_admission["typed_non_census_boundaries"],
        "selected_range": {"start": "0x005202EC", "end_exclusive": "0x00522A20"},
        "before": before,
        "newly_typed": {
            "functions": len(selected),
            "bytes": sum(EXPECTED_SELECTED[entry][1] for entry in selected),
        },
        "after": after,
        "largest_remaining_envelope_bytes": max(int(parent_none[e]["official_opaque_bytes"]) for e in residual_after),
        "provider": {
            "status": "unavailable-and-unidentified",
            "family_description": "graphics command/state construction community",
            "claimed_upstream_identity": None,
            "license": None,
            "reason": "no exact checked-in provider definition; apparent peripheral literal is a validated constant collision",
        },
        "root_direct_calls": {f"0x{entry:08X}": count for entry, count in ROOT_DIRECT_CALLS.items()},
        "mapping_sha256": mapping_sha,
        "records": result_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
