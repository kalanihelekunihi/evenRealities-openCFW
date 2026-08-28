#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Typed evidence and provider boundaries for reachable touch-prefix helpers.

This consumes the authenticated map from analyze_g2_touch_prefix_function_map
and assigns every formerly generic direct-call helper to a reproducible
behavior/provider boundary.  Public symbol matches are candidates unless the
ABI and instruction behavior are independently exact; no historical source
name is inferred merely from physical ordering.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

from capstone.arm import ARM_OP_MEM, ARM_REG_PC

ROOT = Path(__file__).resolve().parents[1]
BASE_ANALYZER = ROOT / "tools/analyze_g2_touch_prefix_function_map.py"
MANIFEST_DIR = ROOT / "tools/manifests"

BASE_ROW_DIGEST = "335e09b1d61057a49e69d4f58f9e9117f4e8db4f475068f76ba3f544919a5e7a"

PROVIDERS = {
    "open_cfw_clean_room": {
        "provider": "OpenCFW clean-room behavior boundary",
        "source": "project-authored replacement required",
        "commit": None,
        "license": "MIT",
        "use": "implement from typed behavior and ABI without copying stock/vendor code",
    },
    "infineon_cat2_pdl": {
        "provider": "Infineon mtb-pdl-cat2",
        "source": "https://github.com/Infineon/mtb-pdl-cat2",
        "commit": "35f1714623cfea682d5e285af80d50416b4c7bbc",
        "license": "Apache-2.0",
        "use": "prefer the upstream provider implementation and retain Apache-2.0 notices",
    },
    "infineon_capsense": {
        "provider": "Infineon CAPSENSE middleware",
        "source": "https://github.com/Infineon/capsense",
        "commit": "b68b744eb75fe976fc5ddd7b16e04e1a5a54bdd3",
        "license": "LicenseRef-Infineon-EULA",
        "use": "interface evidence only for MIT clean-room replacement unless EULA terms are accepted",
    },
    "infineon_emeeprom": {
        "provider": "Infineon Emulated EEPROM middleware",
        "source": "https://github.com/Infineon/emeeprom",
        "commit": "6bbde322b7193528674dbf7fcdc2e971d0cff4fa",
        "license": "LicenseRef-Infineon-EULA",
        "use": "interface/algorithm identification only for MIT clean-room replacement unless EULA terms are accepted",
    },
    "toolchain_runtime": {
        "provider": "ARM EABI / C runtime provider unresolved",
        "source": "compiler-provided runtime ABI",
        "commit": None,
        "license": "LicenseRef-Upstream-Toolchain-Runtime",
        "use": "link an upstream compiler/libc implementation under its own license; do not copy stock bytes",
    },
}

