#!/usr/bin/env python3
"""Authenticate the AmbiqSuite ancestry of G2's Cordio app framework.

This composes the authenticated embedded-source-path map with a byte-level
recovery of the legacy master/slave objects.  It identifies a public source
oracle and its limits; it does not claim exact G2 source text or a historical
private generating commit.
"""

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
IMAGE_BASE = 0x00437FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
SOURCE_MAP_ANALYZER = ROOT / "tools/analyze_g2_cordio_source_map.py"
FUNCTION_MAP = ROOT / "tools/manifests/ambiqsuite-cordio-app-framework-function-map.tsv"
PROVENANCE_MAP = ROOT / "tools/manifests/ambiqsuite-cordio-app-framework-provenance.tsv"
SNAPSHOT = ROOT / "third_party/ambiqsuite-cordio-app-framework"
SNAPSHOT_VERIFIER = SNAPSHOT / "verify_snapshot.py"
SNAPSHOT_PROVENANCE = SNAPSHOT / "PROVENANCE.json"
SELECTED_COMMIT = "de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f"
PACKETCRAFT_ANCESTOR = "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
EXPECTED_STOCK_SUMMARY_SHA256 = "5fca10f44bf5b308ba89e1afcded7f0fb470c8ac19f29d587f2e3e0d27cb055b"
EXPECTED_ALL_ANCHORS_SHA256 = "d00e4ff2b560f970cf23e00d80bf6701581574d14939f5d69843fe13310839e9"

INPUT_SHA256 = {
    FUNCTION_MAP: "f892ac72319a4782ec807bb3f11454c16a607d3690fe80ec4eddef39c132e341",
    PROVENANCE_MAP: "4ca74385c8ad620516b9e44b21251a6737d06b2af9b41dc650896b079315acd8",
}

EXPECTED_PATHS = {
    "common/app_db.c": (0x006D84BC, 22, 14996, "1080c82aa88405a8c3486d69aae5f63014846ece734209efaec116e2438d7b5e"),
    "app_master_leg.c": (0x006D85F4, 2, 376, "c21634d64df804cea1a82c5243db4e03b104e790b8dade3eaf7d1335b480e21e"),
    "app_slave_leg.c": (0x006D865C, 1, 270, "30b8b745ac85cc6ee040a0ee059abedb28b64c09265a93897ff96ec616ba5df6"),
    "common/app_ui.c": (0x006D86C4, 3, 2512, "79b75dd43201e993bd53d332c6e82711e3efa8829b413259cc3cd85b73e8b005"),
    "app_master.c": (0x006DA098, 4, 1522, "a83b030f8232110eba22d9615c731cf7480922726490543b88696896ce3e08d2"),
    "app_server.c": (0x006DA0FC, 1, 296, "2e93bfa30479db74485bd6e0ce973093ac0294a55acadd6f7240394736782db7"),
    "app_slave.c": (0x006DA160, 3, 1944, "2f47d5b9832a523522db7512d0f39b82c09d5933f31996b556ad61279a25cd93"),
    "app_disc.c": (0x006DC694, 11, 6186, "56e95ab896e9bb9fa88c6c67863e71783d73e2d89a4fc7ba87bf03fbff0d3500"),
    "app_main.c": (0x006DC6F4, 3, 1008, "45f0b8e43d8560eb4493028304bf7bd254cc514f1e2715b1f671e92b133f105c"),
}

EXPECTED_LEGACY = {
    "app_master_leg.c": (4, 454, (0x00503298, 0x0050345E)),
    "app_slave_leg.c": (10, 952, (0x004B2A04, 0x004B2DBC)),
}
STORED_CALLBACKS = {
    0x004B2DDC: 0x004B2AFF,
    0x004B2DE0: 0x004B2B91,
}


