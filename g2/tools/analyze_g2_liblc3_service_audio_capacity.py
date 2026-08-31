#!/usr/bin/env python3
"""Audit the whole-address and size-optimized LC3 service route capacity.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from collections import Counter
from itertools import permutations
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
COMPONENT = G2 / "components/apollo_main/liblc3_encoder"
MANIFEST = COMPONENT / "service_audio_capacity_experiment.json"
BUILDER = COMPONENT / "build_service_audio_capacity_experiment.py"


class CapacityAuditError(RuntimeError):
    """Raised when package, placement, or build evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CapacityAuditError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CapacityAuditError(f"cannot read {path}: {error}") from error
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def resolve(relative: str) -> Path:
    path = (G2 / relative).resolve()
    try:
        path.relative_to(G2.resolve())
    except ValueError as error:
        raise CapacityAuditError(f"path escapes G2 root: {relative}") from error
    return path


def authenticate(record: dict[str, Any]) -> tuple[Path, bytes]:
    path = resolve(record["path"])
    payload = path.read_bytes()
    require(len(payload) == record["size"], f"size drift: {path}")
    require(sha256_bytes(payload) == record["sha256"], f"hash drift: {path}")
    return path, payload


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "open_cfw_liblc3_capacity_audit_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise CapacityAuditError("cannot load capacity builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def align_up(value: int, alignment: int) -> int:
    require(alignment > 0 and alignment & (alignment - 1) == 0,
            "invalid placement alignment")
    return (value + alignment - 1) & -alignment


def _compare_directories(first: Path, second: Path) -> None:
    left = sorted(path.relative_to(first) for path in first.rglob("*")
                  if path.is_file())
    right = sorted(path.relative_to(second) for path in second.rglob("*")
                   if path.is_file())
    require(left == right, "capacity artifact set is not deterministic")
    for relative in left:
        require((first / relative).read_bytes() ==
                (second / relative).read_bytes(),
                f"capacity artifact bytes drift: {relative}")


def _package_model(manifest: dict[str, Any]) -> dict[str, Any]:
    evidence = manifest["package_evidence"]
    plan_path, _ = authenticate(evidence["flash_plan"])
    report_path, _ = authenticate(evidence["build_report"])
    authenticate(evidence["core_config"])
    _core_report_path, _ = authenticate(evidence["core_report"])
    _capacity_path, _ = authenticate(evidence["capacity_proposal"])
    plan = read_json(plan_path)
    report = read_json(report_path)
    address = manifest["address_contract"]
    regions = sorted((row for row in plan["flash_regions"]
                      if row.get("component") == "apollo_main" and
                      row.get("target") == "apollo510b_internal_mram"),
                     key=lambda row: (row["target_address"],
                                      row["end_exclusive"]))
    require(len(regions) == address["component_region_count"],
            "package Apollo region count drift")
    cursor = address["run_base"]
    status_bytes: Counter[str] = Counter()
    for row in regions:
        require(row["target_address"] == cursor and
                row["end_exclusive"] - row["target_address"] == row["size"],
                "package Apollo regions are not an exact nonoverlapping cover")
        cursor = row["end_exclusive"]
        status_bytes[row["address_status"]] += row["size"]
    require(cursor == address["current_core_end_exclusive"] and
            cursor - address["run_base"] ==
            address["component_runtime_bytes"],
            "package Apollo runtime cover drift")
    require(status_bytes["generated_padding"] ==
            address["generated_padding_bytes"] and
            status_bytes["generated_alignment"] ==
            address["generated_alignment_bytes"],
            "package generated padding/alignment accounting drift")
    padding = [row for row in regions
               if row["address_status"] == "generated_padding"]
    alignment = [row for row in regions
                 if row["address_status"] == "generated_alignment"]
    require(max(row["size"] for row in padding) ==
            address["largest_generated_padding_interval"] and
            max(row["size"] for row in alignment) ==
            address["largest_generated_alignment_interval"],
            "largest authenticated interior padding interval drift")
    apollo_provider = [row for row in report["providers"]
                       if row["component"] == "apollo_main"]
    apollo_entry = [row for row in report["entries"]
                    if row["filename"] == "ota/s200_firmware_ota.bin"]
    require(len(apollo_provider) == len(apollo_entry) == 1 and
            apollo_provider[0]["size"] == cursor - address["run_base"] + 32 and
            apollo_entry[0]["payload_size"] == apollo_provider[0]["size"] and
            report["unresolved_region_count"] == 0,
            "package Apollo provider/OTA entry receipt drift")
    return {
        "flash_plan_region_count": len(plan["flash_regions"]),
        "apollo_region_count": len(regions),
        "run_base": address["run_base"],
        "runtime_end_exclusive": cursor,
        "runtime_bytes": cursor - address["run_base"],
        "exact_contiguous_region_cover": True,
        "status_bytes": dict(sorted(status_bytes.items())),
        "generated_padding_intervals": [
            {key: row[key] for key in
             ("region", "target_address", "end_exclusive", "size")}
            for row in padding],
        "largest_generated_padding_interval": max(
            row["size"] for row in padding),
        "largest_generated_alignment_interval": max(
            row["size"] for row in alignment),
        "ota_entry_crc32c_msb": apollo_entry[0]["crc32c_msb"],
        "ota_atomic_rebuild_performed": False,
    }


