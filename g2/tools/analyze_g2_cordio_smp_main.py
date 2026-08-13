#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio SMP main module."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-main-function-map.tsv"
READINESS_MANIFEST = ROOT / "research/readiness/smp-main/SHA256SUMS"
READINESS_SHA256 = "0ee02d564ac137eaeacda02b280b308c7bbae99810a5bd92ab648ab6e8af142e"
PATCH = ROOT / "third_party/cordio/g2-patches/smp_main-ambiq-aes-queue-cleanup.patch"
PINNED_INPUTS = {
    FUNCTION_MAP: "018816f5d2d34f9a156daa143ec319f6be6bc5518fcf3825ade043400bf30c39",
    ROOT / "tools/manifests/packetcraft-cordio-smp-main-provenance.tsv": "da7e704805c9ffa9c7f1c8f78b8c1689bbd2e71913369d5d9374fbde2540ea72",
    PATCH: "0b86bf4ff50cdae14662a9c06824404737993d966523421fd3a347d1c3fbdf52",
    ROOT / "tools/manifests/readiness-cordio-smp-main-build-results.tsv": "7c9f4352f14765709294d204d64270ade6286134e26681134eafa65ab0ff963a",
    ROOT / "tools/manifests/readiness-cordio-smp-main-closure-results.tsv": "bf77568aff88ed19aa3db607c2522a56a7bc64668ffc8b6a49224a4a3204ddcf",
    ROOT / "tools/manifests/readiness-cordio-smp-main-include-closure.tsv": "61dc8470b22afd53361768730421354e1a25d616a86bdc4a50762eabaf0ae3e3",
    ROOT / "tools/manifests/readiness-cordio-smp-main-source-identities.tsv": "159834446375565e4a5f18c098f94d60f4dcbd6215a43843e21c39eeac7ab3a2",
    ROOT / "tools/manifests/readiness-cordio-smp-main-undefined-providers.tsv": "072522c62af3e925134692fe0cefaa6261a200c40dd6d8566f7d45d634490620",
}

ENCLOSING_SPAN = (0x00537278, 0x00537EEC)
ENCLOSING_SHA256 = "bba2ea8b7c5ed581d8202b2b7c2978f0ae8f874eccea15cca7de17ff645732fb"
CONCATENATED_BODY_SHA256 = "c70987596989d69f3828cc2d1d5515e7badce57caae5e611f052a75cc55fc88e"
GAPS = [
    (0x005375EE, 0x005375FC, "eb7df66f732c9435836b9ea3c04507f9d7908eeb866db5345abb2a1f39a8251c"),
    (0x00537CF8, 0x00537D0C, "6de58e692a9b935f6e04b28807e635545ac2ab47bd3f1bf4cdaf54cfb5ac3e1b"),
    (0x00537E9E, 0x00537EEC, "441c52381656e608ad9d70c451b97d21439938bc93d21a89b7400fd354ca8e89"),
]
SOURCE_PATH = 0x006DE854
SOURCE_PATH_BYTES = 93
SOURCE_PATH_SHA256 = "966a611194a5bef07b5f981ab9d01670cb980f9b903525afc8ea9a1200389787"
SOURCE_PATH_CELL = 0x00537EAC
SMP_CB = 0x20070AEC
SEC_CB = 0x20072CD8
EXPECTED_FUNCTION_POINTERS = {
    0x004B878C: 0x00537D0D,
    0x00537ED4: 0x00537445,
    0x00537ED8: 0x00537279,
    0x00537EDC: 0x00537503,
}


