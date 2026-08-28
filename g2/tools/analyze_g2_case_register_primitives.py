#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit evidence-closed charging-case register leaf primitives."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_box.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-box-function-map.tsv"
FUNCTION_SUMMARY = ROOT / "tools/manifests/g2-box-function-map-summary.json"
SOURCE = ROOT / "components/shared/case/runtime_case_register_primitives.c"
HEADER = ROOT / "components/shared/case/runtime_case_register_primitives.h"
MANIFEST = ROOT / "tools/manifests/g2-case-register-primitives-admission.tsv"
SUMMARY = ROOT / "tools/manifests/g2-case-register-primitives-admission-summary.json"
APP_BASE = 0x08000000
WRAPPER_BYTES = 32
BLOB_SHA256 = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"

# entry: (size, instruction-byte SHA-256, source symbol, semantic contract)
ADMISSIONS = {
    0x08003EA8: (18, "e0a2fefd7f2126873ac445909d136138f2bebc0021b012427305c48f9657b673", "open_cfw_case_flash_status_classify", "low-byte 0xAA/0xCC acceptance, otherwise 0xBB"),
    0x08003EC0: (10, "aa05e4fdd78fcb7adc2ab80a2034cc34e1af95280fe398b5b77e25bf725d3191", "open_cfw_case_flash_status_masked", "status word 8 masked by 0x077F6000"),
    0x08004328: (6, "a2a14b78d9dbf21beecef82b0c28833fe79269c2c9c6a03579e4ce397d9b7506", "open_cfw_case_handle_word16", "indirect handle word 16 read"),
    0x08004E94: (10, "5dec2b510091957cd310155535f989998e09b1bda69697f9ddacdea44fbd9024", "open_cfw_case_register_any_bits", "word 4 masked nonzero predicate"),
    0x08004E9E: (12, "249cd8559567dea2085da166fd295e516469beb26a4114fee4bd90a65f3b5cad", "open_cfw_case_register_write_channel", "selector chooses word 6 or word 10 write"),
    0x08004EAC: (6, "f9e9ed7deab97ba770020418c839a3824257d2e29c2f736e873b7a50a3efaeb8", "open_cfw_case_tick_word2", "global timing-state word 2 read"),
    0x08004EB8: (6, "895117144ca352baa99d948bb32fc9b248631e995c4d281cb77b6ddb3e9ce023", "open_cfw_case_device_info_word4", "device-information word 4 read"),
    0x08004EC4: (6, "2eff6063dea135fb41d902919548885c3ba486df44d32f50edfd77f765a2b127", "open_cfw_case_device_info_word5", "device-information word 5 read"),
    0x08004ED0: (6, "0894173b4e7a6a728281b8d682734935f48057b84f831256ceb9fd35c9a13825", "open_cfw_case_device_info_word6", "device-information word 6 read"),
    0x0800677A: (8, "a08d5225eca642a91a63cb3e0c488eed61dadd7d3db68a3ae0efcf3a931dd180", "open_cfw_case_status_word2_bit0", "status word 2 bit 0 read"),
    0x08006782: (8, "a08d5225eca642a91a63cb3e0c488eed61dadd7d3db68a3ae0efcf3a931dd180", "open_cfw_case_status_word2_bit0_alias", "second status word 2 bit 0 entry"),
    0x0800678A: (8, "f26fb9fd9d7e8a79514fe21f4732e5ef0437ea869d21a52e7a48f3bc1fa83cb6", "open_cfw_case_status_word2_bit2", "status word 2 bit 2 read"),
    0x08006792: (16, "619b07e7428ce83e04b1676d11703951ad12ffad58ad8bf8018d5f089236d5db", "open_cfw_case_status_word3_field10_clear", "status word 3 bits 10..11 clear predicate"),
}

