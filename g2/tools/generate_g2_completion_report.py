#!/usr/bin/env python3
"""Generate the deterministic public G2 completion assessment.

The report is a presentation of ``analyze_g2_completion_readiness.py`` rather
than an independent progress calculation.  It performs no device operation and
does not turn a classified or attributable byte into source ownership or a
binary redistribution grant.
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import ast
from collections import Counter
from copy import deepcopy
import hashlib
import html
import json
import os
from pathlib import Path
import secrets
import stat
from typing import Any

import analyze_g2_completion_readiness as readiness
import analyze_g2_dual_profile_ownership as dual_ownership
import audit_g2_release_licensing as licensing


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "docs/reports/openCFW-completion-2026-08-28"
ASSESSMENT_NAME = "assessment-data.json"
ARTIFACT_NAME = "artifact.json"
REPORT_NAME = "report.html"
HARDWARE_STATUS = "blocked by unavailable physical evidence"
SOURCE_COMPLETE_DEFINITION = (
    "Every required behavior byte is routed from maintained source: candidate, "
    "retained/external, and unclassified byte counts are all zero."
)

COMPONENT_LABELS = {
    "apollo_main": "Apollo main application",
    "apollo_bootloader": "Apollo bootloader",
    "codec": "GX8002 codec/DSP",
    "ble_em9305": "EM9305 BLE controller",
    "touch": "PSoC touch controller",
    "case": "STM32 charging case",
}
BUCKET_LABELS = {
    "production_source": "Production source",
    "generated_or_reconstructible": "Generated / reconstructible",
    "candidate_source_not_routed": "Candidate source, not routed",
    "typed_retained_or_external": "Typed retained / external",
    "unclassified": "Unclassified",
}
DIRECT_INPUTS = (
    readiness.BASE_MANIFEST,
    readiness.CORE_MANIFEST,
    readiness.MAIN_REPORT,
    readiness.BOOT_REPORT,
    readiness.APOLLO_ORIGIN,
    readiness.TOUCH_SOURCE_IMAGE,
    readiness.TOUCH_SUMMARY,
    readiness.TOUCH_CURRENT,
    readiness.TOUCH_FINAL,
    readiness.TOUCH_CANDIDATE_PROVENANCE,
    readiness.CASE_SOURCE_IMAGE,
    readiness.CASE_SUMMARY,
    readiness.NEMAVG_STROKE_CAPS,
    readiness.CLKMGR_DIVIDERS,
    readiness.PT_SOURCE,
    readiness.CASE_SEMANTIC_LEAVES,
    readiness.CASE_PURE_HELPERS,
    readiness.CASE_REGISTER_POLICIES,
    readiness.CASE_REGISTER_ADMISSION,
    readiness.CASE_REGISTER_TRANSFORMS,
    readiness.CASE_FINAL,
    readiness.RAW_ENCODING_SUMMARY,
    readiness.PROJECT_LICENSE_CENSUS,
    readiness.PROJECT_LICENSE_SUMMARY,
    readiness.PROJECT_LICENSE_SCOPE_PATHS,
    readiness.PROJECT_LICENSE_ADDITIONAL_PATHS,
    ROOT / "tools/manifests/gx8002-source-readiness.tsv",
    ROOT / "tools/manifests/em9305-residual-provenance-map.tsv",
    ROOT / "tools/manifests/em9305-record-package-summary.json",
    readiness.EM9305_FINAL_LEDGER,
    readiness.EM9305_FINAL_SUMMARY,
    ROOT / "components/apollo_main/core_overlay/overlay.json",
    ROOT / "components/bootloader/core_overlay/overlay.json",
    ROOT / "tools/analyze_g2_completion_readiness.py",
    ROOT / "tools/analyze_g2_touch_final_frontier.py",
    ROOT / "tools/analyze_em9305_controller_clusters.py",
    ROOT / "tools/analyze_em9305_first_party_hooks_candidate.py",
    ROOT / "tools/analyze_em9305_master_connection_boundary.py",
    ROOT / "tools/analyze_em9305_metaware_runtime_candidate.py",
    ROOT / "tools/analyze_em9305_pawr_boundary.py",
    ROOT / "tools/analyze_em9305_qpc.py",
    ROOT / "tools/analyze_em9305_qpc_hook_provider_candidate.py",
    ROOT / "tools/analyze_em9305_record_package.py",
    ROOT / "tools/analyze_em9305_sdk_discovery.py",
    ROOT / "tools/analyze_em9305_slave_connection_boundary.py",
    ROOT / "tools/analyze_em9305_source_readiness.py",
    ROOT / "tools/analyze_em9305_unclassified_tail_candidate.py",
    ROOT / "tools/analyze_g2_codec_fwpk_segments.py",
    ROOT / "tools/analyze_g2_codec_stage2_sections.py",
    ROOT / "tools/analyze_g2_dual_profile_ownership.py",
    ROOT / "tools/analyze_g2_production_raw_encoding_quality.py",
    ROOT / "tools/analyze_g2_project_license_normalization.py",
    ROOT / "tools/analyze_gx8002_source_readiness.py",
    ROOT / "tools/apollo_overlay.py",
    ROOT / "tools/apply_g2_canonical_observations.py",
    ROOT / "tools/audit_g2_release_licensing.py",
    ROOT / "tools/manifests/g2-dual-profile-ownership.json",
    ROOT / "components/em9305/source_image/README.md",
    ROOT / "components/em9305/source_image/build_image.py",
    ROOT / "components/em9305/source_image/record_package.py",
    ROOT / "tools/open_cfw.py",
    *sorted((ROOT / "tools/manifests").glob(
        "g2-touch-*-admission-summary.json")),
)
DIRECT_ANALYZER_INPUTS = frozenset(
    path for path in DIRECT_INPUTS
    if path.parent == ROOT / "tools" and path.suffix == ".py"
)


class ReportError(RuntimeError):
    """Raised when the public report cannot conserve its source audit."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReportError(message)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(_read_regular_path_once(path, label="report input"))


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _open_directory_path(path: Path, *, create: bool = False) -> int:
    absolute = Path(os.path.abspath(path))
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(absolute.anchor, flags)
    try:
        for part in absolute.parts[1:]:
            try:
                child = os.open(part, flags, dir_fd=descriptor)
            except FileNotFoundError:
                if not create:
                    raise
                try:
                    os.mkdir(part, 0o755, dir_fd=descriptor)
                except FileExistsError:
                    pass
                child = os.open(part, flags, dir_fd=descriptor)
            if not stat.S_ISDIR(os.fstat(child).st_mode):
                os.close(child)
                raise ReportError(
                    f"report path parent is not a directory: {path}"
                )
            os.close(descriptor)
            descriptor = child
        return descriptor
    except OSError as error:
        os.close(descriptor)
        raise ReportError(
            f"report directory path could not be opened safely: {path}"
        ) from error
    except Exception:
        os.close(descriptor)
        raise


