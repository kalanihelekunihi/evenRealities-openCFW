#!/usr/bin/env python3
"""Compare GNU ARC opcode streams for link-order-placed size-delta functions."""

from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any, Sequence

import analyze_em9305_sdk_discovery as discovery
import compare_em9305_modified_sdk_functions as original
import compare_em9305_sdk_archive as sdk


PLACEMENT_REPORT_SHA256 = "3551b7cfec594daaa627e2e2587dd276c956a241f1758b53b5c848d2d31fb4da"
SELECTED_STATUS = "sdk_archive_symbol_identified_vendor_modified_size_delta"
EXPECTED_FUNCTION_COUNT = 13
EXPECTED_STOCK_BYTES = 3_940
EXPECTED_ARCHIVE_BYTES = 3_820
EXPECTED_SEQUENCE_METRICS = {
    # archive instructions, stock instructions, matched instructions,
    # longest contiguous matched run
    "BbSlvPawrTxAuxCback": (40, 46, 38, 22),
    "EMSRC_TransmitterTestEnd": (40, 42, 37, 26),
    "PalBbBleTxData": (36, 38, 35, 30),
    "bbMstPerScanRxCompCback": (131, 135, 129, 58),
    "lctrAllocConnCtx": (144, 149, 135, 45),
    "lctrMstDiscoverRxAuxAdvPktPostProcessHandler": (162, 164, 162, 87),
    "lctrMstPerScanCommitOp": (119, 123, 117, 65),
    "lctrProcessRxAck": (66, 67, 66, 39),
    "lctrSendPerSyncFromScan": (236, 241, 230, 152),
    "lctrSendPhyUpdateIndPdu": (61, 61, 57, 38),
    "lhciCommonSendCmdCmplEvt": (180, 182, 178, 136),
    "lhciSlvAdvEncodeEvtPkt": (22, 25, 22, 19),
    "palFrcExpiryHandler": (19, 25, 19, 12),
}
EXPECTED_ARCHIVE_INSTRUCTIONS = 1_256
EXPECTED_STOCK_INSTRUCTIONS = 1_298
EXPECTED_MATCHING_INSTRUCTIONS = 1_225
INSTRUCTION_ADDRESS = re.compile(r"^\s*([0-9a-f]+):\s*$")
INSTRUCTION_ENCODING = re.compile(r"[0-9a-f]{2,8}")
FUNCTION_LABEL = re.compile(r"^\s*[0-9a-f]+\s+<([^>]+)>:\s*$")


