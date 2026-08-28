#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit four application-owned storage adapters (touch batch 15)."""

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
PRIOR_ANALYZER = TOOLS / "analyze_g2_touch_configuration_start_pipeline_admission.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_storage_adapters.c"
HEADER = TOUCH / "runtime_touch_storage_adapters.h"

# kind, source symbol, canonical SHA-256, bytes, exact direct targets
ADMISSIONS = {
    0x01D8: ("storage_initialize_adapter", "open_cfw_touch_storage_01d8_initialize",
             "493ad0c9ddd2b2e7ca9846460e4c5fe8138d3629a8a49ede74470806b76a4792",
             50, {0x5738}),
    0x0220: ("bounded_storage_read_adapter", "open_cfw_touch_storage_0220_read",
             "3d7d38add665af67f9bf4bf753be4b0a2f95b0ea4b2d0eecf262670c4d75c2b3",
             60, {0x5778}),
    0x02B0: ("storage_context_operation_adapter",
             "open_cfw_touch_storage_02b0_context_operation",
             "c2dd913ca414462e4ab46f2a9588f9dfe62b45fe880cb86ed60492bb00288f4b",
             38, {0x57E0}),
    0x02E4: ("storage_counter_increment", "open_cfw_touch_storage_02e4_increment",
             "ab999907f93781aaf1f0891b7f9445699d57df620bdd706af76e9c3d36323480",
             10, set()),
}

