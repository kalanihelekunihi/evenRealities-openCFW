#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the touch configuration bootstrap orchestrator (batch 16)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
PRIOR_ANALYZER = TOOLS / "analyze_g2_touch_storage_adapters_admission.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_configuration_bootstrap.c"
HEADER = TOUCH / "runtime_touch_configuration_bootstrap.h"
STORAGE_SOURCE = TOUCH / "runtime_touch_storage_adapters.c"
ENTRY = 0x065C
BODY_DIGEST = "9d5bf579e61812d30ca82903eb07ff1808622a7005f080d878f53d1566a238ae"
CALLEES = {0x01D8, 0x0220, 0x0268, 0x02B0, 0x0BE0, 0x6FF0}
EXPECTED = {
    "input_concrete_gap": 56, "input_gap_instruction_bytes": 5120,
    "admitted_functions": 1, "admitted_instruction_bytes": 156,
    "resident_table_admissions": 0, "mmio_admissions": 0,
    "unimplemented_application_contracts_before": 44,
    "unimplemented_application_contracts_after": 43,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 55,
    "residual_gap_instruction_bytes": 4964,
    "row_digest": "cda930138750aec406bbd05f13b37d122706b3c4eddbdf791a44778749efe193",
    "residual_digest": "183e47c26c0416d96dcdb76b50e32a090bc75ffcbf18ba83c54e0bf8bdea24af",
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
    total = 0
    with tempfile.TemporaryDirectory() as raw:
        for source in (SOURCE, STORAGE_SOURCE):
            output = Path(raw) / (source.stem + ".o")
            proc = subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(TOUCH), "-c", str(source), "-o", str(output),
            ], capture_output=True, text=True)
            require(proc.returncode == 0, f"bootstrap target compile failed: {proc.stderr}")
            total += output.stat().st_size
    return total


def analyze(*, enforce_expected: bool = True) -> dict:
    prior_mod = _load(PRIOR_ANALYZER, "touch_bootstrap_batch15")
    prefix = _load(PREFIX_ANALYZER, "touch_bootstrap_prefix")
    prior = prior_mod.analyze()
    residual_by_entry = {row["entry"]: row for row in prior["residual_rows"]}
    require(ENTRY in residual_by_entry, "bootstrap escaped batch-15 residual")
    require(residual_by_entry[ENTRY]["family"] == "platform_startup_configuration",
            "bootstrap crossed provider boundary")
    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    body = prefix._walk(payload, ENTRY, set(residual_by_entry) | CALLEES)
    canonical = "|".join(f"{address:04X}:{insn.mnemonic} {insn.op_str}"
                         for address, insn in sorted(body["instructions"].items()))
    callees = {call["target"] for call in body["calls"] if call["target"] is not None}
    require(sha256(canonical.encode()) == BODY_DIGEST, "bootstrap canonical body changed")
    require(callees == CALLEES, f"bootstrap calls changed: {sorted(callees)}")
    require(residual_by_entry[ENTRY]["instruction_bytes"] == 156,
            "bootstrap byte span changed")
    require(struct.unpack_from("<I", payload, 0x06FC)[0] == 0x45564E55,
            "bootstrap magic changed")
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "bootstrap MIT declarations changed")
    require("open_cfw_touch_config_065c_bootstrap" in combined,
            "bootstrap source symbol missing")
    target_bytes = _target_compile()

    prior_row = residual_by_entry[ENTRY]
    rows = [{
        "entry": ENTRY, "symbol": "open_cfw_touch_config_065c_bootstrap",
        "kind": "configuration_load_default_and_write_orchestrator",
        "status": "clean_room_configuration_bootstrap_source",
        "license": "MIT", "source": SOURCE.name,
        "direct_callees": sorted(callees),
        "call_closure": "previously_admitted_mit_storage_and_policy_adapters_plus_apache_delay_and_intentional_noop_logger",
        "eula_provider_body_admitted": False,
        "resident_table_dependency": False,
        "instruction_bytes": prior_row["instruction_bytes"],
        "instruction_sha256": prior_row["instruction_sha256"],
        "canonical_body_sha256": BODY_DIGEST,
        "evidence": "complete configuration load/default/write control flow; logging is the established no-op; storage provider remains behind prior typed adapters; no MMIO, resident table or EULA body admitted",
    }]
    residual_rows = [row for entry, row in sorted(residual_by_entry.items()) if entry != ENTRY]
    metrics = {
        "input_concrete_gap": len(residual_by_entry),
        "input_gap_instruction_bytes": sum(row["instruction_bytes"] for row in residual_by_entry.values()),
        "admitted_functions": 1, "admitted_instruction_bytes": 156,
        "resident_table_admissions": 0, "mmio_admissions": 0,
        "unimplemented_application_contracts_before": sum(
            row["family"] in ("platform_startup_configuration", "touch_application_processing")
            for row in residual_by_entry.values()),
        "unimplemented_application_contracts_after": sum(
            row["family"] in ("platform_startup_configuration", "touch_application_processing")
            for row in residual_rows),
        "typed_external_or_unavailable_functions": sum(
            row["family"] in ("emeeprom_eula", "system_handoff_mixed", "legacy_halt")
            for row in residual_rows),
        "concrete_source_or_implementation_gap_after": len(residual_rows),
        "residual_gap_instruction_bytes": sum(row["instruction_bytes"] for row in residual_rows),
        "row_digest": sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(residual_rows, sort_keys=True,
                                               separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"bootstrap {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1, "component": "G2 touch configuration bootstrap admission batch 16",
        "analysis_mode": "offline authenticated control/data flow, injected storage/write/delay providers, host and Cortex-M0+ compile; no hardware/MMIO execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
                   "sha256": sha256(SOURCE.read_bytes()),
                   "target_closure_object_bytes": target_bytes},
        "integration": "isolated source candidate only; not production-routed",
        "remaining": {"concrete_source_or_implementation_functions": len(residual_rows),
                      "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
                      "unimplemented_clean_room_application_contracts": metrics["unimplemented_application_contracts_after"],
                      "typed_external_or_unavailable_functions": 12},
        "exclusions": "all Em_EEPROM EULA provider bodies, resident tables/loaders, ambiguous 0x1B6C/0x1C54/0x2638, system handoff and halt remain unadmitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-configuration-bootstrap-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license", "source",
                         "direct_callees", "call_closure", "eula_provider_body_admitted",
                         "resident_table_dependency", "instruction_bytes",
                         "instruction_sha256", "canonical_body_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["symbol"], row["kind"], row["status"],
                             row["license"], row["source"],
                             ",".join(f"0x{x:04X}" for x in row["direct_callees"]),
                             row["call_closure"], str(row["eula_provider_body_admitted"]).lower(),
                             str(row["resident_table_dependency"]).lower(), row["instruction_bytes"],
                             row["instruction_sha256"], row["canonical_body_sha256"], row["evidence"]])
    residual = MANIFEST_DIR / "g2-touch-configuration-bootstrap-residual.tsv"
    with residual.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "family", "status", "license", "concrete_source",
                         "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for row in result["residual_rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["family"], row["status"], row["license"],
                             str(row["concrete_source"]).lower(), str(row["implemented"]).lower(),
                             row["instruction_bytes"], row["instruction_sha256"], row["reason"]])
    summary = MANIFEST_DIR / "g2-touch-configuration-bootstrap-admission-summary.json"
    slim = {key: value for key, value in result.items() if key not in ("rows", "residual_rows")}
    slim["admitted_row_count"] = 1
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
    print(f"configuration bootstrap sources: {result['metrics']['admitted_functions']}")
    print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch configuration bootstrap admission failed: {exc}") from exc