# entry: proposed name, boundary, name status, confidence, evidence
HELPERS = {
    0x0268: ("touch_config_read_adapter", "open_cfw_clean_room", "clean_room_semantic_name", "high",
             "bounds logical address+length to 256, gates initialized state, calls Em_EEPROM read and translates status"),
    0x071C: ("saved_proximity_baseline_read", "open_cfw_clean_room", "clean_room_semantic_name", "high",
             "reads config u16 +4 only after UNVE/config-ready sentinel"),
    0x0738: ("touch_config_load_from_eeprom", "open_cfw_clean_room", "clean_room_semantic_name", "high",
             "installs UNVE defaults, reads eight bytes through touch_config_read_adapter, logs resulting fields"),
    0x07FC: ("attention_release_timeout_rearm", "open_cfw_clean_room", "clean_room_semantic_name", "medium",
             "writes GPIO_PRT4 state offsets +0x44/+0x40 around a 200 ms delay and dead logger call"),
    0x0BE8: ("timeout_default_1000_if_zero", "open_cfw_clean_room", "clean_room_semantic_name", "high",
             "if non-null u16 state is zero, stores 1000; otherwise leaves it unchanged"),
    0x0BFC: ("gesture_policy_helper_0bfc", "open_cfw_clean_room", "typed_boundary_only", "medium",
             "called only by touch_gesture_state_machine; arithmetic/division plus resident dead-log pointers; exact policy name unavailable"),
    0x0D70: ("touch_gesture_state_machine", "open_cfw_clean_room", "clean_room_semantic_name", "high",
             "report-builder callee using sensor state, gesture timing helpers, copy/fill, and resident gesture log pointers"),
    0x111C: ("proximity_baseline_update_adapter", "open_cfw_clean_room", "clean_room_semantic_name", "high",
             "reads sensor context 0x200004EC, saved baseline, CapSense accessor, and update state 0x200009D8"),

    0x1180: ("Cy_SysLib_DelayCycles", "infineon_cat2_pdl", "exact_public_provider_symbol", "high",
             "instruction-for-instruction CM0+ delay loop: add 2, divide by 4, add/sub loop, two alignment NOPs"),
    0x2CA4: ("pdl_timeout_count_scale", "infineon_cat2_pdl", "typed_provider_candidate", "medium",
             "multiply/divide timeout scaling with explicit divisor-zero status; called by MSCLP scan wait"),
    0x3628: ("msclp_scan_register_prepare", "infineon_cat2_pdl", "typed_provider_candidate", "high",
             "programs an MSCLP register object and invokes the six-word MSCLP configuration writer"),
    0x3680: ("msclp_scan_start_wait", "infineon_cat2_pdl", "typed_provider_candidate", "high",
             "derives a bounded poll count, starts MSCLP, polls completion bit, and clears status"),
    0x5E78: ("msclp_register_config_write", "infineon_cat2_pdl", "typed_provider_candidate", "high",
             "copies six descriptor words to MSCLP offsets 0x3004..0x3034 for selector classes 5/11/other"),
    0x65F4: ("Cy_SCB_I2C_Init", "infineon_cat2_pdl", "public_provider_symbol_match", "high",
             "three-argument base/config/context ABI, SCB register configuration, assertions, context zero/init, status return"),
    0x6F14: ("NVIC_SetPriority", "infineon_cat2_pdl", "exact_cmsis_abi_behavior", "high",
             "maps signed IRQ number to NVIC or SCB priority byte lanes at 0xE000E100/0xE000ED00"),
    0x6F74: ("Cy_SysInt_SetVector", "infineon_cat2_pdl", "public_provider_symbol_match", "high",
             "selects SRAM vector table only when CPUSS vector-in-RAM state is active and returns prior handler"),
    0x6FA8: ("Cy_SysInt_Init", "infineon_cat2_pdl", "public_provider_symbol_match", "high",
             "validates config, applies priority, conditionally installs vector, and returns PDL status"),
    0x6FF0: ("Cy_SysLib_Delay", "infineon_cat2_pdl", "public_provider_symbol_match", "high",
             "overflow-bounded millisecond loop over cy_delay32kMs then cycles = ms*cy_delayFreqKhz"),

    0x4A04: ("capsense_widget_active_query", "infineon_capsense", "typed_provider_candidate", "medium",
             "bounds widget index 0..2 and tests generated widget/sensor state fields"),
    0x4A36: ("capsense_sensor_raw_count_read", "infineon_capsense", "typed_provider_candidate", "high",
             "bounds widget and sensor index then returns the generated sensor record u16 value"),
    0x4A6C: ("capsense_widget_data_pointer", "infineon_capsense", "typed_provider_candidate", "medium",
             "bounds widget index/state class and returns generated widget-data pointer +0x24"),

    0x4B68: ("CalcChecksum", "infineon_emeeprom", "public_provider_symbol_match", "high",
             "CRC-8 seed 0xFF, polynomial 0x31, eight MSB-first rounds: exact Em_EEPROM checksum contract"),
    0x4BA4: ("CheckRanges", "infineon_emeeprom", "public_provider_symbol_candidate", "medium",
             "validates EEPROM configuration/range fields and returns 0x093E0003-class status"),
    0x4C6C: ("CalculateRowChecksum", "infineon_emeeprom", "public_provider_symbol_match", "high",
             "skips the stored checksum byte and invokes CalcChecksum over row size minus four"),
    0x4C78: ("GetStoredRowChecksum", "infineon_emeeprom", "public_provider_symbol_match", "high",
             "returns first word from an EEPROM row"),
    0x4C7C: ("CheckRowChecksum", "infineon_emeeprom", "public_provider_symbol_match", "high",
             "compares stored and calculated row checksums and returns success/bad-checksum status"),
    0x4CA0: ("GetStoredSeqNum", "infineon_emeeprom", "public_provider_symbol_match", "high",
             "returns the second word from an EEPROM row"),
    0x4CA4: ("DefineLastWrittenRow", "infineon_emeeprom", "public_provider_symbol_candidate", "high",
             "scans wear-level rows for greatest sequence number with a valid checksum"),
    0x4D58: ("CheckLastWrittenRowIntegrity", "infineon_emeeprom", "public_provider_symbol_candidate", "high",
             "checks last-row CRC, tries redundant copy, then redefines the last valid row"),
    0x4E0C: ("GetNextRowPointer", "infineon_emeeprom", "public_provider_symbol_match", "high",
             "advances one row and wraps at wear-level region end"),
    0x4E2A: ("GetReadRowPointer", "infineon_emeeprom", "public_provider_symbol_match", "high",
             "moves among wear-level blocks with start/end range correction"),
    0x4E4C: ("CopyHistoricData", "infineon_emeeprom", "public_provider_symbol_candidate", "medium",
             "row/header geometry and checksum helpers match historic-data copy provider topology"),
    0x5254: ("em_eeprom_row_read_helper", "infineon_emeeprom", "typed_provider_candidate", "medium",
             "shared by simple and extended read paths; validates row metadata and copies bounded payload"),
    0x52D4: ("ReadSimpleMode", "infineon_emeeprom", "public_provider_symbol_candidate", "high",
             "selected when context simpleMode is nonzero and performs bounded direct storage read"),
    0x5380: ("em_eeprom_extended_read_row_helper", "infineon_emeeprom", "typed_provider_candidate", "medium",
             "extended-mode row traversal using checksum, wear-level, and bounded copy helpers"),
    0x5508: ("ReadExtendedMode", "infineon_emeeprom", "public_provider_symbol_candidate", "high",
             "selected when context simpleMode is zero and searches checksum-protected historic rows"),
    0x57AC: ("Cy_Em_EEPROM_Read", "infineon_emeeprom", "public_provider_symbol_match", "high",
             "four-argument address/data/size/context ABI, range validation, then simple/extended dispatch"),

    0x73C0: ("__aeabi_uidiv", "toolchain_runtime", "exact_runtime_abi", "high",
             "unsigned restoring division; quotient in r0"),
    0x74CC: ("__aeabi_uidivmod", "toolchain_runtime", "exact_runtime_abi", "high",
             "zero-divisor hook or shared unsigned divider; quotient r0 and remainder r1"),
    0x74D4: ("__aeabi_idiv", "toolchain_runtime", "exact_runtime_abi", "high",
             "signed restoring division with sign normalization"),
    0x76A0: ("__aeabi_idivmod", "toolchain_runtime", "exact_runtime_abi", "high",
             "zero-divisor hook or shared signed divider; quotient r0 and remainder r1"),
    0x76A8: ("__aeabi_idiv0", "toolchain_runtime", "exact_runtime_abi", "high",
             "weak divide-by-zero hook leaf returning immediately"),
    0x76D4: ("memset", "toolchain_runtime", "exact_c_abi_behavior", "high",
             "byte fill from r0 through r0+r2 with r1 and return original r0"),
    0x772C: ("memcpy", "toolchain_runtime", "exact_c_abi_behavior", "high",
             "forward byte copy of r2 bytes from r1 to r0 and return original r0"),
}

