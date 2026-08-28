#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the provider-closed Touch application core (batch 23)."""

from __future__ import annotations

import argparse, csv, hashlib, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
PRIOR = TOOLS / "analyze_g2_touch_clock_application_wrappers_admission.py"
PREFIX = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_application_core.c"
HEADER = TOUCH / "runtime_touch_application_core.h"

# kind, symbol, canonical digest, instruction bytes, direct callees
ADMISSIONS = {
    0x17F4: (
        "top_level_application_run", "open_cfw_touch_application_17f4_run",
        "7bb30e381c7e49e345aecfdd31b26d8186a42d572d621be784cd9320ac56fc22",
        172, {0x17BE, 0x1B1C, 0x1C54, 0x2902, 0x297A, 0x298E,
              0x29A2, 0x2CA4, 0x37C0, 0x48B8, 0x73C0},
    ),
    0x18A8: (
        "per_object_application_processor",
        "open_cfw_touch_application_18a8_process",
        "8db9702937fc0efe8e74afd1187408e014900a7c978cf4c6dd2c6a37a39c544b",
        92, {0x2638, 0x28A2, 0x2902, 0x4ADE},
    ),
    0x1B6C: (
        "object_coefficient_update", "open_cfw_touch_application_1b6c_update",
        "7eac94530cd96e75102f43915a6824aad0104d280814cf571fdd0b0609d8fb22",
        232, {0x1B36, 0x1B58, 0x1B60},
    ),
    0x2638: (
        "object_sample_dispatch", "open_cfw_touch_application_2638_dispatch",
        "ff36864663409f567f7448f47a89fb7b9cfeb84a19af3c8a884d6847449f73e9",
        210, {0x1CEE, 0x1DA0, 0x2620},
    ),
}

SOURCE_PINS = {
    SOURCE: (7620, "4cb7326476acd23c8c9fa5100e643b3aa19e87a44e922afbc5ac99dac5f6f40c"),
    HEADER: (3441, "233e058fdf830793940f9e794c48f1e19d09558e965594ef45138bf7ad91e3c8"),
}

EXPECTED = {
    "input_concrete_gap": 25,
    "input_gap_instruction_bytes": 3864,
    "admitted_functions": 4,
    "admitted_instruction_bytes": 706,
    "resident_body_admissions": 0,
    "fixed_address_accesses": 0,
    "unimplemented_application_contracts_before": 13,
    "unimplemented_application_contracts_after": 9,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 21,
    "residual_gap_instruction_bytes": 3158,
}


class AuditError(RuntimeError): pass
def require(condition, message):
    if not condition: raise AuditError(message)
def sha256(data): return hashlib.sha256(data).hexdigest()


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
    with tempfile.TemporaryDirectory(prefix="open-cfw-touch-app-core-audit-") as raw:
        output = Path(raw) / "touch-app-core.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0,
                f"application core target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected=True):
    prior_mod = _load(PRIOR, "touch_application_core_batch22")
    prefix = _load(PREFIX, "touch_application_core_prefix")
    prior = prior_mod.analyze()
    residual = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual.keys(),
            "application core escaped batch-22 residual")
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
            "status": "clean_room_application_core_source", "license": "MIT",
            "source": SOURCE.name, "direct_callees": sorted(calls),
            "caller_owned_object_views": True,
            "injected_provider_contract": True,
            "resident_body_admitted": False, "fixed_address_access": False,
            "mmio_execution": False, "instruction_bytes": byte_count,
            "instruction_sha256": residual[entry]["instruction_sha256"],
            "canonical_body_sha256": digest,
            "evidence": "complete authenticated application flow represented with caller-owned object views and injected resident/platform providers; no resident body, fixed-address access, MMIO, reset, flash, or product main-loop execution",
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
        "resident_body_admissions": 0, "fixed_address_accesses": 0,
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
                    f"application core {key} changed: {metrics[key]!r} != {value!r}")
    return {
        "schema_version": 1,
        "component": "G2 Touch application core admission batch 23",
        "analysis_mode": "offline authenticated flow with injected providers and caller-owned object views; host and Cortex-M0+ compile; no hardware/MMIO execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
                   "sha256": sha256(SOURCE.read_bytes()),
                   "target_closure_object_bytes": target_bytes},
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
        "exclusions": "all EULA bodies, product main loop, resident table loaders, system handoff, and halt remain unadmitted",
    }


def write_manifests(result):
    admitted = MANIFEST_DIR / "g2-touch-application-core-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license",
                         "source", "direct_callees", "caller_owned_object_views",
                         "injected_provider_contract", "resident_body_admitted",
                         "fixed_address_access", "mmio_execution",
                         "instruction_bytes", "instruction_sha256",
                         "canonical_body_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["symbol"], row["kind"],
                row["status"], row["license"], row["source"],
                ",".join(f"0x{x:04X}" for x in row["direct_callees"]),
                str(row["caller_owned_object_views"]).lower(),
                str(row["injected_provider_contract"]).lower(),
                str(row["resident_body_admitted"]).lower(),
                str(row["fixed_address_access"]).lower(),
                str(row["mmio_execution"]).lower(), row["instruction_bytes"],
                row["instruction_sha256"], row["canonical_body_sha256"],
                row["evidence"],
            ])
    residual = MANIFEST_DIR / "g2-touch-application-core-residual.tsv"
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
    summary = MANIFEST_DIR / "g2-touch-application-core-admission-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("rows", "residual_rows")}
    slim["admitted_row_count"] = len(result["rows"])
    slim["residual_row_count"] = len(result["residual_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    # This admission summary is intentionally not the authoritative whole-blob
    # classification. Only analyze_g2_touch_final_frontier.py may publish the
    # shared current-readiness summary after composing this batch with the
    # exhaustive physical-byte partition.
    return [admitted, residual, summary]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args(); result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(f"application core sources: {result['metrics']['admitted_functions']}")
    print(f"remaining concrete source/implementation gap: {len(result['residual_rows'])}")
    return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch application core admission failed: {exc}") from exc
