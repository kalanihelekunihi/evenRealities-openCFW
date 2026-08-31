#!/usr/bin/env python3
"""Fail-closed tests for case register-primitive source admission."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_case_register_primitives.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("g2_case_register_admission", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CaseRegisterPrimitiveAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.result = cls.module.analyze()

    def test_exact_admission_and_residual(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["admitted_functions"], 13)
        self.assertEqual(metrics["admitted_instruction_bytes"], 120)
        self.assertEqual(metrics["unclassified_bytes_before"], 17070)
        self.assertEqual(metrics["unclassified_bytes_after"], 16950)

    def test_source_is_cortex_m0plus_compilable_and_not_routed(self) -> None:
        self.assertEqual(
            self.result["source"]["target"],
            "thumbv6m-none-eabi / Cortex-M0+ / Thumb",
        )
        self.assertGreater(self.result["metrics"]["target_object_bytes"], 0)
        self.assertEqual(len(self.result["source"]["exports"]), 13)
        self.assertIn("isolated source candidate", self.result["integration"])
        self.assertFalse(self.result["production_routed"])
        self.assertEqual(self.result["hardware_operations"], [])

    def test_target_build_is_deterministic(self) -> None:
        self.assertEqual(
            self.module._target_compile(), self.module._target_compile())

    def test_every_row_is_non_destructive_and_non_mmio(self) -> None:
        for row in self.result["rows"]:
            self.assertFalse(row["mmio_execution"])
            self.assertFalse(row["destructive_operation"])
            self.assertEqual(row["license"], "MIT")

    def test_hardware_validation_is_deferred_by_direction(self) -> None:
        self.assertEqual(
            self.result["hardware_validation"],
            "blocked by unavailable physical evidence",
        )

    def test_manifest_matches_analyzer_rows(self) -> None:
        with self.module.MANIFEST.open(newline="") as handle:
            rows = list(csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t",
            ))
        self.assertEqual(len(rows), 13)
        self.assertEqual(
            {int(row["entry"], 0) for row in rows},
            set(self.module.ADMISSIONS),
        )
        summary = json.loads(self.module.SUMMARY.read_text())
        self.assertEqual(summary["admitted_row_count"], 13)
        self.assertEqual(summary["metrics"], self.result["metrics"])

    def test_blob_tamper_fails_closed(self) -> None:
        data = bytearray(self.module.BLOB.read_bytes())
        data[-1] ^= 1
        with tempfile.TemporaryDirectory(prefix="open-cfw-case-register-tamper-") as raw:
            path = Path(raw) / "case.bin"
            path.write_bytes(data)
            with mock.patch.object(self.module, "BLOB", path):
                with self.assertRaisesRegex(self.module.AuditError, "blob identity"):
                    self.module.analyze()

    def test_source_pin_matches_bytes(self) -> None:
        for path, (size, digest) in self.module.SOURCE_PINS.items():
            data = path.read_bytes()
            self.assertEqual(len(data), size)
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