class SizeDeltaComparisonError(RuntimeError):
    """Raised when size-delta comparison evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_instructions(text: str) -> list[tuple[int, str, str]]:
    result = []
    for line in text.splitlines():
        # GNU objdump separates the address, encoded words, mnemonic, and
        # operands with tabs.  Preserve that boundary: ARC mnemonics such as
        # ``add1`` are themselves valid hexadecimal strings and a whitespace-
        # only regex can therefore mistake them for another encoded word.
        fields = line.split("\t")
        if len(fields) < 3:
            continue
        address = INSTRUCTION_ADDRESS.match(fields[0])
        encoded_words = fields[1].split()
        mnemonic_fields = fields[2].split(None, 1)
        if (
            not address
            or not encoded_words
            or any(not INSTRUCTION_ENCODING.fullmatch(word) for word in encoded_words)
            or not mnemonic_fields
        ):
            continue
        operands = mnemonic_fields[1] if len(mnemonic_fields) == 2 else ""
        if len(fields) > 3:
            operands = "\t".join(part for part in (operands, *fields[3:]) if part).strip()
        result.append((int(address.group(1), 16), mnemonic_fields[0], operands))
    return result


def extract_function_instructions(text: str, name: str) -> list[tuple[int, str, str]]:
    collecting = False
    lines: list[str] = []
    for line in text.splitlines():
        label = FUNCTION_LABEL.match(line)
        if label:
            if collecting:
                break
            collecting = label.group(1) == name
            continue
        if collecting:
            lines.append(line)
    instructions = parse_instructions("\n".join(lines))
    if not instructions:
        raise SizeDeltaComparisonError(f"archive function disassembly missing: {name}")
    return instructions


def opcode_comparison(archive: Sequence[str], stock: Sequence[str]) -> dict[str, Any]:
    matcher = SequenceMatcher(None, list(archive), list(stock), autojunk=False)
    blocks = [block for block in matcher.get_matching_blocks() if block.size]
    matched = sum(block.size for block in blocks)
    return {
        "archive_instruction_count": len(archive),
        "stock_instruction_count": len(stock),
        "matching_instruction_count": matched,
        "sequence_ratio": matcher.ratio(),
        "longest_matching_instruction_run": max((block.size for block in blocks), default=0),
        "archive_only_instruction_count": len(archive) - matched,
        "stock_only_instruction_count": len(stock) - matched,
        "archive_opcode_sha256": sha256("\n".join(archive).encode()),
        "stock_opcode_sha256": sha256("\n".join(stock).encode()),
        "archive_opcode_counts": dict(sorted(Counter(archive).items())),
        "stock_opcode_counts": dict(sorted(Counter(stock).items())),
    }


def compare(
    placement_report: Path,
    application_objdump: Path,
    archive: Path,
    binutils_dir: Path,
) -> dict[str, Any]:
    placement_bytes = placement_report.resolve().read_bytes()
    if sha256(placement_bytes) != PLACEMENT_REPORT_SHA256:
        raise SizeDeltaComparisonError("extended link-order report identity mismatch")
    if discovery.sha256_file(application_objdump.resolve()) != discovery.EXPECTED_APPLICATION_OBJDUMP_SHA256:
        raise SizeDeltaComparisonError("whole-application GNU ARC objdump identity mismatch")
    archive_bytes = archive.resolve().read_bytes()
    if sha256(archive_bytes) != original.ARCHIVE_SHA256:
        raise SizeDeltaComparisonError("controller ISO archive identity mismatch")

    placement_json = json.loads(placement_bytes)
    selected = {
        item["name"]: item
        for item in placement_json["placements"]
        if item["status"] == SELECTED_STATUS
    }
    if (
        len(selected) != EXPECTED_FUNCTION_COUNT
        or sum(item["size"] for item in selected.values()) != EXPECTED_STOCK_BYTES
        or sum(item["archive_size"] for item in selected.values()) != EXPECTED_ARCHIVE_BYTES
        or any(item["archive_size"] * 2 < item["size"] for item in selected.values())
    ):
        raise SizeDeltaComparisonError("selected size-delta membership changed")

    tools = {
        name: binutils_dir.resolve() / f"arc-linux-gnu-{name}"
        for name in ("ar", "objdump", "readelf")
    }
    for name, path in tools.items():
        if not path.is_file():
            raise SizeDeltaComparisonError(f"ARC binutils {name} missing: {path}")
    stock_instructions = parse_instructions(application_objdump.read_text())
    results: dict[str, dict[str, Any]] = {}
    compiler_comments: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="opencfw-em9305-size-delta-") as temp_name:
        temp = Path(temp_name)
        sdk.run((str(tools["ar"]), "x", str(archive.resolve())), cwd=temp)
        object_cache: dict[str, str] = {}
        for name, placement in selected.items():
            object_path = temp / placement["object"]
            if not object_path.is_file():
                raise SizeDeltaComparisonError(f"selected SDK object missing: {object_path.name}")
            if object_path.name not in object_cache:
                object_cache[object_path.name] = sdk.run((
                    str(tools["objdump"]), "-d", "-M", "cpu=em", str(object_path)
                ))
                comment = subprocess.run(
                    (str(tools["readelf"]), "-p", ".comment", str(object_path)),
                    check=False,
                    capture_output=True,
                    text=True,
                ).stdout
                if comment:
                    compiler_comments.add(comment.strip())
            archive_rows = extract_function_instructions(object_cache[object_path.name], name)
            stock_rows = [
                row for row in stock_instructions
                if placement["address"] <= row[0] < placement["end"]
            ]
            if not stock_rows or stock_rows[0][0] != placement["address"]:
                raise SizeDeltaComparisonError(f"stock function disassembly missing: {name}")
            comparison = opcode_comparison(
                [row[1] for row in archive_rows],
                [row[1] for row in stock_rows],
            )
            results[name] = {
                "name": name,
                "object": placement["object"],
                "address": placement["address"],
                "end": placement["end"],
                "stock_size": placement["size"],
                "archive_size": placement["archive_size"],
                "size_delta": placement["size_delta"],
                **comparison,
            }

    if set(results) != set(selected):
        raise SizeDeltaComparisonError("selected size-delta symbol membership changed")
    observed_metrics = {
        name: (
            item["archive_instruction_count"],
            item["stock_instruction_count"],
            item["matching_instruction_count"],
            item["longest_matching_instruction_run"],
        )
        for name, item in results.items()
    }
    if (
        observed_metrics != EXPECTED_SEQUENCE_METRICS
        or sum(item["archive_instruction_count"] for item in results.values())
        != EXPECTED_ARCHIVE_INSTRUCTIONS
        or sum(item["stock_instruction_count"] for item in results.values())
        != EXPECTED_STOCK_INSTRUCTIONS
        or sum(item["matching_instruction_count"] for item in results.values())
        != EXPECTED_MATCHING_INSTRUCTIONS
        or min(item["sequence_ratio"] for item in results.values()) < 0.85
    ):
        raise SizeDeltaComparisonError("size-delta opcode sequence evidence changed")
    comments = "\n".join(sorted(compiler_comments))
    if not all(anchor in comments for anchor in sdk.COMPILER_COMMENT_ANCHORS):
        raise SizeDeltaComparisonError("selected SDK compiler anchors changed")
    return {
        "identity": {
            "archive_git_blob": original.ARCHIVE_GIT_BLOB,
            "archive_sha256": original.ARCHIVE_SHA256,
            "placement_report_sha256": PLACEMENT_REPORT_SHA256,
            "application_objdump_sha256": discovery.EXPECTED_APPLICATION_OBJDUMP_SHA256,
            "compiler_comment_sha256": sha256(comments.encode()),
        },
        "function_count": len(results),
        "stock_bytes": sum(item["stock_size"] for item in results.values()),
        "archive_bytes": sum(item["archive_size"] for item in results.values()),
        "archive_instruction_count": sum(
            item["archive_instruction_count"] for item in results.values()
        ),
        "stock_instruction_count": sum(
            item["stock_instruction_count"] for item in results.values()
        ),
        "matching_instruction_count": sum(
            item["matching_instruction_count"] for item in results.values()
        ),
        "functions": [results[name] for name in sorted(results)],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--placement-report", type=Path, required=True)
    parser.add_argument("--application-objdump", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--binutils-dir", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = compare(
        args.placement_report,
        args.application_objdump,
        args.archive,
        args.binutils_dir,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EM9305 size-delta GNU ARC comparison: PASS")
        print(json.dumps({key: value for key, value in report.items() if key != "functions"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
