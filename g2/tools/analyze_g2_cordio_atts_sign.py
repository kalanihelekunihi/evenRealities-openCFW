#!/usr/bin/env python3
"""Fail-closed audit for the partially linked Cordio ATT server signing unit."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-atts-sign-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-atts-sign-provenance.tsv"
PINS = {
    MAP: "89369f57bbbf3c33fb8fd945ee4efb916bd787bcd94ebfeec38ea527f93dc342",
    PROVENANCE: "aafb0b8dc5bc9806f29f06165c3991b616496ac777d8140a0185ee6724398369",
}

FUNCTIONS = {
    "attsSignCcbByConnId": (0x0052DA58, 0x0052DB92, "b066681727edfd54fbe2c321a6b489d350307a51861588b8f27c3335b80230b6"),
    "AttsSetCsrk": (0x0052DBB8, 0x0052DBD6, "6ef6543f746785df8e7e4d17e9064655f8e806944e0593ef7778e65067c73916"),
    "AttsSetSignCounter": (0x0052DBD6, 0x0052DBE4, "b33b1f78e6c091eeaaf366d5df6791d25b9c5746fbcae44510100fcfa24ebd05"),
    "AttsGetSignCounter": (0x0052DBE4, 0x0052DBF0, "4730fb7f44b6ff8dc4ad2a1adef0015fa0272f8f77be137f67be238e5af53ff9"),
}
SOURCE_ONLY = ["attsSignedWriteStart", "attsProcSignedWrite", "attsSignMsgCback", "AttsSignInit"]
BODY_CONCAT_SHA = "ae182809d1df2204330f054459763a31c5ef66cea9854d869ea703d23c055e36"
PHYSICAL = (0x0052DA58, 0x0052DBF0)
PHYSICAL_SHA = "b62a735715edb1214ec0e9f1a9dd30f72cc928a1ac993930947f9b34a88853a8"
GAP = (0x0052DB92, 0x0052DBB8)
GAP_SHA = "706e93de2d85a233fcb8b9bb8dc5aa115b8363cf951532258e15d2f97340c7a5"
GAP_WORDS = [
    0x00525245, 0x00545441, 0x00494348, 0x0078CCDC, 0x0073C6C0,
    0x0077E2E4, 0x006DCAB4, 0x0078CCE4, 0x2007335C,
]

CALLERS = {
    "attsSignCcbByConnId": [0x0052DBC4, 0x0052DBCE, 0x0052DBDC, 0x0052DBE8],
    "AttsSetCsrk": [0x004B3852, 0x00534594],
    "AttsSetSignCounter": [0x004B3860, 0x005345A4],
    "AttsGetSignCounter": [0x005346D6],
}
CALLER_DIGESTS = {
    "attsSignCcbByConnId": "af69c700b6f439c682d7ceb5320d3d43ea5cfc459ebca731d2db84a4e1e0bff4",
    "AttsSetCsrk": "bdcb53e69bb32694246656590e50bcd3ed49533338a9bcd0205bd6a115aee7ce",
    "AttsSetSignCounter": "9d8e5847fc510583ddf93a1c93396e76cac1cab547f7b564eec1c1180a240ba3",
    "AttsGetSignCounter": "29c5915cbcb32644493eeceb12e6596272505f2826ffc893bfff5a283f03b0b5",
}

ATTS_SIGN_CB = 0x2007335C
ATTS_SIGN_CB_LITERAL_CELLS = [0x0052DBB4]
ATTS_CB = 0x2006E5F0
ATTS_CB_LITERAL_CELLS = [0x0052C6A8, 0x00533E98, 0x00535448, 0x0056CD98, 0x0056E4E4, 0x005A6258]
ATTS_SIGN_MSG_CBACK = ATTS_CB + 0x264
ATTS_INIT = 0x005351DC
ATTS_INIT_CALLS = [0x004B8062]
ATTS_INIT_SIGN_DEFAULT = (0x005351DC, 0x005351FE)
ATTS_INIT_SIGN_DEFAULT_SHA = "85a20cf3a78ced588aea2646cad67ce33ce738b1af5b88045dbb2feac094727d"
ATT_EMPTY_HANDLER = 0x004B4EE6
SEC_CMAC = 0x0053665C
SEC_CMAC_CALLS = [0x00535270, 0x0056CEE2]
SOURCE_PATH = b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_sign.c"
SOURCE_PATH_ADDRESS = 0x006DCAB4
SOURCE_PATH_CELL = 0x0052DBAC
ABSENT_PROCESSING_STRINGS = (
    b"ATTS CSRK not set", b"Signed write counter failed", b"Signed write sig failed",
)


class AuditError(RuntimeError):
    """Raised when authenticated server-signing evidence changes."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [BASE + offset for offset in range(len(blob) - 3) if blob[offset:offset + 4] == packed]


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("atts_sign_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_inventory() -> tuple[list[str], list[str]]:
    linked, source_only = [], []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] == "linked":
                linked.append(row["function"])
            elif row["stock_status"] == "source_only":
                source_only.append(row["function"])
            else:
                raise AuditError("unexpected atts_sign source-map status")
    return linked, source_only


