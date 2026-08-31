#!/usr/bin/env python3
"""Fail-closed tests for selected Touch platform completion batch 26."""

import csv, importlib.util, json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; P = ROOT / "tools/analyze_g2_touch_platform_completion_admission.py"
S = importlib.util.spec_from_file_location("touch_platform_final_batch26_test", P); M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)


class TouchPlatformCompletionAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.result = M.analyze()

    def test_exact_function_frontier_closure(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["admitted_functions"], metrics["admitted_instruction_bytes"]), (8, 942))
        self.assertEqual(metrics["concrete_source_or_implementation_gap_after"], 0)
        self.assertEqual(metrics["residual_gap_instruction_bytes"], 0)
        self.assertTrue(self.result["software_function_frontier_complete"])

    def test_selected_source_policy_is_device_free(self):
        for row in self.result["rows"]:
            self.assertFalse(row["fixed_address_access"]); self.assertFalse(row["mmio_execution"])
        self.assertIn("safe defaults", self.result["configuration_evidence"])

    def test_target_compile_and_hardware_policy(self):
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertEqual(self.result["hardware_validation"], "blocked by unavailable physical evidence")
        self.assertEqual(self.result["hardware_blocker"], "blocked by unavailable physical evidence")
        self.assertIn("not production-routed", self.result["integration"])
        self.assertNotIn("hardware_operations", self.result)

    def test_batch_writer_cannot_overwrite_final_current_summary(self):
        self.assertNotIn('current.write_text', P.read_text(encoding="utf-8"))

    def test_manifests_match_and_residual_empty(self):
        with (M.MANIFEST_DIR / "g2-touch-platform-completion-admission.tsv").open(newline="") as h:
            rows = list(csv.DictReader((line for line in h if not line.startswith("#")), delimiter="\t"))
        self.assertEqual({int(r["entry"], 0) for r in rows}, set(M.ADMISSIONS))
        residual = (M.MANIFEST_DIR / "g2-touch-platform-completion-residual.tsv").read_text().splitlines()
        self.assertEqual(len(residual), 2)
        summary = json.loads((M.MANIFEST_DIR / "g2-touch-platform-completion-admission-summary.json").read_text())
        self.assertEqual(summary["metrics"], self.result["metrics"])


if __name__ == "__main__": unittest.main()
