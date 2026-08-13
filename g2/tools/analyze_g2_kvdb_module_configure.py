#!/usr/bin/env python3
"""Fail-closed audit of the G2 six-function module-configuration KVDB TU."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-kvdb-module-configure-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-kvdb-module-configure-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-kvdb-module-configure-provenance.tsv"
PINS = {
    FUNCTION_MAP: "2395583d982c765b3d94555725ee41fa487c2e29fd54de1fe58e75fef7fa8ef9",
    CLOSURE: "92a765e2f2c2427eedae8c01783e0baa9699a979bc2387ca5086b2b776cb9f30",
    PROVENANCE: "a17979cb271d1651014eed2dfb22097ceb30be9472b256c1199649175905134f",
}
PHYSICAL = (0x004922F8, 0x00492CB4)
PHYSICAL_SHA256 = "0d6e8a631baccc0090004a182331d60bf1e697e11a1b0b0337ad751bfdd958e7"
BODY_SHA256 = "b0d452d61f46d4f3135d76b9249a481ed3a71c050ea7d3700caa61a35f4662eb"
POOL = (0x00492BE6, 0x00492CB4)
POOL_SHA256 = "a64f77fa2fba8363dfd1ea946bb2ae49aff775da5170f491cdcb3f6bbf74dcef"
ENTRY_CALLS = [
    (0x004605CC, 0x0049292E),
    (0x004715B8, 0x0049240E),
    (0x0047166A, 0x004924F6),
]
ENTRY_SHA256 = "81575d4151a3fe34ef2c8bbf2dead9ec5194a487878e09de7093883c91f59eff"
BODY_CALLS = 115
BODY_CALL_SHA256 = "7a042ac4220e4ef941ce2a34ce67c19888a258d280d4482f488606533fbedfae"
STORED = [
    (0x00746D24, 0x00492509),
    (0x00746D28, 0x00492423),
    (0x00746D2C, 0x004922F9),
]
STORED_SHA256 = "2c4163f6b5c46029033683bb8e3c9ddf04dfc2a78f1d976f2b3e2f0a002e829d"
RAW_INTERIOR_WINDOWS = [
    (0x0044B695, 0x0049234A),
    (0x004D0C89, 0x004923D5),
    (0x00531B1D, 0x004923B4),
    (0x0057876D, 0x004927D5),
    (0x0058ECC8, 0x00492A90),
    (0x00596FF9, 0x00492AFD),
    (0x005E7DF7, 0x004929D5),
    (0x0068414F, 0x004924FF),
]
WORDS = {
    0x00492BE8: 0x00783348,
    0x00492BEC: 0x007432DC,
    0x00492BF0: 0x00783334,
    0x00492BF4: 0x006DE674,
    0x00492BF8: 0x00788AA0,
    0x00492BFC: 0x0071861C,
    0x00492C00: 0x20000030,
    0x00492C04: 0x006E9C94,
    0x00492C08: 0x006DE6D4,
    0x00492C0C: 0x0077132C,
    0x00492C10: 0x20000038,
    0x00492C14: 0x006FCE3C,
    0x00492C18: 0x00759B1C,
    0x00492C1C: 0x006E9CE8,
    0x00492C20: 0x006D7DA4,
    0x00492C24: 0x0069C614,
    0x00492C28: 0x2006D43C,
    0x00492C2C: 0x0077B944,
    0x00492C30: 0x5555AAAA,
    0x00492C34: 0x0070EDA4,
    0x00492C38: 0x00764FD0,
    0x00492C3C: 0x006EFA48,
    0x00492C40: 0x2006AD0C,
    0x00492C44: 0x0076B7BC,
    0x00492C48: 0x00759B40,
    0x00492C4C: 0x0072D5F0,
    0x00492C50: 0x006FCE84,
    0x00492C54: 0x006E4D78,
    0x00492C58: 0x006FCECC,
    0x00492C5C: 0x006E4DD0,
    0x00492C60: 0x006FCF14,
    0x00492C64: 0x006E4E28,
    0x00492C68: 0x007059E0,
    0x00492C6C: 0x006E9D3C,
    0x00492C70: 0x006FCF5C,
    0x00492C74: 0x006E4E80,
    0x00492C78: 0x200746FC,
    0x00492C7C: 0x20074700,
    0x00492C80: 0x006FCFA4,
    0x00492C84: 0x006E4ED8,
    0x00492C88: 0x00738504,
    0x00492C8C: 0x00764FF0,
    0x00492C90: 0x0070EDE4,
    0x00492C94: 0x0074DF34,
    0x00492C98: 0x0072D624,
    0x00492C9C: 0x00743308,
    0x00492CA0: 0x00722CF0,
    0x00492CA4: 0x00743334,
    0x00492CA8: 0x00718658,
    0x00492CAC: 0x0072D658,
    0x00492CB0: 0x00705A24,
}
STRINGS = {
    0x00783348: "kvSystemLanguage",
    0x00783334: "_kvdbUpdataLanguage",
    0x006DE674: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_module_configure.c",
    0x00788AA0: "kv.module_cfg",
    0x0077132C: "kvDashboardAutoCloseValue",
    0x00759B1C: "_kvdbUpdataDashboardAutoCloseValue",
    0x0077B944: "kvMenuConfigureValue",
    0x00764FD0: "_kvdbUpdataMenuConfigureValue",
    0x00764FF0: "SVC_KvdbWriteMenuConfigureValue",
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
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = sl(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        bodies.append(raw)
    if len(rows) != 6 or sum(map(len, bodies)) != 2286 or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function inventory changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256 or sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("physical object changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")

    decoder = load(
        "kvdb_module_configure_thumb",
        ROOT / "tools/recover_apollo_embedded_source_paths.py",
    )
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

    encoded_interiors = interiors | {value | 1 for value in interiors}
    raw_windows = [
        (BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded_interiors
    ]
    if raw_windows != RAW_INTERIOR_WINDOWS:
        raise AuditError("raw interior windows changed")
    # Seven windows are byte-unaligned. The sole aligned window begins at
    # 0x58ECC8, the second halfword of the valid 32-bit Thumb instruction
    # `vmov s3, r2` spanning [0x58ECC6,0x58ECCA); none is stored data.
    if any(site % 2 == 0 for site, _ in raw_windows if site != 0x0058ECC8):
        raise AuditError("new aligned raw interior window appeared")
    if sl(blob, 0x0058ECC6, 0x0058ECCA) != bytes.fromhex("01ee902a"):
        raise AuditError("qualified vmov overlap changed")

    flashdb = load("kvdb_module_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    offset = 0x20000030 - flashdb.IAR_SCATTER_DESTINATION
    if sram[offset : offset + 12] != bytes.fromhex("00000000000000000a000000"):
        raise AuditError("language/dashboard initialized state changed")

    return {
        "surface": {
            "linked_functions": 6,
            "body_bytes": 2286,
            "physical_bytes": 2492,
            "direct_bl_ingress_sites": 3,
            "direct_provider_calls": 115,
            "stored_entry_pointers": 3,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 8,
        },
        "scalars": {
            "language": {
                "key": "kvSystemLanguage",
                "payload_bytes": 1,
                "live_address": "0x20000030",
                "accepted_values": "0..7",
                "default": 0,
            },
            "dashboard_auto_close": {
                "key": "kvDashboardAutoCloseValue",
                "payload_bytes": 4,
                "live_address": "0x20000038",
                "default": 10,
                "mode_two_skips_read": True,
            },
        },
        "menu": {
            "key": "kvMenuConfigureValue",
            "record_address": "0x2006D43C",
            "record_bytes": 888,
            "magic": "0x5555AAAA",
            "capacity": 20,
            "stored_item_bytes": 44,
            "runtime_address": "0x2006AD0C",
            "runtime_item_bytes": 52,
            "use_external_address": "0x200746FC",
            "external_count_address": "0x20074700",
            "stock_count_clamp": False,
            "custom_text_copy_adds_terminator": False,
            "writer_skips_identical_record": True,
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/kvdb_module_configure.c",
            "production_routed": False,
            "ownership_bytes": 0,
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
