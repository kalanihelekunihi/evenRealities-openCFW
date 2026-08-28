#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit call-free touch leaf primitives with complete register-level behavior."""

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
APPLICATION_ANALYZER = TOOLS / "analyze_g2_touch_application_boundary.py"
CAT2_FINAL_ANALYZER = TOOLS / "analyze_g2_touch_cat2_source_admission5.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_leaf_primitives.c"
HEADER = TOUCH / "runtime_touch_leaf_primitives.h"

ADMISSIONS = {
    0x1226: ("register_passthrough", "open_cfw_touch_leaf_1226_passthrough",
             "1226:bx lr"),
    0x1236: ("register_passthrough", "open_cfw_touch_leaf_1236_passthrough",
             "1236:bx lr"),
    0x12A4: ("register_passthrough", "open_cfw_touch_leaf_12a4_passthrough",
             "12A4:bx lr"),
    0x1366: ("register_passthrough", "open_cfw_touch_leaf_1366_passthrough",
             "1366:bx lr"),
    0x1370: ("register_passthrough", "open_cfw_touch_leaf_1370_passthrough",
             "1370:bx lr"),
    0x1418: ("register_passthrough", "open_cfw_touch_leaf_1418_passthrough",
             "1418:bx lr"),
    0x1480: ("constant_return", "open_cfw_touch_leaf_1480_constant_1",
             "1480:movs r0, #1|1482:bx lr"),
    0x1484: ("constant_return", "open_cfw_touch_leaf_1484_constant_128",
             "1484:movs r0, #0x80|1486:bx lr"),
    0x1488: ("constant_return", "open_cfw_touch_leaf_1488_constant_128",
             "1488:movs r0, #0x80|148A:bx lr"),
    0x148C: ("constant_return", "open_cfw_touch_leaf_148c_constant_0",
             "148C:movs r0, #0|148E:bx lr"),
    0x14AA: ("constant_return", "open_cfw_touch_leaf_14aa_constant_0",
             "14AA:movs r0, #0|14AC:bx lr"),
    0x1AB4: ("constant_return", "open_cfw_touch_leaf_1ab4_constant_0",
             "1AB4:movs r0, #0|1AB6:bx lr"),
    0x1490: ("pure_arithmetic", "open_cfw_touch_leaf_1490_bounded_sum",
             "1490:cmp r1, #0|1492:beq #0x14a2|1494:adds r1, r1, r2|"
             "1496:movs r3, #0x80|1498:lsls r3, r3, #9|149A:cmp r1, r3|"
             "149C:bls #0x14a6|149E:movs r0, #0|14A0:b #0x14a4|"
             "14A2:movs r0, #0|14A4:bx lr|14A6:movs r0, #1|14A8:b #0x14a4"),
    0x1CA8: ("pure_arithmetic", "open_cfw_touch_leaf_1ca8_median3",
             "1CA8:cmp r0, r1|1CAA:bhi #0x1cb2|1CAC:movs r3, r1|"
             "1CAE:movs r1, r0|1CB0:movs r0, r3|1CB2:cmp r0, r2|"
             "1CB4:bhi #0x1cb8|1CB6:movs r2, r0|1CB8:movs r0, r1|"
             "1CBA:cmp r1, r2|1CBC:bhs #0x1cc0|1CBE:movs r0, r2|1CC0:bx lr"),
    0x1CDE: ("pure_arithmetic", "open_cfw_touch_leaf_1cde_blend_u8",
             "1CDE:muls r0, r2, r0|1CE0:movs r3, #0x80|1CE2:lsls r3, r3, #1|"
             "1CE4:subs r3, r3, r2|1CE6:muls r1, r3, r1|1CE8:adds r0, r0, r1|"
             "1CEA:lsrs r0, r0, #8|1CEC:bx lr"),
    0x2228: ("pure_arithmetic", "open_cfw_touch_leaf_2228_mode_scale",
             "2228:push {r4, lr}|222A:movs r4, r0|222C:movs r0, r2|"
             "222E:movs r3, #3|2230:ands r3, r1|2232:cmp r3, #2|"
             "2234:beq #0x2238|2236:pop {r4, pc}|2238:cmp r4, #1|"
             "223A:beq #0x2244|223C:cmp r4, #0xa|223E:beq #0x2244|"
             "2240:lsrs r0, r2, #1|2242:b #0x2236|2244:lsrs r0, r0, #2|"
             "2246:b #0x2236"),
}

