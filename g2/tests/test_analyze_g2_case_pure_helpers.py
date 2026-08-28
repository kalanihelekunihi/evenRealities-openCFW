# SPDX-License-Identifier: MIT
from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from tools import analyze_g2_case_pure_helpers as analyzer


class CasePureHelperAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = analyzer.analyze()

    def test_source_and_target_closure(self) -> None:
        self.assertTrue(self.report["software_source_complete"])
        self.assertEqual(
            self.report["software_source_complete_scope"],
            "the seven admitted pure helpers only")
        self.assertFalse(self.report["case_image_source_complete"])
        self.assertEqual(self.report["metrics"]["admitted_functions"], 7)
        self.assertEqual(self.report["metrics"]["admitted_instruction_bytes"], 248)
        self.assertEqual(
            (self.report["metrics"]["unclassified_bytes_before"],
             self.report["metrics"]["unclassified_bytes_after"]),
            (2646, 2398))
        self.assertEqual(self.report["metrics"]["target_missing_symbols"], 0)
        self.assertEqual(self.report["metrics"]["target_unexpected_symbols"], 0)
        self.assertEqual(
            self.report["metrics"]["embedded_instruction_byte_arrays"], 0)

    def test_integration_stays_closed(self) -> None:
        self.assertFalse(self.report["production_routed"])
        self.assertEqual(self.report["hardware_validation"],
                         "deferred by project direction")
        self.assertEqual(self.report["hardware_operations"], [])

    def test_target_build_is_deterministic(self) -> None:
        self.assertEqual(analyzer.target_compile(), analyzer.target_compile())

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


if __name__ == "__main__":
    unittest.main()
