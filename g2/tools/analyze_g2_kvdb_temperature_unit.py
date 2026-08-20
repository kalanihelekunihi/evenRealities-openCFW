#!/usr/bin/env python3
"""Fail-closed audit of the G2 three-function temperature-unit KVDB object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-temperature-unit-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-temperature-unit-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-temperature-unit-provenance.tsv"
PINS = {
    FUNCTION_MAP: "676b1b32d3a8938a9d4bd286cf8bc2a781dd40dd7debca5bc3ab74a7b1c879c8",
    CLOSURE: "98872121bbdcfc8b8dd2f9f82479cc9a3fa5674f78fa0c5f461cac4b13aa50d5",
    PROVENANCE: "065997a52ed54d40326e69cf23b5dad124296fcd018d8e7465411afbcb78f6b3",
}
PHYSICAL = (0x0049B014, 0x0049B198)
PHYSICAL_SHA256 = "c03f4581a435c010b7315a9f949a08103d8dcea72869f5f8cba44a57e0fd55d8"
BODY_SHA256 = "4d9a4d88a10e5938b06f23c46e152295575d41dbe6ce7179bdf4864d26be4500"
POOL = (0x0049B166, 0x0049B198)
POOL_SHA256 = "39ce4c863f149589ba4a3a1b8b091d5f09b7542db79ed515c4172a6b09160a12"
ENTRY_CALLS = [(0x00466152, 0x0049B0F8), (0x0049B0E6, 0x0049B0F8), (0x0049B0EE, 0x0049B0F8)]
ENTRY_SHA256 = "e6b92799cf5eee363cc158e556da3374442c3c25de9d44365bd3c63932d5f87d"
BODY_CALLS = 21
BODY_CALL_SHA256 = "a56cc8164693e9c53053a6e96598a3d0d72143f58b9c3230c4a2a77d7e8f4fd4"
STORED = [(0x006D1E54, 0x0049B015), (0x00746D38, 0x0049B029)]
STORED_SHA256 = "589a1b452aad1bac663729260a1e1b377c2f65041a1a1ebbd5ee2fc113604bd4"
WORDS = {
    0x0049B168: 0x200037FC, 0x0049B16C: 0x007833D4,
    0x0049B170: 0x00788B00, 0x0049B174: 0x00771380,
    0x0049B178: 0x006DE734, 0x0049B17C: 0x0078E5C4,
    0x0049B180: 0x0077B9EC, 0x0049B184: 0x00788B10,
    0x0049B188: 0x0077BA04, 0x0049B18C: 0x0074DF84,
    0x0049B190: 0x00765050, 0x0049B194: 0x00738564,
}
STRINGS = {
    0x007833D4: "kvTemperatureUnit",
    0x00771380: "_kvdbUpdataTemperatureUnit",
    0x006DE734: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_temperature_unit.c",
    0x0078E5C4: "kv.tu",
    0x00765050: "SVC_KvdbWriteTemperatureUnit",
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
    starts = set()
    interiors = set()
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

    decoder = load("kvdb_temperature_unit_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
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

    flashdb = load("kvdb_temperature_unit_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x200037FC - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 12] != FACTORY or crc16(FACTORY[:8]) != 0x76ED:
        raise AuditError("factory record changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/kvdb_temperature_unit.c"
    expected_patches = {
        "replace_kvdb_temperature_unit_default_initialize": (
            PHYSICAL[0], 20, "06b1d8566f7f7686e7d0ae6c2ee8c46cc2f227183db1301de0638cfd868d5a5e",
            "open_cfw_kvdb_temperature_unit_default_initialize",
        ),
        "replace_kvdb_temperature_unit_load_and_migrate": (
            0x0049B028, 208, "f1acbafb6f3571ebc7054ffacb90ff35d1bb69993d9ab4b715cbe5684222929a",
            "open_cfw_kvdb_temperature_unit_load_and_migrate",
        ),
        "replace_kvdb_write_temperature_unit": (
            0x0049B0F8, 110, "b5fd4ef6d6f8da8e21ff45ff152a15cdb30868bfd4ee4fef72afa9848491be2c",
            "open_cfw_kvdb_write_temperature_unit",
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
            != "288f83e95b9526816845f197d0ca7c355a259a03348c0e2140346cb30a01e808"
            or leaf.get("profiles") != ["apple-clang"]
            for leaf in leaves.values()
        )
    ):
        raise AuditError("production temperature-unit routing changed")
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
            "address": "0x200037FC", "bytes": 12, "crc_offset": 8,
            "boot_hex": FACTORY.hex(), "initialized_crc16": "0x76ED",
            "key": "kvTemperatureUnit",
        },
        "behavior": {
            "missing_rewrites_current": True,
            "v0_crc_mismatch_rewrites_current": True,
            "v1_crc_mismatch_rewrites_current": False,
            "migration_imports_stored_record": False,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_temperature_unit.c",
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
