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
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave8.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave8/typed_boundaries.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave8-font-sequence-freetype-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave8", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave7_residual_and_selected_root_are_pinned(self) -> None:
        self.assertEqual(self.report["wave7_residual"], {"functions": 1386, "bytes": 163138})
        self.assertEqual(self.report["before"], self.report["wave7_residual"])
        self.assertEqual(self.report["selected_root_range"], {"start": "0x005A8D06", "end_exclusive": "0x005A9628"})

    def test_complete_call_and_range_graph_is_closed(self) -> None:
        self.assertEqual(self.report["actionable_graph"], {"positive_functions": 28, "positive_bytes": 5370, "zero_opaque_functions": 1, "terminal_functions": 6, "call_edges": 38})
        self.assertEqual(self.report["range_partition"], {"functions": 29, "interior_gap_bytes": 0})
        self.assertEqual(self.report["closure_depths"]["3"], {"positive_functions": 8, "positive_bytes": 678, "zero_opaque_functions": 1})
        self.assertEqual(len(self.report["frontier_records"]), 6)

    def test_exact_freetype_source_and_ftl_are_retained(self) -> None:
        self.assertEqual(self.report["source_attributed"], {"functions": 20, "bytes": 2552, "provider": "FreeType 2.9.1", "license": "FTL", "production_codegen_exact": False})
        source = [row for row in self.report["records"] if row["source_identity_authenticated"]]
        self.assertEqual(len(source), 20)
        self.assertTrue(all(row["license_status"] == "FTL" for row in source))
        self.assertIn("FT_Load_Glyph", {row["role"] for row in source})
        self.assertIn("FT_MulDiv", {row["role"] for row in source})
        verified = subprocess.run([sys.executable, str(G2 / "third_party/freetype/verify_snapshot.py")], check=True, capture_output=True, text=True)
        self.assertIn("snapshot verification passed", verified.stdout)

    def test_unavailable_product_and_runtime_rows_fail_closed(self) -> None:
        self.assertEqual(self.report["typed_unavailable"], {"positive_functions": 8, "positive_bytes": 2818, "zero_opaque_functions": 1})
        unavailable = [row for row in self.report["records"] if not row["source_identity_authenticated"]]
        self.assertTrue(all(row["disposition"] == "typed-external-provider-unavailable" for row in unavailable))
        self.assertEqual(self.report["zero_records"][0]["entry"], "0x00481818")
        self.assertEqual(self.report["zero_records"][0]["official_opaque_bytes"], 0)

    def test_direct_shared_data_and_unicode_pool_are_exhaustive(self) -> None:
        shared = self.report["shared_data"]
        self.assertEqual(shared["records"], 9)
        self.assertEqual(shared["physical_bytes"], 6264)
        self.assertEqual(shared["additional_function_bytes"], 0)
        self.assertEqual(shared["direct_dat_cells"], 5)
        self.assertEqual(shared["table_pool"], {"records": 250, "sentinel": 0x1469, "sentinel_records": 53, "unique_non_sentinel_offsets": 186, "maximum_offset": 0x139F, "flag_values": [0, 1, 2, 4, 9, 13, 17], "maximum_string_end": 0x1469})

    def test_accounting_and_next_envelope(self) -> None:
        self.assertEqual(self.report["after"], {"functions": 1357, "bytes": 157768})
        self.assertEqual(self.report["largest_remaining"], {"entry": "0x0051A8EC", "envelope_bytes": 2090})
        self.assertEqual(self.report["mapping_sha256"], "b67635188798a8d629c83be507f13bbf17caac1e13f43c4c9537b05fe3e842d6")

    def test_license_mutation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            mutated = Path(temp) / "typed.tsv"
            mutated.write_text(BOUNDARY.read_text().replace("\tFTL\tsource-attributed", "\tMIT\tsource-attributed", 1))
            old = self.analyzer.BOUNDARY
            try:
                self.analyzer.BOUNDARY = mutated
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
            finally:
                self.analyzer.BOUNDARY = old

    def test_research_only_deterministic_cli_and_production_exclusion(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave8", path.read_text(errors="ignore"))
        self.assertIn("## Production admission", DOC.read_text())
        result = subprocess.run([sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True)
        cli = json.loads(result.stdout)
        self.assertEqual(cli["mapping_sha256"], self.report["mapping_sha256"])
        self.assertEqual(cli["status"], "opacity-wave8-font-sequence-and-freetype-closure-reconciled")


if __name__ == "__main__":
    unittest.main()
