#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the fully closed touch record-processing source family (batch 10)."""

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
BATCH9_ANALYZER = TOOLS / "analyze_g2_touch_record_primitives_admission.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_closed_record_pipeline.c"
HEADER = TOUCH / "runtime_touch_closed_record_pipeline.h"
DEPENDENCIES = (
    TOUCH / "runtime_touch_leaf_primitives.c",
    TOUCH / "runtime_touch_record_primitives.c",
)

ADMISSIONS = {
    0x1AC4: (
        "reset_one_raw_pointer_graph", "open_cfw_touch_pipeline_1ac4_reset_one",
        {0x1AB8},
        "1AC4:push {r4, r5, r6, lr}|1AC6:movs r5, r1|1AC8:ldr r6, [r2, #0xc]|"
        "1ACA:lsls r3, r0, #3|1ACC:adds r0, r3, r0|1ACE:lsls r0, r0, #4|"
        "1AD0:adds r6, r6, r0|1AD2:movs r4, #0|1AD4:cmp r4, #0|"
        "1AD6:beq #0x1ada|1AD8:pop {r4, r5, r6, pc}|1ADA:ldr r0, [r6, #4]|"
        "1ADC:lsls r3, r5, #2|1ADE:adds r3, r3, r5|1AE0:lsls r3, r3, #1|"
        "1AE2:adds r0, r0, r3|1AE4:bl #0x1ab8|1AE8:adds r4, #1|1AEA:b #0x1ad4"),
    0x1AEC: (
        "reset_object_raw_pointer_graph", "open_cfw_touch_pipeline_1aec_reset_object",
        {0x1AC4},
        "1AEC:push {r4, r5, r6, lr}|1AEE:movs r5, r0|1AF0:movs r6, r1|"
        "1AF2:ldr r2, [r1, #0xc]|1AF4:lsls r3, r0, #3|1AF6:adds r3, r3, r0|"
        "1AF8:lsls r3, r3, #4|1AFA:adds r3, r2, r3|1AFC:movs r2, #0x7b|"
        "1AFE:ldrb r2, [r3, r2]|1B00:cmp r2, #7|1B02:beq #0x1b1a|"
        "1B04:ldrh r3, [r3, #0x38]|1B06:b #0x1b14|1B08:movs r2, r6|"
        "1B0A:movs r1, r4|1B0C:movs r0, r5|1B0E:bl #0x1ac4|"
        "1B12:movs r3, r4|1B14:subs r4, r3, #1|1B16:cmp r3, #0|"
        "1B18:bne #0x1b08|1B1A:pop {r4, r5, r6, pc}"),
    0x1B1C: (
        "reset_three_raw_pointer_graph", "open_cfw_touch_pipeline_1b1c_reset_three",
        {0x1AEC},
        "1B1C:push {r4, r5, r6, lr}|1B1E:movs r5, r0|1B20:movs r3, #3|"
        "1B22:b #0x1b2e|1B24:movs r1, r5|1B26:movs r0, r4|1B28:bl #0x1aec|"
        "1B2C:movs r3, r4|1B2E:subs r4, r3, #1|1B30:cmp r3, #0|"
        "1B32:bne #0x1b24|1B34:pop {r4, r5, r6, pc}"),
    0x1CC2: (
        "median_shift", "open_cfw_touch_pipeline_1cc2_median_shift", {0x1CA8},
        "1CC2:push {r4, r5, r6, lr}|1CC4:movs r5, r1|1CC6:movs r4, r2|"
        "1CC8:ldrh r0, [r1]|1CCA:ldrh r6, [r2]|1CCC:ldrh r2, [r2, #2]|"
        "1CCE:movs r1, r6|1CD0:bl #0x1ca8|1CD4:strh r6, [r4, #2]|"
        "1CD6:ldrh r3, [r5]|1CD8:strh r3, [r4]|1CDA:strh r0, [r5]|"
        "1CDC:pop {r4, r5, r6, pc}"),
    0x1CEE: (
        "record_update", "open_cfw_touch_pipeline_1cee_update",
        {0x1AB4, 0x1AB8, 0x1CDE},
        "1CEE:push {r3, r4, r5, r6, r7, lr}|1CF0:movs r5, r0|1CF2:movs r4, r1|"
        "1CF4:movs r7, r3|1CF6:bl #0x1ab4|1CFA:subs r6, r0, #0|"
        "1CFC:bne #0x1d50|1CFE:ldrh r0, [r4]|1D00:ldrh r1, [r4, #2]|"
        "1D02:cmp r0, r1|1D04:blo #0x1d0a|1D06:movs r3, #0|"
        "1D08:strb r3, [r4, #7]|1D0A:ldrh r3, [r5, #0x1c]|"
        "1D0C:adds r3, r3, r0|1D0E:cmp r1, r3|1D10:bls #0x1d28|"
        "1D12:ldrb r3, [r4, #7]|1D14:ldrh r2, [r5, #0xc]|1D16:cmp r3, r2|"
        "1D18:bhs #0x1d20|1D1A:adds r3, #1|1D1C:strb r3, [r4, #7]|"
        "1D1E:b #0x1d50|1D20:movs r0, r4|1D22:bl #0x1ab8|1D26:b #0x1d50|"
        "1D28:ldr r7, [r7]|1D2A:movs r3, #0x28|1D2C:ldrb r3, [r7, r3]|"
        "1D2E:cmp r3, #0|1D30:bne #0x1d3a|1D32:ldrh r3, [r5, #0x1a]|"
        "1D34:adds r3, r1, r3|1D36:cmp r0, r3|1D38:bhi #0x1d50|"
        "1D3A:lsls r1, r1, #8|1D3C:ldrb r3, [r4, #8]|1D3E:orrs r1, r3|"
        "1D40:movs r3, #0x22|1D42:ldrb r2, [r5, r3]|1D44:lsls r0, r0, #8|"
        "1D46:bl #0x1cde|1D4A:lsrs r3, r0, #8|1D4C:strh r3, [r4, #2]|"
        "1D4E:strb r0, [r4, #8]|1D50:movs r0, r6|"
        "1D52:pop {r3, r4, r5, r6, r7, pc}"),
    0x1D54: (
        "integer_or_fractional_blend", "open_cfw_touch_pipeline_1d54_blend",
        {0x1CDE},
        "1D54:push {r3, r4, r5, r6, r7, lr}|1D56:movs r6, r0|1D58:movs r4, r1|"
        "1D5A:movs r5, r2|1D5C:movs r7, r3|1D5E:movs r3, #0x74|"
        "1D60:ldrh r3, [r0, r3]|1D62:movs r2, #0x80|1D64:lsls r2, r2, #2|"
        "1D66:movs r1, #0xc0|1D68:lsls r1, r1, #2|1D6A:ands r3, r1|"
        "1D6C:cmp r3, r2|1D6E:beq #0x1d82|1D70:ldrh r0, [r4]|"
        "1D72:ldrh r1, [r5]|1D74:ldr r2, [r6, #0x24]|1D76:bl #0x1cde|"
        "1D7A:uxth r0, r0|1D7C:strh r0, [r5]|1D7E:strh r0, [r4]|"
        "1D80:pop {r3, r4, r5, r6, r7, pc}|1D82:ldrh r0, [r4]|"
        "1D84:lsls r0, r0, #8|1D86:ldrh r3, [r5]|1D88:lsls r3, r3, #8|"
        "1D8A:ldrb r1, [r7]|1D8C:orrs r1, r3|1D8E:ldr r2, [r6, #0x24]|"
        "1D90:bl #0x1cde|1D94:lsrs r3, r0, #8|1D96:uxth r3, r3|"
        "1D98:strh r3, [r5]|1D9A:strb r0, [r7]|1D9C:strh r3, [r4]|"
        "1D9E:b #0x1d80"),
    0x1DA0: (
        "ordered_filter_chain", "open_cfw_touch_pipeline_1da0_filter_chain",
        {0x1C6E, 0x1CC2, 0x1D54},
        "1DA0:push {r4, r5, r6, r7, lr}|1DA2:sub sp, #0xc|1DA4:movs r6, r0|"
        "1DA6:movs r7, r1|1DA8:movs r4, r2|1DAA:str r3, [sp, #4]|"
        "1DAC:movs r3, #0x74|1DAE:ldrh r5, [r0, r3]|1DB0:lsls r3, r5, #0x1b|"
        "1DB2:bmi #0x1dc0|1DB4:lsls r3, r5, #0x18|1DB6:bmi #0x1dc8|"
        "1DB8:lsls r5, r5, #0x15|1DBA:bmi #0x1dd8|1DBC:add sp, #0xc|"
        "1DBE:pop {r4, r5, r6, r7, pc}|1DC0:bl #0x1cc2|1DC4:adds r4, #4|"
        "1DC6:b #0x1db4|1DC8:ldr r3, [sp, #4]|1DCA:movs r2, r4|"
        "1DCC:movs r1, r7|1DCE:movs r0, r6|1DD0:bl #0x1d54|"
        "1DD4:adds r4, #2|1DD6:b #0x1db8|1DD8:movs r2, r4|"
        "1DDA:movs r1, r7|1DDC:movs r0, r6|1DDE:bl #0x1c6e|1DE2:b #0x1dbc"),
}

