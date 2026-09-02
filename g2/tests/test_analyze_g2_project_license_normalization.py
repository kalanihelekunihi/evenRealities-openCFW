# SPDX-License-Identifier: MIT
"""Tests for MIT-where-possible project source policy."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/analyze_g2_project_license_normalization.py"
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location("g2_project_license_policy", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RootPolicyProjectCensusStaticTests(unittest.TestCase):
    def test_root_policy_project_census_is_exact_and_mit_authenticated(self) -> None:
        rows = MODULE._root_policy_project_rows()
        self.assertEqual(
            MODULE.EXPECTED_ROOT_POLICY_MEMBERS,
            {
                "CODE_OF_CONDUCT.md",
                "CONTRIBUTING.md",
                "SECURITY.md",
                "SUPPORT.md",
            },
        )
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            MODULE.EXPECTED_ROOT_POLICY_CENSUS_DIGEST,
            "3b907b120819ed924d98487c658a02ea9300423ab2348700fe08b05b061f99a8",
        )
        for row in rows:
            self.assertEqual(row["license"], "MIT")
            self.assertEqual(
                row["basis"], "authenticated-root-mit-ownership-scope")
            self.assertEqual(
                (row["license_evidence"]["size"],
                 row["license_evidence"]["sha256"]),
                MODULE.ROOT_MIT_LICENSE_IDENTITY,
            )

    def test_root_policy_census_rejects_non_root_or_mutated_members(self) -> None:
        expanded = dict(MODULE.ROOT_POLICY_PROJECT_FILES)
        expanded["../README.md"] = expanded["SUPPORT.md"]
        with mock.patch.object(MODULE, "ROOT_POLICY_PROJECT_FILES", expanded):
            with self.assertRaisesRegex(
                    MODULE.AuditError, "member census changed"):
                MODULE._root_policy_project_rows()

        mutated = dict(MODULE.ROOT_POLICY_PROJECT_FILES)
        size, digest = mutated["SUPPORT.md"]
        mutated["SUPPORT.md"] = (size, "0" * len(digest))
        with mock.patch.object(MODULE, "ROOT_POLICY_PROJECT_FILES", mutated):
            with self.assertRaisesRegex(
                    MODULE.AuditError, "identity changed: SUPPORT.md"):
                MODULE._root_policy_project_rows()


class ProjectLicenseNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.analyze()

    def test_exact_project_owned_census_is_normalized_mit(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["project_owned_normalization_targets"], 460)
        self.assertEqual(metrics["project_owned_records_normalized_mit"], 460)
        self.assertEqual(metrics["project_owned_gpl_records_pending_mit"], 0)
        self.assertEqual(metrics["project_owned_gpl_only_pending"], 0)
        self.assertEqual(metrics["project_owned_gpl_or_later_pending"], 0)
        self.assertEqual(metrics["expected_mit_records_after_normalization"], 647)
        self.assertEqual(metrics["repository_only_project_mit_files"], 1)
        self.assertEqual(
            metrics["distributed_upstream_gpl_files_preserved"], 1)
        self.assertEqual(
            metrics["distributed_project_mit_normalization_targets"], 919)
        self.assertEqual(metrics["root_policy_project_mit_files"], 4)
        self.assertEqual(
            metrics["root_policy_project_mit_census_sha256"],
            "3b907b120819ed924d98487c658a02ea9300423ab2348700fe08b05b061f99a8",
        )
        self.assertEqual(
            metrics["distributed_unique_project_files_pending_normalization"],
            0)
        self.assertEqual(
            metrics["distributed_project_gpl_spdx_files_pending_mit"],
            metrics["distributed_gpl_spdx_files"] - 1)
        self.assertGreaterEqual(
            metrics["dual_mit_or_gpl_files_already_permit_mit"], 1)
        self.assertTrue(self.result["normalization_complete"])

    def test_every_overlay_target_is_mit_without_upstream(self) -> None:
        self.assertEqual(self.result["pending_rows"], [])
        self.assertEqual(len(self.result["rows"]), 460)
        for row in self.result["rows"]:
            self.assertEqual(row["upstream_record"], "absent")
            self.assertEqual(row["desired_license"], "MIT")
            self.assertTrue(row["source_sha256"])

    def test_real_upstream_licenses_are_preserved(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["upstream_gpl_records_preserved"], 1)
        self.assertEqual(metrics["apache_records_preserved"], 81)
        self.assertEqual(metrics["bsd_records_preserved"], 134)
        self.assertEqual(metrics["isc_records_preserved"], 0)
        self.assertEqual(metrics["zlib_records_preserved"], 27)
        self.assertTrue(all(row["upstream"]
                            for row in self.result["preserved_upstream_gpl"]))
        self.assertEqual(
            {row["path"] for row in self.result["preserved_upstream_gpl"]},
            {"components/apollo_main/ring_gesture/ring_gesture.c"})

    def test_stock_imu_boundary_keeps_repository_source_mit_but_not_public(self) -> None:
        path = "g2/components/apollo_main/core_overlay/imu_icm45608.c"
        self.assertEqual(self.result["repository_only_project_paths"], [path])
        self.assertNotIn(path, MODULE._path_manifest(MODULE.SCOPE_PATHS))
        self.assertIn(path, MODULE._path_manifest(MODULE.ADDITIONAL_PATHS))
        row = next(
            item for item in self.result["rows"]
            if item["path"] == path.removeprefix("g2/")
        )
        self.assertEqual(row["source_spdx"], "MIT")
        self.assertEqual(row["components"], "repository-only-research")
        self.assertEqual(
            row["overlay_license"], "not-compiled-stock-donor-boundary")
        self.assertEqual(row["disposition"], "normalized")

    def test_policy_is_software_only(self) -> None:
        self.assertEqual(self.result["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.result["hardware_blocker"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.result["production_files_modified"], [])

    def test_dual_license_census_is_limited_to_public_project_targets(self) -> None:
        self.assertEqual(
            set(self.result["dual_mit_or_gpl_paths"]),
            {
                "components/shared/touch/runtime_touch_i2c_protocol.c",
                "components/shared/touch/runtime_touch_i2c_protocol.h",
                "components/shared/touch/runtime_touch_sensing.c",
                "components/shared/touch/runtime_touch_sensing.h",
            },
        )

    def test_distributed_census_includes_tools_tests_and_fixtures(self) -> None:
        targets = {row["path"] for row in self.result["distributed_rows"]}
        self.assertTrue(any(path.startswith("g2/tests/") for path in targets))
        self.assertTrue(any(path.startswith("g2/tools/") for path in targets))
        self.assertTrue(any(path.startswith("g2/components/") for path in targets))
        self.assertNotIn(
            "g2/components/apollo_main/ring_gesture/ring_gesture.c", targets)
        self.assertIn(
            "g2/components/apollo_main/core_overlay/"
            "evenhub_lz4_upstream_adapter.c", targets)
        self.assertTrue(
            {
                "g2/tools/apply_g2_canonical_observations.py",
                "g2/tests/test_apply_g2_canonical_observations.py",
            }
            <= targets
        )
        self.assertTrue(
            {
                "g2/community/Makefile",
                "g2/community/make.sh",
                "g2/docs/community-archive-README.md",
                "g2/tests/test_community_markdown_link_closure.py",
            }
            <= targets
        )

    def test_root_policy_docs_inherit_only_the_exact_root_mit_license(self) -> None:
        self.assertEqual(
            set(self.result["root_policy_project_paths"]),
            MODULE.EXPECTED_ROOT_POLICY_MEMBERS,
        )
        distributed = {row["path"]: row
                       for row in self.result["distributed_rows"]}
        for evidence in self.result["root_policy_project_rows"]:
            with self.subTest(path=evidence["path"]):
                row = distributed[evidence["path"]]
                self.assertTrue(row["mit_asserted"])
                self.assertFalse(row["gpl_asserted"])
                self.assertEqual(
                    row["mit_basis"],
                    "authenticated-root-mit-ownership-scope",
                )
                self.assertEqual(row["sha256"], evidence["sha256"])
                self.assertEqual(row["disposition"], "normalized")

    def test_community_controller_and_build_adapter_census_is_exact(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["community_controller_and_adapter_source_files"], 112)
        self.assertEqual(metrics["community_project_mit_compatible_source_files"], 109)
        self.assertEqual(metrics["community_touch_apache_source_files_preserved"], 3)

        project_paths = set(self.result["community_project_paths"])
        apache_paths = set(self.result["community_touch_apache_paths"])
        self.assertEqual(
            apache_paths,
            {
                "g2/components/shared/touch/runtime_touch_cat2_adapters.c",
                "g2/components/shared/touch/runtime_touch_cat2_adapters.h",
                "g2/components/shared/touch/runtime_touch_critical_adapters.S",
            },
        )
        self.assertIn(
            "g2/components/apollo_main/core_overlay/build_component.py",
            project_paths,
        )
        self.assertIn(
            "g2/components/apollo_main/liblc3_ltpf/build_component.py",
            project_paths,
        )
        self.assertIn(
            "g2/components/shared/touch/runtime_touch_unsigned_division.c",
            project_paths,
        )
        self.assertIn(
            "g2/components/shared/touch/runtime_touch_unsigned_division.h",
            project_paths,
        )
        self.assertIn(
            "g2/components/shared/touch/runtime_touch_memory_runtime.c",
            project_paths,
        )
        self.assertIn(
            "g2/components/shared/case/runtime_case_semantic_leaves.c",
            project_paths,
        )
        self.assertIn(
            "g2/components/shared/case/runtime_case_semantic_leaves.h",
            project_paths,
        )
        self.assertIn(
            "g2/components/shared/case/runtime_case_pure_helpers.c",
            project_paths,
        )
        self.assertIn(
            "g2/components/shared/case/runtime_case_pure_helpers.h",
            project_paths,
        )
        distributed = {row["path"]: row for row in self.result["distributed_rows"]}
        for path in project_paths:
            with self.subTest(path=path):
                self.assertTrue(distributed[path]["mit_asserted"])
                self.assertEqual(distributed[path]["disposition"], "normalized")

    def test_touch_source_image_distribution_census_is_exact(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["touch_source_image_project_mit_files"], 9)
        self.assertEqual(metrics["touch_source_image_package_files"], 6)
        self.assertEqual(metrics["touch_source_image_support_files"], 3)
        paths = set(self.result["touch_source_image_paths"])
        self.assertEqual(
            paths,
            {
                "g2/components/touch/source_image/README.md",
                "g2/components/touch/source_image/build_image.py",
                "g2/components/touch/source_image/firmware_image.c",
                "g2/components/touch/source_image/firmware_image.h",
                "g2/components/touch/source_image/linker.ld",
                "g2/components/touch/source_image/startup.c",
                "g2/tests/test_analyze_g2_touch_source_image.py",
                "g2/tests/test_touch_source_image.py",
                "g2/tools/analyze_g2_touch_source_image.py",
            },
        )
        distributed = {row["path"]: row for row in self.result["distributed_rows"]}
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(distributed[path]["mit_asserted"])
                self.assertEqual(distributed[path]["disposition"], "normalized")

    def test_case_source_image_distribution_census_is_exact(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["case_source_image_project_mit_files"], 7)
        self.assertEqual(metrics["case_source_image_package_files"], 5)
        self.assertEqual(metrics["case_source_image_support_files"], 2)
        paths = set(self.result["case_source_image_paths"])
        self.assertEqual(
            paths,
            {
                "g2/components/case/source_image/README.md",
                "g2/components/case/source_image/build_image.py",
                "g2/components/case/source_image/compiler_runtime.c",
                "g2/components/case/source_image/linker.ld",
                "g2/components/case/source_image/startup.c",
                "g2/tests/test_analyze_g2_case_source_image.py",
                "g2/tools/analyze_g2_case_source_image.py",
            },
        )
        distributed = {row["path"]: row for row in self.result["distributed_rows"]}
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(distributed[path]["mit_asserted"])
                self.assertFalse(distributed[path]["gpl_asserted"])
                self.assertEqual(distributed[path]["disposition"], "normalized")

    def test_em9305_source_image_distribution_census_is_exact(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["em9305_source_image_project_mit_files"], 19)
        self.assertEqual(metrics["em9305_source_image_package_files"], 11)
        self.assertEqual(metrics["em9305_source_image_support_files"], 8)
        paths = set(self.result["em9305_source_image_paths"])
        self.assertEqual(paths, {
            "g2/components/em9305/source_image/README.md",
            "g2/components/em9305/source_image/build_image.py",
            "g2/components/em9305/source_image/record_package.py",
            "g2/components/em9305/source_overlay/README.md",
            "g2/components/em9305/source_overlay/build_overlay.py",
            "g2/components/em9305/source_overlay/reconstructible_tail.ld",
            "g2/components/em9305/source_overlay/runtime_metaware.c",
            "g2/components/em9305/source_overlay/runtime_metaware.h",
            "g2/components/em9305/source_overlay/runtime_metaware_entries.c",
            "g2/components/em9305/source_overlay/runtime_reconstructible_tail.c",
            "g2/components/em9305/source_overlay/runtime_reconstructible_tail_entries.c",
            "g2/tests/fixtures/em9305_reconstructible_tail_host.c",
            "g2/tests/test_analyze_em9305_record_package.py",
            "g2/tests/test_em9305_record_package.py",
            "g2/tests/test_em9305_reconstructible_tail_overlay.py",
            "g2/tests/test_runtime_em9305_metaware_production.py",
            "g2/tests/test_runtime_em9305_reconstructible_tail.py",
            "g2/tools/analyze_em9305_record_package.py",
            "g2/tools/integrate_g2_em9305_source_overlay.py",
        })
        distributed = {row["path"]: row for row in self.result["distributed_rows"]}
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(distributed[path]["mit_asserted"])
                self.assertFalse(distributed[path]["gpl_asserted"])
                self.assertEqual(distributed[path]["disposition"], "normalized")

    def test_pt_protocol_public_source_census_is_exact(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["pt_protocol_project_mit_files"], 28)
        self.assertEqual(
            metrics["pt_protocol_upstream_apache_files_preserved"], 1
        )
        paths = set(self.result["pt_protocol_project_paths"])
        apache_paths = set(
            self.result["pt_protocol_upstream_apache_paths"]
        )
        self.assertEqual(apache_paths, MODULE.PT_PROTOCOL_APACHE_PATHS)
        expected_all = {
            "g2/components/apollo_main/core_overlay/" + path.name
            for path in (ROOT / "components/apollo_main/core_overlay").glob(
                "pt_protocol*")
            if path.suffix in {".c", ".h"}
        }
        expected = expected_all - apache_paths
        self.assertEqual(len(expected_all), 29)
        self.assertEqual(len(expected), 28)
        self.assertEqual(paths, expected)
        self.assertTrue(apache_paths.isdisjoint(paths))
        apache_source = ROOT.parent / next(iter(apache_paths))
        apache_text = apache_source.read_text()
        self.assertEqual(
            apache_text.count("SPDX-License-Identifier: Apache-2.0"), 1
        )
        self.assertIn("Copyright 2022 Google LLC", apache_text)
        distributed = {row["path"]: row
                       for row in self.result["distributed_rows"]}
        for path in apache_paths:
            self.assertNotIn(path, distributed)
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(distributed[path]["mit_asserted"])
                self.assertFalse(distributed[path]["gpl_asserted"])
                self.assertEqual(distributed[path]["disposition"], "normalized")

    def test_project_source_prose_has_no_stale_gpl_claims(self) -> None:
        boot_notice = (
            ROOT / "components/bootloader/core_overlay/NOTICE.md"
        ).read_text()
        component_readme = (ROOT / "components/README.md").read_text()
        self.assertNotRegex(boot_notice, r"GPL-3\.0-(?:only|or-later)")
        self.assertNotRegex(component_readme, r"GPL-3\.0-(?:only|or-later)")

        allowed_research = {
            "em9305-qpc-arcompact-audit.md",
            "g2-project-license-normalization-audit.md",
            "g2-touch-i2c-source-closure.md",
            "g2-touch-project-license-readiness.md",
            "g2-touch-sensing-source-closure.md",
            "g2-touch-software-readiness-ledger.md",
        }
        remaining = {
            path.name for path in (ROOT / "docs/research").glob("*.md")
            if re.search(r"GPL-3\.0-(?:only|or-later)", path.read_text())
        }
        self.assertEqual(remaining, allowed_research)

        stale_claim = re.compile(
            r"(clean[- ]room|first-party|openCFW).{0,120}GPL-3|"
            r"GPL-3.{0,120}(clean[- ]room|first-party|openCFW)",
            re.IGNORECASE,
        )
        prose_paths = (
            ROOT / "components/apollo_main/core_overlay/NOTICE.md",
            ROOT / "components/apollo_main/core_overlay/EVIDENCE.md",
            ROOT / "components/shared/lvgl/README.md",
            ROOT / "docs/progress.md",
            ROOT / "docs/source-coverage.md",
            ROOT / "docs/upstream-inventory.md",
        )
        offenders = {
            path.relative_to(ROOT).as_posix(): stale_claim.findall(
                path.read_text())
            for path in prose_paths if stale_claim.search(path.read_text())
        }
        self.assertEqual(offenders, {})


if __name__ == "__main__":
    unittest.main()
