import importlib.util
import sys
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_system_alert.py"
S = importlib.util.spec_from_file_location("g2_system_alert", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class ZeroAnchorClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = M.analyze()

    def test_identity(self):
        self.assertEqual(self.r["identity"], {'disposition': 'linked-unanchored', 'ghidra_discovered_functions': 0, 'image_sha256': '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863', 'path_anchored_functions': 0, 'retained_path': 'app\\gui\\SystemAlert\\systemAlert.c', 'retained_product_path': 'D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\SystemAlert\\systemAlert.c'})

    def test_surface(self):
        self.assertEqual(self.r["surface"], {'body_bytes': 2176, 'direct_body_calls': 171, 'function_escapes': 0, 'indirect_body_calls': 0, 'internal_direct_body_calls': 2, 'linked_functions': 7, 'outer_pool_bytes': 170, 'path_literal_references': 12, 'physical_bytes': 2346, 'raw_path_referencing_functions': 4, 'reachable_instructions': 829})

    def test_ingress(self):
        self.assertEqual(self.r["ingress"], {'direct_b16_entry_sites': 0, 'direct_bl_entry_sites': 7, 'direct_bl_strict_interior_sites': 1, 'direct_bw_entry_sites': 0, 'stored_entry_pointer_words': 2})

    def test_evidence_and_production(self):
        self.assertEqual(self.r["evidence"], {'boundary_guards': True, 'pointer_cells': ['0x004D3424'], 'path_string_run_address': '0x006FD85C', 'tag_strings': 12})
        self.assertEqual(self.r["production"], {
            "source_admitted": True,
            "production_routed": True,
            "source_functions": 7,
            "compiled_text_bytes": 1138,
            "compiled_rodata_bytes": 51,
            "alignment_bytes": 9,
            "stock_replaced_bytes": 2174,
            "retained_literal_pool_bytes": 172,
            "strict_relocations": 85,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": "No authorized responsive G2 pair is available for dual-temple lifecycle, delayed-exit, translation, and rendered-display validation.",
        })


if __name__ == "__main__":
    unittest.main()
