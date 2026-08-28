# SPDX-License-Identifier: MIT
"""Fail-closed admission tests for Case register/state policies."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path
import unittest
from unittest import mock

from tools import analyze_g2_case_register_policies as analyzer


class CaseRegisterPolicyAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = analyzer.analyze()

    def test_exact_authenticated_closure(self) -> None:
        metrics = self.result["metrics"]
        self.assertEqual(metrics["admitted_functions"], 8)
        self.assertEqual(metrics["admitted_instruction_bytes"], 214)
        self.assertEqual(metrics["authenticated_instruction_bytes"], 214)
        self.assertEqual(
            (metrics["unclassified_bytes_before"],
             metrics["unclassified_bytes_after"]),
            (2398, 2184))
        self.assertEqual(metrics["target_missing_symbols"], 0)
        self.assertEqual(metrics["raw_instruction_transcription_bytes"], 0)
        self.assertEqual(metrics["embedded_mmio_addresses"], 0)
        self.assertEqual(self.result["evidence"]["authenticated_rows"], 8)

    def test_every_row_has_one_authenticated_clean_room_disposition(self) -> None:
        self.assertEqual(len(self.result["admissions"]), 8)
        for row in self.result["admissions"]:
            self.assertEqual(row["status"],
                             "isolated_source_candidate_not_routed")
            self.assertEqual(row["license"], "MIT")
            self.assertEqual(len(row["instruction_sha256"]), 64)
            self.assertEqual(len(row["decompilation_sha256"]), 64)
            self.assertTrue(row["contract"])
            self.assertFalse(row["mmio_address_embedded"])
            self.assertFalse(row["hardware_operation"])

    def test_candidate_and_hardware_gates_are_truthful(self) -> None:
        self.assertTrue(self.result["software_source_complete"])
        self.assertFalse(self.result["production_routed"])
        self.assertEqual(self.result["hardware_validation"],
                         "deferred by project direction")
        self.assertEqual(self.result["hardware_operations"], [])
        self.assertEqual(self.result["production_files_modified"], [])

    def test_authenticated_blob_tamper_fails_closed(self) -> None:
        original = Path.read_bytes

        def changed(path: Path) -> bytes:
            data = original(path)
            if path == analyzer.BLOB:
                return data[:-1] + bytes([data[-1] ^ 1])
            return data

        with mock.patch.object(Path, "read_bytes", changed):
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze()

    def test_written_manifest_retains_candidate_boundaries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-case-policy-proof-") as raw:
            output = Path(raw) / "admission.tsv"
            summary = Path(raw) / "summary.json"
            with mock.patch.object(analyzer, "OUTPUT", output), \
                    mock.patch.object(analyzer, "SUMMARY", summary):
                analyzer.write_manifests(self.result)
            with output.open(newline="") as handle:
                rows = list(csv.DictReader(
                    (line for line in handle if not line.startswith("#")),
                    delimiter="\t"))
            self.assertEqual(len(rows), 8)
            self.assertEqual({row["status"] for row in rows},
                             {"isolated_source_candidate_not_routed"})
            self.assertIn('"production_routed": false', summary.read_text())


if __name__ == "__main__":
    unittest.main()