def _read_regular_path_once(path: Path, *, label: str) -> bytes:
    absolute = Path(os.path.abspath(path))
    parent = _open_directory_path(absolute.parent)
    try:
        return _read_regular_at_once(parent, absolute.name, label=label)
    finally:
        os.close(parent)


def _read_regular_at_once(
    parent: int, name: str, *, label: str
) -> bytes:
    try:
        descriptor = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent,
        )
    except OSError as error:
        raise ReportError(f"{label} could not be opened safely: {name}") from error
    try:
        before = os.fstat(descriptor)
        _require(
            stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
            f"{label} is not an independent regular file: {name}",
        )
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            raw = handle.read()
        after = os.fstat(descriptor)
        identity = lambda value: (
            value.st_dev,
            value.st_ino,
            value.st_mode,
            value.st_nlink,
            value.st_size,
            value.st_mtime_ns,
            value.st_ctime_ns,
        )
        _require(
            len(raw) == before.st_size and identity(before) == identity(after),
            f"{label} changed during descriptor read: {name}",
        )
        return raw
    finally:
        os.close(descriptor)


def _input_record(path: Path) -> dict[str, Any]:
    absolute = Path(os.path.abspath(path))
    try:
        relative = absolute.relative_to(ROOT)
    except ValueError as error:
        raise ReportError(f"report input escapes G2 root: {path}") from error
    raw = _read_regular_path_once(absolute, label="report input")
    return {
        "path": relative.as_posix(),
        "size": len(raw),
        "sha256": _sha256_bytes(raw),
    }


