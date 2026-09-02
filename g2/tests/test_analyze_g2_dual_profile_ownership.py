#!/usr/bin/env python3
from __future__ import annotations

# SPDX-License-Identifier: MIT

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
import os
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_dual_profile_ownership.py"
sys.path.insert(0, str(ROOT / "tools"))
import open_cfw  # noqa: E402
EVIDENCE = (
    ROOT / "build/canonical-observation/apple-a/build-report.json",
    ROOT / "build/canonical-observation/apple-b/build-report.json",
    ROOT / "build/canonical-observation/linux-a/build-report.json",
    ROOT / "build/canonical-observation/linux-b/build-report.json",
    ROOT / "components/bootloader/core_overlay/build/build-report.json",
    ROOT / "build/canonical-provider/linux-clang/apollo_bootloader/build-report.json",
    ROOT / "build/postapply-package-apple/build-report.json",
    ROOT / "build/postapply-package-apple/flash-plan.json",
    ROOT / "build/postapply-package-linux/build-report.json",
    ROOT / "build/postapply-package-linux/flash-plan.json",
)


class DualProfileReleaseGateLinkageTests(unittest.TestCase):
    def test_community_distribution_requires_checked_dual_profile_ownership(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        prerequisites = makefile.split(
            "community-distribution-gate:", 1
        )[1].split("\n\tPYTHONDONTWRITEBYTECODE", 1)[0]
        prerequisite_tokens = prerequisites.replace("\\\n", " ").split()
        self.assertIn("dual-profile-ownership", prerequisite_tokens)
        self.assertNotIn("dual-profile-ownership-write", prerequisite_tokens)
        self.assertIn("completion-assessment: dual-profile-ownership", makefile)
        self.assertIn(
            "completion-assessment-check: dual-profile-ownership", makefile
        )
        self.assertIn(
            "dual-profile-ownership-write:\n"
            "\tPYTHONDONTWRITEBYTECODE=1 $(PYTHON) \\\n"
            "\t\ttools/analyze_g2_dual_profile_ownership.py --write-companion",
            makefile,
        )

        root_makefile = (ROOT.parent / "Makefile").read_text(encoding="utf-8")
        self.assertIn("\ndual-profile-ownership:\n", root_makefile)
        self.assertIn(
            "$(MAKE) -C $(G2_DIR) dual-profile-ownership", root_makefile
        )
        self.assertIn("\ndual-profile-ownership-write:\n", root_makefile)

    def test_core_companion_pointer_is_exact_identity_scoped(self):
        components = []
        rows = []
        for index, name in enumerate(sorted(open_cfw.REQUIRED_RELEASE_COMPONENTS)):
            source = name in open_cfw.DUAL_PROFILE_OWNERSHIP_COMPONENTS
            components.append({
                "name": name,
                "provider": {"kind": "source_build" if source else "official_blob"},
                "source_appended_boundary": 0,
            })
            if source:
                rows.append({
                    "component": name,
                    "component_file_offset": 0,
                    "size": index + 1,
                })
        manifest = {"target": "Even Realities G2", "components": components}
        common = {
            "manifest": manifest,
            "package_artifact": "package.bin",
            "flash_regions": rows,
            "unresolved": [],
            "container": [],
        }
        for profile in ("apple-clang", "linux-clang"):
            exact = open_cfw.make_flash_plan(
                **common,
                manifest_id={
                    "sha256": open_cfw.DUAL_PROFILE_OWNERSHIP_MANIFESTS[profile],
                    "sources": [],
                },
                toolchain_profile=profile,
                package_sha256=open_cfw.DUAL_PROFILE_OWNERSHIP_PACKAGES[profile],
            )
            self.assertEqual(
                exact["address_status_semantics"]
                ["authoritative_ownership_companion"],
                "tools/manifests/g2-dual-profile-ownership.json",
            )
            stale = open_cfw.make_flash_plan(
                **common,
                manifest_id={"sha256": "0" * 64, "sources": []},
                toolchain_profile=profile,
                package_sha256=open_cfw.DUAL_PROFILE_OWNERSHIP_PACKAGES[profile],
            )
            semantics = stale["address_status_semantics"]
            self.assertIsNone(semantics["authoritative_ownership_companion"])
            self.assertIn("unreconciled", semantics["ownership_labels"])


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_dual_profile_ownership", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DualProfileObservationIndependenceTests(unittest.TestCase):
    ARTIFACT_KEYS = (
        "overlay", "component", "core_stage_overlay", "core_stage_component",
        "liblc3_payload", "liblc3_component",
    )

    def test_default_observation_paths_match_the_documented_workflow(self):
        analyzer = load_analyzer()
        expected = {
            "apple-clang": (
                ROOT / "build/canonical-observation/apple-a/build-report.json",
                ROOT / "build/canonical-observation/apple-b/build-report.json",
            ),
            "linux-clang": (
                ROOT / "build/canonical-observation/linux-a/build-report.json",
                ROOT / "build/canonical-observation/linux-b/build-report.json",
            ),
        }
        self.assertEqual(analyzer.OBSERVATIONS, expected)
        self.assertEqual(
            EVIDENCE[:4],
            (*expected["apple-clang"], *expected["linux-clang"]),
        )

        documented = (
            ROOT / "docs/community-source-distribution.md"
        ).read_text(encoding="utf-8")
        linux_documented = (
            ROOT / "docs/linux-reproducible-build.md"
        ).read_text(encoding="utf-8")
        for path in (*expected["apple-clang"], *expected["linux-clang"]):
            relative = path.relative_to(ROOT).as_posix()
            self.assertIn(relative, documented)
            self.assertIn(relative, linux_documented)
        self.assertNotIn(".tmp-canonical-observations", documented)

    @staticmethod
    def _identity(path: Path) -> tuple[int, int, int, int, int]:
        metadata = path.stat()
        return (
            metadata.st_dev,
            metadata.st_ino,
            metadata.st_size,
            metadata.st_mtime_ns,
            metadata.st_ctime_ns,
        )

    def _observation(self, root: Path, name: str) -> tuple[dict, dict[str, Path]]:
        paths: dict[str, Path] = {}
        for role in ("report", *self.ARTIFACT_KEYS):
            path = root / f"{name}-{role}.bin"
            path.write_bytes(f"{name}/{role}\n".encode("ascii"))
            paths[role] = path
        return {
            "report_identity": self._identity(paths["report"]),
            "artifact_identities": {
                role: self._identity(paths[role]) for role in self.ARTIFACT_KEYS
            },
        }, paths

    def test_all_four_independence_precedes_readiness_and_other_evidence(self):
        analyzer = load_analyzer()
        pairs = {
            profile: ({"run": f"{profile}-a"}, {"run": f"{profile}-b"})
            for profile in ("apple-clang", "linux-clang")
        }
        events: list[str] = []

        def admit(_paths, profile):
            events.append(f"admit:{profile}")
            return pairs[profile]

        def reject(observations):
            events.append("validate")
            self.assertEqual(
                observations,
                (*pairs["apple-clang"], *pairs["linux-clang"]),
            )
            raise analyzer.canonical_admission.AdmissionError(
                "globally distinct inodes required"
            )

        with (
            mock.patch.object(
                analyzer.canonical_admission,
                "admit_reproducible_pair",
                side_effect=admit,
            ),
            mock.patch.object(
                analyzer.canonical_admission,
                "validate_observation_independence",
                side_effect=reject,
            ),
            mock.patch.object(analyzer.readiness, "analyze") as readiness,
            mock.patch.object(analyzer, "_read") as read,
            mock.patch.object(analyzer, "_boot") as boot,
            mock.patch.object(analyzer, "_package") as package,
        ):
            with self.assertRaisesRegex(
                analyzer.OwnershipError, "canonical observation evidence"
            ):
                analyzer._observed()

        self.assertEqual(
            events,
            ["admit:apple-clang", "admit:linux-clang", "validate"],
        )
        readiness.assert_not_called()
        read.assert_not_called()
        boot.assert_not_called()
        package.assert_not_called()

    def test_cross_profile_hardlink_alias_fails_before_readiness(self):
        analyzer = load_analyzer()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            records_and_paths = [
                self._observation(root, name)
                for name in ("apple-a", "apple-b", "linux-a", "linux-b")
            ]
            records = [item[0] for item in records_and_paths]
            paths = [item[1] for item in records_and_paths]

            linux_overlay = paths[2]["overlay"]
            linux_overlay.unlink()
            os.link(paths[0]["overlay"], linux_overlay)
            records[2]["artifact_identities"]["overlay"] = self._identity(
                linux_overlay
            )

            with (
                mock.patch.object(
                    analyzer.canonical_admission,
                    "admit_reproducible_pair",
                    side_effect=[
                        (records[0], records[1]),
                        (records[2], records[3]),
                    ],
                ),
                mock.patch.object(analyzer.readiness, "analyze") as readiness,
            ):
                with self.assertRaisesRegex(
                    analyzer.OwnershipError, "globally distinct inodes"
                ):
                    analyzer._observed()
            readiness.assert_not_called()


class DualProfileNemaVGBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = load_analyzer()
        self.details = {
            "nemavg_stroke_cap_candidate_functions": 0,
            "nemavg_stroke_cap_candidate_bytes": 0,
            "nemavg_stroke_cap_source_routed_functions": 3,
            "nemavg_stroke_cap_source_routed_stock_bytes": 6614,
            "nemavg_stroke_cap_retained_unpatched_functions": 0,
            "nemavg_stroke_cap_retained_unpatched_stock_bytes": 0,
            "nemavg_stroke_cap_coordinator_production_routed": True,
            "nemavg_stroke_cap_endpoint_stock_entries_unpatched": False,
            "nemavg_stroke_cap_production_routed": True,
        }

    def test_complete_boundary_is_exact_and_non_additive(self):
        boundary = self.analyzer._nemavg_boundary(self.details)
        self.assertEqual(boundary, self.analyzer.NEMAVG_COORDINATOR_BOUNDARY)
        self.assertEqual(boundary["stock_functions"], 3)
        self.assertEqual(boundary["stock_physical_bytes"], 6614)
        self.assertEqual(boundary["source_routed_functions"], 3)
        self.assertEqual(boundary["source_routed_stock_bytes"], 6614)
        self.assertEqual(boundary["retained_unpatched_functions"], 0)
        self.assertEqual(boundary["retained_unpatched_stock_bytes"], 0)
        self.assertEqual(boundary["candidate_source_not_routed_functions"], 0)
        self.assertEqual(boundary["candidate_source_not_routed_bytes"], 0)
        self.assertIn("all three", boundary["ownership_accounting"])

    def test_partial_route_or_false_endpoint_state_fails_closed(self):
        variants = []
        partial_route = copy.deepcopy(self.details)
        partial_route.update({
            "nemavg_stroke_cap_candidate_functions": 2,
            "nemavg_stroke_cap_candidate_bytes": 3308,
            "nemavg_stroke_cap_source_routed_functions": 1,
            "nemavg_stroke_cap_source_routed_stock_bytes": 3306,
            "nemavg_stroke_cap_retained_unpatched_functions": 2,
            "nemavg_stroke_cap_retained_unpatched_stock_bytes": 3308,
            "nemavg_stroke_cap_endpoint_stock_entries_unpatched": True,
            "nemavg_stroke_cap_production_routed": False,
        })
        variants.append(partial_route)
        patched_endpoint = copy.deepcopy(self.details)
        patched_endpoint["nemavg_stroke_cap_endpoint_stock_entries_unpatched"] = True
        variants.append(patched_endpoint)
        falsely_retained_only = copy.deepcopy(self.details)
        falsely_retained_only["nemavg_stroke_cap_candidate_functions"] = 2
        falsely_retained_only["nemavg_stroke_cap_candidate_bytes"] = 3308
        variants.append(falsely_retained_only)
        missing_boundary = copy.deepcopy(self.details)
        missing_boundary.pop("nemavg_stroke_cap_retained_unpatched_stock_bytes")
        variants.append(missing_boundary)

        for details in variants:
            with self.subTest(details=details):
                with self.assertRaisesRegex(
                    self.analyzer.OwnershipError,
                    "NemaVG|invalid integer",
                ):
                    self.analyzer._nemavg_boundary(details)


@unittest.skipUnless(all(path.is_file() for path in EVIDENCE),
                     "admitted dual-profile evidence is unavailable")
class DualProfileOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_checked_companion_conserves_both_profiles(self):
        expected = {
            "apple-clang": {
                "production_source": 475527,
                "generated_or_reconstructible": 494744,
                "candidate_source_not_routed": 29396,
                "typed_retained_or_external": 3749965,
                "unclassified": 0,
            },
            "linux-clang": {
                "production_source": 257897,
                "generated_or_reconstructible": 411980,
                "candidate_source_not_routed": 29396,
                "typed_retained_or_external": 4050343,
                "unclassified": 0,
            },
        }
        for profile, buckets in expected.items():
            row = self.report["profiles"][profile]
            self.assertEqual(row["aggregate_buckets"], buckets)
            self.assertEqual(
                sum(buckets.values()), row["package"]["component_payload_bytes"]
            )
            self.assertEqual(
                row["package"]["component_payload_bytes"]
                + row["package"]["outer_evenota_envelope_bytes"],
                row["package"]["package_size"],
            )
            self.assertEqual(row["package"]["internal_component_container_bytes"], 300)
            self.assertEqual(row["package"]["outer_evenota_envelope_bytes"], 944)

    def test_apple_is_the_only_current_per_byte_ownership_authority(self):
        policy = self.report["per_byte_ownership_policy"]
        self.assertFalse(policy["all_profiles_mask_complete"])
        self.assertEqual(policy["sole_current_authority_profile"], "apple-clang")
        self.assertFalse(policy["linux_per_byte_ownership_mask_complete"])
        apple = self.report["profiles"]["apple-clang"]
        linux = self.report["profiles"]["linux-clang"]
        self.assertTrue(apple["per_byte_ownership_mask_complete"])
        self.assertFalse(linux["per_byte_ownership_mask_complete"])
        self.assertEqual(apple["package"]["typed_mixed_profile_spans"], [])
        self.assertEqual(len(linux["package"]["typed_mixed_profile_spans"]), 3)
        self.assertIn("aggregate totals", linux["per_byte_ownership_authority"])

    def test_linux_profile_coarse_label_error_is_not_accepted(self):
        row = self.report["profiles"]["linux-clang"]
        reconciliation = row["apollo_flash_label_reconciliation"]
        self.assertEqual(reconciliation["bytes_requiring_reconciliation"], 274414)
        self.assertEqual(
            reconciliation["plan_minus_authoritative"],
            {
                "source": 274414,
                "generated_addressed": -1936,
                "retained": -272478,
                "component_container_metadata": 0,
            },
        )
        self.assertEqual(
            row["package"]["address_status_ownership_mode"],
            "non_authoritative_profile_coarse",
        )
        spans = row["package"]["typed_mixed_profile_spans"]
        self.assertEqual([item["classification"] for item in spans],
                         ["typed_mixed_profile_ownership"] * 3)
        self.assertEqual([item["component"] for item in spans],
                         ["ble_em9305", "apollo_bootloader", "apollo_main"])

    def test_apple_stale_labels_also_require_checked_reconciliation(self):
        row = self.report["profiles"]["apple-clang"]
        self.assertEqual(
            row["apollo_flash_label_reconciliation"]
            ["bytes_requiring_reconciliation"],
            17800,
        )
        self.assertEqual(
            row["package"]["address_status_ownership_mode"],
            "non_authoritative_requires_checked_reconciliation",
        )

    def test_tampered_companion_fails_closed(self):
        checked = self.analyzer._read(self.analyzer.COMPANION)
        tampered = copy.deepcopy(checked)
        tampered["profiles"]["linux-clang"]["aggregate_buckets"][
            "typed_retained_or_external"
        ] -= 1
        with tempfile.TemporaryDirectory(dir=ROOT, prefix=".tmp-dual-companion-") as temporary:
            path = Path(temporary) / "ownership.json"
            path.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaisesRegex(
                self.analyzer.OwnershipError, "companion is stale"
            ):
                self.analyzer.analyze(path)

    def test_atomic_companion_write_is_current_and_canonical(self):
        with tempfile.TemporaryDirectory(
            dir=ROOT, prefix=".tmp-dual-companion-write-"
        ) as temporary:
            path = Path(temporary) / "ownership.json"
            path.write_text('{"stale":true}\n', encoding="utf-8")
            old_inode = path.stat().st_ino
            record = self.analyzer.write_companion(self.report, path)
            expected = self.analyzer._companion_payload(self.report)
            self.assertEqual(path.read_bytes(), expected)
            self.assertEqual(record["size"], len(expected))
            self.assertEqual(
                record["sha256"],
                self.analyzer.hashlib.sha256(expected).hexdigest(),
            )
            self.assertNotEqual(path.stat().st_ino, old_inode)
            self.assertEqual(self.analyzer.analyze(path), self.report)

    def test_companion_write_failure_preserves_existing_bytes(self):
        with tempfile.TemporaryDirectory(
            dir=ROOT, prefix=".tmp-dual-companion-failure-"
        ) as temporary:
            path = Path(temporary) / "ownership.json"
            original = b'{"preserve":true}\n'
            path.write_bytes(original)
            with mock.patch.object(
                self.analyzer.canonical_admission,
                "atomic_write",
                side_effect=OSError("injected write failure"),
            ):
                with self.assertRaisesRegex(
                    self.analyzer.OwnershipError, "cannot write ownership companion"
                ):
                    self.analyzer.write_companion(self.report, path)
            self.assertEqual(path.read_bytes(), original)

    def test_companion_write_rejects_redirected_and_multiply_linked_targets(self):
        with tempfile.TemporaryDirectory(
            dir=ROOT, prefix=".tmp-dual-companion-unsafe-"
        ) as temporary:
            directory = Path(temporary)
            target = directory / "target.json"
            target.write_text('{"preserve":true}\n', encoding="utf-8")

            symlink = directory / "symlink.json"
            symlink.symlink_to(target.name)
            with self.assertRaisesRegex(
                self.analyzer.OwnershipError, "symlink"
            ):
                self.analyzer.write_companion(self.report, symlink)

            hardlink = directory / "hardlink.json"
            os.link(target, hardlink)
            with self.assertRaisesRegex(
                self.analyzer.OwnershipError, "hard link"
            ):
                self.analyzer.write_companion(self.report, hardlink)

            real_parent = directory / "real"
            real_parent.mkdir()
            redirected_parent = directory / "redirected"
            redirected_parent.symlink_to(real_parent.name, target_is_directory=True)
            with self.assertRaisesRegex(
                self.analyzer.OwnershipError, "parent contains a symlink"
            ):
                self.analyzer.write_companion(
                    self.report, redirected_parent / "ownership.json"
                )

        with tempfile.TemporaryDirectory() as outside:
            with self.assertRaisesRegex(
                self.analyzer.OwnershipError, "escapes the G2 tree"
            ):
                self.analyzer.write_companion(
                    self.report, Path(outside) / "ownership.json"
                )

    def test_default_cli_is_read_only_and_write_route_is_explicit(self):
        with (
            mock.patch.object(
                self.analyzer, "analyze", return_value=self.report
            ) as analyze,
            mock.patch.object(self.analyzer, "write_companion") as writer,
        ):
            self.assertEqual(self.analyzer.main([]), 0)
            analyze.assert_called_once_with(
                self.analyzer.COMPANION, verify_companion=True
            )
            writer.assert_not_called()

        record = {"path": "tools/manifests/test.json", "size": 1,
                  "sha256": "0" * 64}
        with (
            mock.patch.object(
                self.analyzer, "analyze", side_effect=[self.report, self.report]
            ) as analyze,
            mock.patch.object(
                self.analyzer, "write_companion", return_value=record
            ) as writer,
        ):
            self.assertEqual(self.analyzer.main(["--write-companion"]), 0)
            self.assertEqual(
                analyze.call_args_list,
                [
                    mock.call(self.analyzer.COMPANION, verify_companion=False),
                    mock.call(self.analyzer.COMPANION),
                ],
            )
            writer.assert_called_once_with(self.report, self.analyzer.COMPANION)

    def test_current_source_closure_change_fails_closed(self):
        current = self.analyzer.canonical_admission.current_source_input_report()
        changed = copy.deepcopy(current)
        changed["entries"][0]["size"] += 1
        with mock.patch.object(
            self.analyzer.canonical_admission,
            "current_source_input_report",
            return_value=changed,
        ):
            with self.assertRaisesRegex(
                self.analyzer.OwnershipError, "stale for current source inputs"
            ):
                self.analyzer.analyze()

    def test_malformed_source_receipt_cannot_use_len_as_schema(self):
        pair = self.analyzer.canonical_admission.admit_reproducible_pair(
            list(self.analyzer.OBSERVATIONS["apple-clang"]), "apple-clang"
        )
        malformed = copy.deepcopy(pair)
        for receipt in malformed:
            receipt["observation"]["source_inputs"]["entries"] = "x" * 879
            receipt["report"]["canonical_observation"] = receipt["observation"]
        with mock.patch.object(
            self.analyzer.canonical_admission,
            "admit_reproducible_pair",
            return_value=malformed,
        ):
            with self.assertRaisesRegex(
                self.analyzer.OwnershipError, "entry count changed"
            ):
                self.analyzer._canonical_main("apple-clang")

    def test_artifacts_reject_absolute_traversal_symlink_and_hardlink_paths(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix=".tmp-dual-path-") as temporary:
            directory = Path(temporary)
            payload = b"proof\n"
            source = directory / "source.bin"
            source.write_bytes(payload)
            record = {
                "artifact": source.name,
                "size": len(payload),
                "sha256": self.analyzer.hashlib.sha256(payload).hexdigest(),
            }
            self.assertEqual(
                self.analyzer._artifact(directory, record, "test artifact")["size"],
                len(payload),
            )
            for unsafe in (str(source), "../source.bin"):
                with self.assertRaisesRegex(
                    self.analyzer.OwnershipError, "safe relative path"
                ):
                    self.analyzer._artifact(
                        directory, {**record, "artifact": unsafe}, "test artifact"
                    )
            symlink = directory / "symlink.bin"
            symlink.symlink_to(source.name)
            with self.assertRaisesRegex(self.analyzer.OwnershipError, "symlink"):
                self.analyzer._artifact(
                    directory, {**record, "artifact": symlink.name}, "test artifact"
                )
            hardlink = directory / "hardlink.bin"
            os.link(source, hardlink)
            with self.assertRaisesRegex(self.analyzer.OwnershipError, "hard link"):
                self.analyzer._artifact(
                    directory, {**record, "artifact": hardlink.name}, "test artifact"
                )

    def test_checked_projection_binds_receipts_and_all_six_provider_identities(self):
        checked = self.analyzer._read(self.analyzer.COMPANION)
        self.assertEqual(checked["schema_version"], 4)
        self.assertEqual(
            checked["per_byte_ownership_policy"],
            self.report["per_byte_ownership_policy"],
        )
        for profile, row in checked["profiles"].items():
            self.assertEqual(len(row["main_observation"]["observation_reports"]), 2)
            self.assertEqual(set(row["package"]["providers"]),
                             self.analyzer.COMPONENT_IDS)
            self.assertIn("report", row["boot_provider"])
            self.assertIn("report", row["em9305_provider"])
            self.assertIn("package_report", row["package"])
            self.assertIn("flash_plan", row["package"])
            self.assertEqual(
                row["nemavg_stroke_cap_boundary"],
                self.analyzer.NEMAVG_COORDINATOR_BOUNDARY,
            )
            self.assertEqual(
                row["per_byte_ownership_mask_complete"],
                profile == "apple-clang",
            )
            self.assertEqual(
                row["per_byte_ownership_authority"],
                self.report["profiles"][profile]
                    ["per_byte_ownership_authority"],
            )

    def test_checked_policy_omission_or_drift_fails_closed(self):
        checked = self.analyzer._read(self.analyzer.COMPANION)
        variants = []
        missing = copy.deepcopy(checked)
        missing.pop("per_byte_ownership_policy")
        variants.append(missing)
        drifted = copy.deepcopy(checked)
        drifted["profiles"]["linux-clang"][
            "per_byte_ownership_mask_complete"
        ] = True
        variants.append(drifted)
        with mock.patch.object(
            self.analyzer, "_observed", return_value=self.report
        ):
            for variant in variants:
                with self.subTest(keys=sorted(variant)):
                    with tempfile.TemporaryDirectory(
                        dir=ROOT, prefix=".tmp-dual-policy-"
                    ) as temporary:
                        path = Path(temporary) / "ownership.json"
                        path.write_text(json.dumps(variant), encoding="utf-8")
                        with self.assertRaisesRegex(
                            self.analyzer.OwnershipError,
                            "companion is stale",
                        ):
                            self.analyzer.analyze(path)

    def test_missing_or_duplicate_package_provider_fails_before_conservation(self):
        root = self.analyzer.PACKAGE_DIRS["apple-clang"]
        build = json.loads((root / "build-report.json").read_text())
        plan = json.loads((root / "flash-plan.json").read_text())
        build["providers"].pop()
        records = [
            {"path": "build/postapply-package-apple/build-report.json",
             "size": 1, "sha256": "0" * 64},
            {"path": "build/postapply-package-apple/flash-plan.json",
             "size": 1, "sha256": "0" * 64},
        ]
        with (
            mock.patch.object(
                self.analyzer,
                "_read_with_record",
                side_effect=[(build, records[0]), (plan, records[1])],
            ),
            mock.patch.object(self.analyzer, "_artifact"),
        ):
            with self.assertRaisesRegex(
                self.analyzer.OwnershipError, "exact six providers"
            ):
                self.analyzer._package("apple-clang")

    def test_analysis_does_not_bootstrap_from_completion_assessment(self):
        with tempfile.TemporaryDirectory() as temporary:
            absent = Path(temporary) / "missing-assessment-data.json"
            with mock.patch.object(
                self.analyzer, "ASSESSMENT", absent, create=True
            ):
                self.assertEqual(self.analyzer.analyze(), self.report)

    def test_plan_semantics_forbid_per_byte_ownership_inference(self):
        for profile, directory in self.analyzer.PACKAGE_DIRS.items():
            plan = json.loads((directory / "flash-plan.json").read_text())
            semantics = plan["address_status_semantics"]
            self.assertEqual(
                semantics["authoritative_ownership_companion"],
                "tools/manifests/g2-dual-profile-ownership.json",
            )
            self.assertNotEqual(semantics["ownership_labels"], "authoritative")
            self.assertEqual(semantics["address_and_artifact_mapping"],
                             "authoritative")
            self.assertEqual(plan["unresolved_flash_regions"], [])

    def test_binary_authority_and_hardware_boundary_remain_explicit(self):
        self.assertFalse(self.report["gates"]["release_authorized"])
        self.assertFalse(
            self.report["gates"]["binary_redistribution_authority_resolved"]
        )
        self.assertEqual(
            self.report["gates"]["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(self.report["gates"]["hardware_operations"], [])
        self.assertEqual(len(self.report["unresolved_binary_authority"]), 6)


if __name__ == "__main__":
    unittest.main()
