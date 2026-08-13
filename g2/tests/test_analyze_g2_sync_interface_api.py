import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_sync_interface_api.py";S=importlib.util.spec_from_file_location("g2_sync_interface_api",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2SyncInterfaceApiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(13,0,6136,6432,296,2350));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(353,20,333,0,329,1,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['cmsis_freertos_calls'],p['freertos_assert_calls'],p['iar_dlib_calls'],p['source_owned_heap_wrapper_calls'],p['first_party_calls']),(255,17,9,13,33,6));self.assertFalse(p['new_version_discriminator']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
