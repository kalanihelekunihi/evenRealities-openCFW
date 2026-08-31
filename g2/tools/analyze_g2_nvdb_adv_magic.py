#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party NVDB advertising-magic helper."""

from __future__ import annotations

import argparse
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
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

FUNCTION_MAP = ROOT / "tools/manifests/g2-nvdb-adv-magic-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-nvdb-adv-magic-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-nvdb-adv-magic-provenance.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "6728975150e973c809de53a8ee9b85752f177c9c15162bb6385b00606d1149ff",
    CLOSURE: "8ed32e66d476359fa2a79cac3addd129526d96218c1c1cfdabc3cff5b0266bf5",
    PROVENANCE: "a00f92ba7db4815198f56a171ab9223269a3b8d72e1dd59b5a44318a496b3cbd",
}

PHYSICAL_SPAN = (0x005D9ED0, 0x005D9F48)
PHYSICAL_SHA256 = "624d7bfd338051fe5493107be887f052c41475e1b32f8aeac148889f046ad4f7"
BODY_BYTES = 110
BODY_SHA256 = "54c2a7586a070563f062b418177500ac9af47f88e334029e28ef0ac262f57ba7"
LITERAL_SPAN = (0x005D9F3E, 0x005D9F48)
LITERAL_SHA256 = "617cbc7f0bb3e6341d8ff380ad27541232dbce341759c7035bf29db31bf16646"

EXPECTED_CALLERS = {
    "nvdbAdvMagicDefaultCrcInitialize": [],
    "nvdbAdvMagicLoadAndMigrate": [],
    "nvdbAdvMagicUpdate": [0x005D9F0A, 0x005D9F14],
}
EXPECTED_ENTRY_CALLS = [
    (0x005D9F0A, 0x005D9F1C),
    (0x005D9F14, 0x005D9F1C),
]
EXPECTED_ENTRY_CALL_DIGEST = "5b6d2bbece6567d00f496990c2d8beb26e117874402316830d7f3c15ce30fc20"
EXPECTED_STORED_ENTRIES = [
    (0x006D1E7C, 0x005D9ED1),
    (0x0078F514, 0x005D9EE5),
]
EXPECTED_STORED_DIGEST = "6ef43356215e14e3046901563adae56dbadb108ff19aebbf082068fbd67d84db"
EXPECTED_BODY_CALLS = [
    (0x005D9EDA, 0x0049ACD4),
    (0x005D9EEC, 0x005105F0),
    (0x005D9F0A, 0x005D9F1C),
    (0x005D9F14, 0x005D9F1C),
    (0x005D9F2C, 0x0049ACD4),
    (0x005D9F38, 0x00510602),
]
EXPECTED_BODY_CALL_DIGEST = "9b4879ab60d119706b1d8871b8f5bc964b25963d37960409215fd39f2f452def"
LITERAL_WORDS = {
    0x005D9F40: 0x200038D4,
    0x005D9F44: 0x0078BFE4,
}
RECORD_ADDRESS = 0x200038D4
BOOT_RECORD = bytes.fromhex("01200000")


