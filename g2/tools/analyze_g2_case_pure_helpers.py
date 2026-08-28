#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit evidence-closed pure helpers from the charging-case frontier."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "components/shared/case"
SOURCE = CASE / "runtime_case_pure_helpers.c"
HEADER = CASE / "runtime_case_pure_helpers.h"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_box.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-box-function-map.tsv"
PRIOR = ROOT / "tools/manifests/g2-case-semantic-leaves-admission-summary.json"
OUTPUT = ROOT / "tools/manifests/g2-case-pure-helpers-admission.tsv"
SUMMARY = ROOT / "tools/manifests/g2-case-pure-helpers-admission-summary.json"
APP_BASE = 0x08000000
WRAPPER_BYTES = 32
BLOB_SHA256 = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"

FUNCTIONS = {
    0x08000294: (
        32, "903f3bc68dbe13c349444a3c1d639bbe2bed70e5ad42f57412ec952fb03339cd",
        "open_cfw_case_shift_left64", "64-bit logical left shift with zero for counts >= 64"),
    0x080002B4: (
        34, "a17868e5884e24c692e1c7b94176c1c1d7ef68c802de5a7af36026a9f1eff4dd",
        "open_cfw_case_shift_right64", "64-bit logical right shift with zero for counts >= 64"),
    0x08009638: (
        32, "b73f98d7e0dbd30d1efb56e070f2e7b63d926900f5ed692f9f6ff5329f3a7e5f",
        "open_cfw_case_emit_left_padding", "emit signed-count spaces when flag 0x2000 is set"),
    0x08009658: (
        44, "8f602aaaff394860d9d724862edfe1099d7fcc817d95e3eb195b96a9cf029d5b",
        "open_cfw_case_emit_right_padding", "emit signed-count spaces or zeroes when flag 0x2000 is clear"),
    0x08009B70: (
        36, "b5f840cee803c0d19f8e2614dac602e70b60e78f6a383bc72dc97662d4681735",
        "open_cfw_case_finalize_length_checksum", "validated <=130-byte length-plus-0x7d additive checksum"),
    0x08009B94: (
        42, "cca7331b83e6ccef154ea6bb58da8eb74c35a5de19c532698bef59448d2323d6",
        "open_cfw_case_hex_value", "ASCII hexadecimal digit conversion; invalid input maps to zero"),
    0x0800BE74: (
        28, "8f224c22a12eadcd871eb0a9450431e604bf735128844b4555adce4508985f9b",
        "open_cfw_case_starts_with_de", "case-insensitive two-character de prefix predicate"),
}

SOURCE_PINS = {
    SOURCE: (2665, "1750ca2a0baec320d478488c6973fe9b5c02e4d439284d9f3549058272ad1a32"),
    HEADER: (1042, "6fcb41ade11927fde74f9098dd51d82992ee48c0b2744d808e99be4432d1ce9e"),
}

FORBIDDEN_SOURCE_TOKENS = (
    "__asm", "asm(", ".byte", ".hword", "expected_hex",
)
RAW_ARRAY_RE = re.compile(
    r"\b(?:u?int(?:8|16|32)_t|unsigned\s+char|char)\s+\w+\s*"
    r"\[[^]]+\]\s*=\s*\{")


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def function_rows() -> dict[int, dict[str, str]]:
    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(
            (line for line in handle if not line.startswith("#")), delimiter="\t")
        return {int(row["entry"], 0): row for row in rows}


def _llvm_nm() -> str | None:
    found = shutil.which("llvm-nm")
    homebrew = Path("/opt/homebrew/opt/llvm/bin/llvm-nm")
    if found is None and homebrew.is_file():
        found = str(homebrew)
    return found


def target_compile() -> tuple[int, str, set[str]]:
    clang = shutil.which("clang")
    nm = _llvm_nm()
    if clang is None or nm is None:
        raise AuditError("clang/llvm-nm unavailable")
    with tempfile.TemporaryDirectory(prefix="g2-case-pure-helpers-") as tmp:
        output = Path(tmp) / "pure-helpers.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
            "-mthumb", "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
            "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
            "-Werror", "-I", str(CASE), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        if proc.returncode != 0:
            raise AuditError(f"target compile failed: {proc.stderr}")
        nm_proc = subprocess.run([
            nm, "-g", "--defined-only", str(output),
        ], capture_output=True, text=True)
        if nm_proc.returncode != 0:
            raise AuditError(f"target symbol audit failed: {nm_proc.stderr}")
        symbols = {
            fields[-1]
            for line in nm_proc.stdout.splitlines()
            if len(fields := line.split()) >= 3
        }
        data = output.read_bytes()
        return len(data), sha256(data), symbols