def _bound_dual_input_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Bind every private receipt consumed by the dual-profile analyzer."""
    expected_records: list[dict[str, Any]] = []
    for profile in sorted(report["profiles"]):
        row = report["profiles"][profile]
        expected_records.extend(row["main_observation"]["observation_reports"])
        expected_records.append(row["boot_provider"]["report"])
        expected_records.append(row["package"]["package_report"])
        expected_records.append(row["package"]["flash_plan"])
    observed_by_path: dict[str, dict[str, Any]] = {}
    for expected in expected_records:
        _require(
            isinstance(expected, dict)
            and set(expected) == {"path", "size", "sha256"}
            and isinstance(expected["path"], str),
            "dual-profile direct input record is invalid",
        )
        observed = _input_record(ROOT / expected["path"])
        _require(
            observed == expected,
            f"dual-profile direct input identity changed: {expected['path']}",
        )
        previous = observed_by_path.get(observed["path"])
        _require(
            previous is None or previous == observed,
            f"dual-profile direct input metadata conflicts: {observed['path']}",
        )
        observed_by_path[observed["path"]] = observed
    return [observed_by_path[path] for path in sorted(observed_by_path)]


def _bound_touch_input_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Bind every regular G2 input authenticated by the Touch receipt."""
    try:
        receipt = report["components"]["touch"]["details"][
            "generation_receipt"]
        inputs = receipt["analysis_inputs"]
        expected = inputs["path_sha256"]
    except (KeyError, TypeError) as error:
        raise ReportError("Touch generation receipt is missing") from error
    _require(
        isinstance(expected, dict)
        and inputs.get("path_count") == 69 == len(expected)
        and list(expected) == sorted(expected),
        "Touch direct-input receipt is not canonical and complete",
    )
    observed_by_path: dict[str, dict[str, Any]] = {}
    for relative, digest in expected.items():
        _require(
            isinstance(relative, str) and isinstance(digest, str),
            "Touch direct-input receipt row is invalid",
        )
        observed = _input_record(ROOT / relative)
        _require(
            observed["path"] == relative and observed["sha256"] == digest,
            f"Touch direct input identity changed: {relative}",
        )
        previous = observed_by_path.get(relative)
        _require(
            previous is None or previous == observed,
            f"Touch direct input metadata conflicts: {relative}",
        )
        observed_by_path[relative] = observed
    return [observed_by_path[path] for path in sorted(observed_by_path)]


def _verify_direct_analyzer_import_closure() -> None:
    local_modules = {
        path.stem: path for path in (ROOT / "tools").glob("*.py")
    }
    for path in sorted(DIRECT_ANALYZER_INPUTS):
        try:
            tree = ast.parse(
                _read_regular_path_once(path, label="direct analyzer input").decode(
                    "utf-8"
                ),
                filename=str(path),
            )
        except (UnicodeDecodeError, SyntaxError) as error:
            raise ReportError(f"direct analyzer input is invalid: {path}") from error
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imports.add(node.module.split(".", 1)[0])
        missing = sorted(
            local_modules[module]
            for module in imports
            if module in local_modules
            and local_modules[module] not in DIRECT_ANALYZER_INPUTS
        )
        _require(
            not missing,
            f"completion direct analyzer import is unbound: {missing[0] if missing else ''}",
        )