class AuditError(RuntimeError):
    """Raised when authenticated NVDB advertising-magic evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or first >= last or last > len(blob):
        raise AuditError(f"invalid image span [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def cstring(blob: bytes, address: int) -> str:
    first = address - BASE
    last = blob.find(b"\0", first)
    if first < 0 or last < first:
        raise AuditError(f"invalid C string at 0x{address:08x}")
    return blob[first:last].decode("ascii")


def pair_digest(pairs: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def crc16_ccitt_false(data: bytes) -> int:
    crc = 0xFFFF
    for value in data:
        crc ^= value << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("nvdb_adv_magic_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned NVDB advertising-magic input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 3 or [int(row["recovery_order"]) for row in rows] != [1, 2, 3]:
        raise AuditError("NVDB advertising-magic inventory changed")

    bodies = []
    starts: dict[int, str] = {}
    interiors: set[int] = set()
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock body changed: {row['function']}")
        bodies.append(raw)
        starts[start] = row["function"]
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("NVDB advertising-magic body concatenation changed")
    if sha256(image_slice(blob, *PHYSICAL_SPAN)) != PHYSICAL_SHA256:
        raise AuditError("NVDB advertising-magic physical interval changed")
    if sha256(image_slice(blob, *LITERAL_SPAN)) != LITERAL_SHA256:
        raise AuditError("NVDB advertising-magic literal tail changed")
    if image_slice(blob, 0x005D9F3E, 0x005D9F40) != b"\0\0":
        raise AuditError("NVDB advertising-magic alignment changed")

    for cell, expected in LITERAL_WORDS.items():
        if struct.unpack("<I", image_slice(blob, cell, cell + 4))[0] != expected:
            raise AuditError(f"NVDB advertising-magic literal changed at 0x{cell:08x}")
    if cstring(blob, 0x0078BFE4) != "nvAdvMagic":
        raise AuditError("NVDB advertising-magic key changed")

    decoder = load_decoder()
    entry_calls = []
    interior_calls = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target in starts:
            entry_calls.append((site, target))
        elif target in interiors:
            interior_calls.append((site, target))
    if entry_calls != EXPECTED_ENTRY_CALLS or pair_digest(entry_calls) != EXPECTED_ENTRY_CALL_DIGEST:
        raise AuditError("NVDB advertising-magic direct ingress changed")
    if interior_calls:
        raise AuditError("NVDB advertising-magic strict-interior BL ingress appeared")

    body_calls = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None:
                body_calls.append((site, target))
    if body_calls != EXPECTED_BODY_CALLS or pair_digest(body_calls) != EXPECTED_BODY_CALL_DIGEST:
        raise AuditError("NVDB advertising-magic provider-call closure changed")

    stored_entries = []
    stored_interiors = []
    for value in starts:
        needle = struct.pack("<I", value | 1)
        position = blob.find(needle)
        while position >= 0:
            stored_entries.append((BASE + position, value | 1))
            position = blob.find(needle, position + 1)
    for value in interiors:
        for encoded in (value, value | 1):
            needle = struct.pack("<I", encoded)
            position = blob.find(needle)
            while position >= 0:
                stored_interiors.append((BASE + position, encoded))
                position = blob.find(needle, position + 1)
    stored_entries.sort()
    stored_interiors.sort()
    if stored_entries != EXPECTED_STORED_ENTRIES or pair_digest(stored_entries) != EXPECTED_STORED_DIGEST:
        raise AuditError("NVDB advertising-magic stored roots changed")
    if stored_interiors:
        raise AuditError("NVDB advertising-magic stored strict-interior pointer appeared")

    callers = {name: [] for name in starts.values()}
    for site, target in entry_calls:
        callers[starts[target]].append(site)
    if callers != EXPECTED_CALLERS:
        raise AuditError("NVDB advertising-magic caller topology changed")
    initialized_crc = crc16_ccitt_false(BOOT_RECORD[:2])
    if initialized_crc != 0x0A5C:
        raise AuditError("NVDB advertising-magic default CRC changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/nvdb_adv_magic.c"
    expected_patches = {
        "replace_nvdb_adv_magic_default_crc_initialize": (
            0x005D9ED0,
            20,
            "5653f1fb6916c167139c85501e4ae5549e034304da38265b2adfc24669a6a4b1",
            "open_cfw_nvdb_adv_magic_default_crc_initialize",
        ),
        "replace_nvdb_adv_magic_load_and_migrate": (
            0x005D9EE4,
            56,
            "d0487cc379b27adbf94fd10ddacadc86464ec7fa5d36f574ace3daed4adee841",
            "open_cfw_nvdb_adv_magic_load_and_migrate",
        ),
        "replace_nvdb_adv_magic_update": (
            0x005D9F1C,
            34,
            "6fed33bca24b9e6f7f04583889016a7cfd39a747501d042db2ac7c0c872f8d76",
            "open_cfw_nvdb_adv_magic_update",
        ),
    }
    patches = {
        r["name"]: r
        for r in overlay["patch_sites"]
        if r.get("name") in expected_patches
    }
    leaves = {
        r["function"]: r
        for r in overlay["relocated_leaves"]
        if r.get("source", {}).get("path") == candidate
    }
    if (
        set(patches) != set(expected_patches)
        or any(
            patches[n]["runtime_address"] != a
            or patches[n]["expected_size"] != z
            or patches[n]["expected_sha256"] != d
            or patches[n]["branch"] != "b_w"
            or patches[n]["target_function"] != t
            or patches[n].get("profiles") != ["apple-clang"]
            for n, (a, z, d, t) in expected_patches.items()
        )
        or set(leaves) != {t for *_, t in expected_patches.values()}
        or any(
            l["source"]["sha256"]
            != "13b80f2be2ddd4a9b78c80805eb99a8c091582df745155f5e29d815cbd4bb093"
            or l.get("profiles") != ["apple-clang"]
            for l in leaves.values()
        )
    ):
        raise AuditError("production advertising-magic routing changed")

    return {
        "surface": {
            "linked_functions": 3,
            "body_bytes": BODY_BYTES,
            "physical_bytes": PHYSICAL_SPAN[1] - PHYSICAL_SPAN[0],
            "literal_bytes": LITERAL_SPAN[1] - LITERAL_SPAN[0],
            "direct_bl_ingress_sites": len(entry_calls),
            "stored_entry_pointers": stored_entries,
            "stored_strict_interior_pointers": len(stored_interiors),
            "direct_strict_interior_branches": len(interior_calls),
            "direct_provider_calls": len(body_calls),
        },
        "record": {
            "address": RECORD_ADDRESS,
            "bytes": len(BOOT_RECORD),
            "boot_hex": BOOT_RECORD.hex(),
            "version": BOOT_RECORD[0],
            "magic": BOOT_RECORD[1],
            "boot_crc16": struct.unpack_from("<H", BOOT_RECORD, 2)[0],
            "initialized_crc16": initialized_crc,
            "key": "nvAdvMagic",
        },
        "behavior": {
            "missing_record_rewrites_current_magic": True,
            "v0_crc_mismatch_rewrites_current_magic": True,
            "v1_crc_mismatch_rewrites_current_magic": False,
            "read_crc_compared_to_current_record_crc": True,
            "read_payload_copied_into_current_record": False,
        },
        "callers": callers,
        "lineage": {
            "retained_path": None,
            "retained_exact_symbol": None,
            "whole_file_source_exact": False,
            "historical_generating_commit_resolved": False,
        },
        "production": {
            "candidate_source": candidate,
            "production_routed": True,
            "ownership_bytes": BODY_BYTES,
            "retained_stock_noncode_bytes": LITERAL_SPAN[1] - LITERAL_SPAN[0],
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else (
        "NVDB advertising magic: 3 functions / 110 code bytes; "
        "4-byte v1 record with default magic 0x20"
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
