#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the closed touch application packet/state builder pair (batch 12)."""

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
BATCH11_ANALYZER = TOOLS / "analyze_g2_touch_application_state_pipeline_admission.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_application_packet_pipeline.c"
HEADER = TOUCH / "runtime_touch_application_packet_pipeline.h"
DEPENDENCIES = (
    TOUCH / "runtime_touch_application_state_pipeline.c",
    TOUCH / "runtime_touch_leaf_primitives.c",
    TOUCH / "runtime_touch_record_primitives.c",
)

ADMISSIONS = {
    0x2248: (
        "entry_packet_builder", "open_cfw_touch_packet_2248_build_entry",
        "cce6bd6384e3f1b3e353610c7d0371e6aeade7c9249ce33f0c2a2ab70cddbce1",
        342, {0x1EBC, 0x2228}),
    0x23A4: (
        "group_packet_builder", "open_cfw_touch_packet_23a4_build_group",
        "d3cada4bfc401353ef05ce15ce1d2d69bba540ae85d5fe442897360e3b6605bf",
        452, {0x1E88, 0x2248}),
}

EXPECTED = {
    "input_concrete_gap": 68,
    "input_gap_instruction_bytes": 6984,
    "admitted_functions": 2,
    "admitted_instruction_bytes": 794,
    "internally_closed_admissions": 2,
    "resident_table_admissions": 0,
    "mmio_admissions": 0,
    "product_semantic_names_asserted": 0,
    "unimplemented_application_contracts_before": 56,
    "unimplemented_application_contracts_after": 54,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 66,
    "residual_gap_instruction_bytes": 6190,
    "row_digest": "f4be346e0ac2cdcab927ee591be95da813ec4e618d7d7a0e4b918f67c9779a69",
    "residual_digest": "9e650e64591ca094d595771141d08d792a80f912d3df13cd5f7a7b998e0bcede",
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
    total = 0
    with tempfile.TemporaryDirectory() as raw:
        for source in (SOURCE, *DEPENDENCIES):
            output = Path(raw) / (source.stem + ".o")
            proc = subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(TOUCH), "-c", str(source), "-o", str(output),
            ], capture_output=True, text=True)
            require(proc.returncode == 0,
                    f"packet pipeline target compile failed for {source.name}: {proc.stderr}")
            total += output.stat().st_size
    return total


