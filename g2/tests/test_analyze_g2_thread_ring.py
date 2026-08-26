import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ThreadRingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('thread_ring',ROOT/'tools/analyze_g2_thread_ring.py');cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface_and_recovered_entry(self):
  expected={'linked_functions':17,'ghidra_discovered_functions':5,'restored_functions':12,'path_anchored_functions':5,'raw_path_references':22,'raw_path_referencing_functions':9,'body_bytes':2374,'physical_bytes':2632,'outer_pool_bytes':258,'reachable_instructions':861,'direct_body_calls':171,'internal_direct_body_calls':9,'external_direct_body_calls':162,'indirect_body_calls':0,'direct_bl_entry_sites':21,'stored_entry_pointers':8,'strict_interior_ingress':0}
  for key,value in expected.items():self.assertEqual(self.r['surface'][key],value,key)
 def test_rtos_and_heap_provenance(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['cmsis_freertos_calls'],p['freertos_assert_calls'],p['iar_dlib_calls'],p['source_owned_heap_wrapper_calls'],p['closed_ring_service_calls'],p['event_loop_calls'],p['other_first_party_calls']),(110,10,2,2,3,13,16,6));self.assertEqual(p['cmsis_freertos_commit'],'d213f261b5be6bb29a7cce8b84071706b72f4d53');self.assertEqual(p['freertos_kernel_commit'],'def7d2df2b0506d3d249334974f51e427c17a41c');self.assertEqual(p['tlsf_commit'],'deff9ab509341f264addbd3c8ada533678591905');self.assertEqual(set(p['cmsis_wrappers']),{'osThreadNew','osThreadTerminate','osThreadFlagsSet','osThreadFlagsWait','osDelay','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet','osMessageQueueDelete'});self.assertFalse(p['new_version_discriminator']);self.assertIsNone(p['historical_thread_ring_commit'])
 def test_no_embedded_dependency_and_production_route(self):
  self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertTrue(self.r['production']['production_routed']);self.assertTrue(self.r['production']['source_inventory_available']);self.assertEqual((self.r['production']['ownership_bytes'],self.r['production']['retained_compatibility_bytes'],self.r['production']['compiled_text_bytes'],self.r['production']['generated_alignment_bytes'],self.r['production']['strict_relocations'],self.r['production']['guarded_redirects']),(2370,262,894,22,72,15));self.assertEqual(self.r['production']['hardware_validation'],'blocked_unavailable_physical_evidence');self.assertTrue(all(self.r['behavior'].values()))
if __name__=='__main__':unittest.main()
