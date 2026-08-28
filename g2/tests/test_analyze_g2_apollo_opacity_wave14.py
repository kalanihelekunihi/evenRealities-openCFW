# SPDX-License-Identifier: MIT
from __future__ import annotations
import importlib.util, sys, unittest
from pathlib import Path

G2=Path(__file__).resolve().parents[1]
ANALYZER=G2/"tools/analyze_g2_apollo_opacity_wave14.py"
DOC=G2/"docs/research/g2-apollo-opacity-wave14-freetype-cff-glyph-load-closure.md"

def load_analyzer():
    spec=importlib.util.spec_from_file_location("apollo_opacity_wave14",ANALYZER); assert spec is not None and spec.loader is not None
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module

class ApolloOpacityWave14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.analyzer=load_analyzer();cls.report=cls.analyzer.run_audit()
    def test_wave13_residual_and_root(self):
        self.assertEqual(self.report["wave13_residual"],{"functions":1297,"bytes":136482});self.assertEqual(self.report["before"],self.report["wave13_residual"])
        self.assertEqual(self.report["selected_root_range"],{"start":"0x005AC66E","end_exclusive":"0x005ACD02"})
    def test_complete_source_closure(self):
        self.assertEqual(self.report["actionable_graph"],{"source_functions":5,"source_bytes":2006,"closure_depth_max":1,"static_terminal_functions":9,"dynamic_interfaces":6})
        self.assertEqual(self.report["source_attributed"],{"functions":5,"bytes":2006,"provider":"FreeType-2.9.1-VER-2-9-1","license":"FTL"})
    def test_exact_symbols(self):
        self.assertEqual({r["symbol"] for r in self.report["records"]},{"cff_slot_load","cff_get_glyph_data","cff_free_glyph_data","cff_fd_select_get","ft_synthesize_vertical_metrics"})
        self.assertTrue(all(r["source_identity_authenticated"] for r in self.report["records"]))
    def test_ranges_and_data(self):
        self.assertEqual(self.report["range_partition"],{"functions":5,"interior_islands":0,"interior_physical_bytes":0})
        self.assertEqual(self.report["shared_data"],{"direct_cells":4,"physical_bytes":16,"additional_function_bytes":0})
    def test_residual_and_mapping(self):
        self.assertEqual(self.report["after"],{"functions":1292,"bytes":134476});self.assertEqual(self.report["largest_remaining"],{"entry":"0x0051B8F0","envelope_bytes":1668})
        self.assertEqual(self.report["mapping_sha256"],"6efe9d2bb07b1e7b1a6db87f9d7b3b6c3203a248ebc4136961f8955e05d5abd7")
    def test_research_only_production_exclusion(self):
        self.assertTrue(self.report["read_only"]);self.assertFalse(self.report["hardware_operations"]);self.assertFalse(self.report["production_routed"])
        for path in (G2/"Makefile",G2/"tools/open_cfw.py",G2/"tools/apollo_overlay.py"): self.assertNotIn("apollo_opacity_wave14",path.read_text(errors="ignore"))
        self.assertIn("## Production admission",DOC.read_text())

if __name__=="__main__": unittest.main()