class AuditError(RuntimeError):
    """Raised when authenticated SMP-main evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("smp_main_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_functions() -> tuple[list[dict[str, Any]], list[str]]:
    functions: list[dict[str, Any]] = []
    source_only: list[str] = []
    with FUNCTION_MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if not row["stock_start"]:
                source_only.append(row["stock_name"])
                continue
            functions.append({
                "name": row["stock_name"],
                "start": int(row["stock_start"], 0),
                "end_exclusive": int(row["stock_end_exclusive"], 0),
                "size": int(row["stock_bytes"]),
                "sha256": row["stock_sha256"],
                "source_start_line": int(row["source_start_line"]),
                "source_end_line": int(row["source_end_line"]),
                "source_span_sha256": row["source_span_sha256"],
                "direct_bl_callers": [
                    int(item, 0) for item in row["direct_bl_callers"].split(",") if item
                ],
                "indirect_ingress": row["indirect_ingress"],
                "classification": row["classification"],
            })
    return functions, source_only


def _all_callers(blob: bytes, decoder: Any, functions: list[dict[str, Any]]) -> dict[int, list[int]]:
    callers = {item["start"]: [] for item in functions}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in callers:
            callers[target].append(address)
    return callers


def _aligned_function_pointers(blob: bytes, functions: list[dict[str, Any]]) -> dict[int, int]:
    targets = {
        address | thumb
        for item in functions
        for address in range(item["start"], item["end_exclusive"], 2)
        for thumb in (0, 1)
    }
    return {
        LOAD_BASE + offset: struct.unpack_from("<I", blob, offset)[0]
        for offset in range(0, len(blob) - 3, 4)
        if struct.unpack_from("<I", blob, offset)[0] in targets
    }


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned SMP-main input changed: {path.name}")
    if not READINESS_MANIFEST.is_file() or _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei SMP-main readiness artifact changed")

    functions, source_only = _load_functions()
    decoder = _load_decoder()
    all_callers = _all_callers(blob, decoder, functions)
    body_parts: list[bytes] = []
    for item in functions:
        body = _slice(blob, item["start"], item["end_exclusive"])
        if len(body) != item["size"] or _sha256(body) != item["sha256"]:
            raise AuditError(f"SMP-main stock span changed for {item['name']}")
        if all_callers[item["start"]] != item["direct_bl_callers"]:
            raise AuditError(f"SMP-main direct caller closure changed for {item['name']}")
        body_parts.append(body)
    if _sha256(b"".join(body_parts)) != CONCATENATED_BODY_SHA256:
        raise AuditError("SMP-main concatenated body identity changed")
    if _sha256(_slice(blob, *ENCLOSING_SPAN)) != ENCLOSING_SHA256:
        raise AuditError("SMP-main enclosing interval changed")
    for start, end, expected in GAPS:
        if _sha256(_slice(blob, start, end)) != expected:
            raise AuditError(f"SMP-main data gap changed at 0x{start:08x}")
    if _sha256(_slice(blob, SOURCE_PATH, SOURCE_PATH + SOURCE_PATH_BYTES)) != SOURCE_PATH_SHA256:
        raise AuditError("SMP-main retained source path changed")
    if struct.unpack_from("<I", blob, SOURCE_PATH_CELL - LOAD_BASE)[0] != SOURCE_PATH:
        raise AuditError("SMP-main source-path pointer cell changed")
    if _aligned_function_pointers(blob, functions) != EXPECTED_FUNCTION_POINTERS:
        raise AuditError("SMP-main function-pointer closure changed")
    if struct.unpack_from("<I", blob, 0x00537EBC - LOAD_BASE)[0] != SMP_CB:
        raise AuditError("SMP-main control-block literal changed")
    if struct.unpack_from("<I", blob, 0x00537EE8 - LOAD_BASE)[0] != SEC_CB:
        raise AuditError("SMP-main security-queue literal changed")

    linked_bytes = sum(item["size"] for item in functions)
    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": ENCLOSING_SPAN[0],
            "end_exclusive": ENCLOSING_SPAN[1],
            "enclosing_bytes": ENCLOSING_SPAN[1] - ENCLOSING_SPAN[0],
            "enclosing_sha256": ENCLOSING_SHA256,
            "linked_function_count": len(functions),
            "linked_function_bytes": linked_bytes,
            "concatenated_body_sha256": CONCATENATED_BODY_SHA256,
            "literal_or_data_gap_bytes": sum(end - start for start, end, _ in GAPS),
            "functions": functions,
            "source_only_dead_stripped": source_only,
            "direct_bl_callers": sum(len(item["direct_bl_callers"]) for item in functions),
            "intentional_function_pointers": EXPECTED_FUNCTION_POINTERS,
            "unexpected_stored_entry_or_interior_pointers": 0,
        },
        "abi": {
            "control_block": SMP_CB,
            "control_block_size": 0xFC,
            "connection_count": 3,
            "ccb_size": 0x4C,
            "ccb_offsets": {
                "response_timer": 0x00,
                "wait_timer": 0x10,
                "pair_request": 0x20,
                "pair_response": 0x27,
                "scratch_pointer": 0x30,
                "queued_message_pointer": 0x34,
                "handle": 0x38,
                "connection_id": 0x3D,
                "state": 0x3E,
                "token": 0x41,
                "attempts": 0x42,
                "key_ready": 0x44,
                "secure_connections_pointer": 0x48,
            },
            "security_control_block": SEC_CB,
            "database_service_event": 0x20,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "vendor_patch_oracle": "AmbiqSuite R2.5.1 stale-AES-queue cleanup",
            "reconstruction": "r20.05c public source plus tracked cleanup patch",
            "reconstructed_source_sha256": "dd813e9b3bdf5d4ea6c879a78b7c7e542518a573ea70d18d9e144eb8909b6d74",
            "qualification": "semantic source candidate; retained line constants prove further local textual skew",
            "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST),
            "archive_sha256": READINESS_SHA256,
            "public_compiler_profiles": 2,
            "hybrid_compiler_profiles": 2,
            "external_provider_seams": 32,
            "base_closure_status": "invalid: linker retained zero text/data/BSS",
            "valid_hybrid_closure_profiles": 2,
            "linked_unresolved_symbols": 0,
        },
        "production": {
            "status": "stock-retained; semantic source candidate and provider closure authenticated but not promoted",
            "source_owned_bytes_added": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Cordio SMP main audit: 20 linked functions / 3,076 bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
