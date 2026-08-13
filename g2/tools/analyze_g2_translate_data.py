#!/usr/bin/env python3
"""Fail-closed zero-anchor cross-referenced attestation for app\\gui\\translate\\translate_data.c.

The code carrying this path's literal references exists in the stock image
but was absorbed as unanchored rows into the sibling closure pinned below.
This audit claims zero additional body bytes and re-verifies both the
sibling rows and this path's identity evidence against the official image.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CL = ROOT / "tools/manifests/g2-translate-data-closure.tsv"
SIBLING = ROOT / "tools/manifests/g2-translate-ui-function-map.tsv"
PINS = {CL: "124f3b35de031eedf3634b7993b61dc071a89faf7e061217f6361e6bdaa0db0e", SIBLING: "4e027aa0a336ca9823ed1a0d0d4c9b95ac012fcb8b2a976ef9bd326437387a20"}
RETAINED = 'app\\gui\\translate\\translate_data.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\translate\\translate_data.c'
PATH_RUN = 0x6fe594
CELLS = (5892640,)
CELL_REFS = {5892640: (5891822, 5891886, 5891962, 5892036, 5892334)}
ALL_REFS = (5891822, 5891886, 5891962, 5892036, 5892334)
COVERING_ROWS = ((5891792, 5892578, 'c3ce8a7d4a0c00a26675322ceb5494b3d4f4becc210bff48812d1fe7af1eafeb'),)
EXPECTED_REFS_TOTAL = 5


def _sh(value):
    return hashlib.sha256(value).hexdigest()


def _cstring(blob, address):
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError("unterminated string at 0x%08x" % address)
    return blob[offset:end].decode("ascii")


def analyze(image=IMAGE):
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or _sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if _sh(path.read_bytes()) != expected:
            raise c.AuditError("manifest changed: " + path.name)
    sibling_text = SIBLING.read_text(encoding="utf8")
    for a, z, row_sha in COVERING_ROWS:
        if "0x%08X" % a not in sibling_text or "0x%08X" % z not in sibling_text or row_sha not in sibling_text:
            raise c.AuditError("covering row changed in sibling manifest")
        if _sh(c._slice(blob, a, z)) != row_sha:
            raise c.AuditError("covering row bytes changed in image")
    if _cstring(blob, PATH_RUN) != FULL_PATH:
        raise c.AuditError("retained path changed")
    for cell in CELLS:
        if struct.unpack("<I", c._slice(blob, cell, cell + 4))[0] != PATH_RUN:
            raise c.AuditError("path pointer cell changed")
        if t.literal_references(blob, cell) != list(CELL_REFS[cell]):
            raise c.AuditError("path literal references changed")
    if len(ALL_REFS) != EXPECTED_REFS_TOTAL or not all(any(a <= x < z for a, z, _ in COVERING_ROWS) for x in ALL_REFS):
        raise c.AuditError("path reference coverage changed")
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any(x.get("path", "").replace("\\", "/").split("/")[-1].lower() == 'translate_data.c' for x in overlay["sources"]):
        raise c.AuditError("object entered production overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only zero-anchor cross-referenced attestation",
        "identity": {"disposition": "linked-unanchored-previously-claimed", "ghidra_discovered_functions": 0, "image_sha256": c.IMAGE_SHA256, "path_anchored_functions": 0, "retained_path": RETAINED, "retained_product_path": FULL_PATH},
        "surface": {"body_bytes": 0, "linked_functions": 0, "path_literal_references": len(ALL_REFS), "physical_bytes": 0},
        "covering": {"covering_body_bytes": sum(z - a for a, z, _ in COVERING_ROWS), "covering_manifest": "g2-translate-ui-function-map.tsv", "covering_rows": len(COVERING_ROWS)},
        "evidence": {"pointer_cells": ["0x%08X" % x for x in CELLS], "path_string_run_address": "0x%08X" % PATH_RUN},
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
