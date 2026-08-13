#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio ATT client core."""

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
BASE = 0x437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-attc-main-function-map.tsv"
PINS = {
    MAP: "73ea5905f4aeb135580773180651d378507aa5622dc3556c0fa27e950b9b807e",
    ROOT / "tools/manifests/packetcraft-cordio-attc-main-provenance.tsv": (
        "eccd860cc288b9c00d35477df196468738b2fe5d8c2a9acb2e839563f413038b"
    ),
}

CALLS = {
    "attcPendWriteCmd": [0x531766],
    "attcSetPendWriteCmd": [0x53107E],
    "attcWriteCmdCallback": [0x531354, 0x531474],
    "attcSendSimpleReq": [0x53104E, 0x53105A],
    "attcSendContinuingReq": [],
    "attcSendMtuReq": [],
    "attcSendWriteCmd": [],
    "attcSendPrepWriteReq": [],
    "attcSendReq": [0x4B552E, 0x531196],
    "attcSetupReq": [0x4B5560, 0x5317AC],
    "attcDataCback": [],
    "attcCtrlCback": [],
    "attcConnCback": [],
    "attcMsgCback": [],
    "attcCcbByConnId": [0x4B5656, 0x53133A, 0x531712],
    "attcCcbByHandle": [0x4B594C, 0x5311A6],
    "attcFreePkt": [0x4B54EE, 0x530F1E, 0x53172A, 0x531AFC],
    "attcExecCallback": [0x4B56F8, 0x4B570C, 0x530E14, 0x531076, 0x531B0C],
    "attcReqClear": [0x530E9A, 0x5310F4, 0x5313E6, 0x531422, 0x531776, 0x5317D4, 0x53180E],
    "AttcInit": [0x4B806A],
}

GAPS = [
    (0x531154, 0x531160, "c02ec7b6b3ba35c2c447f9b03a9524ab2c51b381aa92f80a30e3afd9b4488570"),
    (0x531326, 0x531330, "6cf02a751832701b4178158c7b57f37a4fe54a512b9c6928bb517fa4699f7406"),
    (0x5315A8, 0x5315B4, "25dfa65b3a69b6232caf04ec5490ce44d1c26396373ff80c26fb2887b48e354d"),
    (0x531816, 0x531820, "acfceccdeb3cf2093cf58d4103c648f2fbf118e94d9205455caa81a994201bea"),
    (0x531AAA, 0x531AC0, "18c8a85fa796af8f24591ccbb85278584ae5af2431c3a19b9d9a1defbac82415"),
    (0x531B16, 0x531B1C, "f7816ff62a45bfba7577e0f509bbd1f66f11a621a2ebbc7aaaacd5a25240b91f"),
    (0x531B90, 0x531BD4, "7cd493f034f35dad0dc753f855d157d68de21adf863f3b8028a7e3e9e2dce231"),
]

