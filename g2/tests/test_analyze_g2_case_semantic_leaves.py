# SPDX-License-Identifier: MIT
from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from tools import analyze_g2_case_semantic_leaves as analyzer


class CaseSemanticLeafAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = analyzer.analyze()

    def test_source_and_target_closure(self) -> None:
        self.assertTrue(self.report["software_source_complete"])
        self.assertEqual(
            self.report["software_source_complete_scope"],
            "the 189 admitted semantic leaves only")
        self.assertFalse(self.report["case_image_source_complete"])
        self.assertEqual(self.report["metrics"]["admitted_functions"], 189)
        self.assertEqual(self.report["metrics"]["admitted_instruction_bytes"], 14208)
        self.assertEqual(
            (self.report["metrics"]["post_baseline_admitted_functions"],
             self.report["metrics"]["post_baseline_admitted_instruction_bytes"]),
            (160, 14024))
        self.assertEqual(
            (self.report["metrics"]["authenticated_decompilation_rows"],
             self.report["metrics"][
                 "authenticated_decompilation_instruction_bytes"]),
            (189, 14208))
        self.assertEqual(
            (self.report["metrics"]["supplemental_decompilation_pin_rows"],
             self.report["metrics"][
                 "supplemental_decompilation_pin_instruction_bytes"]),
            (11, 148))
        self.assertEqual(
            (self.report["metrics"]["unclassified_bytes_before"],
             self.report["metrics"]["unclassified_bytes_after"]),
            (16854, 2646))
        self.assertEqual(self.report["metrics"]["target_missing_symbols"], 0)
        self.assertEqual(self.report["metrics"]["target_unexpected_symbols"], 0)
        self.assertEqual(
            self.report["metrics"]["embedded_instruction_byte_arrays"], 0)

    def test_integration_and_hardware_gates_stay_honest(self) -> None:
        self.assertFalse(self.report["production_routed"])
        self.assertEqual(self.report["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.report["hardware_operations"], [])

    def test_target_build_is_deterministic(self) -> None:
        first = analyzer.target_compile()
        second = analyzer.target_compile()
        self.assertEqual(first, second)

    def test_source_identity_tamper_is_rejected(self) -> None:
        original = Path.read_bytes

        def changed(path: Path) -> bytes:
            data = original(path)
            if path == analyzer.SOURCE:
                data = data[:-1] + bytes([data[-1] ^ 1])
            return data

        with mock.patch.object(Path, "read_bytes", changed):
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze()

    def test_authenticated_blob_tamper_is_rejected(self) -> None:
        original = Path.read_bytes

        def changed(path: Path) -> bytes:
            data = original(path)
            if path == analyzer.BLOB:
                data = data[:64] + bytes([data[64] ^ 1]) + data[65:]
            return data

        with mock.patch.object(Path, "read_bytes", changed):
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze()

    def test_every_semantic_decompilation_row_is_authenticated(self) -> None:
        evidence = analyzer.evidence_rows()
        address = min(analyzer.FUNCTIONS)
        changed = {key: dict(value) for key, value in evidence.items()}
        changed[address]["decompilation"] += "\n"
        with mock.patch.object(analyzer, "evidence_rows", return_value=changed):
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze()


if __name__ == "__main__":
    unittest.main()
