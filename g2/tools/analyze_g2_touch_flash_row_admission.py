#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the evidence-closed Touch flash-row adapters (batch 19)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
PRIOR = TOOLS / "analyze_g2_touch_startup_closed_admission.py"
PREFIX = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_flash_row_adapters.c"
HEADER = TOUCH / "runtime_touch_flash_row_adapters.h"

ADMISSIONS = {
    0x14B0: ("zero_filled_128_byte_row_writer",
             "open_cfw_touch_flash_14b0_zero_rows",
             "eeecfab26b6a7b414228932baa8265cc72b6ddb2c12218d046fdabc61cd39f53",
             86, {0x1488, 0x5A50, 0x74CC, 0x76D4}),
    0x1510: ("source_backed_128_byte_row_writer",
             "open_cfw_touch_flash_1510_copy_rows",
             "26c3d79b962a2bf8fb1ea26b487d9d0faeea248178b7611b3a062ac8f37debea",
             74, {0x1484, 0x5A50, 0x74CC}),
    0x1560: ("bounded_memcpy_callback",
             "open_cfw_touch_flash_1560_copy_callback",
             "9a67c4f814c6daaf7d230e3d98f944198255ec9bc2b653d3ff514f75326320df",
             12, {0x772C}),
}

EXPECTED = {
    "input_concrete_gap": 50, "input_gap_instruction_bytes": 4722,
    "admitted_functions": 3, "admitted_instruction_bytes": 172,
    "resident_table_admissions": 0, "mmio_admissions": 0,
    "unimplemented_application_contracts_before": 38,
    "unimplemented_application_contracts_after": 35,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 47,
    "residual_gap_instruction_bytes": 4550,
    "row_digest": "92391760e1e1e88ee3e7f59b92fd72ea77086a067cb5e0dc3bd453a423e990eb",
    "residual_digest": "8d8cf5a618dc9d6b80d8b82c4c01905e1b9ec827057266244cf270f52f6cf023",
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _target_compile() -> int:
    clang = shutil.which("clang")
    require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory() as raw:
        output = Path(raw) / "touch-flash-row.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0, f"flash-row target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected: bool = True) -> dict:
    prior_mod = _load(PRIOR, "touch_flash_row_batch18")
    prefix = _load(PREFIX, "touch_flash_row_prefix")
    prior = prior_mod.analyze()
    residual = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual.keys(),
            "flash-row family escaped batch-18 residual")
    require(all(residual[e]["family"] in
                ("platform_startup_configuration", "touch_application_processing")
                for e in ADMISSIONS), "flash-row family crossed provider boundary")
    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(residual)
    for _kind, _symbol, _digest, _size, callees in ADMISSIONS.values():
        entries.update(callees)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "flash-row MIT declarations changed")
    require("0x06160002" in combined,
            "authenticated row-alignment status changed")
    target_bytes = _target_compile()
    rows = []
    for entry, (kind, symbol, digest, byte_count, expected_calls) in sorted(ADMISSIONS.items()):
        body = prefix._walk(payload, entry, entries)
        canonical = "|".join(f"{a:04X}:{i.mnemonic} {i.op_str}"
                             for a, i in sorted(body["instructions"].items()))
        calls = {call["target"] for call in body["calls"]}
        require(sha256(canonical.encode()) == digest,
                f"flash-row body changed at {entry:#x}")
        require(calls == expected_calls,
                f"flash-row calls changed at {entry:#x}: {sorted(calls)}")
        require(residual[entry]["instruction_bytes"] == byte_count,
                f"flash-row byte span changed at {entry:#x}")
        require(symbol in combined, f"flash-row source symbol missing: {symbol}")
        rows.append({
            "entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_flash_row_adapter_source", "license": "MIT",
            "source": SOURCE.name, "direct_callees": sorted(calls),
            "provider_license": "Apache-2.0 CAT2 PDL or selected C runtime",
            "resident_table_dependency": False, "mmio_execution": False,
            "instruction_bytes": byte_count,
            "instruction_sha256": residual[entry]["instruction_sha256"],
            "canonical_body_sha256": digest,
            "evidence": "complete 128-byte row iteration or bounded copy flow; Cy_Flash_WriteRow remains an injected Apache-2.0 provider; no EULA body, resident table, MMIO execution or product policy admitted",
        })
    residual_rows = [row for entry, row in sorted(residual.items())
                     if entry not in ADMISSIONS]
    metrics = {
        "input_concrete_gap": len(residual),
        "input_gap_instruction_bytes": sum(r["instruction_bytes"] for r in residual.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(r["instruction_bytes"] for r in rows),
        "resident_table_admissions": 0, "mmio_admissions": 0,
        "unimplemented_application_contracts_before": sum(
            r["family"] in ("platform_startup_configuration", "touch_application_processing")
            for r in residual.values()),
        "unimplemented_application_contracts_after": sum(
            r["family"] in ("platform_startup_configuration", "touch_application_processing")
            for r in residual_rows),
        "typed_external_or_unavailable_functions": sum(
            r["family"] in ("emeeprom_eula", "system_handoff_mixed", "legacy_halt")
            for r in residual_rows),
        "concrete_source_or_implementation_gap_after": len(residual_rows),
        "residual_gap_instruction_bytes": sum(r["instruction_bytes"] for r in residual_rows),
        "row_digest": sha256(json.dumps(rows, sort_keys=True,
                                           separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(residual_rows, sort_keys=True,
                                                separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, value in EXPECTED.items():
            require(metrics[key] == value,
                    f"flash-row {key} changed: {metrics[key]!r} != {value!r}")
    return {
        "schema_version": 1, "authoritative_batch": 19,
        "hardware_validation": "blocked by unavailable physical evidence",
        "component": "G2 touch flash-row admission batch 19",
        "analysis_mode": "offline authenticated flow, typed Apache/runtime seams, host and Cortex-M0+ compile; no hardware/MMIO execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
                   "sha256": sha256(SOURCE.read_bytes()),
                   "target_closure_object_bytes": target_bytes},
        "integration": "isolated source candidate only; not production-routed",
        "remaining": {"concrete_source_or_implementation_functions": len(residual_rows),
                      "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
                      "unimplemented_clean_room_application_contracts": metrics["unimplemented_application_contracts_after"],
                      "typed_external_or_unavailable_functions": 12},
        "exclusions": "all EULA bodies, resident tables/loaders, 0x1B6C/0x1C54/0x2638, system handoff and halt remain unadmitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-flash-row-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license", "source",
                         "direct_callees", "provider_license", "resident_table_dependency",
                         "mmio_execution", "instruction_bytes", "instruction_sha256",
                         "canonical_body_sha256", "evidence"])
        for r in result["rows"]:
            writer.writerow([f"0x{r['entry']:04X}", r["symbol"], r["kind"], r["status"],
                             r["license"], r["source"],
                             ",".join(f"0x{x:04X}" for x in r["direct_callees"]),
                             r["provider_license"], str(r["resident_table_dependency"]).lower(),
                             str(r["mmio_execution"]).lower(), r["instruction_bytes"],
                             r["instruction_sha256"], r["canonical_body_sha256"], r["evidence"]])
    residual = MANIFEST_DIR / "g2-touch-flash-row-residual.tsv"
    with residual.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "family", "status", "license", "concrete_source",
                         "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for r in result["residual_rows"]:
            writer.writerow([f"0x{r['entry']:04X}", r["family"], r["status"], r["license"],
                             str(r["concrete_source"]).lower(), str(r["implemented"]).lower(),
                             r["instruction_bytes"], r["instruction_sha256"], r["reason"]])
    summary = MANIFEST_DIR / "g2-touch-flash-row-admission-summary.json"
    slim = {k: v for k, v in result.items() if k not in ("rows", "residual_rows")}
    slim["admitted_row_count"] = len(result["rows"])
    slim["residual_row_count"] = len(result["residual_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [admitted, residual, summary]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(f"flash-row sources: {result['metrics']['admitted_functions']}")
    print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch flash-row admission failed: {exc}") from exc
