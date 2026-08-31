#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party NVDB buzzer helper.

The analyzer authenticates the official image, five bounded Thumb bodies,
their literal tail, direct/stored ingress, retained strings, and the twelve-
byte boot record.  It is read-only and has no device or flash-writing path.
Run addresses use ``run = file_offset + 0x00437FE0``.
"""

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

FUNCTION_MAP = ROOT / "tools/manifests/g2-nvdb-buzzer-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-nvdb-buzzer-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-nvdb-buzzer-provenance.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "850aaac25c1fc93b7637f10a24e0efc42f69dee28bb134e2986a77d2c316d6df",
    CLOSURE: "ccbb386bf0f0fed28166eb4dd82f4afa5a46c7f75d16f23fb11dce2de443cc33",
    PROVENANCE: "5e45a36272be3866b05ba27f4533cccc2363e658cb02692fcf522b8f82477e1b",
}

PHYSICAL_SPAN = (0x0058F9D4, 0x0058FAAC)
PHYSICAL_SHA256 = "d6b02b1bed7012f6c8288b83f106454d7a992acba1f92fa10e390f82fe0b0e8b"
BODY_BYTES = 188
BODY_SHA256 = "70118688652fb4a53ee42a522f5df58b6defcba717b99cd8bd420b305bcb95e3"
LITERAL_SPAN = (0x0058FA90, 0x0058FAAC)
LITERAL_SHA256 = "6443889744e2a855e5d4181e761f4876ea417c9d1e871a73a221a3462b59043c"

EXPECTED_CALLERS = {
    "nvdbBuzzerDefaultCrcInitialize": [],
    "_nvdbUpdataBuzzer": [],
    "nvdbBuzzerFrequencyGet": [0x00576B30],
    "nvdbBuzzerDutyGet": [0x00576B4C],
    "nvdbBuzzerUpdate": [0x00576CCE, 0x0058FA4A, 0x0058FA56],
}
EXPECTED_ENTRY_CALLS = [
    (0x00576B30, 0x0058FA60),
    (0x00576B4C, 0x0058FA66),
    (0x00576CCE, 0x0058FA6C),
    (0x0058FA4A, 0x0058FA6C),
    (0x0058FA56, 0x0058FA6C),
]
EXPECTED_ENTRY_CALL_DIGEST = "a18689271e13a5e555481245669abc5a0438e639d07fb424ef017e0349bc286c"
EXPECTED_STORED_ENTRIES = [
    (0x006D1E84, 0x0058F9D5),
    (0x0078F518, 0x0058F9E9),
]
EXPECTED_STORED_DIGEST = "6b91b6a1c04f563f6e29fb31b3154f5c723fa58982e60bd4ac0fc4d806c07763"
EXPECTED_BODY_CALLS = [
    (0x0058F9DE, 0x0049ACD4),
    (0x0058F9EC, 0x0043D0CE),
    (0x0058FA04, 0x0043D574),
    (0x0058FA08, 0x0043D0CE),
    (0x0058FA10, 0x0043D0CE),
    (0x0058FA20, 0x0043CE9E),
    (0x0058FA2A, 0x005105F0),
    (0x0058FA4A, 0x0058FA6C),
    (0x0058FA56, 0x0058FA6C),
    (0x0058FA7E, 0x0049ACD4),
    (0x0058FA8A, 0x00510602),
]
EXPECTED_BODY_CALL_DIGEST = "7db171d936c3ccbc3ff3c6cae8f945fdd2cbe834258fad0d0b63665baf3f6a50"

LITERAL_WORDS = {
    0x0058FA90: 0x200038D8,
    0x0058FA94: 0x0074E04C,
    0x0058FA98: 0x0078344C,
    0x0058FA9C: 0x006E4F88,
    0x0058FAA0: 0x0078BFF0,
    0x0058FAA4: 0x00738594,
    0x0058FAA8: 0x0078BFFC,
}
EXPECTED_STRINGS = {
    0x006E4F88: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_buzzer.c",
    0x00738594: "[nv.buzzer]!!This is only for program debugging",
    0x0074E04C: "!!This is only for program debugging",
    0x0078344C: "_nvdbUpdataBuzzer",
    0x0078BFF0: "nv.buzzer",
    0x0078BFFC: "nvBuzzer",
}
RECORD_ADDRESS = 0x200038D8
BOOT_RECORD = bytes.fromhex("02000000a00f00001e000000")


class AuditError(RuntimeError):
    """Raised when authenticated NVDB buzzer evidence changes."""


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
    spec = importlib.util.spec_from_file_location("nvdb_buzzer_thumb", path)
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
            raise AuditError(f"pinned NVDB buzzer input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 5 or [int(row["recovery_order"]) for row in rows] != list(range(1, 6)):
        raise AuditError("NVDB buzzer function inventory changed")

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
        raise AuditError("NVDB buzzer body concatenation changed")
    if sha256(image_slice(blob, *PHYSICAL_SPAN)) != PHYSICAL_SHA256:
        raise AuditError("NVDB buzzer physical interval changed")
    if sha256(image_slice(blob, *LITERAL_SPAN)) != LITERAL_SHA256:
        raise AuditError("NVDB buzzer literal tail changed")

    for cell, expected in LITERAL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"NVDB buzzer literal changed at 0x{cell:08x}")
    for address, expected in EXPECTED_STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"NVDB buzzer retained string changed at 0x{address:08x}")

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
        raise AuditError("NVDB buzzer direct ingress changed")
    if interior_calls:
        raise AuditError("NVDB buzzer strict-interior BL ingress appeared")

    body_calls = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None:
                body_calls.append((site, target))
    if body_calls != EXPECTED_BODY_CALLS or pair_digest(body_calls) != EXPECTED_BODY_CALL_DIGEST:
        raise AuditError("NVDB buzzer provider-call closure changed")

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
        raise AuditError("NVDB buzzer stored-entry roots changed")
    if stored_interiors:
        raise AuditError("NVDB buzzer stored strict-interior pointer appeared")

    callers = {name: [] for name in starts.values()}
    for site, target in entry_calls:
        callers[starts[target]].append(site)
    if callers != EXPECTED_CALLERS:
        raise AuditError("NVDB buzzer caller topology changed")

    initialized_crc = crc16_ccitt_false(BOOT_RECORD[:10])
    if initialized_crc != 0x9B1E:
        raise AuditError("NVDB buzzer default CRC changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/nvdb_buzzer.c"
    expected_patches = {
        "replace_nvdb_buzzer_default_crc_initialize": (
            0x0058F9D4, 20, "177a661785b53b0057bdc93eec3ec350e2876399d6a47029c758fb1f47cf72c1",
            "open_cfw_nvdb_buzzer_default_crc_initialize",
        ),
        "replace_nvdb_buzzer_load_and_migrate": (
            0x0058F9E8, 120, "06805d442594087356c548b9e6bf1f58fb77d5ae58f1f7db037be790d427ef19",
            "open_cfw_nvdb_buzzer_load_and_migrate",
        ),
        "replace_nvdb_buzzer_frequency_get": (
            0x0058FA60, 6, "f90b05ca12e572b728068cc575c618d3c766251b3551dde1c2da7ca52fca6e61",
            "open_cfw_nvdb_buzzer_frequency_get",
        ),
        "replace_nvdb_buzzer_duty_get": (
            0x0058FA66, 6, "8c705b33d544b9b5c56a0a485c8d2bc1550791fb2186c0ca942d908aae5f22be",
            "open_cfw_nvdb_buzzer_duty_get",
        ),
        "replace_nvdb_buzzer_update": (
            0x0058FA6C, 36, "dfcc2933e62aa533c08d37a3554bff2c80502a5a8dffd6b8a78a879d38d87647",
            "open_cfw_nvdb_buzzer_update",
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
            != "0d76cc6e1dee081a938cb02e20b8a877e086c1239306307da2c4e052d2dca421"
            or leaf.get("profiles") != ["apple-clang"]
            for leaf in leaves.values()
        )
    ):
        raise AuditError("production buzzer routing changed")

    return {
        "surface": {
            "linked_functions": 5,
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
            "frequency_hz": struct.unpack_from("<I", BOOT_RECORD, 4)[0],
            "duty_percent": BOOT_RECORD[8],
            "boot_crc16": struct.unpack_from("<H", BOOT_RECORD, 10)[0],
            "initialized_crc16": initialized_crc,
            "key": "nvBuzzer",
        },
        "behavior": {
            "missing_record_rewrites_defaults": True,
            "pre_v2_crc_mismatch_rewrites_defaults": True,
            "v2_crc_mismatch_rewrites_defaults": False,
            "read_crc_compared_to_current_record_crc": True,
            "read_payload_copied_into_current_record": False,
        },
        "callers": callers,
        "lineage": {
            "retained_path": EXPECTED_STRINGS[0x006E4F88],
            "retained_exact_symbol": "_nvdbUpdataBuzzer",
            "whole_file_source_exact": False,
            "historical_generating_commit_resolved": False,
        },
        "production": {
            "candidate_source": "components/apollo_main/core_overlay/nvdb_buzzer.c",
            "production_routed": True,
            "ownership_bytes": 188,
            "retained_stock_noncode_bytes": 28,
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
        "NVDB buzzer: 5 functions / 188 code bytes; "
        "record v2 4000 Hz 30%; initialized CRC 0x9B1E"
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
