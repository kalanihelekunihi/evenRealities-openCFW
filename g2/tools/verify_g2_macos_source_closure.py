#!/usr/bin/env python3
"""Verify the macOS source-only build and bind it to closure readiness."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_completion_readiness as completion_readiness
import analyze_g2_source_closure_blocker_index as source_closure
import verify_g2_apollo_am115_pullthrough_candidate as am115_pullthrough
import verify_g2_apollo_am142_pullthrough_candidate as am142_pullthrough
import verify_g2_apollo_am145_pullthrough_candidate as am145_pullthrough


SOURCE_ONLY_MANIFEST = "manifests/g2-2.2.6.10-source-only.json"
TOOLCHAIN_PROFILE = "apple-clang"
OUT = ROOT / "tools/manifests/g2-macos-source-closure-witness.json"
SHA_RE = re.compile(r"deterministic package SHA-256 ([0-9a-f]{64})")


def _verify_macos_build() -> dict:
    proc = subprocess.run(
        [
            sys.executable,
            "tools/open_cfw.py",
            "verify",
            "--manifest",
            SOURCE_ONLY_MANIFEST,
            "--toolchain-profile",
            TOOLCHAIN_PROFILE,
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    match = SHA_RE.search(proc.stdout)
    if not match:
        raise RuntimeError("macOS verifier output did not include package SHA-256")
    return {
        "manifest": SOURCE_ONLY_MANIFEST,
        "toolchain_profile": TOOLCHAIN_PROFILE,
        "verified": True,
        "deterministic_package_sha256": match.group(1),
        "stdout": proc.stdout.strip(),
    }


def analyze() -> dict:
    build = _verify_macos_build()
    readiness = completion_readiness.analyze()
    # Rebuild candidate receipts from the checked-out source before deriving
    # the closure frontier. The source-closure index consumes these receipts,
    # so reading saved reports here could hide source or toolchain drift.
    am_receipts = (
        (am115_pullthrough.OUT, am115_pullthrough.analyze()),
        (am142_pullthrough.OUT, am142_pullthrough.analyze()),
        (am145_pullthrough.OUT, am145_pullthrough.analyze()),
    )
    for receipt_path, receipt in am_receipts:
        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    closure = source_closure.analyze()
    gates = readiness["gates"]
    frontier_coverage = closure["frontier_coverage"]
    am142_receipt = closure["next_pull_through_frontier"][
        "apollo_retained_hot_target_frontier"][
            "source_pull_through_recovery_rollup"][
                "am142_target_compile_receipt"]
    am115_receipt = am_receipts[0][1]
    am145_receipt = am_receipts[2][1]
    requirements = {
        "macos_source_only_build_verified": {
            "satisfied": build["verified"],
            "evidence": build["deterministic_package_sha256"],
        },
        "apollo_am115_pullthrough_candidate_target_compiles": {
            "satisfied": (
                am115_receipt["target_compile_verified"]
                and am115_receipt["toolchain_profile"] == TOOLCHAIN_PROFILE
                and am115_receipt["undefined_symbols"] == []
            ),
            "evidence": am115_receipt,
        },
        "apollo_am142_pullthrough_candidate_target_compiles": {
            "satisfied": (
                am142_receipt["available"]
                and am142_receipt["target_compile_verified"]
                and am142_receipt["toolchain_profile"] == TOOLCHAIN_PROFILE
            ),
            "evidence": am142_receipt,
        },
        "apollo_am145_pullthrough_candidate_target_compiles": {
            "satisfied": (
                am145_receipt["target_compile_verified"]
                and am145_receipt["toolchain_profile"] == TOOLCHAIN_PROFILE
                and am145_receipt["undefined_symbols"] == []
            ),
            "evidence": am145_receipt,
        },
        "classification_complete": {
            "satisfied": gates["classification_complete"],
            "evidence": readiness["aggregate"]["unclassified_components"],
        },
        "all_release_blocking_components_have_explicit_frontier": {
            "satisfied": frontier_coverage[
                "all_release_blocking_components_have_frontier"],
            "evidence": frontier_coverage["components"],
        },
        "source_complete": {
            "satisfied": gates["source_complete"],
            "evidence": readiness["aggregate"]["source_incomplete_components"],
        },
        "source_ownership_quality_clean": {
            "satisfied": gates["source_ownership_quality_clean"],
            "evidence": readiness["source_ownership_quality"],
        },
        "release_authorized": {
            "satisfied": gates["release_authorized"],
            "evidence": {
                "release_blocking_bytes": readiness["aggregate"][
                    "release_blocking_bytes"],
                "global_blockers": closure["global_blockers"],
                "next_remediation": closure["remediation_queue"][0],
            },
        },
    }
    return {
        "schema_version": 1,
        "macos_build": build,
        "requirements": requirements,
        "release_authorized": gates["release_authorized"],
        "classification_complete": gates["classification_complete"],
        "source_complete": gates["source_complete"],
        "source_ownership_quality_clean": gates[
            "source_ownership_quality_clean"],
        "project_license_policy_clean": gates["project_license_policy_clean"],
        "release_blocking_bytes": readiness["aggregate"][
            "release_blocking_bytes"],
        "source_owned_bytes_currently_overstated": readiness[
            "source_ownership_quality"][
                "source_owned_bytes_currently_overstated"],
        "closure_frontier": closure["next_pull_through_frontier"],
        "frontier_coverage": frontier_coverage,
        "remediation_queue": closure["remediation_queue"],
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "macos_build_verified": report["macos_build"]["verified"],
        "deterministic_package_sha256": report["macos_build"][
            "deterministic_package_sha256"],
        "release_authorized": report["release_authorized"],
        "release_blocking_bytes": report["release_blocking_bytes"],
        "apollo_am142_pullthrough_target_compiles": report["requirements"][
            "apollo_am142_pullthrough_candidate_target_compiles"][
                "satisfied"],
        "apollo_am142_pullthrough_object_sha256": report["requirements"][
            "apollo_am142_pullthrough_candidate_target_compiles"][
                "evidence"]["object_sha256"],
        "apollo_am115_pullthrough_target_compiles": report["requirements"][
            "apollo_am115_pullthrough_candidate_target_compiles"][
                "satisfied"],
        "apollo_am115_pullthrough_object_sha256": report["requirements"][
            "apollo_am115_pullthrough_candidate_target_compiles"][
                "evidence"]["object_sha256"],
        "apollo_am145_pullthrough_target_compiles": report["requirements"][
            "apollo_am145_pullthrough_candidate_target_compiles"][
                "satisfied"],
        "apollo_am145_pullthrough_object_sha256": report["requirements"][
            "apollo_am145_pullthrough_candidate_target_compiles"][
                "evidence"]["object_sha256"],
        "frontier_coverage_complete": report["requirements"][
            "all_release_blocking_components_have_explicit_frontier"][
                "satisfied"],
        "next_remediation": report["remediation_queue"][0]["scope"],
        "source_complete": report["source_complete"],
        "source_ownership_quality_clean": report[
            "source_ownership_quality_clean"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
