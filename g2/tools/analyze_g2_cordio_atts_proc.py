#!/usr/bin/env python3
"""Fail-closed audit for Cordio's common ATT server request processors."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-atts-proc-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-atts-proc-provenance.tsv"
PINS = {
    MAP: "920f0ff707997c95a91fa1beca1e1488f6a7500a168d11d9e3323da7dd26939b",
    PROVENANCE: "9629db4789183df4010749b0a026fc277f028d9caee6aa3a76366cd96a0a511c",
}

FUNCTIONS = {
    "attsUuidCmp": (0x0056C550, 0x0056C5AA, "4a1581656b586e2110bf6d5209430cee8b45da2b9b8744076c8a2618cdf132f6"),
    "attsUuid16Cmp": (0x0056C5AA, 0x0056C5D4, "fbafb92e3a0cc0c9864db1b91bc96a3725786fa88dc03cff2fd0d4e34199d392"),
    "attsFindByHandle": (0x0056C5D4, 0x0056C610, "1708a4ab8f907b5d6f543d7471699c9a3b58042473de5b79e265410a0db0a918"),
    "attsFindInRange": (0x0056C610, 0x0056C66A, "d76fb110208dc52d9898f09d1b5a754a91f986004025916eaccea73268fda9c4"),
    "attsPermissions": (0x0056C66A, 0x0056C6FC, "8fa28e28a1aa4851a470d4dc2c074195923b416bbe77015536bb22d1202da8a4"),
    "attsProcMtuReq": (0x0056C6FC, 0x0056C924, "04dad7963212e23ac2c53c1022a90f7f92cab9197ff11f35d954d59fd70de9ec"),
    "attsProcFindInfoReq": (0x0056C930, 0x0056CAA8, "708c4978b46cb6fa1610a57d74cc2f60789524b042ca3abef0a4a7f699cd48df"),
    "attsProcReadReq": (0x0056CAA8, 0x0056CBCA, "1fe43670e121bab302479d1bbf9d19eba1e62def23410bb24e3a5a4a0a47e1d6"),
    "attsProcReadMultiVarReq": (0x0056CBCA, 0x0056CD96, "23dc0b8b8ce31f7d597b652a0021f9a279968dc769926c6940e51ac64d61e0d9"),
}
BODY_CONCAT_SHA = "2e76008ae954f8d7f2bd9e866cee89f035c69ef3278ffb0d2d3e88ee34578e48"
PHYSICAL = (0x0056C550, 0x0056CDC0)
PHYSICAL_SHA = "a68493f93b22a0f86bdc996e803e2f9c293a650fd413004c4959e7d83d1ef890"
GAPS = [
    (0x0056C924, 0x0056C930, "c02ec7b6b3ba35c2c447f9b03a9524ab2c51b381aa92f80a30e3afd9b4488570"),
    (0x0056CD96, 0x0056CDC0, "5604b6c0d4b912efb6f920cf3f8407bb13238c2b6ac0aac03566809caa6dc5d9"),
]
NONCODE_CONCAT_SHA = "5b66f9a1296f0800756bef673a03a604721503297db660726ca1b5365df3cb04"
POOL_WORDS = [0x2006E5F0, 0x0078CCCC, 0x0075E2F0, 0x00785300, 0x006DCA54, 0x0078CCD4, 0x200004B4, 0x007524FC, 0x0078A460, 0x00731C64]

CALLERS = {
    "attsUuidCmp": [0x0056D9D4, 0x0056DA78, 0x0056DA86],
    "attsUuid16Cmp": [0x0056E2F0],
    "attsFindByHandle": [0x00533DEC, 0x00534E6A, 0x005353FE, 0x0056CAD0, 0x0056CC44, 0x0056DAD2, 0x0056E15C, 0x005A5DA6, 0x005A5E60, 0x005A5FF6, 0x005A61A8],
    "attsFindInRange": [0x0056C9AC],
    "attsPermissions": [0x0056CAE6, 0x0056CC5C, 0x0056DAEC, 0x0056DE5A, 0x0056E02C, 0x0056E17A, 0x0056E33A, 0x0056E426, 0x005A5E7A, 0x005A6014],
    "attsProcMtuReq": [], "attsProcFindInfoReq": [], "attsProcReadReq": [], "attsProcReadMultiVarReq": [],
}
CALLER_DIGESTS = {
    "attsUuidCmp": "fd1cff8158cc34e821a1ddcc187ca8fe08d10abbacd7bdbf4a8c841e4d10f07e",
    "attsUuid16Cmp": "4f170e269af43d68a8f77693f0649efb8ed7ea73514f8aed7d29948504d6f722",
    "attsFindByHandle": "06516e8234cdad87ba0553975c4b4ee015ab0df26d8a2d7a49e8cb076e789ba7",
    "attsFindInRange": "75b9f8c3092a972a388f5ab4755e4096518d352a8297caab2117228ebe971509",
    "attsPermissions": "b22fd1a5679918c02be985d7d3739266fdcebb0bbd2b743b2f9e63a594755295",
    "attsProcMtuReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsProcFindInfoReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsProcReadReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsProcReadMultiVarReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}

ATTS_PROC_FCN_TBL = 0x2000045C
PROCESSOR_METHODS = {1: "attsProcMtuReq", 2: "attsProcFindInfoReq", 5: "attsProcReadReq", 16: "attsProcReadMultiVarReq"}
PROCESSOR_WORDS = {1: 0x0056C6FD, 2: 0x0056C931, 5: 0x0056CAA9, 16: 0x0056CBCB}
INITIALIZER_ENTRY_WINDOWS = [(0x00791AA0, 0x0056C6FD), (0x00791AA4, 0x0056C931), (0x00791AB0, 0x0056CAA9)]
SOURCE_PATH = b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_proc.c"
SOURCE_PATH_ADDRESS = 0x006DCA54
SOURCE_PATH_CELL = 0x0056CDA8


class AuditError(RuntimeError):
    """Raised when authenticated ATT processor evidence changes."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [BASE + offset for offset in range(len(blob) - 3) if blob[offset:offset + 4] == packed]


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


