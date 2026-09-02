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
import io
import json
import os
from pathlib import Path
import stat
import tempfile
from typing import Any

import analyze_em9305_first_party_hooks_candidate as first_party
import analyze_em9305_metaware_runtime_candidate as metaware
import analyze_em9305_master_connection_boundary as master_connection
import analyze_em9305_pawr_boundary as pawr
import analyze_em9305_qpc as qpc
import analyze_em9305_qpc_hook_provider_candidate as qpc_hook_provider
import analyze_em9305_record_package as record_package
import analyze_em9305_slave_connection_boundary as slave_connection
import analyze_em9305_unclassified_tail_candidate as tail


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "tools/manifests"
PROVENANCE = ROOT / "tools/manifests/em9305-residual-provenance-map.tsv"
PROVENANCE_SIZE = 47_936
PROVENANCE_SHA256 = "2ac24d2abf1f4a4fbce236a82f4591a38dfdb0a71c5ca5b2f8e88bcd9a722d36"
FINAL_LEDGER = MANIFEST_DIR / "em9305-final-source-readiness.tsv"
FINAL_SUMMARY = MANIFEST_DIR / "em9305-final-source-readiness-summary.json"
FINAL_SCHEMA_VERSION = 6
QPC_COMPONENT_RECEIPT = MANIFEST_DIR / "em9305-qpc-component-build-summary.json"
QPC_COMPONENT_RECEIPT_SIZE = 6_604
QPC_COMPONENT_RECEIPT_SHA256 = (
    "e65a1b51eea5065bff760a3e20f1cd17b2f86718da561dbfd55afac35bb17f79"
)
RECORD_PACKAGE_RECEIPT = MANIFEST_DIR / "em9305-record-package-summary.json"
RECORD_PACKAGE_RECEIPT_SIZE = 2_606
RECORD_PACKAGE_RECEIPT_SHA256 = (
    "947bd35ff79c88e3f7386a4966ab50173589223efc76f1ce1b6bbec42df03b19"
)
HARDWARE_VALIDATION = "blocked by unavailable physical evidence"

RESIDUAL_SPANS = 175
RESIDUAL_BYTES = 33_658
COMPONENT_BYTES = 212_984
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


def load_qpc_component_receipt() -> dict[str, Any]:
    raw = QPC_COMPONENT_RECEIPT.read_bytes()
    if (len(raw), sha256(raw)) != (
        QPC_COMPONENT_RECEIPT_SIZE,
        QPC_COMPONENT_RECEIPT_SHA256,
    ):
        raise ReadinessError("EM9305 QP/C target-link receipt identity drift")
    report = json.loads(raw)
    linked = report.get("linked_object", {})
    if (
        report.get("status") != "arcv2-em-qpc-component-target-linked"
        or report.get("target") != "ARCv2 EM"
        or report.get("translation_unit_count") != 10
        or report.get("qpc_translation_unit_count") != 8
        or report.get("port_translation_unit_count") != 2
        or report.get("software_link_complete") is not True
        or report.get("install_placement_resolved") is not False
        or report.get("production_routed") is not False
        or linked.get("undefined_symbols") != []
        or linked.get("forbidden_runtime_imports") != []
        or linked.get("sha256")
        != "c1aa5370945e41afcb29750174fd4531def9a887d37a0f620461eeabad587ad9"
        or report.get("hardware_operations") != []
        or report.get("hardware_validation") != HARDWARE_VALIDATION
    ):
        raise ReadinessError("EM9305 QP/C target-link receipt shape drift")
    return report


