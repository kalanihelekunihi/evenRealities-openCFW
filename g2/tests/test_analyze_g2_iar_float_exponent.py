import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class IarFloatExponentTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('iar_float_exponent',ROOT/'tools/analyze_g2_iar_float_exponent.py');cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_complete_surface(self):
  self.assertEqual(self.r['surface'],{'linked_functions':3,'body_bytes':268,'physical_bytes':268,'reachable_instructions':96,'direct_bl_entry_sites':10,'external_public_entry_sites':9,'internal_direct_calls':1,'stored_entry_pointers':0,'strict_interior_ingress':0})
 def test_iar_identity_is_bounded_not_overclaimed(self):
  i=self.r['identity'];self.assertEqual(i['family'],'IAR-DLIB');self.assertEqual(i['version_floor'],'9.20+');self.assertEqual(i['leading_compatibility_candidate'],'9.60.2');self.assertIsNone(i['exact_release']);self.assertIsNone(i['source_commit']);self.assertFalse(self.r['provenance']['new_exact_release_discriminator'])
 def test_gap_is_explicit(self):
  self.assertTrue(all(self.r['behavior'].values()));self.assertTrue(self.r['production']['production_routed']);self.assertFalse(self.r['production']['remaining_functional_gap']);self.assertEqual(self.r['production']['production_profiles'],['apple-clang']);self.assertEqual(self.r['production']['pending_profiles'],['linux-clang']);self.assertTrue(self.r['production']['exact_stock_reproduction'])
if __name__=='__main__':unittest.main()