def analyze(*, enforce_expected: bool = True) -> dict:
    batch11 = _load(BATCH11_ANALYZER, "touch_packet_batch11")
    prefix = _load(PREFIX_ANALYZER, "touch_packet_prefix")
    prior = batch11.analyze()
    residual_by_entry = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual_by_entry.keys(),
            "packet family escaped batch-11 residual")
    require(all(residual_by_entry[entry]["family"] == "touch_application_processing"
                for entry in ADMISSIONS), "packet family crossed provider boundary")

    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(ADMISSIONS)
    for _kind, _symbol, _digest, _size, callees in ADMISSIONS.values():
        entries.update(callees)
    combined = SOURCE.read_text() + HEADER.read_text()
    dependency_text = "".join(path.read_text() for path in DEPENDENCIES)
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "packet pipeline MIT declarations changed")
    for symbol in ("open_cfw_touch_state_1ebc_pack",
                   "open_cfw_touch_leaf_2228_mode_scale",
                   "open_cfw_touch_record_1e88_mask3"):
        require(symbol in dependency_text, f"packet dependency changed: {symbol}")
    require(struct.unpack_from("<I", payload, 0x23A0)[0] == 0x0FFF0000,
            "shipped 0x2248 immediate-mask literal changed")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (kind, symbol, body_digest, expected_bytes, expected_callees) in sorted(ADMISSIONS.items()):
        prior_row = residual_by_entry[entry]
        canonical, callees = _canonical(prefix, payload, entry, entries)
        require(sha256(canonical.encode()) == body_digest,
                f"packet canonical body changed at {entry:#x}")
        require(prior_row["instruction_bytes"] == expected_bytes,
                f"packet byte span changed at {entry:#x}")
        require(callees == expected_callees,
                f"packet calls changed at {entry:#x}: {sorted(callees)}")
        require(combined.count(symbol) >= 1, f"packet source symbol missing: {symbol}")
        require("[pc," not in canonical or entry == 0x2248,
                f"unapproved packet literal at {entry:#x}")
        rows.append({
            "entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_argument_relative_packet_pipeline_source",
            "license": "MIT", "source": SOURCE.name,
            "direct_callees": sorted(callees),
            "call_closure": "same_batch_or_previously_admitted_mit_source",
            "resident_table_dependency": False,
            "shipped_immediate_literal": "0x23A0=0x0FFF0000" if entry == 0x2248 else "",
            "product_semantics_asserted": False,
            "instruction_bytes": prior_row["instruction_bytes"],
            "instruction_sha256": prior_row["instruction_sha256"],
            "canonical_body_sha256": body_digest,
            "evidence": "complete target control/data flow over argument-relative buffers; no MMIO, resident table or vendor body admitted",
        })

    residual_rows = [row for entry, row in sorted(residual_by_entry.items())
                     if entry not in ADMISSIONS]
    metrics = {
        "input_concrete_gap": len(residual_by_entry),
        "input_gap_instruction_bytes": sum(row["instruction_bytes"] for row in residual_by_entry.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(row["instruction_bytes"] for row in rows),
        "internally_closed_admissions": len(rows),
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
                    f"packet pipeline {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch application packet source admission batch 12",
        "analysis_mode": "offline authenticated target control/data flow, host tokenized 32-bit pointer graph and Cortex-M0+ compile; no MMIO or hardware execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {
            "path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
            "sha256": sha256(SOURCE.read_bytes()),
            "target_closure_object_bytes": target_object_bytes,
            "dependencies": [str(path.relative_to(ROOT)) for path in DEPENDENCIES],
        },
        "integration": "isolated source candidates only; not production-routed",
        "remaining": {
            "concrete_source_or_implementation_functions": len(residual_rows),
            "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
            "unimplemented_clean_room_application_contracts":
                metrics["unimplemented_application_contracts_after"],
            "typed_external_or_unavailable_functions": 12,
            "note": "ten Em_EEPROM EULA rows, system handoff and halt remain external; resident 0xB41C loader and ambiguous 0x1B6C/0x1C54/0x2638 boundaries remain unimplemented",
        },
        "exclusions": "resident-region literal tables, 0x1B6C/0x1C54/0x2638, MMIO, EULA bodies, system handoff and halt remain unadmitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-application-packet-pipeline-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license", "source",
                         "direct_callees", "call_closure", "resident_table_dependency",
                         "shipped_immediate_literal", "product_semantics_asserted",
                         "instruction_bytes", "instruction_sha256", "canonical_body_sha256",
                         "evidence"])
        for row in result["rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["symbol"], row["kind"],
                             row["status"], row["license"], row["source"],
                             ",".join(f"0x{x:04X}" for x in row["direct_callees"]),
                             row["call_closure"], str(row["resident_table_dependency"]).lower(),
                             row["shipped_immediate_literal"],
                             str(row["product_semantics_asserted"]).lower(),
                             row["instruction_bytes"], row["instruction_sha256"],
                             row["canonical_body_sha256"], row["evidence"]])
    residual = MANIFEST_DIR / "g2-touch-application-packet-pipeline-residual.tsv"
    with residual.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "family", "status", "license", "concrete_source",
                         "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for row in result["residual_rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["family"], row["status"], row["license"],
                             str(row["concrete_source"]).lower(), str(row["implemented"]).lower(),
                             row["instruction_bytes"], row["instruction_sha256"], row["reason"]])
    summary = MANIFEST_DIR / "g2-touch-application-packet-pipeline-admission-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("rows", "residual_rows")}
    slim["admitted_row_count"] = len(result["rows"])
    slim["residual_row_count"] = len(result["residual_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [admitted, residual, summary]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifests", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    if args.json:
        print(json.dumps({key: value for key, value in result.items()
                          if key not in ("rows", "residual_rows")}, indent=2, sort_keys=True))
    else:
        print(f"packet pipeline sources: {result['metrics']['admitted_functions']}")
        print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch packet pipeline admission failed: {exc}") from exc
