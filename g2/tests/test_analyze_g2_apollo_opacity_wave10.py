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
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave10.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave10/typed_boundaries.tsv"
CALLOTHER = G2 / "research/admission/apollo_opacity_wave10/reconciled_callother.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave10-round-join-mve-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave10", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave9_residual_and_selected_root_are_pinned(self) -> None:
        self.assertEqual(self.report["wave9_residual"], {"functions": 1353, "bytes": 154460})
        self.assertEqual(self.report["before"], self.report["wave9_residual"])
        self.assertEqual(self.report["selected_root_range"], {"start": "0x0051B140", "end_exclusive": "0x0051B8EA"})

    def test_complete_real_static_call_closure_is_reconciled(self) -> None:
        self.assertEqual(self.report["actionable_graph"], {"positive_functions": 1, "positive_bytes": 1962, "terminal_functions": 7, "call_edges": 7, "static_callsites": 26})
        self.assertEqual(self.report["machine_branch_closure"], {"direct_bl_sites": 26, "wide_nonlink_sites": 0, "register_blx_sites": 0, "targets": 7})
        self.assertEqual(len(self.report["branch_records"]), 26)
        self.assertEqual(len(self.report["frontier_records"]), 7)

    def test_ghidra_callother_artifacts_are_not_provider_boundaries(self) -> None:
        self.assertEqual(self.report["callother_reconciliation"], {"artifacts": 16, "occurrences": 16, "machine_branch_sites": 0, "additional_function_bytes": 0})
        self.assertEqual(len(self.report["callother_records"]), 16)
        self.assertTrue(all(row["disposition"] == "not-a-static-call-boundary" for row in self.report["callother_records"]))
        self.assertTrue(all(row["wave10_additional_function_bytes"] == "0" for row in self.report["callother_records"]))

    def test_interior_shared_and_census_gap_bytes_are_accounted_once(self) -> None:
        self.assertEqual(self.report["range_partition"], {"functions": 1, "interior_islands": 1, "interior_physical_bytes": 4, "additional_function_bytes": 0})
        self.assertEqual(self.report["shared_data"], {"islands": 2, "physical_bytes": 10, "direct_dat_cells": 3, "out_of_envelope_direct_dat_cells": 2, "additional_function_bytes": 0})
        pointer = next(row for row in self.report["shared_records"] if row["start"] == "0x0051BF74")
        self.assertEqual(pointer["consumers"], "0x0051B140,0x0051B8F0")

    def test_provider_and_license_claims_fail_closed(self) -> None:
        self.assertEqual(self.report["source_attributed"], {"functions": 0, "bytes": 0})
        self.assertEqual(self.report["typed_unavailable"], {"functions": 1, "bytes": 1962})
        record = self.report["records"][0]
        self.assertEqual(record["disposition"], "typed-external-provider-unavailable")
        self.assertEqual(record["license_status"], "unavailable")
        self.assertFalse(record["source_identity_authenticated"])
        self.assertIsNone(self.report["provider"]["authenticated_license"])

    def test_accounting_and_next_envelope(self) -> None:
        self.assertEqual(self.report["after"], {"functions": 1352, "bytes": 152498})
        self.assertEqual(self.report["largest_remaining"], {"entry": "0x005AF88C", "envelope_bytes": 1912})
        self.assertEqual(self.report["mapping_sha256"], "eceee6de441e814f3d7c21138755126dffefed12b95634941015bae93813abd9")

    def test_boundary_and_callother_mutations_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            boundary = root / "typed.tsv"
            boundary.write_text(BOUNDARY.read_text().replace("\t1962\t1958\t", "\t1960\t1958\t", 1))
            callother = root / "callother.tsv"
            callother.write_text(CALLOTHER.read_text().replace("0x00D2A29C\t1\t0", "0x00D2A29C\t1\t1", 1))
            old_boundary, old_callother = self.analyzer.BOUNDARY, self.analyzer.CALLOTHER
            try:
                self.analyzer.BOUNDARY = boundary
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.CALLOTHER = callother
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
            finally:
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.CALLOTHER = old_callother

    def test_research_only_deterministic_cli_and_production_exclusion(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave10", path.read_text(errors="ignore"))
        self.assertIn("## Production admission", DOC.read_text())
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        cli = json.loads(first)
        self.assertEqual(cli["mapping_sha256"], self.report["mapping_sha256"])
        self.assertEqual(cli["status"], "opacity-wave10-round-join-mve-closure-typed")


if __name__ == "__main__":
    unittest.main()
