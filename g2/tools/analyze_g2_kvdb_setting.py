#!/usr/bin/env python3
"""Fail-closed audit of the G2 three-function primary setting KVDB object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-setting-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-setting-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-setting-provenance.tsv"
PINS = {
    FUNCTION_MAP: "53025b532bdf1a45a1d7ce9d813928f42a031a0399d20e69e1fab5d783a24a97",
    CLOSURE: "ebdba0a395313f1a8506c699496563a974d4385fe5ffaf0073aca024c933b135",
    PROVENANCE: "cd5302fd34586ba704cdeafbcb89a5f8ebb3daf242149bcf0f09a785d9e75e3c",
}
PHYSICAL = (0x004AEB20, 0x004AECA4)
PHYSICAL_SHA256 = "30946d06c30667b33120a1ae4f2d5d0b3a671e9723f4372b9f0a7e342bd9e6c4"
BODY_SHA256 = "e8b2fc69b27a134b51d4bd037f80ec0977f9f49729a16332c0bbc5d350b992ef"
POOL = (0x004AEC74, 0x004AECA4)
POOL_SHA256 = "138f11d6f0bd750049639d8e1db134a22d2f01d9f262c55defe1d22315b1feca"
ENTRY_CALLS = [(0x0046BF10, 0x004AEC04), (0x004AEBF2, 0x004AEC04), (0x004AEBFA, 0x004AEC04)]
ENTRY_SHA256 = "b9dd60fec3f674e1a27c379f4954b23f9134dc40c79e92ca94e66e3f05dada9b"
BODY_CALLS = 22
BODY_CALL_SHA256 = "44d58e9f32d3f19c84d45d351481efd4c8e0efae682f043841d25f8f4c69de2a"
STORED = [(0x006D1E4C, 0x004AEB21), (0x00746D34, 0x004AEB35)]
STORED_SHA256 = "5206ae3467fa31542bac75f54c3a3bae91b65f7d36ddc0f227207dc601164b58"
WORDS = {
    0x004AEC74: 0x200037E0,
    0x004AEC78: 0x0078BF9C,
    0x004AEC7C: 0x00788AE0,
    0x004AEC80: 0x007833C0,
    0x004AEC84: 0x006E4F30,
    0x004AEC88: 0x0078E5BC,
    0x004AEC8C: 0x0077B9A4,
    0x004AEC90: 0x00788AF0,
    0x004AEC94: 0x0077B9BC,
    0x004AEC98: 0x00765030,
    0x004AEC9C: 0x0077B9D4,
    0x004AECA0: 0x0074DF5C,
}
STRINGS = {
    0x0078BF9C: "kvSetting",
    0x007833C0: "_kvdbUpdataSetting",
    0x006E4F30: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_setting.c",
    0x0078E5BC: "kv.tz",
    0x0077B9D4: "SVC_KvdbWriteSetting",
}
FACTORY = bytes.fromhex("0164010000000000060101001e000000000000000000000000000000")


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

    decoder = load("kvdb_setting_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
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

    flashdb = load("kvdb_setting_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x200037E0 - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 28] != FACTORY or crc16(FACTORY[:24]) != 0xA288:
        raise AuditError("factory record changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/kvdb_setting.c"
    expected_patches = {
        "replace_kvdb_setting_default_initialize": (
            0x004AEB20, 20, "6a4e7922014f2807f0d7ec5b81db9070e3fce9b1ee7eaeedc5258308a767383a",
            "open_cfw_kvdb_setting_default_initialize",
        ),
        "replace_kvdb_setting_load_and_migrate": (
            0x004AEB34, 208, "50314234b7adca393a24180077f806b99d2c62774a502f27304ecf725c79c78f",
            "open_cfw_kvdb_setting_load_and_migrate",
        ),
        "replace_kvdb_write_setting": (
            0x004AEC04, 112, "509916161dca000057a04421b182ba3e0df746be3fa678d10c6a2dcab5fcd9e1",
            "open_cfw_kvdb_write_setting",
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
            != "8205380cddd721ee7e74e08c1ea50618f07cd56158c34b3727bfe4364d240e58"
            or leaf.get("profiles") != ["apple-clang"]
            for leaf in leaves.values()
        )
    ):
        raise AuditError("production setting routing changed")
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
            "address": "0x200037E0",
            "bytes": 28,
            "crc_offset": 24,
            "boot_hex": FACTORY.hex(),
            "initialized_crc16": "0xA288",
            "upgraded_crc16": "0x4987",
            "key": "kvSetting",
        },
        "behavior": {
            "missing_rewrites_current": True,
            "pre_v4_crc_mismatch_rewrites_current": True,
            "v4_crc_mismatch_rewrites_current": False,
            "migration_imports_stored_record": False,
            "rewrite_upgrades_factory_version": True,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_setting.c",
            "production_routed": True,
            "ownership_bytes": 340,
            "retained_stock_noncode_bytes": 48,
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
