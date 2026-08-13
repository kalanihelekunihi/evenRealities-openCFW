import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_display_thread.py";S=importlib.util.spec_from_file_location("g2_display_thread",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2DisplayThreadTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(27,13,14,9100,9834,734,3370));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(545,23,522,12,201,3,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['cmsis_freertos_calls'],p['freertos_calls'],p['lvgl_calls'],p['iar_dlib_calls'],p['source_owned_runtime_calls'],p['first_party_calls']),(310,21,11,12,23,5,140));self.assertFalse(p['new_version_discriminator']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertTrue(self.r['production']['production_routed']);self.assertEqual(self.r['production']['source_routed_functions'],2)
if __name__=='__main__':unittest.main()
