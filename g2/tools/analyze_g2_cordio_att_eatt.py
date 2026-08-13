#!/usr/bin/env python3
"""Fail-closed exclusion audit for the optional Cordio EATT core on G2."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FM = ROOT / "tools/manifests/packetcraft-cordio-att-eatt-function-map.tsv"
PV = ROOT / "tools/manifests/packetcraft-cordio-att-eatt-provenance.tsv"
PINS = {
    FM: "dca4961ec9a048005d9f02932fd76beda3b811eec8f5d2d619237ad215212023",
    PV: "1bc754eef2b95c0cffc6529e6113598e6643900e2b008d6ef99772e71329c8f9",
}

ATT_CB = 0x200610AC
ATT_CB_CELLS = [0x004B51D0, 0x004B599C, 0x00531BCC, 0x00533EB0, 0x00535464]
ABSENT_MARKERS = (
    b"att_eatt.c",
    b"EattEstablishChannels",
    b"EattReconfigureChannels",
    b"eattReqNextChannels",
)


class AuditError(RuntimeError):
    """Raised when authenticated optional-EATT evidence changes."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_tool(name: str, filename: str):
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / filename)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def occurrences(blob: bytes, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    return [BASE + offset for offset in range(len(blob) - 3) if blob[offset:offset + 4] == needle]


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")
    with FM.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 26 or any(row["stock_status"] != "dead_stripped" or row["stock_address"] != "-" for row in rows):
        raise AuditError("att_eatt source inventory changed")
    if occurrences(blob, ATT_CB) != ATT_CB_CELLS:
        raise AuditError("attCb literal-reference closure changed")
    for marker in ABSENT_MARKERS:
        if marker in blob:
            raise AuditError(f"unexpected EATT-core marker appeared: {marker!r}")

    att_main = load_tool("att_eatt_att_main", "analyze_g2_cordio_att_main.py").analyze(image_path)
    architecture = att_main["architecture"]
    if not architecture["eatt_defaults_installed_by_att_handler_init"]:
        raise AuditError("ATT default EATT interface no longer established")
    if architecture["enhanced_att_runtime_override_seen_in_this_tu"]:
        raise AuditError("ATT core unexpectedly reports an EATT override")
    l2c_coc = load_tool("att_eatt_l2c_coc", "analyze_g2_cordio_l2c_coc.py").analyze(image_path)
    if l2c_coc["module"]["linked_function_count"] != 0:
        raise AuditError("L2CAP CoC is no longer excluded")

    return {
        "schema_version": 1,
        "module": {
            "classification": "not_linked_or_dead_stripped",
            "linked_function_count": 0,
            "linked_function_bytes": 0,
            "source_inventory_functions": len(rows),
            "source_only_functions": [row["function"] for row in rows],
            "retained_path_anchors": 0,
            "semantic_body_anchors": 0,
        },
        "exclusion": {
            "att_control_block": ATT_CB,
            "att_control_block_literal_cells": ATT_CB_CELLS,
            "eatt_handler_offset": 0x4C,
            "eatt_dm_callback_offset": 0x50,
            "eatt_l2c_data_req_offset": 0x54,
            "eatt_core_initializers": 0,
            "l2cap_coc_linked_functions": 0,
            "public_tree_consumers_outside_translation_unit": 0,
            "retained_eatt_core_markers": 0,
            "mandatory_init_contract": "EattInit must register L2CAP CoC and replace attCb callbacks at +0x4C/+0x50/+0x54",
            "closure_argument": "the mandatory initializer and every CoC-dependent public path are impossible after the independently closed CoC exclusion; the only standalone public leaf has no public-tree consumer",
        },
        "lineage": {
            "selected_optional_blob": "330d9efe93ef9c994dc996b54efcd3c3d6a2b135",
            "selected_optional_sha256": "16cee15a33f157fc560a8983c057fd5e5186f686ee0d1a8424b0a364d36861d1",
            "later_r4_blob": "a00610aceb87cc04538b921b9277ee28f908743d",
            "later_r4_sha256": "f0ba94715e834d7d7761091c495e24104a43aca6dbdd63775716d56d9a215e67",
            "license": "Apache-2.0",
            "stock_body_version_discriminated": False,
            "r4_delta": "AM_BLE_EATT guard moves automatic channel establishment to the L2CAP callback",
            "compatibility_basis": "surrounding proven r20/R4 ATT three-bearer ABI",
        },
        "production": {"stock_bytes_replaced": 0, "source_owned_bytes_added": 0},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Cordio att_eatt excluded: 26 source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