def _atomic_write_output(path: Path, payload: bytes) -> None:
    absolute = Path(os.path.abspath(path))
    parent = _open_directory_path(absolute.parent, create=True)
    temporary_name = f".{absolute.name}.{secrets.token_hex(16)}.tmp"
    descriptor: int | None = None
    try:
        descriptor = os.open(
            temporary_name,
            os.O_RDWR
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0),
            0o644,
            dir_fd=parent,
        )
        with os.fdopen(descriptor, "w+b", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            handle.seek(0)
            _require(
                handle.read(len(payload) + 1) == payload,
                f"completion output temporary readback changed: {path}",
            )
        try:
            existing = os.open(
                absolute.name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=parent,
            )
        except FileNotFoundError:
            existing = None
        except OSError as error:
            raise ReportError(
                f"completion output could not be opened safely: {path}"
            ) from error
        if existing is not None:
            try:
                metadata = os.fstat(existing)
                _require(
                    stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1,
                    f"completion output is not an independent regular file: {path}",
                )
            finally:
                os.close(existing)
        os.replace(
            temporary_name,
            absolute.name,
            src_dir_fd=parent,
            dst_dir_fd=parent,
        )
        _require(
            _read_regular_at_once(
                parent, absolute.name, label="published completion output"
            ) == payload,
            f"published completion output changed: {path}",
        )
        os.fsync(parent)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            os.unlink(temporary_name, dir_fd=parent)
        except FileNotFoundError:
            pass
        os.close(parent)


def build_assessment() -> dict[str, Any]:
    """Translate the live audit into the public, lossless assessment schema."""
    _verify_direct_analyzer_import_closure()
    direct_inputs_before = [_input_record(path) for path in DIRECT_INPUTS]
    live = readiness.analyze()
    touch_input_records = _bound_touch_input_records(live)
    license_audit = licensing.analyze()
    license_summary = license_audit["summary"]
    _require(live["licensing"]["source_files"] == license_summary["source_files"],
             "completion and licensing audits disagree on source-file count")
    _require(live["licensing"]["source_errors"] == license_summary["source_errors"],
             "completion and licensing audits disagree on source errors")
    _require(
        live["licensing"]["unresolved_binary_authority"] ==
        license_summary["redistribution_authority_unresolved"],
        "completion and licensing audits disagree on binary authority",
    )

    try:
        base = json.loads(_read_regular_path_once(
            readiness.BASE_MANIFEST, label="base manifest"
        ).decode("utf-8"))
        core = json.loads(_read_regular_path_once(
            readiness.CORE_MANIFEST, label="core-source manifest"
        ).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReportError("completion manifest JSON is invalid") from error
    aggregate = deepcopy(live["aggregate"])
    components = []
    for component_id, component in live["components"].items():
        row = deepcopy(component)
        row["component_id"] = component_id
        row["component"] = COMPONENT_LABELS[component_id]
        _require(sum(row["buckets"].values()) == row["size"],
                 f"{component_id} public buckets do not conserve bytes")
        components.append(row)

    bucket_total = sum(aggregate["buckets"].values())
    _require(bucket_total == aggregate["component_payload_bytes"],
             "public aggregate buckets do not conserve component bytes")
    _require(bucket_total + aggregate["package_envelope_bytes"] ==
             aggregate["package_bytes"],
             "public package envelope does not conserve package bytes")

    touch = next(row for row in components if row["component_id"] == "touch")
    touch_detail = touch["details"]
    touch_admission = {
        "authoritative_batch": touch_detail["authoritative_batch"],
        "admission_batches": touch_detail["admission_batches"],
        "cumulative_candidate_instruction_bytes":
            touch_detail["cumulative_candidate_instruction_bytes"],
        "candidate_source_not_routed_bytes":
            touch["buckets"]["candidate_source_not_routed"],
        "remaining_unclassified_bytes": touch["buckets"]["unclassified"],
        "remaining_reachable_functions":
            touch_detail["reachable_unclassified_functions"],
        "remaining_application_contracts":
            touch_detail["unimplemented_application_contracts"],
        "production_routed": touch["production_routed"],
        "candidate_provenance": deepcopy(
            touch_detail["candidate_provenance"]),
        "candidate_provenance_manifest":
            touch_detail["candidate_provenance_manifest"],
        "generation_receipt_sha256":
            touch_detail["generation_receipt"]["generation_receipt_sha256"],
        "analysis_input_count":
            touch_detail["generation_receipt"]["analysis_inputs"]["path_count"],
    }

    source_inventory = license_audit["source_inventory"]
    license_counts = Counter(row["license"] for row in source_inventory)
    classification_counts = Counter(
        row["classification"] for row in source_inventory)
    binary_authority = [
        {
            "component_id": row["component"],
            "component": COMPONENT_LABELS[row["component"]],
            "redistribution_authority": row["redistribution_authority"],
            "source_availability": row["source_availability"],
            "reason": row["reason"],
        }
        for row in license_audit["artifacts"]
    ]

    gates = deepcopy(live["gates"])
    strict_source_complete = all(
        aggregate["buckets"][bucket] == 0
        for bucket in (
            "candidate_source_not_routed",
            "typed_retained_or_external",
            "unclassified",
        )
    )
    _require(
        gates["source_complete"] == strict_source_complete,
        "source-complete gate no longer matches its public definition",
    )
    _require(gates["hardware_validation"] == HARDWARE_STATUS,
             "hardware policy wording drifted")
    _require(gates["hardware_operations"] == [],
             "hardware operations appeared in the software-only audit")

    dual_report = dual_ownership.analyze()
    dual_input_records = _bound_dual_input_records(dual_report)
    companion_path = dual_ownership.COMPANION
    ownership_policy = dual_report.get("per_byte_ownership_policy", {})
    _require(ownership_policy == {
        "all_profiles_mask_complete": False,
        "sole_current_authority_profile": "apple-clang",
        "linux_per_byte_ownership_mask_complete": False,
        "qualification": (
            "Linux aggregate buckets and typed-mixed spans are exact, but no "
            "Linux per-byte source/generated/retained ownership is fabricated"
        ),
    }, "dual-profile per-byte ownership policy changed")
    dual_profiles: dict[str, Any] = {}
    for profile, profile_row in dual_report["profiles"].items():
        package = profile_row["package"]
        buckets = profile_row["aggregate_buckets"]
        _require(
            sum(buckets.values()) == package["component_payload_bytes"],
            f"{profile} dual-profile buckets do not conserve payload bytes",
        )
        _require(
            package["component_payload_bytes"]
            + package["outer_evenota_envelope_bytes"]
            == package["package_size"],
            f"{profile} dual-profile package does not conserve bytes",
        )
        mask_complete = profile_row.get("per_byte_ownership_mask_complete")
        _require(mask_complete is (profile == "apple-clang"),
                 f"{profile} per-byte ownership authority changed")
        _require(
            (not package["typed_mixed_profile_spans"] if mask_complete else
             len(package["typed_mixed_profile_spans"]) == 2),
            f"{profile} typed-mixed ownership boundary changed",
        )
        dual_profiles[profile] = {
            "package_size": package["package_size"],
            "package_sha256": package["package_sha256"],
            "component_payload_bytes": package["component_payload_bytes"],
            "physical_flash_bytes": package["physical_flash_bytes"],
            "internal_component_container_bytes":
                package["internal_component_container_bytes"],
            "outer_evenota_envelope_bytes":
                package["outer_evenota_envelope_bytes"],
            "package_report_sha256": package["package_report_sha256"],
            "flash_plan_sha256": package["flash_plan_sha256"],
            "aggregate_buckets": buckets,
            "per_byte_ownership_mask_complete": mask_complete,
            "per_byte_ownership_authority":
                profile_row["per_byte_ownership_authority"],
            "address_status_ownership_mode":
                package["address_status_ownership_mode"],
            "typed_mixed_profile_spans":
                package["typed_mixed_profile_spans"],
            "bytes_requiring_address_label_reconciliation":
                profile_row["apollo_flash_label_reconciliation"][
                    "bytes_requiring_reconciliation"
                ],
        }
    gates["dual_profile_ownership_reconciliation"] = True
    dual_profile_ownership = {
        "checked": True,
        "companion_schema_version": dual_report["schema_version"],
        "companion": companion_path.relative_to(ROOT).as_posix(),
        "companion_sha256": _sha256_file(companion_path),
        "analyzer": "tools/analyze_g2_dual_profile_ownership.py",
        "classification_policy": dual_report["classification_policy"],
        "per_byte_ownership_policy": deepcopy(
            dual_report["per_byte_ownership_policy"]),
        "source_inputs_sha256": dual_report["source_inputs_sha256"],
        "profiles": dual_profiles,
        "per_byte_ownership_mask_complete": False,
        "sole_current_per_byte_ownership_authority_profile": "apple-clang",
        "typed_mixed_boundary": "typed_mixed_profile_ownership",
        "limitation": (
            "Exact aggregate source/generated/candidate/retained/container totals "
            "are checked for both profiles, but the Linux coarse spans do not "
            "provide a complete per-byte source-vs-generated-vs-retained mask."
        ),
    }
    direct_inputs_after = [_input_record(path) for path in DIRECT_INPUTS]
    _require(
        direct_inputs_before == direct_inputs_after,
        "completion direct inputs changed during assessment",
    )
    _require(
        touch_input_records == _bound_touch_input_records(live),
        "Touch direct inputs changed during assessment",
    )
    source_inputs_by_path = {
        row["path"]: row for row in direct_inputs_after
    }
    for row in (*dual_input_records, *touch_input_records):
        previous = source_inputs_by_path.get(row["path"])
        _require(
            previous is None or previous == row,
            f"completion direct input metadata conflicts: {row['path']}",
        )
        source_inputs_by_path[row["path"]] = row

    return {
        "schema_version": 3,
        "assessment_date": "2026-08-28",
        "target": f"{base['target']} {base['package']['version']}",
        "generated_by": "tools/generate_g2_completion_report.py",
        "authoritative_audit": "tools/analyze_g2_completion_readiness.py",
        "analysis_mode": live["analysis_mode"],
        "hardware_validation": HARDWARE_STATUS,
        "hardware_operations": [],
        "definitions": {
            "production_source": (
                "Bytes emitted from maintained source and routed by the current "
                "production component build."
            ),
            "generated_or_reconstructible": (
                "Deterministic framing, patch, alignment, or format metadata; "
                "this does not imply recovered application behavior."
            ),
            "candidate_source_not_routed": (
                "Reviewed source candidate not used by the production provider."
            ),
            "typed_retained_or_external": (
                "A known retained, upstream, proprietary, or unsupported boundary; "
                "classification is not source ownership."
            ),
            "unclassified": "Bytes without a final source or boundary decision.",
            "classification_complete": (
                "Every byte has a source, generated, candidate, or typed-boundary "
                "decision. This is independent of source completion."
            ),
            "source_complete": (
                SOURCE_COMPLETE_DEFINITION
            ),
            "binary_redistribution_authority_resolved": (
                "A durable redistribution grant is recorded for every packaged "
                "binary. Source licensing does not establish this grant."
            ),
        },
        "package": {
            "format": base["package"]["format"],
            "expected_size": aggregate["package_bytes"],
            "expected_sha256": core["package"]["expected_sha256"],
            "component_payload_bytes": aggregate["component_payload_bytes"],
            "generated_envelope_bytes": aggregate["package_envelope_bytes"],
            "conservation": {
                "component_bucket_bytes": bucket_total,
                "component_buckets_plus_envelope_bytes":
                    bucket_total + aggregate["package_envelope_bytes"],
                "matches_expected_package_size": True,
            },
        },
        "components": components,
        "aggregate": aggregate,
        "touch_admission": touch_admission,
        "gates": gates,
        "dual_profile_ownership": dual_profile_ownership,
        "source_ownership_quality": live["source_ownership_quality"],
        "project_license_policy": live["project_license_policy"],
        "licensing": {
            "source_files": license_summary["source_files"],
            "source_errors": license_summary["source_errors"],
            "source_metadata_clean": license_summary["source_errors"] == 0,
            "source_license_counts": dict(sorted(license_counts.items())),
            "source_classification_counts":
                dict(sorted(classification_counts.items())),
            "binary_redistribution_authority": binary_authority,
            "unresolved_binary_authority":
                license_summary["redistribution_authority_unresolved"],
            "separation_rule": license_audit["separation_rule"],
        },
        "source_inputs": [
            source_inputs_by_path[path] for path in sorted(source_inputs_by_path)
        ],
    }


def _fmt_int(value: int) -> str:
    return f"{value:,}"


def _fmt_bool(value: bool) -> str:
    return "PASS" if value else "OPEN"


def _html_cell(value: Any) -> str:
    if isinstance(value, bool):
        value = "yes" if value else "no"
    return html.escape(str(value))


def build_html(assessment: dict[str, Any], assessment_sha256: str) -> bytes:
    """Render a compact, dependency-free report from the assessment data."""
    package = assessment["package"]
    aggregate = assessment["aggregate"]
    buckets = aggregate["buckets"]
    gates = assessment["gates"]
    component_rows = []
    for row in assessment["components"]:
        b = row["buckets"]
        component_rows.append(
            "<tr>"
            f"<th scope=\"row\">{_html_cell(row['component'])}</th>"
            f"<td>{_fmt_int(row['size'])}</td>"
            f"<td>{_fmt_int(b['production_source'])}</td>"
            f"<td>{_fmt_int(b['generated_or_reconstructible'])}</td>"
            f"<td>{_fmt_int(b['candidate_source_not_routed'])}</td>"
            f"<td>{_fmt_int(b['typed_retained_or_external'])}</td>"
            f"<td>{_fmt_int(b['unclassified'])}</td>"
            f"<td>{_fmt_int(row['release_blocking_bytes'])}</td>"
            f"<td>{_html_cell(row['classification_complete'])}</td>"
            f"<td>{_html_cell(row['source_complete'])}</td>"
            "</tr>"
        )
    bucket_rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{_html_cell(BUCKET_LABELS[key])}</th>"
        f"<td>{_fmt_int(value)}</td>"
        f"<td>{value / aggregate['component_payload_bytes']:.3%}</td>"
        "</tr>"
        for key, value in buckets.items()
    )
    gate_order = (
        "byte_accounting_complete",
        "classification_complete",
        "source_complete",
        "source_metadata_clean",
        "source_ownership_quality_clean",
        "project_license_policy_clean",
        "dual_profile_ownership_reconciliation",
        "binary_redistribution_authority_resolved",
        "release_authorized",
    )
    gate_rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{_html_cell(key.replace('_', ' '))}</th>"
        f"<td class=\"{('pass' if gates[key] else 'open')}\">"
        f"{_fmt_bool(gates[key])}</td>"
        "</tr>"
        for key in gate_order
    )
    license_rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{_html_cell(key)}</th>"
        f"<td>{_fmt_int(value)}</td>"
        "</tr>"
        for key, value in assessment["licensing"]["source_license_counts"].items()
    )
    authority_rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{_html_cell(row['component'])}</th>"
        f"<td>{_html_cell(row['redistribution_authority'])}</td>"
        f"<td>{_html_cell(row['source_availability'])}</td>"
        f"<td>{_html_cell(row['reason'])}</td>"
        "</tr>"
        for row in assessment["licensing"]["binary_redistribution_authority"]
    )
    input_rows = "".join(
        "<tr>"
        f"<th scope=\"row\"><code>{_html_cell(row['path'])}</code></th>"
        f"<td>{_fmt_int(row['size'])}</td>"
        f"<td><code>{_html_cell(row['sha256'])}</code></td>"
        "</tr>"
        for row in assessment["source_inputs"]
    )
    touch = assessment["touch_admission"]
    dual = assessment["dual_profile_ownership"]
    dual_rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{_html_cell(profile)}</th>"
        f"<td>{_fmt_int(row['package_size'])}</td>"
        f"<td><code>{_html_cell(row['package_sha256'])}</code></td>"
        f"<td>{_fmt_int(row['aggregate_buckets']['production_source'])}</td>"
        f"<td>{_fmt_int(row['aggregate_buckets']['generated_or_reconstructible'])}</td>"
        f"<td>{_fmt_int(row['aggregate_buckets']['candidate_source_not_routed'])}</td>"
        f"<td>{_fmt_int(row['aggregate_buckets']['typed_retained_or_external'])}</td>"
        f"<td>{_fmt_int(row['aggregate_buckets']['unclassified'])}</td>"
        f"<td>{_fmt_int(row['internal_component_container_bytes'])}</td>"
        f"<td>{_fmt_int(row['bytes_requiring_address_label_reconciliation'])}</td>"
        "</tr>"
        for profile, row in dual["profiles"].items()
    )
    definitions = "".join(
        f"<dt>{_html_cell(key.replace('_', ' '))}</dt>"
        f"<dd>{_html_cell(value)}</dd>"
        for key, value in assessment["definitions"].items()
    )

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>G2 openCFW completion assessment</title>
<style>
:root{{--ink:#18202a;--muted:#5c6875;--line:#d7dde4;--paper:#fff;--wash:#f5f7f9;--pass:#176b3a;--open:#9a3e19}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--wash);color:var(--ink);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1180px;margin:auto;padding:3rem 1.25rem 5rem}} h1{{font-size:2.25rem;margin:.1rem 0}} h2{{margin-top:2.4rem}}
.lede{{font-size:1.12rem;max-width:78ch}} .meta,.note{{color:var(--muted)}} .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1rem;margin:2rem 0}}
.card,section{{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:1rem 1.2rem}} section{{margin:1rem 0;overflow:auto}}
.card strong{{display:block;font-size:1.65rem}} table{{width:100%;border-collapse:collapse;min-width:720px}} th,td{{padding:.55rem .65rem;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}}
th:first-child,td:first-child{{text-align:left}} code{{font-size:.82em;overflow-wrap:anywhere}} dt{{font-weight:700;margin-top:.8rem}} dd{{margin:.15rem 0 .65rem}}
.pass{{color:var(--pass);font-weight:700}} .open{{color:var(--open);font-weight:700}} .warning{{border-left:5px solid var(--open)}}
</style>
</head>
<body><main data-assessment-sha256="{assessment_sha256}">
<p class="meta">Deterministic software-only snapshot · {assessment['assessment_date']}</p>
<h1>G2 openCFW completion assessment</h1>
<p class="lede">{_html_cell(assessment['target'])}. This report separates byte classification, production source completion, source-license metadata, and binary redistribution authority. Those are independent claims.</p>
<p><strong>Hardware validation: {_html_cell(assessment['hardware_validation'])}.</strong> Hardware operations recorded by this assessment: 0.</p>