def analyze() -> dict[str, object]:
    blob = BLOB.read_bytes()
    if sha256(blob) != BLOB_SHA256:
        raise AuditError("case blob identity changed")
    app = blob[WRAPPER_BYTES:]
    mapped_functions = function_rows()
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    prior_remaining = int(prior["metrics"]["unclassified_bytes_after"])
    if prior_remaining != 2646:
        raise AuditError("prior Case admission tip changed")

    combined_source = SOURCE.read_text(encoding="utf-8") + HEADER.read_text(
        encoding="utf-8")
    if combined_source.count("SPDX-License-Identifier: MIT") != 2:
        raise AuditError("source license declarations changed")
    for path, (expected_size, expected_sha) in SOURCE_PINS.items():
        data = path.read_bytes()
        if len(data) != expected_size or sha256(data) != expected_sha:
            raise AuditError(f"source identity changed: {path.relative_to(ROOT)}")
    if any(token in combined_source for token in FORBIDDEN_SOURCE_TOKENS):
        raise AuditError("source contains a forbidden raw-instruction construct")
    if RAW_ARRAY_RE.search(combined_source):
        raise AuditError("source contains an embedded byte/word array")

    object_size, object_sha, compiled_symbols = target_compile()
    expected_symbols = {row[2] for row in FUNCTIONS.values()}
    if compiled_symbols != expected_symbols:
        raise AuditError(
            f"target exports changed: {sorted(compiled_symbols)} != "
            f"{sorted(expected_symbols)}")

    admissions = []
    for address, (size, digest, symbol, contract) in sorted(FUNCTIONS.items()):
        row = mapped_functions.get(address)
        if row is None or row["ownership_category"] != "unresolved":
            raise AuditError(f"function-map boundary changed at {address:#x}")
        if int(row["size"], 0) != size:
            raise AuditError(f"function size changed at {address:#x}")
        body = app[address - APP_BASE:address - APP_BASE + size]
        if len(body) != size or sha256(body) != digest:
            raise AuditError(
                f"authenticated instruction identity changed at {address:#x}")
        admissions.append({
            "entry": address,
            "size": size,
            "name": row["name"],
            "instruction_sha256": digest,
            "source": str(SOURCE.relative_to(ROOT)),
            "symbol": symbol,
            "contract": contract,
            "license": "MIT",
            "status": "isolated_source_candidate_not_routed",
        })
    admitted_bytes = sum(int(row["size"]) for row in admissions)
    if len(admissions) != 7 or admitted_bytes != 248:
        raise AuditError("pure-helper admission baseline changed")
    return {
        "schema_version": 1,
        "component": "G2 charging-case pure helpers",
        "analysis_mode": (
            "offline authenticated instruction/source/build audit; callback "
            "and buffer adapters only; no hardware, MMIO, flash, reset, signing, "
            "or deployment operation"),
        "integration": "isolated source candidate; production routing absent",
        "admissions": admissions,
        "metrics": {
            "admitted_functions": len(admissions),
            "admitted_instruction_bytes": admitted_bytes,
            "unclassified_bytes_before": prior_remaining,
            "unclassified_bytes_after": prior_remaining - admitted_bytes,
            "target_object_bytes": object_size,
            "target_object_sha256": object_sha,
            "target_missing_symbols": 0,
            "target_unexpected_symbols": 0,
            "embedded_instruction_byte_arrays": 0,
        },
        "software_source_complete": True,
        "software_source_complete_scope": "the seven admitted pure helpers only",
        "case_image_source_complete": False,
        "production_routed": False,
        "hardware_validation": "deferred by project direction",
        "hardware_operations": [],
    }


def write_outputs(report: dict[str, object]) -> None:
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "entry", "size", "name", "instruction_sha256", "source", "symbol",
            "contract", "license", "status",
        ])
        for row in report["admissions"]:
            writer.writerow([
                f"0x{int(row['entry']):08X}", row["size"], row["name"],
                row["instruction_sha256"], row["source"], row["symbol"],
                row["contract"], row["license"], row["status"],
            ])
    slim = {key: value for key, value in report.items() if key != "admissions"}
    SUMMARY.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    report = analyze()
    if args.write_manifests:
        write_outputs(report)
    print(json.dumps(report["metrics"], sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Case pure-helper audit failed: {exc}") from exc
