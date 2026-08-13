import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_evenhub_ui.py";S=importlib.util.spec_from_file_location("g2_evenhub_ui",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2EvenhubUiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(26,10,16,21,14296,15568,1272,5159));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['bounded_indirect_targets'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(855,32,823,2,3,44,10,0))
 def test_provider_and_callback_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['lvgl_calls'],p['nanopb_calls'],p['iar_dlib_calls'],p['source_owned_heap_wrapper_calls'],p['closed_lz4_adapter_calls'],p['first_party_calls']),(690,37,7,22,10,2,55));self.assertEqual((p['indirect_callback_sites'],p['bounded_indirect_targets']),(2,3));self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
