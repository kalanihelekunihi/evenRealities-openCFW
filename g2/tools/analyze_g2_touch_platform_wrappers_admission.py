#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit Touch platform wrapper contracts (batch 21)."""

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
PRIOR = TOOLS / "analyze_g2_touch_terminal_wrappers_admission.py"
PREFIX = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_platform_wrappers.c"
HEADER = TOUCH / "runtime_touch_platform_wrappers.h"

# kind, symbol, canonical digest, instruction bytes, direct callees
ADMISSIONS = {
    0x0324: ("fixed_pair_configuration_wrapper", "open_cfw_touch_platform_0324_configure", "79873d0f5ff50ab8fc69aa915d04e64d783ca852e331c9bded08a12b446f2754", 12, {0x680C}),
    0x0338: ("callback_install_wrapper", "open_cfw_touch_platform_0338_install", "a3b5211c8eee299aa21d87ac1ee8a3f15dfb0d419cb2b59cd79b0515fc9b3c97", 24, {0x7350, 0x73A8}),
    0x0358: ("halfword_sample_wrapper", "open_cfw_touch_platform_0358_sample", "91339171589435147b895e24f582896951e8727cf2e143e8747ea2c98fb606cd", 22, {0x0D4C}),
    0x0648: ("capsense_configuration_wrapper", "open_cfw_touch_platform_0648_configure", "53b5c81d85190b86aea8c40866413c1bd5211fbcbb0d6f014fcd43b9e4d369be", 12, {0x2998}),
    0x09A4: ("power_callback_start_wrapper", "open_cfw_touch_platform_09a4_start", "ea646be64fbbdb0d4674ea659776d73c29d1c82d8c2cb6536d2c09f2f1940bb7", 10, {0x70B0}),
    0x11A0: ("four_stage_startup_wrapper", "open_cfw_touch_platform_11a0_sequence", "70db2b4a55aee79f230d02cba1c9492dad64bbd3d7a6c016a602fbd6a2aa1a59", 20, {0x12D0, 0x11D0, 0x1228, 0x1238}),
    0x11C4: ("five_stage_startup_wrapper", "open_cfw_touch_platform_11c4_sequence", "d974bfc727d837bcdb3c5aa3a9fc1fd4169a87d9b1d45f77378a4a07ede326a9", 12, {0x11A0, 0x11B4}),
    0x1238: ("six_route_configuration_wrapper", "open_cfw_touch_platform_1238_routes", "399ad3bdc934e3346359b50a5b9132868ce7fd6d105272afa5af684f423db268", 70, {0x5BE4}),
    0x1334: ("power_probe_wrapper", "open_cfw_touch_platform_1334_probe", "3e7aec7705bcfc5e877f1fac2531f9b1610c72f24109917d3a65933cd33fb0c0", 20, {0x70B0}),
    0x1350: ("startup_and_probe_wrapper", "open_cfw_touch_platform_1350_initialize", "78fad1737e652a6b9934e7312709d4cd8d5e5ec3ef8b54a656315b9d4ed65fa6", 12, {0x11C4, 0x1334}),
    0x13F8: ("rounded_clock_measurement_wrapper", "open_cfw_touch_platform_13f8_rounded_measurement", "49a4c85d6edea896b1f0c7f5c7dfde8e2b176f28dd7e956f9a5cedfb4df1fa74", 28, {0x6C9C}),
    0x156C: ("callback_record_initializer", "open_cfw_touch_platform_156c_record_init", "6fa1a2ba46dcf90d5cc2d2d766316e591e2bf2d78a2da9ddccd6a0d70eb2070e", 56, set()),
}

SOURCE_PINS = {
    SOURCE: (4722, "20b561b07817df5a49eaafde9898e5af9b44eca1b2b7cbe015233c1323288863"),
    HEADER: (2170, "ded26f5282923836c9f34cbdd165ed9b1a00ada7b620bce6717e3631771fbdba"),
}

