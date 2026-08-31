#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate and admit the deterministic EM9305 record-package wrapper."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/em9305/source_image"
MODULE_PATH = COMPONENT / "record_package.py"
BUILDER_PATH = COMPONENT / "build_image.py"
README_PATH = COMPONENT / "README.md"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
MANIFEST = ROOT / "tools/manifests/em9305-record-package-summary.json"
IMAGE_SIZE = 211_948
IMAGE_SHA256 = "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
HARDWARE_VALIDATION = "blocked by unavailable physical evidence"
EXPECTED_RECORDS = (
    (0x00300000, 224),
    (0x00300400, 656),
    (0x00302000, 56),
    (0x00302400, 210_888),
)
EXPECTED_ERASE_SECTORS = (0, 0, 1, 1, *range(2, 27))


class AuditError(RuntimeError):
    """Raised when authenticated package structure or policy drifts."""


def require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_package_module():
    spec = importlib.util.spec_from_file_location(
        "g2_em9305_record_package", MODULE_PATH)
    require(spec is not None and spec.loader is not None,
            "cannot import EM9305 record-package module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _source_inventory() -> list[dict[str, Any]]:
    result = []
    for path in (MODULE_PATH, BUILDER_PATH, README_PATH):
        payload = path.read_bytes()
        require(b"SPDX-License-Identifier: MIT" in payload,
                f"EM9305 package source lacks MIT SPDX marker: {path.name}")
        result.append({
            "path": str(path.relative_to(ROOT)),
            "size": len(payload),
            "sha256": sha256(payload),
        })
    return result


def analyze() -> dict[str, Any]:
    image = IMAGE.read_bytes()
    require((len(image), sha256(image)) == (IMAGE_SIZE, IMAGE_SHA256),
            "authenticated EM9305 package identity changed")
    module = load_package_module()
    try:
        parsed = module.parse_package(image)
        rebuilt = module.build_package(parsed.records, parsed.erase_sectors)
    except module.RecordPackageError as error:
        raise AuditError(f"EM9305 record-package parser rejected stock: {error}") from error
    record_shape = tuple(
        (record.address, len(record.payload)) for record in parsed.records)
    require(record_shape == EXPECTED_RECORDS,
            "authenticated EM9305 record table changed")
    require(parsed.erase_sectors == EXPECTED_ERASE_SECTORS,
            "authenticated EM9305 erase-sector table changed")
    require(parsed.metadata_size == 124 and parsed.payload_size == 211_824,
            "authenticated EM9305 package extents changed")
    require(rebuilt == image,
            "EM9305 package wrapper is not a byte-exact stock round trip")

    return {
        "schema_version": 1,
        "status": "record-package-software-closed-source-image-incomplete",
        "component": "G2 EM9305 record-table package",
        "authenticated_stock": {
            "path": str(IMAGE.relative_to(ROOT)),
            "size": len(image),
            "sha256": sha256(image),
        },
        "container": {
            "magic_hex": module.MAGIC.hex(),
            "metadata_bytes": parsed.metadata_size,
            "payload_bytes": parsed.payload_size,
            "record_count": len(parsed.records),
            "erase_sector_count": len(parsed.erase_sectors),
            "erase_sector_table_sha256": sha256(
                b"".join(sector.to_bytes(2, "little")
                         for sector in parsed.erase_sectors)),
            "records": [{
                "index": index,
                "target_address": record.address,
                "size": len(record.payload),
                "sha256": sha256(record.payload),
            } for index, record in enumerate(parsed.records)],
        },
        "source_inventory": _source_inventory(),
        "stock_roundtrip_byte_exact": True,
        "software_wrapper_complete": True,
        "software_package_complete": True,
        "source_records_complete": False,
        "source_image_complete": False,
        "production_routed": False,
        "remaining_software_blockers": [
            "provide production source and linked bytes for all four EM9305 records",
            "resolve target placement and redirects for qualified ARC candidates and the target-linked QP/C component",
            "replace the retained proprietary controller record with redistributable compilable source",
        ],
        "hardware_validation": HARDWARE_VALIDATION,
        "hardware_blocker": HARDWARE_VALIDATION,
        "hardware_operations": [],
    }


def write_manifest(report: dict[str, Any]) -> None:
    MANIFEST.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    report = analyze()
    if args.write_manifest:
        write_manifest(report)
        print(f"wrote {MANIFEST.relative_to(ROOT)}")
    print(json.dumps({
        "status": report["status"],
        "record_count": report["container"]["record_count"],
        "stock_roundtrip_byte_exact": report["stock_roundtrip_byte_exact"],
        "source_image_complete": report["source_image_complete"],
        "hardware_validation": report["hardware_validation"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError) as error:
        raise SystemExit(f"EM9305 record-package admission failed: {error}") from error
