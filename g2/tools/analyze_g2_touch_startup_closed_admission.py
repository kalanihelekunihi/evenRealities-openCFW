#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit four evidence-closed Touch startup routines (batch 18)."""

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
PRIOR_ANALYZER = TOOLS / "analyze_g2_touch_deferred_work_admission.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_startup_closed.c"
HEADER = TOUCH / "runtime_touch_startup_closed.h"

# kind, symbol, canonical digest, byte count, exact direct calls
ADMISSIONS = {
    0x0D4C: (
        "bounded_record_initialize_and_timeout_default",
        "open_cfw_touch_startup_0d4c_initialize",
        "c4aa45e8537456b00236eba7be300dc1704c0eb27baf76f802f4c4c0098d6188",
        34, {0x0BE8, 0x76D4},
    ),
    0x11B4: (
        "three_effect_free_passthrough_calls",
        "open_cfw_touch_startup_11b4_passthrough_sequence",
        "1e7577ca86fd405e3c4989487094899c777d64746a063079cdbe576677e64d8d",
        16, {0x1226, 0x1236, 0x12A4},
    ),
    0x11D0: (
        "ordered_peripheral_clock_divider_configuration",
        "open_cfw_touch_startup_11d0_configure_dividers",
        "08f3a701d4fcbf81224f791e45d1a32d5f71e2cbf015cb72ecf01b9212d494b0",
        86, {0x6CD4, 0x6D1C, 0x6E04, 0x6E48},
    ),
    0x1228: (
        "peripheral_clock_divider_assignment",
        "open_cfw_touch_startup_1228_assign_divider",
        "ecebca5638d0e4f62b13b1288f66763d555e1c12755326496ed6c034eb34cca2",
        14, {0x6DBC},
    ),
}

