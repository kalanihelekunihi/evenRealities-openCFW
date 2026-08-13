#!/usr/bin/env python3
"""Compare NOP-aware link-order modified EM9305 functions with their SDK bodies."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Sequence

import compare_em9305_sdk_archive as sdk
import compare_em9305_modified_sdk_functions as original


PLACEMENT_REPORT_SHA256 = "3551b7cfec594daaa627e2e2587dd276c956a241f1758b53b5c848d2d31fb4da"
SELECTED_STATUS = "sdk_archive_symbol_identified_vendor_modified_same_size_nop_aware"
EXPECTED_FUNCTION_COUNT = 29
EXPECTED_FUNCTION_BYTES = 4_496
EXPECTED_COMPARED_BYTES = 3_868
EXPECTED_MATCHING_BYTES = 3_815
EXPECTED_MISMATCHING_BYTES = 53
EXPECTED_MISMATCH_COUNTS = {
    "LctrGetAuthPayloadTimeout": 1,
    "LctrGetChannelMap": 1,
    "LctrIsFeatExchHostInit": 1,
    "LctrIsProcActPended": 1,
    "LctrIsWaitingForReply": 1,
    "LctrRejectCisReq": 1,
    "LctrRxAcl": 1,
    "LctrSetAuthPayloadTimeout": 3,
    "LctrSetConnOpFlags": 1,
    "LctrSetEncMode": 1,
    "LctrSetHostNotifyFeatExch": 1,
    "LctrSetPhyTxPowerLevel": 2,
    "PalRadioRxTifs": 1,
    "lctrCenExecuteEcuSm": 2,
    "lctrConnChClassUpdate": 2,
    "lctrConnDefaults": 1,
    "lctrEncNotifyHostLtkReqInd": 1,
    "lctrExtInitSetupInitiate": 4,
    "lctrExtInitSetupInitiatePawr": 3,
    "lctrGetConnRefTime": 1,
    "lctrMstAuxInitiateEndOp": 1,
    "lctrMstInitiateAdvPktHandler": 3,
    "lctrMstInitiateEndOp": 1,
    "lctrMstInitiateExtAdvPktHandler": 3,
    "lctrMstInitiateRxAuxAdvPktHandler": 3,
    "lctrSetupForTx": 2,
    "lctrSlvProcessConnInd": 3,
    "palRadioRxComplete": 6,
    "palRadioTxComplete": 1,
}


class NopAwareComparisonError(RuntimeError):
    """Raised when NOP-aware modified comparison evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compare(
    image: Path,
    archive: Path,
    binutils_dir: Path,
    placement_report: Path,
) -> dict[str, Any]:
    image_bytes = image.resolve().read_bytes()
    if len(image_bytes) != sdk.IMAGE_SIZE or sha256(image_bytes) != sdk.IMAGE_SHA256:
        raise NopAwareComparisonError("official EM9305 image identity mismatch")
    archive_bytes = archive.resolve().read_bytes()
    if sha256(archive_bytes) != original.ARCHIVE_SHA256:
        raise NopAwareComparisonError("controller ISO archive identity mismatch")
    placement_bytes = placement_report.resolve().read_bytes()
    if sha256(placement_bytes) != PLACEMENT_REPORT_SHA256:
        raise NopAwareComparisonError("extended link-order report identity mismatch")
    placement_json = json.loads(placement_bytes)
    selected = {
        item["name"]: item
        for item in placement_json["placements"]
        if item["status"] == SELECTED_STATUS
    }
    if (
        len(selected) != EXPECTED_FUNCTION_COUNT
        or sum(item["size"] for item in selected.values()) != EXPECTED_FUNCTION_BYTES
        or any(item["size"] != item["archive_size"] for item in selected.values())
    ):
        raise NopAwareComparisonError("selected placement membership changed")

    tools = {
        name: binutils_dir.resolve() / f"arc-linux-gnu-{name}"
        for name in ("ar", "objcopy", "objdump", "readelf")
    }
    for name, executable in tools.items():
        if not executable.is_file():
            raise NopAwareComparisonError(f"ARC binutils {name} missing: {executable}")

    application = image_bytes[sdk.APP_FILE_OFFSET:]
    results: dict[str, dict[str, Any]] = {}
    compiler_comments: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="opencfw-em9305-nop-aware-") as temp_name:
        temp = Path(temp_name)
        sdk.run((str(tools["ar"]), "x", str(archive.resolve())), cwd=temp)
        for object_path in sorted(temp.glob("*.obj")):
            functions = [
                function
                for function in sdk.parse_functions(
                    sdk.run((str(tools["objdump"]), "-t", str(object_path)))
                )
                if function["name"] in selected
            ]
            if not functions:
                continue
            relocations = sdk.parse_relocations(
                sdk.run((str(tools["objdump"]), "-r", str(object_path)))
            )
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
                    raise NopAwareComparisonError(f"duplicate selected SDK symbol: {name}")
                section = function["section"]
                if section not in section_cache:
                    section_path = temp / f"section-{len(section_cache)}.bin"
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
                placement = selected[name]
                if function["size"] != placement["size"]:
                    raise NopAwareComparisonError(f"selected SDK size changed: {name}")
                offset = placement["address"] - sdk.APP_BASE
                stock = application[offset:offset + function["size"]]
                masked = set(masked_tuple)
                mismatches = [
                    index
                    for index in range(function["size"])
                    if index not in masked and candidate[index] != stock[index]
                ]
                compared = function["size"] - len(masked)
                matched = compared - len(mismatches)
                results[name] = {
                    "name": name,
                    "object": object_path.name,
                    "address": placement["address"],
                    "size": function["size"],
                    "masked_byte_count": len(masked),
                    "compared_byte_count": compared,
                    "matching_compared_byte_count": matched,
                    "mismatching_compared_byte_count": len(mismatches),
                    "matching_compared_percent": matched / compared * 100.0,
                    "longest_equal_unmasked_run": original.longest_equal_run(
                        candidate, stock, masked
                    ),
                    "archive_normalized_sha256": sha256(candidate),
                    "stock_sha256": sha256(stock),
                    "mismatch_offsets": mismatches,
                }

    if set(results) != set(selected):
        raise NopAwareComparisonError("selected SDK symbol membership changed")
    comments = "\n".join(sorted(compiler_comments))
    if not all(anchor in comments for anchor in sdk.COMPILER_COMMENT_ANCHORS):
        raise NopAwareComparisonError("selected SDK compiler anchors changed")
    if any(item["mismatching_compared_byte_count"] == 0 for item in results.values()):
        raise NopAwareComparisonError("NOP-aware modified candidate became exact")
    if (
        {
            name: item["mismatching_compared_byte_count"]
            for name, item in results.items()
        }
        != EXPECTED_MISMATCH_COUNTS
        or sum(item["compared_byte_count"] for item in results.values())
        != EXPECTED_COMPARED_BYTES
        or sum(item["matching_compared_byte_count"] for item in results.values())
        != EXPECTED_MATCHING_BYTES
        or sum(item["mismatching_compared_byte_count"] for item in results.values())
        != EXPECTED_MISMATCHING_BYTES
    ):
        raise NopAwareComparisonError("NOP-aware modified byte comparison changed")
    return {
        "identity": {
            "firmware_sha256": sdk.IMAGE_SHA256,
            "archive_git_blob": original.ARCHIVE_GIT_BLOB,
            "archive_sha256": original.ARCHIVE_SHA256,
            "placement_report_sha256": PLACEMENT_REPORT_SHA256,
            "compiler_comment_sha256": sha256(comments.encode()),
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
    parser.add_argument("--placement-report", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = compare(args.image, args.archive, args.binutils_dir, args.placement_report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EM9305 NOP-aware modified SDK comparison: PASS")
        print(json.dumps({key: value for key, value in report.items() if key != "functions"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
