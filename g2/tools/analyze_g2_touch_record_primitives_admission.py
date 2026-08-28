#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit argument-relative, call-free touch record transforms."""

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
SEMANTIC_ANALYZER = TOOLS / "analyze_g2_touch_relocated_semantics.py"
LEAF_ANALYZER = TOOLS / "analyze_g2_touch_leaf_primitives_admission.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_record_primitives.c"
HEADER = TOUCH / "runtime_touch_record_primitives.h"

ADMISSIONS = {
    0x1AB8: ("record_reset", "open_cfw_touch_record_1ab8_reset",
             "1AB8:movs r3, #0|1ABA:strb r3, [r0, #8]|1ABC:ldrh r2, [r0]|"
             "1ABE:strh r2, [r0, #2]|1AC0:strb r3, [r0, #7]|1AC2:bx lr"),
    0x1B36: ("copy_optional_gate", "open_cfw_touch_record_1b36_copy_gate",
             "1B36:ldrh r1, [r1]|1B38:strh r1, [r2]|1B3A:cmp r3, #0|"
             "1B3C:beq #0x1b50|1B3E:movs r2, #0x74|1B40:ldrh r2, [r0, r2]|"
             "1B42:movs r1, #0x80|1B44:lsls r1, r1, #2|1B46:movs r0, #0xc0|"
             "1B48:lsls r0, r0, #2|1B4A:ands r2, r0|1B4C:cmp r2, r1|"
             "1B4E:beq #0x1b52|1B50:bx lr|1B52:movs r2, #0|"
             "1B54:strb r2, [r3]|1B56:b #0x1b50"),
    0x1B58: ("replicate2", "open_cfw_touch_record_1b58_replicate2",
             "1B58:ldrh r3, [r1]|1B5A:strh r3, [r2]|1B5C:strh r3, [r2, #2]|"
             "1B5E:bx lr"),
    0x1B60: ("replicate3", "open_cfw_touch_record_1b60_replicate3",
             "1B60:ldrh r3, [r1]|1B62:strh r3, [r2]|1B64:strh r3, [r2, #2]|"
             "1B66:ldrh r3, [r1]|1B68:strh r3, [r2, #4]|1B6A:bx lr"),
    0x1C6E: ("history_filter", "open_cfw_touch_record_1c6e_history_filter",
             "1C6E:push {r4, r5, lr}|1C70:movs r3, #0x74|1C72:ldrh r3, [r0, r3]|"
             "1C74:movs r0, #0x80|1C76:lsls r0, r0, #5|1C78:movs r4, #0xc0|"
             "1C7A:lsls r4, r4, #5|1C7C:ands r3, r4|1C7E:cmp r3, r0|"
             "1C80:beq #0x1c92|1C82:ldrh r3, [r1]|1C84:ldrh r0, [r2]|"
             "1C86:adds r3, r3, r0|1C88:lsrs r3, r3, #1|1C8A:ldrh r0, [r1]|"
             "1C8C:strh r0, [r2]|1C8E:strh r3, [r1]|1C90:pop {r4, r5, pc}|"
             "1C92:ldrh r3, [r1]|1C94:ldrh r0, [r2]|1C96:adds r3, r3, r0|"
             "1C98:ldrh r4, [r2, #2]|1C9A:adds r3, r3, r4|"
             "1C9C:ldrh r5, [r2, #4]|1C9E:adds r3, r3, r5|"
             "1CA0:lsrs r3, r3, #2|1CA2:strh r4, [r2, #4]|"
             "1CA4:strh r0, [r2, #2]|1CA6:b #0x1c8a"),
    0x1E88: ("three_word_mask", "open_cfw_touch_record_1e88_mask3",
             "1E88:push {r4, r5, r6, lr}|1E8A:ldr r5, [r2]|1E8C:movs r3, r5|"
             "1E8E:bics r3, r0|1E90:str r3, [r2]|1E92:ldr r4, [r2, #4]|"
             "1E94:movs r3, r4|1E96:bics r3, r0|1E98:str r3, [r2, #4]|"
             "1E9A:ldr r3, [r2, #8]|1E9C:movs r6, r3|1E9E:bics r6, r0|"
             "1EA0:str r6, [r2, #8]|1EA2:lsls r6, r1, #0x1d|1EA4:bpl #0x1eaa|"
             "1EA6:orrs r5, r0|1EA8:str r5, [r2]|1EAA:lsls r5, r1, #0x1e|"
             "1EAC:bpl #0x1eb2|1EAE:orrs r4, r0|1EB0:str r4, [r2, #4]|"
             "1EB2:lsls r1, r1, #0x1f|1EB4:bpl #0x1eba|1EB6:orrs r3, r0|"
             "1EB8:str r3, [r2, #8]|1EBA:pop {r4, r5, r6, pc}"),
    0x2620: ("threshold_delta", "open_cfw_touch_record_2620_threshold_delta",
             "2620:push {r4, lr}|2622:movs r3, #0|2624:strh r3, [r1, #4]|"
             "2626:ldrh r2, [r1]|2628:ldrh r4, [r1, #2]|"
             "262A:ldrh r3, [r0, #0x1a]|262C:adds r3, r4, r3|"
             "262E:cmp r2, r3|2630:bls #0x2636|2632:subs r2, r2, r4|"
             "2634:strh r2, [r1, #4]|2636:pop {r4, pc}"),
}

