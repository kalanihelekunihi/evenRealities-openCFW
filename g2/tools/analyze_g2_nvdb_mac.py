#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party NVDB MAC helper.

The analyzer authenticates the official image, three bounded Thumb bodies,
their literal tail, direct/stored ingress, retained strings, and the ten-byte
record ABI.  It is read-only and has no device or flash-writing path.  Run
addresses use ``run = file_offset + 0x00437FE0``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

FUNCTION_MAP = ROOT / "tools/manifests/g2-nvdb-mac-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-nvdb-mac-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-nvdb-mac-provenance.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "b46f9f736e3696f4ca79fbcb27202cc7bec410e8be6e87442674140e3b7dddaa",
    CLOSURE: "3d554b3bbcc8bef98046a7922f691c04509a15f754ac3cc60505f0d40f7c594c",
    PROVENANCE: "c94c30f4b965fc01f2bc22b8aa76b04626e9cddd9cf30ad0ebdfd067214a98cd",
}

PHYSICAL_SPAN = (0x005D9F48, 0x005DA080)
PHYSICAL_SHA256 = "731244e0484db0daef87d3a5224d07640f46631a999ec6fab405b79518de599f"
BODY_BYTES = 280
BODY_SHA256 = "0b74f6f5656bfe25a9412b1dff7171be025a791ad0addbdef48c472f4e0986d1"
LITERAL_SPAN = (0x005DA060, 0x005DA080)
LITERAL_SHA256 = "7c1135adb70b7fec8dade8d8b3f458b1bc4165e8cc00b3e1fb54d18740a8c11c"

EXPECTED_CALLERS = {
    "nvdbMacDefaultInitialize": [],
    "_nvdbUpdataMac": [],
    "nvdbMacUpdate": [0x005DA022, 0x005DA02A],
}
EXPECTED_ENTRY_CALLS = [
    (0x005DA022, 0x005DA034),
    (0x005DA02A, 0x005DA034),
]
EXPECTED_ENTRY_CALL_DIGEST = "683bb2157d72c4c1a104ee94b78dc55bfbb535ddf61c5df817a5428614756a80"
EXPECTED_STORED_ENTRIES = [
    (0x006D1E8C, 0x005D9F49),
    (0x0078F51C, 0x005D9FC3),
]
EXPECTED_STORED_DIGEST = "61e8609f6cd5a03dfa92ec1fa2b27d2e31b1a33dc8eb975747cf802279359eb7"
EXPECTED_BODY_CALLS = [
    (0x005D9F56, 0x00480D72),
    (0x005D9F62, 0x00439BE4),
    (0x005D9F6E, 0x00439BE4),
    (0x005D9F78, 0x004D34C4),
    (0x005D9F88, 0x00439BE4),
    (0x005D9F92, 0x0049ACD4),
    (0x005D9FB6, 0x0049ACD4),
    (0x005D9FC6, 0x0043D0CE),
    (0x005D9FDE, 0x0043D574),
    (0x005D9FE2, 0x0043D0CE),
    (0x005D9FEA, 0x0043D0CE),
    (0x005D9FFA, 0x0043CE9E),
    (0x005DA004, 0x005105F0),
    (0x005DA022, 0x005DA034),
    (0x005DA02A, 0x005DA034),
    (0x005DA040, 0x00439BE4),
    (0x005DA04E, 0x0049ACD4),
    (0x005DA05A, 0x00510602),
]
EXPECTED_BODY_CALL_DIGEST = "c0113d418db8d6292bdcfa1f283d449120a72b92b84dfa7d46f95a48c1fef74e"

LITERAL_WORDS = {
    0x005DA060: 0x200038E4,
    0x005DA064: 0x0074E074,
    0x005DA068: 0x00788C00,
    0x005DA06C: 0x006E9E38,
    0x005DA070: 0x0078E624,
    0x005DA074: 0x007385C4,
    0x005DA078: 0x0078E62C,
    0x005DA07C: 0x200038E5,
}
EXPECTED_STRINGS = {
    0x006E9E38: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_mac.c",
    0x007385C4: "[nv.mac]!!This is only for program debugging",
    0x0074E074: "!!This is only for program debugging",
    0x00788C00: "_nvdbUpdataMac",
    0x0078E624: "nv.mac",
    0x0078E62C: "nvMAC",
}
RECORD_ADDRESS = 0x200038E4
BOOT_RECORD = bytes.fromhex("01000000000000000000")
EXAMPLE_CHIP_ID0 = 0x01234567
EXAMPLE_CHIP_ID1 = 0x89ABCDEF


class AuditError(RuntimeError):
    """Raised when authenticated NVDB MAC evidence changes."""


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


