#!/usr/bin/env python3
"""Summarize source-ownership quality blockers for source-only readiness."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_production_raw_encoding_quality as raw_quality
import analyze_g2_gate_raw_transcript_blockers as gate_raw
import analyze_g2_untracked_overlay_inputs as untracked_inputs


OUT = ROOT / "tools/manifests/g2-source-ownership-quality-blockers.json"
RETAINED_HOT_TARGETS = ROOT / "tools/manifests/g2-apollo-retained-hot-targets.json"


def _list_digest(values: list[str]) -> str:
    return hashlib.sha256(json.dumps(
        values, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()


def _retained_hot_target_recovery_frontier() -> dict[str, object]:
    if not RETAINED_HOT_TARGETS.exists():
        return {
            "available": False,
            "manifest": str(RETAINED_HOT_TARGETS.relative_to(ROOT)),
            "contracts": [],
            "rollup": None,
        }
    report = json.loads(RETAINED_HOT_TARGETS.read_text())
    contracts = []
    for cluster in report.get("source_pull_through_clusters", [])[:6]:
        contracts.append({
            "priority": cluster["priority"],
            "region": cluster["region"],
            "dependency_class": cluster["dependency_class"],
            "start_address": cluster["start_address"],
            "end_address": cluster["end_address"],
            "byte_length": cluster["byte_length"],
            "instruction_count": cluster.get("instruction_count"),
            "source_recovery_status": cluster.get(
                "source_recovery_status"),
            "arithmetic_motif": cluster.get("arithmetic_motif"),
        })
    return {
        "available": True,
        "manifest": str(RETAINED_HOT_TARGETS.relative_to(ROOT)),
        "contracts": contracts,
        "rollup": report.get("source_pull_through_recovery_rollup"),
    }


def analyze() -> dict:
    result = raw_quality.analyze()
    raw_gate = gate_raw.analyze()
    untracked_report = untracked_inputs.analyze()
    sources = result["public_unrouted_raw_instruction_sources"]
    untracked = result["untracked_overlay_source_inputs"]
    raw_bytes = sum(row["inst_directive_bytes"] for row in sources)
    if raw_bytes != raw_gate["raw_transcript_bytes"]:
        raise RuntimeError("raw transcript bytes disagree with gate raw report")
    if len(sources) != raw_gate["raw_transcript_source_count"]:
        raise RuntimeError("raw transcript source count disagrees with gate raw report")
    if untracked_report["path_set_sha256"] != _list_digest(untracked):
        raise RuntimeError("untracked input digest disagrees")
    return {
        "schema_version": 1,
        "source_ownership_suitable": result["source_ownership_suitable"],
        "quality_gate": result["quality_gate"],
        "classification_complete": result["classification_complete"],
        "metrics": result["metrics"],
        "gate_blocking_metrics": {
            "source_owned_bytes_currently_overstated": result["metrics"][
                "source_owned_bytes_currently_overstated"],
            "public_raw_executable_transcript_files": result["metrics"][
                "public_raw_executable_transcript_files"],
            "public_unrouted_raw_instruction_transcript_files": result[
                "metrics"]["public_unrouted_raw_instruction_transcript_files"],
            "public_unrouted_raw_instruction_transcript_bytes": result[
                "metrics"]["public_unrouted_raw_instruction_transcript_bytes"],
            "public_unrouted_raw_instruction_overlay_referenced_files": result[
                "metrics"][
                    "public_unrouted_raw_instruction_overlay_referenced_files"],
            "public_unrouted_raw_instruction_overlay_referenced_bytes": result[
                "metrics"][
                    "public_unrouted_raw_instruction_overlay_referenced_bytes"],
            "public_unrouted_raw_instruction_unreferenced_files": result[
                "metrics"][
                    "public_unrouted_raw_instruction_unreferenced_files"],
            "public_unrouted_raw_instruction_unreferenced_bytes": result[
                "metrics"][
                    "public_unrouted_raw_instruction_unreferenced_bytes"],
            "untracked_raw_bearing_overlay_source_inputs": untracked_report[
                "raw_bearing_input_count"],
        },
        "context_metrics": {
            "untracked_overlay_source_inputs": result["metrics"][
                "untracked_overlay_source_inputs"],
            "untracked_raw_bearing_overlay_source_inputs": untracked_report[
                "raw_bearing_input_count"],
            "untracked_non_raw_overlay_source_inputs": untracked_report[
                "non_raw_input_count"],
            "removed_public_transcript_files": result["metrics"][
                "removed_public_transcript_files"],
            "removed_public_transcript_executable_bytes": result["metrics"][
                "removed_public_transcript_executable_bytes"],
        },
        "public_unrouted_raw_instruction_source_count": len(sources),
        "public_unrouted_raw_instruction_source_bytes": raw_bytes,
        "public_unrouted_raw_instruction_source_path_sha256": _list_digest(
            [row["source"] for row in sources]
        ),
        "raw_transcript_frontier": {
            "am_helper_ranges": raw_gate["am_helper_ranges"],
            "raw_helper_batch_frontier": raw_gate[
                "raw_helper_batch_frontier"],
            "top_raw_helper_batch_decomposition": raw_gate[
                "top_raw_helper_batch_decomposition"],
            "focused_raw_helper_subrange": raw_gate[
                "focused_raw_helper_subrange"],
            "largest_source_function_frontier": raw_gate[
                "largest_source_function_frontier"],
            "mixed_boundary_reason_counts": raw_gate[
                "mixed_boundary_reason_counts"],
            "raw_bearing_am_helper_ranges": untracked_report[
                "raw_bearing_am_helper_ranges"],
            "non_raw_am_helper_ranges": untracked_report[
                "non_raw_am_helper_ranges"],
            "raw_bearing_input_count": untracked_report[
                "raw_bearing_input_count"],
            "non_raw_input_count": untracked_report["non_raw_input_count"],
        },
        "retained_hot_target_recovery_frontier": (
            _retained_hot_target_recovery_frontier()),
        "largest_public_unrouted_raw_instruction_sources": sorted(
            (
                {
                    "source": row["source"],
                    "inst_directive_bytes": row["inst_directive_bytes"],
                    "overlay_referenced": row["overlay_referenced"],
                    "source_sha256": row["source_sha256"],
                }
                for row in sources
            ),
            key=lambda row: (-row["inst_directive_bytes"], row["source"]),
        )[:12],
        "removed_public_transcript_boundaries": result[
            "removed_public_transcript_boundaries"],
        "untracked_overlay_source_input_count": len(untracked),
        "untracked_overlay_source_input_path_sha256": _list_digest(untracked),
        "untracked_overlay_source_input_examples": untracked[:12],
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "source_ownership_suitable": report["source_ownership_suitable"],
        "gate_blocking_metrics": report["gate_blocking_metrics"],
        "public_unrouted_raw_instruction_source_count": report[
            "public_unrouted_raw_instruction_source_count"],
        "public_unrouted_raw_instruction_source_bytes": report[
            "public_unrouted_raw_instruction_source_bytes"],
        "untracked_overlay_source_input_count": report[
            "untracked_overlay_source_input_count"],
        "untracked_raw_bearing_overlay_source_inputs": report[
            "context_metrics"]["untracked_raw_bearing_overlay_source_inputs"],
        "untracked_non_raw_overlay_source_inputs": report[
            "context_metrics"]["untracked_non_raw_overlay_source_inputs"],
        "public_unrouted_raw_instruction_source_path_sha256": report[
            "public_unrouted_raw_instruction_source_path_sha256"],
        "untracked_overlay_source_input_path_sha256": report[
            "untracked_overlay_source_input_path_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
