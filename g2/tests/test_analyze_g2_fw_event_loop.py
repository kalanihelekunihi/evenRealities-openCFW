import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class FwEventLoopTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('fw_event_loop',ROOT/'tools/analyze_g2_fw_event_loop.py');cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_complete_stock_surface(self):
  expected={'linked_functions':6,'ghidra_discovered_functions':5,'restored_functions':1,'path_anchored_functions':5,'raw_path_references':16,'raw_path_referencing_functions':6,'body_bytes':1806,'physical_bytes':2012,'noncode_bytes':206,'reachable_instructions':661,'direct_body_calls':108,'internal_direct_body_calls':4,'external_direct_body_calls':104,'indirect_body_calls':1,'bounded_indirect_body_calls':1,'direct_bl_entry_sites':198,'stored_entry_pointers':0,'raw_interior_word_collisions':1,'strict_interior_ingress':0}
  for key,value in expected.items():self.assertEqual(self.r['surface'][key],value,key)
 def test_dependency_boundary(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['cmsis_freertos_calls'],p['freertos_critical_port_calls'],p['bounded_first_party_indirect_calls']),(80,20,4,1));self.assertEqual(p['cmsis_freertos_commit'],'d213f261b5be6bb29a7cce8b84071706b72f4d53');self.assertEqual(p['freertos_kernel_commit'],'def7d2df2b0506d3d249334974f51e427c17a41c');self.assertFalse(p['new_version_discriminator']);self.assertIsNone(p['historical_fw_event_loop_commit'])
 def test_production_source_route(self):
  self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertEqual(self.r['production'],{'production_routed':True,'source_routed_functions':6,'source_sha256':'e1ac9d2f18f411d712b771a3b698c89de9a340843bc26294e629e14b6e915ccc'});self.assertTrue(all(self.r['behavior'].values()))
if __name__=='__main__':unittest.main()
