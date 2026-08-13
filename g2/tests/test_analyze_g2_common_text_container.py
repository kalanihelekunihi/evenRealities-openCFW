import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_common_text_container.py";S=importlib.util.spec_from_file_location("g2_common_text_container",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2CommonTextContainerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(13,10,3,11,6966,7740,774,2509));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['bounded_indirect_targets'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(445,19,426,4,1,24,3,0))
 def test_provider_and_callback_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['lvgl_calls'],p['iar_dlib_calls'],p['source_owned_heap_wrapper_calls'],p['first_party_calls'],p['navigation_callback_calls']),(325,78,5,6,12,4));self.assertEqual(p['navigation_callback_target'],"0x00494A78");self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
