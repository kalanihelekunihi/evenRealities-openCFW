#!/usr/bin/env python3
"""Compose the authenticated EM9305 residual source-readiness ledger.

The gate accounts for every residual code-or-mixed byte exactly once while
keeping QP/C recovery as a non-additive supporting source audit.  Accounting
completion is deliberately distinct from source completion: typed external
boundaries and unavailable proprietary controller code are known decisions,
not concrete firmware implementations.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import analyze_em9305_first_party_hooks_candidate as first_party
import analyze_em9305_metaware_runtime_candidate as metaware
import analyze_em9305_master_connection_boundary as master_connection
import analyze_em9305_pawr_boundary as pawr
import analyze_em9305_qpc as qpc
import analyze_em9305_qpc_hook_provider_candidate as qpc_hook_provider
import analyze_em9305_slave_connection_boundary as slave_connection
import analyze_em9305_unclassified_tail_candidate as tail


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = ROOT / "tools/manifests/em9305-residual-provenance-map.tsv"
PROVENANCE_SIZE = 47_936
PROVENANCE_SHA256 = "2ac24d2abf1f4a4fbce236a82f4591a38dfdb0a71c5ca5b2f8e88bcd9a722d36"

RESIDUAL_SPANS = 175
RESIDUAL_BYTES = 33_658
CAT_CONTROLLER = "proprietary_modern_controller_source_unavailable"
CAT_METAWARE = "toolchain_or_linker_generated"
CAT_FIRST_PARTY = "first_party_application_retained"
CAT_TAIL = "unclassified_insufficient_evidence"
EXPECTED_SOURCE_CATEGORY_COUNTS = {
    CAT_CONTROLLER: 130,
    CAT_METAWARE: 2,
    CAT_FIRST_PARTY: 7,
    CAT_TAIL: 36,
}
EXPECTED_SOURCE_CATEGORY_BYTES = {
    CAT_CONTROLLER: 30_564,
    CAT_METAWARE: 980,
    CAT_FIRST_PARTY: 1_224,
    CAT_TAIL: 890,
}

READY_CONCRETE = "concrete_source_available"
READY_EXTERNAL = "typed_unsupported_external_boundary"
READY_UNAVAILABLE = "unavailable_proprietary_controller_code"
READINESS_STATES = (READY_CONCRETE, READY_EXTERNAL, READY_UNAVAILABLE)
EXPECTED_READINESS_COUNTS = {
    READY_CONCRETE: 23,
    READY_EXTERNAL: 25,
    READY_UNAVAILABLE: 127,
}
EXPECTED_READINESS_BYTES = {
    READY_CONCRETE: 1_240,
    READY_EXTERNAL: 8_348,
    READY_UNAVAILABLE: 24_070,
}


class ReadinessError(RuntimeError):
    """Raised when an input audit or exhaustive byte accounting drifts."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_residual_rows(path: Path = PROVENANCE) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if (len(raw), sha256(raw)) != (PROVENANCE_SIZE, PROVENANCE_SHA256):
        raise ReadinessError("residual provenance identity drift")
    rows: list[dict[str, Any]] = []
    for item in csv.DictReader(raw.decode("ascii").splitlines(), delimiter="\t"):
        row = dict(item)
        row["start"] = int(item["start"], 16)
        row["end"] = int(item["end"], 16)
        row["size"] = int(item["size"])
        if row["end"] - row["start"] != row["size"]:
            raise ReadinessError(f"invalid residual interval at 0x{row['start']:08x}")
        rows.append(row)
    rows.sort(key=lambda row: row["start"])
    if len(rows) != RESIDUAL_SPANS or sum(row["size"] for row in rows) != RESIDUAL_BYTES:
        raise ReadinessError("residual provenance census drift")
    for previous, current in zip(rows, rows[1:]):
        if previous["end"] > current["start"]:
            raise ReadinessError("residual provenance intervals overlap")
    counts = Counter(row["ownership_category"] for row in rows)
    byte_counts: Counter[str] = Counter()
    for row in rows:
        byte_counts[row["ownership_category"]] += row["size"]
    if dict(counts) != EXPECTED_SOURCE_CATEGORY_COUNTS:
        raise ReadinessError(f"residual source-category count drift: {dict(counts)}")
    if dict(byte_counts) != EXPECTED_SOURCE_CATEGORY_BYTES:
        raise ReadinessError(f"residual source-category byte drift: {dict(byte_counts)}")
    return rows


