import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_sync_framework.py";S=importlib.util.spec_from_file_location("g2_sync_framework",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2SyncFrameworkTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions'],s['path_anchored_functions'],s['function_interval_bytes'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(43,23,20,23,16960,16816,18180,1364,6083));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(1070,19,1051,14,79,24,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['cmsis_freertos_calls'],p['freertos_kernel_calls'],p['tinyframe_calls'],p['ambiqsuite_calls'],p['nanopb_calls'],p['iar_dlib_calls'],p['source_owned_heap_wrapper_calls'],p['thread_pool_calls'],p['delay_wrapper_calls'],p['first_party_calls']),(825,35,4,26,2,1,17,86,18,1,36));self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(p['new_version_discriminator'])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
