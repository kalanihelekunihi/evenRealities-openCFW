#!/usr/bin/env python3
"""Fail-closed audit of the G2 three-function terminal-mode KVDB object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-terminal-mode-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-terminal-mode-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-terminal-mode-provenance.tsv"
PINS = {
    FUNCTION_MAP: "b7c178f626bb2a6a4826d93edcbbee2a531fff7db72667e9055488e6e2903a96",
    CLOSURE: "c758c8afb819ae226620a0bd3edc697dafc1b0345015ae4c1ccc43c8b3e84180",
    PROVENANCE: "355682e4a06631516f3dfdc4ea7d813ec67cb1eda000beeae589fe0acc779680",
}
PHYSICAL = (0x004B03E0, 0x004B0560)
PHYSICAL_SHA256 = "65d3de37ac6d66eeb7bba08453e6fd602d49e0f3331cc5cdc1c53906124b6461"
BODY_SHA256 = "72b928ec066496784ff1b8ffa5c9bf14b44a32ca4972f351c7fe3338d866feba"
POOL = (0x004B052E, 0x004B0560)
POOL_SHA256 = "b55bd7cc9e3b5ad212f7c7071efbc607dc7ec83ecca5268b81e2b15939376abf"
ENTRY_CALLS = [(0x0046C646, 0x004B04C4), (0x004B04B2, 0x004B04C4), (0x004B04BA, 0x004B04C4)]
ENTRY_SHA256 = "101f11a43355d800031e2c6482da62c68db147ff1629ad350c0293150147cd7d"
BODY_CALLS = 21
BODY_CALL_SHA256 = "7f598a1e7719fb80d0d34c96fc6cc5a178403a34d64fb7164f2a61b509480c3f"
STORED = [(0x006D1E5C, 0x004B03E1), (0x00746D3C, 0x004B03F5)]
STORED_SHA256 = "43d7e279cb98ece90065f622b57d54a4d2112ee89879bd87b83ef242385742da"
WORDS = {
    0x004B0530: 0x20003808,
    0x004B0534: 0x00788B20,
    0x004B0538: 0x00788B30,
    0x004B053C: 0x0077BA1C,
    0x004B0540: 0x006DE794,
    0x004B0544: 0x007833E8,
    0x004B0548: 0x00759BAC,
    0x004B054C: 0x00788B40,
    0x004B0550: 0x00759BD0,
    0x004B0554: 0x0074DFAC,
    0x004B0558: 0x0077139C,
    0x004B055C: 0x00722D28,
}
STRINGS = {
    0x00788B20: "kvTerminalMode",
    0x0077BA1C: "_kvdbUpdataTerminalMode",
    0x006DE794: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_terminal_mode.c",
    0x007833E8: "kv.terminal_mode",
    0x0077139C: "SVC_KvdbWriteTerminalMode",
}
FACTORY = bytes.fromhex("01000000")


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
    if len(rows) != 3 or sum(map(len, bodies)) != 334 or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function inventory changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256 or sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("physical object changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")

    decoder = load("kvdb_terminal_mode_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
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

    flashdb = load("kvdb_terminal_mode_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x20003808 - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 4] != FACTORY or crc16(FACTORY[:2]) != 0x2E3E:
        raise AuditError("factory record changed")
    return {
        "surface": {
            "linked_functions": 3,
            "body_bytes": 334,
            "physical_bytes": 384,
            "direct_bl_ingress_sites": 3,
            "direct_provider_calls": 21,
            "stored_entry_pointers": 2,
            "strict_interior_ingress": 0,
        },
        "record": {
            "address": "0x20003808",
            "bytes": 4,
            "mode_offset": 1,
            "crc_offset": 2,
            "boot_hex": FACTORY.hex(),
            "initialized_crc16": "0x2E3E",
            "schema_version": 1,
            "key": "kvTerminalMode",
        },
        "behavior": {
            "missing_rewrites_current": True,
            "v0_crc_mismatch_rewrites_current": True,
            "v1_crc_mismatch_rewrites_current": False,
            "migration_imports_stored_record": False,
            "writer_forces_version": 1,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_terminal_mode.c",
            "production_routed": False,
            "ownership_bytes": 0,
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
