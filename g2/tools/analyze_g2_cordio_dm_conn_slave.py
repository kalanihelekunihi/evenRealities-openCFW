#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio slave connection unit."""
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
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-slave-function-map.tsv": "7c4b78bbe289b5f1dbc3340b72deb1280fa1d2599baa680798ce9f3c4af02825",
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-slave-provenance.tsv": "0867db5f49e1a0bc606d2e355ff34458b0a9d070f73a12caa702fac2b81ba465",
}
FUNCTIONS = {
    "dmConnUpdateCback": (0x56E4F8, 0x56E526, "bbefb6269cfe50e109e67128887afce8f64cee9f0f34c0c2c74105d17ec7c6f5"),
    "dmConnUpdActUpdateSlave": (0x56E526, 0x56E564, "48c98f0dd227f3a52cdb1d929992b13f7b9377aaffa21fcd1afe9b6b46284aad"),
    "dmConnUpdActL2cUpdateCnf": (0x56E564, 0x56E580, "efd59c8c2b769d9c8ed00bbfd2169ab03adf4fef9a53c80ea97395c82c73978b"),
    "DmL2cConnUpdateCnf": (0x56E580, 0x56E5A4, "05cdb79f244178b693ca42e4c71d4c84889c4a536ec38461ad745f23a15359a2"),
    "DmL2cCmdRejInd": (0x56E5A4, 0x56E5C6, "41de48e3802fa5de0d9a98452d10ec005a97fd407ca35c5104c6ecef8ad2060a"),
}
CALLERS = {
    "dmConnUpdateCback": [0x56E55E, 0x56E57A],
    "dmConnUpdActUpdateSlave": [],
    "dmConnUpdActL2cUpdateCnf": [],
    "DmL2cConnUpdateCnf": [0x536C4C, 0x536D14],
    "DmL2cCmdRejInd": [0x536D22],
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
    spec = importlib.util.spec_from_file_location("dm_conn_slave_thumb", path)
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
    if sha(b"".join(bodies)) != "8391722feea37207e7d5010fc21f238777a153d0b78aa780404903e8c0fd4d3e":
        raise RuntimeError("body concatenation changed")
    if sha(sl(image, 0x56E4F8, 0x56E5CC)) != "69b64b7e5f7a5a2e6cb6666a88a25d06373a5c1f778086526836307bd7858f45":
        raise RuntimeError("physical interval changed")

    tail = sl(image, 0x56E5C6, 0x56E5CC)
    if sha(tail) != "b80cfed4b0e18a3a8b7f8878f098736983800213b50952d4dc6f8c07728eadf6" or tail[:2] != b"\0\0" or struct.unpack("<I", tail[2:])[0] != 0x200712A4:
        raise RuntimeError("literal tail changed")
    update_table = sl(image, 0x78D42C, 0x78D434)
    if sha(update_table) != "0de23740d07fc7a7016ee4f748097a49f130a151ea140b24d628accbbbb790b1" or list(struct.unpack("<2I", update_table)) != [0x56E527, 0x56E565]:
        raise RuntimeError("slave update table changed")

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
    if entries != [(0x78D42C, 0x56E527), (0x78D430, 0x56E565)]:
        raise RuntimeError("stored entry closure changed")
    # This odd-address byte window is packed unrelated data, not an aligned pointer.
    if inside != [(0x643397, 0x56E500)]:
        raise RuntimeError("interior byte-window closure changed")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x56E4F8,
            "end_exclusive": 0x56E5CC,
            "physical_bytes": 212,
            "linked_function_count": 5,
            "linked_function_bytes": 206,
            "source_inventory_functions": 6,
            "source_only_functions": ["DmConnAccept"],
            "direct_bl_ingress_sites": 5,
            "registered_function_pointers": 2,
            "strict_interior_pointers": 0,
            "unaligned_false_pointer_windows": 1,
        },
        "architecture": {
            "update_action_entries": 2,
            "separate_update_component": True,
            "l2c_update_confirm_event": 0x73,
            "update_executor": "dmConnUpdExecute",
        },
        "lineage": {
            "selected_blob": "9422ae8e45e12c3ea26aa6dbdc5730ed40e74cdd",
            "selected_sha256": "4fc01fd9a83d370f3899d75c0bda7ce7473067cde17efe41b5e6b87b4c15847e",
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
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else "Cordio dm_conn_slave closed: 5 linked, 1 source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
