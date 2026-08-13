import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_dashboard_watchface_layout4.py";S=importlib.util.spec_from_file_location("g2_dashboard_watchface_layout4",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2DashboardWatchfaceLayout4Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(23,20,3,4184,4606,422,1583));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['raw_overlapping_pseudo_bl_sites'],s['strict_interior_ingress']),(248,18,230,0,18,11,1,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['lvgl_calls'],p['iar_dlib_calls'],p['ambiqsuite_calls'],p['first_party_calls']),(60,122,14,3,31));self.assertFalse(p['new_version_discriminator']);self.assertFalse(p['private_generating_commit_recoverable']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
