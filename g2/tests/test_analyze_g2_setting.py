import importlib.util
import sys
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_setting.py"
S = importlib.util.spec_from_file_location("g2_setting", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class ZeroAnchorClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = M.analyze()

    def test_identity(self):
        self.assertEqual(self.r["identity"], {'disposition': 'linked-unanchored', 'ghidra_discovered_functions': 0, 'image_sha256': '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863', 'path_anchored_functions': 0, 'retained_path': 'app\\gui\\setting\\setting.c', 'retained_product_path': 'D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c'})

    def test_surface(self):
        self.assertEqual(self.r["surface"], {'body_bytes': 5486, 'direct_body_calls': 361, 'function_escapes': 0, 'indirect_body_calls': 0, 'internal_direct_body_calls': 16, 'linked_functions': 18, 'outer_pool_bytes': 286, 'path_literal_references': 51, 'physical_bytes': 5772, 'raw_path_referencing_functions': 15, 'reachable_instructions': 2024})

    def test_ingress(self):
        self.assertEqual(self.r["ingress"], {'direct_b16_entry_sites': 0, 'direct_bl_entry_sites': 17, 'direct_bl_strict_interior_sites': 0, 'direct_bw_entry_sites': 0, 'stored_entry_pointer_words': 4})

    def test_evidence_and_production(self):
        self.assertEqual(self.r["evidence"], {'boundary_guards': True, 'pointer_cells': ['0x004672EC', '0x00467F10'], 'path_string_run_address': '0x0070F3A4', 'tag_strings': 51})
        self.assertFalse(self.r["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