<div class="cards">
<div class="card"><span>Package bytes</span><strong>{_fmt_int(package['expected_size'])}</strong><small>six payloads plus envelope</small></div>
<div class="card"><span>Production source</span><strong>{_fmt_int(buckets['production_source'])}</strong><small>{buckets['production_source']/aggregate['component_payload_bytes']:.3%} of payloads</small></div>
<div class="card"><span>Generated / reconstructible</span><strong>{_fmt_int(buckets['generated_or_reconstructible'])}</strong><small>component bytes; envelope separate</small></div>
<div class="card"><span>Unclassified</span><strong>{_fmt_int(buckets['unclassified'])}</strong><small>{len(aggregate['unclassified_components'])} components remain</small></div>
<div class="card"><span>Release-blocking payload</span><strong>{_fmt_int(aggregate['release_blocking_bytes'])}</strong><small>not a redistribution-authority measure</small></div>
</div>

<section class="warning"><h2>Current gate truth</h2>
<table><thead><tr><th>Gate</th><th>Status</th></tr></thead><tbody>{gate_rows}</tbody></table>
<p>Classification can pass while source completion remains open. Both can be independent of permission to redistribute retained vendor binaries. The release gate remains fail-closed.</p></section>

<section><h2>Exact component byte conservation</h2>
<table><thead><tr><th>Component</th><th>Bytes</th><th>Production source</th><th>Generated / reconstructible</th><th>Candidate, not routed</th><th>Typed retained / external</th><th>Unclassified</th><th>Release-blocking</th><th>Classified</th><th>Source complete</th></tr></thead>
<tbody>{''.join(component_rows)}</tbody></table>
<p class="note">Each component row sums exactly to its byte size. Component payloads total {_fmt_int(aggregate['component_payload_bytes'])}; the deterministic {_fmt_int(package['generated_envelope_bytes'])}-byte package envelope reconciles them to {_fmt_int(package['expected_size'])} bytes.</p></section>

