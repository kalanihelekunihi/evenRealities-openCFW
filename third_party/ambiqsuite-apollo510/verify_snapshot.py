#!/usr/bin/env python3
"""Verify the pinned AmbiqSuite Apollo510 MSPI source dependency closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PROVENANCE = HERE / "PROVENANCE.json"

EXPECTED_PROVENANCE_SHA256 = (
    "ee9eb7e9ab8465bbe8b836b9baf04d6a10d470091bb60fe51f0771fecf36bdec"
)
EXPECTED_REPOSITORY = "https://github.com/AmbiqMicro/ambiqhal_ambiq.git"
EXPECTED_COMMIT = "5efc0228528a8adce5eae0d226fac85d2551eb3b"
EXPECTED_TREE = "02b79dbf428a8cded053c65c92cc58fa5fdb8e78"
EXPECTED_SOURCE = "mcu/apollo510/hal/mcu/am_hal_mspi.c"
EXPECTED_SOURCE_SHA256 = (
    "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"
)
EXPECTED_LOCAL_FILES = {
    ".gitattributes",
    "LICENSE",
    "PROVENANCE.json",
    "README.openCFW.md",
    "verify_snapshot.py",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"AmbiqSuite snapshot verification failed: {message}")


def load_provenance() -> dict[str, Any]:
    data = PROVENANCE.read_bytes()
    require(digest(data) == EXPECTED_PROVENANCE_SHA256, "provenance changed")
    value = json.loads(data)
    require(value["schema_version"] == 1, "unknown provenance schema")
    require(
        value["component"] == "ambiqsuite-apollo510-mspi-closure",
        "component name changed",
    )
    require(value["license"] == "BSD-3-Clause", "license changed")
    upstream = value["upstream"]
    require(upstream["repository"] == EXPECTED_REPOSITORY, "repository changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    selection = value["selection"]
    require(
        selection["root_translation_unit"] == EXPECTED_SOURCE,
        "root translation unit changed",
    )
    require(
        selection["root_function"] == "am_hal_mspi_interrupt_clear",
        "root function changed",
    )
    require(
        value["safety"]["hardware_operations"] == [],
        "snapshot unexpectedly declares hardware operations",
    )
    require(
        value["safety"]["permits_flash_program_or_erase"] is False,
        "snapshot must not authorize program or erase",
    )
    return value


def verify_files(provenance: dict[str, Any]) -> None:
    records = provenance["files"]
    require(len(records) == 71, "dependency file count changed")
    recorded_paths = {record["path"] for record in records}
    require(len(recorded_paths) == len(records), "duplicate dependency path")
    actual_paths = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file()
    }
    require(
        actual_paths == recorded_paths | EXPECTED_LOCAL_FILES,
        "snapshot subtree inventory changed",
    )
    for record in records:
        path = HERE / record["path"]
        data = path.read_bytes()
        require(len(data) == record["size"], f"{record['path']}: size changed")
        require(
            digest(data) == record["sha256"],
            f"{record['path']}: SHA-256 changed",
        )
        require(
            git_blob(data) == record["git_blob_sha1"],
            f"{record['path']}: Git blob identity changed",
        )
        require(b"\r" not in data, f"{record['path']}: line endings changed")
        require(data.endswith(b"\n"), f"{record['path']}: terminal LF missing")


def verify_markers() -> None:
    source = (HERE / EXPECTED_SOURCE).read_bytes()
    require(digest(source) == EXPECTED_SOURCE_SHA256, "MSPI source changed")
    text = source.decode("ascii")
    for marker in (
        "am_hal_mspi_interrupt_clear(void *pHandle,",
        "uint32_t ui32IntMask)",
        "AM_HAL_MSPI_CHK_HANDLE(pHandle)",
        "MSPIn(ui32Module)->INTCLR = ui32IntMask;",
        "*(volatile uint32_t*)(&MSPIn(ui32Module)->INTSTAT);",
    ):
        require(marker in text, f"MSPI source marker missing: {marker}")

    license_text = (HERE / "LICENSE").read_text(encoding="ascii")
    for marker in (
        "BSD 3-Clause License",
        "Copyright (c) 2025, Ambiq Micro, Inc.",
        'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"',
    ):
        require(marker in license_text, f"license marker missing: {marker}")


def main() -> int:
    provenance = load_provenance()
    verify_files(provenance)
    verify_markers()
    print(
        "AmbiqSuite 5.1.0 Apollo510 MSPI source/header closure, "
        "BSD-3-Clause notices, Git blobs, and SHA-256 pins: OK"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
