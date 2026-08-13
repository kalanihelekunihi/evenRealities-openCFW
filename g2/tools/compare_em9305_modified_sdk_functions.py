#!/usr/bin/env python3
"""Measure placed vendor-modified EM9305 functions against the exact SDK archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Sequence

import compare_em9305_sdk_archive as sdk


ARCHIVE_GIT_BLOB = "b9433012b264da2210f602395b144a6d21795f01"
ARCHIVE_SHA256 = "87af23b9b6a582137a02759c4af2344f7160a8b88197dd540ef8268aa55f6cfa"
ARCHIVE_SOURCE_PATH = "libs/third_party/emb/lib_emb_controller_iso.a"
EXPECTED_MODIFIED = {
    "LctrGetPeerMinUsedChan": 0x0030_6F44,
    "lctrCenSendPendingRspRptHandler": 0x0031_8168,
    "lctrConnTxCompletedHandler": 0x0031_8F2C,
    "lctrMstExtInitiateEndOp": 0x0032_0274,
    "lctrReceivePeriodicSyncInd": 0x0032_4FB4,
    "lctrRxConnEnq": 0x0032_5324,
    "lctrSendChanMapUpdateInd": 0x0032_5A68,
    "lctrSendRejectInd": 0x0032_698C,
    "lctrSetCisTest": 0x0032_72D8,
}
EXPECTED_MISMATCH_COUNTS = {
    "LctrGetPeerMinUsedChan": 1,
    "lctrCenSendPendingRspRptHandler": 48,
    "lctrConnTxCompletedHandler": 2,
    "lctrMstExtInitiateEndOp": 1,
    "lctrReceivePeriodicSyncInd": 1,
    "lctrRxConnEnq": 1,
    "lctrSendChanMapUpdateInd": 9,
    "lctrSendRejectInd": 2,
    "lctrSetCisTest": 1,
}
EXPECTED_COMPARED_BYTES = 1_008
EXPECTED_MATCHING_COMPARED_BYTES = 942
EXPECTED_MISMATCHING_COMPARED_BYTES = 66


class ModifiedComparisonError(RuntimeError):
    """Raised when modified-function comparison evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def longest_equal_run(candidate: bytes, stock: bytes, masked: set[int]) -> int:
    longest = 0
    current = 0
    for index, (left, right) in enumerate(zip(candidate, stock)):
        if index not in masked and left == right:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def compare_modified(image: Path, archive: Path, binutils_dir: Path) -> dict[str, Any]:
    image = image.resolve()
    archive = archive.resolve()
    binutils_dir = binutils_dir.resolve()
    image_bytes = image.read_bytes()
    if len(image_bytes) != sdk.IMAGE_SIZE or sha256(image_bytes) != sdk.IMAGE_SHA256:
        raise ModifiedComparisonError("official EM9305 image identity mismatch")
    archive_bytes = archive.read_bytes()
    if sha256(archive_bytes) != ARCHIVE_SHA256:
        raise ModifiedComparisonError("controller ISO archive identity mismatch")
    tools = {
        name: binutils_dir / f"arc-linux-gnu-{name}"
        for name in ("ar", "objcopy", "objdump", "readelf")
    }
    for name, executable in tools.items():
        if not executable.is_file():
            raise ModifiedComparisonError(f"ARC binutils {name} missing: {executable}")

    application = image_bytes[sdk.APP_FILE_OFFSET:]
    results: dict[str, dict[str, Any]] = {}
    compiler_comments: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="opencfw-em9305-modified-") as temp_name:
        temp = Path(temp_name)
        sdk.run((str(tools["ar"]), "x", str(archive)), cwd=temp)
        for object_path in sorted(temp.glob("*.obj")):
            symbol_table = sdk.run((str(tools["objdump"]), "-t", str(object_path)))
            functions = [
                function
                for function in sdk.parse_functions(symbol_table)
                if function["name"] in EXPECTED_MODIFIED
            ]
            if not functions:
                continue
            relocation_table = sdk.run((str(tools["objdump"]), "-r", str(object_path)))
            relocations = sdk.parse_relocations(relocation_table)
            comment = subprocess.run(
                (str(tools["readelf"]), "-p", ".comment", str(object_path)),
                check=False,
                capture_output=True,
                text=True,
            ).stdout
            if comment:
                compiler_comments.add(comment.strip())
            section_cache: dict[str, bytes] = {}
            for function in functions:
                name = function["name"]
                if name in results:
                    raise ModifiedComparisonError(f"duplicate selected SDK symbol: {name}")
                section = function["section"]
                if section not in section_cache:
                    section_path = temp / f"selected-{len(section_cache)}.bin"
                    sdk.run((
                        str(tools["objcopy"]),
                        "--dump-section",
                        f"{section}={section_path}",
                        str(object_path),
                    ))
                    section_cache[section] = section_path.read_bytes()
                candidate, masked_tuple = sdk.normalized_body(
                    section_cache[section],
                    function["offset"],
                    function["size"],
                    relocations.get(section, ()),
                )
                address = EXPECTED_MODIFIED[name]
                offset = address - sdk.APP_BASE
                stock = application[offset:offset + function["size"]]
                if len(stock) != function["size"]:
                    raise ModifiedComparisonError(f"stock range truncated: {name}")
                masked = set(masked_tuple)
                mismatches = [
                    {
                        "offset": index,
                        "archive": candidate[index],
                        "stock": stock[index],
                    }
                    for index in range(function["size"])
                    if index not in masked and candidate[index] != stock[index]
                ]
                compared = function["size"] - len(masked)
                matched = compared - len(mismatches)
                results[name] = {
                    "name": name,
                    "object": object_path.name,
                    "address": address,
                    "end": address + function["size"],
                    "size": function["size"],
                    "relocation_count": sum(
                        1
                        for relocation_offset, _kind in relocations.get(section, ())
                        if function["offset"]
                        <= relocation_offset
                        < function["offset"] + function["size"]
                    ),
                    "masked_byte_count": len(masked),
                    "compared_byte_count": compared,
                    "matching_compared_byte_count": matched,
                    "mismatching_compared_byte_count": len(mismatches),
                    "matching_compared_percent": matched / compared * 100.0,
                    "longest_equal_unmasked_run": longest_equal_run(candidate, stock, masked),
                    "archive_normalized_sha256": sha256(candidate),
                    "stock_sha256": sha256(stock),
                    "mismatches": mismatches,
                }

    if set(results) != set(EXPECTED_MODIFIED):
        raise ModifiedComparisonError("selected SDK symbol membership changed")
    comments = "\n".join(sorted(compiler_comments))
    if not all(anchor in comments for anchor in sdk.COMPILER_COMMENT_ANCHORS):
        raise ModifiedComparisonError("selected SDK compiler anchors changed")
    if any(item["mismatching_compared_byte_count"] == 0 for item in results.values()):
        raise ModifiedComparisonError("link-order modified candidate became exact")
    if (
        {
            name: item["mismatching_compared_byte_count"]
            for name, item in results.items()
        }
        != EXPECTED_MISMATCH_COUNTS
        or sum(item["compared_byte_count"] for item in results.values())
        != EXPECTED_COMPARED_BYTES
        or sum(item["matching_compared_byte_count"] for item in results.values())
        != EXPECTED_MATCHING_COMPARED_BYTES
        or sum(item["mismatching_compared_byte_count"] for item in results.values())
        != EXPECTED_MISMATCHING_COMPARED_BYTES
    ):
        raise ModifiedComparisonError("modified-function byte comparison changed")
    return {
        "identity": {
            "firmware_sha256": sdk.IMAGE_SHA256,
            "archive_source_path": ARCHIVE_SOURCE_PATH,
            "archive_git_blob": ARCHIVE_GIT_BLOB,
            "archive_sha256": ARCHIVE_SHA256,
            "compiler_comment_sha256": sha256(comments.encode()),
            "compiler_anchors_matched": True,
        },
        "function_count": len(results),
        "function_bytes": sum(item["size"] for item in results.values()),
        "compared_bytes": sum(item["compared_byte_count"] for item in results.values()),
        "matching_compared_bytes": sum(
            item["matching_compared_byte_count"] for item in results.values()
        ),
        "mismatching_compared_bytes": sum(
            item["mismatching_compared_byte_count"] for item in results.values()
        ),
        "functions": [results[name] for name in sorted(results)],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=sdk.DEFAULT_IMAGE)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--binutils-dir", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = compare_modified(args.image, args.archive, args.binutils_dir)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EM9305 modified SDK function comparison: PASS")
        print(json.dumps({key: value for key, value in report.items() if key != "functions"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
