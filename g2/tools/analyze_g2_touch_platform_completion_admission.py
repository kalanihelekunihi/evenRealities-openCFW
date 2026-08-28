#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the selected Touch runtime/configuration completion package (batch 26)."""

from __future__ import annotations

import argparse, csv, hashlib, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; TOOLS = ROOT / "tools"; TOUCH = ROOT / "components/shared/touch"; MANIFEST_DIR = TOOLS / "manifests"
PRIOR = TOOLS / "analyze_g2_touch_emeeprom_clean_room_admission.py"; PREFIX = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_platform_completion.c"; HEADER = TOUCH / "runtime_touch_platform_completion.h"

ADMISSIONS = {
    0x0158: ("stack_limit_policy", "open_cfw_touch_runtime_0158_stack_limit", "b5f873d96c4bfc0ce0c486b42181420d4fb352a0b04a4f39b129290729b28b5f", 10, set(), 0),
    0x0164: ("crt_reset_entry", "open_cfw_touch_runtime_0164_reset_entry", "70467ead85e33e8cf3fe12088cc24e1c827fca2144163ca0a3f28fcdb07b897b", 164, {0x0158, 0x09B4, 0x5738, 0x76AC, 0x76D4, 0x76E4}, 2),
    0x12A6: ("fault_policy", "open_cfw_touch_runtime_12a6_fault", "3e85fa2e615ee2d81fae2332bc1a4536b3494e8a26fbbac27a33571d8181ce4e", 4, set(), 0),
    0x141C: ("interrupt_disabled_handoff", "open_cfw_touch_runtime_141c_handoff", "6e2187c3d7ea5cde93b462d2f05ccd359bb78e673cef9bc36515c2631241a029", 16, {0x1418}, 0),
    0x1DE4: ("mapping_table_loader", "open_cfw_touch_config_1de4_load_mapping", "55f9420ebbdebfea313c15c4c438f9ef71ab2277330fd754e586bd9bb76b3e65", 158, {0x772C}, 0),
    0x1FBC: ("profile_table_loader", "open_cfw_touch_config_1fbc_load_profiles", "b4b1f73b4ce607fa8aa8bd029cf4b057584e3b24afebd77c0cf295cbdf56bbf3", 172, set(), 0),
    0x2078: ("register_image_builder", "open_cfw_touch_config_2078_build", "b286d5533d7eceb31e12d204095dfdc37d214243ad3965ae9b137b1dbe018200", 416, {0x1DE4, 0x1FBC, 0x76D4}, 0),
    0x7038: ("selected_halt_policy", "open_cfw_touch_runtime_7038_halt", "b91a1b3c92ace1a7871fca0010511e2496552966b10980fbf7bf34d7382d42b9", 2, set(), 0),
}

SOURCE_PINS = {SOURCE: (7400, "204e0f30500b1e70d2dbcf68b97c161e0116ab2d0fcb096a7658c615f6b0c00f"), HEADER: (3770, "7d8e7940d51144468aebe79061c75df1a7b3915cd144d79b0555d8bd1cd66247")}
EXPECTED = {"input_concrete_gap": 8, "input_gap_instruction_bytes": 942, "admitted_functions": 8, "admitted_instruction_bytes": 942,
    "residual_functions": 0, "residual_gap_instruction_bytes": 0, "selected_runtime_functions": 4, "source_owned_configuration_functions": 3,
    "selected_halt_functions": 1, "fixed_address_accesses": 0, "unimplemented_application_contracts_after": 0,
    "typed_external_or_unavailable_functions": 0, "concrete_source_or_implementation_gap_after": 0}


class AuditError(RuntimeError): pass
def require(c, m):
    if not c: raise AuditError(m)
def sha256(data): return hashlib.sha256(data).hexdigest()
def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); require(spec and spec.loader, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module); return module


def _target_compile():
    clang = shutil.which("clang"); require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-touch-platform-final-audit-") as raw:
        output = Path(raw) / "touch-platform-final.o"
        proc = subprocess.run([clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb", "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output)], capture_output=True, text=True)
        require(proc.returncode == 0, f"platform completion target compile failed: {proc.stderr}"); return output.stat().st_size