EXPECTED = {
    "input_concrete_gap": 86,
    "input_gap_instruction_bytes": 8324,
    "admitted_functions": 7,
    "admitted_instruction_bytes": 388,
    "closed_call_graph_admissions": 7,
    "literal_or_mmio_admissions": 0,
    "product_semantic_names_asserted": 0,
    "unimplemented_application_contracts_before": 74,
    "unimplemented_application_contracts_after": 67,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 79,
    "residual_gap_instruction_bytes": 7936,
    "row_digest": "2b0d15f94b6be1bef03570eadd788fe6aa56d77c243926a5e22cabf32f81f8d7",
    "residual_digest": "a0208a24278fd95fbe3eb8e375de4187fec584217eb209b1d719cb7d8be5b28d",
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


def _canonical_body(prefix, payload: bytes, entry: int, entries: set[int]) -> tuple[str, set[int]]:
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
                    f"closed pipeline target compile failed for {source.name}: {proc.stderr}")
            total += output.stat().st_size
    return total


def analyze(*, enforce_expected: bool = True) -> dict:
    batch9 = _load(BATCH9_ANALYZER, "touch_closed_pipeline_batch9")
    prefix = _load(PREFIX_ANALYZER, "touch_closed_pipeline_prefix")
    prior = batch9.analyze()
    residual_by_entry = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual_by_entry.keys(),
            "closed pipeline escaped batch-9 residual")
    require(all(residual_by_entry[entry]["family"] == "touch_application_processing"
                for entry in ADMISSIONS), "closed pipeline crossed provider boundary")

    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entry_universe = set(ADMISSIONS)
    for _kind, _symbol, callees, _body in ADMISSIONS.values():
        entry_universe.update(callees)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "closed pipeline MIT declarations changed")
    dependency_text = "".join(path.read_text() for path in DEPENDENCIES) + \
        (TOUCH / "runtime_touch_leaf_primitives.h").read_text() + \
        (TOUCH / "runtime_touch_record_primitives.h").read_text()
    target_object_bytes = _target_compile()

    rows = []
    for entry, (kind, symbol, expected_callees, expected_body) in sorted(ADMISSIONS.items()):
        prior_row = residual_by_entry[entry]
        canonical, callees = _canonical_body(prefix, payload, entry, entry_universe)
        require(canonical == expected_body,
                f"closed pipeline target body changed at {entry:#x}: {canonical}")
        require(callees == expected_callees,
                f"closed pipeline calls changed at {entry:#x}: {sorted(callees)}")
        require(combined.count(symbol) >= 1, f"closed pipeline source symbol missing: {symbol}")
        require("[pc," not in canonical,
                f"literal-backed pipeline row admitted at {entry:#x}")
        rows.append({
            "entry": entry,
            "symbol": symbol,
            "kind": kind,
            "status": "clean_room_closed_record_pipeline_source",
            "license": "MIT",
            "source": SOURCE.name,
            "product_semantics_asserted": False,
            "raw_pointer_graph": entry in {0x1AC4, 0x1AEC, 0x1B1C},
            "direct_callees": sorted(callees),
            "call_closure": "same_batch_or_previously_admitted_mit_source",
            "instruction_bytes": prior_row["instruction_bytes"],
            "instruction_sha256": prior_row["instruction_sha256"],
            "canonical_body_sha256": sha256(canonical.encode()),
            "evidence": "complete target control/data flow; direct calls resolve only to this batch or prior MIT leaf/record sources; no literal, MMIO or vendor body admitted",
        })

    required_dependency_symbols = {
        "open_cfw_touch_leaf_1ab4_constant_0",
        "open_cfw_touch_leaf_1ca8_median3",
        "open_cfw_touch_leaf_1cde_blend_u8",
        "open_cfw_touch_record_1ab8_reset",
        "open_cfw_touch_record_1c6e_history_filter",
    }
    require(all(symbol in dependency_text for symbol in required_dependency_symbols),
            "prior MIT dependency source closure changed")

    residual_rows = [row for entry, row in sorted(residual_by_entry.items())
                     if entry not in ADMISSIONS]
    metrics = {
        "input_concrete_gap": len(residual_by_entry),
        "input_gap_instruction_bytes": sum(row["instruction_bytes"]
                                             for row in residual_by_entry.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(row["instruction_bytes"] for row in rows),
        "closed_call_graph_admissions": len(rows),
        "literal_or_mmio_admissions": 0,
        "product_semantic_names_asserted": sum(
            row["product_semantics_asserted"] for row in rows),
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
        "residual_gap_instruction_bytes": sum(row["instruction_bytes"]
                                                for row in residual_rows),
        "row_digest": sha256(json.dumps(rows, sort_keys=True,
                                          separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(residual_rows, sort_keys=True,
                                               separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"closed pipeline {key} changed: {metrics[key]!r} != {expected!r}")

    return {
        "schema_version": 1,
        "component": "G2 touch closed record-processing source admission batch 10",
        "analysis_mode": "offline authenticated target control/data flow, host buffer tests and Cortex-M0+ compile; no MMIO or hardware execution",
        "metrics": metrics,
        "rows": rows,
        "residual_rows": residual_rows,
        "source": {
            "path": str(SOURCE.relative_to(ROOT)),
            "license": "MIT",
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
            "note": "ten Em_EEPROM EULA rows, system handoff and halt remain typed external/unavailable; ambiguous larger pointer-table loops remain unimplemented",
        },
        "exclusions": "0x1B6C, 0x1C54 and 0x2638 larger pointer-table loops; literal tables, globals, MMIO, EULA bodies, system handoff and halt remain unadmitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-closed-record-pipeline-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "entry", "symbol", "kind", "status", "license", "source",
            "raw_pointer_graph", "direct_callees", "call_closure",
            "product_semantics_asserted", "instruction_bytes", "instruction_sha256",
            "canonical_body_sha256", "evidence",
        ])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["symbol"], row["kind"], row["status"],
                row["license"], row["source"], str(row["raw_pointer_graph"]).lower(),
                ",".join(f"0x{entry:04X}" for entry in row["direct_callees"]),
                row["call_closure"], str(row["product_semantics_asserted"]).lower(),
                row["instruction_bytes"], row["instruction_sha256"],
                row["canonical_body_sha256"], row["evidence"],
            ])
    residual = MANIFEST_DIR / "g2-touch-closed-record-pipeline-residual.tsv"
    with residual.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "family", "status", "license", "concrete_source",
                         "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for row in result["residual_rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["family"], row["status"], row["license"],
                str(row["concrete_source"]).lower(), str(row["implemented"]).lower(),
                row["instruction_bytes"], row["instruction_sha256"], row["reason"],
            ])
    summary = MANIFEST_DIR / "g2-touch-closed-record-pipeline-admission-summary.json"
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
                          if key not in ("rows", "residual_rows")},
                         indent=2, sort_keys=True))
    else:
        print(f"closed record-processing sources: {result['metrics']['admitted_functions']}")
        print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch closed pipeline admission failed: {exc}") from exc
