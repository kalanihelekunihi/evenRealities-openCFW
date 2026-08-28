#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit evidence-closed charging-case register/state policy leaves."""

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
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_box.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-box-function-map.tsv"
FRONTIER = ROOT / "tools/manifests/g2-case-final-function-frontier.tsv"
CORPUS = ROOT / "research/corpus/case/ghidra/final-frontier/functions.jsonl"
PRIOR = ROOT / "tools/manifests/g2-case-pure-helpers-admission-summary.json"
CASE = ROOT / "components/shared/case"
SOURCE = CASE / "runtime_case_register_policies.c"
HEADER = CASE / "runtime_case_register_policies.h"
OUTPUT = ROOT / "tools/manifests/g2-case-register-policies-admission.tsv"
SUMMARY = ROOT / "tools/manifests/g2-case-register-policies-admission-summary.json"
APP_BASE = 0x08000000
WRAPPER_BYTES = 32
BLOB_SHA256 = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"
RAW_DIRECTIVE = re.compile(r"\.(?:byte|short|hword|word)\b")
FIXED_MMIO_CAST = re.compile(
    r"\(\s*(?:const\s+)?volatile[^)]*\*\s*\)\s*(?:UINT32_C\()?0x")

# entry: (size, instruction SHA-256, evidence-decompilation SHA-256,
# source symbol, semantic contract)
ADMISSIONS = {
    0x08003EEC: (
        36,
        "56ea55b6763b6184a8f3dbd98468109819949fed6d7e741fba9e15e39b8bbc3d",
        "cba98662990291d2cf6fefdf4e4542fdcbe54c8641281f74d167552660e50bbb",
        "open_cfw_case_gpio_policy_update",
        "caller register word 5 preserve/mode/selection/fixed-mask update",
    ),
    0x08003F1C: (
        22,
        "2f8c43877af0ece822d02dc56db09049871bc7a25328011fd545eeecf9fb770d",
        "ba67a70f835b59ac14d43740790ed89f83dc47d50a37449aff5cec6beaaa80c5",
        "open_cfw_case_register_pair_commit",
        "set register word 5 bit 0 and commit two words across an ISB",
    ),
    0x08004B20: (
        22,
        "8ffaebc5d978ec530921d231282a2fac6ed292a17590bab6a3c50f97ed18563e",
        "5422c3ac3209600faed1504f8dadcf57d50360d351671378b2d7ecdd2b1f126d",
        "open_cfw_case_flag31_set",
        "set register word 5 bit 31 and return its sign-bit-clear predicate",
    ),
    0x08004B3C: (
        16,
        "255dcc7be0c4303a942b9bae389e3c45f6d77e03ca298f5daae118a083ccf732",
        "7c9432f8d4567534c15302c4401213c266b09a5cbbcae3324b3774db42d8ea93",
        "open_cfw_case_flag27_set",
        "set register word 5 bit 27 and return one",
    ),
    0x08004B50: (
        22,
        "d6f7f2f984a99e96501c2e924d5e359d6a6eaa497bb3ea9d6eabac09eacd8b81",
        "c53c06425aaa3a1cfbdd343926886508b38266cbd5f5e65a7dc53ed8468eb47b",
        "open_cfw_case_flag30_set",
        "set register word 5 bit 30 and return its shifted-sign-clear predicate",
    ),
    0x0800500C: (
        18,
        "98fbcb9dc3dd773a89e7b619fd15f70ae95d40e7dcee100ea39ed1b7a274b9d8",
        "f204655add06ef0ebed418b0778945d72fdbd375cccb635e8f5b303f263101b9",
        "open_cfw_case_interrupt_enable",
        "ignore negative IRQs; write one bit selected modulo 32 otherwise",
    ),
    0x0800543C: (
        48,
        "e6fa8811709e85b3fd2b270e4ab60a367efa63d79c478bb47ab5d0b7f8272764",
        "8382048dbb480f99bf573123cb320d9c9cdd16c8b3512e27e7684c61d558bef2",
        "open_cfw_case_clock_descriptor",
        "extract clock configuration fields and a three-bit selector",
    ),
    0x0800A358: (
        30,
        "5893e12d31f1c2bc67b99a5105eda382bbe8cc22667c615237100fd7661d38db",
        "4039c549e869bf04011f61d236fb6d37e1919def55bfd864b95a75b5a06a376f",
        "open_cfw_case_validate_magic_state",
        "validate count >= 2 and marker Z, emit 0x5A, and replace count with boolean",
    ),
}

