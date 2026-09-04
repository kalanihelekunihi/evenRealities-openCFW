import importlib.util
import sys
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_s200_board_config.py"
S = importlib.util.spec_from_file_location("g2_s200_board_config", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class ZeroAnchorClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = M.analyze()

    def test_identity(self):
        self.assertEqual(self.r["identity"], {'disposition': 'linked-unanchored', 'ghidra_discovered_functions': 0, 'image_sha256': '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863', 'path_anchored_functions': 0, 'retained_path': 'product\\s200\\app\\config\\board_config.c', 'retained_product_path': 'D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\app\\config\\board_config.c'})

    def test_surface(self):
        self.assertEqual(self.r["surface"], {'body_bytes': 114, 'direct_body_calls': 9, 'function_escapes': 0, 'indirect_body_calls': 0, 'internal_direct_body_calls': 0, 'linked_functions': 1, 'outer_pool_bytes': 586, 'path_literal_references': 1, 'physical_bytes': 700, 'raw_path_referencing_functions': 1, 'reachable_instructions': 46})

    def test_ingress(self):
        self.assertEqual(self.r["ingress"], {'direct_b16_entry_sites': 0, 'direct_bl_entry_sites': 0, 'direct_bl_strict_interior_sites': 0, 'direct_bw_entry_sites': 0, 'stored_entry_pointer_words': 1})

    def test_evidence_and_production(self):
        self.assertEqual(self.r["evidence"], {'boundary_guards': True, 'pointer_cells': ['0x005094B8'], 'path_string_run_address': '0x006F1BDC', 'tag_strings': 1})
        self.assertEqual(self.r["production"], {
            'alignment_bytes': {'apple-clang': 0, 'linux-clang': 0},
            'candidate': 'components/apollo_main/core_overlay/s200_board_config.c',
            'compiled_text_bytes': {'apple-clang': 38, 'linux-clang': 38},
            'hardware_evidence_required': [
                'authorized G2 examples of both supported charger families, or authenticated golden traces, proving selector-3 record decoding, nPMx versus BQ dispatch, BQ25180-before-BQ27427 ordering, and resulting rail, charging, and fuel-gauge behavior'
            ],
            'hardware_operations': [],
            'hardware_validation': 'blocked by unavailable physical evidence',
            'header': 'components/apollo_main/core_overlay/s200_board_config.h',
            'ownership_bytes': 114,
            'production_routed': True,
            'profiles_verified': ['apple-clang', 'linux-clang'],
            'retained_stock_noncode_bytes': 586,
            'software_functional_gap': False,
            'source_functions': 1,
            'source_inventory_available': True,
            'stock_body_bytes_displaced': 114,
            'strict_relocations': 4,
        })


if __name__ == "__main__":
    unittest.main()
