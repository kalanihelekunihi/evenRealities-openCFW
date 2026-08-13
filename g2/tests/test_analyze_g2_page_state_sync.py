import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_page_state_sync.py';S=importlib.util.spec_from_file_location('analyze_g2_page_state_sync',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class PageStateSyncTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(8,2,1244,1380));self.assertEqual((s['direct_bl_entry_sites'],s['indirect_body_calls'],s['strict_interior_ingress'],s['stored_function_entry_pointers']),(27,0,0,0));self.assertEqual(s['raw_instruction_word_interior_collisions'],22)
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','nanopb_calls','first_party_calls')),(50,3,1,3));self.assertIsNone(p['historical_page_state_sync_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
