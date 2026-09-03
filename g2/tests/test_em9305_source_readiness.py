#!/usr/bin/env python3

from __future__ import annotations

import copy
import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_em9305_source_readiness.py"


def load_analyzer():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location("analyze_em9305_source_readiness", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load EM9305 source-readiness analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Em9305SourceReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.rows = cls.analyzer.load_residual_rows()
        cls.meta = cls.analyzer.metaware.run_audit()
        cls.first = cls.analyzer.first_party.run_audit()
        cls.tail = cls.analyzer.tail.run_audit()
        cls.hook_provider = cls.analyzer.qpc_hook_provider.run_audit()
        cls.slave_connection = cls.analyzer.slave_connection.run_audit()
        cls.pawr = cls.analyzer.pawr.run_audit()
        cls.master_connection = cls.analyzer.master_connection.run_audit()
        cls.qpc = cls.analyzer.qpc.analyze()
        cls.result = cls.analyzer.compose_reports(
            cls.rows, cls.meta, cls.first, cls.tail, cls.hook_provider,
            cls.slave_connection, cls.pawr, cls.master_connection, cls.qpc,
        )

    def test_gate_accounts_every_residual_span_and_byte(self) -> None:
        result = self.result
        self.assertEqual(result["status"], "accounting-complete-source-incomplete")
        self.assertTrue(result["read_only"])
        self.assertEqual(result["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(result["hardware_operations"], [])
        self.assertFalse(result["source_complete"])
        self.assertFalse(result["release"])
        residual = result["residual"]
        self.assertEqual(residual["span_count"], 175)
        self.assertEqual(residual["bytes"], 33_658)
        self.assertEqual(residual["accounted_spans"], 175)
        self.assertEqual(residual["accounted_bytes"], 33_658)
        self.assertEqual(residual["unclassified_spans_after_decision"], 0)
        self.assertEqual(residual["unclassified_bytes_after_decision"], 0)
        self.assertTrue(residual["accounting_complete"])
        self.assertFalse(residual["source_complete"])

    def test_three_readiness_states_are_exact_and_sum_to_census(self) -> None:
        residual = self.result["residual"]
        self.assertEqual(
            residual["readiness_segment_counts"],
            {
                "concrete_source_available": 23,
                "typed_unsupported_external_boundary": 25,
                "unavailable_proprietary_controller_code": 127,
            },
        )
        self.assertEqual(
            residual["readiness_bytes"],
            {
                "concrete_source_available": 1_240,
                "typed_unsupported_external_boundary": 8_348,
                "unavailable_proprietary_controller_code": 24_070,
            },
        )
        self.assertEqual(sum(residual["readiness_segment_counts"].values()), 175)
        self.assertEqual(sum(residual["readiness_bytes"].values()), 33_658)

    def test_completion_mapping_routes_concrete_source_and_keeps_retained_boundary(self) -> None:
        mapping = self.result["completion_bucket_mapping"]
        self.assertEqual(mapping["component_bytes"], 212_984)
        self.assertEqual(mapping["buckets"], {
            "production_source": 1_174,
            "generated_or_reconstructible": 1_226,
            "candidate_source_not_routed": 0,
            "typed_retained_or_external": 210_584,
            "unclassified": 0,
        })
        self.assertTrue(mapping["candidate_production_routed"])
        self.assertEqual(mapping["release_blocking_bytes"], 210_584)

    def test_metaware_arc_target_compile_and_production_route_are_durable(self) -> None:
        audit = self.result["metaware_runtime_audit"]
        self.assertFalse(audit["additive_to_residual_accounting"])
        self.assertEqual(audit["status"], "production-routed")
        self.assertEqual(audit["candidate_source_bytes"], 980)
        self.assertTrue(audit["arcv2_em_target_compiled"])
        self.assertEqual(audit["arcv2_em_undefined_symbols"], [])
        self.assertEqual(audit["arcv2_em_forbidden_runtime_imports"], [])
        self.assertEqual(
            audit["arcv2_em_build_receipt"],
            "tools/manifests/em9305-arc-candidate-build-summary.json",
        )
        self.assertTrue(audit["candidate_production_routed"])
        self.assertEqual(audit["remaining_software_blockers"], [])
        self.assertEqual(
            audit["hardware_validation"],
            "blocked by unavailable physical evidence",
        )

    def test_ledger_intervals_and_hashes_match_authenticated_rows(self) -> None:
        ledger = self.result["residual"]["ledger"]
        self.assertEqual(len(ledger), len(self.rows))
        for row, item in zip(self.rows, ledger):
            self.assertEqual(
                (item["start"], item["end"], item["size"], item["sha256"]),
                (row["start"], row["end"], row["size"], row["sha256"]),
            )
            self.assertEqual(item["end"] - item["start"], item["size"])
            self.assertIn(item["readiness"], self.analyzer.READINESS_STATES)

    def test_checked_final_manifests_are_current_and_schema_exact(self) -> None:
        self.assertEqual(
            self.analyzer.check_manifests(self.result),
            [self.analyzer.FINAL_LEDGER, self.analyzer.FINAL_SUMMARY],
        )
        ledger_payload = self.analyzer.FINAL_LEDGER.read_bytes()
        lines = ledger_payload.decode("utf-8").splitlines()
        self.assertEqual(lines[0], "# SPDX-License-Identifier: MIT")
        rows = list(csv.DictReader(lines[1:], delimiter="\t"))
        self.assertEqual(len(rows), 175)
        self.assertEqual(
            set(rows[0]),
            {
                "start", "end", "size", "sha256", "readiness",
                "decision", "decision_origin",
            },
        )
        self.assertEqual(sum(int(row["size"]) for row in rows), 33_658)
        self.assertTrue(all(row["decision"] and row["decision_origin"]
                            for row in rows))

        summary = json.loads(self.analyzer.FINAL_SUMMARY.read_text())
        self.assertEqual(summary["schema_version"], 7)
        self.assertEqual(summary["residual_span_count"], 175)
        self.assertEqual(summary["residual_bytes"], 33_658)
        self.assertEqual(summary["unclassified_spans"], 0)
        self.assertEqual(summary["unclassified_bytes"], 0)
        self.assertEqual(summary["ledger"], {
            "path": "em9305-final-source-readiness.tsv",
            "size": len(ledger_payload),
            "sha256": self.analyzer.sha256(ledger_payload),
        })

    def test_final_summary_conserves_readiness_and_completion_buckets(self) -> None:
        summary = json.loads(self.analyzer.FINAL_SUMMARY.read_text())
        self.assertEqual(summary["readiness_segment_counts"], {
            "concrete_source_available": 23,
            "typed_unsupported_external_boundary": 25,
            "unavailable_proprietary_controller_code": 127,
        })
        self.assertEqual(summary["readiness_bytes"], {
            "concrete_source_available": 1_240,
            "typed_unsupported_external_boundary": 8_348,
            "unavailable_proprietary_controller_code": 24_070,
        })
        self.assertEqual(sum(summary["readiness_segment_counts"].values()), 175)
        self.assertEqual(sum(summary["readiness_bytes"].values()), 33_658)
        self.assertEqual(summary["completion_buckets"], {
            "production_source": 1_174,
            "generated_or_reconstructible": 1_226,
            "candidate_source_not_routed": 0,
            "typed_retained_or_external": 210_584,
            "unclassified": 0,
        })
        self.assertEqual(sum(summary["completion_buckets"].values()), 212_984)

    def test_final_summary_hardware_and_release_shape_is_fail_closed(self) -> None:
        summary = json.loads(self.analyzer.FINAL_SUMMARY.read_text())
        self.assertFalse(summary["source_complete"])
        self.assertFalse(summary["release"])
        self.assertTrue(summary["candidate_production_routed"])
        self.assertEqual(summary["release_blocking_bytes"], 210_584)
        self.assertEqual(
            summary["hardware_validation"], "blocked by unavailable physical evidence",
        )
        self.assertEqual(summary["hardware_operations"], [])
        self.assertEqual(
            summary["metaware_runtime_audit"],
            self.result["metaware_runtime_audit"],
        )
        self.assertEqual(
            summary["qpc_supporting_audit"],
            self.result["qpc_supporting_audit"],
        )
        self.assertEqual(
            summary["qpc_hook_provider_audit"],
            self.result["qpc_hook_provider_audit"],
        )
        self.assertEqual(
            summary["deployment_package_audit"],
            self.result["deployment_package_audit"],
        )

    def test_deployment_package_routes_mixed_provider_without_source_complete_claim(self) -> None:
        audit = self.result["deployment_package_audit"]
        self.assertFalse(audit["additive_to_residual_accounting"])
        self.assertEqual(
            audit["status"],
            "mixed-provider-production-routed-source-incomplete",
        )
        self.assertEqual(audit["record_count"], 4)
        self.assertEqual(audit["erase_sector_count"], 29)
        self.assertTrue(audit["stock_roundtrip_byte_exact"])
        self.assertTrue(audit["software_wrapper_complete"])
        self.assertTrue(audit["software_package_complete"])
        self.assertFalse(audit["source_records_complete"])
        self.assertFalse(audit["source_image_complete"])
        self.assertTrue(audit["production_routed"])
        self.assertEqual(audit["remaining_software_blockers"], [])
        self.assertEqual(audit["remaining_source_completeness_blockers"], [
            "210584 typed retained or external provider bytes require unavailable exact provider source and redistribution authority",
        ])
        self.assertEqual(audit["provider_size"], 212_984)
        self.assertEqual(
            audit["provider_sha256"],
            "1a4ccc61cae6e9b90d0eb3d694179d726c935171788167d28ea45060d7431c42",
        )
        self.assertEqual(audit["hardware_operations"], [])
        self.assertEqual(
            audit["hardware_validation"],
            "blocked by unavailable physical evidence",
        )

    def test_manifest_mutation_and_stale_result_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="em9305-final-manifest-test-"
        ) as raw_temporary:
            temporary = Path(raw_temporary)
            ledger = temporary / self.analyzer.FINAL_LEDGER.name
            summary = temporary / self.analyzer.FINAL_SUMMARY.name
            with (
                mock.patch.object(self.analyzer, "MANIFEST_DIR", temporary),
                mock.patch.object(self.analyzer, "FINAL_LEDGER", ledger),
                mock.patch.object(self.analyzer, "FINAL_SUMMARY", summary),
            ):
                self.analyzer.write_manifests(self.result)
                self.analyzer.check_manifests(self.result)

                ledger.write_bytes(ledger.read_bytes() + b"mutated\n")
                with self.assertRaisesRegex(
                    self.analyzer.ReadinessError, "manifest is stale"
                ):
                    self.analyzer.check_manifests(self.result)

                self.analyzer.write_manifests(self.result)
                summary.write_bytes(summary.read_bytes() + b" ")
                with self.assertRaisesRegex(
                    self.analyzer.ReadinessError, "manifest is stale"
                ):
                    self.analyzer.check_manifests(self.result)

                self.analyzer.write_manifests(self.result)
                altered = copy.deepcopy(self.result)
                altered["residual"]["ledger"][0]["decision"] += "_stale"
                with self.assertRaisesRegex(
                    self.analyzer.ReadinessError, "manifest is stale"
                ):
                    self.analyzer.check_manifests(altered)

    def test_qpc_is_supporting_and_not_double_counted(self) -> None:
        qpc = self.result["qpc_supporting_audit"]
        self.assertFalse(qpc["additive_to_residual_accounting"])
        self.assertEqual(qpc["selected_release_tag"], "v6.5.1")
        self.assertEqual(qpc["portable_function_count"], 22)
        self.assertEqual(qpc["portable_function_bytes"], 2_450)
        self.assertTrue(qpc["cluster_partition_complete"])
        self.assertEqual(qpc["hook_pointer_count"], 9)
        self.assertFalse(qpc["exact_vendor_checkout_proven"])
        self.assertTrue(qpc["arcv2_em_target_linked"])
        self.assertEqual(qpc["arcv2_em_translation_units"], 10)
        self.assertEqual(qpc["arcv2_em_undefined_symbols"], [])
        self.assertEqual(qpc["arcv2_em_forbidden_runtime_imports"], [])
        self.assertEqual(
            qpc["arcv2_em_linked_object_sha256"],
            "c1aa5370945e41afcb29750174fd4531def9a887d37a0f620461eeabad587ad9",
        )
        self.assertFalse(qpc["install_placement_resolved"])
        self.assertFalse(qpc["production_routed"])
        self.assertEqual(
            qpc["hardware_validation"],
            "blocked by unavailable physical evidence",
        )

    def test_named_hook_providers_narrow_two_typed_boundaries(self) -> None:
        ledger = {
            item["start"]: item for item in self.result["residual"]["ledger"]
        }
        for start in (0x00311150, 0x00311620):
            self.assertEqual(
                ledger[start]["decision_origin"],
                "qpc_named_hook_provider_boundary",
            )
            self.assertEqual(
                ledger[start]["readiness"],
                "typed_unsupported_external_boundary",
            )
        audit = self.result["qpc_hook_provider_audit"]
        self.assertFalse(audit["additive_to_residual_accounting"])
        self.assertEqual(
            audit["named_providers"],
            ["PalUartResume", "VoltMon_DoMeasurement", "wsfOsRunIdleTasks"],
        )
        self.assertEqual(audit["unresolved_providers"], [])
        self.assertEqual(audit["software_provider_gaps"], [])
        self.assertTrue(audit["software_provider_source_available"])
        self.assertEqual(
            audit["hardware_dependent_providers"],
            ["PalUartResume", "VoltMon_DoMeasurement"],
        )
        self.assertEqual(audit["wsf_idle_semantics"]["callback_capacity"], 3)
        self.assertFalse(audit["exact_provider_source_available"])
        self.assertFalse(audit["redistribution_authority_resolved"])
        self.assertFalse(audit["candidate_production_routed"])

    def test_second_largest_controller_residual_is_a_typed_pawr_boundary(self) -> None:
        ledger = {item["start"]: item for item in self.result["residual"]["ledger"]}
        item = ledger[0x00321C30]
        self.assertEqual(item["size"], 1_804)
        self.assertEqual(item["readiness"], "typed_unsupported_external_boundary")
        self.assertEqual(item["decision_origin"], "pawr_fail_closed_boundary")
        audit = self.result["pawr_boundary_audit"]
        self.assertEqual((audit["span_count"], audit["bytes"], audit["function_count"]),
                         (1, 1_804, 4))
        self.assertFalse(audit["exact_source_available"])
        self.assertFalse(audit["candidate_production_routed"])

    def test_third_largest_controller_residual_is_a_typed_master_boundary(self) -> None:
        ledger = {item["start"]: item for item in self.result["residual"]["ledger"]}
        item = ledger[0x0031DFD0]
        self.assertEqual((item["size"], item["decision_origin"]),
                         (1_564, "master_connection_fail_closed_boundary"))
        audit = self.result["master_connection_boundary_audit"]
        self.assertEqual((audit["bytes"], audit["entry_count"]), (1_564, 3))
        self.assertFalse(audit["exact_source_available"])
        self.assertEqual(
            audit["hardware_validation"], "blocked by unavailable physical evidence",
        )

    def test_largest_controller_residual_is_a_typed_boundary_not_source(self) -> None:
        ledger = {
            item["start"]: item for item in self.result["residual"]["ledger"]
        }
        item = ledger[0x00329888]
        self.assertEqual(item["size"], 3_126)
        self.assertEqual(item["readiness"], "typed_unsupported_external_boundary")
        self.assertEqual(
            item["decision_origin"], "slave_connection_fail_closed_boundary",
        )
        audit = self.result["slave_connection_boundary_audit"]
        self.assertEqual(audit["span_count"], 1)
        self.assertEqual(audit["bytes"], 3_126)
        self.assertEqual(audit["function_count"], 6)
        self.assertFalse(audit["exact_source_available"])
        self.assertFalse(audit["redistribution_authority_resolved"])
        self.assertFalse(audit["candidate_production_routed"])

    def test_release_gate_does_not_confuse_accounted_with_implemented(self) -> None:
        gate = self.result["release_gate"]
        self.assertTrue(gate["accounting_complete"])
        self.assertFalse(gate["source_complete"])
        self.assertFalse(gate["production_ready"])
        self.assertEqual(gate["blocking_spans"], 152)
        self.assertEqual(gate["blocking_bytes"], 32_418)

    def test_missing_tail_decision_fails_before_zero_unclassified_claim(self) -> None:
        altered = copy.deepcopy(self.tail)
        altered["tail"]["decisions"].pop("0x00302D80")
        with self.assertRaisesRegex(self.analyzer.ReadinessError, "no readiness overlay"):
            self.analyzer.compose_reports(
                self.rows, self.meta, self.first, altered,
                self.hook_provider, self.slave_connection, self.pawr,
                self.master_connection, self.qpc,
            )

    def test_overlay_identity_mismatch_fails_closed(self) -> None:
        altered = copy.deepcopy(self.meta)
        altered["stock_runtime"]["islands"]["0x00302664"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(self.analyzer.ReadinessError, "identity mismatch"):
            self.analyzer.compose_reports(
                self.rows, altered, self.first, self.tail,
                self.hook_provider, self.slave_connection, self.pawr,
                self.master_connection, self.qpc,
            )

    def test_metaware_arc_target_compile_drift_fails_closed(self) -> None:
        altered = copy.deepcopy(self.meta)
        altered["candidate"]["arcv2_em_target_compiled"] = False
        with self.assertRaisesRegex(
            self.analyzer.ReadinessError, "MetaWare ARCv2 EM readiness evidence drift",
        ):
            result = self.analyzer.compose_reports(
                self.rows, altered, self.first, self.tail,
                self.hook_provider, self.slave_connection, self.pawr,
                self.master_connection, self.qpc,
            )
            self.analyzer._manifest_payloads(result)

    def test_named_hook_provider_identity_mismatch_fails_closed(self) -> None:
        altered = copy.deepcopy(self.hook_provider)
        altered["decisions"]["0x00311150"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            self.analyzer.ReadinessError, "hook-provider identity mismatch",
        ):
            self.analyzer.compose_reports(
                self.rows, self.meta, self.first, self.tail, altered,
                self.slave_connection, self.pawr, self.master_connection, self.qpc,
            )

    def test_slave_connection_identity_mismatch_fails_closed(self) -> None:
        altered = copy.deepcopy(self.slave_connection)
        altered["decision"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            self.analyzer.ReadinessError, "controller typed-boundary identity mismatch",
        ):
            self.analyzer.compose_reports(
                self.rows, self.meta, self.first, self.tail,
                self.hook_provider, altered, self.pawr, self.master_connection, self.qpc,
            )

    def test_pawr_identity_mismatch_fails_closed(self) -> None:
        altered = copy.deepcopy(self.pawr)
        altered["decision"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            self.analyzer.ReadinessError, "controller typed-boundary identity mismatch",
        ):
            self.analyzer.compose_reports(
                self.rows, self.meta, self.first, self.tail,
                self.hook_provider, self.slave_connection, altered,
                self.master_connection, self.qpc,
            )

    def test_master_connection_identity_mismatch_fails_closed(self) -> None:
        altered = copy.deepcopy(self.master_connection)
        altered["decision"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            self.analyzer.ReadinessError, "controller typed-boundary identity mismatch",
        ):
            self.analyzer.compose_reports(
                self.rows, self.meta, self.first, self.tail, self.hook_provider,
                self.slave_connection, self.pawr, altered, self.qpc,
            )

    def test_incomplete_qpc_partition_fails_closed(self) -> None:
        altered = copy.deepcopy(self.qpc)
        altered["recovery"]["cluster_partition_complete"] = False
        with self.assertRaisesRegex(self.analyzer.ReadinessError, "QP/C cluster"):
            self.analyzer.compose_reports(
                self.rows, self.meta, self.first, self.tail,
                self.hook_provider, self.slave_connection, self.pawr,
                self.master_connection, altered,
            )

    def test_json_cli_is_machine_readable(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"], cwd=ROOT,
            env=environment, check=True, capture_output=True, text=True,
        )
        result = json.loads(completed.stdout)
        self.assertTrue(result["residual"]["accounting_complete"])
        self.assertFalse(result["release_gate"]["production_ready"])

    def test_check_manifests_cli_is_read_only_and_current(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--check-manifests"], cwd=ROOT,
            env=environment, check=True, capture_output=True, text=True,
        )
        self.assertIn(
            "checked tools/manifests/em9305-final-source-readiness.tsv",
            completed.stdout,
        )
        self.assertIn(
            "checked tools/manifests/em9305-final-source-readiness-summary.json",
            completed.stdout,
        )


if __name__ == "__main__":
    unittest.main()
