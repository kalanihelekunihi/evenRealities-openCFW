#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio slave-security wrappers."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = str(ROOT / "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
from cordio_dm_sec_roles_production import audit as audit_production
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
ARCHIVE = ROOT / "research/readiness/dm-sec-slave/SHA256SUMS"
ARCHIVE_BYTES = 1_208
ARCHIVE_SHA256 = "f0dec4046d8162237f86202dd5a57fb51c1f87fd301c643c24a5f466f7dd9e1f"

PINS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-sec-slave-function-map.tsv": "0864a2c7bb70b10811f75e0ec0eeca9b36f05e89fb165c74f566bb9ac6ef3ba7",
    ROOT / "tools/manifests/packetcraft-cordio-dm-sec-slave-provenance.tsv": "589ac42fc4cd110ac1b51af9a983c290a1935fa14f80af02ade8c87375d339ca",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-slave-build-results.tsv": "7386ec161a93784b15e8cf7644c23142e3fdf6702399b7658979cc4f74a11a52",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-slave-closure-results.tsv": "f11542a6c14cb5e85ed6938e4c9ffcfbb99fd983dbd1d09ed952c4dda5342759",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-slave-include-closure.tsv": "0be9b47f2758d93074a723f43c453e369295ead1efde9fd157bf5e594d6f7077",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-slave-source-identities.tsv": "8cb6767b44d1071dd38074aa0565f7161defb36664e67a6dd52511d2369dc5e6",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-slave-undefined-providers.tsv": "560055bf9f0b3505722727bf75fbe40abd2859d3f82bf447693035f50e23453b",
}

FUNCTIONS = {
    "DmSecPairRsp": (0x52BACC, 0x52BB00, "51d88a9a4c1f5cbefe18ac0aa4d38e370e5d1b0c82bb283fcf930f7b09f1a994"),
    "DmSecSlaveReq": (0x52BB00, 0x52BB20, "03f00894b62705485ce6b488c58600f9dea84754fa336768c44c64d77e3b28e3"),
    "DmSecLtkRsp": (0x52BB20, 0x52BB60, "72922857d5608ffb10cf738c0051c2272e950fed5c65948109bd40a571e47fe4"),
}
CALLERS = {
    "DmSecPairRsp": [0x4B3A7E],
    "DmSecSlaveReq": [0x4B38EA, 0x4B39D8, 0x4B469E],
    "DmSecLtkRsp": [0x4B36E4, 0x4B36F6],
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(image: bytes, start: int, end: int) -> bytes:
    return image[start - LOAD_BASE : end - LOAD_BASE]


def _decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_sec_slave_thumb", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze(image_path: Path = IMAGE) -> dict[str, Any]:
    image = image_path.read_bytes()
    if len(image) != IMAGE_BYTES or _sha(image) != IMAGE_SHA256:
        raise RuntimeError("official image changed")
    if ARCHIVE.stat().st_size != ARCHIVE_BYTES or _sha(ARCHIVE.read_bytes()) != ARCHIVE_SHA256:
        raise RuntimeError("dm_sec_slave readiness artifact changed")
    for path, expected in PINS.items():
        if _sha(path.read_bytes()) != expected:
            raise RuntimeError(f"pinned input changed: {path}")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        body = _slice(image, start, end)
        if _sha(body) != expected:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if _sha(b"".join(bodies)) != "04cd77517a8fca33270b8df5fe1b7ea1d07738396bc4283e974f7ed1f35789ac":
        raise RuntimeError("body concatenation changed")
    if _sha(_slice(image, 0x52BACC, 0x52BB64)) != "5156521de0630c8921394b506f309e416ed9c7a4d9adb6b0d7b0293943a52722":
        raise RuntimeError("physical dm_sec_slave interval changed")
    tail = _slice(image, 0x52BB60, 0x52BB64)
    if _sha(tail) != "6aef07c089b4125e912a04d0b4a227025fcb0d4b38ee20dee0c1bcec270a7cea" or struct.unpack("<I", tail)[0] != 0x20073B78:
        raise RuntimeError("dm_sec_slave literal tail changed")

    decoder = _decoder()
    starts = {start: name for name, (start, _, _) in FUNCTIONS.items()}
    calls = {name: [] for name in FUNCTIONS}
    for address in range(LOAD_BASE, LOAD_BASE + len(image) - 3, 2):
        target = decoder._thumb_bl_target(image, address)
        if target in starts:
            calls[starts[target]].append(address)
    if calls != CALLERS:
        raise RuntimeError("direct caller closure changed")

    entries = set(starts)
    interiors: set[int] = set()
    for start, end, _ in FUNCTIONS.values():
        interiors.update(range(start + 2, end, 2))
    entry_pointers = []
    interior_pointers = []
    for offset in range(0, len(image) - 3):
        value = struct.unpack_from("<I", image, offset)[0]
        target = value & ~1
        if target in entries:
            entry_pointers.append((LOAD_BASE + offset, value))
        elif target in interiors:
            interior_pointers.append((LOAD_BASE + offset, value))
    if entry_pointers or interior_pointers:
        raise RuntimeError("stored entry/interior ingress changed")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x52BACC,
            "end_exclusive": 0x52BB64,
            "physical_bytes": 152,
            "linked_function_count": 3,
            "linked_function_bytes": 148,
            "source_inventory_functions": 3,
            "source_only_functions": [],
            "direct_bl_ingress_sites": 6,
            "registered_function_pointers": 0,
            "strict_interior_pointers": 0,
        },
        "architecture": {
            "ltk_response_event": 0x29,
            "message_id_shift": 3,
            "key_distribution_mask": 0x07,
        },
        "abi": {"dm_cb": 0x20073B78, "ltk_response_bytes": 0x16},
        "lineage": {
            "selected_blob": "bb8dd0d6fcf2eb0861f9f4b308498ee3b1a89c49",
            "selected_sha256": "7bbf923ff434d8ae73fad83b566c5359178079e046c99e9bb9909806f7bceb81",
            "license": "Apache-2.0",
            "historical_generating_commit_resolved": False,
        },
        "readiness": {
            "archive_sha256": ARCHIVE_SHA256,
            "source_functions_built": 3,
            "provider_seams": 5,
            "valid_non_vacuous_closure_profiles": 2,
            "linked_unresolved_symbols": 0,
        },
        "production": audit_production("slave"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else "Cordio dm_sec_slave closed: 3 linked / 0 source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
