#!/usr/bin/env python3
"""Fail-closed tests for Touch product orchestration admission batch 24."""

import csv, importlib.util, json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_touch_product_orchestration_admission.py"
S = importlib.util.spec_from_file_location("touch_product_batch24_test", P)
M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)


class TouchProductOrchestrationAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.result = M.analyze()

    def test_exact_progress(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["admitted_functions"], metrics["admitted_instruction_bytes"]), (2, 580))
        self.assertEqual((metrics["concrete_source_or_implementation_gap_after"], metrics["residual_gap_instruction_bytes"]), (19, 2578))
        self.assertEqual(metrics["unimplemented_application_contracts_after"], 0)
        self.assertEqual(metrics["typed_external_or_unavailable_functions"], 19)

    def test_hardware_and_resident_execution_are_excluded(self):
        for row in self.result["rows"]:
            self.assertTrue(row["caller_supplied_register_views"])
            self.assertTrue(row["injected_provider_contract"])
            self.assertFalse(row["resident_body_admitted"])
            self.assertFalse(row["fixed_address_access"])
            self.assertFalse(row["mmio_execution"])

    def test_target_compile_and_block(self):
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertEqual(self.result["hardware_validation"], "deferred by project direction")
        self.assertEqual(self.result["hardware_blocker"], "deferred by project direction")
        self.assertIn("not production-routed", self.result["integration"])

    def test_manifests_match(self):
        with (M.MANIFEST_DIR / "g2-touch-product-orchestration-admission.tsv").open(newline="") as h:
            rows = list(csv.DictReader((line for line in h if not line.startswith("#")), delimiter="\t"))
        self.assertEqual({int(r["entry"], 0) for r in rows}, set(M.ADMISSIONS))
        summary = json.loads((M.MANIFEST_DIR / "g2-touch-product-orchestration-admission-summary.json").read_text())
        self.assertEqual(summary["metrics"], self.result["metrics"])

    def test_batch_writer_cannot_downgrade_final_classification(self):
        source = Path(M.__file__).read_text()
        self.assertNotIn(
            'current.write_text(json.dumps({', source,
            "an admission batch must not overwrite whole-blob readiness",
        )
        self.assertIn("analyze_g2_touch_final_frontier.py", source)


if __name__ == "__main__": unittest.main()