EXPECTED = {
    "input_concrete_gap": 93,
    "input_gap_instruction_bytes": 8524,
    "admitted_functions": 7,
    "admitted_instruction_bytes": 200,
    "argument_relative_record_admissions": 7,
    "literal_or_mmio_admissions": 0,
    "product_semantic_names_asserted": 0,
    "unimplemented_application_contracts_before": 81,
    "unimplemented_application_contracts_after": 74,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 86,
    "residual_gap_instruction_bytes": 8324,
    "row_digest": "d2a8c165513ee40a8df882dd64b00f53405f3394089e1d7ae93306682fee195f",
    "residual_digest": "311cf2bea1866b7fb4451099958bee9007f231c58ecee847818019dce49a10de",
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


def _canonical_body(prefix, payload: bytes, entry: int, entries: set[int]) -> str:
    body = prefix._walk(payload, entry, entries)
    return "|".join(
        f"{address:04X}:{insn.mnemonic} {insn.op_str}"
        for address, insn in sorted(body["instructions"].items())
    )


def _target_compile() -> int:
    clang = shutil.which("clang")
    require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory() as raw:
        output = Path(raw) / "touch-record-primitives.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0,
                f"record primitive target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected: bool = True) -> dict:
    semantic_mod = _load(SEMANTIC_ANALYZER, "touch_record_admission_semantics")
    leaf_mod = _load(LEAF_ANALYZER, "touch_record_admission_leaf")
    prefix = _load(PREFIX_ANALYZER, "touch_record_admission_prefix")
    semantic = semantic_mod.analyze()
    leaf = leaf_mod.analyze()
    residual_by_entry = {row["entry"]: row for row in leaf["residual_rows"]}
    require(set(ADMISSIONS) <= residual_by_entry.keys(),
            "record family escaped batch-8 residual")
    require(all(residual_by_entry[entry]["family"] in
                ("platform_startup_configuration", "touch_application_processing")
                for entry in ADMISSIONS), "record admission crossed provider boundary")
    semantic_by_entry = {row["entry"]: row for row in semantic["semantic_rows"]}
    all_entries = set(semantic_by_entry)
    blob = prefix.BLOB.read_bytes()
    payload = blob[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]

    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "record primitive MIT declarations changed")
    target_object_bytes = _target_compile()
    rows = []
    for entry, (kind, symbol, expected_body) in sorted(ADMISSIONS.items()):
        source_row = semantic_by_entry[entry]
        require(not source_row["callees"], f"record transform gained a call at {entry:#x}")
        canonical = _canonical_body(prefix, payload, entry, all_entries)
        require(canonical == expected_body,
                f"record target body changed at {entry:#x}: {canonical}")
        require(combined.count(symbol) >= 1, f"record source symbol missing: {symbol}")
        require("[pc," not in canonical, f"literal-backed record row admitted at {entry:#x}")
        rows.append({
            "entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_argument_relative_record_source",
            "license": "MIT", "source": SOURCE.name,
            "product_semantics_asserted": False,
            "argument_relative_memory_only": True,
            "instruction_bytes": source_row["instruction_bytes"],
            "instruction_sha256": source_row["instruction_sha256"],
            "canonical_body_sha256": sha256(canonical.encode()),
            "evidence": "complete call-free target control/data flow; memory is argument-relative; no literal, global, MMIO or vendor source admitted",
        })

    residual_rows = [row for entry, row in sorted(residual_by_entry.items())
                     if entry not in ADMISSIONS]
    metrics = {
        "input_concrete_gap": len(residual_by_entry),
        "input_gap_instruction_bytes": sum(row["instruction_bytes"]
                                             for row in residual_by_entry.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(row["instruction_bytes"] for row in rows),
        "argument_relative_record_admissions": len(rows),
        "literal_or_mmio_admissions": 0,
        "product_semantic_names_asserted": sum(
            row["product_semantics_asserted"] for row in rows),
        "unimplemented_application_contracts_before": sum(
            row["family"] in ("platform_startup_configuration",
                              "touch_application_processing")
            for row in residual_by_entry.values()),
        "unimplemented_application_contracts_after": sum(
            row["family"] in ("platform_startup_configuration",
                              "touch_application_processing") for row in residual_rows),
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
                    f"record admission {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch argument-relative record source admission batch 9",
        "analysis_mode": "offline authenticated target control/data flow and Cortex-M0+ compile; argument-relative host buffers only, no MMIO or hardware execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
                   "sha256": sha256(SOURCE.read_bytes()),
                   "target_object_bytes": target_object_bytes},
        "integration": "isolated source candidates only; not production-routed",
        "remaining": {
            "concrete_source_or_implementation_functions": len(residual_rows),
            "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
            "unimplemented_clean_room_application_contracts":
                metrics["unimplemented_application_contracts_after"],
            "typed_external_or_unavailable_functions": 12,
            "note": "argument-relative functional transforms do not assert volatile/atomic memory semantics; residual providers/contracts remain non-source",
        },
        "exclusions": "nested pointer graphs, literal tables, global state, MMIO, breakpoints, product semantic roles, EULA bodies, system handoff and halt remain unadmitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-record-primitives-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license", "source",
                         "product_semantics_asserted", "argument_relative_memory_only",
                         "instruction_bytes", "instruction_sha256",
                         "canonical_body_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["symbol"], row["kind"], row["status"],
                row["license"], row["source"],
                str(row["product_semantics_asserted"]).lower(),
                str(row["argument_relative_memory_only"]).lower(),
                row["instruction_bytes"], row["instruction_sha256"],
                row["canonical_body_sha256"], row["evidence"],
            ])
    residual = MANIFEST_DIR / "g2-touch-record-primitives-residual.tsv"
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
    summary = MANIFEST_DIR / "g2-touch-record-primitives-admission-summary.json"
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
        print(f"argument-relative record sources: {result['metrics']['admitted_functions']}")
        print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch record primitive admission failed: {exc}") from exc
