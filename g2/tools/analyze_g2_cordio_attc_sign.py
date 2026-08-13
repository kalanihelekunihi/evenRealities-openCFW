#!/usr/bin/env python3
"""Fail-closed exclusion audit for optional Cordio ATT client signing."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-attc-sign-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-attc-sign-provenance.tsv"

# Filled with immutable SHA-256 pins after the two authored manifests.
PINS = {
    MAP: "1073b3730f7594a11fb2eaeed974c9c06ee36c9b575baffc4f628f65c5f61dbc",
    PROVENANCE: "92461826056a715d49ebe8d84d983bd0f3df422ca8e2ba3f24c5cef192fe95d4",
}

ATTC_CB = 0x2006F904
ATTC_SIGN_SLOT = ATTC_CB + 0x1B0
ATTC_CB_LITERAL_CELLS = [0x004B59A8, 0x00531BAC]
ATTC_CB_LITERAL_CELLS_SHA = "2a6d9e181c5717922a0077f080dcbb124e501e754a001c3bd054f1e7864ac746"
ATTC_INIT = 0x00531B1C
ATTC_INIT_CALLS = [0x004B806A]
ATTC_INIT_CALLS_SHA = "29d7980f43ad49f470e875c97487a4ccebcefb5f2a3e54fe5ca4a9ae3784340d"
ATTC_INIT_SIGN_CLEAR = (0x00531B1C, 0x00531B2C)
ATTC_INIT_SIGN_CLEAR_SHA = "80f9038ef13280f56e56effb0562eebca8810bedf8a23628334f98858a0fb74f"

SEC_CMAC = 0x0053665C
DM_SEC_GET_LOCAL_CSRK = 0x004D251E
DM_CONN_SEC_LEVEL = 0x004B71B2
ATTC_WRITE_CMD = 0x00539DEA
PROVIDER_CALLS = {
    SEC_CMAC: [0x00535270, 0x0056CEE2],
    DM_SEC_GET_LOCAL_CSRK: [0x0056EB34],
    DM_CONN_SEC_LEVEL: [
        0x004B468C, 0x0050382A, 0x00503FDA, 0x0052C632,
        0x00532D50, 0x0056C6A6, 0x0056E680,
    ],
    ATTC_WRITE_CMD: [0x004C4A60],
}
PROVIDER_CALL_SHA = {
    SEC_CMAC: "c128088e846db07524185e43caa9c3d1949ce6bbadc902b50b889979f2b4e1cb",
    DM_SEC_GET_LOCAL_CSRK: "47fc76f15205fceccd5bac43dfdec76b74dae7b52a8889028a619808062d97a2",
    DM_CONN_SEC_LEVEL: "c975c072febb4a80c79585e98b2fe85509df169fd7657e867c6e5d000d26ead2",
    ATTC_WRITE_CMD: "012f4c6d49ecf3d5c66e2c4af6ed07702f1f4b86a2135a38eef5e6c750ab06bd",
}

# The sole AttcWriteCmd caller is a product command dispatcher.  Its complete
# Ghidra-bounded body has no call to DmConnSecLevel, excluding the mandatory
# encrypted-link fallback shape of AttcSignedWriteCmd.
WRITE_CALLER = (0x004C4910, 0x004C4B7E)
WRITE_CALLER_SHA = "6698734dc25fe37714846d077d9e2ca32f02f1b877b09089126e726eb053ff6d"
ABSENT_MARKERS = (b"attc_sign.c", b"attcSign", b"AttcSign", b"AttcSignedWriteCmd")


class AuditError(RuntimeError):
    """Raised when authenticated client-signing exclusion evidence changes."""


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
    spec = importlib.util.spec_from_file_location("attc_sign_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_functions() -> list[str]:
    names = []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] != "dead_stripped" or row["stock_address"] != "-":
                raise AuditError("client-signing source map no longer records total exclusion")
            names.append(row["function"])
    return names


def direct_calls(blob: bytes, decoder, target: int) -> list[int]:
    return [
        address
        for address in range(BASE, BASE + len(blob) - 3, 2)
        if decoder._thumb_bl_target(blob, address) == target
    ]


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")

    functions = source_functions()
    if functions != [
        "attcSignCbAlloc", "attcSignCbFree", "attcSignCbByConnId",
        "attcSignCloseCback", "attcSignMsgCback", "AttcSignedWriteCmd",
        "AttcSignInit",
    ]:
        raise AuditError("client-signing source inventory changed")

    if occurrences(blob, ATTC_CB) != ATTC_CB_LITERAL_CELLS:
        raise AuditError("attcCb literal closure changed")
    packed_cells = b"".join(struct.pack("<I", value) for value in ATTC_CB_LITERAL_CELLS)
    if sha(packed_cells) != ATTC_CB_LITERAL_CELLS_SHA:
        raise AuditError("attcCb literal-cell digest changed")
    if occurrences(blob, ATTC_SIGN_SLOT):
        raise AuditError("unexpected direct attcCb.pSign literal appeared")
    if sha(image_slice(blob, *ATTC_INIT_SIGN_CLEAR)) != ATTC_INIT_SIGN_CLEAR_SHA:
        raise AuditError("AttcInit signing-pointer clear changed")

    for marker in ABSENT_MARKERS:
        if marker in blob:
            raise AuditError(f"unexpected client-signing marker appeared: {marker!r}")

    decoder = load_decoder()
    init_calls = direct_calls(blob, decoder, ATTC_INIT)
    if init_calls != ATTC_INIT_CALLS:
        raise AuditError("AttcInit caller closure changed")
    init_raw = b"".join(struct.pack("<I", value) for value in init_calls)
    if sha(init_raw) != ATTC_INIT_CALLS_SHA:
        raise AuditError("AttcInit caller digest changed")

    provider_calls = {}
    for target, expected in PROVIDER_CALLS.items():
        sites = direct_calls(blob, decoder, target)
        if sites != expected:
            raise AuditError(f"provider caller closure changed for {target:#x}")
        raw = b"".join(struct.pack("<I", value) for value in sites)
        if sha(raw) != PROVIDER_CALL_SHA[target]:
            raise AuditError(f"provider caller digest changed for {target:#x}")
        provider_calls[f"0x{target:08x}"] = sites

    if sha(image_slice(blob, *WRITE_CALLER)) != WRITE_CALLER_SHA:
        raise AuditError("sole AttcWriteCmd caller body changed")
    caller_targets = {
        decoder._thumb_bl_target(blob, address)
        for address in range(WRITE_CALLER[0], WRITE_CALLER[1], 2)
    }
    if ATTC_WRITE_CMD not in caller_targets or DM_CONN_SEC_LEVEL in caller_targets:
        raise AuditError("AttcWriteCmd caller no longer excludes signed-write wrapper")

    return {
        "schema_version": 1,
        "module": {
            "classification": "not_linked_or_dead_stripped",
            "linked_function_count": 0,
            "linked_function_bytes": 0,
            "source_inventory_functions": len(functions),
            "source_only_functions": functions,
            "retained_path_anchors": 0,
            "semantic_body_anchors": 0,
        },
        "exclusion": {
            "attc_control_block": ATTC_CB,
            "sign_interface_offset": 0x1B0,
            "sign_interface_address": ATTC_SIGN_SLOT,
            "attc_control_block_literal_cells": ATTC_CB_LITERAL_CELLS,
            "sign_interface_direct_literals": 0,
            "attc_init_calls": init_calls,
            "attc_init_clears_sign_interface": True,
            "later_sign_interface_installations": 0,
            "retained_name_or_path_markers": 0,
            "provider_direct_calls": provider_calls,
            "signed_write_wrapper_candidates": 0,
        },
        "lineage": {
            "selected_optional_source": "Packetcraft r20.05 through r20.05c and official AmbiqSuite R4.4.1 import",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "0595be9f0ae3f7b7f19c5d8d4fb0074eb6a0cf97",
            "selected_sha256": "0c13297d0724fbd2f2bd44ca6e86431423c14e0648d76116e2fe069b01f1f0b9",
            "stock_body_version_discriminated": False,
            "compatibility_basis": "neighboring stock ATT core is r20 EATT; this optional TU is absent",
            "historical_generating_commit_resolved": False,
            "license": "Apache-2.0",
        },
        "production": {"stock_bytes_replaced": 0, "source_owned_bytes_added": 0},
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
        print("Cordio attc_sign excluded: 0 linked / 7 source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
