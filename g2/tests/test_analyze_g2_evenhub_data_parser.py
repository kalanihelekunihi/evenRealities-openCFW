import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_evenhub_data_parser.py";S=importlib.util.spec_from_file_location("g2_evenhub_data_parser",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2EvenhubDataParserTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions'],s['path_anchored_functions'],s['function_interval_bytes'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(19,17,2,12,10496,10336,10874,538,3819));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(590,49,541,0,93,0,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['nanopb_calls'],p['cmsis_freertos_calls'],p['lvgl_calls'],p['iar_dlib_calls'],p['source_owned_heap_wrapper_calls'],p['first_party_calls']),(385,25,3,14,54,12,48));self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
