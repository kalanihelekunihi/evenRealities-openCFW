#!/usr/bin/env python3
"""Fail-closed tests for Touch platform wrapper admission batch 21."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_touch_platform_wrappers_admission.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("touch_platform_batch21_test", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TouchPlatformWrapperAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.result = cls.module.analyze()

    def test_exact_progress(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["admitted_functions"], 12)
        self.assertEqual(metrics["admitted_instruction_bytes"], 298)
        self.assertEqual(metrics["concrete_source_or_implementation_gap_after"], 31)
        self.assertEqual(metrics["residual_gap_instruction_bytes"], 4180)
        self.assertEqual(metrics["unimplemented_application_contracts_after"], 19)

    def test_no_vendor_body_or_mmio_was_admitted(self) -> None:
        for row in self.result["rows"]:
            self.assertFalse(row["eula_provider_body_admitted"])
            self.assertFalse(row["resident_table_dependency"])
            self.assertFalse(row["mmio_execution"])

    def test_source_target_closure_and_hardware_block(self) -> None:
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertIn("isolated source candidate", self.result["integration"])
        self.assertEqual(
            self.result["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(
            self.result["hardware_blocker"],
            "blocked by unavailable physical evidence",
        )

    def test_manifests_match(self) -> None:
        manifest = self.module.MANIFEST_DIR / "g2-touch-platform-wrappers-admission.tsv"
        with manifest.open(newline="") as handle:
            rows = list(csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t",
            ))
        self.assertEqual({int(row["entry"], 0) for row in rows},
                         set(self.module.ADMISSIONS))
        summary = json.loads((self.module.MANIFEST_DIR /
            "g2-touch-platform-wrappers-admission-summary.json").read_text())
        self.assertEqual(summary["metrics"], self.result["metrics"])


if __name__ == "__main__":
    unittest.main()