EXPECTED = {
    "input_concrete_gap": 60, "input_gap_instruction_bytes": 5278,
    "admitted_functions": 4, "admitted_instruction_bytes": 158,
    "typed_eula_provider_admissions": 3, "resident_table_admissions": 0,
    "mmio_admissions": 0, "product_semantic_names_asserted": 0,
    "unimplemented_application_contracts_before": 48,
    "unimplemented_application_contracts_after": 44,
    "typed_external_or_unavailable_functions": 12,
    "concrete_source_or_implementation_gap_after": 56,
    "residual_gap_instruction_bytes": 5120,
    "row_digest": "a666155803290d0602c84bcf42b07f58a74cb7e45140c59a1b787e961e68e406",
    "residual_digest": "07740f41e331853c1e4d9046940dff38ac38c47906e03c657b55c6e0ebe03e4f",
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
    canonical = "|".join(f"{address:04X}:{insn.mnemonic} {insn.op_str}"
                         for address, insn in sorted(body["instructions"].items()))
    return canonical, {call["target"] for call in body["calls"]
                       if call["target"] is not None}


def _target_compile() -> int:
    clang = shutil.which("clang")
    require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory() as raw:
        output = Path(raw) / "touch-storage.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0, f"storage target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected: bool = True) -> dict:
    prior_mod = _load(PRIOR_ANALYZER, "touch_storage_batch14")
    prefix = _load(PREFIX_ANALYZER, "touch_storage_prefix")
    prior = prior_mod.analyze()
    residual_by_entry = {row["entry"]: row for row in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual_by_entry.keys(),
            "storage adapters escaped batch-14 residual")
    require(all(residual_by_entry[entry]["family"] == "platform_startup_configuration"
                for entry in ADMISSIONS), "storage adapters crossed provider boundary")

    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(ADMISSIONS)
    for _kind, _symbol, _digest, _size, callees in ADMISSIONS.values():
        entries.update(callees)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "storage adapter MIT declarations changed")
    require(struct.unpack_from("<I", payload, 0x021C)[0] == 0x093E0004,
            "storage accepted-status literal changed")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (kind, symbol, body_digest, expected_bytes, expected_callees) in sorted(ADMISSIONS.items()):
        prior_row = residual_by_entry[entry]
        canonical, callees = _canonical(prefix, payload, entry, entries)
        require(sha256(canonical.encode()) == body_digest,
                f"storage canonical body changed at {entry:#x}")
        require(prior_row["instruction_bytes"] == expected_bytes,
                f"storage byte span changed at {entry:#x}")
        require(callees == expected_callees,
                f"storage calls changed at {entry:#x}: {sorted(callees)}")
        require(symbol in combined, f"storage source symbol missing: {symbol}")
        rows.append({
            "entry": entry, "symbol": symbol, "kind": kind,
            "status": "clean_room_storage_adapter_with_typed_eula_provider",
            "license": "MIT", "source": SOURCE.name,
            "direct_callees": sorted(callees),
            "typed_providers": sorted(callees & {0x5738, 0x5778, 0x57E0}),
            "provider_license": "LicenseRef-Infineon-EULA" if callees else "",
            "resident_table_dependency": False,
            "product_semantics_asserted": False,
            "instruction_bytes": prior_row["instruction_bytes"],
            "instruction_sha256": prior_row["instruction_sha256"],
            "canonical_body_sha256": body_digest,
            "evidence": "complete application-owned bounds/status/state flow; Em_EEPROM body remains an injected typed EULA provider; no MMIO or resident table admitted",
        })

    residual_rows = [row for entry, row in sorted(residual_by_entry.items())
                     if entry not in ADMISSIONS]
    metrics = {
        "input_concrete_gap": len(residual_by_entry),
        "input_gap_instruction_bytes": sum(row["instruction_bytes"] for row in residual_by_entry.values()),
        "admitted_functions": len(rows),
        "admitted_instruction_bytes": sum(row["instruction_bytes"] for row in rows),
        "typed_eula_provider_admissions": sum(bool(row["typed_providers"]) for row in rows),
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
                    f"storage adapter {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1, "component": "G2 touch storage adapter source admission batch 15",
        "analysis_mode": "offline authenticated control/data flow, injected EULA provider callbacks, host tests and Cortex-M0+ compile; no MMIO or hardware execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT",
                   "sha256": sha256(SOURCE.read_bytes()),
                   "target_closure_object_bytes": target_object_bytes},
        "integration": "isolated source candidates only; not production-routed",
        "remaining": {
            "concrete_source_or_implementation_functions": len(residual_rows),
            "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"],
            "unimplemented_clean_room_application_contracts": metrics["unimplemented_application_contracts_after"],
            "typed_external_or_unavailable_functions": 12,
            "note": "ten Em_EEPROM EULA provider bodies, system handoff and halt remain external; resident 0xB41C/0xB4C4 loaders and 0x1B6C/0x1C54/0x2638 remain unimplemented",
        },
        "exclusions": "all Em_EEPROM provider bodies, resident tables, ambiguous application ABIs, MMIO, system handoff and halt remain unadmitted",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-storage-adapters-admission.tsv"
    with admitted.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "kind", "status", "license", "source",
                         "direct_callees", "typed_providers", "provider_license",
                         "resident_table_dependency", "instruction_bytes",
                         "instruction_sha256", "canonical_body_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["symbol"], row["kind"],
                             row["status"], row["license"], row["source"],
                             ",".join(f"0x{x:04X}" for x in row["direct_callees"]),
                             ",".join(f"0x{x:04X}" for x in row["typed_providers"]),
                             row["provider_license"],
                             str(row["resident_table_dependency"]).lower(),
                             row["instruction_bytes"], row["instruction_sha256"],
                             row["canonical_body_sha256"], row["evidence"]])
    residual = MANIFEST_DIR / "g2-touch-storage-adapters-residual.tsv"
    with residual.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "family", "status", "license", "concrete_source",
                         "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for row in result["residual_rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["family"], row["status"], row["license"],
                             str(row["concrete_source"]).lower(), str(row["implemented"]).lower(),
                             row["instruction_bytes"], row["instruction_sha256"], row["reason"]])
    summary = MANIFEST_DIR / "g2-touch-storage-adapters-admission-summary.json"
    slim = {key: value for key, value in result.items() if key not in ("rows", "residual_rows")}
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
    print(f"storage adapter sources: {result['metrics']['admitted_functions']}")
    print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch storage adapter admission failed: {exc}") from exc
