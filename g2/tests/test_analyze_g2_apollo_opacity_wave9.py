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
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave9.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave9/typed_boundaries.tsv"
SHARED = G2 / "research/admission/apollo_opacity_wave9/shared_data.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave9-elliptical-arc-runtime-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave9", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave8_residual_and_authoritative_root_are_pinned(self) -> None:
        self.assertEqual(self.report["wave8_residual"], {"functions": 1357, "bytes": 157768})
        self.assertEqual(self.report["before"], self.report["wave8_residual"])
        self.assertEqual(self.report["selected_root_range"], {"start": "0x0051A8EC", "end_exclusive": "0x0051B116"})

    def test_complete_static_call_closure_is_typed(self) -> None:
        self.assertEqual(self.report["actionable_graph"], {"positive_functions": 4, "positive_bytes": 3308, "terminal_functions": 11, "call_edges": 18, "static_callsites": 35})
        self.assertEqual(self.report["closure_depths"]["2"], {"typed_functions": 2, "typed_bytes": 640})
        self.assertEqual(len(self.report["frontier_records"]), 11)
        self.assertEqual(len(self.report["callers"]["0x0051A8EC"]), 4)

    def test_interiors_and_shared_data_are_exhaustive_and_zero_additional(self) -> None:
        self.assertEqual(self.report["range_partition"], {"functions": 4, "interior_islands": 4, "interior_physical_bytes": 12, "additional_function_bytes": 0})
        self.assertEqual(self.report["shared_data"], {"islands": 5, "physical_bytes": 124, "direct_dat_cells": 33, "out_of_envelope_direct_dat_cells": 31, "additional_function_bytes": 0})
        self.assertTrue(all(row["wave9_additional_bytes"] == "0" for row in self.report["interior_records"]))
        self.assertTrue(all(row["wave9_additional_function_bytes"] == "0" for row in self.report["shared_records"]))

    def test_unavailable_providers_and_licenses_fail_closed(self) -> None:
        self.assertEqual(self.report["source_attributed"], {"functions": 0, "bytes": 0})
        self.assertEqual(self.report["typed_unavailable"], {"vector_path_functions": 3, "vector_path_bytes": 2942, "iar_runtime_functions": 1, "iar_runtime_bytes": 366})
        self.assertTrue(all(row["disposition"] == "typed-external-provider-unavailable" for row in self.report["records"]))
        self.assertTrue(all(not row["source_identity_authenticated"] for row in self.report["records"]))
        tanf = next(row for row in self.report["records"] if row["entry"] == "0x00563F40")
        self.assertEqual(tanf["license_status"], "proprietary-runtime-source-unavailable")
        self.assertIsNone(self.report["provider"]["authenticated_vector_license"])

    def test_terminal_frontier_retains_prior_classifications(self) -> None:
        frontier = {row["entry"]: row for row in self.report["frontier_records"]}
        self.assertEqual(frontier["0x004397A8"]["license_status"], "MIT")
        self.assertEqual(frontier["0x00509690"]["classification"], "existing-parent-first-party")
        self.assertEqual(frontier["0x00517E18"]["source_wave"], "apollo-opacity-wave3")
        self.assertTrue(all(row["wave9_additional_function_bytes"] == "0" for row in frontier.values()))

    def test_accounting_and_next_envelope(self) -> None:
        self.assertEqual(self.report["after"], {"functions": 1353, "bytes": 154460})
        self.assertEqual(self.report["largest_remaining"], {"entry": "0x0051B140", "envelope_bytes": 1962})
        self.assertEqual(self.report["mapping_sha256"], "597da99d0f495b237ad97191030ea26ab2e9133f91a59c3c65fd95e4e80b7fb2")

    def test_boundary_and_data_mutations_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            boundary = root / "typed.tsv"
            boundary.write_text(BOUNDARY.read_text().replace("\t366\t366\t", "\t364\t366\t", 1))
            shared = root / "shared.tsv"
            shared.write_text(SHARED.read_text().replace("83f9223f", "82f9223f", 1))
            old_boundary, old_shared = self.analyzer.BOUNDARY, self.analyzer.SHARED
            try:
                self.analyzer.BOUNDARY = boundary
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.SHARED = shared
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
            finally:
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.SHARED = old_shared

    def test_research_only_deterministic_cli_and_production_exclusion(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave9", path.read_text(errors="ignore"))
        self.assertIn("## Production admission", DOC.read_text())
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        cli = json.loads(first)
        self.assertEqual(cli["mapping_sha256"], self.report["mapping_sha256"])
        self.assertEqual(cli["status"], "opacity-wave9-elliptical-arc-and-runtime-closure-typed")


if __name__ == "__main__":
    unittest.main()