SOURCE_PINS = {
    SOURCE: (2630, "5807d154e9401f8d8ce176ed24d675899c59abb97b00bcfcd78c4e0fec41270a"),
    HEADER: (1315, "ae13943525cde3e1ee5f2920bdfc42304da8c66f5f0a9348d34377d951e04f72"),
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_map() -> dict[int, dict[str, str]]:
    with FUNCTION_MAP.open(newline="") as handle:
        reader = csv.DictReader(
            (line for line in handle if not line.startswith("#")), delimiter="\t")
        return {int(row["entry"], 0): row for row in reader}


def _defined_symbols(nm: str, obj: Path) -> set[str]:
    output = subprocess.run(
        [nm, "-g", str(obj)], check=True, capture_output=True, text=True).stdout
    result = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[-2].upper() in {"T", "W"}:
            result.add(fields[-1])
    return result


def _target_compile() -> tuple[int, str, list[str]]:
    clang = shutil.which("clang")
    nm = shutil.which("llvm-nm") or shutil.which("nm")
    require(clang is not None, "clang unavailable")
    require(nm is not None, "nm unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-case-register-audit-") as raw:
        output = Path(raw) / "case-register.o"
        proc = subprocess.run([
            clang, "--target=thumbv6m-none-eabi", "-mthumb",
            "-mcpu=cortex-m0plus", "-O2", "-ffreestanding", "-fno-builtin",
            "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
            "-Werror", "-I" + str(SOURCE.parent), "-c", str(SOURCE),
            "-o", str(output),
        ], cwd=ROOT, capture_output=True, text=True)
        require(proc.returncode == 0, f"target compile failed: {proc.stderr}")
        symbols = _defined_symbols(nm, output)
        expected = {row[2] for row in ADMISSIONS.values()}
        require(symbols == expected,
                f"target exports changed: {sorted(symbols)} != {sorted(expected)}")
        data = output.read_bytes()
        return len(data), sha256(data), sorted(symbols)


def analyze() -> dict:
    blob = BLOB.read_bytes()
    require(sha256(blob) == BLOB_SHA256, "case blob identity changed")
    app = blob[WRAPPER_BYTES:]
    function_rows = _read_map()
    function_summary = json.loads(FUNCTION_SUMMARY.read_text())
    combined = SOURCE.read_text() + HEADER.read_text()

    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "source license declarations changed")
    for path, (size, digest) in SOURCE_PINS.items():
        data = path.read_bytes()
        require(len(data) == size, f"source size changed: {path.relative_to(ROOT)}")
        require(sha256(data) == digest,
                f"source digest changed: {path.relative_to(ROOT)}")

    rows = []
    for entry, (size, digest, symbol, contract) in sorted(ADMISSIONS.items()):
        require(entry in function_rows, f"function-map entry missing: {entry:#x}")
        mapped = function_rows[entry]
        require(mapped["ownership_category"] == "unresolved",
                f"entry is no longer unresolved: {entry:#x}")
        require(int(mapped["size"], 0) == size,
                f"function size changed at {entry:#x}")
        body = app[entry - APP_BASE:entry - APP_BASE + size]
        require(len(body) == size and sha256(body) == digest,
                f"instruction bytes changed at {entry:#x}")
        require(symbol in combined, f"source symbol missing: {symbol}")
        rows.append({
            "entry": entry, "size": size, "instruction_sha256": digest,
            "symbol": symbol, "contract": contract,
            "status": "clean_room_compilable_c_candidate",
            "license": "MIT",
            "source": str(SOURCE.relative_to(ROOT)),
            "mmio_execution": False, "destructive_operation": False,
        })

    object_bytes, object_digest, exports = _target_compile()
    admitted_bytes = sum(row["size"] for row in rows)
    categories = function_summary["map"]["combined_category_bytes"]
    require(categories["unresolved"] == 17070,
            "case unresolved byte baseline changed")
    require(admitted_bytes == 120, "admitted-byte total changed")
    return {
        "schema_version": 1,
        "component": "G2 charging-case register leaf primitives",
        "analysis_mode": "offline authenticated instruction/source/build audit; caller-supplied register views; no hardware, MMIO, flash, reset, signing, or deployment operation",
        "metrics": {
            "admitted_functions": len(rows),
            "admitted_instruction_bytes": admitted_bytes,
            "unclassified_bytes_before": categories["unresolved"],
            "unclassified_bytes_after": categories["unresolved"] - admitted_bytes,
            "target_object_bytes": object_bytes,
            "target_object_sha256": object_digest,
        },
        "source": {
            "path": str(SOURCE.relative_to(ROOT)),
            "sha256": sha256(SOURCE.read_bytes()),
            "license": "MIT",
            "target": "thumbv6m-none-eabi / Cortex-M0+ / Thumb",
            "exports": exports,
        },
        "rows": rows,
        "integration": "isolated source candidate only; platform MMIO adapter and image routing remain open",
        "production_routed": False,
        "hardware_validation": "deferred by project direction",
        "hardware_operations": [],
        "hardware_note": "software-only admission; directed hardware work is outside the current project phase",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "entry", "size", "instruction_sha256", "symbol", "contract",
            "status", "license", "source", "mmio_execution",
            "destructive_operation",
        ])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:08X}", row["size"],
                row["instruction_sha256"], row["symbol"], row["contract"],
                row["status"], row["license"], row["source"],
                str(row["mmio_execution"]).lower(),
                str(row["destructive_operation"]).lower(),
            ])
    summary = {key: value for key, value in result.items() if key != "rows"}
    summary["admitted_row_count"] = len(result["rows"])
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return [MANIFEST, SUMMARY]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(f"case register primitives: {result['metrics']['admitted_functions']}")
    print(f"admitted instruction bytes: {result['metrics']['admitted_instruction_bytes']}")
    print(f"unclassified bytes remaining: {result['metrics']['unclassified_bytes_after']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Case register primitive admission failed: {exc}") from exc
