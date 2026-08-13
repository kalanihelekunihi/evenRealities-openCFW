import importlib.util
import sys
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_message_notify.py"
S = importlib.util.spec_from_file_location("g2_message_notify", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class ZeroAnchorClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = M.analyze()

    def test_identity(self):
        self.assertEqual(self.r["identity"], {'disposition': 'linked-unanchored', 'ghidra_discovered_functions': 0, 'image_sha256': '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863', 'path_anchored_functions': 0, 'retained_path': 'app\\gui\\MessageNotify\\message_notify.c', 'retained_product_path': 'D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\MessageNotify\\message_notify.c'})

    def test_surface(self):
        self.assertEqual(self.r["surface"], {'body_bytes': 1016, 'direct_body_calls': 62, 'function_escapes': 0, 'indirect_body_calls': 0, 'internal_direct_body_calls': 1, 'linked_functions': 4, 'outer_pool_bytes': 84, 'path_literal_references': 5, 'physical_bytes': 1100, 'raw_path_referencing_functions': 3, 'reachable_instructions': 422})

    def test_ingress(self):
        self.assertEqual(self.r["ingress"], {'direct_b16_entry_sites': 0, 'direct_bl_entry_sites': 1, 'direct_bl_strict_interior_sites': 0, 'direct_bw_entry_sites': 0, 'stored_entry_pointer_words': 2})

    def test_evidence_and_production(self):
        self.assertEqual(self.r["evidence"], {'boundary_guards': True, 'pointer_cells': ['0x004E1F38'], 'path_string_run_address': '0x006F45B8', 'tag_strings': 5})
        self.assertFalse(self.r["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
