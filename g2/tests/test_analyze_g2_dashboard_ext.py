import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_dashboard_ext.py";S=importlib.util.spec_from_file_location("g2_dashboard_ext",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2DashboardExtTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(16,10,6,5904,7806,1902,2142));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['unaligned_word_pseudo_pointers'],s['strict_interior_ingress']),(315,24,291,0,32,0,13,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['iar_dlib_calls'],p['source_owned_file_runtime_calls'],p['nanopb_calls'],p['freertos_calls'],p['first_party_calls']),(220,18,16,5,3,29));self.assertFalse(p['new_version_discriminator']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
