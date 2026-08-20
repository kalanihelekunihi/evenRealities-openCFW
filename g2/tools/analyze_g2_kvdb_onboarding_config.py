#!/usr/bin/env python3
"""Fail-closed audit of the G2 six-function onboarding-config KVDB object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-onboarding-config-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-onboarding-config-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-onboarding-config-provenance.tsv"
PINS = {
    FUNCTION_MAP: "f16ff9b9620b9ffc1e13cb5548a016c690ec8559342711ba7e040342cbdc6b93",
    CLOSURE: "662de0a6cdd4a2976c0ae102db83b91019b0fb0b3a71cd727b7f4118cf563459",
    PROVENANCE: "51fc420e99eb51d669442e44568d2549711f890890c92ec80af2960fa14004c3",
}
PHYSICAL = (0x004A777C, 0x004A78D0)
PHYSICAL_SHA256 = "5e36bd2e41d5291d353576207da6c5584405af347f3af9a32503c3f40fdd9362"
BODY_SHA256 = "16069fe85f9c1bc5e5bd94870e699c63f560ac3a8b9bf8047b821c4cf406e986"
POOL = (0x004A789A, 0x004A78D0)
POOL_SHA256 = "6b23e391dd71beb890ab659a1e92d9a1b832d9ff211e43a26befec099c8eb8b6"
ENTRY_CALLS = [
    (0x00468036, 0x004A7832),
    (0x0046805C, 0x004A7832),
    (0x0046872C, 0x004A7838),
    (0x00468832, 0x004A7838),
    (0x0047E428, 0x004A77D2),
    (0x0047E474, 0x004A7838),
    (0x0047E490, 0x004A777C),
    (0x0047E4AA, 0x004A7832),
    (0x004A7824, 0x004A777C),
    (0x004A782C, 0x004A77D2),
    (0x004A7894, 0x004A7838),
    (0x004D9900, 0x004A7846),
    (0x004D994A, 0x004A77D2),
    (0x00542DB0, 0x004A7820),
    (0x00542ED4, 0x004A7820),
    (0x00576F3C, 0x004A7820),
    (0x00584398, 0x004A7846),
    (0x00584404, 0x004A7820),
]
ENTRY_SHA256 = "5b072e0f155de73595f9351cabb91645d1ac0515dbe85f93fc106bc737c8a303"
BODY_CALLS = 20
BODY_CALL_SHA256 = "b39cd033976f3858f69145efa101983e416ca5a82b61a7c1678ece2c497229b1"
WORDS = {
    0x004A789C: 0x20000040,
    0x004A78A0: 0x0078335C,
    0x004A78A4: 0x00771348,
    0x004A78A8: 0x006DB934,
    0x004A78AC: 0x0077B95C,
    0x004A78B0: 0x00743360,
    0x004A78B4: 0x00783370,
    0x004A78B8: 0x00738534,
    0x004A78BC: 0x00759B64,
    0x004A78C0: 0x006FCFEC,
    0x004A78C4: 0x0074338C,
    0x004A78C8: 0x00765010,
    0x004A78CC: 0x0070EE24,
}
STRINGS = {
    0x0078335C: "Unknown kv dataIdx\n",
    0x00771348: "SVC_SetKvdbOnboardingConfig",
    0x006DB934: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_onboarding_config.c",
    0x0077B95C: "kv.onboarding_config",
    0x00783370: "kvOnboardingConfig",
    0x00738534: "SVC_KvdbBlobWriteOnboardingConfig: write fail!!",
    0x00759B64: "SVC_KvdbBlobWriteOnboardingConfig",
    0x0074338C: "SVC_KvdbReadOnboardingConfig: read fail!!",
    0x00765010: "SVC_KvdbReadOnboardingConfig",
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sl(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def pairs(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


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
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = sl(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        bodies.append(raw)
    if len(rows) != 6 or sum(map(len, bodies)) != 286 or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function inventory changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256 or sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("physical object changed")
    if sl(blob, 0x004A789A, 0x004A789C) != b"\0\0":
        raise AuditError("alignment changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")

    thumb = load("kvdb_onboarding_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
    entry = []
    interior_bl = []
    entry_bw = []
    interior_bw = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = thumb._thumb_bl_target(blob, site)
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
            target = thumb._thumb_bl_target(blob, site)
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
    if stored:
        raise AuditError("stored entry pointer appeared")
    encoded_interiors = interiors | {value | 1 for value in interiors}
    if any(
        struct.unpack_from("<I", blob, offset)[0] in encoded_interiors
        for offset in range(len(blob) - 3)
    ):
        raise AuditError("strict-interior raw pointer appeared")

    flashdb = load("kvdb_onboarding_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x20000040 - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 1] != b"\0":
        raise AuditError("factory record changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/kvdb_onboarding_config.c"
    expected_patches = {
        "replace_kvdb_onboarding_config_set_indexed": (
            PHYSICAL[0], 86, "2d1f3385ca05b98fb342dc34c1ee8ad71aa60175f8af470026fa9be95851a661",
            "open_cfw_kvdb_onboarding_config_set_indexed",
        ),
        "replace_kvdb_onboarding_config_persist": (
            0x004A77D2, 78, "d67c09e4a97c6506e504143a0f7e196beda3799fa0f7ee8f00069d1a3c510091",
            "open_cfw_kvdb_onboarding_config_persist",
        ),
        "replace_kvdb_onboarding_config_update_and_persist": (
            0x004A7820, 18, "bd671bcfd8e230bd4c5aa25927221bc9dea065e75177646d49d13f268930544f",
            "open_cfw_kvdb_onboarding_config_update_and_persist",
        ),
        "replace_kvdb_onboarding_config_get": (
            0x004A7832, 6, "c45ce6f337503c4c006d32e9251a9eb2abdf9b50be847dee072a74bc580985e0",
            "open_cfw_kvdb_onboarding_config_get",
        ),
        "replace_kvdb_onboarding_config_pointer": (
            0x004A7838, 14, "802bbbec5254cb9a652a5f29a6cae17d15b476cea2f0b7d5099c2ad830a323ed",
            "open_cfw_kvdb_onboarding_config_pointer",
        ),
        "replace_kvdb_onboarding_config_read": (
            0x004A7846, 84, "e853e570c2f01ae9464b3d4e532c0e59bf54ab52de8de068545f75810231daa9",
            "open_cfw_kvdb_onboarding_config_read",
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
            != "f8c3154fe326878b2f89908555238ddc190a6cecc6c874aeed342624b24d561e"
            or leaf.get("profiles") != ["apple-clang"]
            for leaf in leaves.values()
        )
    ):
        raise AuditError("production onboarding-config routing changed")
    return {
        "surface": {
            "linked_functions": 6,
            "body_bytes": 286,
            "physical_bytes": 340,
            "direct_bl_ingress_sites": 18,
            "direct_provider_calls": 20,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        },
        "record": {
            "address": "0x20000040",
            "bytes": 1,
            "boot_hex": "00",
            "key": "kvOnboardingConfig",
            "has_version": False,
            "has_crc": False,
        },
        "behavior": {
            "only_index_zero_is_writable": True,
            "index_zero_null_value_succeeds": True,
            "pointer_getter_ignores_index": True,
            "read_zero_result_is_diagnosed": True,
            "read_imports_stored_byte": True,
            "write_result_is_propagated": True,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_onboarding_config.c",
            "production_routed": True,
            "ownership_bytes": 286,
            "retained_stock_tail_bytes": 54,
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