def load_record_package_receipt() -> dict[str, Any]:
    raw = RECORD_PACKAGE_RECEIPT.read_bytes()
    if (len(raw), sha256(raw)) != (
        RECORD_PACKAGE_RECEIPT_SIZE,
        RECORD_PACKAGE_RECEIPT_SHA256,
    ):
        raise ReadinessError("EM9305 record-package receipt identity drift")
    report = json.loads(raw)
    try:
        live = record_package.analyze()
    except record_package.AuditError as error:
        raise ReadinessError(
            f"EM9305 record-package live audit failed: {error}") from error
    if report != live:
        raise ReadinessError("EM9305 record-package receipt is stale")
    container = report.get("container", {})
    stock = report.get("authenticated_stock", {})
    if (
        report.get("schema_version") != 1
        or report.get("status")
        != "record-package-software-closed-source-image-incomplete"
        or stock.get("size") != 211_948
        or stock.get("sha256")
        != "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
        or container.get("metadata_bytes") != 124
        or container.get("payload_bytes") != 211_824
        or container.get("record_count") != 4
        or container.get("erase_sector_count") != 29
        or report.get("stock_roundtrip_byte_exact") is not True
        or report.get("software_wrapper_complete") is not True
        or report.get("software_package_complete") is not True
        or report.get("source_records_complete") is not False
        or report.get("source_image_complete") is not False
        or report.get("production_routed") is not False
        or not report.get("remaining_software_blockers")
        or report.get("hardware_operations") != []
        or report.get("hardware_validation") != HARDWARE_VALIDATION
    ):
        raise ReadinessError("EM9305 record-package receipt shape drift")
    return report


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
    if metaware_report.get("status") != "production-routed":
        raise ReadinessError("EM9305 source route is not qualified")
    if first_party_report.get("status") != "candidate-qualified-fail-closed":
        raise ReadinessError("first-party hook boundary is not qualified")
    if tail_report.get("status") != "candidate-qualified-exhaustive":
        raise ReadinessError("residual-tail partition is not qualified")
    if hook_provider_report.get("status") != "candidate-qualified-one-software-two-hardware":
        raise ReadinessError("QP/C named hook-provider boundary is not qualified")
    if (
        hook_provider_report.get("software_provider_gaps") != []
        or hook_provider_report.get("hardware_dependent_providers")
        != ["PalUartResume", "VoltMon_DoMeasurement"]
        or not hook_provider_report.get("providers", {})
        .get("wsfOsRunIdleTasks", {})
        .get("clean_room_source_available")
    ):
        raise ReadinessError("QP/C WSF software-provider closure drift")
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
        "metaware_runtime_production_route",
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
        "tail_reconstructible_production_route",
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

    metaware_candidate = metaware_report["candidate"]
    completion_buckets = {
        "production_source": metaware_candidate["production_source_bytes"],
        "generated_or_reconstructible": metaware_candidate[
            "generated_or_reconstructible_bytes"],
        "candidate_source_not_routed": metaware_candidate[
            "candidate_source_not_routed_bytes"],
        "typed_retained_or_external": 210_584,
        "unclassified": 0,
    }
    if (sum(completion_buckets.values()) != COMPONENT_BYTES or
            completion_buckets["production_source"] != 1_174 or
            completion_buckets["generated_or_reconstructible"] != 1_226 or
            completion_buckets["candidate_source_not_routed"] != 0 or
            completion_buckets["typed_retained_or_external"] != 210_584):
        raise ReadinessError("EM9305 completion-bucket mapping changed")

    qpc_upstream = qpc_report["upstream"]
    qpc_recovery = qpc_report["recovery"]
    qpc_component_receipt = load_qpc_component_receipt()
    record_package_receipt = load_record_package_receipt()
    qpc_linked = qpc_component_receipt["linked_object"]
    return {
        "status": "accounting-complete-source-incomplete",
        "read_only": True,
        "hardware_validation": HARDWARE_VALIDATION,
        "hardware_operations": [],
        "source_complete": False,
        "release": False,
        "accounting_scope": "stock_retained_unresolved_code_or_mixed",
        "completion_bucket_mapping": {
            "component_bytes": COMPONENT_BYTES,
            "buckets": completion_buckets,
            "candidate_production_routed": True,
            "release_blocking_bytes": 210_584,
            "qualification": (
                "all 1,240 reviewed concrete-source stock spans are production "
                "routed; 210,584 provider bytes remain a typed retained/external "
                "boundary and keep whole-component source closure false"
            ),
        },
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
            "arcv2_em_target_linked": qpc_component_receipt["software_link_complete"],
            "arcv2_em_translation_units": qpc_component_receipt["translation_unit_count"],
            "arcv2_em_undefined_symbols": qpc_linked["undefined_symbols"],
            "arcv2_em_forbidden_runtime_imports": qpc_linked["forbidden_runtime_imports"],
            "arcv2_em_linked_object_sha256": qpc_linked["sha256"],
            "arcv2_em_build_receipt": (
                "tools/manifests/em9305-qpc-component-build-summary.json"
            ),
            "install_placement_resolved": qpc_component_receipt["install_placement_resolved"],
            "production_routed": qpc_component_receipt["production_routed"],
            "required_hardware_providers": qpc_component_receipt["required_hardware_providers"],
            "hardware_validation": qpc_component_receipt["hardware_validation"],
        },
        "deployment_package_audit": {
            "additive_to_residual_accounting": False,
            "status": "mixed-provider-production-routed-source-incomplete",
            "build_receipt": metaware_candidate["production_build_receipt"],
            "authenticated_stock_size": record_package_receipt[
                "authenticated_stock"]["size"],
            "authenticated_stock_sha256": record_package_receipt[
                "authenticated_stock"]["sha256"],
            "record_count": record_package_receipt["container"]["record_count"],
            "erase_sector_count": record_package_receipt[
                "container"]["erase_sector_count"],
            "stock_roundtrip_byte_exact": record_package_receipt[
                "stock_roundtrip_byte_exact"],
            "software_wrapper_complete": record_package_receipt[
                "software_wrapper_complete"],
            "software_package_complete": record_package_receipt[
                "software_package_complete"],
            "source_records_complete": record_package_receipt[
                "source_records_complete"],
            "source_image_complete": False,
            "production_routed": True,
            "provider_size": metaware_candidate["provider_size"],
            "provider_sha256": metaware_candidate["provider_sha256"],
            "remaining_software_blockers": [
                "210584 typed retained or external provider bytes are not yet reproducible from community C source"
            ],
            "hardware_operations": record_package_receipt["hardware_operations"],
            "hardware_validation": record_package_receipt["hardware_validation"],
        },
        "metaware_runtime_audit": {
            "additive_to_residual_accounting": False,
            "status": metaware_report["status"],
            "candidate_source_bytes": metaware_report["stock_runtime"]["total_bytes"],
            "arcv2_em_target_compiled": metaware_candidate["arcv2_em_target_compiled"],
            "arcv2_em_undefined_symbols": metaware_candidate["arcv2_em_undefined_symbols"],
            "arcv2_em_forbidden_runtime_imports": metaware_candidate["arcv2_em_forbidden_runtime_imports"],
            "arcv2_em_build_receipt": metaware_candidate["arcv2_em_build_receipt"],
            "candidate_production_routed": metaware_candidate["production_routed"],
            "remaining_software_blockers": metaware_report["integration_blockers"],
            "hardware_validation": HARDWARE_VALIDATION,
        },
        "qpc_hook_provider_audit": {
            "additive_to_residual_accounting": False,
            "status": hook_provider_report["status"],
            "named_providers": sorted(hook_provider_report["providers"]),
            "unresolved_providers": hook_provider_report["unresolved_providers"],
            "software_provider_gaps": hook_provider_report["software_provider_gaps"],
            "software_provider_source_available": True,
            "wsf_idle_semantics": hook_provider_report["wsf_idle_semantics"],
            "hardware_dependent_providers": hook_provider_report["hardware_dependent_providers"],
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


def _require_manifest_shape(result: dict[str, Any]) -> list[dict[str, Any]]:
    residual = result.get("residual", {})
    ledger = residual.get("ledger")
    if not isinstance(ledger, list) or len(ledger) != RESIDUAL_SPANS:
        raise ReadinessError("final readiness ledger span count drift")
    if (
        residual.get("span_count") != RESIDUAL_SPANS
        or residual.get("bytes") != RESIDUAL_BYTES
        or residual.get("accounted_spans") != RESIDUAL_SPANS
        or residual.get("accounted_bytes") != RESIDUAL_BYTES
        or residual.get("unclassified_spans_after_decision") != 0
        or residual.get("unclassified_bytes_after_decision") != 0
        or residual.get("accounting_complete") is not True
        or residual.get("source_complete") is not False
        or residual.get("readiness_segment_counts")
        != EXPECTED_READINESS_COUNTS
        or residual.get("readiness_bytes") != EXPECTED_READINESS_BYTES
    ):
        raise ReadinessError("final readiness summary conservation drift")
    if (
        result.get("source_complete") is not False
        or result.get("release") is not False
        or result.get("hardware_validation") != HARDWARE_VALIDATION
        or result.get("hardware_operations") != []
    ):
        raise ReadinessError("final readiness policy shape drift")
    qpc_audit = result.get("qpc_supporting_audit", {})
    if (
        qpc_audit.get("additive_to_residual_accounting") is not False
        or qpc_audit.get("arcv2_em_target_linked") is not True
        or qpc_audit.get("arcv2_em_translation_units") != 10
        or qpc_audit.get("arcv2_em_undefined_symbols") != []
        or qpc_audit.get("arcv2_em_forbidden_runtime_imports") != []
        or qpc_audit.get("arcv2_em_linked_object_sha256")
        != "c1aa5370945e41afcb29750174fd4531def9a887d37a0f620461eeabad587ad9"
        or qpc_audit.get("arcv2_em_build_receipt")
        != "tools/manifests/em9305-qpc-component-build-summary.json"
        or qpc_audit.get("install_placement_resolved") is not False
        or qpc_audit.get("production_routed") is not False
        or qpc_audit.get("hardware_validation") != HARDWARE_VALIDATION
    ):
        raise ReadinessError("QP/C ARCv2 EM target-link evidence drift")
    deployment_audit = result.get("deployment_package_audit", {})
    if (
        deployment_audit.get("additive_to_residual_accounting") is not False
        or deployment_audit.get("status")
        != "mixed-provider-production-routed-source-incomplete"
        or deployment_audit.get("build_receipt")
        != "components/em9305/source_overlay/build/build-report.json"
        or deployment_audit.get("authenticated_stock_size") != 211_948
        or deployment_audit.get("authenticated_stock_sha256")
        != "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
        or deployment_audit.get("record_count") != 4
        or deployment_audit.get("erase_sector_count") != 29
        or deployment_audit.get("stock_roundtrip_byte_exact") is not True
        or deployment_audit.get("software_wrapper_complete") is not True
        or deployment_audit.get("software_package_complete") is not True
        or deployment_audit.get("source_records_complete") is not False
        or deployment_audit.get("source_image_complete") is not False
        or deployment_audit.get("production_routed") is not True
        or deployment_audit.get("provider_size") != COMPONENT_BYTES
        or deployment_audit.get("provider_sha256")
        != "1a4ccc61cae6e9b90d0eb3d694179d726c935171788167d28ea45060d7431c42"
        or not deployment_audit.get("remaining_software_blockers")
        or deployment_audit.get("hardware_operations") != []
        or deployment_audit.get("hardware_validation") != HARDWARE_VALIDATION
    ):
        raise ReadinessError("EM9305 deployment-package evidence drift")
    metaware_audit = result.get("metaware_runtime_audit", {})
    if (
        metaware_audit.get("additive_to_residual_accounting") is not False
        or metaware_audit.get("status") != "production-routed"
        or metaware_audit.get("candidate_source_bytes") != 980
        or metaware_audit.get("arcv2_em_target_compiled") is not True
        or metaware_audit.get("arcv2_em_undefined_symbols") != []
        or metaware_audit.get("arcv2_em_forbidden_runtime_imports") != []
        or metaware_audit.get("arcv2_em_build_receipt")
        != "tools/manifests/em9305-arc-candidate-build-summary.json"
        or metaware_audit.get("candidate_production_routed") is not True
        or metaware_audit.get("remaining_software_blockers") != []
        or metaware_audit.get("hardware_validation") != HARDWARE_VALIDATION
    ):
        raise ReadinessError("MetaWare ARCv2 EM readiness evidence drift")
    qpc_hook_audit = result.get("qpc_hook_provider_audit", {})
    if (
        qpc_hook_audit.get("additive_to_residual_accounting") is not False
        or qpc_hook_audit.get("status")
        != "candidate-qualified-one-software-two-hardware"
        or qpc_hook_audit.get("software_provider_gaps") != []
        or qpc_hook_audit.get("software_provider_source_available") is not True
        or qpc_hook_audit.get("hardware_dependent_providers")
        != ["PalUartResume", "VoltMon_DoMeasurement"]
        or qpc_hook_audit.get("wsf_idle_semantics", {}).get("callback_capacity") != 3
        or qpc_hook_audit.get("wsf_idle_semantics", {}).get("production_routed") is not False
        or qpc_hook_audit.get("candidate_production_routed") is not False
        or qpc_hook_audit.get("hardware_validation") != HARDWARE_VALIDATION
    ):
        raise ReadinessError("QP/C WSF provider readiness evidence drift")

    required = {
        "start", "end", "size", "sha256", "readiness", "decision",
        "decision_origin",
    }
    previous_end: int | None = None
    total = 0
    for index, row in enumerate(ledger):
        if set(row) != required:
            raise ReadinessError(
                f"final readiness ledger field drift at row {index}"
            )
        start, end, size = row["start"], row["end"], row["size"]
        if (
            not isinstance(start, int)
            or not isinstance(end, int)
            or not isinstance(size, int)
            or end - start != size
            or size <= 0
            or (previous_end is not None and previous_end > start)
        ):
            raise ReadinessError(
                f"final readiness ledger interval drift at row {index}"
            )
        if (
            not isinstance(row["sha256"], str)
            or len(row["sha256"]) != 64
            or any(character not in "0123456789abcdef"
                   for character in row["sha256"])
            or row["readiness"] not in READINESS_STATES
        ):
            raise ReadinessError(
                f"final readiness ledger identity drift at row {index}"
            )
        for field in ("decision", "decision_origin"):
            value = row[field]
            if (
                not isinstance(value, str)
                or not value
                or any(character in value for character in "\t\r\n")
            ):
                raise ReadinessError(
                    f"final readiness ledger {field} drift at row {index}"
                )
        total += size
        previous_end = end
    if total != RESIDUAL_BYTES:
        raise ReadinessError("final readiness ledger byte conservation drift")
    return ledger


def _manifest_payloads(result: dict[str, Any]) -> dict[Path, bytes]:
    ledger = _require_manifest_shape(result)
    fields = (
        "start", "end", "size", "sha256", "readiness", "decision",
        "decision_origin",
    )
    handle = io.StringIO(newline="")
    writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    writer.writerow(["# SPDX-License-Identifier: MIT"])
    writer.writerow(fields)
    for row in ledger:
        writer.writerow([
            f"0x{row['start']:08x}",
            f"0x{row['end']:08x}",
            row["size"],
            row["sha256"],
            row["readiness"],
            row["decision"],
            row["decision_origin"],
        ])
    ledger_payload = handle.getvalue().encode("utf-8")

    residual = result["residual"]
    completion = result["completion_bucket_mapping"]
    summary = {
        "schema_version": FINAL_SCHEMA_VERSION,
        "status": result["status"],
        "component_bytes": completion["component_bytes"],
        "residual_span_count": residual["span_count"],
        "residual_bytes": residual["bytes"],
        "readiness_segment_counts": residual["readiness_segment_counts"],
        "readiness_bytes": residual["readiness_bytes"],
        "unclassified_spans": residual["unclassified_spans_after_decision"],
        "unclassified_bytes": residual["unclassified_bytes_after_decision"],
        "completion_buckets": completion["buckets"],
        "candidate_production_routed": completion["candidate_production_routed"],
        "release_blocking_bytes": completion["release_blocking_bytes"],
        "source_complete": result["source_complete"],
        "release": result["release"],
        "hardware_validation": result["hardware_validation"],
        "hardware_operations": result["hardware_operations"],
        "metaware_runtime_audit": result["metaware_runtime_audit"],
        "qpc_supporting_audit": result["qpc_supporting_audit"],
        "qpc_hook_provider_audit": result["qpc_hook_provider_audit"],
        "deployment_package_audit": result["deployment_package_audit"],
        "ledger": {
            "path": FINAL_LEDGER.name,
            "size": len(ledger_payload),
            "sha256": sha256(ledger_payload),
        },
    }
    summary_payload = (
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return {FINAL_LEDGER: ledger_payload, FINAL_SUMMARY: summary_payload}


def _read_checked_regular(path: Path) -> bytes:
    try:
        descriptor = os.open(
            path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        )
    except OSError as error:
        raise ReadinessError(f"checked manifest is missing or unsafe: {path.name}") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ReadinessError(
                f"checked manifest is not an independent regular file: {path.name}"
            )
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            payload = handle.read()
        after = os.fstat(descriptor)
        before_identity = (
            before.st_dev, before.st_ino, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns,
        )
        after_identity = (
            after.st_dev, after.st_ino, after.st_size,
            after.st_mtime_ns, after.st_ctime_ns,
        )
        if len(payload) != before.st_size or before_identity != after_identity:
            raise ReadinessError(f"checked manifest changed during read: {path.name}")
        return payload
    finally:
        os.close(descriptor)


def check_manifests(result: dict[str, Any]) -> list[Path]:
    payloads = _manifest_payloads(result)
    for path, expected in payloads.items():
        if _read_checked_regular(path) != expected:
            raise ReadinessError(f"checked EM9305 manifest is stale: {path.name}")
    return list(payloads)


def write_manifests(result: dict[str, Any]) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    payloads = _manifest_payloads(result)
    with tempfile.TemporaryDirectory(
        prefix="em9305-final-readiness-", dir=MANIFEST_DIR
    ) as raw_staging:
        staging = Path(raw_staging)
        staged: list[tuple[Path, Path]] = []
        for path, payload in payloads.items():
            candidate = staging / path.name
            with candidate.open("xb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            if _read_checked_regular(candidate) != payload:
                raise ReadinessError(f"staged EM9305 manifest changed: {path.name}")
            staged.append((candidate, path))
        for candidate, path in staged:
            candidate.replace(path)
    check_manifests(result)
    return list(payloads)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--write-manifests", action="store_true")
    actions.add_argument("--check-manifests", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_audit()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    elif args.check_manifests:
        for path in check_manifests(result):
            print(f"checked {path.relative_to(ROOT)}")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("EM9305 source readiness: accounting-complete-source-incomplete")
        print("residual accounting: 175 spans / 33658 bytes / 0 unclassified")
        print("concrete source: 23 spans / 1240 bytes")
        print("release gate: blocked")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReadinessError as error:
        raise SystemExit(f"EM9305 source readiness failed: {error}") from error