EXPECTED = {
    "input_concrete_gap": 54,
    "input_gap_instruction_bytes": 4872,
    "admitted_functions": 4,
    "admitted_instruction_bytes": 150,
    "typed_provider_admissions": 2,
    "resident_table_admissions": 0,
    "mmio_admissions": 0,
    "unimplemented_application_contracts_before": 42,
    "unimplemented_application_contracts_after": 38,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 50,
    "residual_gap_instruction_bytes": 4722,
    "row_digest": "d728a7b2595c31ae4cd684c5538e223a1605301e9b6719e6772c13d7eb2c507b",
    "residual_digest": "51e1ad6a29abf47e0661644fdcc80e2d1f91744dcdd925c78e202f7bed89b19f",
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
        output = Path(raw) / "touch-startup-closed.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0,
                f"startup-closed target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected: bool = True) -> dict:
    prior_mod = _load(PRIOR_ANALYZER, "touch_startup_closed_batch17")
    prefix = _load(PREFIX_ANALYZER, "touch_startup_closed_prefix")
    prior = prior_mod.analyze()
    residual_by_entry = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual_by_entry.keys(),
            "startup-closed routines escaped batch-17 residual")
    require(all(residual_by_entry[entry]["family"] ==
                "platform_startup_configuration" for entry in ADMISSIONS),
            "startup-closed admission crossed family boundary")

    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(residual_by_entry)
    for _kind, _symbol, _digest, _size, callees in ADMISSIONS.values():
        entries.update(callees)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "startup-closed MIT declarations changed")
    target_bytes = _target_compile()
    rows = []
    for entry, (kind, symbol, digest, byte_count, expected_callees) in sorted(ADMISSIONS.items()):
        body = prefix._walk(payload, entry, entries)
        canonical = "|".join(
            f"{address:04X}:{insn.mnemonic} {insn.op_str}"
            for address, insn in sorted(body["instructions"].items()))
        callees = {call["target"] for call in body["calls"]}
        require(sha256(canonical.encode()) == digest,
                f"startup-closed body changed at {entry:#x}")
        require(callees == expected_callees,
                f"startup-closed calls changed at {entry:#x}: {sorted(callees)}")
        prior_row = residual_by_entry[entry]
        require(prior_row["instruction_bytes"] == byte_count,
                f"startup-closed span changed at {entry:#x}")
        require(symbol in combined, f"startup-closed source symbol missing: {symbol}")
        clock_provider = entry in (0x11D0, 0x1228)
        rows.append({
            "entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_startup_source_with_typed_providers",
            "license": "MIT", "source": SOURCE.name,
            "direct_callees": sorted(callees),
            "typed_providers": sorted(callees) if clock_provider else [],
            "provider_license": "Apache-2.0" if clock_provider else "MIT or exact C runtime behavior",
            "resident_table_dependency": False,
            "mmio_execution": False,
            "instruction_bytes": byte_count,
            "instruction_sha256": prior_row["instruction_sha256"],
            "canonical_body_sha256": digest,
            "evidence": (
                "complete authenticated argument-relative control/data flow; "
                "clock MMIO remains behind exact Apache-2.0 provider callbacks; "
                "no resident table, EULA body, MMIO execution or product policy admitted"
            ),
        })

    residual_rows = [row for entry, row in sorted(residual_by_entry.items())
                     if entry not in ADMISSIONS]
    metrics = {
        "input_concrete_gap": len(residual_by_entry),
        "input_gap_instruction_bytes": sum(
            row["instruction_bytes"] for row in residual_by_entry.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(row["instruction_bytes"] for row in rows),
        "typed_provider_admissions": sum(bool(row["typed_providers"]) for row in rows),
        "resident_table_admissions": 0,
        "mmio_admissions": 0,
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
        "residual_gap_instruction_bytes": sum(
            row["instruction_bytes"] for row in residual_rows),
        "row_digest": sha256(json.dumps(rows, sort_keys=True,
                                           separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(residual_rows, sort_keys=True,
                                                separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"startup-closed {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "authoritative_batch": 18,
        "hardware_validation": "blocked by unavailable physical evidence",
        "component": "G2 touch evidence-closed startup admission batch 18",
        "analysis_mode": "offline authenticated control/data flow, injected Apache provider seams, host and Cortex-M0+ compile; no hardware/MMIO execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
                   "sha256": sha256(SOURCE.read_bytes()),
                   "target_closure_object_bytes": target_bytes},
        "integration": "isolated source candidate only; not production-routed",
        "remaining": {
            "concrete_source_or_implementation_functions": len(residual_rows),
            "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
            "unimplemented_clean_room_application_contracts": metrics["unimplemented_application_contracts_after"],
            "typed_external_or_unavailable_functions": 12,
        },
        "exclusions": "all EULA bodies, resident tables/loaders, 0x1B6C/0x1C54/0x2638, system handoff and halt remain unadmitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-startup-closed-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license", "source",
                         "direct_callees", "typed_providers", "provider_license",
                         "resident_table_dependency", "mmio_execution",
                         "instruction_bytes", "instruction_sha256",
                         "canonical_body_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["symbol"], row["kind"], row["status"],
                row["license"], row["source"],
                ",".join(f"0x{x:04X}" for x in row["direct_callees"]),
                ",".join(f"0x{x:04X}" for x in row["typed_providers"]),
                row["provider_license"],
                str(row["resident_table_dependency"]).lower(),
                str(row["mmio_execution"]).lower(), row["instruction_bytes"],
                row["instruction_sha256"], row["canonical_body_sha256"], row["evidence"],
            ])
    residual = MANIFEST_DIR / "g2-touch-startup-closed-residual.tsv"
    with residual.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "family", "status", "license", "concrete_source",
                         "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for row in result["residual_rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["family"], row["status"],
                             row["license"], str(row["concrete_source"]).lower(),
                             str(row["implemented"]).lower(), row["instruction_bytes"],
                             row["instruction_sha256"], row["reason"]])
    summary = MANIFEST_DIR / "g2-touch-startup-closed-admission-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("rows", "residual_rows")}
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
    print(f"startup-closed sources: {result['metrics']['admitted_functions']}")
    print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch startup-closed admission failed: {exc}") from exc
