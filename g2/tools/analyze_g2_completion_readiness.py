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
import json
from pathlib import Path
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
class AuditError(RuntimeError):
    """Raised when a component ledger stops conserving bytes."""


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def _sum(mapping: dict[str, int]) -> int:
    return sum(int(value) for value in mapping.values())


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
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_blocker": "blocked by unavailable physical evidence",
        "hardware_operations": [],
        "details": details,
    }


def analyze() -> dict[str, Any]:
    base = _read(BASE_MANIFEST)
    core = _read(CORE_MANIFEST)
    base_components = {row["name"]: row for row in base["components"]}
    main = _read(MAIN_REPORT)["component"]
    boot = _read(BOOT_REPORT)["component"]

    main_override = core["component_overrides"]["apollo_main"]["provider"]
    boot_override = core["component_overrides"]["apollo_bootloader"]["provider"]
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

    em = em9305_readiness.run_audit()
    em_residual = em["residual"]
    _require(em_residual["accounting_complete"] and
             em_residual["unclassified_bytes_after_decision"] == 0,
             "EM9305 retained residual is not exhaustively classified")
    _require(_sum(em_residual["readiness_bytes"]) == em_residual["bytes"],
             "EM9305 residual readiness does not conserve bytes")

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
             "blocked by unavailable physical evidence",
             "Touch source image hardware blocker changed")
    case_source_image = _read(CASE_SOURCE_IMAGE)
    _require(case_source_image.get("software_link_complete") is True,
             "Case source image is not link-complete")
    _require(case_source_image.get("software_package_complete") is True,
             "Case source package is not complete")
    _require(case_source_image.get("production_routed") is False,
             "Case source image unexpectedly claims production routing")
    _require(case_source_image.get("hardware_validation") ==
             "blocked by unavailable physical evidence",
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
             "blocked by unavailable physical evidence",
             "PT protocol hardware blocker changed")
    nemavg_caps = _read(NEMAVG_STROKE_CAPS)
    _require(nemavg_caps.get("status") ==
             "nemavg-stroke-caps-clean-room-candidate-qualified",
             "NemaVG stroke-cap candidate status changed")
    _require(nemavg_caps.get("hardware_validation") ==
             "blocked by unavailable physical evidence",
             "NemaVG stroke-cap hardware blocker changed")
    nemavg_cap_bytes = int(nemavg_caps["stock"]["physical_bytes"])
    _require(nemavg_caps["stock"]["functions"] == 3 and
             nemavg_cap_bytes == 6614 and
             nemavg_caps["candidate"]["semantic_c"] is True and
             nemavg_caps["candidate"]["production_routed"] is False,
             "NemaVG stroke-cap source admission changed")
    _require(nemavg_cap_bytes <= main["opaque_base_bytes"],
             "NemaVG stroke-cap admission exceeds Apollo retained bytes")
    clkmgr_dividers = _read(CLKMGR_DIVIDERS)
    _require(clkmgr_dividers.get("status") ==
             "apollo-clkmgr-divider-production-routed",
             "clock-manager divider production status changed")
    _require(clkmgr_dividers.get("hardware_validation") ==
             "blocked by unavailable physical evidence",
             "clock-manager divider hardware blocker changed")
    clkmgr_boot_bytes = int(clkmgr_dividers["stock"]["bootloader_bytes"])
    clkmgr_main_bytes = int(clkmgr_dividers["stock"]["apollo_main_bytes"])
    _require(clkmgr_dividers["stock"]["functions_per_image"] == 2 and
             clkmgr_boot_bytes == 52 and clkmgr_main_bytes == 52 and
             clkmgr_dividers["candidate"]["semantic_c"] is True and
             clkmgr_dividers["candidate"]["production_routed"] is True and
             clkmgr_dividers["candidate"]["software_blocker"] is None,
             "clock-manager divider production admission changed")
    _require(nemavg_cap_bytes <= main["opaque_base_bytes"],
             "Apollo-main candidate admission exceeds retained bytes")
    touch_metrics = touch["metrics"]
    touch_buckets = dict(touch_metrics["whole_blob_bucket_bytes"])
    _require(_sum(touch_buckets) == touch_metrics["whole_blob_bytes"],
             "touch readiness does not conserve bytes")
    touch_progress = _touch_admission_progress()
    touch_delta = touch_progress["cumulative_candidate_instruction_bytes"]
    if touch_current.get("classification_complete", False):
        touch_final = _read(TOUCH_FINAL)
        _require(touch_final.get("classification_complete") is True,
                 "Touch final frontier is not classification-complete")
        final_metrics = touch_final.get("metrics", {})
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
        touch_buckets = {key: int(value)
                         for key, value in final_buckets.items()}
    else:
        _require(touch_delta <= touch_buckets["still_unclassified"],
                 "Touch candidate admission exceeds the unclassified bucket")
        touch_buckets["project_source_candidate"] += touch_delta
        touch_buckets["still_unclassified"] -= touch_delta
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
    em_size = int(base_components["ble_em9305"]["provider"]["size"])
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
             pt_software["target_loadable_bytes"] == 20303 and
             pt_software["target_bss_bytes"] == 0 and
             pt_software["production_text_placement_free_bytes"] == 4314 and
             pt_software["production_text_placement_shortfall_bytes"] == 15989 and
             pt_software["production_ram_binding_remaining_bytes"] == 0 and
             pt_software["production_in_place_loadable_bytes"] == 20348 and
             pt_software["production_placement_complete"] is True,
             "PT protocol candidate is not source/link complete")
    _require(pt_software["production_routed"] is True,
             "PT protocol is not production-routed")
    pt_provider_candidate_bytes = int(
        pt_software["board_retained_provider_candidate_stock_body_bytes"])
    _require(
        pt_software["board_retained_provider_candidate_bindings"] == 40 and
        pt_software["board_top_level_retained_provider_bindings_remaining"] == 0 and
        pt_software["board_retained_provider_bindings_remaining"] == 23 and
        pt_provider_candidate_bytes == 3402 and
        pt_software["board_retained_provider_candidates_semantic_c"] is True and
        pt_software["board_retained_provider_candidates_production_routed"] is
        True and
        pt_software["board_retained_providers_source_owned"] is False and
        pt_software["board_source_complete"] is False and
        pt_software["board_second_order_callable_bindings"] == 60 and
        pt_software["board_second_order_source_overlay_callable_bindings"] == 21 and
        pt_software["board_second_order_source_local_callable_bindings"] == 16 and
        pt_software["board_second_order_retained_callable_bindings"] == 23 and
        pt_software["board_second_order_data_bindings"] == 46,
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
            candidate_source=nemavg_cap_bytes,
            typed_retained_or_external=(main["opaque_base_bytes"] -
                                        nemavg_cap_bytes),
            release_blocking=main["opaque_base_bytes"], production_routed=True,
            details={"origin_buckets": origin_buckets,
                     "provider_sha256": main["sha256"],
                     "nemavg_stroke_cap_candidate_functions":
                         nemavg_caps["stock"]["functions"],
                     "nemavg_stroke_cap_candidate_bytes": nemavg_cap_bytes,
                     "nemavg_stroke_cap_production_routed":
                         nemavg_caps["candidate"]["production_routed"],
                     "clkmgr_divider_candidate_functions":
                         clkmgr_dividers["stock"]["functions_per_image"],
                     "clkmgr_divider_candidate_bytes": clkmgr_main_bytes,
                     "clkmgr_divider_production_routed":
                         clkmgr_dividers["candidate"]["production_routed"],
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
                     "pt_protocol_second_order_retained_callable_bindings":
                         pt_software[
                             "board_second_order_retained_callable_bindings"],
                     "pt_protocol_second_order_data_bindings":
                         pt_software["board_second_order_data_bindings"],
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
                     "clkmgr_divider_candidate_functions":
                         clkmgr_dividers["stock"]["functions_per_image"],
                     "clkmgr_divider_candidate_bytes": clkmgr_boot_bytes,
                     "clkmgr_divider_production_routed":
                         clkmgr_dividers["candidate"]["production_routed"]}),
        "codec": _component(
            size=codec_size, generated_or_reconstructible=gx_reconstructible,
            typed_retained_or_external=gx_external + gx_unavailable,
            release_blocking=gx_external + gx_unavailable,
            production_routed=False,
            details={"typed_external_spans":
                         gx_ready["typed_unsupported_external_boundary"]["spans"],
                     "unavailable_proprietary_bytes": gx_unavailable}),
        "ble_em9305": _component(
            size=em_size, typed_retained_or_external=em_size,
            release_blocking=em_size, production_routed=False,
            details={"residual_scope_bytes": em_residual["bytes"],
                     "residual_readiness_bytes": em_residual["readiness_bytes"],
                     "residual_unclassified_bytes": 0}),
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
                     "admission_batches": touch_progress["admission_batches"],
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
                         touch_source_image["metrics"]["raw_flash_bytes"]}),
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
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": "blocked by unavailable physical evidence",
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
