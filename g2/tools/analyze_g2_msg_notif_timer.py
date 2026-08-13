#!/usr/bin/env python3
"""Fail-closed zero-anchor cross-referenced attestation for app\\gui\\MessageNotify\\msg_notif_timer.c.

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
CL = ROOT / "tools/manifests/g2-msg-notif-timer-closure.tsv"
SIBLING = ROOT / "tools/manifests/g2-ui-msg-notif-list-function-map.tsv"
PINS = {CL: "1e9de1ce141495b4a72a4544a18650dcf357bb78c79109bc6c634dc9df7dd89e", SIBLING: "67d9541d516f3a31a38e0608874acc8c4d7c9402f0eac2b748b76cbc066b3b63"}
RETAINED = 'app\\gui\\MessageNotify\\msg_notif_timer.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\MessageNotify\\msg_notif_timer.c'
PATH_RUN = 0x6f4604
CELLS = (5581544,)
CELL_REFS = {5581544: (5581022, 5581088, 5581176, 5581244, 5581338, 5581414)}
ALL_REFS = (5581022, 5581088, 5581176, 5581244, 5581338, 5581414)
COVERING_ROWS = ((5580984, 5581062, 'b3a1c5d957946d28b9b28afc28207bb4757a749a3c22b407a93416ab339954bd'), (5581062, 5581128, 'c7f9ff0ef7866345bc7f73967808f1b9935f2f145943cf956d70bb7800f671f2'), (5581128, 5581218, '4e0b652917c86b4d69031dbe8d177b0e38c522971e2de418a8478bfd50c5c093'), (5581218, 5581284, '215fbc85e486694ab5962b4fcef100313945a0f00d4ffbc8dd697eefd94f683d'), (5581284, 5581386, '011ab160b2a247e6c42960f449d75750c1f1fae9bd09bbeb194ffc01fbf37a47'), (5581386, 5581488, '7a9505c00c6a6b1f98f6c63a987b55e434cf7ab5e5388f09bd17d64f8267cbc7'))
EXPECTED_REFS_TOTAL = 6


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
    if any(x.get("path", "").replace("\\", "/").split("/")[-1].lower() == 'msg_notif_timer.c' for x in overlay["sources"]):
        raise c.AuditError("object entered production overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only zero-anchor cross-referenced attestation",
        "identity": {"disposition": "linked-unanchored-previously-claimed", "ghidra_discovered_functions": 0, "image_sha256": c.IMAGE_SHA256, "path_anchored_functions": 0, "retained_path": RETAINED, "retained_product_path": FULL_PATH},
        "surface": {"body_bytes": 0, "linked_functions": 0, "path_literal_references": len(ALL_REFS), "physical_bytes": 0},
        "covering": {"covering_body_bytes": sum(z - a for a, z, _ in COVERING_ROWS), "covering_manifest": "g2-ui-msg-notif-list-function-map.tsv", "covering_rows": len(COVERING_ROWS)},
        "evidence": {"pointer_cells": ["0x%08X" % x for x in CELLS], "path_string_run_address": "0x%08X" % PATH_RUN},
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
