#!/usr/bin/env python3
"""Fail-closed census for Cordio's linker-retained ATT 16-bit UUID objects."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-att-uuid-object-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-att-uuid-provenance.tsv"
PINS = {
    MAP: "c2e5b77cd0d44680a164244f49eb791b82d34202828ad1c9733d31614766888f",
    PROVENANCE: "1d1faf94d943bf77eafaede3dc945906de2870444b5a2394b29c47c747d76fb5",
}

BLOCK = (0x0078F53A, 0x0078F550)
BLOCK_BYTES = bytes.fromhex("0118002803280229002a012a052aa62ac92a292b2a2b")
BLOCK_SHA = "abd74006e64d5b20f979480d581c692fe24b82bc85d6c3fc8b4ee8ffcfb735e3"
PRIOR_BYTES = bytes.fromhex("3d00")
FOLLOWING_BYTES = bytes.fromhex("002801280028")

LINKED = {
    "attGattSvcUuid": (0x0078F53A, 0x1801, 1),
    "attPrimSvcUuid": (0x0078F53C, 0x2800, 8),
    "attChUuid": (0x0078F53E, 0x2803, 23),
    "attCliChCfgUuid": (0x0078F540, 0x2902, 10),
    "attDnChUuid": (0x0078F542, 0x2A00, 1),
    "attApChUuid": (0x0078F544, 0x2A01, 1),
    "attScChUuid": (0x0078F546, 0x2A05, 3),
    "attCarChUuid": (0x0078F548, 0x2AA6, 1),
    "attRpaoChUuid": (0x0078F54A, 0x2AC9, 1),
    "attGattCsfChUuid": (0x0078F54C, 0x2B29, 1),
    "attGattDbhChUuid": (0x0078F54E, 0x2B2A, 4),
}

REFERENCE_CELLS = [
    (0x004B5ABC, 0x0078F53A), (0x005338A8, 0x0078F54E),
    (0x00533EB4, 0x0078F546), (0x00535468, 0x0078F54E),
    (0x0056C37C, 0x0078F53E), (0x0056E4F0, 0x0078F54E),
    (0x006D271C, 0x0078F53C), (0x006D272C, 0x0078F53E),
    (0x006D274C, 0x0078F53E), (0x006D276C, 0x0078F53E),
    (0x006D278C, 0x0078F53E), (0x006D27AC, 0x0078F53E),
    (0x006D3F30, 0x0078F53C), (0x006D3F40, 0x0078F53E),
    (0x006D3F50, 0x0078F542), (0x006D3F60, 0x0078F53E),
    (0x006D3F70, 0x0078F544), (0x006D3F80, 0x0078F53E),
    (0x006D3F90, 0x0078F548), (0x006D3FA0, 0x0078F53E),
    (0x006D3FB0, 0x0078F54A), (0x006D5AD8, 0x0078F53C),
    (0x006D5AE8, 0x0078F53E), (0x006D5AF8, 0x0078F546),
    (0x006D5B08, 0x0078F540), (0x006D5B18, 0x0078F53E),
    (0x006D5B28, 0x0078F54C), (0x006D5B38, 0x0078F53E),
    (0x006D5B48, 0x0078F54E), (0x006DE974, 0x0078F53C),
    (0x006DE984, 0x0078F53E), (0x006DE9A4, 0x0078F53E),
    (0x006DE9C4, 0x0078F540), (0x006DE9D4, 0x0078F53C),
    (0x006DE9E4, 0x0078F53E), (0x006DEA04, 0x0078F53E),
    (0x006DEA24, 0x0078F540), (0x006DEA34, 0x0078F53C),
    (0x006DEA44, 0x0078F53E), (0x006DEA64, 0x0078F53E),
    (0x006DEA84, 0x0078F540), (0x006DEA94, 0x0078F53C),
    (0x006DEAA4, 0x0078F53E), (0x006DEAC4, 0x0078F53E),
    (0x006DEAE4, 0x0078F540), (0x006DEAF4, 0x0078F53C),
    (0x006DEB04, 0x0078F53E), (0x006DEB24, 0x0078F53E),
    (0x006DEB44, 0x0078F540), (0x0078DF9C, 0x0078F540),
    (0x0078DFB4, 0x0078F540), (0x0078DFBC, 0x0078F546),
    (0x0078DFC4, 0x0078F540), (0x0078DFDC, 0x0078F540),
]
REFERENCE_DIGEST = "fc35bb83ea308315a67feaef930c61b9e5c81bebef7223b1847c664c71277aa1"


class AuditError(RuntimeError):
    """Raised when authenticated ATT UUID evidence changes."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def load_inventory() -> tuple[list[dict[str, str]], list[str]]:
    with MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 152 or [int(row["source_order"]) for row in rows] != list(range(1, 153)):
        raise AuditError("att_uuid source order changed")
    symbols = [row["symbol"] for row in rows]
    if len(set(symbols)) != len(symbols):
        raise AuditError("att_uuid source inventory contains duplicate symbols")
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row["symbol"] for row in rows if row["stock_status"] == "source_only"]
    if [row["symbol"] for row in linked] != list(LINKED) or len(source_only) != 141:
        raise AuditError("att_uuid linked/source-only inventory changed")
    for row in linked:
        address, value, references = LINKED[row["symbol"]]
        if (int(row["stock_address"], 16), int(row["uuid16"], 16), int(row["stock_reference_count"])) != (address, value, references):
            raise AuditError(f"att_uuid inventory row changed: {row['symbol']}")
    if any(row["stock_status"] not in {"linked", "source_only"} for row in rows):
        raise AuditError("att_uuid inventory contains an unknown status")
    return rows, source_only


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")
    rows, source_only = load_inventory()

    block = image_slice(blob, *BLOCK)
    if block != BLOCK_BYTES or sha(block) != BLOCK_SHA:
        raise AuditError("att_uuid retained object block changed")
    if image_slice(blob, BLOCK[0] - 2, BLOCK[0]) != PRIOR_BYTES:
        raise AuditError("att_uuid lower object boundary changed")
    if image_slice(blob, BLOCK[1], BLOCK[1] + 6) != FOLLOWING_BYTES:
        raise AuditError("att_uuid upper object boundary changed")
    for _, (address, value, _) in LINKED.items():
        if image_slice(blob, address, address + 2) != struct.pack("<H", value):
            raise AuditError(f"att_uuid object value changed at {address:#x}")

    targets = {address for address, _, _ in LINKED.values()}
    references = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in targets:
            references.append((BASE + offset, value))
    if references != REFERENCE_CELLS:
        raise AuditError("att_uuid whole-image reference topology changed")
    if any(site % 4 for site, _ in references):
        raise AuditError("att_uuid gained an unaligned reference window")
    digest = sha(b"".join(struct.pack("<II", site, target) for site, target in references))
    if digest != REFERENCE_DIGEST:
        raise AuditError("att_uuid reference digest changed")
    counts = {address: 0 for address in targets}
    for _, target in references:
        counts[target] += 1
    for _, (address, _, expected) in LINKED.items():
        if counts[address] != expected:
            raise AuditError(f"att_uuid per-object reference count changed at {address:#x}")

    with PROVENANCE.open(newline="") as handle:
        provenance = list(csv.DictReader(handle, delimiter="\t"))
    if [row["role"] for row in provenance] != ["historical_oracle", "selected_exact_oracle", "official_later_corroboration"]:
        raise AuditError("att_uuid provenance roles changed")

    return {
        "schema_version": 1,
        "module": {
            "classification": "partially_linked_constant_object",
            "start": BLOCK[0], "end_exclusive": BLOCK[1],
            "linked_data_bytes": len(block),
            "source_inventory_objects": len(rows),
            "linked_object_count": len(LINKED),
            "source_only_object_count": len(source_only),
            "source_only_objects": source_only,
            "stored_reference_cells": len(references),
            "unaligned_reference_windows": 0,
            "block_sha256": BLOCK_SHA,
        },
        "objects": {
            name: {"address": address, "uuid16": value, "reference_cells": references}
            for name, (address, value, references) in LINKED.items()
        },
        "boundaries": {
            "preceding_u16": 0x003D,
            "following_att_uuid_owner": "atts_read.c",
            "following_values": [0x2800, 0x2801, 0x2800],
        },
        "lineage": {
            "selected_source": "Packetcraft r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "52cda51039c7665b66711cb45093395b0d55da34",
            "selected_sha256": "084b088781df6ef09647f6a4251406d92ec1b1aab6c6a61ef93a4982f5b756b7",
            "r4_byte_identical": True,
            "legacy_family_also_contains_all_linked_objects": True,
            "independently_release_discriminating": False,
            "historical_generating_commit_resolved": False,
            "license": "Apache-2.0",
        },
        "production": {"source_owned_bytes_added": 0, "stock_bytes_replaced": 0},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        module = report["module"]
        print("att_uuid audit: PASS")
        print(f"retained object block: {module['start']:#010x}..{module['end_exclusive']:#010x}")
        print(f"objects: {module['linked_object_count']} linked / {module['source_only_object_count']} source-only")
        print(f"whole-image references: {module['stored_reference_cells']} aligned / 0 unaligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