<section><h2>Aggregate payload classes</h2>
<table><thead><tr><th>Class</th><th>Bytes</th><th>Payload share</th></tr></thead><tbody>{bucket_rows}</tbody></table></section>

<section><h2>Checked dual-profile ownership</h2>
<p>The Apple and Linux package reports, flash plans, admitted component receipts, and checked companion conserve exact aggregate ownership totals. Flash-plan ownership labels remain non-authoritative presentation boundaries.</p>
<table><thead><tr><th>Profile</th><th>Package bytes</th><th>Package SHA-256</th><th>Production source</th><th>Generated</th><th>Candidate</th><th>Retained / external</th><th>Unclassified</th><th>Internal container</th><th>Reconciled label bytes</th></tr></thead><tbody>{dual_rows}</tbody></table>
<p class="note">Internal container is an orthogonal location count already included in the ownership buckets, not an additional byte bucket. {_html_cell(dual['limitation'])} Checked companion: <code>{_html_cell(dual['companion'])}</code> (<code>{_html_cell(dual['companion_sha256'])}</code>).</p></section>

<section><h2>Touch candidate-admission chain</h2>
<p>Authoritative batch <strong>{touch['authoritative_batch']}</strong> closes a contiguous chain of {touch['admission_batches']} admission batches. Those batches add {_fmt_int(touch['cumulative_candidate_instruction_bytes'])} instruction bytes; the whole-image candidate bucket is {_fmt_int(touch['candidate_source_not_routed_bytes'])} bytes. It remains explicitly <strong>not production-routed</strong>.</p>
<p>{_fmt_int(touch['remaining_unclassified_bytes'])} Touch bytes, {touch['remaining_reachable_functions']} reachable functions, and {touch['remaining_application_contracts']} application contracts remain open in this snapshot.</p></section>