class AuditError(RuntimeError):
    """Raised when an authenticated input or bounded conclusion changes."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _slice(image: bytes, start: int, end: int) -> bytes:
    if start < IMAGE_BASE or end < start or end - IMAGE_BASE > len(image):
        raise AuditError(f"invalid image interval {start:#x}..{end:#x}")
    return image[start - IMAGE_BASE : end - IMAGE_BASE]


def _app_relative(relative: str) -> str:
    marker = "ble-profiles\\sources\\apps\\app\\"
    if marker not in relative:
        raise AuditError(f"unexpected application path: {relative}")
    return relative.split(marker, 1)[1].replace("\\", "/")


def _verify_snapshot() -> dict[str, Any]:
    verifier = _load("ambiqsuite_cordio_app_snapshot_for_audit", SNAPSHOT_VERIFIER)
    result = verifier.verify()
    if result["selected_commit"] != SELECTED_COMMIT or result["source_files"] != 9:
        raise AuditError("selected AmbiqSuite snapshot changed")
    provenance = json.loads(SNAPSHOT_PROVENANCE.read_text())
    boundary = provenance["g2_boundary"]
    if boundary != {
        "retained_paths": 9,
        "anchored_functions": 50,
        "anchored_body_bytes": 29110,
        "stock_anchor_summary_sha256": EXPECTED_STOCK_SUMMARY_SHA256,
        "lineage": "AmbiqSuite application-framework fork of Packetcraft Cordio with G2 downstream extensions",
        "source_identification_closed": True,
        "exact_source_text_identity": False,
        "production_routed": False,
        "local_delta": "G2 expands the Ambiq application database from the sample NVM model into a ten-record role-aware MRAM database and adds product connection, privacy, pairing-failure, discovery, diagnostics, and UI policy.",
    }:
        raise AuditError("snapshot G2 boundary changed")
    if provenance["packetcraft_ancestor"]["selected_commit"] != PACKETCRAFT_ANCESTOR:
        raise AuditError("Packetcraft ancestor changed")
    return result


def _path_evidence(source_map: dict[str, Any], image: bytes) -> list[dict[str, Any]]:
    paths = [
        row for row in source_map["paths"]
        if row["ownership_boundary"] == "ambiq_or_product_application_layer"
    ]
    if len(paths) != 9:
        raise AuditError(f"application path census changed: {len(paths)}")
    found: dict[str, dict[str, Any]] = {}
    all_bodies: list[bytes] = []
    for row in paths:
        relative = _app_relative(row["relative"])
        if relative not in EXPECTED_PATHS or relative in found:
            raise AuditError(f"application path set changed: {relative}")
        run, count, size, digest = EXPECTED_PATHS[relative]
        bodies = [
            _slice(image, anchor["body_start"], anchor["body_end_inclusive"] + 1)
            for anchor in row["function_anchors"]
        ]
        if row["path_run_address"] != run or len(bodies) != count:
            raise AuditError(f"path anchors changed: {relative}")
        joined = b"".join(bodies)
        if len(joined) != size or _sha(joined) != digest:
            raise AuditError(f"anchored stock bytes changed: {relative}")
        all_bodies.extend(bodies)
        found[relative] = {
            "retained_path": row["relative"],
            "selected_source": relative,
            "path_run_address": run,
            "anchored_functions": count,
            "anchored_body_bytes": size,
            "anchored_body_sha256": digest,
            "maximum_diagnostic_line": max(
                (line for anchor in row["function_anchors"] for line in anchor["diagnostic_or_assert_line_numbers"]),
                default=None,
            ),
        }
    if set(found) != set(EXPECTED_PATHS):
        raise AuditError("application path set incomplete")
    joined_all = b"".join(all_bodies)
    if len(joined_all) != 29110 or _sha(joined_all) != EXPECTED_ALL_ANCHORS_SHA256:
        raise AuditError("aggregate application anchors changed")
    return [found[name] for name in EXPECTED_PATHS]


def _legacy_evidence(image: bytes) -> dict[str, Any]:
    for path, digest in INPUT_SHA256.items():
        if _sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned manifest changed: {path.name}")
    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 14:
        raise AuditError("legacy function census changed")
    by_path: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = _slice(image, start, end)
        if len(raw) != int(row["stock_bytes"]) or _sha(raw) != row["stock_sha256"]:
            raise AuditError(f"legacy stock body changed: {row['function']}")
        by_path.setdefault(row["retained_path"], []).append(row)
    objects = {}
    for path, (count, size, bounds) in EXPECTED_LEGACY.items():
        rows_for_path = by_path.get(path, [])
        if len(rows_for_path) != count or sum(int(row["stock_bytes"]) for row in rows_for_path) != size:
            raise AuditError(f"legacy object inventory changed: {path}")
        if int(rows_for_path[0]["stock_start"], 0) != bounds[0] or int(rows_for_path[-1]["stock_end_exclusive"], 0) != bounds[1]:
            raise AuditError(f"legacy object bounds changed: {path}")
        objects[path] = {
            "linked_functions": count,
            "physical_bytes": size,
            "start": bounds[0],
            "end_exclusive": bounds[1],
            "functions": [row["function"] for row in rows_for_path],
        }
    for cell, value in STORED_CALLBACKS.items():
        observed = struct.unpack("<I", _slice(image, cell, cell + 4))[0]
        if observed != value:
            raise AuditError(f"stored callback changed at {cell:#x}")
    return {
        "objects": objects,
        "aggregate": {
            "linked_functions": 14,
            "physical_bytes": 1406,
            "path_anchored_functions": 3,
            "additional_recovered_functions": 11,
            "stored_callbacks": 2,
        },
        "stored_callback_cells": {f"{cell:#010x}": f"{value:#010x}" for cell, value in STORED_CALLBACKS.items()},
        "selected_source_definitions_not_linked_in_stock_cluster": [
            "AppAdvSetAdValue", "AppSetAdvPeerAddr", "AppConnAccept"
        ],
    }


def analyze(corpus: Path, image_path: Path = IMAGE) -> dict[str, Any]:
    image = image_path.read_bytes()
    if len(image) != IMAGE_SIZE or _sha(image) != IMAGE_SHA256:
        raise AuditError("official G2 application image changed")
    snapshot = _verify_snapshot()
    source_map = _load("g2_cordio_source_map_for_app_framework", SOURCE_MAP_ANALYZER).analyze(corpus)
    paths = _path_evidence(source_map, image)
    legacy = _legacy_evidence(image)
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("ambiqsuite-cordio-app-framework" in row.get("path", "") for row in overlay["sources"])
    if routed:
        raise AuditError("source oracle unexpectedly entered production")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only; authenticated source/corpus/image evidence; no hardware or firmware mutation",
        "lineage": {
            "component": "AmbiqSuite Cordio application framework",
            "selected_release": snapshot["selected_release"],
            "selected_commit": SELECTED_COMMIT,
            "public_packetcraft_ancestor": PACKETCRAFT_ANCESTOR,
            "historical_g2_generating_commit": None,
            "source_identification_closed": True,
            "exact_source_text_identity": False,
        },
        "stock_path_anchors": {
            "retained_paths": len(paths),
            "anchored_functions": sum(row["anchored_functions"] for row in paths),
            "anchored_body_bytes": sum(row["anchored_body_bytes"] for row in paths),
            "concatenated_anchor_sha256": EXPECTED_ALL_ANCHORS_SHA256,
            "prior_canonical_summary_sha256": EXPECTED_STOCK_SUMMARY_SHA256,
            "paths": paths,
        },
        "legacy_master_slave_objects": legacy,
        "g2_local_delta": {
            "exact_source_reconstruction_required": True,
            "database": "ten-record role-aware MRAM persistence and product policy",
            "other": ["privacy/address resolution", "pairing-failure cleanup", "connection policy", "product logging and UI policy"],
        },
        "production": {"source_admitted": True, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "source-path anchors are lower bounds and do not cover every function in each translation unit",
            "the selected public commit is a semantic rebuild oracle, not the private G2 producing commit",
            "G2-local extensions still require clean implementation and target validation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        anchors = report["stock_path_anchors"]
        legacy = report["legacy_master_slave_objects"]["aggregate"]
        print(
            "G2 AmbiqSuite Cordio application-framework lineage: PASS "
            f"({anchors['retained_paths']} paths, {anchors['anchored_functions']} anchored functions, "
            f"{legacy['linked_functions']} legacy master/slave functions)"
        )
        print("exact historical G2 commit: unobservable")
        print("production routing: disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