def source_inventory() -> list[str]:
    with MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(row["stock_status"] != "linked" for row in rows):
        raise AuditError("unexpected atts_proc source-map status")
    return [row["function"] for row in rows]


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")
    if source_inventory() != list(FUNCTIONS):
        raise AuditError("atts_proc source inventory changed")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = image_slice(blob, start, end)
        if sha(data) != expected:
            raise AuditError(f"stock atts_proc body changed: {name}")
        bodies.append(data)
    if sha(b"".join(bodies)) != BODY_CONCAT_SHA or sha(image_slice(blob, *PHYSICAL)) != PHYSICAL_SHA:
        raise AuditError("atts_proc physical/body concatenation changed")
    noncode = []
    for start, end, expected in GAPS:
        data = image_slice(blob, start, end)
        if sha(data) != expected:
            raise AuditError("atts_proc owned gap changed")
        noncode.append(data)
    if sha(b"".join(noncode)) != NONCODE_CONCAT_SHA:
        raise AuditError("atts_proc non-code concatenation changed")
    if noncode[-1][:2] != b"\0\0" or list(struct.unpack("<10I", noncode[-1][2:])) != POOL_WORDS:
        raise AuditError("atts_proc trailing literal pool changed")

    flashdb = load_tool("atts_proc_flashdb", "analyze_g2_flashdb.py")
    initialized = flashdb._decode_initialized_sram(blob)
    table = flashdb._sram_slice(initialized, ATTS_PROC_FCN_TBL, 72)
    table_words = list(struct.unpack("<18I", table))
    for method, expected in PROCESSOR_WORDS.items():
        if table_words[method] != expected:
            raise AuditError(f"live atts_proc method {method} changed")

    if occurrences(blob, SOURCE_PATH_ADDRESS) != [SOURCE_PATH_CELL]:
        raise AuditError("atts_proc path-cell closure changed")
    if image_slice(blob, SOURCE_PATH_ADDRESS, SOURCE_PATH_ADDRESS + len(SOURCE_PATH) + 1) != SOURCE_PATH + b"\0":
        raise AuditError("retained atts_proc source path changed")

    decoder = load_tool("atts_proc_thumb", "recover_apollo_embedded_source_paths.py")
    result = {start: [] for start, _, _ in FUNCTIONS.values()}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in result:
            result[target].append(address)
    for name, (start, _, _) in FUNCTIONS.items():
        sites = result[start]
        if sites != CALLERS[name]:
            raise AuditError(f"direct caller closure changed: {name}")
        if sha(b"".join(struct.pack("<I", site) for site in sites)) != CALLER_DIGESTS[name]:
            raise AuditError(f"direct caller digest changed: {name}")

    entries = {start for start, _, _ in FUNCTIONS.values()}
    interiors = {address for start, end, _ in FUNCTIONS.values() for address in range(start + 1, end)}
    stored_entries, stored_interiors = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in entries:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != INITIALIZER_ENTRY_WINDOWS or stored_interiors:
        raise AuditError("atts_proc initializer/interior window closure changed")
    for address in range(BASE, BASE + len(blob) - 3, 2):
        if decoder._thumb_bl_target(blob, address) in interiors:
            raise AuditError("unexpected direct BL into atts_proc interior")

    return {
        "schema_version": 1,
        "module": {
            "classification": "linked_eatt_common_server_processors",
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "owned_noncode_bytes": sum(end - start for start, end, _ in GAPS),
            "source_inventory_functions": len(FUNCTIONS), "source_only_functions": [],
            "direct_bl_ingress_sites": sum(len(sites) for sites in CALLERS.values()),
            "live_processor_table_entries": len(PROCESSOR_METHODS),
            "initializer_stream_entry_windows": len(INITIALIZER_ENTRY_WINDOWS),
            "strict_interior_pointers": 0,
        },
        "dispatch": {
            "processor_table_live_sram": ATTS_PROC_FCN_TBL,
            "methods": {str(method): {"name": PROCESSOR_METHODS[method], "entry": PROCESSOR_WORDS[method]} for method in PROCESSOR_METHODS},
            "initializer_stream_is_not_runtime_table": True,
        },
        "architecture": {
            "eatt_aware": True, "read_multiple_variable_linked": True,
            "mtu_request_rejected_on_eatt_bearer": True,
            "uuid16_uuid128_conversion": True,
            "authorization_callback_optional": True,
        },
        "abi": {"atts_cb": 0x2006E5F0, "p_att_cfg": 0x200004B4, "server_ccb_main_offset": 0x10, "server_ccb_slot_offset": 0x25},
        "lineage": {
            "selected_source": "Packetcraft r20.05c / byte-identical AmbiqSuite R4.4.1 import",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "455950e73bd19d0a6ee02e5bdfcd86149d0cb1cb",
            "selected_sha256": "b06af2dc72c57bb8742b5fbbf083dfdd2e5187768cb16db693e00463b8fcc502",
            "historical_generating_commit_resolved": False, "license": "Apache-2.0",
        },
        "production": {"source_owned_bytes_added": 0, "stock_bytes_replaced": 0},
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
        print("Cordio atts_proc closed: 9 linked functions / 4 initialized processor entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
