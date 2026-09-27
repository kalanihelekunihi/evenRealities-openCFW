#!/usr/bin/env python3
"""Persist the source-only release blockers from completion readiness."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_completion_readiness as readiness


OUT = ROOT / "tools/manifests/g2-source-only-blockers.json"


def analyze() -> dict:
    report = readiness.analyze()
    components = {}
    for name, row in sorted(report["components"].items()):
        blocking = row["release_blocking_bytes"]
        if blocking == 0 and row["production_routed"]:
            continue
        components[name] = {
            "release_blocking_bytes": blocking,
            "production_routed": row["production_routed"],
            "source_complete": row["source_complete"],
            "classification_complete": row["classification_complete"],
            "buckets": row["buckets"],
            "blocker_class": _blocker_class(name, row),
            "exit_criteria": _exit_criteria(name, row),
        }
    global_exit = {
        "source_ownership_quality": [
            "Replace public raw instruction transcript sources with source-owned code models or remove them from production routing.",
            "Reduce public_unrouted_raw_instruction_transcript_files and public_unrouted_raw_instruction_transcript_bytes to zero.",
            "Drive source_owned_bytes_currently_overstated back to zero while preserving macOS apple-clang source-only verification.",
        ],
    }
    remediation_queue = _remediation_queue(
        components,
        report["source_only"]["global_blockers"],
        global_exit,
    )
    return {
        "schema_version": 1,
        "ready": report["source_only"]["ready"],
        "global_blockers": report["source_only"]["global_blockers"],
        "component_count": len(report["components"]),
        "blocking_component_count": len(components),
        "release_blocking_bytes": report["aggregate"]["release_blocking_bytes"],
        "global_exit_criteria": global_exit,
        "remediation_queue": remediation_queue,
        "components": components,
    }


def _remediation_queue(
    components: dict,
    global_blockers: list[str],
    global_exit: dict[str, list[str]],
) -> list[dict]:
    rows = []
    for blocker in global_blockers:
        rows.append({
            "scope": blocker,
            "kind": "global_gate",
            "priority": 0,
            "blocking_bytes": None,
            "exit_criteria": global_exit[blocker],
        })
    for index, (name, row) in enumerate(sorted(
        components.items(),
        key=lambda item: (-item[1]["release_blocking_bytes"], item[0]),
    ), start=1):
        rows.append({
            "scope": name,
            "kind": "component_release_blocker",
            "priority": index,
            "blocking_bytes": row["release_blocking_bytes"],
            "blocker_class": row["blocker_class"],
            "production_routed": row["production_routed"],
            "exit_criteria": row["exit_criteria"],
        })
    return rows


def _blocker_class(name: str, row: dict) -> str:
    details = row["details"]
    if not row["production_routed"]:
        return details.get("candidate_admission_blocker_class", "not-production-routed")
    if name == "codec":
        return "external-provider-unavailable"
    if name == "ble_em9305":
        return "typed-retained-or-external-controller-code"
    if name.startswith("apollo_"):
        return "typed-retained-or-external-apollo-bytes"
    return "release-blocking-retained-or-external-bytes"


def _exit_criteria(name: str, row: dict) -> list[str]:
    details = row["details"]
    if name == "apollo_main":
        return [
            "Replace or source-model all retained Apollo-main raw/mixed boundary code currently covered by AM helper transcript sources.",
            "Resolve PC-relative/PC operand, nonlinear literal/data island, vector, IT-block, branch-target, and linear raw instruction text blockers without raw instruction transcript production routing.",
            "Drive Apollo-main release_blocking_bytes to zero while preserving deterministic apple-clang source-only package verification.",
        ]
    if name == "codec":
        return [
            "Provide source-owned or redistributable exact-provider implementations for all 11 GX8002 typed external spans.",
            "Resolve proprietary model data, opaque executable/runtime data, and gxNPU command stream redistribution/source authority.",
            "Production-route the codec provider without increasing unclassified bytes.",
        ]
    if name == "ble_em9305":
        return [
            "Resolve EM9305 unavailable proprietary controller code and typed unsupported external boundaries to concrete source or authorized provider payloads.",
            "Production-route any required hardware/provider boundaries such as slave connection, PAwR, and master connection spans.",
            "Preserve the authenticated residual ledger with zero unclassified bytes.",
        ]
    if name == "apollo_bootloader":
        return [
            "Replace retained official bootloader intervals with source-owned equivalents or authorized external boundaries.",
            "Prioritize EasyLogger, redirect-init, SpotMgr, platform-services, and post-redirect retained interval families.",
            "Keep bootloader production routing and source-owned in-place accounting conserved.",
        ]
    if name == "case":
        return [
            "Resolve hardware-dependent board routing for the source-built charging-case image.",
            "Production-route project source candidates and typed external/unsupported physical buckets.",
            "Prove board services, GPIO/timer routing, dual-bank updater handoff, and preserved identity copy-forward on the target contract.",
        ]
    if name == "touch":
        return [
            "Resolve the touch resident ABI and physical board-service routing.",
            "Production-route project source candidates and typed physical buckets including CapSense/CAT2 provider bytes, owner-unresolved code, literals, vectors, strings, and configuration tables.",
            "Preserve the software-complete source image and FWPK package while proving stock-byte authority or replacement mappings.",
        ]
    if not row["production_routed"]:
        return [
            f"Production-route {name} source candidates.",
            "Resolve every typed retained or external boundary without adding unclassified bytes.",
        ]
    if details:
        return [
            f"Resolve {name} retained or external bytes to source-owned or authorized provider evidence.",
            "Drive release_blocking_bytes to zero.",
        ]
    return ["Drive release_blocking_bytes to zero."]


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "ready": report["ready"],
        "global_blockers": report["global_blockers"],
        "blocking_component_count": report["blocking_component_count"],
        "release_blocking_bytes": report["release_blocking_bytes"],
        "components": {
            name: row["release_blocking_bytes"]
            for name, row in report["components"].items()
        },
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
