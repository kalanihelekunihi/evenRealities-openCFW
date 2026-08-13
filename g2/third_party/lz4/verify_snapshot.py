#!/usr/bin/env python3
"""Offline verification for the authenticated LZ4 v1.10.0 snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVENANCE_PATH = HERE / "PROVENANCE.json"
CANDIDATE_PATH = ROOT / "research" / "candidates" / "evenhub_lz4_1_10_0.c"

EXPECTED_REPOSITORY = "https://github.com/lz4/lz4.git"
EXPECTED_REF = "refs/tags/v1.10.0"
EXPECTED_COMMIT = "ebb370ca83af193212df4dcbadcc5d87bc0de2f0"
EXPECTED_TREE = "1ff35e0f086e3b431ea0efd001eb5c6254561953"
EXPECTED_FILES = {
    "lz4.c": {
        "size": 118145,
        "sha256": "9396f7de527bc8435de9c7569fb7998e56545a84b4f3c2d808c0235c01774539",
        "git_blob_sha1": "a2f7abee19fb9a5c768f2a6c266acf5b571f0855",
    },
    "lz4.h": {
        "size": 46014,
        "sha256": "26b82efc53d1570f3b54eef02e9c4764c1ad374ff03cac04e2ced5ea4d4c552f",
        "git_blob_sha1": "80e3e5ca04d22db9ec4980dfc43672a13984aa15",
    },
    "LICENSE": {
        "size": 1311,
        "sha256": "8b58c446121a109ccf32edc094bba3010a3d85e4ee3702950db55e4d3e87736c",
        "git_blob_sha1": "488491695a6b6984aa3a49a8392b192ed2bcac1d",
    },
}
EXPECTED_SUBTREE = {
    ".gitattributes",
    "LICENSE",
    "PROVENANCE.json",
    "README.openCFW.md",
    "lz4.c",
    "lz4.h",
    "verify_snapshot.py",
}
EXPECTED_IMAGE = {
    "path": ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin",
    "size": 3523396,
    "sha256": "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
    "mapping_bias": 0x00437FE0,
}
EXPECTED_SPANS = {
    "read_variable_length": (
        0x0054EE90,
        0x0054EF08,
        "ac7afc67dfe6e35d5ccf23ba3e232439b75084fb80ae8b997674c0e473412a55",
    ),
    "LZ4_decompress_generic": (
        0x0054EF08,
        0x0054F338,
        "8d8e6a9598ea565a6ca9b7fa1a41a67a2b1756b8fb43e84e684ed5b11de990ae",
    ),
    "LZ4_decompress_safe": (
        0x0054F338,
        0x0054F356,
        "d824bb067efb6bac662409f00f466631da69272c25c9bea6134c658e713eaef1",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"LZ4 snapshot verification failed: {message}")


def verify_provenance() -> dict[str, Any]:
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    require(provenance["schema_version"] == 1, "unknown provenance schema")
    require(provenance["component"] == "lz4", "component changed")
    require(provenance["license"] == "BSD-2-Clause", "license changed")
    upstream = provenance["upstream"]
    require(upstream["repository"] == EXPECTED_REPOSITORY, "repository changed")
    require(upstream["selected_ref"] == EXPECTED_REF, "selected ref changed")
    require(upstream["selected_commit"] == EXPECTED_COMMIT, "commit changed")
    require(upstream["selected_tree"] == EXPECTED_TREE, "tree changed")
    require(upstream["declared_library_version_number"] == 11000, "version changed")
    selection = provenance["selection"]
    require(
        selection["classification"] == "authenticated upstream release candidate",
        "candidate classification changed",
    )
    require(selection["exact_historical_checkout_proven"] is False, "stock checkout overclaimed")
    require(
        selection["comparison_baseline"]["commit"]
        == "5ff839680134437dbf4678f3d0c7b371d84f4964",
        "v1.9.4 comparison pin changed",
    )
    require(
        provenance["candidate"]["integration_status"]
        == "isolated and not production-configured",
        "candidate unexpectedly marked integrated",
    )
    recorded = {
        item["path"]: {
            "size": item["size"],
            "sha256": item["sha256"],
            "git_blob_sha1": item["git_blob_sha1"],
        }
        for item in provenance["files"]
    }
    require(recorded == EXPECTED_FILES, "upstream inventory changed")
    return provenance


def verify_files() -> None:
    actual = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file()
    }
    require(actual == EXPECTED_SUBTREE, "snapshot subtree inventory changed")
    for name, expected in EXPECTED_FILES.items():
        data = (HERE / name).read_bytes()
        require(len(data) == expected["size"], f"{name} size changed")
        require(sha256(data) == expected["sha256"], f"{name} SHA-256 changed")
        require(git_blob_sha1(data) == expected["git_blob_sha1"], f"{name} Git blob changed")
        require(b"\r" not in data, f"{name} is no longer LF-only")
        require(data.endswith(b"\n"), f"{name} lost terminal LF")


def verify_markers_and_isolation() -> None:
    header = (HERE / "lz4.h").read_text(encoding="utf-8")
    source = (HERE / "lz4.c").read_text(encoding="utf-8")
    license_text = (HERE / "LICENSE").read_text(encoding="utf-8")
    candidate = CANDIDATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "#define LZ4_VERSION_MAJOR    1",
        "#define LZ4_VERSION_MINOR   10",
        "#define LZ4_VERSION_RELEASE  0",
        "LZ4LIB_API int LZ4_decompress_safe (const char* src, char* dst, int compressedSize, int dstCapacity);",
    ):
        require(marker in header, f"header marker missing: {marker}")
    for marker in (
        "read_variable_length(const BYTE** ip, const BYTE* ilimit,",
        "if (unlikely((*ip) > ilimit))",
        "length > ((Rvl_t)(-1)/2)",
        "int LZ4_decompress_safe(const char* source, char* dest, int compressedSize, int maxDecompressedSize)",
        "decode_full_block, noDict,",
    ):
        require(marker in source, f"source marker missing: {marker}")
    require("Redistribution and use in source and binary forms" in license_text, "license grant missing")
    require("THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS" in license_text, "license disclaimer missing")
    require('#include "../../third_party/lz4/lz4.h"' in candidate, "candidate does not use snapshot header")
    require("return LZ4_decompress_safe(" in candidate, "candidate does not delegate upstream")

    forbidden_path = "research/candidates/evenhub_lz4_1_10_0.c"
    configured_paths = [ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"]
    configured_paths.extend((ROOT / "manifests").glob("*.json"))
    for path in configured_paths:
        require(forbidden_path not in path.read_text(encoding="utf-8"), f"candidate configured by {path}")


def verify_official_spans() -> None:
    path = EXPECTED_IMAGE["path"]
    if not path.exists():
        return
    image = path.read_bytes()
    require(len(image) == EXPECTED_IMAGE["size"], "official image size changed")
    require(sha256(image) == EXPECTED_IMAGE["sha256"], "official image hash changed")
    bias = EXPECTED_IMAGE["mapping_bias"]
    for name, (start, end, digest) in EXPECTED_SPANS.items():
        span = image[start - bias:end - bias]
        require(len(span) == end - start, f"{name} span truncated")
        require(sha256(span) == digest, f"{name} stock span changed")


def main() -> None:
    verify_provenance()
    verify_files()
    verify_markers_and_isolation()
    verify_official_spans()
    print("LZ4 v1.10.0 snapshot verification passed")


if __name__ == "__main__":
    main()
