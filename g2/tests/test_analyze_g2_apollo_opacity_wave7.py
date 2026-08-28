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
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave7.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave7/typed_boundaries.tsv"
INTERIORS = G2 / "research/admission/apollo_opacity_wave7/reconciled_interiors.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave7-vector-clipping-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave7", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave7Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave6_residual_and_root_are_pinned(self) -> None:
        self.assertEqual(self.report["wave6_residual"], {"functions": 1388, "bytes": 167922})
        self.assertEqual(self.report["before"], self.report["wave6_residual"])
        self.assertEqual(self.report["selected_root_range"], {"start": "0x00564974", "end_exclusive": "0x0056539A"})

    def test_complete_actionable_graph_is_closed(self) -> None:
        self.assertEqual(self.report["newly_typed"], {"functions": 2, "bytes": 4784})
        self.assertEqual(self.report["closure_depths"], {"0": {"typed_functions": 1, "typed_bytes": 2598}, "1": {"typed_functions": 1, "typed_bytes": 2186}})
        self.assertEqual(self.report["terminal_frontier"], {"functions": 0})

    def test_shared_and_interior_bytes_are_reconciled_once(self) -> None:
        self.assertEqual(self.report["reconciled_interiors"], {"islands": 4, "physical_bytes": 22, "additional_bytes": 0, "shared_pointer_cell": "0x00564A40"})
        rows = self.report["interior_records"]
        self.assertEqual(sum(row["size"] for row in rows), 22)
        shared = next(row for row in rows if row["data_address"] == "0x00564A40")
        self.assertEqual(shared["consumers"], ["0x005640E4", "0x00564974"])
        self.assertTrue(all(row["wave7_additional_bytes"] == 0 for row in rows))

    def test_bodies_are_sha_pinned_and_fail_closed(self) -> None:
        records = self.report["records"]
        self.assertEqual(len(records), 2)
        self.assertTrue(all(row["disposition"] == "typed-external-provider-unavailable" for row in records))
        self.assertTrue(all(row["license_status"] == "unavailable" for row in records))
        self.assertTrue(all(not row["callable_implementation_available"] for row in records))
        self.assertEqual(
            self.report["mapping_sha256"],
            "e827320e493b0759f27908de29bb199f2a4bcd17fdbc87e62a77b69514390d84",
        )

    def test_provider_context_does_not_become_source_identity(self) -> None:
        provider = self.report["provider"]
        self.assertEqual(provider["authenticated_function_identities"], [])
        self.assertIsNone(provider["authenticated_provider"])
        self.assertIsNone(provider["authenticated_license"])
        self.assertEqual(provider["callers"]["0x00564974"], ["0x005653A0", "0x005657D8"])

    def test_accounting_and_next_envelope(self) -> None:
        self.assertEqual(self.report["after"], {"functions": 1386, "bytes": 163138})
        self.assertEqual(self.report["largest_remaining"], {"entry": "0x005A8D06", "envelope_bytes": 2338})

    def test_table_mutations_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            boundary = temp_path / "typed.tsv"
            boundary.write_text(BOUNDARY.read_text().replace("\t2598\t2588\t", "\t2596\t2588\t", 1))
            interiors = temp_path / "interiors.tsv"
            interiors.write_text(INTERIORS.read_text().replace("00bf0100803f", "00bf0000803f", 1))
            old_boundary, old_interiors = self.analyzer.BOUNDARY, self.analyzer.INTERIORS
            try:
                self.analyzer.BOUNDARY = boundary
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.INTERIORS = interiors
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
            finally:
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.INTERIORS = old_interiors

    def test_research_only_and_deterministic_cli(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave7", path.read_text(errors="ignore"))
        self.assertIn("Production admission", DOC.read_text())
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "opacity-wave7-vector-clipping-closure-typed")


if __name__ == "__main__":
    unittest.main()
