#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the internally closed touch application-state family (batch 11)."""

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
BATCH10_ANALYZER = TOOLS / "analyze_g2_touch_closed_record_pipeline_admission.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_application_state_pipeline.c"
HEADER = TOUCH / "runtime_touch_application_state_pipeline.h"
LEAF_SOURCE = TOUCH / "runtime_touch_leaf_primitives.c"

# kind, symbol, canonical-body SHA-256, bytes, exact direct targets
ADMISSIONS = {
    0x16D4: ("conditional_copy8", "open_cfw_touch_state_16d4_copy8",
             "7082073da8f5e1241d05b0d66d94470cf2b85ee7ac41773385b7e42f830495dd", 18, {0x772C}),
    0x16E6: ("conditional_pair_blend", "open_cfw_touch_state_16e6_blend_pair",
             "5998466885abe37f1de4114cc27a940fabffb909559fbf419bb41ebfc842e73f", 68, {0x1CDE}),
    0x172A: ("record_sync", "open_cfw_touch_state_172a_sync_records",
             "99d0f50b145f60c6658b71e190cf9dcdb86e9f799d04bffab0e84031bfb0bb9a", 148,
             {0x16D4, 0x16E6}),
    0x1EBC: ("argument_graph_pack", "open_cfw_touch_state_1ebc_pack",
             "13ce51aa14d28d2a43f0bb8b82d4b6f91f8ccba329d1cb6d4564a1d4fc50ae02", 250, set()),
    0x2568: ("object_state_reset", "open_cfw_touch_state_2568_reset_object",
             "1b74071e6f08612f608f68cdfb63dede9e843f84d45939950ae8ee2f8c0e6e2c", 142,
             {0x76D4}),
    0x270A: ("lane_counter_update", "open_cfw_touch_state_270a_update_lanes",
             "38b7885b8d0b4178627bfa4f207b0ebdcb01b0c57480c79b2fccd47753be09c9", 138, set()),
    0x28C0: ("object_value_cap", "open_cfw_touch_state_28c0_cap_object",
             "306400ef9d6971797cba4d9ebd94ed5bf6a5eb04f079cc3730f892ab6a310456", 66, set()),
    0x2902: ("enabled_object_value_cap", "open_cfw_touch_state_2902_cap_enabled_object",
             "cd23e5e8ee766e4aa2e24001e2f894ca3f25fd30d0451123ae2f98cb97ad2dd6", 28,
             {0x28C0}),
    0x291E: ("single_record_value_cap", "open_cfw_touch_state_291e_cap_record",
             "772b83cd5411d54e8b7fa2a733de52e74d8c42764a981e03e59ed99bc6ef2d3f", 56, set()),
    0x2956: ("enabled_record_value_cap", "open_cfw_touch_state_2956_cap_enabled_record",
             "c4b717d36351e90c96f6bb22bc02bf655a99da23d90738c965fde4d632831ee0", 28,
             {0x291E}),
    0x298E: ("nested_status_bit80", "open_cfw_touch_state_298e_status80",
             "d3dc41ca2a590a92d76f76f84487e6cab818d0d4dac056e37a544bf9a49e3bec", 10, set()),
}

EXPECTED = {
    "input_concrete_gap": 79,
    "input_gap_instruction_bytes": 7936,
    "admitted_functions": 11,
    "admitted_instruction_bytes": 952,
    "internally_closed_admissions": 11,
    "resident_table_admissions": 0,
    "mmio_admissions": 0,
    "product_semantic_names_asserted": 0,
    "unimplemented_application_contracts_before": 67,
    "unimplemented_application_contracts_after": 56,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 68,
    "residual_gap_instruction_bytes": 6984,
    "row_digest": "2a95b1df745feb61997f82f7a3f3db12066589fbdb288600757d71ee8da3a5ab",
    "residual_digest": "cc3f01aaa27907e1ccf7eac6a880a8fc77caa5679b5ba090c58a3321cbd7c94d",
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
        for source in (SOURCE, LEAF_SOURCE):
            output = Path(raw) / (source.stem + ".o")
            proc = subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(TOUCH), "-c", str(source), "-o", str(output),
            ], capture_output=True, text=True)
            require(proc.returncode == 0,
                    f"application-state target compile failed for {source.name}: {proc.stderr}")
            total += output.stat().st_size
    return total


