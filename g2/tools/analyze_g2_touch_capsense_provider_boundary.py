#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Resolve the 55-row touch CAPSENSE provider boundary without source claims."""

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
CAT2_FINAL_ANALYZER = TOOLS / "analyze_g2_touch_cat2_source_admission5.py"
SOURCE = TOUCH / "runtime_touch_capsense_provider.c"
HEADER = TOUCH / "runtime_touch_capsense_provider.h"

# Official public comparison/provider release. This is not claimed as the
# historical source revision used to build the shipped image.
PROVIDER_REPOSITORY = "https://github.com/Infineon/capsense"
PROVIDER_TAG = "release-v3.0.1"
PROVIDER_COMMIT = "25fa1cd5abb4cc66981b04f8872d57d74e398976"
PROVIDER_VERSION = "3.0.1.4842"
PROVIDER_LICENSE = "LicenseRef-Infineon-Cypress-EULA"
LICENSE_SHA256 = "aed445dc4b6832c07501ddb0c937a7bc342bb630d54636fca2b8177ec5722de0"
VERSION_XML_SHA256 = "6576ebac735442b8dd29bb3d172d48a81686ee9f0e135fdf0bcc19d6846501ba"
C_SOURCE_COUNT = 15
C_SOURCE_INVENTORY_DIGEST = "46a460dc11956edb330d1c5950c4409af7fb06b79186eea2d1f74cd47143bb99"

