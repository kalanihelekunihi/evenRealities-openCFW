#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the evidence-closed touch selection/update family (batch 13)."""

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
BATCH12_ANALYZER = TOOLS / "analyze_g2_touch_application_packet_pipeline_admission.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_selection_update_pipeline.c"
HEADER = TOUCH / "runtime_touch_selection_update_pipeline.h"
DEPENDENCIES = (
    TOUCH / "runtime_touch_application_state_pipeline.c",
    TOUCH / "runtime_touch_leaf_primitives.c",
)

# kind, source symbol, canonical-body SHA-256, instruction bytes, direct targets
ADMISSIONS = {
    0x15CC: (
        "three_sample_peak_selection", "open_cfw_touch_select_15cc_peak",
        "dc767e3f2144266d3631e2b55b8b381f77305842565cc98b7cbd4787f30b5d43",
        258, {0x73C0, 0x74D4},
    ),
    0x2794: (
        "lane_state_and_selection_update", "open_cfw_touch_select_2794_update",
        "e6db6c6afdc6ce8258b499e6163e28dfeb65da3619fff840e83872c2f5c40464",
        270, {0x15CC, 0x172A, 0x772C},
    ),
    0x28A2: (
        "mode_selection_dispatch", "open_cfw_touch_select_28a2_dispatch",
        "1227f4cd2f3ad44609791b1f5e56a609e6edd53991d4def9d0895517e6d3571b",
        30, {0x270A, 0x2794},
    ),
}

EXPECTED = {
    "input_concrete_gap": 66,
    "input_gap_instruction_bytes": 6190,
    "admitted_functions": 3,
    "admitted_instruction_bytes": 558,
    "internally_closed_admissions": 3,
    "resident_table_admissions": 0,
    "mmio_admissions": 0,
    "product_semantic_names_asserted": 0,
    "unimplemented_application_contracts_before": 54,
    "unimplemented_application_contracts_after": 51,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 63,
    "residual_gap_instruction_bytes": 5632,
    "row_digest": "49bc17c358b41d4d4cb8d61532c5a9358de12a2cf97ff6884b7603982b53576a",
    "residual_digest": "13d3822f7038c45be1d4d4533cbf30e98dcd469e3c2c214ae0b83cbd4b04ea6f",
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
                    f"selection/update target compile failed for {source.name}: {proc.stderr}")
            total += output.stat().st_size
    return total


def analyze(*, enforce_expected: bool = True) -> dict:
    batch12 = _load(BATCH12_ANALYZER, "touch_selection_batch12")
    prefix = _load(PREFIX_ANALYZER, "touch_selection_prefix")
    prior = batch12.analyze()
    residual_by_entry = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual_by_entry.keys(),
            "selection/update family escaped batch-12 residual")
    require(all(residual_by_entry[entry]["family"] == "touch_application_processing"
                for entry in ADMISSIONS), "selection/update family crossed provider boundary")

    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(ADMISSIONS)
    for _kind, _symbol, _digest, _size, callees in ADMISSIONS.values():
        entries.update(callees)
    combined = SOURCE.read_text() + HEADER.read_text()
    dependency_text = "".join(path.read_text() for path in DEPENDENCIES)
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "selection/update MIT declarations changed")
    for symbol in ("open_cfw_touch_state_172a_sync_records",
                   "open_cfw_touch_state_270a_update_lanes"):
        require(symbol in dependency_text, f"selection/update dependency changed: {symbol}")
    require(struct.unpack_from("<I", payload, 0x16D0)[0] == 0x0000FFFF,
            "shipped peak-selection sentinel changed")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (kind, symbol, body_digest, expected_bytes, expected_callees) in sorted(ADMISSIONS.items()):
        prior_row = residual_by_entry[entry]
        canonical, callees = _canonical(prefix, payload, entry, entries)
        require(sha256(canonical.encode()) == body_digest,
                f"selection/update canonical body changed at {entry:#x}")
        require(prior_row["instruction_bytes"] == expected_bytes,
                f"selection/update byte span changed at {entry:#x}")
        require(callees == expected_callees,
                f"selection/update calls changed at {entry:#x}: {sorted(callees)}")
        require(combined.count(symbol) >= 1, f"selection/update symbol missing: {symbol}")
        rows.append({
            "entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_argument_relative_selection_update_source",
            "license": "MIT", "source": SOURCE.name,
            "direct_callees": sorted(callees),
            "call_closure": "same_batch_or_previously_admitted_mit_or_exact_runtime_behavior",
            "resident_table_dependency": False,
            "shipped_immediate_literal": "0x16D0=0x0000FFFF" if entry == 0x15CC else "",
            "product_semantics_asserted": False,
            "instruction_bytes": prior_row["instruction_bytes"],
            "instruction_sha256": prior_row["instruction_sha256"],
            "canonical_body_sha256": body_digest,
            "evidence": "complete target control/data flow over argument-relative buffers; division and copying use MIT clean-room primitives; no MMIO, resident table or vendor body admitted",
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
                    f"selection/update {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch selection/update source admission batch 13",
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
    admitted = MANIFEST_DIR / "g2-touch-selection-update-pipeline-admission.tsv"
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
    residual = MANIFEST_DIR / "g2-touch-selection-update-pipeline-residual.tsv"
    with residual.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "family", "status", "license", "concrete_source",
                         "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for row in result["residual_rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["family"], row["status"], row["license"],
                             str(row["concrete_source"]).lower(), str(row["implemented"]).lower(),
                             row["instruction_bytes"], row["instruction_sha256"], row["reason"]])
    summary = MANIFEST_DIR / "g2-touch-selection-update-pipeline-admission-summary.json"
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
        print(f"selection/update sources: {result['metrics']['admitted_functions']}")
        print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch selection/update admission failed: {exc}") from exc
