#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the last evidence-closed Touch wrappers (batch 20)."""

from __future__ import annotations

import argparse, csv, hashlib, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
PRIOR = TOOLS / "analyze_g2_touch_flash_row_admission.py"
PREFIX = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_terminal_wrappers.c"
HEADER = TOUCH / "runtime_touch_terminal_wrappers.h"
ADMISSIONS = {
    0x1368: ("effect_free_passthrough_wrapper", "open_cfw_touch_terminal_1368_passthrough",
             "5f90f1fb06e9903674b82d2dc8e06dd5ceeceb2679288693ebaba2e449421f6f", 8, {0x1366}),
    0x25F8: ("three_object_reset_wrapper", "open_cfw_touch_terminal_25f8_reset_three",
             "62aa5da5f3d6cf8956b068579bb2c2afd7f8f805407e7abcf9f86fd5959d3886", 36, {0x2568}),
    0x2972: ("typed_capsense_provider_wrapper", "open_cfw_touch_terminal_2972_provider_call",
             "15ff04f8e98a081f64aa5afa467588b2dcac6b5daad5022baa74b1a6a66b801d", 8, {0x38D4}),
    0x297A: ("conditional_capsense_provider_wrapper", "open_cfw_touch_terminal_297a_conditional_call",
             "f14129b80f7f0d08287c74c1f89493287b16c32f65e2d5afbc010c95e00e2e40", 20, {0x2972}),
}
EXPECTED = {
    "input_concrete_gap": 47, "input_gap_instruction_bytes": 4550,
    "admitted_functions": 4, "admitted_instruction_bytes": 72,
    "resident_table_admissions": 0, "mmio_admissions": 0,
    "unimplemented_application_contracts_before": 35,
    "unimplemented_application_contracts_after": 31,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 43,
    "residual_gap_instruction_bytes": 4478,
    "row_digest": "37fabb976d51eb880c82f93324c00f93d2369774bfe62407987d4a4517081655",
    "residual_digest": "4c807b2b8b0d2586d65fd2345ab963c6bd31c7fcb35db8d91705a2fc11638bf2",
}


class AuditError(RuntimeError): pass
def require(c, m):
    if not c: raise AuditError(m)
def sha256(data): return hashlib.sha256(data).hexdigest()
def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module); return module


