import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_translate_fsm.py';S=importlib.util.spec_from_file_location('analyze_g2_translate_fsm',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class TranslateFsmTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(8,6,1304,1448));self.assertEqual((s['direct_bl_entry_sites'],s['indirect_body_calls'],s['strict_interior_ingress'],s['stored_function_entry_pointers']),(11,1,0,6));self.assertEqual(s['indirect_dispatch_bounded_by_stored_state_table'],6)
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','nanopb_calls','first_party_calls')),(55,4,3,24));self.assertIsNone(p['historical_translate_fsm_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
