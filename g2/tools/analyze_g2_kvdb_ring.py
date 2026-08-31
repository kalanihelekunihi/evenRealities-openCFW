#!/usr/bin/env python3
"""Fail-closed audit of the G2 three-function ring KVDB object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-ring-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-ring-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-ring-provenance.tsv"
PINS = {
    FUNCTION_MAP: "e422e0eed3728dec1f62e77b12ed5aee27b8ccedc60027fffe5c570f480b0cdc",
    CLOSURE: "68f1fd585e656b6c4ab7d61e963c6680fe6f259d7adf0d8b14b26f44335f9ca2",
    PROVENANCE: "78461fcf8ba3ce747cf129caff04c2ae518d518bae979ec60489462b0fb520e2",
}
PHYSICAL = (0x005D9B6C, 0x005D9ED0)
PHYSICAL_SHA256 = "2b319f20a4542cc7e036eb7cb6264af5c571139de15657518826b13275f2c489"
BODY_SHA256 = "890a82e4756f95ebeb75bd253b5c2914b58fc7f30b125ea0589a1832153bb5ad"
POOL = (0x005D9E88, 0x005D9ED0)
POOL_SHA256 = "07247fcbdc0c0332c261c8661b6b2cfabe213472e8ef613a7b467e892b6ad990"
ENTRY_CALLS = [(0x005D9D2A, 0x005D9D40), (0x005D9D36, 0x005D9D40)]
ENTRY_SHA256 = "a42429415acd2b39f639efdb5cd0d3aa38cdce1730fb17e2e955cca4dc840ead"
BODY_CALLS = 45
BODY_CALL_SHA256 = "3b4a4d6b0239e40000cb8370a7770cef869d495dc82beebc955401a40630663b"
STORED = [(0x006D1E44, 0x005D9B6D), (0x00746D30, 0x005D9B83)]
STORED_SHA256 = "3358a01155136d77e711a27b4c3b975fb19f657d0064d7080ee6efd2f922091b"
WORDS = {
    0x005D9E88: 0x200037C8,
    0x005D9E8C: 0x0078E5A4,
    0x005D9E90: 0x00788AC0,
    0x005D9E94: 0x00788AB0,
    0x005D9E98: 0x006E9D90,
    0x005D9E9C: 0x0078E5AC,
    0x005D9EA0: 0x0077B974,
    0x005D9EA4: 0x00788AD0,
    0x005D9EA8: 0x0077B98C,
    0x005D9EAC: 0x00759B88,
    0x005D9EB0: 0x007433B8,
    0x005D9EB4: 0x0078E5B4,
    0x005D9EB8: 0x00783384,
    0x005D9EBC: 0x200037C9,
    0x005D9EC0: 0x200037CF,
    0x005D9EC4: 0x007833AC,
    0x005D9EC8: 0x00783398,
    0x005D9ECC: 0x00771364,
}
STRINGS = {
    0x0078E5A4: "kvRing",
    0x00788AB0: "_kvdbUpdataRing",
    0x006E9D90: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_ring.c",
    0x0078E5AC: "kv.ring",
    0x00759B88: "mac %02X:%02X:%02X:%02X:%02X:%02X",
    0x0078E5B4: "name %s",
    0x007833AC: "record_check 0x%x",
    0x00783398: "SVC_KvdbWriteRing",
}
FACTORY = bytes.fromhex("01ffffffffffff4556454e2052315f464646464646000000")


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


def thumb_bw_target(blob: bytes, address: int) -> int | None:
    offset = address - BASE
    first, second = struct.unpack_from("<HH", blob, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


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
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = sl(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        bodies.append(raw)
    if len(rows) != 3 or sum(map(len, bodies)) != 796 or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function inventory changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256 or sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("physical object changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")

    decoder = load("kvdb_ring_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
    entry = []
    interior_bl = []
    entry_bw = []
    interior_bw = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior_bl.append((site, target))
        target = thumb_bw_target(blob, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    if entry != ENTRY_CALLS or pairs(entry) != ENTRY_SHA256 or interior_bl:
        raise AuditError("BL entry/interior closure changed")
    if entry_bw or interior_bw:
        raise AuditError("B.W entry/interior closure changed")

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
        for encoded in (start, start | 1):
            needle = struct.pack("<I", encoded)
            position = blob.find(needle)
            while position >= 0:
                stored.append((BASE + position, encoded))
                position = blob.find(needle, position + 1)
    if sorted(stored) != STORED or pairs(sorted(stored)) != STORED_SHA256:
        raise AuditError("stored roots changed")
    encoded = interiors | {value | 1 for value in interiors}
    if any(struct.unpack_from("<I", blob, offset)[0] in encoded for offset in range(len(blob) - 3)):
        raise AuditError("strict-interior raw pointer appeared")

    flashdb = load("kvdb_ring_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x200037C8 - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 24] != FACTORY or crc16(FACTORY[:22]) != 0x06D4:
        raise AuditError("factory record changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/kvdb_ring.c"
    expected_patches = {
        "replace_kvdb_ring_default_initialize": (
            0x005D9B6C, 22, "ef35718875dd86b68dcb6ce403d801def07fb263ebce8e276f899e0aaf34c36d",
            "open_cfw_kvdb_ring_default_initialize",
        ),
        "replace_kvdb_ring_load_and_migrate": (
            0x005D9B82, 446, "8820609ec9c69ccca51e740e6c6e90c1482bb29b3d7688b13508a787a368dd9a",
            "open_cfw_kvdb_ring_load_and_migrate",
        ),
        "replace_kvdb_write_ring": (
            0x005D9D40, 328, "009e81ba8b01aef6489577a8241a55330e68791f2a6c8d6edea9c2223781f6f4",
            "open_cfw_kvdb_write_ring",
        ),
    }
    patches = {
        row["name"]: row
        for row in overlay["patch_sites"]
        if row.get("name") in expected_patches
    }
    leaves = {
        row["function"]: row
        for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == candidate
    }
    if (
        set(patches) != set(expected_patches)
        or any(
            patches[name]["runtime_address"] != address
            or patches[name]["expected_size"] != size
            or patches[name]["expected_sha256"] != digest
            or patches[name]["branch"] != "b_w"
            or patches[name]["target_function"] != target
            or patches[name].get("profiles") != ["apple-clang"]
            for name, (address, size, digest, target) in expected_patches.items()
        )
        or set(leaves) != {target for *_, target in expected_patches.values()}
        or any(
            leaf["source"]["sha256"]
            != "470ce433f52d117d76638f7ca39c257429cbb1bb4e52a12f1421de986ba84269"
            or leaf.get("profiles") != ["apple-clang"]
            for leaf in leaves.values()
        )
    ):
        raise AuditError("production ring routing changed")
    return {
        "surface": {
            "linked_functions": 3,
            "body_bytes": 796,
            "physical_bytes": 868,
            "direct_bl_ingress_sites": 2,
            "direct_provider_calls": 45,
            "stored_entry_pointers": 2,
            "strict_interior_ingress": 0,
        },
        "record": {
            "address": "0x200037C8",
            "bytes": 24,
            "mac_offset": 1,
            "name_offset": 7,
            "name_bytes": 14,
            "reserved_offset": 21,
            "crc_offset": 22,
            "boot_hex": FACTORY.hex(),
            "initialized_crc16": "0x06D4",
            "rewritten_factory_crc16": "0xA1BE",
            "key": "kvRing",
        },
        "behavior": {
            "missing_rewrites_current": True,
            "v0_crc_mismatch_rewrites_current": True,
            "v1_crc_mismatch_rewrites_current": False,
            "migration_imports_stored_record": False,
            "nonnull_name_forces_byte_20_zero": True,
            "null_name_fills_all_14_bytes_ff": True,
            "writer_preserves_reserved_byte": True,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_ring.c",
            "production_routed": True,
            "ownership_bytes": 796,
            "retained_stock_noncode_bytes": 72,
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
