#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio SMP Secure Connections utility."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-sc-main-function-map.tsv"
PINS = {
    MAP: "7203d6fceb3eda607229e862414d7843fe37ab563725829255bf98d7f1ac7bbc",
    ROOT / "tools/manifests/packetcraft-cordio-smp-sc-main-provenance.tsv": (
        "8908df5b21b0937fe1c70d318800c3fd889df3cf499880a32205fcc2fc284d38"
    ),
}
CALLS = {
    "SmpScAllocScratchBuffers": [0x5E2958],
    "SmpScFreeScratchBuffers": [0x5E2B38],
    "SmpScCmac": [
        0x56CF6C, 0x5E2D1A, 0x5E2EBC, 0x5E2F5A, 0x5E2FD8, 0x5E305C,
        0x5E30D2,
    ],
    "SmpScAlloc": [
        0x56CF3E, 0x5E2CC6, 0x5E2E92, 0x5E2F04, 0x5E2F82, 0x5E3002,
        0x5E3078,
    ],
    "SmpScCalcF4": [
        0x5E2C68, 0x5E2CB4, 0x5E35E0, 0x5E361C, 0x5E3706, 0x5E3F24,
        0x5E3F78, 0x5E4052,
    ],
    "SmpScInit": [0x537F1E, 0x53810E],
    "SmpScCat": [
        0x56CF54, 0x56CF5C, 0x5E2CE0, 0x5E2CEA, 0x5E2CF6, 0x5E2D00,
        0x5E2F1A, 0x5E2F98,
    ],
    "SmpScCat128": [
        0x5E2D0A, 0x5E2F22, 0x5E2F2C, 0x5E2FA0, 0x5E2FAA, 0x5E3012,
        0x5E301C, 0x5E3026, 0x5E308A, 0x5E3092, 0x5E309C,
    ],
    "smpScSendPubKey": [0x5E3484, 0x5E3DE0],
    "smpScSendDHKeyCheck": [0x5E37DE, 0x5E41BA],
    "smpScSendRand": [
        0x5E3502, 0x5E3664, 0x5E378A, 0x5E3E8C, 0x5E3FEA, 0x5E40E0,
        0x5E4116,
    ],
    "smpScSendPairCnf": [0x5E3638, 0x5E3E4E, 0x5E3F40],
    "smpGetPkBit": [0x5E35C6, 0x5E3600, 0x5E3F08, 0x5E3F5E],
    "SmpScGetCancelMsgWithReattempt": [0x53493C, 0x56D310, 0x5E2ECA],
    "smpScFailWithReattempt": [
        0x5E3550, 0x5E368E, 0x5E3760, 0x5E3FB2, 0x5E40AC,
    ],
    "smpEventStr": [0x56EEB2, 0x56EEFC, 0x56EF46, 0x56EF82, 0x56EFC4],
    "smpStateStr": [0x56EEAA, 0x56EEF4, 0x56EF3E, 0x56EF7A, 0x56EFBC],
    "smpLogByteArray": [
        0x5E2C2C, 0x5E2C3A, 0x5E2C4C, 0x5E2C78, 0x5E2C86, 0x5E2C98,
        0x5E2D38, 0x5E2E88, 0x5E2EFA, 0x5E2F6E, 0x5E2FEA, 0x5E306E,
        0x5E34A2, 0x5E34F0, 0x5E3538, 0x5E35C0, 0x5E362E, 0x5E3676,
        0x5E3748, 0x5E377E, 0x5E37BE, 0x5E3E06, 0x5E3E44, 0x5E3EFC,
        0x5E3F36, 0x5E3F8A, 0x5E3F9A, 0x5E4094, 0x5E40D0, 0x5E4152,
    ],
}
GAPS = [
    (
        0x56D2F8,
        0x56D304,
        "e63014acd8eb1f3ecd08c5ab96a4738bc4551662e2a4b7607ad1b4339e21f2be",
    ),
    (
        0x56D474,
        0x56D478,
        "dc81150db97a1851e655b42e04fc71865b2f3d1a70ff32ff48962214db47fe1a",
    ),
    (
        0x56D812,
        0x56D8C4,
        "826ca5bbd3d10b2bca1cbec271955a70cc8a9ff93b88f3bec0ccfbb368fd880c",
    ),
]
RAW_FALSE_WINDOWS = [(0x643377, 0x56D3FF), (0x64A903, 0x56CF00)]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("smp_sc_main_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows():
    linked = []
    source_only = []
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
    bodies = []
    for name, start, end, digest in linked:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != digest:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != (
        "faf9b25846805909a8f5766249a005ec4ecf5732f5521c1935059cd789b81656"
    ):
        raise RuntimeError("body concat changed")
    if sha(image_slice(blob, 0x56CDC0, 0x56D8C4)) != (
        "dfc0e2f6db94885e44328a855dcba1ee1fa1ca0fddca8aa1191f6820ddda2315"
    ):
        raise RuntimeError("physical object changed")

    for start, end, digest in GAPS:
        if sha(image_slice(blob, start, end)) != digest:
            raise RuntimeError(f"inline data changed at {start:#x}")
    if sha(image_slice(blob, 0x6DE8B4, 0x6DE914)) != (
        "90093e4723cadf127753f7af8ba375228da927153995381684c134f93a52ba9e"
    ):
        raise RuntimeError("retained path changed")
    if struct.unpack_from("<I", blob, 0x56D838 - BASE)[0] != 0x6DE8B4:
        raise RuntimeError("retained path pointer changed")

    decoder = load_decoder()
    starts = {start: name for name, start, _, _ in linked}
    calls = {name: [] for name, _, _, _ in linked}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
    if calls != CALLS:
        raise RuntimeError("direct ingress changed")

    interior = set()
    for _, start, end, _ in linked:
        interior.update(range(start + 2, end, 2))
    entry_values = []
    interior_values = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts:
            entry_values.append((BASE + offset, value))
        elif target in interior:
            interior_values.append((BASE + offset, value))
    if entry_values or interior_values != RAW_FALSE_WINDOWS:
        raise RuntimeError("stored/interior-value closure changed")

    smp_cb = struct.unpack_from("<I", blob, 0x56D81C - BASE)[0]
    sc_cb = struct.unpack_from("<I", blob, 0x56D820 - BASE)[0]
    if smp_cb != 0x20070AEC or sc_cb != 0x200728F4:
        raise RuntimeError("SMP control-block literals changed")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x56CDC0,
            "end_exclusive": 0x56D8C4,
            "physical_bytes": 2820,
            "linked_function_count": len(linked),
            "linked_function_bytes": sum(end - start for _, start, end, _ in linked),
            "source_inventory_functions": len(linked) + len(source_only),
            "source_only_functions": source_only,
            "direct_bl_ingress_sites": sum(map(len, CALLS.values())),
            "registered_function_pointers": 0,
            "strict_interior_pointers": 0,
            "accidental_unaligned_value_windows": len(RAW_FALSE_WINDOWS),
        },
        "architecture": {
            "retained_source_path": 0x6DE8B4,
            "smp_control_block": 0x20070AEC,
            "secure_connections_control_blocks": 0x200728F4,
            "connection_count": 3,
            "secure_connections_record_size": 0x1C,
            "cleanup_event": 0x1F,
            "next_unit_entry": 0x56D8C4,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "00515542371b1403f2716a02676064bf4aac2dcb",
            "selected_sha256": (
                "cc2e97537c11f7eb0df9b713100ad0165c34e1e39d6c5b6846d9772f14b01c33"
            ),
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "discriminator": "stock smpEventStr includes SMP_MSG_INT_CLEANUP",
        },
        "production": {
            "stock_bytes_replaced": 0,
            "source_owned_bytes_added": 0,
        },
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
        print("Cordio smp_sc_main closed: 18 linked, 4 source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