def derive_record(chip_id0: int, chip_id1: int) -> bytes:
    serial = struct.pack("<II", chip_id1, chip_id0)
    suffix = crc16_ccitt_false(serial)
    address = bytearray(struct.pack("<I", zlib.crc32(serial) & 0xFFFFFFFF))
    address.extend((suffix >> 8, ((suffix & 0xFF) & 0xFC) | 0xC0))
    record = bytearray((1, *address, 0, 0, 0))
    struct.pack_into("<H", record, 8, crc16_ccitt_false(record[:8]))
    return bytes(record)


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("nvdb_mac_thumb", path)
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
            raise AuditError(f"pinned NVDB MAC input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 3 or [int(row["recovery_order"]) for row in rows] != [1, 2, 3]:
        raise AuditError("NVDB MAC function inventory changed")

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
        raise AuditError("NVDB MAC body concatenation changed")
    if sha256(image_slice(blob, *PHYSICAL_SPAN)) != PHYSICAL_SHA256:
        raise AuditError("NVDB MAC physical interval changed")
    if sha256(image_slice(blob, *LITERAL_SPAN)) != LITERAL_SHA256:
        raise AuditError("NVDB MAC literal tail changed")

    for cell, expected in LITERAL_WORDS.items():
        if struct.unpack("<I", image_slice(blob, cell, cell + 4))[0] != expected:
            raise AuditError(f"NVDB MAC literal changed at 0x{cell:08x}")
    for address, expected in EXPECTED_STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"NVDB MAC retained string changed at 0x{address:08x}")

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
        raise AuditError("NVDB MAC direct ingress changed")
    if interior_calls:
        raise AuditError("NVDB MAC strict-interior BL ingress appeared")

    body_calls = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None:
                body_calls.append((site, target))
    if body_calls != EXPECTED_BODY_CALLS or pair_digest(body_calls) != EXPECTED_BODY_CALL_DIGEST:
        raise AuditError("NVDB MAC provider-call closure changed")

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
        raise AuditError("NVDB MAC stored-entry roots changed")
    if stored_interiors:
        raise AuditError("NVDB MAC stored strict-interior pointer appeared")

    callers = {name: [] for name in starts.values()}
    for site, target in entry_calls:
        callers[starts[target]].append(site)
    if callers != EXPECTED_CALLERS:
        raise AuditError("NVDB MAC caller topology changed")

    example = derive_record(EXAMPLE_CHIP_ID0, EXAMPLE_CHIP_ID1)
    if example.hex() != "0147e23b4411c800ef1d":
        raise AuditError("NVDB MAC derivation model changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/nvdb_mac.c"
    expected_patches = {
        "replace_nvdb_mac_default_initialize": (
            0x005D9F48,
            122,
            "6518ae9a8bde9545acffeb0896bdac49b86993c9234e46d88bb7554827be3d6f",
            "open_cfw_nvdb_mac_default_initialize",
        ),
        "replace_nvdb_mac_load_and_migrate": (
            0x005D9FC2,
            114,
            "b634daa132d5501b66a4ae1545c3a740987e46c46714cfa054b8ab64faa0d089",
            "open_cfw_nvdb_mac_load_and_migrate",
        ),
        "replace_nvdb_mac_update": (
            0x005DA034,
            44,
            "03972cfd3d66bf294c5c46c3c4323ea7492976d2c0c2092b75b5b3fa48868145",
            "open_cfw_nvdb_mac_update",
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
    device_ids_binding = (
        "-DOPEN_CFW_NVDB_MAC_DEVICE_IDS_GET(chip_id0, chip_id1)="
        "do { unsigned int open_cfw_mcuctrl_info_get(unsigned int, void *); "
        "unsigned int record[16]; "
        "(void)open_cfw_mcuctrl_info_get(1u, record); "
        "*(chip_id0) = record[1]; *(chip_id1) = record[2]; } while (0)"
    )
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
            != "038b882d360fc155dbccdb911e9910779cdabf97b244e53c9baaa38f196943ac"
            or l.get("profiles") != ["apple-clang"]
            or device_ids_binding not in l["toolchain"]["flags"]
            for l in leaves.values()
        )
    ):
        raise AuditError("production MAC routing changed")

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
            "key": "nvMAC",
            "example_chip_id0": EXAMPLE_CHIP_ID0,
            "example_chip_id1": EXAMPLE_CHIP_ID1,
            "example_initialized_hex": example.hex(),
        },
        "derivation": {
            "serial_order": "CHIPID1 little-endian, then CHIPID0 little-endian",
            "address_prefix": "canonical reflected CRC-32, little-endian",
            "address_suffix": "CCITT-FALSE high byte, then low byte",
            "last_octet_mask": "(value & 0xFC) | 0xC0",
            "record_crc_coverage_bytes": 8,
        },
        "behavior": {
            "missing_record_rewrites_current_address": True,
            "v0_crc_mismatch_rewrites_current_address": True,
            "v1_crc_mismatch_rewrites_current_address": False,
            "read_crc_compared_to_current_record_crc": True,
            "read_payload_copied_into_current_record": False,
        },
        "callers": callers,
        "lineage": {
            "retained_path": EXPECTED_STRINGS[0x006E9E38],
            "retained_exact_symbol": "_nvdbUpdataMac",
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
        "NVDB MAC: 3 functions / 280 code bytes; "
        "10-byte v1 derived static-random address record"
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
