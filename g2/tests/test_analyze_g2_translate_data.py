import importlib.util
import sys
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_translate_data.py"
S = importlib.util.spec_from_file_location("g2_translate_data", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class ZeroAnchorAttestationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = M.analyze()

    def test_identity(self):
        self.assertEqual(self.r["identity"], {'disposition': 'linked-unanchored-previously-claimed', 'ghidra_discovered_functions': 0, 'image_sha256': '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863', 'path_anchored_functions': 0, 'retained_path': 'app\\gui\\translate\\translate_data.c', 'retained_product_path': 'D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\translate\\translate_data.c'})

    def test_surface_and_covering(self):
        self.assertEqual(self.r["surface"], {'body_bytes': 0, 'linked_functions': 0, 'path_literal_references': 5, 'physical_bytes': 0})
        self.assertEqual(self.r["covering"], {'covering_body_bytes': 786, 'covering_manifest': 'g2-translate-ui-function-map.tsv', 'covering_rows': 1})

    def test_production(self):
        self.assertFalse(self.r["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
