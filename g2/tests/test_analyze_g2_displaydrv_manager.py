import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_displaydrv_manager.py";S=importlib.util.spec_from_file_location("g2_displaydrv_manager",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2DisplaydrvManagerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(19,7,12,2796,3070,274,1035));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['stored_interior_callback_pointers'],s['raw_overlapping_pseudo_bl_sites'],s['strict_interior_ingress']),(184,6,178,0,18,6,1,1,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['cmsis_freertos_calls'],p['iar_dlib_calls'],p['first_party_uled_display_calls'],p['direct_lvgl_calls'],p['direct_ambiqsuite_calls']),(125,20,11,22,0,0));self.assertFalse(p['new_version_discriminator']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
