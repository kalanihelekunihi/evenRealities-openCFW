#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the touch configuration/start family with typed providers (batch 14)."""

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
BATCH13_ANALYZER = TOOLS / "analyze_g2_touch_selection_update_pipeline_admission.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_configuration_start_pipeline.c"
HEADER = TOUCH / "runtime_touch_configuration_start_pipeline.h"

# kind, source symbol, canonical SHA-256, bytes, exact direct targets
ADMISSIONS = {
    0x1944: (
        "capture_and_event_start", "open_cfw_touch_config_1944_start",
        "18ea1d396d5385f5c20b629728ef657d1d822d2ecb0c638dcd608be38b138990",
        46, {0x37C0, 0x5CA0},
    ),
    0x1972: (
        "start_wrapper", "open_cfw_touch_config_1972_start_wrapper",
        "de66b20c719e9c639fbc89c13b5f246f15544b333bbd1c3a81b2daaf0bc753ec",
        8, {0x1944},
    ),
    0x197C: (
        "argument_relative_configuration_initializer",
        "open_cfw_touch_config_197c_initialize",
        "eb0d72804fc6004926b00b3b75b79e379353f4205b1c5bec452f1fa9b625e501",
        300, {0x1972, 0x37C0},
    ),
}

EXPECTED = {
    "input_concrete_gap": 63,
    "input_gap_instruction_bytes": 5632,
    "admitted_functions": 3,
    "admitted_instruction_bytes": 354,
    "typed_provider_admissions": 2,
    "resident_table_admissions": 0,
    "mmio_admissions": 0,
    "product_semantic_names_asserted": 0,
    "unimplemented_application_contracts_before": 51,
    "unimplemented_application_contracts_after": 48,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 60,
    "residual_gap_instruction_bytes": 5278,
    "row_digest": "5a407f4bd82a9ad1ea45531c029c8b8c633602c244be1dfa7e55d76bbe26ba4c",
    "residual_digest": "ec169645fbdc18a998a98958c072f3b23b14fd32149d1ed3c9002c43a65156d9",
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


def _canonical(prefix, payload: bytes, entry: int, entries: set[int]) -> tuple[str, set[int]]:
    body = prefix._walk(payload, entry, entries)
    canonical = "|".join(
        f"{address:04X}:{insn.mnemonic} {insn.op_str}"
        for address, insn in sorted(body["instructions"].items())
    )
    return canonical, {call["target"] for call in body["calls"]}


def _target_compile() -> int:
    clang = shutil.which("clang")
    require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory() as raw:
        output = Path(raw) / "touch-config-start.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0,
                f"configuration/start target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected: bool = True) -> dict:
    batch13 = _load(BATCH13_ANALYZER, "touch_config_batch13")
    prefix = _load(PREFIX_ANALYZER, "touch_config_prefix")
    prior = batch13.analyze()
    residual_by_entry = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual_by_entry.keys(),
            "configuration/start family escaped batch-13 residual")
    require(all(residual_by_entry[entry]["family"] == "touch_application_processing"
                for entry in ADMISSIONS), "configuration/start crossed provider boundary")

    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(ADMISSIONS)
    for _kind, _symbol, _digest, _size, callees in ADMISSIONS.values():
        entries.update(callees)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "configuration/start MIT declarations changed")
    require("open_cfw_touch_capture_provider" in combined and
            "open_cfw_touch_event_provider" in combined,
            "typed provider boundary changed")
    for offset, value in ((0x1AA8, 0x0000028F), (0x1AAC, 0x0000084C),
                          (0x1AB0, 0x0000F424)):
        require(struct.unpack_from("<I", payload, offset)[0] == value,
                f"configuration literal changed at {offset:#x}")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (kind, symbol, body_digest, expected_bytes, expected_callees) in sorted(ADMISSIONS.items()):
        prior_row = residual_by_entry[entry]
        canonical, callees = _canonical(prefix, payload, entry, entries)
        require(sha256(canonical.encode()) == body_digest,
                f"configuration/start canonical body changed at {entry:#x}")
        require(prior_row["instruction_bytes"] == expected_bytes,
                f"configuration/start byte span changed at {entry:#x}")
        require(callees == expected_callees,
                f"configuration/start calls changed at {entry:#x}: {sorted(callees)}")
        require(combined.count(symbol) >= 1, f"configuration/start symbol missing: {symbol}")
        external = sorted(callees & {0x37C0, 0x5CA0})
        rows.append({
            "entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_configuration_source_with_typed_providers",
            "license": "MIT", "source": SOURCE.name,
            "direct_callees": sorted(callees),
            "typed_providers": external,
            "provider_licenses": ["MIT OR GPL-3.0-only wrapper" if value == 0x37C0
                                  else "Apache-2.0" for value in external],
            "resident_table_dependency": False,
            "product_semantics_asserted": False,
            "instruction_bytes": prior_row["instruction_bytes"],
            "instruction_sha256": prior_row["instruction_sha256"],
            "canonical_body_sha256": body_digest,
            "evidence": "complete argument-relative target control/data flow; 0x37C0 event dispatch and 0x5CA0 CAT2 capture remain injected typed providers; no MMIO, resident table or provider body admitted",
        })

    residual_rows = [row for entry, row in sorted(residual_by_entry.items())
                     if entry not in ADMISSIONS]
    metrics = {
        "input_concrete_gap": len(residual_by_entry),
        "input_gap_instruction_bytes": sum(row["instruction_bytes"] for row in residual_by_entry.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(row["instruction_bytes"] for row in rows),
        "typed_provider_admissions": sum(bool(row["typed_providers"]) for row in rows),
        "resident_table_admissions": 0, "mmio_admissions": 0,
        "product_semantic_names_asserted": 0,
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
                    f"configuration/start {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch configuration/start source admission batch 14",
        "analysis_mode": "offline authenticated target control/data flow, injected provider callbacks, host tokenized 32-bit pointer graph and Cortex-M0+ compile; no MMIO or hardware execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {
            "path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
            "sha256": sha256(SOURCE.read_bytes()),
            "target_closure_object_bytes": target_object_bytes,
        },
        "integration": "isolated source candidates only; not production-routed",
        "remaining": {
            "concrete_source_or_implementation_functions": len(residual_rows),
            "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
            "unimplemented_clean_room_application_contracts":
                metrics["unimplemented_application_contracts_after"],
            "typed_external_or_unavailable_functions": 12,
            "note": "ten Em_EEPROM EULA rows, system handoff and halt remain external; resident 0xB41C/0xB4C4 loaders and ambiguous 0x1B6C/0x1C54/0x2638 boundaries remain unimplemented",
        },
        "exclusions": "resident-region literal tables, 0x1B6C/0x1C54/0x2638, MMIO, EULA bodies, system handoff and halt remain unadmitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-configuration-start-pipeline-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license", "source",
                         "direct_callees", "typed_providers", "provider_licenses",
                         "resident_table_dependency", "product_semantics_asserted",
                         "instruction_bytes", "instruction_sha256", "canonical_body_sha256",
                         "evidence"])
        for row in result["rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["symbol"], row["kind"],
                             row["status"], row["license"], row["source"],
                             ",".join(f"0x{x:04X}" for x in row["direct_callees"]),
                             ",".join(f"0x{x:04X}" for x in row["typed_providers"]),
                             ",".join(row["provider_licenses"]),
                             str(row["resident_table_dependency"]).lower(),
                             str(row["product_semantics_asserted"]).lower(),
                             row["instruction_bytes"], row["instruction_sha256"],
                             row["canonical_body_sha256"], row["evidence"]])
    residual = MANIFEST_DIR / "g2-touch-configuration-start-pipeline-residual.tsv"
    with residual.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "family", "status", "license", "concrete_source",
                         "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for row in result["residual_rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["family"], row["status"], row["license"],
                             str(row["concrete_source"]).lower(), str(row["implemented"]).lower(),
                             row["instruction_bytes"], row["instruction_sha256"], row["reason"]])
    summary = MANIFEST_DIR / "g2-touch-configuration-start-pipeline-admission-summary.json"
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
    print(f"configuration/start sources: {result['metrics']['admitted_functions']}")
    print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch configuration/start admission failed: {exc}") from exc
