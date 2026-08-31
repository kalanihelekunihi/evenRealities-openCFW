#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the second evidence-closed charging-case register leaf family."""

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
PRIOR = ROOT / "tools/manifests/g2-case-register-primitives-admission-summary.json"
SOURCE = ROOT / "components/shared/case/runtime_case_register_transforms.c"
HEADER = ROOT / "components/shared/case/runtime_case_register_transforms.h"
MANIFEST = ROOT / "tools/manifests/g2-case-register-transforms-admission.tsv"
SUMMARY = ROOT / "tools/manifests/g2-case-register-transforms-admission-summary.json"
APP_BASE = 0x08000000
WRAPPER_BYTES = 32
BLOB_SHA256 = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"

ADMISSIONS = {
    0x08003E94: (16, "7533600672ed0b85ea80f528cc71d43f5784eea0e2549d79fb392df1eecdf467", "open_cfw_case_control_word5_set", "word 5 OR update with caller bits and bit 16"),
    0x08003ED4: (20, "6eda4e654152137182f4a4aaf10cbc30031df690e7b8faeec68a7b460aaa3a95", "open_cfw_case_flash_control_update", "word 8 clear-mask/low-byte replacement and two set masks"),
    0x080067A2: (14, "4fc4c5fde1161433cc305108b5f3095a1b9aa18e1bd59cdae53c5102f2197196", "open_cfw_case_control_word0_replace_field22", "word 0 bits 22..24 replacement"),
    0x080067B0: (22, "912c8fd271d215b906fc6ef21c377fed0876721e3e2cc3f5e96c5455c1b37289", "open_cfw_case_control_word5_replace_slot", "word 5 three-bit slot replacement at shift 0 or 4"),
    0x0800A3BA: (24, "c72df4f29df65fa0e03ef2ee0066001c29c3262a85ba4dc07b1d7315fe1ccb4f", "open_cfw_case_sign_extend_u16", "16-bit sign extension"),
}

SOURCE_PINS = {
    SOURCE: (1615, "963150b4aa2d544136ae541d788aaea52489cb917aa2ae5540b2ad4641fefa03"),
    HEADER: (674, "19c9315931c1de71b30b50d1d30473d479b7328340ec0d9c1654856ce65040e1"),
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
    return {
        fields[-1]
        for line in output.splitlines()
        if len(fields := line.split()) >= 3 and fields[-2].upper() in {"T", "W"}
    }


def _target_compile() -> tuple[int, str, list[str]]:
    clang = shutil.which("clang")
    nm = shutil.which("llvm-nm") or shutil.which("nm")
    require(clang is not None and nm is not None, "clang/nm unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-case-transform-audit-") as raw:
        output = Path(raw) / "case-transform.o"
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
        require(symbols == expected, f"target exports changed: {sorted(symbols)}")
        data = output.read_bytes()
        return len(data), sha256(data), sorted(symbols)


def analyze() -> dict:
    blob = BLOB.read_bytes()
    require(sha256(blob) == BLOB_SHA256, "case blob identity changed")
    app = blob[WRAPPER_BYTES:]
    function_rows = _read_map()
    prior = json.loads(PRIOR.read_text())
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "source license declarations changed")
    for path, (size, digest) in SOURCE_PINS.items():
        data = path.read_bytes()
        require(len(data) == size and sha256(data) == digest,
                f"source identity changed: {path.relative_to(ROOT)}")

    rows = []
    for entry, (size, digest, symbol, contract) in sorted(ADMISSIONS.items()):
        mapped = function_rows.get(entry)
        require(mapped is not None, f"function-map entry missing: {entry:#x}")
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
    before = int(prior["metrics"]["unclassified_bytes_after"])
    require(before == 16950, "prior case admission tip changed")
    require(admitted_bytes == 96, "admitted-byte total changed")
    return {
        "schema_version": 1,
        "component": "G2 charging-case register transforms",
        "analysis_mode": "offline authenticated instruction/source/build audit; caller-supplied register views; no hardware, MMIO, flash, reset, signing, or deployment operation",
        "metrics": {
            "admitted_functions": len(rows),
            "admitted_instruction_bytes": admitted_bytes,
            "unclassified_bytes_before": before,
            "unclassified_bytes_after": before - admitted_bytes,
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
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
        "hardware_note": "software-only admission; directed hardware work is outside the current project phase",
    }


def write_manifests(result: dict) -> list[Path]:
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
    print(f"case register transforms: {result['metrics']['admitted_functions']}")
    print(f"admitted instruction bytes: {result['metrics']['admitted_instruction_bytes']}")
    print(f"unclassified bytes remaining: {result['metrics']['unclassified_bytes_after']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Case register transform admission failed: {exc}") from exc