<section><h2>Definitions</h2><dl>{definitions}</dl></section>

<section><h2>Source-license metadata</h2>
<p>{_fmt_int(assessment['licensing']['source_files'])} unique overlay source files were audited with {assessment['licensing']['source_errors']} metadata errors.</p>
<table><thead><tr><th>SPDX license</th><th>Files</th></tr></thead><tbody>{license_rows}</tbody></table>
<p>{_html_cell(assessment['licensing']['separation_rule'])}.</p></section>

<section class="warning"><h2>Binary redistribution authority</h2>
<table><thead><tr><th>Component</th><th>Authority</th><th>Source availability</th><th>Reason</th></tr></thead><tbody>{authority_rows}</tbody></table></section>

<section><h2>Reproducible inputs</h2>
<p>Regenerate with <code>python3 g2/tools/generate_g2_completion_report.py</code>; verify without writes using <code>python3 g2/tools/generate_g2_completion_report.py --check</code>.</p>
<table><thead><tr><th>Ledger or analyzer</th><th>Bytes</th><th>SHA-256</th></tr></thead><tbody>{input_rows}</tbody></table></section>

<p class="meta">Assessment data SHA-256: <code>{assessment_sha256}</code>. No flashing, signing, publishing, MMIO, reset, DFU, or device interaction is performed by the generator.</p>
</main></body></html>
"""
    return document.encode("utf-8")


def build_outputs() -> dict[str, bytes]:
    assessment = build_assessment()
    assessment_bytes = _json_bytes(assessment)
    assessment_sha = _sha256_bytes(assessment_bytes)
    report_bytes = build_html(assessment, assessment_sha)
    artifact = {
        "schema_version": 3,
        "surface": "report",
        "title": "G2 openCFW Completion Assessment",
        "generator": "g2/tools/generate_g2_completion_report.py",
        "authoritative_audit": "g2/tools/analyze_g2_completion_readiness.py",
        "deterministic": True,
        "hardware_validation": HARDWARE_STATUS,
        "hardware_operations": [],
        "commands": {
            "generate": "python3 g2/tools/generate_g2_completion_report.py",
            "check": "python3 g2/tools/generate_g2_completion_report.py --check",
        },
        "files": {
            ASSESSMENT_NAME: {
                "size": len(assessment_bytes),
                "sha256": assessment_sha,
            },
            REPORT_NAME: {
                "size": len(report_bytes),
                "sha256": _sha256_bytes(report_bytes),
            },
        },
        "gate_snapshot": assessment["gates"],
        "dual_profile_ownership": {
            "checked": assessment["dual_profile_ownership"]["checked"],
            "companion": assessment["dual_profile_ownership"]["companion"],
            "companion_sha256": assessment["dual_profile_ownership"][
                "companion_sha256"
            ],
        },
    }
    return {
        ASSESSMENT_NAME: assessment_bytes,
        ARTIFACT_NAME: _json_bytes(artifact),
        REPORT_NAME: report_bytes,
    }


def write_outputs(output_dir: Path, *, check: bool) -> list[str]:
    outputs = build_outputs()
    stale = []
    output_dir = Path(os.path.abspath(output_dir))
    if check and not os.path.lexists(output_dir):
        return list(outputs)
    directory = _open_directory_path(output_dir, create=not check)
    os.close(directory)
    for name, content in outputs.items():
        path = output_dir / name
        if check:
            if not os.path.lexists(path) or _read_regular_path_once(
                path, label="committed completion output"
            ) != content:
                stale.append(name)
        else:
            _atomic_write_output(path, content)
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed report differs from live ledgers")
    parser.add_argument("--output-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args(argv)
    stale = write_outputs(args.output_dir, check=args.check)
    if stale:
        print("G2 completion assessment is stale: " + ", ".join(stale))
        return 2
    action = "verified" if args.check else "generated"
    print(f"G2 completion assessment {action}: {args.output_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReportError as exc:
        raise SystemExit(f"G2 completion report failed: {exc}") from exc
