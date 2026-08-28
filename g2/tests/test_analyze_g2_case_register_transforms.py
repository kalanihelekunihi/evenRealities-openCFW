#!/usr/bin/env python3
"""Fail-closed tests for the second case register admission."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_case_register_transforms.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("g2_case_transform_admission", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CaseRegisterTransformAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.result = cls.module.analyze()

    def test_exact_second_admission(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["admitted_functions"], 5)
        self.assertEqual(metrics["admitted_instruction_bytes"], 96)
        self.assertEqual(metrics["unclassified_bytes_before"], 16950)
        self.assertEqual(metrics["unclassified_bytes_after"], 16854)

    def test_target_closure_and_source_state(self) -> None:
        self.assertGreater(self.result["metrics"]["target_object_bytes"], 0)
        self.assertEqual(len(self.result["source"]["exports"]), 5)
        self.assertIn("isolated source candidate", self.result["integration"])
        self.assertFalse(self.result["production_routed"])
        self.assertEqual(self.result["hardware_operations"], [])
        self.assertEqual(
            self.result["hardware_validation"],
            "deferred by project direction",
        )
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertTrue(all(row["license"] == "MIT"
                            for row in self.result["rows"]))

    def test_target_build_is_deterministic(self) -> None:
        self.assertEqual(
            self.module._target_compile(), self.module._target_compile())

    def test_rows_and_manifests_are_exact(self) -> None:
        for row in self.result["rows"]:
            self.assertFalse(row["mmio_execution"])
            self.assertFalse(row["destructive_operation"])
        with self.module.MANIFEST.open(newline="") as handle:
            rows = list(csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t",
            ))
        self.assertEqual({int(row["entry"], 0) for row in rows},
                         set(self.module.ADMISSIONS))
        summary = json.loads(self.module.SUMMARY.read_text())
        self.assertEqual(summary["metrics"], self.result["metrics"])


if __name__ == "__main__":
    unittest.main()
