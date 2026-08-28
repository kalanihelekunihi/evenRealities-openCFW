#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit exact critical helpers and bound the remaining touch application family."""

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
CAPSENSE_ANALYZER = TOOLS / "analyze_g2_touch_capsense_provider_boundary.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
APPLICATION_SOURCE = TOUCH / "runtime_touch_application_boundary.c"
APPLICATION_HEADER = TOUCH / "runtime_touch_application_boundary.h"
CRITICAL_ASSEMBLY = TOUCH / "runtime_touch_critical_adapters.S"

CAT2_COMMIT = "35f1714623cfea682d5e285af80d50416b4c7bbc"
SYSLIB_ASSEMBLY = "drivers/source/COMPONENT_CM0P/TOOLCHAIN_GCC_ARM/cy_syslib_gcc.S"
SYSLIB_ASSEMBLY_SHA256 = "c566a2156931e4179b8adfd591eee9fe3bc88e90d325ec37f43fdb599dcae281"
APPLICATION_CUTOFF = 0x156C

EXACT_ADMISSIONS = {
    0x1192: (
        "Cy_SysLib_EnterCriticalSection",
        "open_cfw_touch_enter_critical",
        "1192:mrs r0, primask|1196:cpsid i|1198:bx lr",
    ),
    0x119A: (
        "Cy_SysLib_ExitCriticalSection",
        "open_cfw_touch_exit_critical",
        "119A:msr primask, r0|119E:bx lr",
    ),
}