def _target_compile():
    clang = shutil.which("clang"); require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory() as raw:
        output = Path(raw) / "touch-terminal.o"
        proc = subprocess.run([clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
            "-mthumb", "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output)],
            capture_output=True, text=True)
        require(proc.returncode == 0, f"terminal target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected=True):
    prior_mod = _load(PRIOR, "touch_terminal_batch19")
    prefix = _load(PREFIX, "touch_terminal_prefix")
    prior = prior_mod.analyze(); residual = {r["entry"]: r for r in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual.keys(), "terminal wrappers escaped batch-19 residual")
    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(residual)
    for _k, _s, _d, _b, calls in ADMISSIONS.values(): entries.update(calls)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2, "MIT declarations changed")
    target_bytes = _target_compile(); rows = []
    for entry, (kind, symbol, digest, byte_count, expected_calls) in sorted(ADMISSIONS.items()):
        body = prefix._walk(payload, entry, entries)
        canonical = "|".join(f"{a:04X}:{i.mnemonic} {i.op_str}" for a, i in sorted(body["instructions"].items()))
        calls = {c["target"] for c in body["calls"]}
        require(sha256(canonical.encode()) == digest, f"body changed at {entry:#x}")
        require(calls == expected_calls, f"calls changed at {entry:#x}")
        require(residual[entry]["instruction_bytes"] == byte_count, f"span changed at {entry:#x}")
        require(symbol in combined, f"source symbol missing: {symbol}")
        rows.append({"entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_terminal_wrapper_source", "license": "MIT",
            "source": SOURCE.name, "direct_callees": sorted(calls),
            "eula_provider_body_admitted": False, "resident_table_dependency": False,
            "mmio_execution": False, "instruction_bytes": byte_count,
            "instruction_sha256": residual[entry]["instruction_sha256"],
            "canonical_body_sha256": digest,
            "evidence": "complete wrapper control/data flow; 0x38D4 remains an injected CAPSENSE EULA provider and 0x2568/0x1366 are admitted MIT source; no vendor body, resident table, MMIO execution or product policy admitted"})
    residual_rows = [r for e, r in sorted(residual.items()) if e not in ADMISSIONS]
    is_app = lambda r: r["family"] in ("platform_startup_configuration", "touch_application_processing")
    is_ext = lambda r: r["family"] in ("emeeprom_eula", "system_handoff_mixed", "legacy_halt")
    metrics = {"input_concrete_gap": len(residual),
        "input_gap_instruction_bytes": sum(r["instruction_bytes"] for r in residual.values()),
        "admitted_functions": len(rows), "admitted_instruction_bytes": sum(r["instruction_bytes"] for r in rows),
        "resident_table_admissions": 0, "mmio_admissions": 0,
        "unimplemented_application_contracts_before": sum(map(is_app, residual.values())),
        "unimplemented_application_contracts_after": sum(map(is_app, residual_rows)),
        "typed_external_or_unavailable_functions": sum(map(is_ext, residual_rows)),
        "concrete_source_or_implementation_gap_after": len(residual_rows),
        "residual_gap_instruction_bytes": sum(r["instruction_bytes"] for r in residual_rows),
        "row_digest": sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(residual_rows, sort_keys=True, separators=(",", ":")).encode())}
    if enforce_expected:
        for key, value in EXPECTED.items(): require(metrics[key] == value, f"terminal {key} changed: {metrics[key]!r} != {value!r}")
    return {"schema_version": 1, "component": "G2 touch terminal wrapper admission batch 20",
        "analysis_mode": "offline authenticated flow with typed EULA provider seam; host and Cortex-M0+ compile; no hardware/MMIO execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT", "sha256": sha256(SOURCE.read_bytes()), "target_closure_object_bytes": target_bytes},
        "integration": "isolated source candidate only; not production-routed",
        "remaining": {"concrete_source_or_implementation_functions": len(residual_rows), "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"], "unimplemented_clean_room_application_contracts": metrics["unimplemented_application_contracts_after"], "typed_external_or_unavailable_functions": 12},
        "exclusions": "all EULA bodies, resident tables/loaders, 0x1B6C/0x1C54/0x2638, system handoff and halt remain unadmitted"}


def write_manifests(result):
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-terminal-wrappers-admission.tsv"
    with admitted.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["entry", "symbol", "kind", "status", "license", "source", "direct_callees", "eula_provider_body_admitted", "resident_table_dependency", "mmio_execution", "instruction_bytes", "instruction_sha256", "canonical_body_sha256", "evidence"])
        for r in result["rows"]: w.writerow([f"0x{r['entry']:04X}", r["symbol"], r["kind"], r["status"], r["license"], r["source"], ",".join(f"0x{x:04X}" for x in r["direct_callees"]), str(r["eula_provider_body_admitted"]).lower(), str(r["resident_table_dependency"]).lower(), str(r["mmio_execution"]).lower(), r["instruction_bytes"], r["instruction_sha256"], r["canonical_body_sha256"], r["evidence"]])
    residual = MANIFEST_DIR / "g2-touch-terminal-wrappers-residual.tsv"
    with residual.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["entry", "family", "status", "license", "concrete_source", "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for r in result["residual_rows"]: w.writerow([f"0x{r['entry']:04X}", r["family"], r["status"], r["license"], str(r["concrete_source"]).lower(), str(r["implemented"]).lower(), r["instruction_bytes"], r["instruction_sha256"], r["reason"]])
    summary = MANIFEST_DIR / "g2-touch-terminal-wrappers-admission-summary.json"
    slim = {k: v for k, v in result.items() if k not in ("rows", "residual_rows")}; slim["admitted_row_count"] = len(result["rows"]); slim["residual_row_count"] = len(result["residual_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [admitted, residual, summary]


def main():
    p = argparse.ArgumentParser(); p.add_argument("--write-manifests", action="store_true"); args = p.parse_args(); result = analyze()
    if args.write_manifests:
        for path in write_manifests(result): print(f"wrote {path.relative_to(ROOT)}")
    print(f"terminal wrapper sources: {result['metrics']['admitted_functions']}"); print(f"remaining concrete source/implementation gap: {len(result['residual_rows'])}"); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AuditError as exc: raise SystemExit(f"Touch terminal wrapper admission failed: {exc}") from exc
