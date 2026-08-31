#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit the MIT clean-room Touch Em_EEPROM replacement (batch 25)."""

from __future__ import annotations

import argparse, csv, hashlib, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
PRIOR = TOOLS / "analyze_g2_touch_product_orchestration_admission.py"
PREFIX = TOOLS / "analyze_g2_touch_prefix_function_map.py"
SOURCE = TOUCH / "runtime_touch_emeeprom_clean_room.c"
HEADER = TOUCH / "runtime_touch_emeeprom_clean_room.h"

# kind, symbol, canonical digest, instruction bytes, direct callees, indirect calls
ADMISSIONS = {
    0x4B44: ("simple_read", "open_cfw_touch_eeprom_4b44_read_simple", "23c9c9ce6481ea502261b1811e814916eacff598e69f79268f55f1f74360f9fd", 30, set(), 1),
    0x4C08: ("backend_write_range", "open_cfw_touch_eeprom_4c08_write_range", "c291c9ee8fca7d53fc615038634a349cc5b32fc50590d5a35096c679976064c9", 96, set(), 3),
    0x4F00: ("physical_geometry_size", "open_cfw_touch_eeprom_4f00_physical_bytes", "78d59c5af1a5d63bacb1c2cd04627dd671b35278f3674bf3445c9b649954aa41", 30, set(), 0),
    0x4F20: ("configuration_validation", "open_cfw_touch_eeprom_4f20_validate", "edb96e93211d0cd4c3770cb09dc35409a9e3dad468a610ef305dd9d7cc1281a1", 104, {0x4F00}, 1),
    0x4F8C: ("row_geometry", "open_cfw_touch_eeprom_4f8c_geometry", "4fccb9f719a03cb6ed7fe67199ccbca20c4c3b160c4ac8caefc6ea54cc8ce3a3", 84, {0x73C0}, 1),
    0x4FE0: ("extended_read", "open_cfw_touch_eeprom_4fe0_read_extended", "041a3d505b775d4a2ff66845f6428db91d2e8c70b8d23beb03fd3977119c81a1", 620, {0x4C78, 0x4C7C, 0x4CA0, 0x4D58, 0x4E0C, 0x4E2A, 0x73C0, 0x74CC, 0x76D4}, 2),
    0x560C: ("row_write", "open_cfw_touch_eeprom_560c_write_row", "c2340489f17c679340a4f4834986d9a84b994733addd59c527d1bbf193c8747b", 124, {0x4C08, 0x74CC, 0x772C}, 1),
    0x568C: ("context_initialize", "open_cfw_touch_eeprom_568c_initialize", "2bf1e762b9ee0c8df6e77823e00e58b105ce2fb76c4b14c0acfbc7325618f78e", 168, {0x4CA4, 0x4F20, 0x4F8C, 0x73C0, 0x76D4}, 1),
    0x5738: ("initialize_adapter", "open_cfw_touch_eeprom_5738_initialize_adapter", "756e967a0366b30eaa30c193b7413b53461784c59b17d5dd957cb9383baf94b4", 60, {0x156C, 0x568C}, 0),
    0x5778: ("read_adapter", "open_cfw_touch_eeprom_5778_read_adapter", "5838a1ddc9b980a27f9910572e3a4970da4e5c1875497e576832e5ed2de80942", 48, {0x4B44, 0x4FE0}, 0),
    0x57E0: ("erase_adapter", "open_cfw_touch_eeprom_57e0_erase_adapter", "8a379bfc4b6cd457219895f3b4ef6d0abc354b17ebbb04df60b5006e88cfc786", 272, {0x4C6C, 0x4D58, 0x4E0C, 0x5254, 0x560C, 0x73C0, 0x76D4}, 0),
}

SOURCE_PINS = {
    SOURCE: (12896, "699f35a2116389fb3603217d0455edcde4f16922589b9114fb2d866312543636"),
    HEADER: (3136, "ff201426be0806da0e256de467515cc0b294759e9974179a36d3632684162373"),
}

