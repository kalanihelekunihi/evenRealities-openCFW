#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio SMP SC initiator actions."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-smpi-sc-act-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-smpi-sc-act-provenance.tsv"
PINS = {
    MAP: "d29100a9e531a789db6b512e03e58be63139d54e3fb18105ade45ad565f7cfc5",
    PROVENANCE: "d177777b7fc28d8d73a8aa19afd135a654d2de6febfa40b28665f8eb43225494",
}

ACTION_TABLE = (0x6D1214, 0x6D12E0,
                "2f7d77ff2105f2a6153d40c15bff8ed0ee8197df738ea1547ff57a023185dd01")
EXPECTED_STORED_ENTRIES = [
    (0x6D1278, 0x5E347D), (0x6D127C, 0x5E3475),
    (0x6D1280, 0x5E348B), (0x6D1284, 0x5E34CB),
    (0x6D1288, 0x5E3509), (0x6D128C, 0x5E352B),
    (0x6D12A0, 0x5E3561), (0x6D12A4, 0x5E35E7),
    (0x6D12A8, 0x5E3623), (0x6D12AC, 0x5E363F),
    (0x6D12B0, 0x5E366B), (0x6D12B4, 0x5E36CD),
    (0x6D12B8, 0x5E3735), (0x6D12BC, 0x5E3791),
    (0x6D12D8, 0x5E37B3), (0x6D12DC, 0x5E37E5),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("smpi_sc_act_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows() -> list[tuple[str, int, int, str]]:
    rows = []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] != "linked":
                raise RuntimeError("unexpected source-only SC initiator action")
            rows.append((row["function"], int(row["stock_start"], 0),
                         int(row["stock_end_exclusive"], 0), row["stock_sha256"]))
    return rows


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise RuntimeError(f"pinned input changed: {path}")

    rows = load_rows()
    if len(rows) != 16:
        raise RuntimeError("source inventory changed")
    bodies = []
    for name, start, end, digest in rows:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != digest:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "ca0b592a6ba9df5a6ed2065dab1a88ff428d0383c5563f13ab4453d816fcd1ac":
        raise RuntimeError("body concatenation changed")
    if sha(image_slice(blob, 0x5E3474, 0x5E38C8)) != "00ae4d04166a1c435a3447b11bff93001fba191080f6468062aab4e3e064aace":
        raise RuntimeError("physical object changed")
    tail = image_slice(blob, 0x5E38A2, 0x5E38C8)
    if sha(tail) != "574667b863570d2d3aa362f1834ccfd7203dabcea661586853dc5a1ed0cd60ae":
        raise RuntimeError("owned tail changed")
    if tail[:10] != b"\0\0Cai\0Cbi\0":
        raise RuntimeError("SC initiator tail labels changed")
    if list(struct.unpack("<7I", tail[10:])) != [
        0x78E734, 0x7856B0, 0x78E73C, 0x78C1D0,
        0x7891A0, 0x78C1DC, 0x200004B8,
    ]:
        raise RuntimeError("SC initiator literal pool changed")
    if image_slice(blob, 0x5E383E, 0x5E3844) != bytes.fromhex("012084f84400"):
        raise RuntimeError("r20 SC initiator keyReady assignment changed")

    decoder = load_decoder()
    starts = {start: name for name, start, _, _ in rows}
    calls = {name: [] for name, _, _, _ in rows}
    outbound = []
    interiors = set()
    for _, start, end, _ in rows:
        interiors.update(range(start + 2, end, 2))
        for address in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                outbound.append((address, target))
    interior_branches = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
        elif target in interiors:
            interior_branches.append((address, target))
    if any(calls.values()):
        raise RuntimeError("unexpected direct SC initiator entry call")
    if interior_branches:
        raise RuntimeError("direct branch to SC initiator body interior found")
    if len(outbound) != 56:
        raise RuntimeError("SC initiator outbound-call closure changed")

    start, end, digest = ACTION_TABLE
    if sha(image_slice(blob, start, end)) != digest:
        raise RuntimeError("initiator SC action table changed")
    stored_entries = []
    stored_interiors = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != EXPECTED_STORED_ENTRIES:
        raise RuntimeError("stored SC initiator entry-pointer closure changed")
    if stored_interiors:
        raise RuntimeError("stored SC initiator strict-interior pointer found")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x5E3474,
            "end_exclusive": 0x5E38C8,
            "physical_bytes": 1108,
            "linked_function_count": 16,
            "linked_function_bytes": 1070,
            "owned_noncode_bytes": 38,
            "source_inventory_functions": 16,
            "source_only_functions": [],
            "direct_bl_ingress_sites": 0,
            "registered_function_pointers": 16,
            "strict_interior_pointers": 0,
            "decoded_outbound_bl_sites": 56,
        },
        "architecture": {
            "retained_source_path": None,
            "smp_config_pointer": 0x200004B8,
            "calc128_zeros": 0x7856B0,
            "ccb_key_ready_offset": 0x44,
            "secure_connections_action_roots": 16,
            "next_unit_entry": 0x5E38C8,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "38ed4197099e84e5dd17dac4a05385e42fe556fb",
            "selected_sha256": "195b7619013e746462ee1cb2cb4db7ccce3f68a1fe7dd15d0d05e1ca2567c952",
            "official_later_oracle": "AmbiqSuite R4.4.1 import at 4264b930",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "discriminator": "stock DH-key-check verify writes smpCcb.keyReady at +0x44; r19/AmbiqSuite 2.x omits it",
            "historical_generating_commit_resolved": False,
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
        print("Cordio smpi_sc_act closed: 16/16 linked; 16 table roots; r20 keyReady path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