EXPECTED = {
    "helper_count": 44,
    "remaining_untyped_helpers": 0,
    "boundary_counts": {
        "infineon_capsense": 3,
        "infineon_cat2_pdl": 10,
        "infineon_emeeprom": 16,
        "open_cfw_clean_room": 8,
        "toolchain_runtime": 7,
    },
    "high_confidence_helpers": 35,
    "medium_confidence_helpers": 9,
    "evidence_digest": "27b3373ad1475a6370eb0acb338f4564e10ba523a4e35d10ab6f61406b00329d",
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_base():
    spec = importlib.util.spec_from_file_location("g2_touch_prefix_map_for_helpers", BASE_ANALYZER)
    require(spec is not None and spec.loader is not None, "cannot load touch prefix analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _literal_evidence(base, payload: bytes, row: dict, entries: set[int]) -> dict:
    body = base._walk(payload, row["entry"], entries)
    literals = []
    for address, insn in sorted(body["instructions"].items()):
        if (
            len(insn.operands) >= 2
            and insn.operands[1].type == ARM_OP_MEM
            and insn.operands[1].mem.base == ARM_REG_PC
        ):
            pool = ((address + 4) & ~3) + insn.operands[1].mem.disp
            if 0 <= pool <= len(payload) - 4:
                value = struct.unpack_from("<I", payload, pool)[0]
                literals.append({"site": address, "pool": pool, "value": value})
    return {
        "literal_words": literals,
        "mmio_literals": sorted({item["value"] for item in literals
                                  if 0x40000000 <= item["value"] < 0x41000000
                                  or 0xE0000000 <= item["value"] < 0xE0100000}),
        "sram_literals": sorted({item["value"] for item in literals
                                  if 0x20000000 <= item["value"] < 0x20002000}),
        "resident_literals": sorted({item["value"] for item in literals
                                      if 0x8680 <= item["value"] < 0x10000}),
        "status_literals": sorted({item["value"] for item in literals
                                    if item["value"] & 0xFFFF0000 == 0x093E0000}),
    }


def _evidence_digest(rows: list[dict]) -> str:
    stable = [{key: row[key] for key in (
        "entry", "proposed_name", "boundary", "name_status", "confidence",
        "instruction_sha256", "callers", "callees", "mmio_literals",
        "sram_literals", "resident_literals", "status_literals",
    )} for row in rows]
    return sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode())


def analyze(*, enforce_expected: bool = True) -> dict:
    base = _load_base()
    prefix = base.analyze()
    require(prefix["metrics"]["row_digest"] == BASE_ROW_DIGEST,
            "touch prefix base-map digest changed")
    unresolved = {row["entry"] for row in prefix["rows"]
                  if row["classification"] == "unresolved_shipped_prefix"}
    require(unresolved == set(HELPERS),
            f"typed helper set does not cover base map: missing={sorted(unresolved-set(HELPERS))}, extra={sorted(set(HELPERS)-unresolved)}")

    payload = base.BLOB.read_bytes()[base.RECORD_OFFSET:base.RECORD_OFFSET + base.RECORD_SIZE]
    entries = {row["entry"] for row in prefix["rows"]}
    callers = {entry: [] for entry in entries}
    for row in prefix["rows"]:
        for callee in row["direct_callees"]:
            callers[callee].append(row["entry"])

    rows = []
    by_entry = {row["entry"]: row for row in prefix["rows"]}
    for entry in sorted(HELPERS):
        name, boundary, name_status, confidence, evidence = HELPERS[entry]
        source = by_entry[entry]
        literals = _literal_evidence(base, payload, source, entries)
        rows.append({
            "entry": entry,
            "stock_name": source["name"],
            "proposed_name": name,
            "boundary": boundary,
            "name_status": name_status,
            "confidence": confidence,
            "evidence": evidence,
            "instruction_bytes": source["instruction_bytes"],
            "instruction_sha256": source["instruction_sha256"],
            "callers": sorted(callers[entry]),
            "callees": source["direct_callees"],
            **{key: value for key, value in literals.items() if key != "literal_words"},
        })

    # Structural pins for the strongest public-provider matches.
    require(by_entry[0x1180]["instruction_bytes"] == 18,
            "Cy_SysLib_DelayCycles body size changed")
    require(by_entry[0x4B68]["instruction_bytes"] == 60,
            "Em_EEPROM CalcChecksum body size changed")
    require({0x093E0000, 0x093E0001, 0x093E0002, 0x093E0003, 0x093E0004}
            <= {value for row in rows if row["boundary"] == "infineon_emeeprom"
                for value in row["status_literals"]},
            "Em_EEPROM status-family literals changed")
    require(set(rows[[row["entry"] for row in rows].index(0x6F14)]["mmio_literals"])
            == {0xE000E100, 0xE000ED00}, "NVIC_SetPriority register evidence changed")
    require(set(rows[[row["entry"] for row in rows].index(0x65F4)]["callees"]) == set(),
            "Cy_SCB_I2C_Init unexpectedly gained a direct callee")

    counts = {boundary: 0 for boundary in PROVIDERS}
    for row in rows:
        counts[row["boundary"]] += 1
    metrics = {
        "helper_count": len(rows),
        "remaining_untyped_helpers": len(unresolved - set(HELPERS)),
        "boundary_counts": counts,
        "high_confidence_helpers": sum(row["confidence"] == "high" for row in rows),
        "medium_confidence_helpers": sum(row["confidence"] == "medium" for row in rows),
        "evidence_digest": _evidence_digest(rows),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"helper evidence {key} changed: {metrics[key]!r} != {expected!r}")

    return {
        "schema_version": 1,
        "analysis_mode": "offline authenticated helper evidence and public-provider comparison; no hardware operation",
        "base_row_digest": BASE_ROW_DIGEST,
        "metrics": metrics,
        "providers": PROVIDERS,
        "rows": rows,
        "clean_room_rules": [
            "MIT is the default for newly authored OpenCFW replacement code.",
            "Apache-2.0 CAT2 PDL code may be reused only with its upstream notices and license preserved.",
            "CAPSENSE and Em_EEPROM public repositories are attribution evidence but carry the Infineon EULA; do not copy them into MIT files.",
            "Compiler/libc routines must come from the selected upstream toolchain/runtime under that provider's license.",
            "A public symbol candidate is not a claim that the stock binary was built from the currently pinned public commit.",
        ],
        "remaining_opacity": {
            "typed_helpers": 44,
            "untyped_helpers": 0,
            "historical_source_commit_proven": 0,
            "exact_historical_private_symbols_proven": 0,
            "note": "All reachable generic helpers now have typed implementation boundaries; historical generating versions remain unavailable.",
        },
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    helper_path = MANIFEST_DIR / "g2-touch-prefix-helper-evidence.tsv"
    lines = [
        "# SPDX-License-Identifier: MIT",
        "# Names marked candidate/clean-room are not historical symbol claims",
        "entry\tproposed_name\tboundary\tname_status\tconfidence\tinstruction_bytes\tinstruction_sha256\tcallers\tcallees\tmmio_literals\tsram_literals\tresident_literals\tstatus_literals\tevidence",
    ]
    for row in result["rows"]:
        fmt = lambda values: ",".join(f"0x{x:08X}" for x in values)
        lines.append(
            f"0x{row['entry']:04X}\t{row['proposed_name']}\t{row['boundary']}\t"
            f"{row['name_status']}\t{row['confidence']}\t{row['instruction_bytes']}\t"
            f"{row['instruction_sha256']}\t{fmt(row['callers'])}\t{fmt(row['callees'])}\t"
            f"{fmt(row['mmio_literals'])}\t{fmt(row['sram_literals'])}\t"
            f"{fmt(row['resident_literals'])}\t{fmt(row['status_literals'])}\t{row['evidence']}"
        )
    helper_path.write_text("\n".join(lines) + "\n")

    provider_path = MANIFEST_DIR / "g2-touch-prefix-provider-boundaries.tsv"
    provider_lines = [
        "# SPDX-License-Identifier: MIT",
        "boundary\tprovider\tsource\tcommit\tlicense\timplementation_rule",
    ]
    for boundary, item in sorted(result["providers"].items()):
        provider_lines.append(
            f"{boundary}\t{item['provider']}\t{item['source']}\t"
            f"{item['commit'] or '-'}\t{item['license']}\t{item['use']}"
        )
    provider_path.write_text("\n".join(provider_lines) + "\n")

    summary_path = MANIFEST_DIR / "g2-touch-prefix-helper-evidence-summary.json"
    summary = {key: value for key, value in result.items() if key != "rows"}
    summary["row_count"] = len(result["rows"])
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return [helper_path, provider_path, summary_path]


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
        print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2, sort_keys=True))
    else:
        print(f"typed helpers: {result['metrics']['helper_count']}")
        print(f"remaining untyped: {result['metrics']['remaining_untyped_helpers']}")
        for boundary, count in result["metrics"]["boundary_counts"].items():
            print(f"  {boundary}: {count}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch prefix helper evidence failed: {exc}") from exc
