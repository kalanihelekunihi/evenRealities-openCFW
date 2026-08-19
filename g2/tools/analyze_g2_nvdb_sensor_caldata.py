#!/usr/bin/env python3
"""Fail-closed audit of the G2 sensor-calibration NVDB object.

The audit authenticates eight bounded Thumb bodies, their literal pool,
direct and stored ingress, both persistent records, and the compiled AG
fallback matrix.  It is read-only and has no device or flash-writing path.
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

FUNCTION_MAP = ROOT / "tools/manifests/g2-nvdb-sensor-caldata-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-nvdb-sensor-caldata-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-nvdb-sensor-caldata-provenance.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "98976fa1bf44a5d633e96b1470ee725deb9fff21af4bfb2c7b862106b14b1f29",
    CLOSURE: "7d1a8540f2eea826ff1401a4dab28369e946d232fa2cf105ad29716fb1985acc",
    PROVENANCE: "139678e85fce9b961c234e73c6ffc9fe26a4a3b221e603cb1ac8c3033cc89c96",
}

PHYSICAL_SPAN = (0x00509764, 0x00509B48)
PHYSICAL_SHA256 = "aea081d2dc99d08bbdc14fdb96a4e6b9e55825f41335e1dbf36dce6e4c60ae3b"
BODY_BYTES = 900
BODY_SHA256 = "4baf671c1b1f3e1c18a80ecd6bb5e614aa0ceae3cdbc82949cac0d411475ff6a"
ALIGNMENT_SPAN = (0x00509A3E, 0x00509A40)
ALIGNMENT_SHA256 = "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"
LITERAL_SPAN = (0x00509AEA, 0x00509B48)
LITERAL_SHA256 = "e85c0f0f85a07d3a1383e95e1847c0448ed6fb592d327c639e358c58bfcb20b1"
NONCODE_SHA256 = "5a0a3229b7aab979aa1b85c08384cb33323001973b2cd1da63678507589b17e7"

EXPECTED_ENTRY_CALLS = [
    (0x004A6BF8, 0x005099F8),
    (0x0050989C, 0x0050990C),
    (0x00509902, 0x0050990C),
    (0x00509A12, 0x00509A40),
    (0x00573830, 0x0050999E),
    (0x005742E8, 0x005099F8),
    (0x00580920, 0x005099F8),
    (0x00580A94, 0x0050999E),
    (0x00580AE0, 0x0050999E),
    (0x00580B2C, 0x0050999E),
]
EXPECTED_ENTRY_CALL_DIGEST = "1a911dc247c94e6dca4d21c8b952ded208e0ece64550f86fbc953fcce35710d1"
EXPECTED_STORED_ENTRIES = [
    (0x006D1E9C, 0x00509765),
    (0x006D1EA4, 0x00509985),
    (0x0078F524, 0x0050977D),
    (0x0078F528, 0x0050999B),
]
EXPECTED_STORED_DIGEST = "e0f49b30fec61fe133ac9626298e3d81d8b11cb4ebf515f3ea4a873d66d0f4ee"
EXPECTED_UNALIGNED_INTERIOR_WINDOWS = [
    (0x0045E32D, 0x005097F2),
    (0x004F2897, 0x005099F2),
]
EXPECTED_BODY_CALL_DIGEST = "ad118885f88873ca1a4bacab82d7aa09045f748013d629fe9e5ec76d2d0d8ff7"
EXPECTED_BODY_CALL_COUNT = 50

LITERAL_WORDS = {
    0x00509AEC: 0x3F19999B,
    0x00509AF0: 0x3F59999A,
    0x00509AF4: 0xBF333333,
    0x00509AF8: 0xBF733332,
    0x00509AFC: 0x200038F4,
    0x00509B00: 0x0074E0EC,
    0x00509B04: 0x0077140C,
    0x00509B08: 0x006DE7F4,
    0x00509B0C: 0x0078C014,
    0x00509B10: 0x007385F4,
    0x00509B14: 0x0078E634,
    0x00509B18: 0x00788C20,
    0x00509B1C: 0x00771428,
    0x00509B20: 0x00788C30,
    0x00509B24: 0x00771444,
    0x00509B28: 0x00722E08,
    0x00509B2C: 0x0070EE64,
    0x00509B30: 0x20003950,
    0x00509B34: 0x0078C020,
    0x00509B38: 0x0070EEA4,
    0x00509B3C: 0x0077BB24,
    0x00509B40: 0x006F5EA8,
    0x00509B44: 0x00759C60,
}
EXPECTED_STRINGS = {
    0x006DE7F4: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_sensor_caldata.c",
    0x0077140C: "_nvdbUpdataSensorCaldata",
    0x0077BB24: "_nvdbCheckSensorCaldata",
    0x0078C014: "nv.s.cald",
    0x0078E634: "nvSCald",
    0x0078C020: "nvSCaldAG",
    0x0070EEA4: "Detected abnormal caldata_matrix pattern, resetting to default",
}
DEFAULT_MATRIX_ADDRESS = 0x00759C60
DEFAULT_MATRIX_HEX = (
    "4bab51bf99d5bbbefd12d93ecb48e53eff0c8a3d02805f3f"
    "4ad1b2be88d66e3f849eed3d"
)
DEFAULT_MATRIX_SHA256 = "07beb66d765a155d2367c308a22d9b7f039818d27bf8bdd8f8adab756001bfea"
PRIMARY_BOOT_RECORD = bytes.fromhex(
    "010000000000a03f0000a03f0000a03f0000a03f0000a03f0000a03f"
    "0000a03f0000a03f0000a03f0000a03f7929edff87d6120087d61200"
    "7929edff0000a03fffffffffffffffffffffffffffffffffffffffffffff"
    "ffff00000000"
)
AG_BOOT_RECORD = bytes.fromhex(
    "01000000000000000000000000000000000000000000000000000000"
    + DEFAULT_MATRIX_HEX + "00000000"
)


class AuditError(RuntimeError):
    """Raised when authenticated sensor-calibration evidence changes."""


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
    spec = importlib.util.spec_from_file_location("nvdb_sensor_caldata_thumb", path)
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
            raise AuditError(f"pinned sensor-caldata input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 8 or [int(row["recovery_order"]) for row in rows] != list(range(1, 9)):
        raise AuditError("sensor-caldata function inventory changed")

    bodies = []
    starts: set[int] = set()
    interiors: set[int] = set()
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock body changed: {row['function']}")
        bodies.append(raw)
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("sensor-caldata body concatenation changed")
    if sha256(image_slice(blob, *PHYSICAL_SPAN)) != PHYSICAL_SHA256:
        raise AuditError("sensor-caldata physical interval changed")
    alignment = image_slice(blob, *ALIGNMENT_SPAN)
    literal = image_slice(blob, *LITERAL_SPAN)
    if sha256(alignment) != ALIGNMENT_SHA256 or sha256(literal) != LITERAL_SHA256:
        raise AuditError("sensor-caldata non-code bytes changed")
    if sha256(alignment + literal) != NONCODE_SHA256:
        raise AuditError("sensor-caldata non-code concatenation changed")

    for cell, expected in LITERAL_WORDS.items():
        if struct.unpack("<I", image_slice(blob, cell, cell + 4))[0] != expected:
            raise AuditError(f"sensor-caldata literal changed at 0x{cell:08x}")
    for address, expected in EXPECTED_STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"sensor-caldata string changed at 0x{address:08x}")
    matrix = image_slice(blob, DEFAULT_MATRIX_ADDRESS, DEFAULT_MATRIX_ADDRESS + 36)
    if matrix.hex() != DEFAULT_MATRIX_HEX or sha256(matrix) != DEFAULT_MATRIX_SHA256:
        raise AuditError("sensor-caldata default matrix changed")

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
        raise AuditError("sensor-caldata direct ingress changed")
    if interior_calls:
        raise AuditError("sensor-caldata strict-interior BL ingress appeared")

    body_calls = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None:
                body_calls.append((site, target))
    if len(body_calls) != EXPECTED_BODY_CALL_COUNT or pair_digest(body_calls) != EXPECTED_BODY_CALL_DIGEST:
        raise AuditError("sensor-caldata provider-call closure changed")

    stored_entries = []
    for value in starts:
        needle = struct.pack("<I", value | 1)
        position = blob.find(needle)
        while position >= 0:
            stored_entries.append((BASE + position, value | 1))
            position = blob.find(needle, position + 1)
    stored_entries.sort()
    if stored_entries != EXPECTED_STORED_ENTRIES or pair_digest(stored_entries) != EXPECTED_STORED_DIGEST:
        raise AuditError("sensor-caldata stored entry roots changed")

    raw_interior_windows = []
    for value in interiors:
        for encoded in (value, value | 1):
            needle = struct.pack("<I", encoded)
            position = blob.find(needle)
            while position >= 0:
                raw_interior_windows.append((BASE + position, encoded))
                position = blob.find(needle, position + 1)
    raw_interior_windows.sort()
    if raw_interior_windows != EXPECTED_UNALIGNED_INTERIOR_WINDOWS:
        raise AuditError("sensor-caldata raw interior windows changed")
    if any(address % 4 == 0 for address, _ in raw_interior_windows):
        raise AuditError("aligned sensor-caldata strict-interior pointer appeared")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/nvdb_sensor_caldata.c"
    expected_patches = {
        "replace_nvdb_sensor_caldata_default_initialize": (
            0x00509764, 24, "de5d7932c7206ec0b45983986f89465c9321c1af496c0a0d2b344d4ec5a04ac9",
            "open_cfw_nvdb_sensor_caldata_default_initialize",
        ),
        "replace_nvdb_sensor_caldata_load_and_migrate": (
            0x0050977C, 400, "1e7a393fea147d565878b038fc6f28da1909dd532e49d03754a1a97ec6182edc",
            "open_cfw_nvdb_sensor_caldata_load_and_migrate",
        ),
        "replace_nvdb_sensor_caldata_update": (
            0x0050990C, 120, "d150d259a93568b54fb4496e38ef99c74778961dad526f9bd4b822e0b2920393",
            "open_cfw_nvdb_sensor_caldata_update",
        ),
        "replace_nvdb_sensor_caldata_ag_default_initialize": (
            0x00509984, 22, "70a9ed13bd7b982380fd99a4bec78b1285e40d64d7b78858384130ea1f44d501",
            "open_cfw_nvdb_sensor_caldata_ag_default_initialize",
        ),
        "replace_nvdb_sensor_caldata_ag_load_and_migrate": (
            0x0050999A, 4, "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
            "open_cfw_nvdb_sensor_caldata_ag_load_and_migrate",
        ),
        "replace_nvdb_sensor_caldata_ag_update": (
            0x0050999E, 90, "672d51e8e98d7e9709afbecbe606e63e7639a705912090028955869226bc9c92",
            "open_cfw_nvdb_sensor_caldata_ag_update",
        ),
        "replace_nvdb_sensor_caldata_ag_read": (
            0x005099F8, 70, "bb55d198e1e11e13c14b6931d4d4ce5a2a9eef7af481ebc3c718ac218912ba39",
            "open_cfw_nvdb_sensor_caldata_ag_read",
        ),
        "replace_nvdb_sensor_caldata_check": (
            0x00509A40, 170, "96115eaf104ea073d40f77085ec765f89844909e679bafbdcb16067975cc60b0",
            "open_cfw_nvdb_sensor_caldata_check",
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
            != "3d321cdfffab322fede0d7e3cb6699ba27e49aee9cc14f779da6bac1aafd16a3"
            or leaf.get("profiles") != ["apple-clang"]
            for leaf in leaves.values()
        )
    ):
        raise AuditError("production sensor-caldata routing changed")

    if len(PRIMARY_BOOT_RECORD) != 92 or len(AG_BOOT_RECORD) != 68:
        raise AuditError("sensor-caldata factory ABI changed")
    if sha256(PRIMARY_BOOT_RECORD) != "9940a499daf357537c1794838645920b2f6ac0416f549d4536ba43f282868150":
        raise AuditError("nvSCald boot record changed")
    if sha256(AG_BOOT_RECORD) != "0942e58d67cb61eb2bdfba259d1ae01d5dd2c5424f2d296d7d0292c48ee55311":
        raise AuditError("nvSCaldAG boot record changed")
    if PRIMARY_BOOT_RECORD[28:64] != bytes.fromhex(
        "0000a03f0000a03f0000a03f0000a03f7929edff87d6120087d612007929edff0000a03f"
    ):
        raise AuditError("nvSCald payload layout changed")
    if AG_BOOT_RECORD[28:64] != matrix:
        raise AuditError("nvSCaldAG factory matrix no longer matches compiled fallback")

    return {
        "image_sha256": IMAGE_SHA256,
        "physical_span": [f"0x{value:08X}" for value in PHYSICAL_SPAN],
        "physical_sha256": PHYSICAL_SHA256,
        "functions": len(rows),
        "body_bytes": BODY_BYTES,
        "body_sha256": BODY_SHA256,
        "entry_calls": len(entry_calls),
        "stored_entries": len(stored_entries),
        "strict_interior_ingress": 0,
        "raw_unaligned_interior_windows": len(raw_interior_windows),
        "primary_record": {
            "address": "0x200038F4",
            "bytes": 92,
            "crc_offset": 88,
            "initialized_crc16": f"0x{crc16_ccitt_false(PRIMARY_BOOT_RECORD[:88]):04X}",
        },
        "ag_record": {
            "address": "0x20003950",
            "bytes": 68,
            "crc_offset": 64,
            "initialized_crc16": f"0x{crc16_ccitt_false(AG_BOOT_RECORD[:64]):04X}",
        },
        "default_matrix_sha256": DEFAULT_MATRIX_SHA256,
        "production": {
            "candidate": "components/apollo_main/core_overlay/nvdb_sensor_caldata.c",
            "production_routed": True,
            "ownership_bytes": BODY_BYTES,
            "retained_stock_noncode_bytes": (
                ALIGNMENT_SPAN[1] - ALIGNMENT_SPAN[0]
                + LITERAL_SPAN[1] - LITERAL_SPAN[0]
            ),
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
    try:
        report = analyze(args.image)
    except (AuditError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "sensor-caldata NVDB closure OK: "
            f"{report['functions']} functions / {report['body_bytes']} body bytes / "
            f"{report['entry_calls']} BL ingress / {report['stored_entries']} stored roots"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
