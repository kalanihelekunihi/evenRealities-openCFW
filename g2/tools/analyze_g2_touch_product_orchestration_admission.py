#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the final Touch product-owned orchestration functions (batch 24)."""

from __future__ import annotations

import argparse, csv, hashlib, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
PRIOR = TOOLS / "analyze_g2_touch_application_core_admission.py"
PREFIX = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_product_orchestration.c"
HEADER = TOUCH / "runtime_touch_product_orchestration.h"

ADMISSIONS = {
    0x05E0: (
        "application_bringup", "open_cfw_touch_product_05e0_bringup",
        "cc55d52d71edc71b2f0cc3f22008910146c653969b1ca6f9cd3b6b7134399ca1",
        86, {0x17F4, 0x197C, 0x6FA8},
    ),
    0x09B4: (
        "nonreturning_product_state_machine", "open_cfw_touch_product_09b4_run",
        "4a1f1ac88f78e111b91a764d021b18e58a32f35be25a26a181d7149beb4ba998",
        494, {0x0338, 0x0358, 0x0378, 0x05E0, 0x065C, 0x0780, 0x0824,
              0x09A4, 0x0BE0, 0x1192, 0x119A, 0x1350, 0x1904, 0x297A,
              0x298E, 0x2A90, 0x2AD8, 0x3D50, 0x49F8, 0x4A04, 0x7228,
              0x728C, 0x76D4},
    ),
}

SOURCE_PINS = {
    SOURCE: (7609, "3456f3a24b6301823f822d4e82588ea8b660e31b2bb5833d1320605a8a182f61"),
    HEADER: (2509, "b217498a7adb72a96130b570a817526cd094cfebbe09d32e61f96e40fdae1050"),
}

EXPECTED = {
    "input_concrete_gap": 21, "input_gap_instruction_bytes": 3158,
    "admitted_functions": 2, "admitted_instruction_bytes": 580,
    "resident_body_admissions": 0, "fixed_address_accesses": 0,
    "unimplemented_application_contracts_before": 9,
    "unimplemented_application_contracts_after": 0,
    "typed_external_or_unavailable_functions": 19,
    "concrete_source_or_implementation_gap_after": 19,
    "residual_gap_instruction_bytes": 2578,
}


class AuditError(RuntimeError): pass
def require(c, m):
    if not c: raise AuditError(m)
def sha256(data): return hashlib.sha256(data).hexdigest()
def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec and spec.loader, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module); return module


