#!/usr/bin/env python3
"""Fail-closed exclusion audit for the optional Cordio EATT client on G2."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FM = ROOT / "tools/manifests/packetcraft-cordio-attc-eatt-function-map.tsv"
PV = ROOT / "tools/manifests/packetcraft-cordio-attc-eatt-provenance.tsv"
PINS = {
    FM: "9857db79749973bec183818a5d2a8758e478608f1d0d404927d1d5e59c1262ec",
    PV: "a5268a8199e8c2686dbbe5370a7c8f22b2684b1a10d21c5e29f4633ee13ecdd8",
}
ABSENT_MARKERS = (b"attc_eatt.c", b"eattcGetFreeSlot", b"EattcFindInfoReq", b"EattcReadMultVarLenReq")


class AuditError(RuntimeError):
    """Raised when authenticated optional-EATT-client evidence changes."""


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


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")
    with FM.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 20 or any(row["stock_status"] != "dead_stripped" or row["stock_address"] != "-" for row in rows):
        raise AuditError("attc_eatt source inventory changed")
    for marker in ABSENT_MARKERS:
        if marker in blob:
            raise AuditError(f"unexpected EATT-client marker appeared: {marker!r}")

    att_eatt = load_tool("attc_eatt_core", "analyze_g2_cordio_att_eatt.py").analyze(image_path)
    if att_eatt["module"]["linked_function_count"] != 0:
        raise AuditError("EATT core is no longer excluded")
    att_main_module = load_tool("attc_eatt_att_main", "analyze_g2_cordio_att_main.py")
    att_main = att_main_module.analyze(image_path)
    if not att_main["architecture"]["eatt_defaults_installed_by_att_handler_init"]:
        raise AuditError("ATT default EATT client interface no longer established")
    attc_main_module = load_tool("attc_eatt_attc_main", "analyze_g2_cordio_attc_main.py")
    attc_main = attc_main_module.analyze(image_path)
    if attc_main["architecture"]["att_control_block"] != 0x200610AC:
        raise AuditError("ATTC control-block relationship changed")
    if att_main_module.CALLERS["attMsgAlloc"] != [
        0x004B5606, 0x004B572A, 0x004B5762, 0x004B57AE, 0x004B5802, 0x004B5964,
        0x00530E76, 0x005310B4, 0x00533D28, 0x00534CA6, 0x00534E36, 0x00539DFC,
        0x0056C492, 0x0056C502, 0x0056C8E0, 0x0056C986, 0x0056CB6A, 0x0056CC00,
        0x0056DB9C, 0x0056DC68, 0x0056DF1E, 0x0056E110, 0x0056E352, 0x005A5F4C,
        0x005A60FC, 0x005A6236,
    ]:
        raise AuditError("attMsgAlloc provider closure changed")
    if attc_main_module.CALLS["attcCcbByConnId"] != [0x004B5656, 0x0053133A, 0x00531712]:
        raise AuditError("attcCcbByConnId provider closure changed")

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
            "att_control_block": 0x200610AC,
            "eatt_client_interface_offset": 0x48,
            "default_eatt_client_interface": 0x007851F0,
            "eatt_client_initializers": 0,
            "eatt_core_linked_functions": 0,
            "att_msg_alloc_callers": att_main_module.CALLERS["attMsgAlloc"],
            "attc_ccb_by_conn_id_callers": attc_main_module.CALLS["attcCcbByConnId"],
            "public_tree_consumers_outside_translation_unit": 0,
            "retained_eatt_client_markers": 0,
            "mandatory_init_contract": "EattcInit must replace attCb.pEnClient at +0x48 with attcFcnIf",
            "closure_argument": "all request builders flow through the closed packet allocator/send path; callbacks are rooted only by the absent interface initializer",
        },
        "lineage": {
            "selected_optional_blob": "45305ddb59ed34713f02f9a2783b62eca25cfc04",
            "selected_optional_sha256": "8f5e062300131697f705461eecdf57b1639e4b2168520dea5b8395e40e62f713",
            "later_r4_blob": "3555f7784b6f16f634a60bdd5658d6e9ecc24288",
            "later_r4_sha256": "c09d391bca06db1ba4129ee778848927576b4bb7adf33a118db4d80eafa53345",
            "license": "Apache-2.0",
            "stock_body_version_discriminated": False,
            "r4_delta": "equivalent explicit non-null spelling in eattcGetFreeSlot",
            "compatibility_basis": "surrounding proven r20/R4 ATT three-bearer client ABI",
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
        print("Cordio attc_eatt excluded: 20 source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
