import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_common_list_container.py";S=importlib.util.spec_from_file_location("g2_common_list_container",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2CommonListContainerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(14,7342,8588,1246,2710));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['bounded_indirect_targets'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(458,39,419,2,1,46,2,0))
 def test_provider_and_callback_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['lvgl_calls'],p['iar_dlib_calls'],p['source_owned_heap_wrapper_calls'],p['first_party_calls'],p['selection_callback_calls']),(310,91,3,6,9,2));self.assertEqual(p['selection_callback_target'],"0x004949C0");self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
