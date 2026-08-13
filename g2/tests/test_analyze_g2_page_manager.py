import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_page_manager.py';S=importlib.util.spec_from_file_location('analyze_g2_page_manager',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class PageManagerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(45,36,9,3,4510,4656,146));self.assertEqual((s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['indirect_body_calls'],s['strict_interior_ingress']),(112,7,12,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','lvgl_calls','source_owned_heap_wrapper_calls','closed_first_party_calls','iar_dlib_calls')),(27,96,5,7,4));self.assertIsNone(p['historical_page_manager_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
