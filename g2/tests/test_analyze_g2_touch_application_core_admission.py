#!/usr/bin/env python3
"""Fail-closed tests for Touch application core admission batch 23."""

import csv, importlib.util, json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_touch_application_core_admission.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("touch_application_core_batch23_test", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module); return module


class TouchApplicationCoreAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_analyzer(); cls.result = cls.module.analyze()

    def test_exact_progress(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["admitted_functions"], 4)
        self.assertEqual(metrics["admitted_instruction_bytes"], 706)
        self.assertEqual(metrics["concrete_source_or_implementation_gap_after"], 21)
        self.assertEqual(metrics["residual_gap_instruction_bytes"], 3158)
        self.assertEqual(metrics["unimplemented_application_contracts_after"], 9)

    def test_resident_and_hardware_bodies_are_not_embedded(self):
        for row in self.result["rows"]:
            self.assertTrue(row["caller_owned_object_views"])
            self.assertTrue(row["injected_provider_contract"])
            self.assertFalse(row["resident_body_admitted"])
            self.assertFalse(row["fixed_address_access"])
            self.assertFalse(row["mmio_execution"])

    def test_target_closure_and_physical_block(self):
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertEqual(
            self.result["hardware_validation"],
            "deferred by project direction",
        )
        self.assertEqual(
            self.result["hardware_blocker"],
            "deferred by project direction",
        )
        self.assertIn("not production-routed", self.result["integration"])

    def test_manifests_match(self):
        path = self.module.MANIFEST_DIR / "g2-touch-application-core-admission.tsv"
        with path.open(newline="") as handle:
            rows = list(csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t"))
        self.assertEqual({int(row["entry"], 0) for row in rows},
                         set(self.module.ADMISSIONS))
        summary = json.loads((self.module.MANIFEST_DIR /
            "g2-touch-application-core-admission-summary.json").read_text())
        self.assertEqual(summary["metrics"], self.result["metrics"])

    def test_batch_writer_cannot_downgrade_final_classification(self):
        source = Path(self.module.__file__).read_text()
        self.assertNotIn(
            'current.write_text(json.dumps({', source,
            "an admission batch must not overwrite whole-blob readiness",
        )
        self.assertIn("analyze_g2_touch_final_frontier.py", source)


if __name__ == "__main__": unittest.main()