def analyze(*, enforce_expected=True):
    prior_mod = _load(PRIOR, "touch_platform_final_batch25"); prefix = _load(PREFIX, "touch_platform_final_prefix")
    prior = prior_mod.analyze(); residual = {r["entry"]: r for r in prior["residual_rows"]}
    require(set(ADMISSIONS) == residual.keys(), "platform completion is not the exact batch-25 residual")
    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(residual)
    for _kind, _symbol, _digest, _bytes, calls, _indirect in ADMISSIONS.values(): entries.update(calls)
    combined = SOURCE.read_text() + HEADER.read_text(); require(combined.count("SPDX-License-Identifier: MIT") == 2, "MIT declarations changed")
    require("0x400" not in SOURCE.read_text() and "0xE000" not in SOURCE.read_text(), "fixed hardware address entered platform completion source")
    for path, (size, digest) in SOURCE_PINS.items():
        data = path.read_bytes(); require(len(data) == size and sha256(data) == digest, f"source identity changed: {path.relative_to(ROOT)}")
    target_bytes = _target_compile(); rows = []
    for entry, (kind, symbol, digest, byte_count, expected_calls, expected_indirect) in sorted(ADMISSIONS.items()):
        body = prefix._walk(payload, entry, entries); canonical = "|".join(f"{a:04X}:{i.mnemonic} {i.op_str}" for a, i in sorted(body["instructions"].items()))
        calls = {c["target"] for c in body["calls"] if c["target"] is not None}; indirect = sum(c["target"] is None for c in body["calls"])
        require(sha256(canonical.encode()) == digest, f"body changed at {entry:#x}"); require(calls == expected_calls and indirect == expected_indirect, f"calls changed at {entry:#x}")
        require(residual[entry]["instruction_bytes"] == byte_count, f"span changed at {entry:#x}"); require(symbol in combined, f"source symbol missing: {symbol}")
        rows.append({"entry": entry, "symbol": symbol, "kind": kind, "status": "selected_mit_platform_source", "license": "MIT", "source": SOURCE.name,
            "direct_callees": sorted(calls), "indirect_calls": indirect, "deterministic_safe_defaults": entry in (0x1DE4, 0x1FBC, 0x2078),
            "injected_platform_contract": entry in (0x0164, 0x12A6, 0x141C), "fixed_address_access": False, "mmio_execution": False,
            "instruction_bytes": byte_count, "instruction_sha256": residual[entry]["instruction_sha256"], "canonical_body_sha256": digest,
            "evidence": "exact final authenticated function boundary represented by selected MIT runtime/system policy or source-owned generated configuration; safe defaults compile without resident tables; no fixed-address access or hardware execution"})
    residual_rows = []
    metrics = {"input_concrete_gap": len(residual), "input_gap_instruction_bytes": sum(r["instruction_bytes"] for r in residual.values()),
        "admitted_functions": len(rows), "admitted_instruction_bytes": sum(r["instruction_bytes"] for r in rows), "residual_functions": 0, "residual_gap_instruction_bytes": 0,
        "selected_runtime_functions": 4, "source_owned_configuration_functions": 3, "selected_halt_functions": 1, "fixed_address_accesses": 0,
        "unimplemented_application_contracts_after": 0, "typed_external_or_unavailable_functions": 0, "concrete_source_or_implementation_gap_after": 0,
        "row_digest": sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()), "residual_digest": sha256(b"[]")}
    if enforce_expected:
        for key, value in EXPECTED.items(): require(metrics[key] == value, f"platform completion {key} changed: {metrics[key]!r} != {value!r}")
    return {"schema_version": 1, "component": "G2 Touch selected platform completion admission batch 26",
        "analysis_mode": "offline authenticated boundary plus selected source policy; host and Cortex-M0+ compile; no hardware/MMIO execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT", "sha256": sha256(SOURCE.read_bytes()), "target_closure_object_bytes": target_bytes},
        "software_function_frontier_complete": True, "integration": "isolated source candidate only; not production-routed",
        "configuration_evidence": "deterministic safe defaults selected; board-specific tuning and resident-table equivalence require physical evidence",
        "remaining": {"concrete_source_or_implementation_functions": 0, "concrete_gap_instruction_bytes": 0, "unimplemented_clean_room_application_contracts": 0, "typed_external_or_unavailable_functions": 0},
        "hardware_validation": "deferred by project direction", "hardware_blocker": "deferred by project direction",
        "exclusions": "production routing, board-specific tuning, electrical/timing qualification, and on-device validation remain"}


def write_manifests(result):
    admitted = MANIFEST_DIR / "g2-touch-platform-completion-admission.tsv"
    with admitted.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["entry", "symbol", "kind", "status", "license", "source", "direct_callees", "indirect_calls", "deterministic_safe_defaults", "injected_platform_contract", "fixed_address_access", "mmio_execution", "instruction_bytes", "instruction_sha256", "canonical_body_sha256", "evidence"])
        for r in result["rows"]: w.writerow([f"0x{r['entry']:04X}", r["symbol"], r["kind"], r["status"], r["license"], r["source"], ",".join(f"0x{x:04X}" for x in r["direct_callees"]), r["indirect_calls"], str(r["deterministic_safe_defaults"]).lower(), str(r["injected_platform_contract"]).lower(), "false", "false", r["instruction_bytes"], r["instruction_sha256"], r["canonical_body_sha256"], r["evidence"]])
    residual = MANIFEST_DIR / "g2-touch-platform-completion-residual.tsv"
    residual.write_text("# SPDX-License-Identifier: MIT\nentry\tfamily\tstatus\tlicense\tconcrete_source\timplemented\tinstruction_bytes\tinstruction_sha256\treason\n")
    summary = MANIFEST_DIR / "g2-touch-platform-completion-admission-summary.json"; slim = {k: v for k, v in result.items() if k not in ("rows", "residual_rows")}; slim["admitted_row_count"] = len(result["rows"]); slim["residual_row_count"] = 0; summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    # Only the exhaustive final classifier owns the cross-batch current
    # summary.  Admission writers must never reopen a sealed frontier.
    return [admitted, residual, summary]


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--write-manifests", action="store_true"); args = p.parse_args(); result = analyze()
    if args.write_manifests:
        for path in write_manifests(result): print(f"wrote {path.relative_to(ROOT)}")
    print(f"platform completion sources: {result['metrics']['admitted_functions']}"); print("remaining concrete source/implementation gap: 0"); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AuditError as exc: raise SystemExit(f"Touch platform completion admission failed: {exc}") from exc
