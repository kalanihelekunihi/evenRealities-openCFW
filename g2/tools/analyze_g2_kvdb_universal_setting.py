#!/usr/bin/env python3
"""Fail-closed audit of the G2 three-function universal-setting KVDB object."""

from __future__ import annotations

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
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-universal-setting-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-universal-setting-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-universal-setting-provenance.tsv"
PINS = {
    FUNCTION_MAP: "abf3b8e2eb8b1e016250a17f1a45a21be9b755362f0d7aff05f1257d6a8d44bf",
    CLOSURE: "227890e4667eb65a0aa0b4647b2e881316bc50548306917ea50998995e3c00df",
    PROVENANCE: "34764f7c0761ff933e63eb2eb7d9c370d73ca826690366dcdf1ae6670710b640",
}
PHYSICAL = (0x0049AD0C, 0x0049AE90)
PHYSICAL_SHA256 = "a8c3b7fe6bb4fa598fc9b206a8b4aea9f92a46c5684a2f906f2e81ed3f06be96"
BODY_SHA256 = "0c7b17a6828276160a44ec967144a55e1acf465153aded28414832c7df06eea6"
POOL = (0x0049AE60, 0x0049AE90)
POOL_SHA256 = "d01ff95edc07073d88c037556948b0f21c7080d6331bae5584551a20314f5901"
ENTRY_CALLS = [(0x00466092, 0x0049ADF0), (0x0049ADDE, 0x0049ADF0), (0x0049ADE6, 0x0049ADF0)]
ENTRY_SHA256 = "e3fcbbf5b9c8db6a7064f29e5b168eb92b17e041b14f0f559e744e8df753df9a"
BODY_CALLS = 22
BODY_CALL_SHA256 = "406a09fe0fcc8a138282f34216c890c198702d6cd7406baee3f153d07ce4f33b"
STORED = [(0x006D1E74, 0x0049AD0D), (0x00746D48, 0x0049AD21)]
STORED_SHA256 = "d3776b1ede1a7dbdaeacfb81ffcb6aa862670460c82762ac8138bfa0b05aa390"
WORDS = {
    0x0049AE60: 0x20003824,
    0x0049AE64: 0x00783424,
    0x0049AE68: 0x00788BB0,
    0x0049AE6C: 0x007713D4,
    0x0049AE70: 0x006DB998,
    0x0049AE74: 0x0077BAC4,
    0x0049AE78: 0x0074DFD4,
    0x0049AE7C: 0x00788BC0,
    0x0049AE80: 0x0074DFFC,
    0x0049AE84: 0x0074343C,
    0x0049AE88: 0x00765070,
    0x0049AE8C: 0x00705A68,
}
STRINGS = {
    0x00783424: "kvUniversalSetting",
    0x007713D4: "_kvdbUpdataUniversalSetting",
    0x006DB998: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_universal_setting.c",
    0x0077BAC4: "kvdb_universal_setting",
    0x00765070: "SVC_KvdbWriteUniversalSetting",
}
FACTORY = bytes.fromhex("030000000100000000000000ffffffffffff0000")


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sl(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def pairs(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def crc16(data: bytes) -> int:
    value = 0xFFFF
    for byte in data:
        value ^= byte << 8
        for _ in range(8):
            value = ((value << 1) ^ 0x1021) & 0xFFFF if value & 0x8000 else (value << 1) & 0xFFFF
    return value


def load(name: str, path: Path):
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def cstring(blob: bytes, address: int) -> str:
    offset = address - BASE
    end = blob.find(b"\0", offset)
    return blob[offset:end].decode("ascii")


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != 3_523_396 or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    starts: set[int] = set()
    interiors: set[int] = set()
    bodies = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = sl(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        bodies.append(raw)
    if len(rows) != 3 or sum(map(len, bodies)) != 340 or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function inventory changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256 or sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("physical object changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")

    decoder = load("kvdb_universal_setting_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
    entry = []
    interior_bl = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior_bl.append((site, target))
    if entry != ENTRY_CALLS or pairs(entry) != ENTRY_SHA256 or interior_bl:
        raise AuditError("entry/interior closure changed")

    calls = []
    for row in rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != BODY_CALLS or pairs(calls) != BODY_CALL_SHA256:
        raise AuditError("provider-call closure changed")

    stored = []
    for start in starts:
        needle = struct.pack("<I", start | 1)
        position = blob.find(needle)
        while position >= 0:
            stored.append((BASE + position, start | 1))
            position = blob.find(needle, position + 1)
    if sorted(stored) != STORED or pairs(sorted(stored)) != STORED_SHA256:
        raise AuditError("stored roots changed")
    encoded = interiors | {value | 1 for value in interiors}
    if any(struct.unpack_from("<I", blob, offset)[0] in encoded for offset in range(len(blob) - 3)):
        raise AuditError("strict-interior raw pointer appeared")

    flashdb = load("kvdb_universal_setting_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x20003824 - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 20] != FACTORY or crc16(FACTORY[:18]) != 0xA967:
        raise AuditError("factory record changed")
    return {
        "surface": {
            "linked_functions": 3,
            "body_bytes": 340,
            "physical_bytes": 388,
            "direct_bl_ingress_sites": 3,
            "direct_provider_calls": 22,
            "stored_entry_pointers": 2,
            "strict_interior_ingress": 0,
        },
        "record": {
            "address": "0x20003824",
            "bytes": 20,
            "crc_offset": 18,
            "boot_hex": FACTORY.hex(),
            "initialized_crc16": "0xA967",
            "key": "kvUniversalSetting",
        },
        "behavior": {
            "missing_rewrites_current": True,
            "pre_v3_crc_mismatch_rewrites_current": True,
            "v3_crc_mismatch_rewrites_current": False,
            "migration_imports_stored_record": False,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_universal_setting.c",
            "production_routed": False,
            "ownership_bytes": 0,
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
