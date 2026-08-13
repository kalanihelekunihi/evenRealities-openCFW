#!/usr/bin/env python3
"""Fail-closed audit of the G2 three-function time-format KVDB object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-time-format-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-time-format-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-time-format-provenance.tsv"
PINS = {
    FUNCTION_MAP: "af290d95f4c15687c6e88a7ffd8b97c504ab9df4c10f8ca22dff329838818c13",
    CLOSURE: "e96bacaa3647d1867b38d5c357f472bc86879959d10ff4e24225211a4b64953e",
    PROVENANCE: "3c28925018e63ca26d5e891b13edf59512aba01db2e8adf3a04d805075b44576",
}
PHYSICAL = (0x0049AE90, 0x0049B014)
PHYSICAL_SHA256 = "e75b4c89bfb846c04e656ec8def696f8565097e80319cfb4d9921e23282c32bd"
BODY_SHA256 = "b08b331f35aab05b6b15d5ec7b56b44b0c0db4e82d3e47889df6473ad650a7ea"
POOL = (0x0049AFE2, 0x0049B014)
POOL_SHA256 = "a570f5d14600d8a84a59231ee9f45168d18bd7f5b8846e379e5a67e5f2c9cf6d"
ENTRY_CALLS = [(0x004660F4, 0x0049AF74), (0x0049AF62, 0x0049AF74), (0x0049AF6A, 0x0049AF74)]
ENTRY_SHA256 = "629e20a1764fd8e44690610b69f2a3073cd509e057c4da2220ab31917e362804"
BODY_CALLS = 21
BODY_CALL_SHA256 = "e309f3bb68d65ee1def6a6eaaa75af16b10a7eca5fae827c549fe5dc86399cbe"
STORED = [(0x006D1E6C, 0x0049AE91), (0x00746D44, 0x0049AEA5)]
STORED_SHA256 = "96229db33a44dc25f50d3d9bdef70aa7d47f0fecad999298bd777dd756c5c75e"
WORDS = {
    0x0049AFE4: 0x20003818,
    0x0049AFE8: 0x00788B80,
    0x0049AFEC: 0x00788B90,
    0x0049AFF0: 0x0077BA64,
    0x0049AFF4: 0x006E1880,
    0x0049AFF8: 0x0078E5DC,
    0x0049AFFC: 0x0077BA7C,
    0x0049B000: 0x00788BA0,
    0x0049B004: 0x0077BA94,
    0x0049B008: 0x00759C18,
    0x0049B00C: 0x0077BAAC,
    0x0049B010: 0x00743410,
}
STRINGS = {
    0x00788B80: "kvTimeFormat",
    0x0077BA64: "_kvdbUpdataTimeFormat",
    0x006E1880: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_time_format.c",
    0x0078E5DC: "kv.tz",
    0x0077BAAC: "SVC_KvdbWriteTimeFormat",
}
FACTORY = bytes.fromhex("010000000000000000000000")


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
    if len(rows) != 3 or sum(map(len, bodies)) != 338 or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function inventory changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256 or sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("physical object changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")

    decoder = load("kvdb_time_format_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
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

    flashdb = load("kvdb_time_format_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x20003818 - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 12] != FACTORY or crc16(FACTORY[:8]) != 0x76ED:
        raise AuditError("factory record changed")
    return {
        "surface": {
            "linked_functions": 3,
            "body_bytes": 338,
            "physical_bytes": 388,
            "direct_bl_ingress_sites": 3,
            "direct_provider_calls": 21,
            "stored_entry_pointers": 2,
            "strict_interior_ingress": 0,
        },
        "record": {
            "address": "0x20003818",
            "bytes": 12,
            "crc_offset": 8,
            "boot_hex": FACTORY.hex(),
            "initialized_crc16": "0x76ED",
            "key": "kvTimeFormat",
        },
        "behavior": {
            "missing_rewrites_current": True,
            "v0_crc_mismatch_rewrites_current": True,
            "v1_crc_mismatch_rewrites_current": False,
            "migration_imports_stored_record": False,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_time_format.c",
            "production_routed": False,
            "ownership_bytes": 0,
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
