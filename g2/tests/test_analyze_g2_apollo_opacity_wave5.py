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
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave5.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave5/typed_boundaries.tsv"
RECONCILED = G2 / "research/admission/apollo_opacity_wave5/reconciled_graph.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave5-cubic-vector-path-root.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave5", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave4_residual_and_largest_root_are_pinned(self) -> None:
        self.assertEqual(
            self.report["wave4_residual"], {"functions": 1396, "bytes": 177364}
        )
        self.assertEqual(self.report["before"], self.report["wave4_residual"])
        self.assertEqual(
            self.report["selected_root_range"],
            {"start": "0x00519290", "end_exclusive": "0x0051A650"},
        )

    def test_complete_graph_reconciles_before_new_bytes(self) -> None:
        self.assertEqual(
            self.report["reconciled_frontier"],
            {
                "functions": 13,
                "prior_typed_functions": 12,
                "source_owned_zero_opaque_rows": 1,
                "new_bytes": 0,
            },
        )
        self.assertEqual(
            self.report["closure_depths"],
            {
                "0": {"typed_functions": 1, "typed_bytes": 5056},
                "1": {
                    "prior_typed_functions": 12,
                    "source_owned_zero_opaque_rows": 1,
                    "wave5_new_bytes": 0,
                },
            },
        )
        self.assertEqual(
            sum(row["call_count"] for row in self.report["reconciled_records"]),
            74,
        )
        self.assertTrue(
            all(row["wave5_new_opaque_bytes"] == 0 for row in self.report["reconciled_records"])
        )

    def test_root_is_sha_pinned_and_fail_closed(self) -> None:
        self.assertEqual(self.report["newly_typed"], {"functions": 1, "bytes": 5056})
        record = self.report["records"][0]
        self.assertEqual(record["corpus_body_bytes"], 4998)
        self.assertEqual(record["envelope_bytes"] - record["corpus_body_bytes"], 58)
        self.assertEqual(
            record["body_sha256"],
            "48ef98e94015af6eaac62bfaf88469032b41ab98021cc4d097c8cd54d8c737b1",
        )
        self.assertEqual(record["disposition"], "typed-external-provider-unavailable")
        self.assertEqual(record["license_status"], "unavailable")
        self.assertFalse(record["callable_implementation_available"])
        self.assertEqual(
            self.report["mapping_sha256"],
            "91a954208da4ede673adfcb118e61f4e336e44f04cc0d3c06b46915e16a6d5b7",
        )

    def test_provider_context_does_not_become_identity_or_license(self) -> None:
        provider = self.report["provider"]
        self.assertEqual(
            provider["callers"], ["0x005171F8", "0x0051D2E0", "0x0051F798"]
        )
        self.assertIsNone(provider["authenticated_function_identity"])
        self.assertIsNone(provider["authenticated_provider"])
        self.assertIsNone(provider["authenticated_license"])
        self.assertEqual(len(provider["negative_evidence"]), 3)

    def test_accounting_closes_and_selects_next_envelope(self) -> None:
        self.assertEqual(self.report["after"], {"functions": 1395, "bytes": 172308})
        self.assertEqual(
            self.report["largest_remaining"],
            {"entry": "0x0051C5EC", "envelope_bytes": 3306},
        )

    def test_boundary_and_reconciliation_mutations_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            boundary = temp_path / "typed.tsv"
            boundary.write_text(BOUNDARY.read_text().replace("\t5056\t4998\t", "\t5054\t4998\t", 1))
            reconciled = temp_path / "reconciled.tsv"
            reconciled.write_text(RECONCILED.read_text().replace("0x004397A8\t7\t", "0x004397A8\t6\t", 1))
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

    def test_research_only_and_no_hardware_or_production_route(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave5", path.read_text(errors="ignore"))
        document = DOC.read_text()
        self.assertIn("typed-external-provider-unavailable", document)
        self.assertIn("Production admission", document)

    def test_cli_is_deterministic(self) -> None:
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(
            json.loads(first)["status"], "opacity-wave5-cubic-vector-path-root-typed"
        )


if __name__ == "__main__":
    unittest.main()