def _target_compile():
    clang = shutil.which("clang"); require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-touch-product-audit-") as raw:
        output = Path(raw) / "touch-product.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0,
                f"product orchestration target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected=True):
    prior_mod = _load(PRIOR, "touch_product_batch23")
    prefix = _load(PREFIX, "touch_product_prefix")
    prior = prior_mod.analyze()
    residual = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual.keys(),
            "product orchestration escaped batch-23 residual")
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
    target_bytes = _target_compile(); rows = []
    for entry, (kind, symbol, digest, byte_count, expected_calls) in sorted(
            ADMISSIONS.items()):
        body = prefix._walk(payload, entry, entries)
        canonical = "|".join(
            f"{address:04X}:{insn.mnemonic} {insn.op_str}"
            for address, insn in sorted(body["instructions"].items()))
        calls = {call["target"] for call in body["calls"]}
        require(sha256(canonical.encode()) == digest, f"body changed at {entry:#x}")
        require(calls == expected_calls, f"calls changed at {entry:#x}")
        require(residual[entry]["instruction_bytes"] == byte_count,
                f"span changed at {entry:#x}")
        require(symbol in combined, f"source symbol missing: {symbol}")
        rows.append({
            "entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_product_orchestration_source", "license": "MIT",
            "source": SOURCE.name, "direct_callees": sorted(calls),
            "caller_supplied_register_views": True,
            "injected_provider_contract": True,
            "resident_body_admitted": False, "fixed_address_access": False,
            "mmio_execution": False, "instruction_bytes": byte_count,
            "instruction_sha256": residual[entry]["instruction_sha256"],
            "canonical_body_sha256": digest,
            "evidence": "complete authenticated startup and state-machine flow with deterministic init/step tests and nonreturning production entry; all board/resident calls injected and all register writes caller-authorized",
        })
    residual_rows = [row for entry, row in sorted(residual.items())
                     if entry not in ADMISSIONS]
    is_app = lambda row: row["family"] in (
        "platform_startup_configuration", "touch_application_processing")
    is_external = lambda row: row["family"] in (
        "emeeprom_eula", "system_handoff_mixed", "legacy_halt")
    metrics = {
        "input_concrete_gap": len(residual),
        "input_gap_instruction_bytes": sum(r["instruction_bytes"] for r in residual.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(r["instruction_bytes"] for r in rows),
        "resident_body_admissions": 0, "fixed_address_accesses": 0,
        "unimplemented_application_contracts_before": sum(map(is_app, residual.values())),
        "unimplemented_application_contracts_after": 0,
        "typed_external_or_unavailable_functions": len(residual_rows),
        "concrete_source_or_implementation_gap_after": len(residual_rows),
        "residual_gap_instruction_bytes": sum(r["instruction_bytes"] for r in residual_rows),
        "row_digest": sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(residual_rows, sort_keys=True, separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, value in EXPECTED.items():
            require(metrics[key] == value,
                    f"product orchestration {key} changed: {metrics[key]!r} != {value!r}")
    return {
        "schema_version": 1,
        "component": "G2 Touch product orchestration admission batch 24",
        "analysis_mode": "offline authenticated flow with injected providers and caller-owned register views; host and Cortex-M0+ compile; no hardware/MMIO execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
                   "sha256": sha256(SOURCE.read_bytes()),
                   "target_closure_object_bytes": target_bytes},
        "integration": "isolated source candidate only; not production-routed",
        "remaining": {"concrete_source_or_implementation_functions": len(residual_rows),
                      "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
                      "unimplemented_clean_room_application_contracts": metrics["unimplemented_application_contracts_after"],
                      "typed_external_or_unavailable_functions": 19},
        "hardware_validation": "deferred by project direction",
        "hardware_blocker": "deferred by project direction",
        "exclusions": "only selected-runtime, resident-configuration, system-handoff, Infineon EULA provider, and halt boundaries remain",
    }


def write_manifests(result):
    admitted = MANIFEST_DIR / "g2-touch-product-orchestration-admission.tsv"
    with admitted.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n")
        w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["entry", "symbol", "kind", "status", "license", "source",
                    "direct_callees", "caller_supplied_register_views",
                    "injected_provider_contract", "resident_body_admitted",
                    "fixed_address_access", "mmio_execution", "instruction_bytes",
                    "instruction_sha256", "canonical_body_sha256", "evidence"])
        for r in result["rows"]:
            w.writerow([f"0x{r['entry']:04X}", r["symbol"], r["kind"], r["status"],
                        r["license"], r["source"], ",".join(f"0x{x:04X}" for x in r["direct_callees"]),
                        str(r["caller_supplied_register_views"]).lower(),
                        str(r["injected_provider_contract"]).lower(),
                        str(r["resident_body_admitted"]).lower(),
                        str(r["fixed_address_access"]).lower(),
                        str(r["mmio_execution"]).lower(), r["instruction_bytes"],
                        r["instruction_sha256"], r["canonical_body_sha256"], r["evidence"]])
    residual = MANIFEST_DIR / "g2-touch-product-orchestration-residual.tsv"
    with residual.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n")
        w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["entry", "family", "status", "license", "concrete_source",
                    "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for r in result["residual_rows"]:
            w.writerow([f"0x{r['entry']:04X}", r["family"], r["status"], r["license"],
                        str(r["concrete_source"]).lower(), str(r["implemented"]).lower(),
                        r["instruction_bytes"], r["instruction_sha256"], r["reason"]])
    summary = MANIFEST_DIR / "g2-touch-product-orchestration-admission-summary.json"
    slim = {k: v for k, v in result.items() if k not in ("rows", "residual_rows")}
    slim["admitted_row_count"] = len(result["rows"]); slim["residual_row_count"] = len(result["residual_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    # This admission summary is intentionally not the authoritative whole-blob
    # classification. Only analyze_g2_touch_final_frontier.py may publish the
    # shared current-readiness summary after composing this batch with the
    # exhaustive physical-byte partition.
    return [admitted, residual, summary]


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--write-manifests", action="store_true")
    args = p.parse_args(); result = analyze()
    if args.write_manifests:
        for path in write_manifests(result): print(f"wrote {path.relative_to(ROOT)}")
    print(f"product orchestration sources: {result['metrics']['admitted_functions']}")
    print(f"remaining concrete source/implementation gap: {len(result['residual_rows'])}")
    return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AuditError as exc: raise SystemExit(f"Touch product orchestration admission failed: {exc}") from exc
