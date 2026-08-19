#!/usr/bin/env python3
"""Partition Apollo-main compatibility bytes by conservative origin evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH_ANALYZER = ROOT / "tools/analyze_apollo_embedded_source_paths.py"
DEFAULT_PLAN = ROOT / "build/source/flash-plan.json"
DEFAULT_COMPONENT_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "tools/manifests/g2-apollo-origin-accounting.json"
PLAN_SHA256 = "086841ac128a812376e0389b3b6f0fc91d75186b6a48f79d1d8de4297e54e34c"
MAX_TRUSTWORTHY_FUNCTION_ENVELOPE = 16_384
EXPECTED_FUNCTIONS = 7_370
EXPECTED_REJECTED_ENVELOPES = 8
EXPECTED_MANIFEST_OFFICIAL_BYTES = 3_421_868
EXPECTED_METADATA_GAP_BYTES = 2044
EXPECTED_METADATA_GAP_SITES = 26


class AccountingError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("apollo_paths_for_origin", path)
    if spec is None or spec.loader is None:
        raise AccountingError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _mark(mask: bytearray, start: int, end: int, base: int) -> None:
    first = max(0, start - base)
    last = min(len(mask), end - base)
    if last > first:
        mask[first:last] = b"\1" * (last - first)


def _clear_and_count(mask: bytearray, start: int, end: int, base: int) -> int:
    first = max(0, start - base)
    last = min(len(mask), end - base)
    if last <= first:
        return 0
    overlap = sum(mask[first:last])
    mask[first:last] = b"\0" * (last - first)
    return overlap


def analyze(plan_path: Path, component_report_path: Path, corpus: Path) -> dict[str, Any]:
    if _sha256(plan_path) != PLAN_SHA256:
        raise AccountingError("canonical flash plan identity changed")
    plan = json.loads(plan_path.read_text())
    component_report = json.loads(component_report_path.read_text())
    path_module = _load(PATH_ANALYZER)
    path_report = path_module.analyze(corpus_root=corpus)
    correlation = path_report["ghidra_correlation"]
    base = path_module.LOAD_BASE
    image_size = path_module.IMAGE_SIZE

    official = bytearray(image_size)
    official_regions = [
        row for row in plan["flash_regions"]
        if row.get("component") == "apollo_main"
        and row.get("address_status") == "official_blob"
    ]
    for row in official_regions:
        _mark(official, row["target_address"], row["end_exclusive"], base)
    manifest_official_bytes = sum(official)
    if manifest_official_bytes != EXPECTED_MANIFEST_OFFICIAL_BYTES:
        raise AccountingError(f"manifest official-byte census changed: {manifest_official_bytes}")

    # The component builder is the canonical ownership authority.  Detect
    # flash-plan regions that have not yet been split around newer patch sites,
    # and remove those controlled bytes before classifying the residual.
    metadata_gap_sites = []
    for site in component_report["overlay"]["patched_sites"]:
        size = len(bytes.fromhex(site["replacement_hex"]))
        overlap = _clear_and_count(
            official, site["runtime_address"], site["runtime_address"] + size, base
        )
        if overlap:
            metadata_gap_sites.append({
                "runtime_address": site["runtime_address"],
                "bytes": overlap,
                "branch": site["branch"],
                "name": site["name"],
            })
    for leaf in component_report.get("in_place_leaves", []):
        placement = leaf["placement"]
        overlap = _clear_and_count(
            official,
            placement["runtime_address"],
            placement["runtime_address"] + placement["size"],
            base,
        )
        if overlap:
            metadata_gap_sites.append({
                "runtime_address": placement["runtime_address"],
                "bytes": overlap,
                "branch": "in_place",
                "name": placement["function"],
            })
    metadata_gap_bytes = sum(row["bytes"] for row in metadata_gap_sites)
    if len(metadata_gap_sites) != EXPECTED_METADATA_GAP_SITES or metadata_gap_bytes != EXPECTED_METADATA_GAP_BYTES:
        raise AccountingError(
            f"flash-plan ownership metadata gap changed: sites={len(metadata_gap_sites)} bytes={metadata_gap_bytes}"
        )

    component = component_report["component"]
    true_opaque_bytes = sum(official)
    if true_opaque_bytes != component["opaque_base_bytes"]:
        raise AccountingError(
            f"component/plan opaque reconciliation failed: {true_opaque_bytes} != {component['opaque_base_bytes']}"
        )

    anchored = {row["entry"]: row for row in correlation["functions"]}
    first_party = bytearray(image_size)
    third_party = bytearray(image_size)
    unanchored = bytearray(image_size)
    dependencies = {
        name: bytearray(image_size)
        for name in path_module.EXPECTED_THIRD_PARTY_COUNTS
    }
    accepted = 0
    rejected = []
    for log in path_module.verify_corpus(corpus):
        for match in path_module.FUNCTION_BEGIN_RE.finditer(log.read_text()):
            entry, start, end_inclusive = (
                int(value, 16) for value in match.groups()
            )
            end = end_inclusive + 1
            if end - start > MAX_TRUSTWORTHY_FUNCTION_ENVELOPE:
                rejected.append({
                    "entry": entry, "start": start, "end_exclusive": end,
                    "bytes": end - start,
                })
                continue
            accepted += 1
            anchor = anchored.get(entry)
            if anchor is None:
                _mark(unanchored, start, end, base)
            elif "third_party" in anchor["roots"]:
                _mark(third_party, start, end, base)
                for dependency in anchor["third_party_dependencies"]:
                    _mark(dependencies[dependency], start, end, base)
            else:
                _mark(first_party, start, end, base)
    if accepted + len(rejected) != EXPECTED_FUNCTIONS or len(rejected) != EXPECTED_REJECTED_ENVELOPES:
        raise AccountingError(
            f"trustworthy Ghidra envelope census changed: accepted={accepted} rejected={len(rejected)}"
        )
    if any(row["entry"] in anchored for row in rejected):
        raise AccountingError("an oversized rejected Ghidra envelope gained a source-path anchor")

    buckets = {
        "third_party_path_anchored": 0,
        "first_party_or_project_path_anchored": 0,
        "unanchored_discovered_function": 0,
        "outside_trustworthy_function_envelopes": 0,
    }
    cross_root = 0
    for index, is_official in enumerate(official):
        if not is_official:
            continue
        if third_party[index] and first_party[index]:
            cross_root += 1
        elif third_party[index]:
            buckets["third_party_path_anchored"] += 1
        elif first_party[index]:
            buckets["first_party_or_project_path_anchored"] += 1
        elif unanchored[index]:
            buckets["unanchored_discovered_function"] += 1
        else:
            buckets["outside_trustworthy_function_envelopes"] += 1
    if cross_root:
        raise AccountingError(f"cross-root byte ownership appeared: {cross_root}")
    if sum(buckets.values()) != true_opaque_bytes:
        raise AccountingError("origin buckets do not cover the opaque Apollo base")

    dependency_bytes = {
        name: sum(
            1 for index, is_official in enumerate(official)
            if is_official and mask[index]
        )
        for name, mask in sorted(dependencies.items())
    }
    if sum(dependency_bytes.values()) != buckets["third_party_path_anchored"]:
        raise AccountingError("third-party family buckets do not reconcile")

    expected = json.loads(MANIFEST.read_text())
    actual_counts = {
        "component_opaque_base_bytes": true_opaque_bytes,
        "manifest_official_blob_bytes_before_reconciliation": manifest_official_bytes,
        "controlled_bytes_mislabeled_official_blob": metadata_gap_bytes,
        "origin_buckets": buckets,
        "third_party_family_bytes": dependency_bytes,
    }
    if actual_counts != expected["expected_counts"]:
        raise AccountingError(
            "origin-accounting companion manifest changed: "
            + json.dumps(actual_counts, sort_keys=True)
        )

    external = {}
    for component_name in ("ble_em9305", "case", "touch", "codec"):
        placed = sum(
            row["size"] for row in plan["flash_regions"]
            if row.get("component") == component_name
        )
        unresolved = sum(
            row["size"] for row in plan["unresolved_flash_regions"]
            if row.get("component") == component_name
        )
        container = sum(
            row["size"] for row in plan["container_only_regions"]
            if row.get("component") == component_name
        )
        external[component_name] = {
            "placed_payload_bytes": placed,
            "unresolved_payload_bytes": unresolved,
            "container_metadata_bytes": container,
        }

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "inputs": {
            "flash_plan": str(plan_path), "flash_plan_sha256": PLAN_SHA256,
            "component_sha256": component["sha256"],
            "ghidra_sha256sums_sha256": correlation["corpus"]["sha256sums_sha256"],
        },
        "component_accounting": {
            "bytes": component["size"],
            "generated_wrapper_bytes": component["generated_wrapper_bytes"],
            "generated_patch_site_bytes": component["generated_patch_site_bytes"],
            "source_owned_bytes": component["source_owned_bytes"],
            "opaque_base_bytes": true_opaque_bytes,
        },
        "flash_plan_metadata_gap": {
            "official_blob_bytes_before_reconciliation": manifest_official_bytes,
            "controlled_bytes_mislabeled_official_blob": metadata_gap_bytes,
            "sites": sorted(metadata_gap_sites, key=lambda row: row["runtime_address"]),
            "qualification": "companion accounting corrects classification only; emitted bytes and flash addresses are unchanged",
        },
        "opaque_origin_lower_bounds": buckets,
        "third_party_path_anchored_bytes_by_family": dependency_bytes,
        "ghidra_envelopes": {
            "accepted": accepted,
            "maximum_bytes": MAX_TRUSTWORTHY_FUNCTION_ENVELOPE,
            "rejected_oversized": rejected,
            "qualification": "function envelopes and retained paths are conservative ownership anchors, not pristine-source or instruction-byte identity",
        },
        "external_component_accounting": external,
        "residual_qualification": {
            "unanchored_discovered_function": "code discovered by Ghidra with no retained source-path ownership anchor",
            "outside_trustworthy_function_envelopes": "mixed data, assets, alignment, missed code, and rejected analyzer artifacts; not classified as data alone",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flash-plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--component-report", type=Path, default=DEFAULT_COMPONENT_REPORT)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.flash_plan, args.component_report, args.ghidra_corpus)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        buckets = report["opaque_origin_lower_bounds"]
        print("G2 Apollo origin accounting: PASS")
        print(f"  opaque base: {sum(buckets.values())} bytes")
        print(f"  third-party path-anchored: {buckets['third_party_path_anchored']} bytes")
        print(f"  first-party/project path-anchored: {buckets['first_party_or_project_path_anchored']} bytes")
        print(f"  unanchored discovered functions: {buckets['unanchored_discovered_function']} bytes")
        print(f"  outside trustworthy envelopes: {buckets['outside_trustworthy_function_envelopes']} bytes")
        print("hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