EXPECTED = {
    "boundary_functions": 55,
    "provider_family_resolved": 55,
    "concrete_source_functions": 0,
    "typed_external_functions": 55,
    "mixed_provider_gap_before": 55,
    "mixed_provider_gap_after": 0,
    "semantic_source_gap_before": 166,
    "semantic_source_gap_after_external_typing": 111,
    "component_sizes": [50, 2, 1, 1, 1],
    "external_dependency_entries": 23,
    "row_digest": "eb837e2abd0e62d4628a22476d4db2588ba92dbca2bd27f8ecac3996733a65b4",
    "topology_digest": "10a3f07513133b78772f8ae288e92a84311ca3cc799a1e3c1c3ef8e57f8cb2ed",
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


def _target_compile() -> int:
    clang = shutil.which("clang")
    require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory() as raw:
        output = Path(raw) / "capsense-provider.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0, f"CAPSENSE boundary compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected: bool = True) -> dict:
    semantic_mod = _load(SEMANTIC_ANALYZER, "touch_capsense_boundary_semantics")
    cat2_mod = _load(CAT2_FINAL_ANALYZER, "touch_capsense_boundary_cat2")
    semantic = semantic_mod.analyze()
    cat2 = cat2_mod.analyze()
    source_rows = [row for row in semantic["semantic_rows"]
                   if row["batch"] == "capsense_cat2_mixed"]
    entries = {row["entry"] for row in source_rows}
    require(len(entries) == 55, "mixed CAPSENSE boundary size changed")
    require(cat2["remaining"]["typed_unavailable_entry"] == "0x7038",
            "CAT2 census is no longer closed to one typed halt boundary")
    cat2_admitted = {row["entry"] for row in cat2["rows"]}
    require(not (entries & cat2_admitted), "CAPSENSE boundary overlaps CAT2 admission")

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

    rows = []
    for source_row in sorted(source_rows, key=lambda row: row["entry"]):
        rows.append({
            "entry": source_row["entry"],
            "name": source_row["proposed_name"],
            "status": "typed_external_eula_provider_boundary",
            "provider_family": "Infineon CAPSENSE middleware",
            "provider_comparison_commit": PROVIDER_COMMIT,
            "provider_version_claim": "comparison-only-not-historical-build",
            "license": PROVIDER_LICENSE,
            "concrete_source": False,
            "clean_room_reimplementation_required": True,
            "instruction_bytes": source_row["instruction_bytes"],
            "instruction_sha256": source_row["instruction_sha256"],
            "component": component_by_entry[source_row["entry"]],
            "internal_callers": sorted(set(source_row["callers"]) & entries),
            "internal_callees": sorted(set(source_row["callees"]) & entries),
            "external_dependencies": sorted(
                (set(source_row["callers"]) | set(source_row["callees"])) - entries
            ),
            "evidence": "closed CAT2 census plus cohesive fifth-generation sensing/processing call cluster; exact per-function historical source identity intentionally not asserted",
        })

    combined = SOURCE.read_text() + HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: MIT") == 2,
            "clean-room CAPSENSE boundary license changed")
    require(combined.count("open_cfw_touch_capsense_provider_route") == 2,
            "CAPSENSE provider route changed")
    target_object_bytes = _target_compile()
    topology = [{"component": index, "entries": component}
                for index, component in enumerate(components)]
    metrics = {
        "boundary_functions": len(rows),
        "provider_family_resolved": len(rows),
        "concrete_source_functions": sum(row["concrete_source"] for row in rows),
        "typed_external_functions": sum(row["status"] ==
                                         "typed_external_eula_provider_boundary"
                                         for row in rows),
        "mixed_provider_gap_before": len(rows),
        "mixed_provider_gap_after": 0,
        "semantic_source_gap_before": cat2["metrics"]["semantic_gap_after"],
        "semantic_source_gap_after_external_typing":
            cat2["metrics"]["semantic_gap_after"] - len(rows),
        "component_sizes": sorted((len(component) for component in components),
                                  reverse=True),
        "external_dependency_entries": len(external_dependencies),
        "row_digest": sha256(json.dumps(rows, sort_keys=True,
                                          separators=(",", ":")).encode()),
        "topology_digest": sha256(json.dumps(topology, sort_keys=True,
                                               separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"CAPSENSE boundary {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch CAPSENSE provider boundary admission batch 6",
        "analysis_mode": "offline provider-family and call-topology resolution; no vendor body copied, no hardware or MMIO execution",
        "metrics": metrics, "rows": rows, "topology": topology,
        "provider": {
            "repository": PROVIDER_REPOSITORY, "tag": PROVIDER_TAG,
            "commit": PROVIDER_COMMIT, "version": PROVIDER_VERSION,
            "version_claim": "comparison/provider API pin only; shipped historical revision unresolved",
            "license": PROVIDER_LICENSE, "license_sha256": LICENSE_SHA256,
            "version_xml_sha256": VERSION_XML_SHA256,
            "c_source_count": C_SOURCE_COUNT,
            "c_source_inventory_digest": C_SOURCE_INVENTORY_DIGEST,
        },
        "adapter": {"path": str(SOURCE.relative_to(ROOT)),
                    "license": "MIT", "sha256": sha256(SOURCE.read_bytes()),
                    "target_object_bytes": target_object_bytes},
        "integration": "isolated typed provider contract; not production-routed; absent provider fails closed",
        "remaining": {
            "actionable_semantic_or_source_functions": 111,
            "typed_external_capsense_functions": 55,
            "note": "typed external bytes/functions are not concrete OpenCFW source",
        },
        "exclusions": "CAPSENSE vendor bodies are not copied or counted as open source; EULA Em_EEPROM, application/startup, legacy halt and DFU/system boundaries unchanged",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    boundary = MANIFEST_DIR / "g2-touch-capsense-provider-boundary.tsv"
    with boundary.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "name", "status", "provider_family",
                         "provider_comparison_commit", "provider_version_claim",
                         "license", "concrete_source", "clean_room_reimplementation_required",
                         "instruction_bytes", "instruction_sha256", "component",
                         "internal_callers", "internal_callees", "external_dependencies",
                         "evidence"])
        for row in result["rows"]:
            fmt = lambda values: ",".join(f"0x{value:04X}" for value in values)
            writer.writerow([
                f"0x{row['entry']:04X}", row["name"], row["status"],
                row["provider_family"], row["provider_comparison_commit"],
                row["provider_version_claim"], row["license"],
                str(row["concrete_source"]).lower(),
                str(row["clean_room_reimplementation_required"]).lower(),
                row["instruction_bytes"], row["instruction_sha256"], row["component"],
                fmt(row["internal_callers"]), fmt(row["internal_callees"]),
                fmt(row["external_dependencies"]), row["evidence"],
            ])
    topology = MANIFEST_DIR / "g2-touch-capsense-provider-topology.tsv"
    with topology.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["component", "functions", "entries"])
        for row in result["topology"]:
            writer.writerow([row["component"], len(row["entries"]),
                             ",".join(f"0x{entry:04X}" for entry in row["entries"])])
    summary = MANIFEST_DIR / "g2-touch-capsense-provider-boundary-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("rows", "topology")}
    slim["row_count"] = len(result["rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [boundary, topology, summary]


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
                          if key not in ("rows", "topology")},
                         indent=2, sort_keys=True))
    else:
        print(f"typed CAPSENSE provider boundaries: {result['metrics']['typed_external_functions']}")
        print(f"remaining actionable semantic/source functions: {result['remaining']['actionable_semantic_or_source_functions']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch CAPSENSE boundary failed: {exc}") from exc
