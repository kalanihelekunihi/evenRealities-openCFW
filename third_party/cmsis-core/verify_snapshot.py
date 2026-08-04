#!/usr/bin/env python3
"""Verify the pinned Arm CMSIS Core header dependency closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PROVENANCE = HERE / "PROVENANCE.json"

EXPECTED_PROVENANCE_SHA256 = (
    "b70d669752a897b04ea6ac2cbdf6f5c7ad68e1c172c3805f2fb1ff15f2bb2260"
)
EXPECTED_REPOSITORY = "https://github.com/ARM-software/CMSIS_5.git"
EXPECTED_COMMIT = "d23a6949a0331ca96853bcd98b0fdcc4db47184c"
EXPECTED_TREE = "3474af187114165f3623732474e4e1bd4b3d01d8"
EXPECTED_CORE_SHA256 = (
    "23c98f9996ce044c7a4a3affe4d7be36d15c67d4a1389d604e06d02672bdb1d7"
)
EXPECTED_VERSION_SHA256 = (
    "184c19fd3ee73632edf35a0b4d49cd48be75fbf49e6ccb19d9db05fa83bea4b3"
)
EXPECTED_LOCAL_FILES = {
    ".gitattributes",
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
        raise SystemExit(f"CMSIS Core snapshot verification failed: {message}")


def load_provenance() -> dict[str, Any]:
    data = PROVENANCE.read_bytes()
    require(digest(data) == EXPECTED_PROVENANCE_SHA256, "provenance changed")
    value = json.loads(data)
    require(value["schema_version"] == 1, "unknown provenance schema")
    require(
        value["component"] == "cmsis-core-apollo510-compile-closure",
        "component name changed",
    )
    require(value["license"] == "Apache-2.0", "license changed")
    upstream = value["upstream"]
    require(upstream["repository"] == EXPECTED_REPOSITORY, "repository changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    require(value["safety"]["headers_only"] is True, "snapshot is not headers-only")
    require(
        value["safety"]["hardware_operations"] == [],
        "snapshot unexpectedly declares hardware operations",
    )
    return value


def verify_files(provenance: dict[str, Any]) -> None:
    records = provenance["files"]
    require(len(records) == 8, "dependency file count changed")
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
        data = (HERE / record["path"]).read_bytes()
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
    core = HERE / "CMSIS/Core/Include/core_cm55.h"
    version = HERE / "CMSIS/Core/Include/cmsis_version.h"
    require(digest(core.read_bytes()) == EXPECTED_CORE_SHA256, "core_cm55.h changed")
    require(
        digest(version.read_bytes()) == EXPECTED_VERSION_SHA256,
        "cmsis_version.h changed",
    )
    license_text = (HERE / "LICENSE.txt").read_text(encoding="utf-8")
    require("Apache License" in license_text, "Apache license heading missing")
    require("Version 2.0, January 2004" in license_text, "license version changed")


def main() -> int:
    provenance = load_provenance()
    verify_files(provenance)
    verify_markers()
    print(
        "Arm CMSIS Core Cortex-M55 header closure, Apache-2.0 license, "
        "Git blobs, and SHA-256 pins: OK"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