EXPECTED = {
    "input_concrete_gap": 19, "input_gap_instruction_bytes": 2578,
    "admitted_functions": 11, "admitted_instruction_bytes": 1636,
    "eula_source_copied": 0, "fixed_address_accesses": 0,
    "unimplemented_application_contracts_after": 0,
    "typed_external_or_unavailable_functions": 8,
    "concrete_source_or_implementation_gap_after": 8,
    "residual_gap_instruction_bytes": 942,
}


class AuditError(RuntimeError): pass
def require(c, m):
    if not c: raise AuditError(m)
def sha256(data): return hashlib.sha256(data).hexdigest()
def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); require(spec and spec.loader, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module); return module


def _target_compile():
    clang = shutil.which("clang"); require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-touch-eeprom-audit-") as raw:
        output = Path(raw) / "touch-eeprom.o"
        proc = subprocess.run([clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb", "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output)], capture_output=True, text=True)
        require(proc.returncode == 0, f"Em_EEPROM target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected=True):
    prior_mod = _load(PRIOR, "touch_eeprom_batch24"); prefix = _load(PREFIX, "touch_eeprom_prefix")
    prior = prior_mod.analyze(); residual = {r["entry"]: r for r in prior["residual_rows"]}
    require(set(ADMISSIONS) <= residual.keys(), "Em_EEPROM replacement escaped batch-24 residual")
    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(residual)
    for _kind, _symbol, _digest, _bytes, calls, _indirect in ADMISSIONS.values(): entries.update(calls)
    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2, "MIT declarations changed")
    require("LicenseRef-Infineon-EULA" not in combined, "EULA implementation marker entered clean-room source")
    for path, (size, digest) in SOURCE_PINS.items():
        data = path.read_bytes(); require(len(data) == size and sha256(data) == digest, f"source identity changed: {path.relative_to(ROOT)}")
    target_bytes = _target_compile(); rows = []
    for entry, (kind, symbol, digest, byte_count, expected_calls, expected_indirect) in sorted(ADMISSIONS.items()):
        body = prefix._walk(payload, entry, entries)
        canonical = "|".join(f"{address:04X}:{insn.mnemonic} {insn.op_str}" for address, insn in sorted(body["instructions"].items()))
        calls = {call["target"] for call in body["calls"] if call["target"] is not None}
        indirect = sum(call["target"] is None for call in body["calls"])
        require(sha256(canonical.encode()) == digest, f"body changed at {entry:#x}")
        require(calls == expected_calls and indirect == expected_indirect, f"calls changed at {entry:#x}")
        require(residual[entry]["instruction_bytes"] == byte_count, f"span changed at {entry:#x}")
        require(symbol in combined, f"source symbol missing: {symbol}")
        rows.append({"entry": entry, "symbol": symbol, "kind": kind,
            "status": "mit_clean_room_functional_replacement", "license": "MIT",
            "source": SOURCE.name, "direct_callees": sorted(calls), "indirect_calls": indirect,
            "backend_injected": True, "eula_source_copied": False,
            "fixed_address_access": False, "mmio_execution": False,
            "instruction_bytes": byte_count, "instruction_sha256": residual[entry]["instruction_sha256"],
            "canonical_body_sha256": digest,
            "evidence": "authenticated Em_EEPROM boundary replaced independently by bounds-checked simple/extended storage, CRC-8, row sequencing, fallback, write, and erase over an injected backend; no vendor source or fixed-address flash access"})
    residual_rows = [r for e, r in sorted(residual.items()) if e not in ADMISSIONS]
    metrics = {"input_concrete_gap": len(residual),
        "input_gap_instruction_bytes": sum(r["instruction_bytes"] for r in residual.values()),
        "admitted_functions": len(rows), "admitted_instruction_bytes": sum(r["instruction_bytes"] for r in rows),
        "eula_source_copied": 0, "fixed_address_accesses": 0,
        "unimplemented_application_contracts_after": 0,
        "typed_external_or_unavailable_functions": len(residual_rows),
        "concrete_source_or_implementation_gap_after": len(residual_rows),
        "residual_gap_instruction_bytes": sum(r["instruction_bytes"] for r in residual_rows),
        "row_digest": sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()),
        "residual_digest": sha256(json.dumps(residual_rows, sort_keys=True, separators=(",", ":")).encode())}
    if enforce_expected:
        for key, value in EXPECTED.items(): require(metrics[key] == value, f"Em_EEPROM {key} changed: {metrics[key]!r} != {value!r}")
    return {"schema_version": 1, "component": "G2 Touch MIT clean-room Em_EEPROM admission batch 25",
        "analysis_mode": "offline authenticated boundary plus independent functional replacement; host and Cortex-M0+ compile; no hardware/MMIO execution",
        "metrics": metrics, "rows": rows, "residual_rows": residual_rows,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "license": "MIT", "sha256": sha256(SOURCE.read_bytes()), "target_closure_object_bytes": target_bytes},
        "integration": "isolated source candidate only; not production-routed",
        "compatibility": "clean-room on-storage format; migration from Infineon extended-mode rows requires hardware/capture evidence",
        "remaining": {"concrete_source_or_implementation_functions": len(residual_rows), "concrete_gap_instruction_bytes": metrics["residual_gap_instruction_bytes"], "unimplemented_clean_room_application_contracts": 0, "typed_external_or_unavailable_functions": len(residual_rows)},
        "hardware_validation": "blocked by unavailable physical evidence", "hardware_blocker": "blocked by unavailable physical evidence",
        "exclusions": "selected runtime, resident configuration, system handoff/fault, and halt boundaries remain"}


