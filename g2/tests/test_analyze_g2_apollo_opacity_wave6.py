# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave6.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave6/typed_boundaries.tsv"
RECONCILED = G2 / "research/admission/apollo_opacity_wave6/reconciled_frontier.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave6-vector-stroke-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave6", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave5_residual_and_root_are_pinned(self) -> None:
        self.assertEqual(self.report["wave5_residual"], {"functions": 1395, "bytes": 172308})
        self.assertEqual(self.report["before"], self.report["wave5_residual"])
        self.assertEqual(self.report["selected_root_range"], {"start": "0x0051C5EC", "end_exclusive": "0x0051D2D6"})

    def test_complete_actionable_closure_is_closed(self) -> None:
        self.assertEqual(self.report["newly_typed"], {"functions": 7, "bytes": 4386})
        self.assertEqual(self.report["closure_depths"], {
            "0": {"typed_functions": 1, "typed_bytes": 3306},
            "1": {"typed_functions": 5, "typed_bytes": 644},
            "2": {"typed_functions": 1, "typed_bytes": 436},
        })
        self.assertEqual(self.report["reconciled_frontier"], {"functions": 7, "new_bytes": 0})

    def test_guarded_continuation_is_not_lost(self) -> None:
        self.assertEqual(self.report["guarded_continuation"], {
            "entry": "0x00523A34", "target": "0x00523A3A",
            "instruction_bytes": "032900da7047", "accounted": True,
        })
        entries = {row["entry"] for row in self.report["records"]}
        self.assertIn("0x00523A34", entries)
        self.assertIn("0x00523A3A", entries)

    def test_all_bodies_are_sha_pinned_and_fail_closed(self) -> None:
        records = self.report["records"]
        self.assertEqual(len(records), 7)
        self.assertEqual(len({row["body_sha256"] for row in records}), 7)
        self.assertTrue(all(row["disposition"] == "typed-external-provider-unavailable" for row in records))
        self.assertTrue(all(row["license_status"] == "unavailable" for row in records))
        self.assertTrue(all(not row["callable_implementation_available"] for row in records))
        self.assertEqual(
            self.report["mapping_sha256"],
            "ae07afe04fd3aad513236a46bad8c04e55431a37c2ed6b29a10c68cf58117e2d",
        )

    def test_provider_context_does_not_become_admission(self) -> None:
        provider = self.report["provider"]
        self.assertEqual(provider["authenticated_function_identities"], [])
        self.assertIsNone(provider["authenticated_provider"])
        self.assertIsNone(provider["authenticated_license"])
        self.assertEqual(len(provider["negative_evidence"]), 3)

    def test_accounting_and_next_envelope(self) -> None:
        self.assertEqual(self.report["after"], {"functions": 1388, "bytes": 167922})
        self.assertEqual(self.report["largest_remaining"], {"entry": "0x00564974", "envelope_bytes": 2598})

    def test_table_mutations_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            boundary = temp_path / "typed.tsv"
            boundary.write_text(BOUNDARY.read_text().replace("\t3306\t3298\t", "\t3304\t3298\t", 1))
            reconciled = temp_path / "frontier.tsv"
            reconciled.write_text(RECONCILED.read_text().replace("\t138\t0\t", "\t136\t0\t", 1))
            old_boundary, old_reconciled = self.analyzer.BOUNDARY, self.analyzer.RECONCILED
            try:
                self.analyzer.BOUNDARY = boundary
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.RECONCILED = reconciled
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
            finally:
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.RECONCILED = old_reconciled

    def test_research_only_and_deterministic_cli(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave6", path.read_text(errors="ignore"))
        self.assertIn("Production admission", DOC.read_text())
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "opacity-wave6-vector-stroke-closure-typed")


if __name__ == "__main__":
    unittest.main()
