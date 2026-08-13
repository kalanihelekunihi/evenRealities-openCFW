#!/usr/bin/env python3
"""Authenticate the complete stock G2 eAT command registry."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
REGISTRY_MAP = ROOT / "tools/manifests/g2-eat-registry-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-eat-registry-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-eat-registry-provenance.tsv"
PINS = {
    REGISTRY_MAP: "4e31012d8426730ae0cdaecba7365f849e590d83c7c3595704ea0bca2ef5c89c",
    CLOSURE: "0c773c880cd1fce72db177b8d5e9d4fa38e01dfe4e45e75ad8a4550b60586eb4",
    PROVENANCE: "0c06b3ded1f91a6b817a2d66c65bf5788fba7aaca9000c6aa4cbcefe89c732dc",
}
REGISTRY = (0x006C9260, 0x006C93B0)
REGISTRY_SHA256 = "f47c2827a472adac781e19ae785e32c1eec101f5b7947d4be67a6dc07d7884ae"


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cstring(data: bytes, address: int) -> str:
    offset = address - BASE
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return data[offset:end].decode("ascii")


def discover_records(data: bytes) -> list[tuple[int, int, str, int]]:
    high = BASE + len(data)
    result: list[tuple[int, int, str, int]] = []
    for offset in range(0, len(data) - 15, 4):
        kind, name_pointer, handler, auxiliary = struct.unpack_from("<IIII", data, offset)
        if kind > 8 or auxiliary != 0:
            continue
        if not (BASE <= name_pointer < high and handler & 1 and BASE <= (handler & ~1) < high):
            continue
        try:
            name = cstring(data, name_pointer)
        except (AuditError, UnicodeError):
            continue
        if name.startswith("AT") and len(name) <= 80:
            result.append((BASE + offset, kind, name, handler))
    return result


def analyze(image_path: Path = IMAGE) -> dict:
    data = image_path.read_bytes()
    if len(data) != 3_523_396 or sha256(data) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    raw = data[REGISTRY[0] - BASE : REGISTRY[1] - BASE]
    if len(raw) != 336 or sha256(raw) != REGISTRY_SHA256:
        raise AuditError("registry bytes changed")
    with REGISTRY_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = [
        (int(row["record_address"], 0), int(row["type"]), row["command"], int(row["handler"], 0))
        for row in rows
    ]
    discovered = discover_records(data)
    if discovered != expected:
        raise AuditError("global AT record inventory changed")
    if len(rows) != 21 or len({row["handler"] for row in rows}) != 21:
        raise AuditError("registry cardinality changed")
    modules: dict[str, int] = {}
    for row in rows:
        modules[row["closed_by"]] = modules.get(row["closed_by"], 0) + 1
    expected_modules = {
        "g2-eat-bond-connect": 2,
        "g2-at-buzzer": 1,
        "g2-at-codec": 1,
        "g2-at-nus": 1,
        "g2-at-fs": 3,
        "g2-eat-core-sensor": 12,
        "g2-at-tp": 1,
    }
    if modules != expected_modules:
        raise AuditError("module assignment changed")

    return {
        "registry": {
            "interval": "[0x006c9260,0x006c93b0)",
            "bytes": 336,
            "record_size": 16,
            "registered_commands": 21,
            "unassigned_commands": 0,
            "valid_records_elsewhere": 0,
        },
        "modules": modules,
        "commands": [item[2] for item in discovered],
        "production": {
            "production_routed_commands": 0,
            "ownership_bytes": 0,
            "historical_source_inventory_complete": False,
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 complete eAT registry audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