def _placement_model(manifest: dict[str, Any],
                     profile: dict[str, Any]) -> dict[str, Any]:
    address = manifest["address_contract"]
    sizes = {name: profile["sections"][name]["size"]
             for name in ("text", "rodata", "table_rodata")}
    alignments = {"text": 16, "rodata": 16, "table_rodata": 8}
    start = address["current_core_end_exclusive"]
    limit = address["protected_update_record_start"]
    candidates = []
    for order in permutations(sizes):
        cursor = start
        placed = []
        for name in order:
            section_start = align_up(cursor, alignments[name])
            section_end = section_start + sizes[name]
            placed.append({"name": name, "start": section_start,
                           "end_exclusive": section_end,
                           "size": sizes[name],
                           "alignment": alignments[name]})
            cursor = section_end
        candidates.append((max(0, cursor - limit), cursor, order, placed))
    shortfall, end, order, sections = min(candidates)
    require(shortfall <= profile["capacity"]["shortfall"],
            "whole-address append solver is worse than linked receipt")
    no_table_ends = []
    for no_table_order in permutations(("text", "rodata")):
        no_table_cursor = start
        for name in no_table_order:
            no_table_cursor = align_up(
                no_table_cursor, alignments[name]) + sizes[name]
        no_table_ends.append(no_table_cursor)
    conditional_start = start - address["conditional_repack_savings"]
    conditional_candidates = []
    for conditional_order in permutations(sizes):
        conditional_cursor = conditional_start
        for name in conditional_order:
            conditional_cursor = align_up(
                conditional_cursor, alignments[name]) + sizes[name]
        conditional_candidates.append(
            (limit - conditional_cursor, conditional_cursor,
             conditional_order))
    conditional_margin, conditional_end, conditional_order = max(
        conditional_candidates)
    text_section = next(row for row in sections if row["name"] == "text")
    stock_entries = {
        "open_cfw_liblc3_service_audio_stock_setup": 0x0057A926,
        "open_cfw_liblc3_service_audio_stock_encode": 0x0057A940,
    }
    veneer_targets = {
        name: text_section["start"] + int(profile["roots"][name]["offset"])
        for name in stock_entries
    }
    maximum_displacement = max(
        abs(veneer_targets[name] - stock_entry)
        for name, stock_entry in stock_entries.items())
    return {
        "permutation_count": len(candidates),
        "best_append_order": list(order),
        "best_append_sections": sections,
        "best_append_end_exclusive": end,
        "append_shortfall": shortfall,
        "linked_order_append_shortfall": profile["capacity"]["shortfall"],
        "whole_address_production_fit": False,
        "interior_intervals_admitted_for_new_ownership": 0,
        "protected_interior_padding_bytes":
            address["generated_padding_bytes"] +
            address["generated_alignment_bytes"],
        "largest_protected_interior_interval": max(
            address["largest_generated_padding_interval"],
            address["largest_generated_alignment_interval"]),
        "smallest_indivisible_section_bytes": min(sizes.values()),
        "smallest_executable_or_bulk_rodata_section_bytes": min(
            sizes["text"], sizes["rodata"]),
        "veneer_targets": veneer_targets,
        "maximum_veneer_displacement": maximum_displacement,
        "thumb_bw_range_sufficient": maximum_displacement < (1 << 24),
        "best_order_final_relocation_replay_attempted": False,
        "placing_only_table_in_protected_padding_counterfactual_shortfall":
            max(0, min(no_table_ends) - limit),
        "conditional_repack": {
            "already_applied": False,
            "savings": address["conditional_repack_savings"],
            "core_end_exclusive": conditional_start,
            "best_order": list(conditional_order),
            "encoder_end_exclusive": conditional_end,
            "margin_before_update_record": conditional_margin,
            "oz_closure_would_fit": conditional_margin >= 0,
            "production_authority": False,
        },
    }


