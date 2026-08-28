# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave13.py"
DOC = G2 / "docs/research/g2-apollo-opacity-wave13-liblc3-ltpf-source-closure.md"
ADMISSION = G2 / "research/admission/apollo_opacity_wave13"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave13", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave12_residual_and_selected_delta_are_pinned(self) -> None:
        self.assertEqual(self.report["wave12_residual"], {"functions": 1308, "bytes": 140498})
        self.assertEqual(self.report["before"], self.report["wave12_residual"])
        self.assertEqual(self.report["selected_root_range"], {"start":"0x00438FB8","end_exclusive":"0x00439666"})

    def test_complete_static_and_indirect_graph(self) -> None:
        self.assertEqual(self.report["actionable_graph"], {"selected_functions":11,"official_bytes":4016,"static_root_closure_functions":6,"indirect_residual_functions":4,"shared_indirect_callee_functions":1,"static_terminal_relations":1,"indirect_slots":7})
        self.assertEqual(self.report["reconciled_zero_opaque"], {"functions":1,"bytes":0,"provider":"IAR-DLIB-proprietary-runtime"})

    def test_qualified_source_and_license_are_exact(self) -> None:
        self.assertEqual(self.report["source_attributed"]["functions"], 10)
        self.assertEqual(self.report["source_attributed"]["bytes"], 4016)
        self.assertEqual(self.report["source_attributed"]["license"], "Apache-2.0")
        self.assertFalse(self.report["source_attributed"]["exact_generating_checkout_proven"])

    def test_non_corpus_entries_fail_closed(self) -> None:
        self.assertEqual(self.report["non_corpus_boundaries"], {"entries":2,"bounded_physical_bytes":624,"official_bytes":0,"complete_body_proven":False})

    def test_interior_and_data_graphs_are_exhaustive(self) -> None:
        self.assertEqual(self.report["range_partition"], {"functions_with_interiors":2,"interior_islands":11,"interior_physical_bytes":46,"additional_function_bytes":0})
        self.assertEqual(self.report["shared_data"], {"spans":18,"physical_bytes":2204,"byte_exact_upstream_tables":8,"additional_function_bytes":0})

    def test_residual_and_next_root_are_deterministic(self) -> None:
        self.assertEqual(self.report["after"], {"functions":1297,"bytes":136482})
        self.assertEqual(self.report["largest_remaining"], {"entry":"0x005AC66E","envelope_bytes":1684})
        self.assertEqual(self.report["mapping_sha256"], "e458feddf55b41e8cf4425a6ac6125021a5a55878cb9374e7e015a19276d174f")

    def test_source_route_is_production_admitted_but_hardware_free(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertTrue(self.report["production_routed"])
        self.assertEqual(self.report["production_capable_source"], {"available":True,"provider_entry":"open_cfw_liblc3_ltpf_analyse_bounded","dispatch_slots":7,"historical_individual_bodies_routed":False})
        self.assertEqual(self.report["production_route"]["unresolved_runtime_symbols"], 0)
        self.assertEqual(self.report["production_route"]["profiles"]["apple-clang"]["source_owned_bytes"], 7576)
        self.assertEqual(self.report["production_route"]["profiles"]["linux-clang"]["source_owned_bytes"], 7596)
        self.assertFalse(self.report["production_route"]["historical_individual_bodies_routed"])
        self.assertIn("device qualification", self.report["production_blocker"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave13", path.read_text(errors="ignore"))
        self.assertIn("## Production admission", DOC.read_text())
        self.assertTrue((ADMISSION / "source_provider.json").is_file())


if __name__ == "__main__":
    unittest.main()
