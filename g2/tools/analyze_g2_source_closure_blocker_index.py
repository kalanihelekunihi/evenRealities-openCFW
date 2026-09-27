#!/usr/bin/env python3
"""Build one index of the remaining source-closure blockers."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_apollo_main_source_blockers as apollo_main
import analyze_g2_bootloader_source_blockers as bootloader
import analyze_g2_case_source_blockers as case
import analyze_g2_codec_source_blockers as codec
import analyze_g2_em9305_source_blockers as em9305
import analyze_g2_gate_raw_transcript_blockers as gate_raw
import analyze_g2_source_only_blockers as source_only
import analyze_g2_source_ownership_quality_blockers as ownership_quality
import analyze_g2_touch_source_blockers as touch
import analyze_g2_untracked_overlay_inputs as untracked_inputs
import analyze_g2_am_branch_target_blockers as am_branch_targets
import analyze_g2_am_linear_raw_blockers as am_linear_raw
import analyze_g2_am_pc_boundary_blockers as am_pc_boundary
import analyze_g2_am_pc_relative_blockers as am_pc_relative
import analyze_g2_am_system_decode_blockers as am_system_decode
import analyze_g2_am_vector_it_blockers as am_vector_it


OUT = ROOT / "tools/manifests/g2-source-closure-blocker-index.json"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
RETAINED_HOT_TARGETS = ROOT / "tools/manifests/g2-apollo-retained-hot-targets.json"
AM115_PULLTHROUGH = (
    ROOT / "tools/manifests/g2-apollo-am115-pullthrough-candidate.json"
)
AM145_PULLTHROUGH = (
    ROOT / "tools/manifests/g2-apollo-am145-pullthrough-candidate.json"
)


def _component_frontier(components: dict, source_components: dict) -> list[dict]:
    rows = []
    for name, report in components.items():
        blocking = report["release_blocking_bytes"]
        if blocking == 0:
            continue
        row = {
            "scope": name,
            "kind": "component_release_blocker",
            "blocking_bytes": blocking,
            "production_routed": report["production_routed"],
            "source_complete": report.get("source_complete", blocking == 0),
            "exit_criteria": source_components[name]["exit_criteria"],
        }
        if name == "codec":
            row["external_provider_bytes_by_class"] = report[
                "external_provider"]["bytes_by_class"]
            row["typed_external_span_count"] = report[
                "typed_external_span_map"]["span_count"]
            row["source_only_macos_route"] = report["source_only_macos_route"]
        if name == "apollo_main":
            row["source_build_route"] = report["source_build_route"]
        if name == "ble_em9305":
            row["residual_readiness"] = report["residual_frontier"]["readiness"]
            row["largest_residual_blocker"] = report[
                "residual_frontier"]["largest_unresolved_spans"][0]
            row["source_build_route"] = report["source_build_route"]
        if name == "apollo_bootloader":
            row["retained_official_bytes_by_family"] = report[
                "retained_official_frontier"]["bytes_by_family"]
            row["largest_retained_interval"] = report[
                "retained_official_frontier"]["largest_intervals"][0]
            row["source_build_route"] = report["source_build_route"]
        if name == "case":
            row["whole_blob_bucket_bytes"] = report["whole_blob_bucket_bytes"]
            row["candidate_admission_blocker_class"] = report[
                "candidate_admission_blocker_class"]
            row["gap_classification_counts"] = report[
                "gap_classification_counts"]
            row["source_only_macos_route"] = report["source_only_macos_route"]
        if name == "touch":
            row["whole_blob_bucket_bytes"] = report["whole_blob_bucket_bytes"]
            row["candidate_admission_blocker_class"] = report[
                "candidate_admission_blocker_class"]
            row["typed_physical_bucket_bytes"] = report[
                "typed_physical_bucket_bytes"]
            row["resident_abi_available"] = report["resident_abi_available"]
            row["source_only_macos_route"] = report["source_only_macos_route"]
        rows.append(row)
    return sorted(rows, key=lambda row: (-row["blocking_bytes"], row["scope"]))


def _owner_counts_for_segments(segments: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for segment in segments:
        for owner, count in segment.get("branch_target_owner_counts", {}).items():
            counts[owner] = counts.get(owner, 0) + count
    return dict(sorted(counts.items()))


def _ranked_counts(field: str, counts: dict[str, int]) -> list[dict[str, object]]:
    return [
        {field: key, "count": count}
        for key, count in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]


def _apollo_main_region_index() -> dict[str, dict[str, object]]:
    manifest = json.loads(CORE_MANIFEST.read_text())
    regions = manifest["component_overrides"]["apollo_main"]["regions"]
    return {region["name"]: region for region in regions}


def _ranked_owner_frontier(
    counts: dict[str, int],
    apollo_main_regions: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    rows = _ranked_counts("owner", counts)
    for row in rows:
        owner = str(row["owner"])
        owner_parts = owner.split(":")
        if len(owner_parts) != 3 or owner_parts[0] != "apollo_main":
            continue
        region = apollo_main_regions.get(owner_parts[1])
        if region is None:
            continue
        file_offset = region["file_offset"]
        target_address = region["target_address"]
        size = region["size"]
        row["component"] = "apollo_main"
        row["region"] = region["name"]
        row["address_status"] = region["address_status"]
        row["file_offset"] = file_offset
        row["end_file_offset"] = file_offset + size
        row["target_address"] = target_address
        row["end_target_address"] = target_address + size
        row["size"] = size
        row["function"] = region["function"]
        row["output"] = region["output"]
    return rows


def _site_key(row: dict[str, object]) -> tuple[str, int]:
    return (str(row["owner"]), int(row["target_address"]))


def _ranked_branch_target_sites(
    segments: list[dict[str, object]],
) -> list[dict[str, object]]:
    counts: dict[tuple[str, int], int] = {}
    sites: dict[tuple[str, int], dict[str, object]] = {}
    call_site_examples: dict[tuple[str, int], list[dict[str, object]]] = {}
    for segment in segments:
        for site in segment.get("branch_target_site_frontier", []):
            key = _site_key(site)
            counts[key] = counts.get(key, 0) + int(site["count"])
            sites.setdefault(key, {
                "owner": site["owner"],
                "target_address": site["target_address"],
                "target_owner": site["target_owner"],
            })
            examples = call_site_examples.setdefault(key, [])
            for example in site.get("call_site_examples", []):
                if len(examples) >= 8:
                    break
                examples.append(example)
    return [
        {
            **sites[key],
            "count": count,
            "call_site_examples": call_site_examples[key],
        }
        for key, count in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0][0], item[0][1]),
        )
    ]


def _am_frontier(raw_gate: dict, am: dict) -> list[dict]:
    mixed = raw_gate["mixed_boundary_function_class_counts"]
    rows = []
    for key, report in mixed.items():
        rows.append({
            "scope": "apollo_main",
            "kind": "am_mixed_boundary_class",
            "class": key,
            "blocking_bytes": report["bytes"],
            "function_count": report["functions"],
        })
    rows.sort(key=lambda row: (-row["blocking_bytes"], row["class"]))
    audits = [
        {
            "scope": "apollo_main",
            "kind": "am_boundary_audit",
            "class": "pc_boundary",
            "blocking_bytes": am["pc_boundary"]["blocker_bytes"],
            "blocker_count": am["pc_boundary"]["blocker_count"],
        },
        {
            "scope": "apollo_main",
            "kind": "am_boundary_audit",
            "class": "vector_it",
            "blocking_bytes": am["vector_it"]["blocker_bytes"],
            "blocker_count": am["vector_it"]["blocker_count"],
        },
        {
            "scope": "apollo_main",
            "kind": "am_boundary_audit",
            "class": "linear_raw",
            "blocking_bytes": am["linear_raw"]["byte_count"],
            "function_count": am["linear_raw"]["function_count"],
        },
        {
            "scope": "apollo_main",
            "kind": "am_boundary_audit",
            "class": "branch_targets",
            "blocking_bytes": am["branch_targets"]["byte_count"],
            "function_count": am["branch_targets"]["function_count"],
            "site_count": am["branch_targets"]["site_count"],
        },
    ]
    focused_source = raw_gate[
        "focused_raw_helper_subrange"]["top_source_function_frontier"]
    largest_source = raw_gate["largest_source_function_frontier"]
    focused_functions = []
    pc_by_function = {
        row["function"]: row for row in am["pc_boundary"]["blockers"]
    }
    vector_it_by_function = {
        row["function"]: row for row in am["vector_it"]["blockers"]
    }
    apollo_main_regions = _apollo_main_region_index()
    for row in focused_source["blocked_functions"][:5]:
        pc = pc_by_function.get(row["function"])
        vector_it = vector_it_by_function.get(row["function"])
        branch_target_owner_counts = (
            {} if pc is None else _owner_counts_for_segments(
                pc["largest_return_terminated_segments"])
        )
        focused_functions.append({
            **row,
            "pc_reference_count": 0 if pc is None else pc["pc_reference_count"],
            "pc_reference_relation_counts": (
                {} if pc is None else pc["pc_reference_relation_counts"]
            ),
            "return_terminated_segment_count": (
                0 if pc is None else pc["return_terminated_segment_count"]
            ),
            "unresolved_source_field_path_counts": (
                {} if pc is None else pc[
                    "unresolved_source_field_path_counts"]
            ),
            "largest_return_terminated_segments": (
                [] if pc is None else pc["largest_return_terminated_segments"]
            ),
            "branch_target_owner_counts": branch_target_owner_counts,
            "branch_target_owner_frontier": _ranked_owner_frontier(
                branch_target_owner_counts,
                apollo_main_regions,
            ),
            "branch_target_site_frontier": (
                [] if pc is None else _ranked_branch_target_sites(
                    pc["largest_return_terminated_segments"])
            ),
            "pc_reference_examples": [] if pc is None else pc["pc_references"][:4],
            "it_offsets": [] if vector_it is None else vector_it["it_offsets"],
            "vector_examples": [] if vector_it is None else vector_it[
                "vector_examples"],
        })
    unresolved_source_field_path_counts: dict[str, int] = {}
    branch_target_owner_counts: dict[str, int] = {}
    branch_target_sites: dict[tuple[str, int], dict[str, object]] = {}
    branch_target_site_counts: dict[tuple[str, int], int] = {}
    branch_target_call_site_examples: dict[tuple[str, int], list[dict[str, object]]] = {}
    for row in focused_functions:
        for path, count in row["unresolved_source_field_path_counts"].items():
            unresolved_source_field_path_counts[path] = (
                unresolved_source_field_path_counts.get(path, 0) + count
            )
        for owner, count in row["branch_target_owner_counts"].items():
            branch_target_owner_counts[owner] = (
                branch_target_owner_counts.get(owner, 0) + count
            )
        for site in row["branch_target_site_frontier"]:
            key = _site_key(site)
            branch_target_sites.setdefault(key, {
                "owner": site["owner"],
                "target_address": site["target_address"],
                "target_owner": site["target_owner"],
            })
            branch_target_site_counts[key] = (
                branch_target_site_counts.get(key, 0) + int(site["count"])
            )
            examples = branch_target_call_site_examples.setdefault(key, [])
            for example in site.get("call_site_examples", []):
                if len(examples) >= 8:
                    break
                examples.append(example)
    return {
        "top_mixed_boundary_classes": rows[:10],
        "audited_boundary_surfaces": sorted(
            audits,
            key=lambda row: (-row["blocking_bytes"], row["class"]),
        ),
        "largest_raw_source_function_frontier": {
            **{
                key: largest_source[key]
                for key in (
                    "number",
                    "source",
                    "inst_directive_bytes",
                    "blocked_function_count",
                    "blocked_function_bytes",
                    "reasons",
                )
            },
            "blocked_functions": largest_source["blocked_functions"],
            "largest_function_shape": largest_source[
                "largest_function_shape"],
            "next_blocked_function_shape": largest_source[
                "next_blocked_function_shape"],
            "third_blocked_function_shape": largest_source[
                "third_blocked_function_shape"],
            "fourth_blocked_function_shape": largest_source[
                "fourth_blocked_function_shape"],
            "fifth_blocked_function_shape": largest_source[
                "fifth_blocked_function_shape"],
            "sixth_blocked_function_shape": largest_source[
                "sixth_blocked_function_shape"],
            "seventh_blocked_function_shape": largest_source[
                "seventh_blocked_function_shape"],
            "eighth_blocked_function_shape": largest_source[
                "eighth_blocked_function_shape"],
            "ninth_blocked_function_shape": largest_source[
                "ninth_blocked_function_shape"],
            "tenth_blocked_function_shape": largest_source[
                "tenth_blocked_function_shape"],
            "eleventh_blocked_function_shape": largest_source[
                "eleventh_blocked_function_shape"],
            "twelfth_blocked_function_shape": largest_source[
                "twelfth_blocked_function_shape"],
            "thirteenth_blocked_function_shape": largest_source[
                "thirteenth_blocked_function_shape"],
            "fourteenth_blocked_function_shape": largest_source[
                "fourteenth_blocked_function_shape"],
            "fifteenth_blocked_function_shape": largest_source[
                "fifteenth_blocked_function_shape"],
            "sixteenth_blocked_function_shape": largest_source[
                "sixteenth_blocked_function_shape"],
            "seventeenth_blocked_function_shape": largest_source[
                "seventeenth_blocked_function_shape"],
            "eighteenth_blocked_function_shape": largest_source[
                "eighteenth_blocked_function_shape"],
            "nineteenth_blocked_function_shape": largest_source[
                "nineteenth_blocked_function_shape"],
            "twentieth_blocked_function_shape": largest_source[
                "twentieth_blocked_function_shape"],
            "twenty_first_blocked_function_shape": largest_source[
                "twenty_first_blocked_function_shape"],
            "twenty_second_blocked_function_shape": largest_source[
                "twenty_second_blocked_function_shape"],
            "twenty_third_blocked_function_shape": largest_source[
                "twenty_third_blocked_function_shape"],
            "twenty_fourth_blocked_function_shape": largest_source[
                "twenty_fourth_blocked_function_shape"],
            "twenty_fifth_blocked_function_shape": largest_source[
                "twenty_fifth_blocked_function_shape"],
            "twenty_sixth_blocked_function_shape": largest_source[
                "twenty_sixth_blocked_function_shape"],
            "twenty_seventh_blocked_function_shape": largest_source[
                "twenty_seventh_blocked_function_shape"],
        },
        "focused_source_function_frontier": {
            **{
                key: focused_source[key]
                for key in (
                    "number",
                    "source",
                    "inst_directive_bytes",
                    "blocked_function_count",
                    "blocked_function_bytes",
                )
            },
            "unresolved_source_field_path_counts": dict(
                sorted(unresolved_source_field_path_counts.items())),
            "branch_target_owner_counts": dict(
                sorted(branch_target_owner_counts.items())),
            "branch_target_owner_frontier": _ranked_owner_frontier(
                branch_target_owner_counts,
                apollo_main_regions,
            ),
            "branch_target_site_frontier": [
                {
                    **branch_target_sites[key],
                    "count": count,
                    "call_site_examples": branch_target_call_site_examples[key],
                }
                for key, count in sorted(
                    branch_target_site_counts.items(),
                    key=lambda item: (-item[1], item[0][0], item[0][1]),
                )
            ],
            "blocked_functions": focused_functions,
        },
    }


def _retained_hot_target_frontier() -> dict[str, object]:
    if not RETAINED_HOT_TARGETS.exists():
        return {
            "available": False,
            "manifest": str(RETAINED_HOT_TARGETS.relative_to(ROOT)),
            "reason": "run tools/analyze_g2_apollo_retained_hot_targets.py",
        }
    report = json.loads(RETAINED_HOT_TARGETS.read_text())
    rollup = report.get("source_pull_through_recovery_rollup") or {}
    return {
        "available": True,
        "manifest": str(RETAINED_HOT_TARGETS.relative_to(ROOT)),
        "source": report["source"],
        "hot_target_count": report["hot_target_count"],
        "target_shape_counts": report.get("target_shape_counts", {}),
        "direct_subroutine_frontier": report.get(
            "direct_subroutine_frontier", [])[:5],
        "source_pull_through_queue": report.get(
            "source_pull_through_queue", [])[:7],
        "source_pull_through_clusters": report.get(
            "source_pull_through_clusters", [])[:6],
        "source_pull_through_recovery_rollup": rollup,
        "semantic_status": {
            "contract_complete": rollup.get(
                "semantic_model_contract_complete", False),
            "contract_count": rollup.get("semantic_model_contract_count", 0),
            "contract_kind_counts": rollup.get(
                "semantic_model_kind_counts", {}),
            "firmware_routing_status_counts": rollup.get(
                "semantic_model_firmware_routing_status_counts", {}),
        },
        "top_targets": [
            {
                "count": row["count"],
                "target_address": row["target_address"],
                "region": row["region"],
                "offset_in_region": row["offset_in_region"],
                "target_shape": row.get("target_shape", "unknown"),
                "first_instruction": (
                    None if not row["instructions"] else
                    row["instructions"][0]["instruction"]
                ),
                "call_site_examples": row["call_site_examples"][:3],
            }
            for row in report["hot_targets"][:5]
        ],
    }


def _pullthrough_receipt_frontier(path: Path, command: str) -> dict[str, object]:
    if not path.exists():
        return {
            "available": False,
            "manifest": str(path.relative_to(ROOT)),
            "reason": f"run {command}",
        }
    receipt = json.loads(path.read_text())
    return {
        "available": True,
        "manifest": str(path.relative_to(ROOT)),
        "source": receipt["source"],
        "candidate_addresses": receipt["candidate_addresses"],
        "target_compile_verified": receipt["target_compile_verified"],
        "toolchain_profile": receipt["toolchain_profile"],
        "object_sha256": receipt["object_sha256"],
        "symbol_count": receipt["symbol_count"],
        "undefined_symbol_count": len(receipt["undefined_symbols"]),
        "relocation_count": receipt["relocation_count"],
        "relocation_summary": receipt["relocation_summary"],
        "firmware_routing_status": receipt["firmware_routing_status"],
    }


def _next_pull_through_frontier(
    source: dict,
    components: dict,
    ownership: dict,
    raw_gate: dict,
    am: dict,
) -> dict:
    return {
        "release_authorized": source["ready"],
        "macos_build_proven_elsewhere": True,
        "primary_global_gate": {
            "kind": "source_ownership_quality",
            "blocking": not ownership["source_ownership_suitable"],
            "raw_transcript_source_count": raw_gate["raw_transcript_source_count"],
            "raw_transcript_bytes": raw_gate["raw_transcript_bytes"],
            "source_path_sha256": raw_gate["source_path_sha256"],
            "exit_criteria": source["global_exit_criteria"][
                "source_ownership_quality"],
        },
        "component_priority": _component_frontier(
            components,
            source["components"],
        ),
        "apollo_main_priority": _am_frontier(raw_gate, am),
        "apollo_am115_pullthrough_candidate_frontier": (
            _pullthrough_receipt_frontier(
                AM115_PULLTHROUGH,
                "tools/verify_g2_apollo_am115_pullthrough_candidate.py",
            )),
        "apollo_am145_pullthrough_candidate_frontier": (
            _pullthrough_receipt_frontier(
                AM145_PULLTHROUGH,
                "tools/verify_g2_apollo_am145_pullthrough_candidate.py",
            )),
        "apollo_retained_hot_target_frontier": _retained_hot_target_frontier(),
    }


def _frontier_coverage(frontier: dict) -> dict:
    rows = {}
    for row in frontier["component_priority"]:
        scope = row["scope"]
        if scope == "apollo_main":
            rows[scope] = {
                "coverage": "am_boundary_audits_and_raw_transcript_gate",
                "frontier_fields": [
                    "component_priority.source_build_route",
                    "apollo_main_priority",
                    "apollo_main_priority.focused_source_function_frontier",
                    "apollo_retained_hot_target_frontier",
                    "primary_global_gate",
                ],
                "explicit": True,
            }
        elif scope == "codec":
            rows[scope] = {
                "coverage": "typed_external_span_map",
                "frontier_fields": [
                    "external_provider_bytes_by_class",
                    "typed_external_span_count",
                    "source_only_macos_route",
                ],
                "explicit": True,
            }
        elif scope == "ble_em9305":
            rows[scope] = {
                "coverage": "residual_readiness_and_largest_span",
                "frontier_fields": [
                    "residual_readiness",
                    "largest_residual_blocker",
                    "source_build_route",
                ],
                "explicit": True,
            }
        elif scope == "apollo_bootloader":
            rows[scope] = {
                "coverage": "retained_official_interval_frontier",
                "frontier_fields": [
                    "retained_official_bytes_by_family",
                    "largest_retained_interval",
                    "source_build_route",
                ],
                "explicit": True,
            }
        elif scope == "case":
            rows[scope] = {
                "coverage": "physical_bucket_and_board_route_frontier",
                "frontier_fields": [
                    "whole_blob_bucket_bytes",
                    "candidate_admission_blocker_class",
                    "gap_classification_counts",
                    "source_only_macos_route",
                ],
                "explicit": True,
            }
        elif scope == "touch":
            rows[scope] = {
                "coverage": "physical_bucket_and_resident_abi_frontier",
                "frontier_fields": [
                    "whole_blob_bucket_bytes",
                    "typed_physical_bucket_bytes",
                    "candidate_admission_blocker_class",
                    "resident_abi_available",
                    "source_only_macos_route",
                ],
                "explicit": True,
            }
        else:
            rows[scope] = {
                "coverage": "missing",
                "frontier_fields": [],
                "explicit": False,
            }
    missing = sorted(
        name for name, row in rows.items()
        if not row["explicit"]
    )
    return {
        "all_release_blocking_components_have_frontier": not missing,
        "missing_frontier_components": missing,
        "components": dict(sorted(rows.items())),
    }


def analyze() -> dict:
    source = source_only.analyze()
    components = {
        "apollo_main": apollo_main.analyze(),
        "apollo_bootloader": bootloader.analyze(),
        "ble_em9305": em9305.analyze(),
        "case": case.analyze(),
        "codec": codec.analyze(),
        "touch": touch.analyze(),
    }
    ownership = ownership_quality.analyze()
    raw_gate = gate_raw.analyze()
    untracked = untracked_inputs.analyze()
    am = {
        "linear_raw": am_linear_raw.analyze(),
        "branch_targets": am_branch_targets.analyze(),
        "pc_boundary": am_pc_boundary.analyze(),
        "pc_relative_only": am_pc_relative.analyze(),
        "system_decode_only": am_system_decode.analyze(),
        "vector_it": am_vector_it.analyze(),
    }

    component_blocking = {
        name: row["release_blocking_bytes"]
        for name, row in components.items()
    }
    if component_blocking != {
        name: row["release_blocking_bytes"]
        for name, row in source["components"].items()
    }:
        raise RuntimeError("component blocker reports disagree with source-only report")
    if ownership["untracked_overlay_source_input_path_sha256"] != untracked["path_set_sha256"]:
        raise RuntimeError("untracked overlay input digest disagrees")
    if ownership["untracked_overlay_source_input_count"] != untracked["input_count"]:
        raise RuntimeError("untracked overlay input counts disagree")
    if ownership["public_unrouted_raw_instruction_source_path_sha256"] != raw_gate["source_path_sha256"]:
        raise RuntimeError("gate raw transcript source digest disagrees")
    if ownership["public_unrouted_raw_instruction_source_bytes"] != raw_gate["raw_transcript_bytes"]:
        raise RuntimeError("gate raw transcript byte total disagrees")

    frontier = _next_pull_through_frontier(
        source,
        components,
        ownership,
        raw_gate,
        am,
    )
    coverage = _frontier_coverage(frontier)
    if not coverage["all_release_blocking_components_have_frontier"]:
        raise RuntimeError("release-blocking component frontier coverage is incomplete")

    return {
        "schema_version": 1,
        "source_only_ready": source["ready"],
        "release_blocking_bytes": source["release_blocking_bytes"],
        "global_blockers": source["global_blockers"],
        "remediation_queue": source["remediation_queue"],
        "component_blockers": {
            name: {
                "release_blocking_bytes": components[name]["release_blocking_bytes"],
                "production_routed": components[name]["production_routed"],
                "source_complete": components[name].get(
                    "source_complete",
                    components[name]["release_blocking_bytes"] == 0,
                ),
                "buckets": components[name]["buckets"],
            }
            for name in sorted(components)
        },
        "source_ownership_quality": {
            "source_ownership_suitable": ownership["source_ownership_suitable"],
            "gate_blocking_metrics": ownership["gate_blocking_metrics"],
            "context_metrics": ownership["context_metrics"],
            "raw_transcript_frontier": ownership["raw_transcript_frontier"],
            "retained_hot_target_recovery_frontier": ownership.get(
                "retained_hot_target_recovery_frontier", {
                    "available": False,
                    "contracts": [],
                    "rollup": None,
                }),
            "public_unrouted_raw_instruction_source_count": ownership[
                "public_unrouted_raw_instruction_source_count"],
            "public_unrouted_raw_instruction_source_bytes": ownership[
                "public_unrouted_raw_instruction_source_bytes"],
            "public_unrouted_raw_instruction_source_path_sha256": ownership[
                "public_unrouted_raw_instruction_source_path_sha256"],
            "untracked_overlay_source_input_count": ownership[
                "untracked_overlay_source_input_count"],
            "untracked_overlay_source_input_path_sha256": ownership[
                "untracked_overlay_source_input_path_sha256"],
        },
        "gate_raw_transcript_blockers": {
            "raw_transcript_source_count": raw_gate["raw_transcript_source_count"],
            "raw_transcript_bytes": raw_gate["raw_transcript_bytes"],
            "source_path_sha256": raw_gate["source_path_sha256"],
            "am_helper_ranges": raw_gate["am_helper_ranges"],
            "mixed_boundary_reason_counts": raw_gate[
                "mixed_boundary_reason_counts"],
        },
        "untracked_overlay_inputs": {
            "input_count": untracked["input_count"],
            "total_source_bytes": untracked["total_source_bytes"],
            "total_inst_directive_bytes": untracked["total_inst_directive_bytes"],
            "raw_bearing_input_count": untracked["raw_bearing_input_count"],
            "non_raw_input_count": untracked["non_raw_input_count"],
            "raw_bearing_am_helper_ranges": untracked[
                "raw_bearing_am_helper_ranges"],
            "non_raw_am_helper_ranges": untracked["non_raw_am_helper_ranges"],
            "family_counts": untracked["family_counts"],
            "am_helper_range": untracked["am_helper_range"],
            "path_set_sha256": untracked["path_set_sha256"],
            "largest_raw_bearing_inputs": untracked["largest_inputs"][:12],
        },
        "next_pull_through_frontier": frontier,
        "frontier_coverage": coverage,
        "am_blocker_audits": {
            "linear_raw": {
                "function_count": am["linear_raw"]["function_count"],
                "byte_count": am["linear_raw"]["byte_count"],
                "blocker_class_count": len(am["linear_raw"]["blocker_class_counts"]),
            },
            "branch_targets": {
                "function_count": am["branch_targets"]["function_count"],
                "byte_count": am["branch_targets"]["byte_count"],
                "site_count": am["branch_targets"]["site_count"],
                "relation_counts": am["branch_targets"]["relation_counts"],
            },
            "pc_boundary": {
                "blocker_count": am["pc_boundary"]["blocker_count"],
                "blocker_bytes": am["pc_boundary"]["blocker_bytes"],
                "pc_reference_count": am["pc_boundary"]["pc_reference_count"],
                "relation_counts": am["pc_boundary"]["relation_counts"],
            },
            "pc_relative_only": {
                "blocker_count": am["pc_relative_only"]["blocker_count"],
                "blocker_bytes": am["pc_relative_only"]["blocker_bytes"],
                "outside_body_reference_count": am["pc_relative_only"][
                    "outside_body_reference_count"],
            },
            "system_decode_only": {
                "blocker_count": am["system_decode_only"]["blocker_count"],
                "blocker_bytes": am["system_decode_only"]["blocker_bytes"],
                "system_instruction_count": am["system_decode_only"][
                    "system_instruction_count"],
                "zero_halfword_count": am["system_decode_only"][
                    "zero_halfword_count"],
            },
            "vector_it": {
                "blocker_count": am["vector_it"]["blocker_count"],
                "blocker_bytes": am["vector_it"]["blocker_bytes"],
                "it_blocker_count": am["vector_it"]["it_blocker_count"],
                "vector_blocker_count": am["vector_it"]["vector_blocker_count"],
            },
        },
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "source_only_ready": report["source_only_ready"],
        "release_blocking_bytes": report["release_blocking_bytes"],
        "global_blockers": report["global_blockers"],
        "component_blockers": {
            name: row["release_blocking_bytes"]
            for name, row in report["component_blockers"].items()
        },
        "am_linear_raw_bytes": report["am_blocker_audits"]["linear_raw"][
            "byte_count"],
        "untracked_overlay_inputs": report["untracked_overlay_inputs"][
            "input_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