def analyze(*, enforce_expected: bool = True) -> dict:
    batch10 = _load(BATCH10_ANALYZER, "touch_application_state_batch10")
    prefix = _load(PREFIX_ANALYZER, "touch_application_state_prefix")
    prior = batch10.analyze()
    residual_by_entry = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual_by_entry.keys(),
            "application-state family escaped batch-10 residual")
    require(all(residual_by_entry[entry]["family"] == "touch_application_processing"
                for entry in ADMISSIONS), "application-state family crossed provider boundary")

    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(ADMISSIONS)
    for _kind, _symbol, _digest, _size, callees in ADMISSIONS.values():
        entries.update(callees)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "application-state MIT declarations changed")
    require("open_cfw_touch_leaf_1cde_blend_u8" in LEAF_SOURCE.read_text(),
            "prior MIT blend dependency changed")
    require(struct.unpack_from("<I", payload, 0x1FB8)[0] == 0x0FFF0000,
            "shipped 0x1EBC immediate-mask literal changed")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (kind, symbol, body_digest, expected_bytes, expected_callees) in sorted(ADMISSIONS.items()):
        prior_row = residual_by_entry[entry]
        canonical, callees = _canonical(prefix, payload, entry, entries)
        require(sha256(canonical.encode()) == body_digest,
                f"application-state canonical body changed at {entry:#x}")
        require(prior_row["instruction_bytes"] == expected_bytes,
                f"application-state byte span changed at {entry:#x}")
        require(callees == expected_callees,
                f"application-state calls changed at {entry:#x}: {sorted(callees)}")
        require(combined.count(symbol) >= 1,
                f"application-state source symbol missing: {symbol}")
        pc_literal = "[pc," in canonical
        require(not pc_literal or entry == 0x1EBC,
                f"unapproved literal-backed row at {entry:#x}")
        rows.append({
            "entry": entry,
            "symbol": symbol,
            "kind": kind,
            "status": "clean_room_argument_relative_application_state_source",
            "license": "MIT",
            "source": SOURCE.name,
            "product_semantics_asserted": False,
            "direct_callees": sorted(callees),
            "call_closure": "same_batch_or_established_mit_or_exact_runtime_behavior",
            "resident_table_dependency": False,
            "shipped_immediate_literal": "0x1FB8=0x0FFF0000" if entry == 0x1EBC else "",
            "instruction_bytes": prior_row["instruction_bytes"],
            "instruction_sha256": prior_row["instruction_sha256"],
            "canonical_body_sha256": body_digest,
            "evidence": "complete target control/data flow over argument-relative buffers; no MMIO, resident table or vendor body admitted",
        })

    residual_rows = [row for entry, row in sorted(residual_by_entry.items())
                     if entry not in ADMISSIONS]
    metrics = {
        "input_concrete_gap": len(residual_by_entry),
        "input_gap_instruction_bytes": sum(row["instruction_bytes"]
                                             for row in residual_by_entry.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(row["instruction_bytes"] for row in rows),
        "internally_closed_admissions": len(rows),
        "resident_table_admissions": 0,
        "mmio_admissions": 0,
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
        "row_digest": sha256(json.dumps(rows, sort_keys=True,
                                          separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(residual_rows, sort_keys=True,
                                               separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"application-state {key} changed: {metrics[key]!r} != {expected!r}")

    return {
        "schema_version": 1,
        "component": "G2 touch application-state source admission batch 11",
        "analysis_mode": "offline authenticated target control/data flow, host tokenized 32-bit pointer graph and Cortex-M0+ compile; no MMIO or hardware execution",
        "metrics": metrics,
        "rows": rows,
        "residual_rows": residual_rows,
        "source": {
            "path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
            "sha256": sha256(SOURCE.read_bytes()),
            "target_closure_object_bytes": target_object_bytes,
            "dependencies": [str(LEAF_SOURCE.relative_to(ROOT)),
                             "exact memcpy/memset behavior reimplemented as bounded MIT loops"],
        },
        "integration": "isolated source candidates only; not production-routed",
        "remaining": {
            "concrete_source_or_implementation_functions": len(residual_rows),
            "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
            "unimplemented_clean_room_application_contracts":
                metrics["unimplemented_application_contracts_after"],
            "typed_external_or_unavailable_functions": 12,
            "note": "ten Em_EEPROM EULA rows, system handoff and halt remain external; resident 0xB41C table loader and ambiguous 0x1B6C/0x1C54/0x2638 boundaries remain unimplemented",
        },
        "exclusions": "resident-region literal tables, 0x1B6C/0x1C54/0x2638, MMIO, EULA bodies, system handoff and halt remain unadmitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-application-state-pipeline-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license", "source",
                         "direct_callees", "call_closure", "resident_table_dependency",
                         "shipped_immediate_literal", "product_semantics_asserted",
                         "instruction_bytes", "instruction_sha256", "canonical_body_sha256",
                         "evidence"])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["symbol"], row["kind"], row["status"],
                row["license"], row["source"],
                ",".join(f"0x{value:04X}" for value in row["direct_callees"]),
                row["call_closure"], str(row["resident_table_dependency"]).lower(),
                row["shipped_immediate_literal"],
                str(row["product_semantics_asserted"]).lower(), row["instruction_bytes"],
                row["instruction_sha256"], row["canonical_body_sha256"], row["evidence"],
            ])
    residual = MANIFEST_DIR / "g2-touch-application-state-pipeline-residual.tsv"
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
    summary = MANIFEST_DIR / "g2-touch-application-state-pipeline-admission-summary.json"
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
        print(f"application-state sources: {result['metrics']['admitted_functions']}")
        print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch application-state admission failed: {exc}") from exc