def analyze(manifest_path: Path = MANIFEST) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    require(manifest.get("schema_version") == 1 and
            manifest.get("mode") ==
            "whole-address-capacity-qualified-unplaced",
            "capacity manifest schema drift")
    require(manifest.get("routing") == {
        "production_placement": False, "service_audio_routed": False,
        "firmware_image_emitted": False, "hardware_operations": False,
    }, "capacity manifest gained routing or hardware authority")
    for name, source in manifest["sources"].items():
        path = resolve(source["path"])
        require(path.is_file() and sha256(path) == source["sha256"],
                f"{name} source pin drift")
    route = manifest["route_config"]
    require(sha256(resolve(route["path"])) == route["sha256"],
            "route config pin drift")
    package = _package_model(manifest)
    builder = load_builder()
    profiles: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(
            prefix="open-cfw-lc3-whole-address-") as temporary:
        root = Path(temporary)
        for profile in sorted(manifest["profiles"]):
            first_dir = root / profile / "first"
            second_dir = root / profile / "second"
            first = builder.build(
                manifest_path=manifest_path, output_dir=first_dir,
                profile=profile, record=False)
            second = builder.build(
                manifest_path=manifest_path, output_dir=second_dir,
                profile=profile, record=False)
            require(first == second,
                    f"{profile}: capacity build report drift")
            _compare_directories(first_dir, second_dir)
            selected = first["accepted"]["oz_gc"]
            require(selected["imports"] ==
                    manifest["required_runtime_imports"] and
                    selected["relocation_application"][
                        "all_input_relocations_applied"] and
                    selected["relocation_application"][
                        "output_relocations"] == 0 and
                    selected["relocation_application"][
                        "input_table_initializers"] == 78 and
                    selected["relocation_application"][
                        "input_table_code_references"] == 6,
                    f"{profile}: selected relocation/table closure drift")
            profiles[profile] = {
                "build": first,
                "byte_reproducible_two_builds": True,
                "placement": _placement_model(manifest, selected),
            }
    require(profiles["apple-clang"]["placement"]["append_shortfall"] ==
            9152 and
            profiles["linux-clang"]["placement"]["append_shortfall"] ==
            9100,
            "dual-profile optimized shortfall drift")
    return {
        "schema_version": 1,
        "status": "liblc3-whole-address-size-qualified-placement-blocked",
        "manifest": {"path": str(manifest_path.relative_to(G2)),
                     "sha256": sha256(manifest_path)},
        "package": package,
        "profiles": profiles,
        "behavior": {
            "host_o2_vs_oz_complete_dynamic_grid_required": True,
            "compile_time_feature_set_unchanged": True,
            "external_runtime_binding_set_unchanged": True,
            "read_only_table_object_set_unchanged": True,
        },
        "routing": manifest["routing"] | {
            "production_patch_bytes_emitted": False,
            "remaining_blockers": [
                "The accepted Apple -Oz/GC closure still exceeds the only "
                "unowned contiguous append interval by 9,152 bytes even "
                "after enumerating all six section orders.",
                "All interior package bytes are already owned; generated PT "
                "padding and LTPF/alignment reservations have no LC3 ownership.",
                "The 30,676-byte capacity repack would make -Oz fit with "
                "21,532 bytes margin, but its production move/replay contract "
                "is not implemented.",
                "Final stock runtime addresses, OTA CRC regeneration, and "
                "atomic package emission remain unassigned.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze(args.manifest.resolve())
    except (CapacityAuditError, OSError, KeyError, TypeError, ValueError,
            RuntimeError) as error:
        print(f"LC3 whole-address capacity audit failed: {error}",
              file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True,
                     indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