SOURCE_PINS = {
    SOURCE: (
        2887,
        "5952682feb7dddf1e155fce2a9e198e5e8079ed87b8bf938c798d157055145e4",
    ),
    HEADER: (
        1011,
        "c1296e62e18de816dce5f89d76f285bbc8b1bc960c59bdb1b098d6a6bb9df277",
    ),
}


class AuditError(RuntimeError):
    """Raised when authenticated evidence or source admission changes."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_tsv(path: Path) -> dict[int, dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(
            (line for line in handle if not line.startswith("#")),
            delimiter="\t",
        )
        return {int(row["entry"], 0): row for row in reader}


def _read_corpus() -> dict[int, dict]:
    rows = {}
    for line in CORPUS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[int(row["address"])] = row
    return rows


def _target_compile() -> tuple[int, str, list[str]]:
    clang = shutil.which("clang")
    nm = shutil.which("llvm-nm") or shutil.which("nm")
    require(clang is not None, "clang unavailable")
    require(nm is not None, "llvm-nm/nm unavailable")
    with tempfile.TemporaryDirectory(prefix="g2-case-register-policy-") as raw:
        output = Path(raw) / "policy.o"
        proc = subprocess.run([
            clang, "--target=thumbv6m-none-eabi", "-mthumb",
            "-mcpu=cortex-m0plus", "-std=c11", "-Oz", "-ffreestanding",
            "-fno-builtin", "-ffunction-sections", "-fdata-sections",
            "-Wall", "-Wextra", "-Werror", "-I", str(CASE), "-c",
            str(SOURCE), "-o", str(output),
        ], cwd=ROOT, capture_output=True, text=True)
        require(proc.returncode == 0, f"target compile failed: {proc.stderr}")
        nm_output = subprocess.run(
            [nm, "-g", "--defined-only", str(output)],
            check=True, capture_output=True, text=True,
        ).stdout
        symbols = []
        for line in nm_output.splitlines():
            fields = line.split()
            if len(fields) >= 3 and fields[-2].upper() in {"T", "W"}:
                symbols.append(fields[-1])
        symbols.sort()
        expected = sorted(record[3] for record in ADMISSIONS.values())
        require(symbols == expected,
                f"target exports changed: {symbols} != {expected}")
        data = output.read_bytes()
        return len(data), sha256(data), symbols


def analyze() -> dict:
    blob = BLOB.read_bytes()
    require(sha256(blob) == BLOB_SHA256, "official Case blob identity changed")
    function_map = _read_tsv(FUNCTION_MAP)
    frontier = _read_tsv(FRONTIER)
    corpus = _read_corpus()
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    prior_remaining = int(prior["metrics"]["unclassified_bytes_after"])
    require(prior_remaining == 2398, "prior Case admission tip changed")

    combined = SOURCE.read_text(encoding="utf-8") + HEADER.read_text(encoding="utf-8")
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "source license declarations changed")
    require(RAW_DIRECTIVE.search(combined) is None,
            "register-policy source contains a raw assembler encoding directive")
    require(FIXED_MMIO_CAST.search(combined) is None,
            "register-policy source embeds a fixed volatile/MMIO address")
    for path, (size, digest) in SOURCE_PINS.items():
        data = path.read_bytes()
        require(len(data) == size,
                f"source size changed: {path.relative_to(ROOT)}")
        require(sha256(data) == digest,
                f"source digest changed: {path.relative_to(ROOT)}")

    admissions = []
    for address, record in sorted(ADMISSIONS.items()):
        size, instruction_digest, decompilation_digest, symbol, contract = record
        mapped = function_map.get(address)
        require(mapped is not None, f"function-map entry missing: {address:#x}")
        require(mapped["ownership_category"] == "unresolved",
                f"function-map ownership changed: {address:#x}")
        require(int(mapped["size"], 0) == size,
                f"function-map size changed: {address:#x}")

        final = frontier.get(address)
        require(final is not None, f"final-frontier entry missing: {address:#x}")
        require(final["classification"] ==
                "project_source_candidate_not_routed",
                f"final-frontier classification changed: {address:#x}")
        require(int(final["size"], 0) == size and
                final["instruction_sha256"] == instruction_digest,
                f"final-frontier identity changed: {address:#x}")
        require(final["owner_or_contract"] ==
                "components/shared/case/runtime_case_register_policies.c" and
                final["license"] == "MIT",
                f"final-frontier source disposition changed: {address:#x}")

        evidence = corpus.get(address)
        require(evidence is not None, f"evidence corpus entry missing: {address:#x}")
        require(int(evidence["size"]) == size,
                f"evidence size changed: {address:#x}")
        require(evidence["instruction_sha256"] == instruction_digest,
                f"evidence instruction digest changed: {address:#x}")
        require(evidence["decompilation_sha256"] == decompilation_digest,
                f"evidence decompilation digest changed: {address:#x}")
        require(evidence["prior_classification"] ==
                "project_source_candidate_not_routed",
                f"evidence source classification changed: {address:#x}")

        start = WRAPPER_BYTES + address - APP_BASE
        body = blob[start:start + size]
        require(len(body) == size and sha256(body) == instruction_digest,
                f"authenticated instruction bytes changed: {address:#x}")
        require(symbol in combined, f"source symbol missing: {symbol}")
        admissions.append({
            "entry": address,
            "size": size,
            "name": mapped["name"],
            "instruction_sha256": instruction_digest,
            "decompilation_sha256": decompilation_digest,
            "contract": contract,
            "source": str(SOURCE.relative_to(ROOT)),
            "symbol": symbol,
            "license": "MIT",
            "status": "isolated_source_candidate_not_routed",
            "mmio_address_embedded": False,
            "hardware_operation": False,
        })

    admitted = sum(row["size"] for row in admissions)
    require(len(admissions) == 8 and admitted == 214,
            "register-policy admission baseline changed")
    object_size, object_digest, symbols = _target_compile()
    return {
        "schema_version": 1,
        "component": "G2 charging-case register/state policy source slice",
        "analysis_mode": (
            "offline authenticated official-image/corpus/source/build audit; "
            "caller-supplied register views; no hardware, MMIO, flash, reset, "
            "signing, routing, or deployment operation"
        ),
        "integration": "isolated source candidate; production routing absent",
        "evidence": {
            "official_blob": str(BLOB.relative_to(ROOT)),
            "official_blob_sha256": BLOB_SHA256,
            "corpus": str(CORPUS.relative_to(ROOT)),
            "authenticated_rows": len(admissions),
        },
        "source": {
            "path": str(SOURCE.relative_to(ROOT)),
            "sha256": sha256(SOURCE.read_bytes()),
            "header": str(HEADER.relative_to(ROOT)),
            "header_sha256": sha256(HEADER.read_bytes()),
            "license": "MIT",
            "target": "thumbv6m-none-eabi / Cortex-M0+ / Thumb",
            "exports": symbols,
            "raw_instruction_transcription_bytes": 0,
            "embedded_mmio_addresses": 0,
        },
        "admissions": admissions,
        "metrics": {
            "admitted_functions": len(admissions),
            "admitted_instruction_bytes": admitted,
            "authenticated_instruction_bytes": admitted,
            "unclassified_bytes_before": prior_remaining,
            "unclassified_bytes_after": prior_remaining - admitted,
            "target_object_bytes": object_size,
            "target_object_sha256": object_digest,
            "target_missing_symbols": 0,
            "raw_instruction_transcription_bytes": 0,
            "embedded_mmio_addresses": 0,
        },
        "software_source_complete": True,
        "production_routed": False,
        "hardware_validation": "deferred by project direction",
        "hardware_operations": [],
        "production_files_modified": [],
    }


def write_manifests(result: dict) -> list[Path]:
    with OUTPUT.open("w", newline="") as handle:
        fields = [
            "entry", "size", "name", "instruction_sha256",
            "decompilation_sha256", "contract", "source", "symbol",
            "license", "status", "mmio_address_embedded", "hardware_operation",
        ]
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        handle.write("# SPDX-License-Identifier: MIT\n")
        writer.writeheader()
        for row in result["admissions"]:
            output_row = dict(row)
            output_row["entry"] = f"0x{row['entry']:08X}"
            output_row["mmio_address_embedded"] = str(
                row["mmio_address_embedded"]).lower()
            output_row["hardware_operation"] = str(row["hardware_operation"]).lower()
            writer.writerow(output_row)
    summary = {key: value for key, value in result.items() if key != "admissions"}
    summary["admitted_row_count"] = len(result["admissions"])
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return [OUTPUT, SUMMARY]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(json.dumps(result["metrics"], sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Case register-policy audit failed: {exc}") from exc