EXPECTED = {
    "family_functions": 99,
    "exact_upstream_functions": 2,
    "clean_room_contract_functions": 97,
    "platform_startup_contracts": 46,
    "touch_application_contracts": 51,
    "application_ambiguity_before": 99,
    "application_ambiguity_after": 0,
    "actionable_semantic_source_before": 111,
    "concrete_source_or_implementation_gap_after": 109,
    "concrete_implemented_contracts": 0,
    "component_sizes": [71, 5, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "external_dependency_entries": 61,
    "exact_row_digest": "9d4c00849617cf694e43fdf0402f8c68bbcfef6aa12cbd90fe2891aea12975a2",
    "contract_row_digest": "17a55e2947ac8488b396119dffcc68d274b6944dd257a9db4f8386c30081f69c",
    "topology_digest": "21257118b041a260fe9c8fbf6cd7fb0cc5e3027249acfa70ac0ff0c045ff84b8",
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


def _components(entries: set[int], adjacency: dict[int, set[int]]) -> list[list[int]]:
    remaining = set(entries)
    result = []
    while remaining:
        pending = [min(remaining)]
        component = set()
        while pending:
            entry = pending.pop()
            if entry in component:
                continue
            component.add(entry)
            pending.extend(sorted(adjacency[entry] - component, reverse=True))
        remaining -= component
        result.append(sorted(component))
    return sorted(result, key=lambda values: (-len(values), values))


def _canonical_body(prefix, payload: bytes, entry: int, entries: set[int]) -> str:
    body = prefix._walk(payload, entry, entries)
    return "|".join(
        f"{address:04X}:{insn.mnemonic} {insn.op_str}"
        for address, insn in sorted(body["instructions"].items())
    )


def _target_compile() -> dict[str, int]:
    clang = shutil.which("clang")
    require(clang is not None, "clang unavailable")
    sizes = {}
    with tempfile.TemporaryDirectory() as raw:
        for source in (APPLICATION_SOURCE, CRITICAL_ASSEMBLY):
            output = Path(raw) / f"{source.stem}.o"
            command = [
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                "-ffreestanding", "-Wall", "-Wextra", "-Werror", "-I", str(TOUCH),
            ]
            if source.suffix == ".c":
                command.append("-std=c11")
            command.extend(["-c", str(source), "-o", str(output)])
            proc = subprocess.run(command, capture_output=True, text=True)
            require(proc.returncode == 0,
                    f"application boundary target compile failed: {proc.stderr}")
            sizes[source.name] = output.stat().st_size
    return sizes


def analyze(*, enforce_expected: bool = True) -> dict:
    semantic_mod = _load(SEMANTIC_ANALYZER, "touch_application_boundary_semantics")
    capsense_mod = _load(CAPSENSE_ANALYZER, "touch_application_boundary_capsense")
    prefix = _load(PREFIX_ANALYZER, "touch_application_boundary_prefix")
    semantic = semantic_mod.analyze()
    capsense = capsense_mod.analyze()
    source_rows = [row for row in semantic["semantic_rows"]
                   if row["batch"] == "application_startup_clean_room"]
    by_entry = {row["entry"]: row for row in source_rows}
    entries = set(by_entry)
    require(len(entries) == 99, "application/startup family size changed")
    require(set(EXACT_ADMISSIONS) <= entries, "exact critical helpers disappeared")
    require(capsense["remaining"]["actionable_semantic_or_source_functions"] == 111,
            "batch-6 actionable census changed")

    blob = prefix.BLOB.read_bytes()
    payload = blob[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    all_semantic_entries = {row["entry"] for row in semantic["semantic_rows"]}
    signatures = {}
    for entry, (_, _, expected_body) in EXACT_ADMISSIONS.items():
        canonical = _canonical_body(prefix, payload, entry, all_semantic_entries)
        require(canonical == expected_body,
                f"critical helper target body changed at {entry:#x}: {canonical}")
        signatures[entry] = sha256(canonical.encode())

    application_text = APPLICATION_SOURCE.read_text() + APPLICATION_HEADER.read_text()
    require(application_text.count("SPDX-License-Identifier: MIT") == 2,
            "clean-room application boundary license changed")
    require(application_text.count("open_cfw_touch_application_provider_route") == 2,
            "application provider route changed")
    assembly_text = CRITICAL_ASSEMBLY.read_text()
    require(assembly_text.count("SPDX-License-Identifier: Apache-2.0") == 1,
            "critical adapter Apache declaration changed")
    require(CAT2_COMMIT in assembly_text, "critical adapter provider pin changed")
    for _, adapter, _ in EXACT_ADMISSIONS.values():
        require(assembly_text.count(adapter) == 5,
                f"critical adapter symbol declaration changed: {adapter}")
    target_objects = _target_compile()

    adjacency = {entry: set() for entry in entries}
    external_dependencies = set()
    for row in source_rows:
        for target in row["callers"] + row["callees"]:
            if target in entries:
                adjacency[row["entry"]].add(target)
                adjacency[target].add(row["entry"])
            else:
                external_dependencies.add(target)
    components = _components(entries, adjacency)
    component_by_entry = {
        entry: index for index, component in enumerate(components)
        for entry in component
    }

    exact_rows = []
    for entry, (symbol, adapter, _) in sorted(EXACT_ADMISSIONS.items()):
        source_row = by_entry[entry]
        exact_rows.append({
            "entry": entry,
            "symbol": symbol,
            "status": "exact_upstream_source_admitted",
            "source": f"https://github.com/Infineon/mtb-pdl-cat2/blob/{CAT2_COMMIT}/{SYSLIB_ASSEMBLY}",
            "source_file_sha256": SYSLIB_ASSEMBLY_SHA256,
            "provider_commit": CAT2_COMMIT,
            "license": "Apache-2.0",
            "adapter": CRITICAL_ASSEMBLY.name,
            "adapter_symbol": adapter,
            "instruction_bytes": source_row["instruction_bytes"],
            "instruction_sha256": source_row["instruction_sha256"],
            "target_signature_sha256": signatures[entry],
            "component": component_by_entry[entry],
            "evidence": "exact Cortex-M0+ instruction body and public upstream assembly symbol",
        })

    contract_rows = []
    for source_row in sorted(source_rows, key=lambda row: row["entry"]):
        entry = source_row["entry"]
        if entry in EXACT_ADMISSIONS:
            continue
        family = ("platform_startup_configuration" if entry < APPLICATION_CUTOFF
                  else "touch_application_processing")
        contract_rows.append({
            "entry": entry,
            "name": source_row["proposed_name"],
            "family": family,
            "status": "typed_clean_room_reimplementation_contract",
            "license": "MIT-for-new-clean-room-code",
            "concrete_source": False,
            "implemented": False,
            "instruction_bytes": source_row["instruction_bytes"],
            "instruction_sha256": source_row["instruction_sha256"],
            "component": component_by_entry[entry],
            "internal_callers": sorted(set(source_row["callers"]) & entries),
            "internal_callees": sorted(set(source_row["callees"]) & entries),
            "external_dependencies": sorted(
                (set(source_row["callers"]) | set(source_row["callees"])) - entries
            ),
            "evidence": "address partition and call topology only; behavior, ABI and historical source remain unasserted",
        })

    topology = [{"component": index, "entries": component}
                for index, component in enumerate(components)]
    metrics = {
        "family_functions": len(source_rows),
        "exact_upstream_functions": len(exact_rows),
        "clean_room_contract_functions": len(contract_rows),
        "platform_startup_contracts": sum(
            row["family"] == "platform_startup_configuration" for row in contract_rows),
        "touch_application_contracts": sum(
            row["family"] == "touch_application_processing" for row in contract_rows),
        "application_ambiguity_before": len(source_rows),
        "application_ambiguity_after": 0,
        "actionable_semantic_source_before":
            capsense["remaining"]["actionable_semantic_or_source_functions"],
        "concrete_source_or_implementation_gap_after":
            capsense["remaining"]["actionable_semantic_or_source_functions"] - len(exact_rows),
        "concrete_implemented_contracts": sum(row["implemented"] for row in contract_rows),
        "component_sizes": [len(component) for component in components],
        "external_dependency_entries": len(external_dependencies),
        "exact_row_digest": sha256(json.dumps(exact_rows, sort_keys=True,
                                                  separators=(",", ":")).encode()),
        "contract_row_digest": sha256(json.dumps(contract_rows, sort_keys=True,
                                                     separators=(",", ":")).encode()),
        "topology_digest": sha256(json.dumps(topology, sort_keys=True,
                                                separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"application boundary {key} changed: {metrics[key]!r} != {expected!r}")

    return {
        "schema_version": 1,
        "component": "G2 touch application/startup source admission batch 7",
        "analysis_mode": "offline exact instruction/source admission plus conservative call-topology contracts; no vendor body copied and no hardware or MMIO execution",
        "metrics": metrics,
        "exact_rows": exact_rows,
        "contract_rows": contract_rows,
        "topology": topology,
        "upstream": {
            "repository": "https://github.com/Infineon/mtb-pdl-cat2",
            "commit": CAT2_COMMIT,
            "source": SYSLIB_ASSEMBLY,
            "source_file_sha256": SYSLIB_ASSEMBLY_SHA256,
            "license": "Apache-2.0",
        },
        "adapters": {
            "critical": {"path": str(CRITICAL_ASSEMBLY.relative_to(ROOT)),
                         "license": "Apache-2.0",
                         "sha256": sha256(CRITICAL_ASSEMBLY.read_bytes()),
                         "target_object_bytes": target_objects[CRITICAL_ASSEMBLY.name]},
            "application_contract": {
                "path": str(APPLICATION_SOURCE.relative_to(ROOT)),
                "license": "MIT", "sha256": sha256(APPLICATION_SOURCE.read_bytes()),
                "target_object_bytes": target_objects[APPLICATION_SOURCE.name],
            },
        },
        "integration": "isolated adapters and typed contracts; not production-routed; absent application provider fails closed",
        "remaining": {
            "concrete_source_or_implementation_functions": 109,
            "clean_room_contracts_unimplemented": len(contract_rows),
            "other_typed_external_or_unavailable_functions": 12,
            "note": "typed clean-room contracts are not implementations and are not counted as concrete OpenCFW source",
        },
        "exclusions": "CAPSENSE and Em_EEPROM EULA bodies remain external; application behavior and startup policy are not inferred from control-flow topology",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    exact = MANIFEST_DIR / "g2-touch-application-upstream-admission.tsv"
    with exact.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "status", "source", "source_file_sha256",
                         "provider_commit", "license", "adapter", "adapter_symbol",
                         "instruction_bytes", "instruction_sha256",
                         "target_signature_sha256", "component", "evidence"])
        for row in result["exact_rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["symbol"], row["status"], row["source"],
                row["source_file_sha256"], row["provider_commit"], row["license"],
                row["adapter"], row["adapter_symbol"], row["instruction_bytes"],
                row["instruction_sha256"], row["target_signature_sha256"],
                row["component"], row["evidence"],
            ])
    contracts = MANIFEST_DIR / "g2-touch-application-clean-room-contracts.tsv"
    with contracts.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "name", "family", "status", "license",
                         "concrete_source", "implemented", "instruction_bytes",
                         "instruction_sha256", "component", "internal_callers",
                         "internal_callees", "external_dependencies", "evidence"])
        fmt = lambda values: ",".join(f"0x{value:04X}" for value in values)
        for row in result["contract_rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["name"], row["family"], row["status"],
                row["license"], str(row["concrete_source"]).lower(),
                str(row["implemented"]).lower(), row["instruction_bytes"],
                row["instruction_sha256"], row["component"],
                fmt(row["internal_callers"]), fmt(row["internal_callees"]),
                fmt(row["external_dependencies"]), row["evidence"],
            ])
    topology = MANIFEST_DIR / "g2-touch-application-topology.tsv"
    with topology.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["component", "functions", "entries"])
        for row in result["topology"]:
            writer.writerow([row["component"], len(row["entries"]),
                             ",".join(f"0x{entry:04X}" for entry in row["entries"])])
    summary = MANIFEST_DIR / "g2-touch-application-boundary-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("exact_rows", "contract_rows", "topology")}
    slim["exact_row_count"] = len(result["exact_rows"])
    slim["contract_row_count"] = len(result["contract_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [exact, contracts, topology, summary]


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
                          if key not in ("exact_rows", "contract_rows", "topology")},
                         indent=2, sort_keys=True))
    else:
        print(f"exact upstream application helpers: {result['metrics']['exact_upstream_functions']}")
        print(f"unimplemented clean-room contracts: {result['remaining']['clean_room_contracts_unimplemented']}")
        print(f"remaining concrete source/implementation gap: {result['remaining']['concrete_source_or_implementation_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch application boundary failed: {exc}") from exc
