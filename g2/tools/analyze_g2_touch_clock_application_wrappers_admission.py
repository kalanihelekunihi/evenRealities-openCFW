#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit Touch clock and application wrapper contracts (batch 22)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
PRIOR = TOOLS / "analyze_g2_touch_platform_wrappers_admission.py"
PREFIX = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_clock_application_wrappers.c"
HEADER = TOUCH / "runtime_touch_clock_application_wrappers.h"

# kind, symbol, canonical digest, instruction bytes, direct callees
ADMISSIONS = {
    0x12AC: (
        "clock_divider_validation_wrapper",
        "open_cfw_touch_clock_12ac_validate",
        "2b89b3915e08b403bad1d70f45bd50fb568552197d713b81f2a0c2cde1871355",
        32, {0x12A6, 0x6C44},
    ),
    0x12D0: (
        "clock_transition_orchestrator",
        "open_cfw_touch_clock_12d0_transition",
        "838977da5996485da5a5ce9e811381ad079525a48ab76b9ed31e087b90e18ce6",
        88, {0x12AC, 0x1434, 0x6980, 0x6C44, 0x6E88, 0x703C},
    ),
    0x1434: (
        "clock_calibration_state_writer",
        "open_cfw_touch_clock_1434_calibrate",
        "fdf5a2b96e24b71316663954de8cf39fd73f171c0dd65f09637f740e35cc5df4",
        54, {0x13F8, 0x73C0},
    ),
    0x17BE: (
        "application_preflight_wrapper",
        "open_cfw_touch_application_17be_preflight",
        "ab9b803f198a89091d625b2cc7e6b07f567bab9db74da5cf07db1fa01eda7ac2",
        52, {0x25F8, 0x3EC8, 0x4A92, 0x4B04},
    ),
    0x1904: (
        "three_object_processing_wrapper",
        "open_cfw_touch_application_1904_process_three",
        "6cfc38f6fd73de1ba0c4e3846af8ddb98020de85c17dd0469a10f236d46eaf0e",
        64, {0x18A8, 0x4ADE},
    ),
    0x1C54: (
        "three_pointer_update_wrapper",
        "open_cfw_touch_application_1c54_update_three",
        "396c8dc7d7403c45eea76b0c8ab995746b593be2739a587f6b9edc4aef5f8a47",
        26, {0x1B6C},
    ),
}

SOURCE_PINS = {
    SOURCE: (5728, "1a3d243e50dfcef1dd9eb276bf72f5af5c67229994cb417bcf20e86109b80ee9"),
    HEADER: (2527, "fbfe99bc13a94d1a997db7885b6d4c5dbba4eb4d9a05a54ba70c1547f7a6b613"),
}

EXPECTED = {
    "input_concrete_gap": 31,
    "input_gap_instruction_bytes": 4180,
    "admitted_functions": 6,
    "admitted_instruction_bytes": 316,
    "fixed_address_accesses": 0,
    "mmio_executions": 0,
    "unimplemented_application_contracts_before": 19,
    "unimplemented_application_contracts_after": 13,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 25,
    "residual_gap_instruction_bytes": 3864,
}


