#!/usr/bin/env python3
"""Fail-closed exclusion audit for the optional Cordio EATT server on G2."""

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
FM = ROOT / "tools/manifests/packetcraft-cordio-atts-eatt-function-map.tsv"
PV = ROOT / "tools/manifests/packetcraft-cordio-atts-eatt-provenance.tsv"
PINS = {
    FM: "4b7404bf4c878de39b1d4e3b55411df24d8bc397ac5db881e24e18fd046f7dc1",
    PV: "ad2f52f0af841f76db13b3c6e545b6ffe29d019009ce9933a9a81cc3a5cfe801",
}

ATT_CB = 0x200610AC
ATT_CB_CELLS = [0x004B51D0, 0x004B599C, 0x00531BCC, 0x00533EB0, 0x00535464]
ATT_CCB_BY_CONN_ID = 0x004B4EEE
ATT_CCB_CALLERS = [0x004B4E10, 0x004B4E58, 0x004B5208]
ATTS_HANDLE_VALUE_WORKER = 0x00533C6C
ATTS_HANDLE_VALUE_CALLERS = [0x00533ED2, 0x00533EEE]
INITIALIZERS = {
    (0x004B511E, 0x004B5146): "3fd39a6ee0725a847482491557373f558cd27ca4b0c81b1c0e92846676e8f342",
    (0x00531B1C, 0x00531B90): "c1be6b3ada20c1c70cb53db7b6ae8600f68c4c936d9f21f81f1817c92fc1ca48",
    (0x005351DC, 0x00535258): "e95331e3a4690f7f3b6fe71c099316a36971c554d3d629601db19f7414e856b6",
}
ABSENT_MARKERS = (b"atts_eatt.c", b"eattsGetFreeSlot", b"EattsMultiValueNtf", b"EattsContinueWriteReq")


class AuditError(RuntimeError):
    """Raised when authenticated optional-EATT evidence changes."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


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
    if len(rows) != 12 or any(row["stock_status"] != "dead_stripped" or row["stock_address"] != "-" for row in rows):
        raise AuditError("atts_eatt source inventory changed")
    if occurrences(blob, ATT_CB) != ATT_CB_CELLS:
        raise AuditError("attCb literal-reference closure changed")
    for bounds, expected in INITIALIZERS.items():
        if sha(image_slice(blob, *bounds)) != expected:
            raise AuditError(f"ATT initializer changed at {bounds[0]:#x}")
    for marker in ABSENT_MARKERS:
        if marker in blob:
            raise AuditError(f"unexpected EATT-server marker appeared: {marker!r}")

    att_main = load_tool("atts_eatt_att_main", "analyze_g2_cordio_att_main.py").analyze(image_path)
    if not att_main["architecture"]["eatt_defaults_installed_by_att_handler_init"]:
        raise AuditError("ATT default EATT interface no longer established")
    if att_main["module"]["source_only_functions"] != ["attCcbByHandle", "AttMsgAlloc"]:
        raise AuditError("ATT zero-copy allocation boundary changed")
    l2c_coc = load_tool("atts_eatt_l2c_coc", "analyze_g2_cordio_l2c_coc.py").analyze(image_path)
    if l2c_coc["module"]["linked_function_count"] != 0:
        raise AuditError("L2CAP CoC is no longer excluded")

    decoder = load_tool("atts_eatt_thumb", "recover_apollo_embedded_source_paths.py")
    by_target: dict[int, list[int]] = {}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target is not None:
            by_target.setdefault(target, []).append(address)
    if by_target.get(ATT_CCB_BY_CONN_ID, []) != ATT_CCB_CALLERS:
        raise AuditError("attCcbByConnId caller closure changed")
    if by_target.get(ATTS_HANDLE_VALUE_WORKER, []) != ATTS_HANDLE_VALUE_CALLERS:
        raise AuditError("ATTS handle-value worker caller closure changed")

    return {
        "schema_version": 1,
        "module": {
            "classification": "not_linked_or_dead_stripped",
            "linked_function_count": 0, "linked_function_bytes": 0,
            "source_inventory_functions": len(rows),
            "source_only_functions": [row["function"] for row in rows],
            "retained_path_anchors": 0, "semantic_body_anchors": 0,
        },
        "exclusion": {
            "att_control_block": ATT_CB,
            "att_control_block_literal_cells": ATT_CB_CELLS,
            "eatt_server_interface_offset": 0x44,
            "default_eatt_server_interface": 0x007851F0,
            "eatt_server_initializers": 0,
            "att_ccb_by_conn_id_callers": ATT_CCB_CALLERS,
            "handle_value_worker_callers": ATTS_HANDLE_VALUE_CALLERS,
            "l2cap_coc_linked_functions": 0,
            "retained_eatt_server_markers": 0,
            "mandatory_init_contract": "EattsInit must replace attCb.pEnServer at +0x44 with attsFcnIf",
            "closure_argument": "every externally useful send/data/continuation path either calls attCcbByConnId, calls the shared handle-value worker, or is rooted by the absent attsFcnIf initializer",
        },
        "lineage": {
            "selected_optional_blob": "f1ca4879c8c32ef42127971399592329ca084680",
            "selected_optional_sha256": "99d169c7e0066186fb6d1ebfe718f36c84a45eddf54b4a99091747deedc51355",
            "license": "Apache-2.0", "stock_body_version_discriminated": False,
            "compatibility_basis": "surrounding proven r20/R4 ATT three-bearer and message ABI",
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
        print("Cordio atts_eatt excluded: 12 source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