def _overlay_records(
    report: dict[str, Any],
    container: tuple[str, ...],
    readiness: str,
    origin: str,
) -> dict[int, dict[str, Any]]:
    value: Any = report
    for key in container:
        value = value[key]
    result = {}
    for key, item in value.items():
        start = int(key, 16)
        result[start] = {
            "start": start,
            "end": item["end_exclusive"],
            "size": item["bytes"],
            "sha256": item["sha256"],
            "readiness": readiness,
            "decision_origin": origin,
            "decision": item.get("decision", item.get("source_model", origin)),
        }
    return result


def compose_reports(
    rows: list[dict[str, Any]],
    metaware_report: dict[str, Any],
    first_party_report: dict[str, Any],
    tail_report: dict[str, Any],
    hook_provider_report: dict[str, Any],
    slave_connection_report: dict[str, Any],
    pawr_report: dict[str, Any],
    master_connection_report: dict[str, Any],
    qpc_report: dict[str, Any],
) -> dict[str, Any]:
    if metaware_report.get("status") != "candidate-qualified":
        raise ReadinessError("MetaWare source candidate is not qualified")
    if first_party_report.get("status") != "candidate-qualified-fail-closed":
        raise ReadinessError("first-party hook boundary is not qualified")
    if tail_report.get("status") != "candidate-qualified-exhaustive":
        raise ReadinessError("residual-tail partition is not qualified")
    if hook_provider_report.get("status") != "candidate-qualified-named-fail-closed":
        raise ReadinessError("QP/C named hook-provider boundary is not qualified")
    if slave_connection_report.get("status") != "candidate-qualified-fail-closed":
        raise ReadinessError("slave-connection boundary is not qualified")
    if pawr_report.get("status") != "candidate-qualified-fail-closed":
        raise ReadinessError("PAwR boundary is not qualified")
    if master_connection_report.get("status") != "candidate-qualified-fail-closed":
        raise ReadinessError("master-connection boundary is not qualified")
    if not qpc_report.get("recovery", {}).get("cluster_partition_complete"):
        raise ReadinessError("QP/C cluster partition is incomplete")
    if len(qpc_report.get("hooks", {}).get("pointer_table", {}).get("entries", [])) != 9:
        raise ReadinessError("QP/C hook table audit is incomplete")

    meta_overlay = _overlay_records(
        metaware_report, ("stock_runtime", "islands"), READY_CONCRETE,
        "metaware_runtime_candidate",
    )
    first_overlay = _overlay_records(
        first_party_report, ("stock_first_party", "spans"), READY_EXTERNAL,
        "first_party_fail_closed_boundary",
    )
    named_hook_decisions = {
        int(key, 16): item
        for key, item in hook_provider_report.get("decisions", {}).items()
    }
    expected_named_starts = {0x00311150, 0x00311620}
    if set(named_hook_decisions) != expected_named_starts:
        raise ReadinessError("named QP/C hook-provider decision-set drift")
    for start, item in named_hook_decisions.items():
        current = first_overlay.get(start)
        if current is None or (
            current["end"] != item["end_exclusive"] or
            current["size"] != item["bytes"] or
            current["sha256"] != item["sha256"] or
            item["readiness"] != READY_EXTERNAL
        ):
            raise ReadinessError(
                f"named QP/C hook-provider identity mismatch at 0x{start:08x}"
            )
        current["decision_origin"] = "qpc_named_hook_provider_boundary"
        current["decision"] = item["decision"]
    tail_decisions = tail_report["tail"]["decisions"]
    tail_concrete = {
        key: item for key, item in tail_decisions.items()
        if item["decision"].startswith("reconstructible_")
    }
    tail_external = {
        key: item for key, item in tail_decisions.items()
        if item["decision"] == "external_provider"
    }
    tail_concrete_overlay = _overlay_records(
        {"items": tail_concrete}, ("items",), READY_CONCRETE,
        "tail_reconstructible_candidate",
    )
    tail_external_overlay = _overlay_records(
        {"items": tail_external}, ("items",), READY_EXTERNAL,
        "tail_unsupported_external_boundary",
    )
    slave_item = slave_connection_report.get("decision", {})
    slave_start = slave_item.get("start")
    if slave_start != 0x00329888:
        raise ReadinessError("slave-connection boundary start drift")
    slave_overlay = {
        slave_start: {
            "start": slave_start,
            "end": slave_item.get("end_exclusive"),
            "size": slave_item.get("bytes"),
            "sha256": slave_item.get("sha256"),
            "readiness": slave_item.get("readiness"),
            "decision_origin": "slave_connection_fail_closed_boundary",
            "decision": slave_item.get("decision"),
        }
    }
    if slave_overlay[slave_start]["readiness"] != READY_EXTERNAL:
        raise ReadinessError("slave-connection boundary readiness drift")
    pawr_item = pawr_report.get("decision", {})
    pawr_start = pawr_item.get("start")
    if pawr_start != 0x00321C30:
        raise ReadinessError("PAwR boundary start drift")
    pawr_overlay = {
        pawr_start: {
            "start": pawr_start, "end": pawr_item.get("end_exclusive"),
            "size": pawr_item.get("bytes"), "sha256": pawr_item.get("sha256"),
            "readiness": pawr_item.get("readiness"),
            "decision_origin": "pawr_fail_closed_boundary",
            "decision": pawr_item.get("decision"),
        }
    }
    if pawr_overlay[pawr_start]["readiness"] != READY_EXTERNAL:
        raise ReadinessError("PAwR boundary readiness drift")
    master_item = master_connection_report.get("decision", {})
    master_start = master_item.get("start")
    if master_start != 0x0031DFD0:
        raise ReadinessError("master-connection boundary start drift")
    master_overlay = {master_start: {
        "start": master_start, "end": master_item.get("end_exclusive"),
        "size": master_item.get("bytes"), "sha256": master_item.get("sha256"),
        "readiness": master_item.get("readiness"),
        "decision_origin": "master_connection_fail_closed_boundary",
        "decision": master_item.get("decision"),
    }}
    if master_overlay[master_start]["readiness"] != READY_EXTERNAL:
        raise ReadinessError("master-connection boundary readiness drift")

    decisions: dict[int, dict[str, Any]] = {}
    expected_overlays = {
        CAT_METAWARE: meta_overlay,
        CAT_FIRST_PARTY: first_overlay,
        CAT_TAIL: {**tail_concrete_overlay, **tail_external_overlay},
    }
    for row in rows:
        category = row["ownership_category"]
        if category == CAT_CONTROLLER:
            decision = slave_overlay.get(
                row["start"], pawr_overlay.get(row["start"], master_overlay.get(row["start"]))
            )
            if decision is None:
                decision = {
                    "start": row["start"], "end": row["end"],
                    "size": row["size"], "sha256": row["sha256"],
                    "readiness": READY_UNAVAILABLE,
                    "decision_origin": "authenticated_residual_provenance",
                    "decision": row["family_hint"],
                }
            elif (
                decision["end"] != row["end"] or
                decision["size"] != row["size"] or
                decision["sha256"] != row["sha256"]
            ):
                raise ReadinessError("controller typed-boundary identity mismatch")
        else:
            decision = expected_overlays[category].get(row["start"])
            if decision is None:
                raise ReadinessError(
                    f"no readiness overlay for residual 0x{row['start']:08x}"
                )
            if (
                decision["end"] != row["end"] or
                decision["size"] != row["size"] or
                decision["sha256"] != row["sha256"]
            ):
                raise ReadinessError(
                    f"readiness overlay identity mismatch at 0x{row['start']:08x}"
                )
        if row["start"] in decisions:
            raise ReadinessError(f"duplicate readiness decision at 0x{row['start']:08x}")
        decisions[row["start"]] = decision

    expected_starts = {row["start"] for row in rows}
    overlay_starts = set(meta_overlay) | set(first_overlay) | set(tail_concrete_overlay) | set(tail_external_overlay)
    noncontroller_starts = {
        row["start"] for row in rows if row["ownership_category"] != CAT_CONTROLLER
    }
    if overlay_starts != noncontroller_starts:
        missing = sorted(noncontroller_starts - overlay_starts)
        extra = sorted(overlay_starts - noncontroller_starts)
        raise ReadinessError(f"overlay closure drift: missing={missing!r}, extra={extra!r}")
    if set(decisions) != expected_starts:
        raise ReadinessError("readiness ledger does not cover the residual census")

    readiness_counts = Counter(item["readiness"] for item in decisions.values())
    readiness_bytes: Counter[str] = Counter()
    for item in decisions.values():
        readiness_bytes[item["readiness"]] += item["size"]
    if dict(readiness_counts) != EXPECTED_READINESS_COUNTS:
        raise ReadinessError(f"readiness count drift: {dict(readiness_counts)}")
    if dict(readiness_bytes) != EXPECTED_READINESS_BYTES:
        raise ReadinessError(f"readiness byte drift: {dict(readiness_bytes)}")

    accounted_bytes = sum(item["size"] for item in decisions.values())
    unclassified_starts = expected_starts - set(decisions)
    accounting_complete = (
        len(decisions) == RESIDUAL_SPANS and
        accounted_bytes == RESIDUAL_BYTES and
        not unclassified_starts
    )
    if not accounting_complete:
        raise ReadinessError("zero-unclassified claim requires complete byte accounting")

    qpc_upstream = qpc_report["upstream"]
    qpc_recovery = qpc_report["recovery"]
    return {
        "status": "accounting-complete-source-incomplete",
        "read_only": True,
        "hardware_operations": False,
        "accounting_scope": "stock_retained_unresolved_code_or_mixed",
        "residual": {
            "span_count": RESIDUAL_SPANS,
            "bytes": RESIDUAL_BYTES,
            "accounted_spans": len(decisions),
            "accounted_bytes": accounted_bytes,
            "unclassified_spans_after_decision": len(unclassified_starts),
            "unclassified_bytes_after_decision": 0,
            "accounting_complete": accounting_complete,
            "source_complete": readiness_bytes[READY_CONCRETE] == RESIDUAL_BYTES,
            "readiness_segment_counts": dict(readiness_counts),
            "readiness_bytes": dict(readiness_bytes),
            "ledger": [decisions[start] for start in sorted(decisions)],
        },
        "qpc_supporting_audit": {
            "additive_to_residual_accounting": False,
            "selected_release_tag": qpc_upstream["selected_release_tag"],
            "portable_function_count": qpc_recovery["portable_function_count"],
            "portable_function_bytes": qpc_recovery["portable_function_bytes"],
            "cluster_partition_complete": qpc_recovery["cluster_partition_complete"],
            "hook_pointer_count": len(qpc_report["hooks"]["pointer_table"]["entries"]),
            "exact_vendor_checkout_proven": qpc_upstream["exact_vendor_checkout_proven"],
        },
        "qpc_hook_provider_audit": {
            "additive_to_residual_accounting": False,
            "status": hook_provider_report["status"],
            "named_providers": sorted(hook_provider_report["providers"]),
            "unresolved_providers": hook_provider_report["unresolved_providers"],
            "exact_provider_source_available": False,
            "redistribution_authority_resolved": False,
            "candidate_production_routed": hook_provider_report["candidate"]["production_routed"],
            "hardware_validation": hook_provider_report["hardware_validation"],
        },
        "slave_connection_boundary_audit": {
            "additive_to_residual_accounting": False,
            "status": slave_connection_report["status"],
            "span_count": 1,
            "bytes": slave_item["bytes"],
            "function_count": slave_connection_report["function_count"],
            "exact_source_available": slave_connection_report["exact_source_available"],
            "redistribution_authority_resolved": slave_connection_report["redistribution_authority_resolved"],
            "candidate_production_routed": slave_connection_report["candidate"]["production_routed"],
            "hardware_validation": slave_connection_report["hardware_validation"],
        },
        "pawr_boundary_audit": {
            "additive_to_residual_accounting": False,
            "status": pawr_report["status"], "span_count": 1,
            "bytes": pawr_item["bytes"], "function_count": pawr_report["function_count"],
            "exact_source_available": pawr_report["exact_source_available"],
            "redistribution_authority_resolved": pawr_report["redistribution_authority_resolved"],
            "candidate_production_routed": pawr_report["candidate"]["production_routed"],
            "hardware_validation": pawr_report["hardware_validation"],
        },
        "master_connection_boundary_audit": {
            "additive_to_residual_accounting": False,
            "status": master_connection_report["status"], "span_count": 1,
            "bytes": master_item["bytes"],
            "entry_count": master_connection_report["entry_count"],
            "exact_source_available": master_connection_report["exact_source_available"],
            "redistribution_authority_resolved": master_connection_report["redistribution_authority_resolved"],
            "candidate_production_routed": master_connection_report["candidate"]["production_routed"],
            "hardware_validation": master_connection_report["hardware_validation"],
        },
        "release_gate": {
            "accounting_complete": accounting_complete,
            "source_complete": False,
            "production_ready": False,
            "blocking_spans": readiness_counts[READY_EXTERNAL] + readiness_counts[READY_UNAVAILABLE],
            "blocking_bytes": readiness_bytes[READY_EXTERNAL] + readiness_bytes[READY_UNAVAILABLE],
            "reason": "typed boundaries and proprietary controller retentions are accounted but not concrete community firmware source",
        },
    }


def run_audit() -> dict[str, Any]:
    return compose_reports(
        load_residual_rows(),
        metaware.run_audit(),
        first_party.run_audit(),
        tail.run_audit(),
        qpc_hook_provider.run_audit(),
        slave_connection.run_audit(),
        pawr.run_audit(),
        master_connection.run_audit(),
        qpc.analyze(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("EM9305 source readiness: accounting-complete-source-incomplete")
        print("residual accounting: 175 spans / 33658 bytes / 0 unclassified")
        print("concrete source: 23 spans / 1240 bytes")
        print("release gate: blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
