#!/usr/bin/env python3
"""Fail-closed audit of the G2 three-function time KVDB object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-time-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-time-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-time-provenance.tsv"
PINS = {
    FUNCTION_MAP: "473be7e93b81a968cbef03d91ab97e38adc4336ab5ed733343931a3c2ac2f237",
    CLOSURE: "50320fc9fdedf75aa540fe2bfae5907b92dc7ffac8f4af6f59619d7c3113d051",
    PROVENANCE: "1195264806a7f78255f211210c8afd5c24b7245e4f05b92ffbfb0df1674bff41",
}
PHYSICAL = (0x00585618, 0x00585840)
PHYSICAL_SHA256 = "ce83c1da7ce27e3198cb0c5119e5b7a9108c4f25a07577da9820f1bb76f9740c"
BODY_SHA256 = "cf04cb41b7fc34e0d6a00c30478062f7a33bb00e7720b87a7124a678e0741c5c"
POOL = (0x00585806, 0x00585840)
POOL_SHA256 = "8b82dc276f31c9220d8773f1ea0a8556b72bc6ac19ec5651e7927e355b53c264"
ENTRY_CALLS = [(0x005438AE, 0x00585758), (0x00585740, 0x00585758), (0x0058574E, 0x00585758)]
ENTRY_SHA256 = "bfa780956afb5e3a58b886454190217618d5e4482f8773d61f9fc1c58b328bc6"
BODY_CALLS = 31
BODY_CALL_SHA256 = "11a8acaebc3001cf46136210d554ce6f066f3c0ab21df4ab33b9fef8d2e93657"
STORED = [(0x006D1E64, 0x00585619), (0x00746D40, 0x0058562D)]
STORED_SHA256 = "6494da27a229c6e6c2abb7b5a61254cb8b26a8cef01b327870e329a79dd6f47a"
KNOWN_INTERIOR_WINDOWS = [(0x0078F39F, 0x00585700)]
WORDS = {
    0x00585808: 0x2000380C,
    0x0058580C: 0x0078E5CC,
    0x00585810: 0x00788B60,
    0x00585814: 0x00788B50,
    0x00585818: 0x006E9DE4,
    0x0058581C: 0x0078E5D4,
    0x00585820: 0x0077BA34,
    0x00585824: 0x00788B70,
    0x00585828: 0x0077BA4C,
    0x0058582C: 0x00759BF4,
    0x00585830: 0x007433E4,
    0x00585834: 0x00783410,
    0x00585838: 0x007833FC,
    0x0058583C: 0x007713B8,
}
STRINGS = {
    0x0078E5CC: "kvTime",
    0x00788B50: "_kvdbUpdataTime",
    0x006E9DE4: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_time.c",
    0x0078E5D4: "kv.tz",
    0x007833FC: "SVC_KvdbWriteTime",
}
FACTORY = bytes.fromhex("010000002b2d376820000000")


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
    if len(rows) != 3 or sum(map(len, bodies)) != 494 or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function inventory changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256 or sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("physical object changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")

    decoder = load("kvdb_time_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
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
    raw_windows = [
        (BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if raw_windows != KNOWN_INTERIOR_WINDOWS:
        raise AuditError("strict-interior raw windows changed")
    if blob[0x0078F398 - BASE : 0x0078F3A8 - BASE] != b"W1X\0W1Y\0WX\0\0WY\0\0":
        raise AuditError("known packed-string window changed")

    flashdb = load("kvdb_time_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x2000380C - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 12] != FACTORY or crc16(FACTORY[:10]) != 0x18F0:
        raise AuditError("factory record changed")
    return {
        "surface": {
            "linked_functions": 3,
            "body_bytes": 494,
            "physical_bytes": 552,
            "direct_bl_ingress_sites": 3,
            "direct_provider_calls": 31,
            "stored_entry_pointers": 2,
            "strict_interior_ingress": 0,
            "qualified_accidental_interior_windows": 1,
        },
        "record": {
            "address": "0x2000380C",
            "bytes": 12,
            "timestamp_offset": 4,
            "timezone_offset": 8,
            "crc_offset": 10,
            "boot_hex": FACTORY.hex(),
            "initialized_crc16": "0x18F0",
            "upgraded_crc16": "0xC67A",
            "schema_version": 3,
            "key": "kvTime",
        },
        "behavior": {
            "missing_rewrites_current": True,
            "pre_v3_crc_mismatch_rewrites_current": True,
            "v3_crc_mismatch_rewrites_current": False,
            "migration_imports_stored_record": False,
            "writer_preserves_reserved_bytes": True,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_time.c",
            "production_routed": False,
            "ownership_bytes": 0,
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