def write_manifests(result):
    admitted = MANIFEST_DIR / "g2-touch-emeeprom-clean-room-admission.tsv"
    with admitted.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["entry", "symbol", "kind", "status", "license", "source", "direct_callees", "indirect_calls", "backend_injected", "eula_source_copied", "fixed_address_access", "mmio_execution", "instruction_bytes", "instruction_sha256", "canonical_body_sha256", "evidence"])
        for r in result["rows"]: w.writerow([f"0x{r['entry']:04X}", r["symbol"], r["kind"], r["status"], r["license"], r["source"], ",".join(f"0x{x:04X}" for x in r["direct_callees"]), r["indirect_calls"], "true", "false", "false", "false", r["instruction_bytes"], r["instruction_sha256"], r["canonical_body_sha256"], r["evidence"]])
    residual = MANIFEST_DIR / "g2-touch-emeeprom-clean-room-residual.tsv"
    with residual.open("w", newline="") as h:
        w = csv.writer(h, delimiter="\t", lineterminator="\n"); w.writerow(["# SPDX-License-Identifier: MIT"])
        w.writerow(["entry", "family", "status", "license", "concrete_source", "implemented", "instruction_bytes", "instruction_sha256", "reason"])
        for r in result["residual_rows"]: w.writerow([f"0x{r['entry']:04X}", r["family"], r["status"], r["license"], str(r["concrete_source"]).lower(), str(r["implemented"]).lower(), r["instruction_bytes"], r["instruction_sha256"], r["reason"]])
    summary = MANIFEST_DIR / "g2-touch-emeeprom-clean-room-admission-summary.json"
    slim = {k: v for k, v in result.items() if k not in ("rows", "residual_rows")}; slim["admitted_row_count"] = len(result["rows"]); slim["residual_row_count"] = len(result["residual_rows"]); summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    # This batch owns only its admission artifacts.  The exhaustive final
    # classifier is the sole writer of the cross-batch current summary.
    return [admitted, residual, summary]


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--write-manifests", action="store_true"); args = p.parse_args(); result = analyze()
    if args.write_manifests:
        for path in write_manifests(result): print(f"wrote {path.relative_to(ROOT)}")
    print(f"clean-room Em_EEPROM sources: {result['metrics']['admitted_functions']}"); print(f"remaining concrete source/implementation gap: {len(result['residual_rows'])}"); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AuditError as exc: raise SystemExit(f"Touch Em_EEPROM admission failed: {exc}") from exc