class AuditError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _target_compile():
    clang = shutil.which("clang")
    require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-touch-clock-app-audit-") as raw:
        output = Path(raw) / "touch-clock-app.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0,
                f"clock/application target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected=True):
    prior_mod = _load(PRIOR, "touch_clock_app_batch21")
    prefix = _load(PREFIX, "touch_clock_app_prefix")
    prior = prior_mod.analyze()
    residual = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual.keys(),
            "clock/application wrappers escaped batch-21 residual")
    payload = prefix.BLOB.read_bytes()[
        prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(residual)
    for _kind, _symbol, _digest, _bytes, calls in ADMISSIONS.values():
        entries.update(calls)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "MIT declarations changed")
    require("0x400" not in SOURCE.read_text() and "0xE000" not in SOURCE.read_text(),
            "fixed peripheral address entered clean-room source")
    for path, (size, digest) in SOURCE_PINS.items():
        data = path.read_bytes()
        require(len(data) == size and sha256(data) == digest,
                f"source identity changed: {path.relative_to(ROOT)}")
    target_bytes = _target_compile()
    rows = []
    for entry, (kind, symbol, digest, byte_count, expected_calls) in sorted(
            ADMISSIONS.items()):
        body = prefix._walk(payload, entry, entries)
        canonical = "|".join(
            f"{address:04X}:{insn.mnemonic} {insn.op_str}"
            for address, insn in sorted(body["instructions"].items()))
        calls = {call["target"] for call in body["calls"]}
        require(sha256(canonical.encode()) == digest,
                f"body changed at {entry:#x}")
        require(calls == expected_calls, f"calls changed at {entry:#x}")
        require(residual[entry]["instruction_bytes"] == byte_count,
                f"span changed at {entry:#x}")
        require(symbol in combined, f"source symbol missing: {symbol}")
        rows.append({
            "entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_injected_wrapper_source", "license": "MIT",
            "source": SOURCE.name, "direct_callees": sorted(calls),
            "caller_supplied_register_view": entry in (0x12AC, 0x12D0),
            "injected_provider_contract": True,
            "fixed_address_access": False, "mmio_execution": False,
            "instruction_bytes": byte_count,
            "instruction_sha256": residual[entry]["instruction_sha256"],
            "canonical_body_sha256": digest,
            "evidence": "complete authenticated wrapper flow represented by caller-owned state and injected providers; no fixed-address dereference, live MMIO, vendor body, resident table, reset, flash, or product loop execution",
        })
    residual_rows = [
        row for entry, row in sorted(residual.items()) if entry not in ADMISSIONS]
    is_app = lambda row: row["family"] in (
        "platform_startup_configuration", "touch_application_processing")
    is_external = lambda row: row["family"] in (
        "emeeprom_eula", "system_handoff_mixed", "legacy_halt")
    metrics = {
        "input_concrete_gap": len(residual),
        "input_gap_instruction_bytes": sum(
            row["instruction_bytes"] for row in residual.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(
            row["instruction_bytes"] for row in rows),
        "fixed_address_accesses": 0, "mmio_executions": 0,
        "unimplemented_application_contracts_before": sum(
            map(is_app, residual.values())),
        "unimplemented_application_contracts_after": sum(
            map(is_app, residual_rows)),
        "typed_external_or_unavailable_functions": sum(
            map(is_external, residual_rows)),
        "concrete_source_or_implementation_gap_after": len(residual_rows),
        "residual_gap_instruction_bytes": sum(
            row["instruction_bytes"] for row in residual_rows),
        "row_digest": sha256(json.dumps(
            rows, sort_keys=True, separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(
            residual_rows, sort_keys=True, separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, value in EXPECTED.items():
            require(metrics[key] == value,
                    f"clock/application {key} changed: {metrics[key]!r} != {value!r}")
    return {
        "schema_version": 1,
        "component": "G2 Touch clock/application wrapper admission batch 22",
        "analysis_mode": "offline authenticated flow with injected providers and caller-owned register views; host and Cortex-M0+ compile; no hardware/MMIO execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {
            "path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
            "sha256": sha256(SOURCE.read_bytes()),
            "target_closure_object_bytes": target_bytes,
        },
        "integration": "isolated source candidate only; not production-routed",
        "remaining": {
            "concrete_source_or_implementation_functions": len(residual_rows),
            "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
            "unimplemented_clean_room_application_contracts": metrics[
                "unimplemented_application_contracts_after"],
            "typed_external_or_unavailable_functions": 12,
        },
        "hardware_validation": "deferred by project direction",
        "hardware_blocker": "deferred by project direction",
        "exclusions": "all EULA bodies, product main loop, resident table loaders, unresolved pointer-table implementations, system handoff, and halt remain unadmitted",
    }


def write_manifests(result):
    admitted = MANIFEST_DIR / "g2-touch-clock-application-wrappers-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license",
                         "source", "direct_callees", "caller_supplied_register_view",
                         "injected_provider_contract", "fixed_address_access",
                         "mmio_execution", "instruction_bytes", "instruction_sha256",
                         "canonical_body_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["symbol"], row["kind"],
                row["status"], row["license"], row["source"],
                ",".join(f"0x{x:04X}" for x in row["direct_callees"]),
                str(row["caller_supplied_register_view"]).lower(),
                str(row["injected_provider_contract"]).lower(),
                str(row["fixed_address_access"]).lower(),
                str(row["mmio_execution"]).lower(), row["instruction_bytes"],
                row["instruction_sha256"], row["canonical_body_sha256"],
                row["evidence"],
            ])
    residual = MANIFEST_DIR / "g2-touch-clock-application-wrappers-residual.tsv"
    with residual.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "family", "status", "license",
                         "concrete_source", "implemented", "instruction_bytes",
                         "instruction_sha256", "reason"])
        for row in result["residual_rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["family"], row["status"],
                row["license"], str(row["concrete_source"]).lower(),
                str(row["implemented"]).lower(), row["instruction_bytes"],
                row["instruction_sha256"], row["reason"],
            ])
    summary = MANIFEST_DIR / "g2-touch-clock-application-wrappers-admission-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("rows", "residual_rows")}
    slim["admitted_row_count"] = len(result["rows"])
    slim["residual_row_count"] = len(result["residual_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    # This admission summary is intentionally not the authoritative whole-blob
    # classification.  Only analyze_g2_touch_final_frontier.py may publish the
    # shared current-readiness summary after it composes this batch with the
    # exhaustive physical-byte partition.
    return [admitted, residual, summary]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(f"clock/application wrapper sources: {result['metrics']['admitted_functions']}")
    print(f"remaining concrete source/implementation gap: {len(result['residual_rows'])}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch clock/application wrapper admission failed: {exc}") from exc