def direct_calls(blob: bytes, decoder, target: int) -> list[int]:
    return [
        address for address in range(BASE, BASE + len(blob) - 3, 2)
        if decoder._thumb_bl_target(blob, address) == target
    ]


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")

    linked, source_only = source_inventory()
    if linked != list(FUNCTIONS) or source_only != SOURCE_ONLY:
        raise AuditError("atts_sign source inventory changed")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = image_slice(blob, start, end)
        if sha(data) != expected:
            raise AuditError(f"stock atts_sign body changed: {name}")
        bodies.append(data)
    if sha(b"".join(bodies)) != BODY_CONCAT_SHA:
        raise AuditError("atts_sign body concatenation changed")
    if sha(image_slice(blob, *PHYSICAL)) != PHYSICAL_SHA:
        raise AuditError("atts_sign physical interval changed")
    gap = image_slice(blob, *GAP)
    if sha(gap) != GAP_SHA or gap[:2] != b"\0\0" or list(struct.unpack("<9I", gap[2:])) != GAP_WORDS:
        raise AuditError("atts_sign alignment/literal gap changed")

    if occurrences(blob, ATTS_SIGN_CB) != ATTS_SIGN_CB_LITERAL_CELLS:
        raise AuditError("attsSignCb literal closure changed")
    if occurrences(blob, ATTS_CB) != ATTS_CB_LITERAL_CELLS:
        raise AuditError("attsCb literal closure changed")
    if occurrences(blob, ATTS_SIGN_MSG_CBACK):
        raise AuditError("unexpected direct sign callback-slot literal")
    if image_slice(blob, SOURCE_PATH_ADDRESS, SOURCE_PATH_ADDRESS + len(SOURCE_PATH) + 1) != SOURCE_PATH + b"\0":
        raise AuditError("retained atts_sign source path changed")
    if struct.unpack("<I", image_slice(blob, SOURCE_PATH_CELL, SOURCE_PATH_CELL + 4))[0] != SOURCE_PATH_ADDRESS:
        raise AuditError("retained atts_sign path cell changed")

    init_prefix = image_slice(blob, *ATTS_INIT_SIGN_DEFAULT)
    if sha(init_prefix) != ATTS_INIT_SIGN_DEFAULT_SHA:
        raise AuditError("AttsInit signing default changed")
    # The two final stores in this prefix install the default indication table
    # and the empty signing callback at attsCb +0x260/+0x264.
    if struct.pack("<I", ATT_EMPTY_HANDLER | 1) not in image_slice(blob, 0x0053547C, 0x00535484):
        raise AuditError("AttsInit empty-handler literal changed")

    for marker in ABSENT_PROCESSING_STRINGS:
        if marker in blob:
            raise AuditError(f"unexpected signed-write processing marker appeared: {marker!r}")

    decoder = load_decoder()
    for name, (start, _, _) in FUNCTIONS.items():
        sites = direct_calls(blob, decoder, start)
        if sites != CALLERS[name]:
            raise AuditError(f"direct caller closure changed: {name}")
        raw = b"".join(struct.pack("<I", site) for site in sites)
        if sha(raw) != CALLER_DIGESTS[name]:
            raise AuditError(f"direct caller digest changed: {name}")
    if direct_calls(blob, decoder, ATTS_INIT) != ATTS_INIT_CALLS:
        raise AuditError("AttsInit caller closure changed")
    if direct_calls(blob, decoder, SEC_CMAC) != SEC_CMAC_CALLS:
        raise AuditError("SecCmac caller closure changed")

    entries = {start for start, _, _ in FUNCTIONS.values()}
    interiors = {
        address for start, end, _ in FUNCTIONS.values()
        for address in range(start + 1, end)
    }
    stored_entries, stored_interiors = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in entries:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries or stored_interiors:
        raise AuditError("unexpected stored atts_sign entry/interior pointer")
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in interiors:
            raise AuditError("unexpected direct branch into atts_sign interior")

    return {
        "schema_version": 1,
        "module": {
            "classification": "partially_linked_configuration_only",
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "source_inventory_functions": len(linked) + len(source_only),
            "source_only_functions": source_only,
            "direct_bl_ingress_sites": sum(len(sites) for sites in CALLERS.values()),
            "stored_function_pointers": 0,
            "strict_interior_pointers": 0,
        },
        "abi": {
            "atts_sign_cb": ATTS_SIGN_CB, "atts_sign_cb_bytes": 56,
            "connection_records": 3, "connection_record_stride": 16,
            "sign_counter_offset": 0, "csrk_offset": 4,
            "current_buffer_offset": 8, "authenticated_offset": 12,
            "atts_cb": ATTS_CB, "sign_message_callback_offset": 0x264,
        },
        "processing_exclusion": {
            "atts_init_installs_empty_sign_handler": True,
            "atts_sign_init_linked": False,
            "signed_write_processor_linked": False,
            "signed_write_cmac_worker_linked": False,
            "signed_write_completion_callback_linked": False,
            "later_sign_handler_installations": 0,
            "signed_write_cmac_calls": 0,
            "processing_failure_strings": 0,
        },
        "lineage": {
            "selected_source": "official later AmbiqSuite R4.4.1 import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "c2f34343cd43e4633ec50f4899ab3e7af9bee820",
            "selected_sha256": "9a4b42b2e6cb0549eabfa4479a3a7516b8030c63f4497fcac227cb6a1bd7a81d",
            "authenticated_csrk_extension": True,
            "public_r20_api_exact": False,
            "historical_generating_commit_resolved": False,
            "license": "Apache-2.0",
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
        print("Cordio atts_sign closed: 4 linked configuration functions / 4 processing functions stripped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