SEND_TABLE = [
    0,
    0x530F09,
    0x530E65,
    0x530E65,
    0x530E65,
    0x530E31,
    0x530E65,
    0x530E31,
    0x530E65,
    0x530E31,
    0x531055,
    0x531089,
    0x530E31,
    0,
    0,
    0,
    0x530E31,
]
INTERFACE = [0x53119D, 0x531331, 0x5315B5, 0x53135B]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("attc_main_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows():
    linked, source_only = [], []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] == "linked":
                linked.append(
                    (
                        row["function"],
                        int(row["stock_start"], 0),
                        int(row["stock_end_exclusive"], 0),
                        row["stock_sha256"],
                    )
                )
            else:
                source_only.append(row["function"])
    return linked, source_only


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise RuntimeError(f"pinned input changed: {path}")

    linked, source_only = load_rows()
    if len(linked) != 20 or source_only != ["AttcSetAutoConfirm"]:
        raise RuntimeError("source inventory changed")
    bodies = []
    for name, start, end, digest in linked:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != digest:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "4ad46a1239865f2b236a5a94d3b501a32efc7d208f4bb8826e85a9551a60212a":
        raise RuntimeError("body concat changed")
    if sha(image_slice(blob, 0x530D74, 0x531BD4)) != "3571bc76a244b81e8a605b4da8386fc1f3007b49eb3fae763ab077101422970d":
        raise RuntimeError("physical object changed")
    for start, end, digest in GAPS:
        if sha(image_slice(blob, start, end)) != digest:
            raise RuntimeError(f"owned data changed at {start:#x}")

    path_bytes = image_slice(blob, 0x6DC814, 0x6DC874)
    if sha(path_bytes) != "64a5de8c467d8de43fbf957506b1d675ab7762004f09cb3c9f57b8faa10a4b01":
        raise RuntimeError("retained path changed")
    literals = {
        0x531BA0: 0x700920,
        0x531BAC: 0x2006F904,
        0x531ABC: 0x6DC814,
        0x531BCC: 0x200610AC,
        0x531BD0: 0x785250,
    }
    for address, expected in literals.items():
        if struct.unpack_from("<I", blob, address - BASE)[0] != expected:
            raise RuntimeError(f"literal changed at {address:#x}")

    send_data = image_slice(blob, 0x700920, 0x700964)
    if sha(send_data) != "63b7a30278fdb4c9cdab55b9a5f40bc8d24fad6fd114d014a8e38dc391f8ad0a":
        raise RuntimeError("send-request table changed")
    if list(struct.unpack("<17I", send_data)) != SEND_TABLE:
        raise RuntimeError("send-request dispatch changed")
    interface_data = image_slice(blob, 0x785250, 0x785260)
    if sha(interface_data) != "e3f7d889b2b7fd85cc4ac0ebefa49f4292ed1f738f3baa20885b70210feb3ed9":
        raise RuntimeError("client interface changed")
    if list(struct.unpack("<4I", interface_data)) != INTERFACE:
        raise RuntimeError("client interface dispatch changed")

    decoder = load_decoder()
    starts = {start: name for name, start, _, _ in linked}
    calls = {name: [] for name, _, _, _ in linked}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
    if calls != CALLS:
        raise RuntimeError("direct ingress changed")

    expected_stored = []
    for address in range(0x700920, 0x700964, 4):
        value = struct.unpack_from("<I", blob, address - BASE)[0]
        if (value & ~1) in starts:
            expected_stored.append((address, value))
    for address in range(0x785250, 0x785260, 4):
        value = struct.unpack_from("<I", blob, address - BASE)[0]
        if (value & ~1) in starts:
            expected_stored.append((address, value))
    interiors = set()
    for _, start, end, _ in linked:
        interiors.update(range(start + 2, end, 2))
    stored, inside = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts:
            stored.append((BASE + offset, value))
        elif target in interiors:
            inside.append((BASE + offset, value))
    if stored != sorted(expected_stored) or len(stored) != 17:
        raise RuntimeError("stored entry-pointer closure changed")
    if inside:
        raise RuntimeError("stored strict-interior pointer found")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x530D74,
            "end_exclusive": 0x531BD4,
            "physical_bytes": 3680,
            "linked_function_count": 20,
            "linked_function_bytes": 3540,
            "source_inventory_functions": 21,
            "source_only_functions": source_only,
            "direct_bl_ingress_sites": 32,
            "registered_function_pointers": 17,
            "strict_interior_pointers": 0,
        },
        "architecture": {
            "retained_source_path": 0x6DC814,
            "attc_control_block": 0x2006F904,
            "att_control_block": 0x200610AC,
            "attc_ccb_bytes": 44,
            "connection_count": 3,
            "bearers_per_connection": 3,
            "send_request_entries": 17,
            "client_interface": 0x785250,
            "r4_zero_length_data_guard": True,
            "auto_confirm_initialized_true": True,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "10cb08f29cd37d0e6f86cdf1b35ad185ae052d11",
            "selected_sha256": "e5235e4929ee10a88c80fcf7a3fb4465a329efaa5d428a24796a1f3b26d729e8",
            "later_r4_sha256": "fba056a78c5bfa9157e05ccc1ede07e4c7ee297c4a975eec34a3e820c795b2a0",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "historical_generating_commit_resolved": False,
            "discriminator": "r20 EATT request/bearer architecture plus official R4 zero-length-data guard",
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
        print("Cordio attc_main closed: 20 linked / 1 source-only; 32 BL + 17 stored ingress")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
