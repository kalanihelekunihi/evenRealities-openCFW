#!/usr/bin/env python3
"""Compose the byte-level and release-gate readiness of every G2 payload.

This audit is deliberately software-only.  It distinguishes production source,
generated/reconstructible bytes, typed retained or external boundaries, source
candidates that are not production-routed, and genuinely unclassified bytes.
An explicit retained boundary closes byte-accounting opacity; it does not make
that byte open source or grant permission to redistribute it.
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import struct
from typing import Any

import analyze_em9305_source_readiness as em9305_readiness
import analyze_gx8002_source_readiness as gx8002_readiness
import analyze_g2_production_raw_encoding_quality as raw_encoding_quality
import analyze_g2_project_license_normalization as project_license_policy
import audit_g2_release_licensing as licensing


ROOT = Path(__file__).resolve().parents[1]
BASE_MANIFEST = ROOT / "manifests/g2-2.2.6.10.json"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAIN_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
BOOT_REPORT = ROOT / "components/bootloader/core_overlay/build/build-report.json"
APOLLO_ORIGIN = ROOT / "tools/manifests/g2-apollo-origin-accounting.json"
TOUCH_SUMMARY = ROOT / "tools/manifests/g2-touch-software-readiness-summary.json"
TOUCH_CURRENT = ROOT / "tools/manifests/g2-touch-current-source-readiness-summary.json"
TOUCH_FINAL = ROOT / "tools/manifests/g2-touch-final-classification-summary.json"
TOUCH_CANDIDATE_PROVENANCE = (
    ROOT / "tools/manifests/g2-touch-final-source-candidate-provenance.tsv"
)
TOUCH_FINAL_FRONTIER = ROOT / "tools/manifests/g2-touch-final-frontier.tsv"
TOUCH_FINAL_PHYSICAL_BUCKETS = (
    ROOT / "tools/manifests/g2-touch-final-physical-byte-buckets.tsv"
)
TOUCH_SOURCE_IMAGE = ROOT / "tools/manifests/g2-touch-source-image-summary.json"
CASE_SOURCE_IMAGE = ROOT / "tools/manifests/g2-case-source-image-summary.json"
NEMAVG_STROKE_CAPS = (
    ROOT / "tools/manifests/g2-nemavg-stroke-caps-candidate-summary.json"
)
CLKMGR_DIVIDERS = (
    ROOT / "tools/manifests/g2-clkmgr-divider-candidate-summary.json"
)
PT_SOURCE = ROOT / "tools/manifests/g2-pt-protocol-source-summary.json"
CASE_SUMMARY = ROOT / "tools/manifests/g2-box-function-map-summary.json"
CASE_REGISTER_ADMISSION = (
    ROOT / "tools/manifests/g2-case-register-primitives-admission-summary.json"
)
CASE_REGISTER_TRANSFORMS = (
    ROOT / "tools/manifests/g2-case-register-transforms-admission-summary.json"
)
CASE_SEMANTIC_LEAVES = (
    ROOT / "tools/manifests/g2-case-semantic-leaves-admission-summary.json"
)
CASE_PURE_HELPERS = (
    ROOT / "tools/manifests/g2-case-pure-helpers-admission-summary.json"
)
CASE_REGISTER_POLICIES = (
    ROOT / "tools/manifests/g2-case-register-policies-admission-summary.json"
)
CASE_FINAL = ROOT / "tools/manifests/g2-case-final-classification-summary.json"
RAW_ENCODING_SUMMARY = (
    ROOT / "tools/manifests/g2-production-raw-encoding-quality-summary.json"
)
PROJECT_LICENSE_CENSUS = (
    ROOT / "tools/manifests/g2-project-license-normalization.tsv"
)
PROJECT_LICENSE_SUMMARY = (
    ROOT / "tools/manifests/g2-project-license-normalization-summary.json"
)
PROJECT_LICENSE_SCOPE_PATHS = (
    ROOT / "tools/manifests/g2-project-mit-normalization-scope-paths.txt"
)
PROJECT_LICENSE_ADDITIONAL_PATHS = (
    ROOT /
    "tools/manifests/g2-project-mit-normalization-research-and-wrapper.txt"
)
EM9305_FINAL_LEDGER = (
    ROOT / "tools/manifests/em9305-final-source-readiness.tsv"
)
EM9305_FINAL_SUMMARY = (
    ROOT / "tools/manifests/em9305-final-source-readiness-summary.json"
)
EM9305_FINAL_LEDGER_SHA256 = (
    "cfda63c68a73d27235af204f01ee6c848db9495d0294d55faf70096b7ab08bf9"
)
EM9305_FINAL_SUMMARY_SHA256 = (
    "5cd0e51ef3274fe1e96d8c3e4aa0ff776fef4587305112f05573b5cde0d194fd"
)
HARDWARE_VALIDATION = "blocked by unavailable physical evidence"
TOUCH_CANDIDATE_BYTES = 14_510
TOUCH_CANDIDATE_PROVENANCE_FIELDS = (
    "category", "bytes", "address_set_sha256", "content_sha256",
    "entry_count", "entry_set_sha256", "admission_manifests",
    "source_routes", "source_route_license", "claimed_route_licenses",
    "translation_unit_present_in_nonproduction_source_image",
    "adapter_translation_unit_present_in_nonproduction_source_image",
    "semantic_stock_address_candidate_only",
    "admitted_body_linked_to_stock_address", "production_elf_ownership",
    "stock_byte_license_authority", "eula_vendor_source_included",
    "excluded_source_boundaries", "evidence",
)
TOUCH_CANDIDATE_BOOL_FIELDS = frozenset({
    "translation_unit_present_in_nonproduction_source_image",
    "adapter_translation_unit_present_in_nonproduction_source_image",
    "semantic_stock_address_candidate_only",
    "admitted_body_linked_to_stock_address",
    "production_elf_ownership",
    "eula_vendor_source_included",
})
TOUCH_CANDIDATE_ROUTE_ORDER = (
    "project_mit_nonproduction_source_image_tu_semantic_route",
    "project_mit_or_gpl_nonproduction_source_image_tu_semantic_route",
    "project_mit_emeeprom_clean_room_nonproduction_source_image_tu_semantic_route",
    "apache_critical_adapter_nonproduction_source_image_tu_semantic_route",
    "apache_cat2_upstream_body_identified_not_linked",
    "overlap_or_source_output_identity_unresolved",
)
TOUCH_CANDIDATE_ROUTE_LICENSES = frozenset({
    "MIT", "MIT OR GPL-3.0-only", "Apache-2.0", "NOASSERTION",
})
TOUCH_CANDIDATE_OVERLAP_CATEGORY = (
    "overlap_or_source_output_identity_unresolved"
)
TOUCH_CANDIDATE_TU_EXPECTED = {
    TOUCH_CANDIDATE_ROUTE_ORDER[0]: True,
    TOUCH_CANDIDATE_ROUTE_ORDER[1]: True,
    TOUCH_CANDIDATE_ROUTE_ORDER[2]: True,
    TOUCH_CANDIDATE_ROUTE_ORDER[3]: True,
    TOUCH_CANDIDATE_ROUTE_ORDER[4]: False,
}
TOUCH_CANDIDATE_ADAPTER_TU_EXPECTED = {
    TOUCH_CANDIDATE_ROUTE_ORDER[0]: False,
    TOUCH_CANDIDATE_ROUTE_ORDER[1]: False,
    TOUCH_CANDIDATE_ROUTE_ORDER[2]: False,
    TOUCH_CANDIDATE_ROUTE_ORDER[3]: True,
}


class AuditError(RuntimeError):
    """Raised when a component ledger stops conserving bytes."""


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def _sum(mapping: dict[str, int]) -> int:
    return sum(int(value) for value in mapping.values())


def _canonical_list(value: str, label: str) -> list[str]:
    parts = value.split(";")
    _require(
        bool(parts) and all(parts) and parts == sorted(set(parts)),
        f"Touch candidate provenance {label} is not a canonical set",
    )
    return parts


def _read_stable_g2_regular(path: Path, label: str) -> bytes:
    root = ROOT.resolve()
    lexical = Path(os.path.abspath(path))
    try:
        lexical.relative_to(root)
        resolved = lexical.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError, RuntimeError) as error:
        raise AuditError(f"{label} is not contained in the G2 root: {path}") from error
    _require(resolved == lexical,
             f"{label} traverses a symlinked path: {path}")
    try:
        descriptor = os.open(
            resolved, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        )
    except OSError as error:
        raise AuditError(f"{label} could not be opened safely: {path}") from error
    try:
        before = os.fstat(descriptor)
        _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                 f"{label} is not an independent regular file: {path}")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            raw = handle.read()
        after = os.fstat(descriptor)
        identity = lambda value: (
            value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_mtime_ns, value.st_ctime_ns,
        )
        _require(len(raw) == before.st_size and
                 identity(before) == identity(after),
                 f"{label} changed during descriptor read: {path}")
        return raw
    finally:
        os.close(descriptor)


def _sha256_digest(value: Any, label: str) -> str:
    _require(isinstance(value, str) and len(value) == 64 and
             all(char in "0123456789abcdef" for char in value),
             f"{label} is not a canonical SHA-256 digest")
    return value


def _em9305_final_receipts(result: dict[str, Any]) -> dict[str, Any]:
    """Authenticate the persisted zero-unclassified EM9305 ledger."""
    try:
        checked = em9305_readiness.check_manifests(result)
    except em9305_readiness.ReadinessError as error:
        raise AuditError(f"EM9305 final readiness receipt failed: {error}") from error
    _require(
        checked == [EM9305_FINAL_LEDGER, EM9305_FINAL_SUMMARY],
        "EM9305 final readiness receipt set changed",
    )

    ledger_raw = _read_stable_g2_regular(
        EM9305_FINAL_LEDGER, "EM9305 final readiness ledger"
    )
    summary_raw = _read_stable_g2_regular(
        EM9305_FINAL_SUMMARY, "EM9305 final readiness summary"
    )
    ledger_sha256 = hashlib.sha256(ledger_raw).hexdigest()
    summary_sha256 = hashlib.sha256(summary_raw).hexdigest()
    _require(
        ledger_sha256 == EM9305_FINAL_LEDGER_SHA256,
        "EM9305 final readiness ledger identity changed",
    )
    _require(
        summary_sha256 == EM9305_FINAL_SUMMARY_SHA256,
        "EM9305 final readiness summary identity changed",
    )
    try:
        summary = json.loads(summary_raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AuditError("EM9305 final readiness summary is not canonical JSON") from error

    residual = result["residual"]
    completion = result["completion_bucket_mapping"]
    expected_summary = {
        "schema_version": em9305_readiness.FINAL_SCHEMA_VERSION,
        "status": result["status"],
        "component_bytes": completion["component_bytes"],
        "residual_span_count": residual["span_count"],
        "residual_bytes": residual["bytes"],
        "readiness_segment_counts": residual["readiness_segment_counts"],
        "readiness_bytes": residual["readiness_bytes"],
        "unclassified_spans": residual["unclassified_spans_after_decision"],
        "unclassified_bytes": residual["unclassified_bytes_after_decision"],
        "completion_buckets": completion["buckets"],
        "candidate_production_routed": completion[
            "candidate_production_routed"
        ],
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
            "path": EM9305_FINAL_LEDGER.name,
            "size": len(ledger_raw),
            "sha256": ledger_sha256,
        },
    }
    _require(summary == expected_summary,
             "EM9305 final readiness summary disagrees with the live audit")
    _require(
        residual["span_count"] == 175
        and residual["bytes"] == 33_658
        and residual["accounted_spans"] == 175
        and residual["accounted_bytes"] == 33_658
        and residual["unclassified_spans_after_decision"] == 0
        and residual["unclassified_bytes_after_decision"] == 0
        and result["hardware_operations"] == [],
        "EM9305 final readiness conservation or hardware policy changed",
    )
    return {
        "schema_version": summary["schema_version"],
        "manifest_count": 2,
        "residual_span_count": summary["residual_span_count"],
        "residual_bytes": summary["residual_bytes"],
        "hardware_operations": [],
        "ledger": {
            "path": EM9305_FINAL_LEDGER.name,
            "size": len(ledger_raw),
            "sha256": ledger_sha256,
        },
        "summary": {
            "path": EM9305_FINAL_SUMMARY.name,
            "size": len(summary_raw),
            "sha256": summary_sha256,
        },
    }


def _touch_candidate_provenance_rows() -> list[dict[str, Any]]:
    """Read the disjoint Touch semantic-candidate route/license partition."""
    try:
        lines = _read_stable_g2_regular(
            TOUCH_CANDIDATE_PROVENANCE, "Touch candidate provenance"
        ).decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise AuditError("Touch candidate provenance is not UTF-8") from error
    _require(
        bool(lines) and lines[0] == "# SPDX-License-Identifier: MIT",
        "Touch candidate provenance SPDX header changed",
    )
    reader = csv.DictReader(lines[1:], delimiter="\t")
    _require(
        tuple(reader.fieldnames or ()) == TOUCH_CANDIDATE_PROVENANCE_FIELDS,
        "Touch candidate provenance schema changed",
    )
    rows: list[dict[str, Any]] = []
    for raw in reader:
        _require(
            None not in raw and set(raw) == set(TOUCH_CANDIDATE_PROVENANCE_FIELDS),
            "Touch candidate provenance row shape changed",
        )
        _require(
            all(isinstance(raw[field], str) and raw[field] and
                raw[field] == raw[field].strip()
                for field in TOUCH_CANDIDATE_PROVENANCE_FIELDS),
            "Touch candidate provenance contains an empty or padded field",
        )
        row: dict[str, Any] = {}
        for field in TOUCH_CANDIDATE_PROVENANCE_FIELDS:
            value = raw[field]
            if field in ("bytes", "entry_count"):
                try:
                    number = int(value)
                except ValueError as error:
                    raise AuditError(
                        f"Touch candidate provenance {field} is not an integer"
                    ) from error
                _require(number > 0 and str(number) == value,
                         f"Touch candidate provenance {field} is not canonical")
                row[field] = number
            elif field in TOUCH_CANDIDATE_BOOL_FIELDS:
                _require(value in ("true", "false"),
                         f"Touch candidate provenance {field} is not lowercase bool")
                row[field] = value == "true"
            else:
                row[field] = value
        rows.append(row)
    _validate_touch_candidate_provenance_rows(rows)
    return rows


def _validate_touch_candidate_provenance_rows(
    rows: list[dict[str, Any]],
) -> None:
    _require(bool(rows), "Touch candidate provenance is empty")
    categories = [str(row.get("category", "")) for row in rows]
    _require(len(categories) == len(set(categories)),
             "Touch candidate provenance categories are not unique")
    _require(categories == list(TOUCH_CANDIDATE_ROUTE_ORDER),
             "Touch candidate provenance category order or membership changed")
    _require(sum(int(row.get("bytes", -1)) for row in rows) ==
             TOUCH_CANDIDATE_BYTES,
             "Touch candidate provenance rows do not conserve candidate bytes")
    for row in rows:
        category = str(row["category"])
        for field in ("address_set_sha256", "content_sha256",
                      "entry_set_sha256"):
            digest = row.get(field)
            _require(isinstance(digest, str) and len(digest) == 64 and
                     all(char in "0123456789abcdef" for char in digest),
                     f"Touch candidate provenance {field} is not SHA-256")
        _canonical_list(str(row["admission_manifests"]),
                        "admission manifests")
        _canonical_list(str(row["source_routes"]), "source routes")
        claimed = set(_canonical_list(
            str(row["claimed_route_licenses"]), "claimed route licenses"))
        route_license = str(row["source_route_license"])
        _require(route_license in TOUCH_CANDIDATE_ROUTE_LICENSES and
                 claimed <= TOUCH_CANDIDATE_ROUTE_LICENSES - {"NOASSERTION"},
                 "Touch candidate provenance route license changed")
        if category == TOUCH_CANDIDATE_OVERLAP_CATEGORY:
            _require(route_license == "NOASSERTION",
                     "Touch overlap candidate gained a source-route license")
        else:
            _require(route_license != "NOASSERTION" and
                     claimed == {route_license},
                     "Touch non-overlap candidate mixes route licenses")
        if category in TOUCH_CANDIDATE_TU_EXPECTED:
            _require(
                row.get(
                    "translation_unit_present_in_nonproduction_source_image"
                ) is TOUCH_CANDIDATE_TU_EXPECTED[category],
                "Touch candidate provenance translation-unit route changed",
            )
        if category in TOUCH_CANDIDATE_ADAPTER_TU_EXPECTED:
            _require(
                row.get(
                    "adapter_translation_unit_present_in_nonproduction_source_image"
                ) is TOUCH_CANDIDATE_ADAPTER_TU_EXPECTED[category],
                "Touch candidate provenance adapter route changed",
            )
        _require(row.get("semantic_stock_address_candidate_only") is True and
                 row.get("admitted_body_linked_to_stock_address") is False and
                 row.get("production_elf_ownership") is False,
                 "Touch semantic candidate overclaims stock-address ownership")
        _require(row.get("stock_byte_license_authority") == "NOASSERTION" and
                 row.get("eula_vendor_source_included") is False,
                 "Touch candidate provenance overclaims stock-byte authority")
        boundaries = str(row["excluded_source_boundaries"])
        if boundaries != "none":
            _canonical_list(boundaries, "excluded source boundaries")


def _touch_candidate_provenance_summary(
    current: dict[str, Any], final: dict[str, Any],
    source_image: dict[str, Any], rows: list[dict[str, Any]],
) -> dict[str, Any]:
    current_provenance = current.get("candidate_provenance")
    final_provenance = final.get("candidate_provenance")
    expected_fields = {
        "candidate_bytes", "subrow_count", "subrow_overlap_bytes",
        "overlapping_semantic_claim_bytes",
        "semantic_stock_address_candidates_only", "production_elf_ownership",
        "stock_address_to_linked_output_identity_proven",
        "stock_byte_redistribution_authority", "eula_vendor_source_included",
        "row_digest", "address_set_sha256", "content_sha256",
        "entry_claim_count", "manifest",
        "nonproduction_source_image_elf_sha256",
        "nonproduction_source_image_production_routed",
    }
    _require(isinstance(final_provenance, dict) and
             set(final_provenance) == expected_fields and
             current_provenance == final_provenance,
             "Touch current/final candidate provenance disagrees")
    canonical_digest = hashlib.sha256(json.dumps(
        rows, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    overlap_bytes = sum(
        int(row["bytes"]) for row in rows
        if row["category"] == TOUCH_CANDIDATE_OVERLAP_CATEGORY
    )
    _require(final_provenance["candidate_bytes"] == TOUCH_CANDIDATE_BYTES and
             final_provenance["subrow_count"] == len(rows) and
             final_provenance["subrow_overlap_bytes"] == 0 and
             final_provenance["overlapping_semantic_claim_bytes"] ==
             overlap_bytes and
             final_provenance["row_digest"] == canonical_digest,
             "Touch candidate provenance conservation or row digest changed")
    _require(final.get("candidate_provenance_row_count") == len(rows) and
             final.get("admission_entry_count") ==
             final_provenance["entry_claim_count"],
             "Touch final candidate provenance counts changed")
    _require(final_provenance["semantic_stock_address_candidates_only"] is True and
             final_provenance["production_elf_ownership"] is False and
             final_provenance[
                 "stock_address_to_linked_output_identity_proven"] is False and
             final_provenance["stock_byte_redistribution_authority"] ==
             "NOASSERTION" and
             final_provenance["eula_vendor_source_included"] is False,
             "Touch candidate provenance overclaims production or authority")
    _require(final_provenance["manifest"] ==
             TOUCH_CANDIDATE_PROVENANCE.name and
             final_provenance["nonproduction_source_image_production_routed"]
             is False and
             final_provenance["nonproduction_source_image_elf_sha256"] ==
             source_image.get("artifacts", {}).get("elf_sha256"),
             "Touch candidate provenance source-image binding changed")
    final_metrics = final.get("metrics", {})
    _require(final_provenance["address_set_sha256"] ==
             final_metrics.get("candidate_union_address_set_sha256") ==
             current.get("candidate_union_address_set_sha256") and
             final_provenance["content_sha256"] ==
             final_metrics.get("candidate_union_content_sha256") ==
             current.get("candidate_union_content_sha256"),
             "Touch candidate provenance union digests changed")
    return dict(final_provenance)


def _touch_generation_receipt(
    current: dict[str, Any], final: dict[str, Any],
) -> dict[str, Any]:
    receipt = final.get("generation_receipt")
    _require(isinstance(receipt, dict) and
             current.get("generation_receipt") == receipt,
             "Touch current/final generation receipts disagree")
    _require(set(receipt) == {
        "logical_manifest_count", "generation_receipt_sha256",
        "analysis_inputs", "rendered_outputs",
    }, "Touch generation receipt schema changed")
    analysis_inputs = receipt.get("analysis_inputs")
    _require(isinstance(analysis_inputs, dict) and set(analysis_inputs) == {
        "path_count", "aggregate_sha256", "path_sha256",
    }, "Touch generation receipt input schema changed")
    path_sha256 = analysis_inputs.get("path_sha256")
    _require(isinstance(path_sha256, dict) and
             analysis_inputs.get("path_count") == 69 == len(path_sha256) and
             list(path_sha256) == sorted(path_sha256),
             "Touch generation receipt path map is not canonical and complete")
    actual_path_sha256: dict[str, str] = {}
    for relative, expected_digest in path_sha256.items():
        _require(isinstance(relative, str) and relative and
                 relative == PurePosixPath(relative).as_posix() and
                 not PurePosixPath(relative).is_absolute() and
                 ".." not in PurePosixPath(relative).parts and
                 "\\" not in relative,
                 "Touch generation receipt contains a non-canonical path")
        digest = _sha256_digest(
            expected_digest, f"Touch analysis input {relative}"
        )
        actual = hashlib.sha256(_read_stable_g2_regular(
            ROOT / relative, f"Touch analysis input {relative}"
        )).hexdigest()
        _require(actual == digest,
                 f"Touch analysis input identity changed: {relative}")
        actual_path_sha256[relative] = actual
    aggregate = hashlib.sha256(json.dumps(
        actual_path_sha256, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    _require(
        _sha256_digest(
            analysis_inputs.get("aggregate_sha256"),
            "Touch analysis-input aggregate",
        ) == aggregate,
        "Touch analysis-input aggregate changed",
    )
    _require(final.get("analysis_inputs") == analysis_inputs,
             "Touch final summary lost its analysis-input receipt")

    rendered = receipt.get("rendered_outputs")
    output_paths = {
        TOUCH_FINAL_FRONTIER.name: TOUCH_FINAL_FRONTIER,
        TOUCH_FINAL_PHYSICAL_BUCKETS.name: TOUCH_FINAL_PHYSICAL_BUCKETS,
        TOUCH_CANDIDATE_PROVENANCE.name: TOUCH_CANDIDATE_PROVENANCE,
    }
    expected_output_names = {
        *output_paths,
        f"{TOUCH_FINAL.name}:core",
        f"{TOUCH_CURRENT.name}:core",
    }
    _require(isinstance(rendered, dict) and
             set(rendered) == expected_output_names and
             receipt.get("logical_manifest_count") == 5 == len(rendered),
             "Touch rendered-output receipt changed")
    actual_rendered = {
        name: hashlib.sha256(_read_stable_g2_regular(
            path, f"Touch rendered output {name}"
        )).hexdigest()
        for name, path in output_paths.items()
    }
    final_core = dict(final)
    current_core = dict(current)
    final_core.pop("generation_receipt", None)
    current_core.pop("generation_receipt", None)
    actual_rendered[f"{TOUCH_FINAL.name}:core"] = hashlib.sha256(json.dumps(
        final_core, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    actual_rendered[f"{TOUCH_CURRENT.name}:core"] = hashlib.sha256(json.dumps(
        current_core, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    for name, actual in actual_rendered.items():
        _require(_sha256_digest(
            rendered.get(name), f"Touch rendered output {name}"
        ) == actual, f"Touch rendered output identity changed: {name}")
    receipt_digest = hashlib.sha256(json.dumps({
        "analysis_inputs": analysis_inputs,
        "rendered_outputs": rendered,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    _require(_sha256_digest(
        receipt.get("generation_receipt_sha256"),
        "Touch generation receipt",
    ) == receipt_digest, "Touch generation receipt digest changed")
    return dict(receipt)


def _region_partition(regions: list[dict[str, Any]], size: int,
                      component: str) -> dict[str, Any]:
    """Derive one disjoint provider-byte partition from current manifest intervals."""
    ordered = sorted(regions, key=lambda row: int(row["file_offset"]))
    cursor = 0
    by_status: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    retained_addresses: set[int] = set()
    for row in ordered:
        offset = int(row["file_offset"])
        length = int(row["size"])
        status = row.get("address_status")
        _require(offset == cursor and length > 0,
                 f"{component} provider intervals have a gap or overlap")
        _require(isinstance(status, str) and status,
                 f"{component} provider interval lacks an address status")
        by_status[status] = by_status.get(status, 0) + length
        status_counts[status] = status_counts.get(status, 0) + 1
        if status == "official_blob":
            retained_addresses.update(range(offset, offset + length))
        cursor += length
    _require(cursor == size, f"{component} provider intervals do not reach EOF")
    retained_digest = hashlib.sha256(b"".join(
        struct.pack("<I", address) for address in sorted(retained_addresses)
    )).hexdigest()
    return {
        "component_bytes": size,
        "intervals": len(ordered),
        "bytes_by_address_status": dict(sorted(by_status.items())),
        "intervals_by_address_status": dict(sorted(status_counts.items())),
        "retained_official_bytes": len(retained_addresses),
        "retained_file_offset_set_sha256": retained_digest,
        "derivation": (
            "disjoint current core-manifest file-offset intervals; no candidate "
            "or historical-frontier bytes are added"
        ),
    }


def _touch_admission_progress() -> dict[str, int]:
    """Reconcile the contiguous Touch source-admission chain.

    The whole-image readiness ledger predates the rapid application batches.
    Each later batch records an exact input gap, admitted instruction count,
    and residual gap.  Walking that chain keeps the whole-image buckets live
    without weakening the original byte ledger or double-counting candidates.
    """
    current = _read(TOUCH_CURRENT)
    edges: dict[int, tuple[int, int, str]] = {}
    for path in sorted((ROOT / "tools/manifests").glob(
            "g2-touch-*-admission-summary.json")):
        metrics = _read(path).get("metrics", {})
        required = {
            "input_gap_instruction_bytes", "admitted_instruction_bytes",
            "residual_gap_instruction_bytes",
        }
        if not required <= set(metrics):
            continue
        before = int(metrics["input_gap_instruction_bytes"])
        admitted = int(metrics["admitted_instruction_bytes"])
        after = int(metrics["residual_gap_instruction_bytes"])
        _require(before - admitted == after,
                 f"Touch admission does not conserve bytes: {path.name}")
        _require(before not in edges,
                 f"Touch admission chain branches at {before} bytes")
        edges[before] = (after, admitted, path.name)
    _require(bool(edges), "Touch source-admission chain is empty")
    initial = max(edges)
    cursor = initial
    admitted_total = 0
    batches = 0
    while cursor in edges:
        after, admitted, _ = edges[cursor]
        _require(after < cursor, "Touch admission chain does not advance")
        admitted_total += admitted
        batches += 1
        cursor = after
    current_gap = int(current["concrete_gap_instruction_bytes"])
    _require(cursor == current_gap,
             "Touch current readiness is not the tip of its admission chain")
    _require(initial - current_gap == admitted_total,
             "Touch cumulative source admission does not conserve bytes")
    return {
        "authoritative_batch": int(current["authoritative_batch"]),
        "initial_gap_instruction_bytes": initial,
        "current_gap_instruction_bytes": current_gap,
        "cumulative_candidate_instruction_bytes": admitted_total,
        "admission_batches": batches,
        "remaining_functions": int(
            current["concrete_source_or_implementation_gap"]),
        "remaining_application_contracts": int(
            current["unimplemented_application_contracts"]),
        "unclassified_functions": int(current.get(
            "unclassified_functions",
            current["concrete_source_or_implementation_gap"])),
    }


def _component(
    *,
    size: int,
    production_source: int = 0,
    generated_or_reconstructible: int = 0,
    candidate_source: int = 0,
    typed_retained_or_external: int = 0,
    unclassified: int = 0,
    release_blocking: int,
    production_routed: bool,
    details: dict[str, Any],
) -> dict[str, Any]:
    buckets = {
        "production_source": production_source,
        "generated_or_reconstructible": generated_or_reconstructible,
        "candidate_source_not_routed": candidate_source,
        "typed_retained_or_external": typed_retained_or_external,
        "unclassified": unclassified,
    }
    _require(_sum(buckets) == size, "component byte ledger does not conserve bytes")
    _require(0 <= release_blocking <= size, "invalid release-blocking byte count")
    return {
        "size": size,
        "buckets": buckets,
        "classification_complete": unclassified == 0,
        "source_complete": release_blocking == 0,
        "release_blocking_bytes": release_blocking,
        "production_routed": production_routed,
        "hardware_validation": HARDWARE_VALIDATION,
        "hardware_blocker": HARDWARE_VALIDATION,
        "hardware_operations": [],
        "details": details,
    }


def analyze() -> dict[str, Any]:
    base = _read(BASE_MANIFEST)
    core = _read(CORE_MANIFEST)
    base_components = {row["name"]: row for row in base["components"]}
    main = _read(MAIN_REPORT)["component"]
    boot = _read(BOOT_REPORT)["component"]

    main_component_override = core["component_overrides"]["apollo_main"]
    boot_component_override = core["component_overrides"]["apollo_bootloader"]
    main_override = main_component_override["provider"]
    boot_override = boot_component_override["provider"]
    _require((main_override["size"], main_override["sha256"]) ==
             (main["size"], main["sha256"]),
             "Apollo-main build and manifest provider disagree")
    _require((boot_override["size"], boot_override["sha256"]) ==
             (boot["size"], boot["sha256"]),
             "bootloader build and manifest provider disagree")

    origin = _read(APOLLO_ORIGIN)["expected_counts"]
    origin_buckets = origin["origin_buckets"]
    _require(_sum(origin_buckets) == main["opaque_base_bytes"],
             "Apollo-main origin buckets do not cover retained bytes")
    main_generated = (main["generated_patch_site_bytes"] +
                      main.get("generated_wrapper_bytes", 0))
    _require(main["source_owned_bytes"] + main_generated +
             main["opaque_base_bytes"] == main["size"],
             "Apollo-main build accounting changed")

    boot_generated = (boot["generated_patch_site_bytes"] +
                      boot["generated_alignment_bytes"])
    _require(boot["source_owned_bytes"] + boot_generated +
             boot["opaque_base_bytes"] == boot["size"],
             "bootloader build accounting changed")
    boot_partition = _region_partition(
        boot_component_override["regions"], boot["size"], "Apollo bootloader"
    )
    boot_status = boot_partition["bytes_by_address_status"]
    _require(boot_status == {
        "generated_alignment": boot["generated_alignment_bytes"],
        "generated_source_entry_replacement":
            boot["generated_patch_site_bytes"],
        "official_blob": boot["opaque_base_bytes"],
        "source_compiled": boot["source_owned_bytes"],
    }, "bootloader current interval partition disagrees with its builder")
    _require(boot_partition["retained_official_bytes"] == 87_985,
             "bootloader retained complement changed")

    gx = gx8002_readiness.run_audit()
    gx_ready = gx["readiness"]
    _require(gx["partition"]["contiguous"] and
             gx["partition"]["gaps"] == 0 and gx["partition"]["overlaps"] == 0,
             "GX8002 partition is not exhaustive")
    gx_reconstructible = gx_ready["reconstructible_mit_format_metadata"]["bytes"]
    gx_external = gx_ready["typed_unsupported_external_boundary"]["bytes"]
    gx_unavailable = gx_ready["unavailable_proprietary_codec_firmware"]["bytes"]
    _require(gx_reconstructible + gx_external + gx_unavailable ==
             gx["partition"]["bytes"], "GX8002 readiness does not conserve bytes")
    codec_external_detail = gx.get("external_provider_detail", {})
    _require(codec_external_detail.get("bytes_by_class") == {
        "opaque_executable": 190_912,
        "opaque_runtime_data": 5_124,
        "opaque_npu_commands": 9_164,
        "proprietary_model_data": 120_800,
    } and codec_external_detail.get("bytes") == 326_000 and
        codec_external_detail.get("open_source_available") is False,
        "GX8002 external-provider detail changed")

    em = em9305_readiness.run_audit()
    em_final_receipts = _em9305_final_receipts(em)
    em_residual = em["residual"]
    _require(em_residual["accounting_complete"] and
             em_residual["unclassified_bytes_after_decision"] == 0,
             "EM9305 retained residual is not exhaustively classified")
    _require(_sum(em_residual["readiness_bytes"]) == em_residual["bytes"],
             "EM9305 residual readiness does not conserve bytes")
    em_completion = em.get("completion_bucket_mapping", {})
    _require(em_completion.get("component_bytes") == 212_984 and
             em_completion.get("candidate_production_routed") is True and
             em_completion.get("release_blocking_bytes") == 210_584 and
             em_completion.get("buckets") == {
                 "production_source": 1_174,
                 "generated_or_reconstructible": 1_226,
                 "candidate_source_not_routed": 0,
                 "typed_retained_or_external": 210_584,
                 "unclassified": 0,
             }, "EM9305 completion mapping changed")

    touch = _read(TOUCH_SUMMARY)
    touch_current = _read(TOUCH_CURRENT)
    touch_source_image = _read(TOUCH_SOURCE_IMAGE)
    _require(touch_source_image.get("software_link_complete") is True,
             "Touch source image does not link completely")
    _require(touch_source_image.get("software_package_complete") is True,
             "Touch source image does not produce a complete FWPK package")
    _require(touch_source_image.get("production_routed") is False,
             "Touch source image unexpectedly claims production routing")
    _require(touch_source_image.get("hardware_validation") ==
             HARDWARE_VALIDATION,
             "Touch source image hardware blocker changed")
    case_source_image = _read(CASE_SOURCE_IMAGE)
    _require(case_source_image.get("software_link_complete") is True,
             "Case source image is not link-complete")
    _require(case_source_image.get("software_package_complete") is True,
             "Case source package is not complete")
    _require(case_source_image.get("production_routed") is False,
             "Case source image unexpectedly claims production routing")
    _require(case_source_image.get("hardware_validation") ==
             HARDWARE_VALIDATION,
             "Case source image hardware blocker changed")
    pt_source = _read(PT_SOURCE)
    pt_software = pt_source.get("software", {})
    _require(pt_software.get("handler_surface_complete") is True,
             "PT protocol handler surface is not source-complete")
    _require(int(pt_software.get("bound_commands", -1)) == 66,
             "PT protocol does not bind all 66 commands")
    _require(int(pt_software.get("missing_commands", -1)) == 0 and
             int(pt_software.get("duplicate_commands", -1)) == 0,
             "PT protocol command bindings are not one-to-one")
    _require(int(pt_software.get("target_undefined_symbols", -1)) == 0,
             "PT protocol relocatable retains undefined symbols")
    _require(pt_source.get("hardware", {}).get("validation") ==
             HARDWARE_VALIDATION,
             "PT protocol hardware blocker changed")
    nemavg_caps = _read(NEMAVG_STROKE_CAPS)
    _require(nemavg_caps.get("status") ==
             "nemavg-stroke-caps-production-source-routed",
             "NemaVG stroke-cap production status changed")
    _require(nemavg_caps.get("hardware_validation") ==
             HARDWARE_VALIDATION,
             "NemaVG stroke-cap hardware blocker changed")
    nemavg_stock_bytes = int(nemavg_caps["stock"]["physical_bytes"])
    nemavg_routed_functions = int(
        nemavg_caps["candidate"]["production_routed_functions"]
    )
    nemavg_routed_bytes = int(
        nemavg_caps["candidate"]["production_routed_physical_bytes"]
    )
    nemavg_retained_functions = int(
        nemavg_caps["candidate"]["remaining_candidate_functions"]
    )
    nemavg_retained_bytes = int(
        nemavg_caps["candidate"]["remaining_candidate_physical_bytes"]
    )
    nemavg_records = nemavg_caps["stock"].get("records", [])
    _require(nemavg_caps["stock"]["functions"] == 3 and
             nemavg_stock_bytes == 6614 and
             nemavg_caps["candidate"]["semantic_c"] is True and
             nemavg_caps["candidate"]["production_routed"] is True and
             nemavg_caps["candidate"]["endpoint_stock_entries_unpatched"] is False and
             nemavg_caps["candidate"]["endpoint_candidate_exact_stock_abi"] is True and
             nemavg_routed_functions == 3 and nemavg_routed_bytes == 6614 and
             nemavg_retained_functions == 0 and nemavg_retained_bytes == 0 and
             nemavg_routed_bytes + nemavg_retained_bytes == nemavg_stock_bytes and
             nemavg_caps["candidate"]["software_blocker"] is None,
             "NemaVG stroke-cap source admission changed")
    _require(len(nemavg_records) == 3 and
             [row.get("production_routed") for row in nemavg_records] ==
             [True, True, True] and
             [row.get("physical_bytes") for row in nemavg_records] ==
             [1668, 1640, 3306],
             "NemaVG stroke-cap per-entry routing boundary changed")
    origin_release = origin.get("release_readiness_partition", {})
    origin_unanchored = origin.get("unanchored_frontier_partition", {})
    origin_object_evidence = origin.get(
        "overlapping_object_closure_evidence", {}
    )
    _require(origin_release == {
        "candidate_source_not_routed": 0,
        "typed_retained_or_external": 3_065_088,
    } and _sum(origin_release) == main["opaque_base_bytes"],
        "Apollo origin/readiness partition changed")
    _require(origin_unanchored == {
        "candidate_source_not_routed": 0,
        "typed_retained_unanchored_without_candidate": 599_340,
    } and _sum(origin_unanchored) ==
        int(origin_buckets["unanchored_discovered_function"]),
        "Apollo unanchored frontier changed")
    _require(origin_object_evidence == {
        "bytes": 885_418,
        "additive_to_disjoint_release_totals": False,
    }, "Apollo overlapping object evidence policy changed")
    _require(int(origin["controlled_bytes_mislabeled_official_blob"]) == 17_800,
             "Apollo controlled-label reconciliation changed")
    clkmgr_dividers = _read(CLKMGR_DIVIDERS)
    _require(clkmgr_dividers.get("status") ==
             "apollo-clkmgr-divider-production-routed",
             "clock-manager divider production status changed")
    _require(clkmgr_dividers.get("hardware_validation") ==
             HARDWARE_VALIDATION,
             "clock-manager divider hardware blocker changed")
    clkmgr_boot_bytes = int(clkmgr_dividers["stock"]["bootloader_bytes"])
    clkmgr_main_bytes = int(clkmgr_dividers["stock"]["apollo_main_bytes"])
    _require(clkmgr_dividers["stock"]["functions_per_image"] == 2 and
             clkmgr_boot_bytes == 52 and clkmgr_main_bytes == 52 and
             clkmgr_dividers["candidate"]["semantic_c"] is True and
             clkmgr_dividers["candidate"]["production_routed"] is True and
             clkmgr_dividers["candidate"]["software_blocker"] is None,
             "clock-manager divider production admission changed")
    _require(nemavg_routed_bytes <= main["replaced_stock_function_bytes"],
             "Apollo-main NemaVG route exceeds replaced stock bytes")
    touch_metrics = touch["metrics"]
    touch_buckets = dict(touch_metrics["whole_blob_bucket_bytes"])
    baseline_touch_candidate = int(touch_buckets["project_source_candidate"])
    _require(_sum(touch_buckets) == touch_metrics["whole_blob_bytes"],
             "touch readiness does not conserve bytes")
    touch_progress = _touch_admission_progress()
    touch_admission_chain_delta = touch_progress[
        "cumulative_candidate_instruction_bytes"
    ]
    _require(touch_current.get("classification_complete") is True,
             "Touch current frontier is not classification-complete")
    touch_final = _read(TOUCH_FINAL)
    _require(touch_final.get("classification_complete") is True,
             "Touch final frontier is not classification-complete")
    touch_generation_receipt = _touch_generation_receipt(
        touch_current, touch_final
    )
    final_metrics: dict[str, Any] = touch_final.get("metrics", {})
    final_buckets = touch_current.get("whole_blob_bucket_bytes", {})
    _require(final_buckets == final_metrics.get("whole_blob_bucket_bytes"),
             "Touch current and final physical buckets disagree")
    _require(touch_current.get("physical_bucket_digest") ==
             final_metrics.get("physical_bucket_digest"),
             "Touch current and final physical bucket digests disagree")
    _require(set(final_buckets) == {
        "generated_transport_fill", "project_source_candidate",
        "typed_external_or_unsupported", "still_unclassified",
    }, "Touch final physical buckets are incomplete")
    _require(_sum(final_buckets) == touch_metrics["whole_blob_bytes"],
             "Touch final physical buckets do not cover the whole blob")
    _require(int(final_buckets["still_unclassified"]) == 0,
             "Touch final classification retains unclassified bytes")
    _require(int(final_buckets["generated_transport_fill"]) ==
             int(touch_buckets["generated_transport_fill"]),
             "Touch generated transport identity changed")
    _require(int(final_buckets["project_source_candidate"]) >=
             int(touch_buckets["project_source_candidate"]),
             "Touch final source bucket lost the baseline candidates")
    candidate_provenance_rows = _touch_candidate_provenance_rows()
    touch_candidate_provenance = _touch_candidate_provenance_summary(
        touch_current, touch_final, touch_source_image,
        candidate_provenance_rows,
    )
    touch_delta = (
        touch_candidate_provenance["candidate_bytes"] -
        baseline_touch_candidate
    )
    _require(int(final_buckets["project_source_candidate"]) ==
             touch_candidate_provenance["candidate_bytes"] and
             baseline_touch_candidate + touch_delta ==
             touch_candidate_provenance["candidate_bytes"] and
             0 <= touch_candidate_provenance[
                 "overlapping_semantic_claim_bytes"] <=
             touch_candidate_provenance["candidate_bytes"] and
             0 <= touch_admission_chain_delta <= touch_delta,
             "Touch candidate provenance does not bind the final bucket")
    touch_buckets = {key: int(value) for key, value in final_buckets.items()}
    _require(_sum(touch_buckets) == touch_metrics["whole_blob_bytes"],
             "live Touch readiness does not conserve bytes")

    case = _read(CASE_SUMMARY)
    case_map = case["map"]
    case_app = int(case["identity"]["app_bytes"])
    case_categories = case_map["combined_category_bytes"]
    _require(_sum(case_categories) == case_app,
             "case ownership map does not cover the application")
    case_unclassified = int(case_categories["unresolved"])
    case_admission = _read(CASE_REGISTER_ADMISSION)
    case_admission_metrics = case_admission["metrics"]
    case_candidate = int(case_admission_metrics["admitted_instruction_bytes"])
    _require(case_admission["integration"].startswith("isolated source candidate"),
             "case register primitives unexpectedly claim production routing")
    _require(case_admission_metrics["unclassified_bytes_before"] ==
             case_unclassified,
             "case register admission baseline changed")
    _require(case_admission_metrics["unclassified_bytes_after"] ==
             case_unclassified - case_candidate,
             "case register admission does not conserve bytes")
    case_unclassified -= case_candidate
    case_transforms = _read(CASE_REGISTER_TRANSFORMS)
    case_transform_metrics = case_transforms["metrics"]
    case_transform_candidate = int(
        case_transform_metrics["admitted_instruction_bytes"])
    _require(case_transforms["integration"].startswith(
                 "isolated source candidate"),
             "case register transforms unexpectedly claim production routing")
    _require(case_transform_metrics["unclassified_bytes_before"] ==
             case_unclassified,
             "case register transform baseline changed")
    _require(case_transform_metrics["unclassified_bytes_after"] ==
             case_unclassified - case_transform_candidate,
             "case register transform admission does not conserve bytes")
    case_unclassified -= case_transform_candidate
    case_candidate += case_transform_candidate
    case_semantic = _read(CASE_SEMANTIC_LEAVES)
    case_semantic_metrics = case_semantic["metrics"]
    case_semantic_candidate = int(
        case_semantic_metrics["admitted_instruction_bytes"])
    _require(case_semantic["integration"].startswith(
                 "isolated source candidate"),
             "case semantic leaves unexpectedly claim production routing")
    _require(int(case_semantic_metrics["admitted_functions"]) == 189 and
             case_semantic_candidate == 14208,
             "case semantic-leaf admission baseline changed")
    case_candidate += case_semantic_candidate
    case_pure = _read(CASE_PURE_HELPERS)
    case_pure_metrics = case_pure["metrics"]
    case_pure_candidate = int(case_pure_metrics["admitted_instruction_bytes"])
    _require(case_pure["integration"].startswith("isolated source candidate"),
             "case pure helpers unexpectedly claim production routing")
    _require(int(case_pure_metrics["admitted_functions"]) == 7 and
             case_pure_candidate == 248,
             "case pure-helper admission baseline changed")
    case_candidate += case_pure_candidate
    case_policies = _read(CASE_REGISTER_POLICIES)
    case_policy_metrics = case_policies["metrics"]
    case_policy_candidate = int(case_policy_metrics["admitted_instruction_bytes"])
    _require(case_policies["integration"].startswith("isolated source candidate"),
             "case register policies unexpectedly claim production routing")
    _require(int(case_policy_metrics["admitted_functions"]) == 8 and
             case_policy_candidate == 214,
             "case register-policy admission baseline changed")
    case_candidate += case_policy_candidate
    case_size = int(base_components["case"]["provider"]["size"])
    case_wrapper = case_size - case_app
    _require(case_wrapper >= 0, "case wrapper accounting is negative")

    codec_size = int(base_components["codec"]["provider"]["size"])
    em_size = int(em_completion["component_bytes"])
    em_override = core["component_overrides"]["ble_em9305"]["provider"]
    _require(
        (em_override.get("size"), em_override.get("sha256"),
         em_override.get("kind"), em_override.get("path"))
        == (212_984,
            "1a4ccc61cae6e9b90d0eb3d694179d726c935171788167d28ea45060d7431c42",
            "source_build",
            "components/em9305/source_overlay/build/firmware_ble_em9305.bin"),
        "EM9305 core-manifest provider identity changed",
    )
    touch_size = int(base_components["touch"]["provider"]["size"])
    _require(codec_size == gx["partition"]["bytes"], "codec identity changed")
    _require(touch_size == touch_metrics["whole_blob_bytes"], "touch identity changed")
    case_final = _read(CASE_FINAL)
    _require(case_final.get("classification_complete") is True,
             "case final frontier is not classification-complete")
    case_final_metrics = case_final.get("metrics", {})
    case_final_buckets = case_final_metrics.get("whole_blob_bucket_bytes", {})
    _require(_sum(case_final_buckets) == case_size,
             "case final physical buckets do not cover the whole blob")
    _require(int(case_final_buckets.get("still_unclassified", -1)) == 0,
             "case final classification retains unclassified bytes")

    pt_candidate_bytes = int(
        pt_source["evidence"]["stock_function_body_bytes"])
    _require(pt_candidate_bytes == 32866,
             "PT protocol candidate stock-byte baseline changed")
    _require(pt_software["handler_surface_complete"] is True and
             pt_software["target_undefined_symbols"] == 0 and
             pt_software["production_bootstrap_complete"] is True and
             pt_software["platform_backend_production_bound"] is True and
             pt_software["target_loadable_bytes"] == 22643 and
             pt_software["target_bss_bytes"] == 0 and
             pt_software["production_text_placement_free_bytes"] == 72740 and
             pt_software["production_text_placement_shortfall_bytes"] == 0 and
             pt_software["production_ram_binding_remaining_bytes"] == 0 and
             pt_software["production_in_place_loadable_bytes"] == 22696 and
             pt_software["production_placement_complete"] is True,
             "PT protocol candidate is not source/link complete")
    _require(pt_software["production_routed"] is True,
             "PT protocol is not production-routed")
    pt_provider_candidate_bytes = int(
        pt_software["board_retained_provider_candidate_stock_body_bytes"])
    _require(
        pt_software["board_retained_provider_candidate_bindings"] == 40 and
        pt_software["board_top_level_retained_provider_bindings_remaining"] == 4 and
        pt_software["board_retained_provider_bindings_remaining"] == 13 and
        pt_provider_candidate_bytes == 3402 and
        pt_software["board_retained_provider_candidates_semantic_c"] is True and
        pt_software["board_retained_provider_candidates_production_routed"] is
        True and
        pt_software["board_retained_providers_source_owned"] is False and
        pt_software["board_source_complete"] is False and
        pt_software["board_second_order_callable_bindings"] == 81 and
        pt_software["board_second_order_source_overlay_callable_bindings"] == 29 and
        pt_software["board_second_order_source_local_callable_bindings"] == 39 and
        pt_software["board_second_order_source_callable_bindings"] == 68 and
        pt_software["board_second_order_retained_callable_bindings"] == 13 and
        pt_software["board_second_order_retained_callable_unique_addresses"] == 13 and
        pt_software["board_second_order_data_bindings"] == 97 and
        pt_software["board_second_order_data_unique_addresses"] == 94 and
        pt_software["board_second_order_data_source_owned"] == 0 and
        pt_software["board_second_order_retained_data_bindings"] == 97 and
        pt_software["board_second_order_data_categories"] == {
            "external_xip_bound": 2,
            "external_xip_data": 2,
            "immutable_flash_data": 33,
            "peripheral_mmio": 5,
            "retained_callback_entry": 2,
            "runtime_sram_data": 53,
        } and
        pt_software["board_second_order_retained_boundaries_deliberately_supported"]
        is True,
        "PT retained-provider leaf candidate admission changed")
    _require(
        pt_software["board_stock_layout_data_bindings"] == 53 and
        pt_software["board_stock_layout_data_immutable_flash_bindings"] == 17 and
        pt_software["board_stock_layout_data_runtime_sram_bindings"] == 36 and
        pt_software["board_stock_layout_data_deliberately_supported"] is True and
        pt_software["board_stock_layout_data_software_gap"] is False and
        pt_software["board_stock_layout_data_source_owned"] is False,
        "PT retained-data ABI support policy changed")

    components = {
        "apollo_main": _component(
            size=main["size"], production_source=main["source_owned_bytes"],
            generated_or_reconstructible=main_generated,
            candidate_source=nemavg_retained_bytes,
            typed_retained_or_external=(main["opaque_base_bytes"] -
                                        nemavg_retained_bytes),
            release_blocking=main["opaque_base_bytes"], production_routed=True,
            details={"origin_buckets": origin_buckets,
                     "provider_sha256": main["sha256"],
                     "nemavg_stroke_cap_candidate_functions":
                         nemavg_retained_functions,
                     "nemavg_stroke_cap_candidate_bytes":
                         nemavg_retained_bytes,
                     "nemavg_stroke_cap_source_routed_functions":
                         nemavg_routed_functions,
                     "nemavg_stroke_cap_source_routed_stock_bytes":
                         nemavg_routed_bytes,
                     "nemavg_stroke_cap_retained_unpatched_functions":
                         nemavg_retained_functions,
                     "nemavg_stroke_cap_retained_unpatched_stock_bytes":
                         nemavg_retained_bytes,
                     "nemavg_stroke_cap_production_routed":
                         nemavg_caps["candidate"]["production_routed"],
                     "nemavg_stroke_cap_coordinator_production_routed":
                         nemavg_caps["stock"]["records"][2]
                             ["production_routed"],
                     "nemavg_stroke_cap_endpoint_stock_entries_unpatched":
                         nemavg_caps["candidate"]
                             ["endpoint_stock_entries_unpatched"],
                     "clkmgr_divider_source_functions":
                         clkmgr_dividers["stock"]["functions_per_image"],
                     "clkmgr_divider_source_stock_bytes": clkmgr_main_bytes,
                     "clkmgr_divider_production_routed":
                         clkmgr_dividers["candidate"]["production_routed"],
                     "release_readiness_partition": origin_release,
                     "unanchored_frontier_partition": origin_unanchored,
                     "controlled_label_reconciliation_bytes":
                         origin["controlled_bytes_mislabeled_official_blob"],
                     "controlled_label_reconciliation_additive": False,
                     "overlapping_object_closure_evidence":
                         origin_object_evidence,
                     "pt_protocol_handler_surface_complete":
                         pt_software["handler_surface_complete"],
                     "pt_protocol_candidate_stock_body_bytes":
                         pt_candidate_bytes,
                     "pt_protocol_target_loadable_bytes":
                         pt_software["target_loadable_bytes"],
                     "pt_protocol_target_bss_bytes":
                         pt_software["target_bss_bytes"],
                     "pt_protocol_production_text_placement_free_bytes":
                         pt_software["production_text_placement_free_bytes"],
                     "pt_protocol_production_text_placement_shortfall_bytes":
                         pt_software[
                             "production_text_placement_shortfall_bytes"],
                     "pt_protocol_production_ram_binding_remaining_bytes":
                         pt_software[
                             "production_ram_binding_remaining_bytes"],
                     "pt_protocol_production_placement_complete":
                         pt_software["production_placement_complete"],
                     "pt_protocol_retained_provider_candidate_bindings":
                         pt_software[
                             "board_retained_provider_candidate_bindings"],
                     "pt_protocol_retained_provider_candidate_stock_body_bytes":
                         pt_provider_candidate_bytes,
                     "pt_protocol_retained_provider_bindings_remaining":
                         pt_software[
                             "board_retained_provider_bindings_remaining"],
                     "pt_protocol_top_level_retained_provider_bindings_remaining":
                         pt_software[
                             "board_top_level_retained_provider_bindings_remaining"],
                     "pt_protocol_board_source_complete":
                         pt_software["board_source_complete"],
                     "pt_protocol_second_order_callable_bindings":
                         pt_software["board_second_order_callable_bindings"],
                     "pt_protocol_second_order_source_overlay_callable_bindings":
                         pt_software[
                             "board_second_order_source_overlay_callable_bindings"],
                     "pt_protocol_second_order_source_local_callable_bindings":
                         pt_software[
                             "board_second_order_source_local_callable_bindings"],
                     "pt_protocol_second_order_source_callable_bindings":
                         pt_software[
                             "board_second_order_source_callable_bindings"],
                     "pt_protocol_second_order_retained_callable_bindings":
                         pt_software[
                             "board_second_order_retained_callable_bindings"],
                     "pt_protocol_second_order_retained_callable_unique_addresses":
                         pt_software[
                             "board_second_order_retained_callable_unique_addresses"],
                     "pt_protocol_second_order_data_bindings":
                         pt_software["board_second_order_data_bindings"],
                     "pt_protocol_second_order_data_unique_addresses":
                         pt_software[
                             "board_second_order_data_unique_addresses"],
                     "pt_protocol_second_order_data_source_owned":
                         pt_software["board_second_order_data_source_owned"],
                     "pt_protocol_second_order_retained_data_bindings":
                         pt_software[
                             "board_second_order_retained_data_bindings"],
                     "pt_protocol_second_order_data_categories":
                         pt_software["board_second_order_data_categories"],
                     "pt_protocol_second_order_retained_boundaries_deliberately_supported":
                         pt_software[
                             "board_second_order_retained_boundaries_deliberately_supported"],
                     "pt_protocol_stock_layout_data_bindings":
                         pt_software["board_stock_layout_data_bindings"],
                     "pt_protocol_stock_layout_data_immutable_flash_bindings":
                         pt_software[
                             "board_stock_layout_data_immutable_flash_bindings"],
                     "pt_protocol_stock_layout_data_runtime_sram_bindings":
                         pt_software[
                             "board_stock_layout_data_runtime_sram_bindings"],
                     "pt_protocol_stock_layout_data_deliberately_supported":
                         pt_software[
                             "board_stock_layout_data_deliberately_supported"],
                     "pt_protocol_stock_layout_data_software_gap":
                         pt_software["board_stock_layout_data_software_gap"],
                     "pt_protocol_bound_commands":
                         pt_software["bound_commands"],
                     "pt_protocol_target_undefined_symbols":
                         pt_software["target_undefined_symbols"],
                     "pt_protocol_provider_adapters_complete":
                         pt_software["provider_adapters_complete"],
                     "pt_protocol_platform_backend_contract_complete":
                         pt_software["platform_backend_contract_complete"],
                     "pt_protocol_stock_abi_entry_complete":
                         pt_software["stock_abi_entry_complete"],
                     "pt_protocol_production_bootstrap_complete":
                         pt_software["production_bootstrap_complete"],
                     "pt_protocol_platform_backend_production_bound":
                         pt_software["platform_backend_production_bound"],
                     "pt_protocol_production_routed":
                         pt_software["production_routed"]}),
        "apollo_bootloader": _component(
            size=boot["size"], production_source=boot["source_owned_bytes"],
            generated_or_reconstructible=boot_generated,
            candidate_source=0,
            typed_retained_or_external=boot["opaque_base_bytes"],
            release_blocking=boot["opaque_base_bytes"], production_routed=True,
            details={"provider_sha256": boot["sha256"],
                     "source_owned_in_place_bytes":
                         boot["source_owned_in_place_bytes"],
                     "retained_complement": boot_partition,
                     "clkmgr_divider_source_functions":
                         clkmgr_dividers["stock"]["functions_per_image"],
                     "clkmgr_divider_source_stock_bytes": clkmgr_boot_bytes,
                     "clkmgr_divider_production_routed":
                         clkmgr_dividers["candidate"]["production_routed"]}),
        "codec": _component(
            size=codec_size, generated_or_reconstructible=gx_reconstructible,
            typed_retained_or_external=gx_external + gx_unavailable,
            release_blocking=gx_external + gx_unavailable,
            production_routed=False,
            details={"typed_external_spans":
                         gx_ready["typed_unsupported_external_boundary"]["spans"],
                     "unavailable_proprietary_bytes": gx_unavailable,
                     "external_provider_detail": codec_external_detail,
                     "external_provider_claims_open_availability": False}),
        "ble_em9305": _component(
            size=em_size,
            production_source=em_completion["buckets"]["production_source"],
            generated_or_reconstructible=em_completion["buckets"]
                ["generated_or_reconstructible"],
            candidate_source=em_completion["buckets"]
                ["candidate_source_not_routed"],
            typed_retained_or_external=em_completion["buckets"]
                ["typed_retained_or_external"],
            release_blocking=em_completion["release_blocking_bytes"],
            production_routed=True,
            details={"residual_scope_bytes": em_residual["bytes"],
                     "residual_readiness_bytes": em_residual["readiness_bytes"],
                     "residual_unclassified_bytes": 0,
                     "production_source_bytes": 1_174,
                     "generated_or_reconstructible_bytes": 1_226,
                     "candidate_source_not_routed_bytes": 0,
                     "typed_retained_or_external_bytes": 210_584,
                     "candidate_production_routed": True,
                     "hardware_operations": em["hardware_operations"],
                     "final_source_readiness_receipts": em_final_receipts,
                     "completion_bucket_mapping": em_completion}),
        "touch": _component(
            size=touch_size,
            generated_or_reconstructible=touch_buckets["generated_transport_fill"],
            candidate_source=touch_buckets["project_source_candidate"],
            typed_retained_or_external=touch_buckets["typed_external_or_unsupported"],
            unclassified=touch_buckets["still_unclassified"],
            release_blocking=touch_size - touch_buckets["generated_transport_fill"],
            production_routed=bool(touch["release_readiness"]["production_routed"]),
            details={"reachable_unclassified_functions":
                         touch_progress["unclassified_functions"],
                     "remaining_source_or_implementation_functions":
                         touch_progress["remaining_functions"],
                     "unimplemented_application_contracts":
                         touch_progress["remaining_application_contracts"],
                     "authoritative_batch":
                         touch_progress["authoritative_batch"],
                     "cumulative_candidate_instruction_bytes": touch_delta,
                     "admission_chain_candidate_instruction_bytes":
                         touch_admission_chain_delta,
                     "admission_batches": touch_progress["admission_batches"],
                     "candidate_provenance": touch_candidate_provenance,
                     "candidate_provenance_subrows":
                         len(candidate_provenance_rows),
                     "candidate_provenance_manifest":
                         TOUCH_CANDIDATE_PROVENANCE.name,
                     "generation_receipt": touch_generation_receipt,
                     "resident_abi_available":
                         touch["release_readiness"]["resident_abi_available"],
                     "software_image_link_complete":
                         touch_source_image["software_link_complete"],
                     "software_fwpk_package_complete":
                         touch_source_image["software_package_complete"],
                     "source_image_translation_units":
                         touch_source_image["metrics"]["source_translation_units"],
                     "source_image_undefined_symbols":
                         touch_source_image["metrics"]["undefined_symbols"],
                     "source_image_raw_flash_bytes":
                         touch_source_image["metrics"]["raw_flash_bytes"],
                     "typed_code_complement_bytes":
                         final_metrics.get("typed_code_complement_bytes"),
                     "typed_noncode_bytes":
                         final_metrics.get("typed_noncode_bytes"),
                     "typed_noncode_partition":
                         final_metrics.get("typed_noncode_partition"),
                     "typed_semantic_mask_digest":
                         final_metrics.get("physical_bucket_digest")}),
        "case": _component(
            size=case_size,
            generated_or_reconstructible=int(
                case_final_buckets["generated_transport_fill"]),
            candidate_source=int(
                case_final_buckets["project_source_candidate"]),
            typed_retained_or_external=int(
                case_final_buckets["typed_external_or_unsupported"]),
            unclassified=int(case_final_buckets["still_unclassified"]),
            release_blocking=case_app, production_routed=False,
            details={"ownership_categories": case_categories,
                     "register_candidate_bytes": case_candidate,
                     "register_candidate_functions":
                         (case_admission_metrics["admitted_functions"] +
                          case_transform_metrics["admitted_functions"] +
                          case_semantic_metrics["admitted_functions"] +
                          case_pure_metrics["admitted_functions"] +
                          case_policy_metrics["admitted_functions"]),
                     "register_primitive_candidate_bytes":
                         case_admission_metrics["admitted_instruction_bytes"],
                     "register_primitive_candidate_functions":
                         case_admission_metrics["admitted_functions"],
                     "register_transform_candidate_bytes":
                         case_transform_metrics["admitted_instruction_bytes"],
                     "register_transform_candidate_functions":
                         case_transform_metrics["admitted_functions"],
                     "semantic_leaf_candidate_bytes":
                         case_semantic_candidate,
                     "semantic_leaf_candidate_functions":
                         case_semantic_metrics["admitted_functions"],
                     "pure_helper_candidate_bytes": case_pure_candidate,
                     "pure_helper_candidate_functions":
                         case_pure_metrics["admitted_functions"],
                     "register_policy_candidate_bytes": case_policy_candidate,
                     "register_policy_candidate_functions":
                         case_policy_metrics["admitted_functions"],
                     "open_semantic_questions": case["unresolved"],
                     "prior_unresolved_bytes": 17070,
                     "final_unclassified_bytes":
                         case_final_metrics["unclassified_bytes"],
                     "typed_unsupported_frontier_bytes":
                         case_final_metrics["typed_unsupported_frontier_bytes"],
                     "software_image_link_complete":
                         case_source_image["software_link_complete"],
                     "software_even_package_complete":
                         case_source_image["software_package_complete"],
                     "source_image_translation_units":
                         case_source_image["metrics"]["source_translation_units"],
                     "source_image_undefined_symbols":
                         case_source_image["metrics"]["undefined_symbols"],
                     "source_image_raw_flash_bytes":
                         case_source_image["metrics"]["raw_flash_bytes"],
                     "physical_bucket_digest":
                         case_final_metrics["physical_bucket_digest"]}),
    }

    aggregate_buckets = {
        key: sum(component["buckets"][key] for component in components.values())
        for key in next(iter(components.values()))["buckets"]
    }
    component_bytes = sum(component["size"] for component in components.values())
    _require(_sum(aggregate_buckets) == component_bytes,
             "aggregate component ledger does not conserve bytes")
    package_bytes = int(core["package"]["expected_size"])
    _require(package_bytes >= component_bytes, "package is smaller than its components")

    license_report = licensing.analyze()
    license_summary = license_report["summary"]
    unresolved_authority = license_summary["redistribution_authority_unresolved"]
    raw_quality = raw_encoding_quality.analyze()
    raw_quality_summary = _read(RAW_ENCODING_SUMMARY)
    _require(raw_quality["classification_complete"] is True,
             "production raw-encoding census is not classification-complete")
    _require(raw_quality["metrics"] == raw_quality_summary["metrics"],
             "live production raw-encoding audit disagrees with its summary")
    raw_overstated = int(
        raw_quality["metrics"]["source_owned_bytes_currently_overstated"])
    raw_quality_clean = raw_overstated == 0
    _require(raw_quality_clean == bool(raw_quality["source_ownership_suitable"]),
             "production raw-encoding quality disposition is inconsistent")
    project_license = project_license_policy.analyze()
    project_license_summary = _read(PROJECT_LICENSE_SUMMARY)
    _require(project_license["metrics"] == project_license_summary["metrics"],
             "live project license policy disagrees with its summary")
    project_license_pending = int(project_license["metrics"]
        ["distributed_unique_project_files_pending_normalization"])
    project_license_clean = project_license_pending == 0
    _require(project_license_clean == bool(
                 project_license["normalization_complete"]),
             "project license normalization disposition is inconsistent")
    expected_names = set(components)
    artifact_names = {row["component"] for row in license_report["artifacts"]}
    _require(artifact_names == expected_names,
             "licensing audit no longer covers every G2 component")
    _require(set(unresolved_authority) <= expected_names,
             "licensing audit named an unknown G2 component")

    unclassified_components = [
        name for name, row in components.items() if not row["classification_complete"]
    ]
    source_incomplete_components = [
        name for name, row in components.items() if not row["source_complete"]
    ]
    return {
        "schema_version": 1,
        "analysis_mode": (
            "offline composed byte/source/license audit; no hardware, MMIO, reset, "
            "DFU, signing, flashing, or publishing operation"
        ),
        "components": components,
        "aggregate": {
            "component_payload_bytes": component_bytes,
            "package_bytes": package_bytes,
            "package_envelope_bytes": package_bytes - component_bytes,
            "buckets": aggregate_buckets,
            "release_blocking_bytes": sum(
                row["release_blocking_bytes"] for row in components.values()),
            "unclassified_components": unclassified_components,
            "source_incomplete_components": source_incomplete_components,
        },
        "gates": {
            "byte_accounting_complete": True,
            "classification_complete": not unclassified_components,
            "source_complete": not source_incomplete_components,
            "source_metadata_clean": license_summary["source_errors"] == 0,
            "source_ownership_quality_clean": raw_quality_clean,
            "project_license_policy_clean": project_license_clean,
            "binary_redistribution_authority_resolved": not unresolved_authority,
            "release_authorized": (
                license_summary["release_authorized"] and raw_quality_clean
                and project_license_clean),
            "hardware_validation": HARDWARE_VALIDATION,
            "hardware_blocker": HARDWARE_VALIDATION,
            "hardware_operations": [],
        },
        "licensing": {
            "source_files": license_summary["source_files"],
            "source_errors": license_summary["source_errors"],
            "unresolved_binary_authority": unresolved_authority,
        },
        "source_ownership_quality": {
            "clean": raw_quality_clean,
            "source_owned_bytes_currently_overstated": raw_overstated,
            "production_routed_sources_with_directives": raw_quality["metrics"][
                "production_routed_sources_with_directives"],
            "raw_instruction_transcription_bytes": raw_quality["metrics"][
                "raw_instruction_transcription_bytes"],
            "semantic_literal_bytes": raw_quality["metrics"][
                "semantic_literal_bytes"],
            "quality_gate": raw_quality["quality_gate"],
        },
        "project_license_policy": {
            "clean": project_license_clean,
            "project_owned_normalization_targets": project_license["metrics"][
                "project_owned_normalization_targets"],
            "project_owned_records_normalized_mit": project_license["metrics"][
                "project_owned_records_normalized_mit"],
            "project_owned_gpl_records_pending_mit": project_license_pending,
            "overlay_records_pending_mit": project_license["metrics"][
                "project_owned_gpl_records_pending_mit"],
            "distributed_project_mit_normalization_targets":
                project_license["metrics"][
                    "distributed_project_mit_normalization_targets"],
            "community_controller_and_adapter_source_files":
                project_license["metrics"][
                    "community_controller_and_adapter_source_files"],
            "community_project_mit_compatible_source_files":
                project_license["metrics"][
                    "community_project_mit_compatible_source_files"],
            "community_touch_apache_source_files_preserved":
                project_license["metrics"][
                    "community_touch_apache_source_files_preserved"],
            "touch_source_image_project_mit_files":
                project_license["metrics"][
                    "touch_source_image_project_mit_files"],
            "touch_source_image_package_files":
                project_license["metrics"][
                    "touch_source_image_package_files"],
            "touch_source_image_support_files":
                project_license["metrics"][
                    "touch_source_image_support_files"],
            "case_source_image_project_mit_files":
                project_license["metrics"][
                    "case_source_image_project_mit_files"],
            "case_source_image_package_files":
                project_license["metrics"][
                    "case_source_image_package_files"],
            "case_source_image_support_files":
                project_license["metrics"][
                    "case_source_image_support_files"],
            "em9305_source_image_project_mit_files":
                project_license["metrics"][
                    "em9305_source_image_project_mit_files"],
            "em9305_source_image_package_files":
                project_license["metrics"][
                    "em9305_source_image_package_files"],
            "em9305_source_image_support_files":
                project_license["metrics"][
                    "em9305_source_image_support_files"],
            "pt_protocol_project_mit_files":
                project_license["metrics"][
                    "pt_protocol_project_mit_files"],
            "upstream_gpl_records_preserved": project_license["metrics"][
                "upstream_gpl_records_preserved"],
            "apache_records_preserved": project_license["metrics"][
                "apache_records_preserved"],
            "bsd_records_preserved": project_license["metrics"][
                "bsd_records_preserved"],
            "zlib_records_preserved": project_license["metrics"][
                "zlib_records_preserved"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-classified", action="store_true")
    parser.add_argument("--require-source-complete", action="store_true")
    parser.add_argument("--require-source-ownership-quality", action="store_true")
    parser.add_argument("--require-project-license-policy", action="store_true")
    args = parser.parse_args()
    report = analyze()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        aggregate = report["aggregate"]
        print("G2 firmware completion readiness")
        print(f"  component payload bytes: {aggregate['component_payload_bytes']}")
        print(f"  unclassified bytes: {aggregate['buckets']['unclassified']}")
        print(f"  release-blocking bytes: {aggregate['release_blocking_bytes']}")
        print(f"  classification complete: {report['gates']['classification_complete']}")
        print(f"  source complete: {report['gates']['source_complete']}")
        print("  source ownership quality clean: "
              f"{report['gates']['source_ownership_quality_clean']}")
        print("  source-owned bytes currently overstated: "
              f"{report['source_ownership_quality']['source_owned_bytes_currently_overstated']}")
        print("  project license policy clean: "
              f"{report['gates']['project_license_policy_clean']}")
        print("  project-owned GPL records pending MIT: "
              f"{report['project_license_policy']['project_owned_gpl_records_pending_mit']}")
        print(f"  release authorized: {report['gates']['release_authorized']}")
    if args.require_classified and not report["gates"]["classification_complete"]:
        return 2
    if args.require_source_complete and not report["gates"]["source_complete"]:
        return 3
    if (args.require_source_ownership_quality and
            not report["gates"]["source_ownership_quality_clean"]):
        return 4
    if (args.require_project_license_policy and
            not report["gates"]["project_license_policy_clean"]):
        return 5
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"G2 completion readiness audit failed: {exc}") from exc
