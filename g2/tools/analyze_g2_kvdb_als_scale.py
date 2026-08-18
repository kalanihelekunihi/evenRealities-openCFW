#!/usr/bin/env python3
"""Fail-closed audit of the G2 three-function ALS-scale KVDB object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-als-scale-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-als-scale-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-als-scale-provenance.tsv"
PINS = {
    FUNCTION_MAP: "4719f276bdd303c4b6629356297ad71fd770be041fc31622ba7b08d97e4d2417",
    CLOSURE: "1290538865f3c11cda17511a3702e66bd113feb1f3374e7e918bef650fe1bd6f",
    PROVENANCE: "778770aab0dbd235e0e475498d9f98b0571b0663adb7cbf033f2c54b8566838a",
}
PHYSICAL = (0x004AECA4, 0x004AEE28)
PHYSICAL_SHA256 = "441f205adb26893cd98b4edcc5802512ee42f427740f113bd037c07068a98800"
BODY_SHA256 = "a215781fb9f1596bd1bd35cf3602e02575418a1d62fd62649ccbfaee6dc806f7"
POOL = (0x004AEDF6, 0x004AEE28)
POOL_SHA256 = "993a796bad367c61812f298987719535ffab680d11fc1bdfe88d66cdc2a2b41e"
ENTRY_CALLS = [(0x0046BF8A, 0x004AED88), (0x004AED76, 0x004AED88), (0x004AED7E, 0x004AED88)]
ENTRY_SHA256 = "ed9e86ccb9820f7ba47627406836af91d69cd8bca3b3644bbe582edbcbd01372"
BODY_CALLS = 21
BODY_CALL_SHA256 = "085c0a2bc45507b8d777fecadfa96bf3fb3ce0342cbe5f232a3fd5bb10bb19e7"
STORED = [(0x006D1E3C, 0x004AECA5), (0x00746D20, 0x004AECB9)]
STORED_SHA256 = "1ce1da60e334331e2c970862665292b0b882b5f57f4cd0ba0e5f05788267cea5"
WORDS = {
    0x004AEDF8: 0x200037BC,
    0x004AEDFC: 0x0078BF90,
    0x004AEE00: 0x00788A80,
    0x004AEE04: 0x00783320,
    0x004AEE08: 0x006E1824,
    0x004AEE0C: 0x00788A70,
    0x004AEE10: 0x00764F90,
    0x004AEE14: 0x00788A90,
    0x004AEE18: 0x00764FB0,
    0x004AEE1C: 0x00759AF8,
    0x004AEE20: 0x0077B92C,
    0x004AEE24: 0x007384D4,
}
STRINGS = {
    0x0078BF90: "kvAlsScale",
    0x00783320: "_kvdbUpdataAlsScale",
    0x006E1824: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_als_scale.c",
    0x00788A70: "kv.als_scale",
    0x0077B92C: "SVC_KvdbWriteAlsScale",
}
FACTORY = bytes.fromhex("010000000004000000000000")


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

    decoder = load("kvdb_als_scale_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
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

    flashdb = load("kvdb_als_scale_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x200037BC - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 12] != FACTORY or crc16(FACTORY[:8]) != 0xAA2D:
        raise AuditError("factory record changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/kvdb_als_scale.c"
    expected_patches = {
        "replace_kvdb_als_scale_default_initialize": (
            PHYSICAL[0], 20, "e48145091ccb88dae5d4c5be82e5f82713ecd547dc4117c5a7bcaea241e8c1f8",
            "open_cfw_kvdb_als_scale_default_initialize",
        ),
        "replace_kvdb_als_scale_load_and_migrate": (
            0x004AECB8, 208, "13ea4e9b0fa20c2d99e330dedbc23590b6a5de7afbb93e7f1d79feec3a7ba6b5",
            "open_cfw_kvdb_als_scale_load_and_migrate",
        ),
        "replace_kvdb_write_als_scale": (
            0x004AED88, 110, "63ddae17be03306b8a8bb55744d14a5cdec6f3cc6b899b03c43666a26908f7c5",
            "open_cfw_kvdb_write_als_scale",
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
            != "626119a5b2298aa233d22294cfd6121b6c5dad45a2bacacb84cb0124899649d4"
            or leaf.get("profiles") != ["apple-clang"]
            for leaf in leaves.values()
        )
    ):
        raise AuditError("production ALS-scale routing changed")
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
            "address": "0x200037BC",
            "bytes": 12,
            "crc_offset": 8,
            "boot_hex": FACTORY.hex(),
            "initialized_crc16": "0xAA2D",
            "schema_version": 1,
            "key": "kvAlsScale",
        },
        "behavior": {
            "missing_rewrites_current": True,
            "pre_v1_crc_mismatch_rewrites_current": True,
            "v1_crc_mismatch_rewrites_current": False,
            "migration_imports_stored_record": False,
            "writer_forces_version": 1,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_als_scale.c",
            "production_routed": True,
            "ownership_bytes": 338,
            "retained_stock_tail_bytes": 50,
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
