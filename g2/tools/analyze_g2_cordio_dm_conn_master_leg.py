#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio legacy-master connection unit."""
from __future__ import annotations

import argparse
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
PINS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-master-leg-function-map.tsv": "201ba73eade03e81f4285f7a2d83431733c9fa5c7e553b92bf39273e41f36d12",
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-master-leg-provenance.tsv": "308f133caf339064a57fa3977a28159fc814340a1d99005b0def5f91d541d044",
}
FUNCTIONS = {
    "dmConnOpen": (0x536A28, 0x536A86, "9975e28872778dd43bb7342475ee4e4001c39c8971eba92782be2fc3ae62652f"),
    "dmConnSmActOpen": (0x536A86, 0x536A98, "0077a67b79a2766d4853a171429aa024dfaaf0c8e36fc08f3a334dd202214e5a"),
    "DmConnMasterInit": (0x536A98, 0x536AB0, "cb3ef0ea7d184dac46ed70aba73c6f212e1308cdee48c567827704f518a9935b"),
}
CALLERS = {
    "dmConnOpen": [0x536A92],
    "dmConnSmActOpen": [],
    "DmConnMasterInit": [0x4B801E],
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sl(image: bytes, start: int, end: int) -> bytes:
    return image[start - BASE : end - BASE]


def decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_conn_master_leg_thumb", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze(image_path: Path = IMAGE) -> dict:
    image = image_path.read_bytes()
    if len(image) != IMAGE_BYTES or sha(image) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, expected in PINS.items():
        if sha(path.read_bytes()) != expected:
            raise RuntimeError(f"pinned input changed: {path}")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        body = sl(image, start, end)
        if sha(body) != expected:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "d56996db7796f420899a184c131c11eb461464e1d0de0c1075570afc6350b5ec":
        raise RuntimeError("body concatenation changed")
    if sha(sl(image, 0x536A28, 0x536AC8)) != "b68a143267080514feaba249003d8cfd14b41a1c7714ceda7d274ce1cf4ccc30":
        raise RuntimeError("physical interval changed")

    tail = sl(image, 0x536AB0, 0x536AC8)
    expected_tail = [0x20073B78, 0x200712A4, 0x0078D424, 0x20073FE4, 0x0078D41C, 0x20073FD8]
    if sha(tail) != "abfc26714075e468a60f182516a0834d147dbbe9cc488c44eadb51c9066ce04b" or list(struct.unpack("<6I", tail)) != expected_tail:
        raise RuntimeError("literal tail changed")
    main_table = sl(image, 0x78D424, 0x78D42C)
    update_table = sl(image, 0x78D41C, 0x78D424)
    if list(struct.unpack("<2I", main_table)) != [0x536A87, 0x55BC5D]:
        raise RuntimeError("master action table changed")
    if list(struct.unpack("<2I", update_table)) != [0x55BC71, 0x55BC7D]:
        raise RuntimeError("master update table changed")

    thumb = decoder()
    starts = {start: name for name, (start, _, _) in FUNCTIONS.items()}
    calls = {name: [] for name in FUNCTIONS}
    for address in range(BASE, BASE + len(image) - 3, 2):
        target = thumb._thumb_bl_target(image, address)
        if target in starts:
            calls[starts[target]].append(address)
    if calls != CALLERS:
        raise RuntimeError("direct caller closure changed")

    interiors = set()
    for start, end, _ in FUNCTIONS.values():
        interiors.update(range(start + 2, end, 2))
    entries = []
    inside = []
    for offset in range(len(image) - 3):
        value = struct.unpack_from("<I", image, offset)[0]
        target = value & ~1
        if target in starts:
            entries.append((BASE + offset, value))
        elif target in interiors:
            inside.append((BASE + offset, value))
    if entries != [(0x78D424, 0x536A87)] or inside:
        raise RuntimeError("stored/interior ingress changed")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x536A28,
            "end_exclusive": 0x536AC8,
            "physical_bytes": 160,
            "linked_function_count": 3,
            "linked_function_bytes": 136,
            "source_inventory_functions": 3,
            "source_only_functions": [],
            "direct_bl_ingress_sites": 2,
            "registered_function_pointers": 1,
            "strict_interior_pointers": 0,
        },
        "architecture": {
            "main_action_entries": 2,
            "update_action_entries": 2,
            "separate_update_table": True,
            "task_locked_init": True,
            "init_phys": 2,
        },
        "lineage": {
            "selected_blob": "bdf160b21e58d3e2c34901b1829d81d4890d2b56",
            "selected_sha256": "a0ad6fdc783da5e96979b622ab05ecb2a46dc05b6a7eb2ede2740fc50a3fa656",
            "license": "Apache-2.0",
            "historical_generating_commit_resolved": False,
        },
        "build_readiness": {
            "status": "deferred",
            "reason": "local arm-none-eabi toolchain unavailable; binary/source closure is independent",
        },
        "production": {"stock_bytes_replaced": 0, "source_owned_bytes_added": 0},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else "Cordio dm_conn_master_leg closed: 3 linked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