EXPECTED = {
    "input_concrete_gap": 109,
    "admitted_functions": 16,
    "register_passthrough_functions": 6,
    "constant_return_functions": 6,
    "pure_arithmetic_functions": 4,
    "upstream_body_admissions": 0,
    "clean_room_instruction_exact_sources": 16,
    "pointer_or_mmio_admissions": 0,
    "unimplemented_application_contracts_before": 97,
    "unimplemented_application_contracts_after": 81,
    "typed_external_eula_functions": 10,
    "typed_system_handoff_functions": 1,
    "typed_unavailable_halt_functions": 1,
    "concrete_source_or_implementation_gap_after": 93,
    "admitted_instruction_bytes": 136,
    "row_digest": "1802179e7a5b1a4e49b3cabc3d3d1bcc5a9e5f8de57605cb4b02d9961948c130",
    "residual_digest": "63ac44df4dae71667fce6ae64c6737c3dd7650ec3072000f5b296b21d2211241",
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
        output = Path(raw) / "touch-leaf-primitives.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0, f"leaf primitive target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected: bool = True) -> dict:
    semantic_mod = _load(SEMANTIC_ANALYZER, "touch_leaf_admission_semantics")
    application_mod = _load(APPLICATION_ANALYZER, "touch_leaf_admission_application")
    cat2_mod = _load(CAT2_FINAL_ANALYZER, "touch_leaf_admission_cat2")
    prefix = _load(PREFIX_ANALYZER, "touch_leaf_admission_prefix")
    semantic = semantic_mod.analyze()
    application = application_mod.analyze()
    cat2 = cat2_mod.analyze()

    prior_contracts = {row["entry"]: row for row in application["contract_rows"]}
    require(set(ADMISSIONS) <= prior_contracts.keys(),
            "leaf family is no longer wholly inside unimplemented contracts")
    require(application["remaining"]["concrete_source_or_implementation_functions"] == 109,
            "batch-7 concrete gap changed")
    semantic_by_entry = {row["entry"]: row for row in semantic["semantic_rows"]}
    all_entries = set(semantic_by_entry)
    blob = prefix.BLOB.read_bytes()
    payload = blob[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]

    source_text = SOURCE.read_text() + HEADER.read_text()
    require(source_text.count("SPDX-License-Identifier: MIT") == 2,
            "leaf primitive MIT license declarations changed")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (kind, symbol, expected_body) in sorted(ADMISSIONS.items()):
        source_row = semantic_by_entry[entry]
        require(not source_row["callees"], f"leaf candidate gained a call at {entry:#x}")
        canonical = _canonical_body(prefix, payload, entry, all_entries)
        require(canonical == expected_body,
                f"leaf target body changed at {entry:#x}: {canonical}")
        require(source_text.count(symbol) >= 1, f"leaf source symbol missing: {symbol}")
        rows.append({
            "entry": entry,
            "symbol": symbol,
            "kind": kind,
            "status": "clean_room_instruction_exact_source",
            "license": "MIT",
            "source": SOURCE.name,
            "product_semantics_asserted": False,
            "raw_aapcs_register_behavior_complete": True,
            "instruction_bytes": source_row["instruction_bytes"],
            "instruction_sha256": source_row["instruction_sha256"],
            "canonical_body_sha256": sha256(canonical.encode()),
            "evidence": "complete call-free Thumb body; independent C expression preserves uint32 register behavior; no pointer or MMIO access",
        })

    residual_rows = []
    for entry, row in sorted(prior_contracts.items()):
        if entry in ADMISSIONS:
            continue
        residual_rows.append({
            "entry": entry, "family": row["family"], "status": row["status"],
            "license": row["license"], "concrete_source": False,
            "implemented": False, "instruction_bytes": row["instruction_bytes"],
            "instruction_sha256": row["instruction_sha256"],
            "reason": "application behavior or typed pointer/callback ABI remains unestablished",
        })
    for source_row in sorted(semantic["semantic_rows"], key=lambda row: row["entry"]):
        if source_row["batch"] not in ("emeeprom_eula", "system_handoff_mixed"):
            continue
        is_eeprom = source_row["batch"] == "emeeprom_eula"
        residual_rows.append({
            "entry": source_row["entry"],
            "family": source_row["batch"],
            "status": ("typed_external_eula_provider_boundary" if is_eeprom
                       else "typed_external_system_handoff_boundary"),
            "license": ("LicenseRef-Infineon-EULA" if is_eeprom
                        else "LicenseRef-Unresolved"),
            "concrete_source": False, "implemented": False,
            "instruction_bytes": source_row["instruction_bytes"],
            "instruction_sha256": source_row["instruction_sha256"],
            "reason": ("vendor provider body remains EULA-isolated" if is_eeprom
                       else "system handoff ABI remains unavailable"),
        })
    halt = cat2["typed_unavailable"][0]
    residual_rows.append({
        "entry": halt["entry"], "family": "legacy_halt",
        "status": halt["status"], "license": halt["license"],
        "concrete_source": False, "implemented": False,
        "instruction_bytes": semantic_by_entry[halt["entry"]]["instruction_bytes"],
        "instruction_sha256": halt["instruction_sha256"],
        "reason": "authentic upstream provider body unavailable; injected halt provider required",
    })
    residual_rows.sort(key=lambda row: row["entry"])

    metrics = {
        "input_concrete_gap": application["remaining"]["concrete_source_or_implementation_functions"],
        "admitted_functions": len(rows),
        "register_passthrough_functions": sum(row["kind"] == "register_passthrough" for row in rows),
        "constant_return_functions": sum(row["kind"] == "constant_return" for row in rows),
        "pure_arithmetic_functions": sum(row["kind"] == "pure_arithmetic" for row in rows),
        "upstream_body_admissions": 0,
        "clean_room_instruction_exact_sources": len(rows),
        "pointer_or_mmio_admissions": 0,
        "unimplemented_application_contracts_before": len(prior_contracts),
        "unimplemented_application_contracts_after": sum(
            row["family"] in ("platform_startup_configuration",
                              "touch_application_processing") for row in residual_rows),
        "typed_external_eula_functions": sum(
            row["family"] == "emeeprom_eula" for row in residual_rows),
        "typed_system_handoff_functions": sum(
            row["family"] == "system_handoff_mixed" for row in residual_rows),
        "typed_unavailable_halt_functions": sum(
            row["family"] == "legacy_halt" for row in residual_rows),
        "concrete_source_or_implementation_gap_after": len(residual_rows),
        "admitted_instruction_bytes": sum(row["instruction_bytes"] for row in rows),
        "row_digest": sha256(json.dumps(rows, sort_keys=True,
                                          separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(residual_rows, sort_keys=True,
                                               separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"leaf admission {key} changed: {metrics[key]!r} != {expected!r}")

    return {
        "schema_version": 1,
        "component": "G2 touch call-free leaf primitive source admission batch 8",
        "analysis_mode": "offline complete Thumb-body/register semantics and isolated Cortex-M0+ compile; no pointer, MMIO, hardware or production execution",
        "metrics": metrics,
        "rows": rows,
        "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
                   "sha256": sha256(SOURCE.read_bytes()),
                   "target_object_bytes": target_object_bytes},
        "integration": "isolated source candidates only; not production-routed",
        "remaining": {
            "concrete_source_or_implementation_functions": len(residual_rows),
            "unimplemented_clean_room_application_contracts":
                metrics["unimplemented_application_contracts_after"],
            "typed_external_or_unavailable_functions": 12,
            "note": "external/unavailable provider rows and unimplemented contracts remain non-source",
        },
        "exclusions": "no product semantic names, pointer layouts, callback ABIs, EULA bodies, MMIO or system-handoff behavior admitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-leaf-primitives-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license", "source",
                         "product_semantics_asserted", "raw_aapcs_register_behavior_complete",
                         "instruction_bytes", "instruction_sha256",
                         "canonical_body_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["symbol"], row["kind"], row["status"],
                row["license"], row["source"],
                str(row["product_semantics_asserted"]).lower(),
                str(row["raw_aapcs_register_behavior_complete"]).lower(),
                row["instruction_bytes"], row["instruction_sha256"],
                row["canonical_body_sha256"], row["evidence"],
            ])
    residual = MANIFEST_DIR / "g2-touch-leaf-primitives-residual.tsv"
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
    summary = MANIFEST_DIR / "g2-touch-leaf-primitives-admission-summary.json"
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
        print(f"instruction-exact clean-room sources: {result['metrics']['admitted_functions']}")
        print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch leaf primitive admission failed: {exc}") from exc
