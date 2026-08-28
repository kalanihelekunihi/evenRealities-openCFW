#!/usr/bin/env python3
"""Fail-closed tests for Touch clock/application wrapper admission batch 22."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_touch_clock_application_wrappers_admission.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("touch_clock_app_batch22_test", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TouchClockApplicationWrapperAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.result = cls.module.analyze()

    def test_exact_progress(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["admitted_functions"], 6)
        self.assertEqual(metrics["admitted_instruction_bytes"], 316)
        self.assertEqual(metrics["concrete_source_or_implementation_gap_after"], 25)
        self.assertEqual(metrics["residual_gap_instruction_bytes"], 3864)
        self.assertEqual(metrics["unimplemented_application_contracts_after"], 13)

    def test_hardware_access_is_not_embedded(self) -> None:
        for row in self.result["rows"]:
            self.assertTrue(row["injected_provider_contract"])
            self.assertFalse(row["fixed_address_access"])
            self.assertFalse(row["mmio_execution"])

    def test_target_closure_and_physical_block(self) -> None:
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertIn("isolated source candidate", self.result["integration"])
        self.assertEqual(
            self.result["hardware_validation"],
            "deferred by project direction",
        )
        self.assertEqual(
            self.result["hardware_blocker"],
            "deferred by project direction",
        )

    def test_manifests_match(self) -> None:
        manifest = self.module.MANIFEST_DIR / "g2-touch-clock-application-wrappers-admission.tsv"
        with manifest.open(newline="") as handle:
            rows = list(csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t",
            ))
        self.assertEqual({int(row["entry"], 0) for row in rows},
                         set(self.module.ADMISSIONS))
        summary = json.loads((self.module.MANIFEST_DIR /
            "g2-touch-clock-application-wrappers-admission-summary.json").read_text())
        self.assertEqual(summary["metrics"], self.result["metrics"])

    def test_batch_writer_cannot_downgrade_final_classification(self) -> None:
        source = self.module.ANALYZER.read_text() if hasattr(
            self.module, "ANALYZER") else Path(self.module.__file__).read_text()
        self.assertNotIn(
            'current.write_text(json.dumps({', source,
            "an admission batch must not overwrite whole-blob readiness",
        )
        self.assertIn("analyze_g2_touch_final_frontier.py", source)


if __name__ == "__main__":
    unittest.main()