EXPECTED = {
    "input_concrete_gap": 43,
    "input_gap_instruction_bytes": 4478,
    "admitted_functions": 12,
    "admitted_instruction_bytes": 298,
    "resident_table_admissions": 0,
    "mmio_admissions": 0,
    "unimplemented_application_contracts_before": 31,
    "unimplemented_application_contracts_after": 19,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 31,
    "residual_gap_instruction_bytes": 4180,
    "row_digest": "f9a115127e1dbdea2748b75e35c98c1130edf4474c0759beff2607782f691291",
    "residual_digest": "988eb3b5678eea013104d0dcaa75d4ee8c157f656d11dbfbd556f256ccde96f7",
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
    with tempfile.TemporaryDirectory(prefix="open-cfw-touch-platform-audit-") as raw:
        output = Path(raw) / "touch-platform.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0,
                f"platform wrapper target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected=True):
    prior_mod = _load(PRIOR, "touch_platform_batch20")
    prefix = _load(PREFIX, "touch_platform_prefix")
    prior = prior_mod.analyze()
    residual = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual.keys(),
            "platform wrappers escaped batch-20 residual")
    payload = prefix.BLOB.read_bytes()[
        prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(residual)
    for _kind, _symbol, _digest, _bytes, calls in ADMISSIONS.values():
        entries.update(calls)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "MIT declarations changed")
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
            "status": "clean_room_platform_wrapper_source", "license": "MIT",
            "source": SOURCE.name, "direct_callees": sorted(calls),
            "eula_provider_body_admitted": False,
            "resident_table_dependency": False, "mmio_execution": False,
            "instruction_bytes": byte_count,
            "instruction_sha256": residual[entry]["instruction_sha256"],
            "canonical_body_sha256": digest,
            "evidence": "complete wrapper flow with fixed tokens and injected providers; no vendor body, resident table, fixed-address access, MMIO execution, reset, or product loop admitted",
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
        "resident_table_admissions": 0, "mmio_admissions": 0,
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
                    f"platform wrapper {key} changed: {metrics[key]!r} != {value!r}")
    return {
        "schema_version": 1,
        "component": "G2 Touch platform wrapper admission batch 21",
        "analysis_mode": "offline authenticated flow with injected providers; host and Cortex-M0+ compile; no hardware/MMIO execution",
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
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_blocker": "blocked by unavailable physical evidence",
        "exclusions": "all EULA bodies, direct-MMIO clock transitions, product main loop, resident table loaders, pointer-table ABIs, system handoff, and halt remain unadmitted",
    }


def write_manifests(result):
    admitted = MANIFEST_DIR / "g2-touch-platform-wrappers-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license",
                         "source", "direct_callees", "eula_provider_body_admitted",
                         "resident_table_dependency", "mmio_execution",
                         "instruction_bytes", "instruction_sha256",
                         "canonical_body_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["symbol"], row["kind"],
                row["status"], row["license"], row["source"],
                ",".join(f"0x{x:04X}" for x in row["direct_callees"]),
                str(row["eula_provider_body_admitted"]).lower(),
                str(row["resident_table_dependency"]).lower(),
                str(row["mmio_execution"]).lower(), row["instruction_bytes"],
                row["instruction_sha256"], row["canonical_body_sha256"],
                row["evidence"],
            ])
    residual = MANIFEST_DIR / "g2-touch-platform-wrappers-residual.tsv"
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
    summary = MANIFEST_DIR / "g2-touch-platform-wrappers-admission-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("rows", "residual_rows")}
    slim["admitted_row_count"] = len(result["rows"])
    slim["residual_row_count"] = len(result["residual_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [admitted, residual, summary]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(f"platform wrapper sources: {result['metrics']['admitted_functions']}")
    print(f"remaining concrete source/implementation gap: {len(result['residual_rows'])}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch platform wrapper admission failed: {exc}") from exc
