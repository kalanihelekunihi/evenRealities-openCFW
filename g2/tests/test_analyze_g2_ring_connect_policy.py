import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RingConnectPolicyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('ring_connect_policy',ROOT/'tools/analyze_g2_ring_connect_policy.py');cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_complete_stock_surface(self):
  expected={'linked_functions':15,'ghidra_discovered_functions':11,'restored_functions':4,'path_anchored_functions':12,'raw_path_references':19,'raw_path_referencing_functions':12,'body_bytes':1828,'physical_bytes':2056,'noncode_bytes':228,'reachable_instructions':702,'direct_body_calls':120,'internal_direct_body_calls':12,'external_direct_body_calls':108,'indirect_body_calls':0,'direct_bl_entry_sites':29,'stored_entry_pointers':1,'raw_interior_word_collisions':1,'strict_interior_ingress':0}
  for key,value in expected.items():self.assertEqual(self.r['surface'][key],value,key)
 def test_dependency_boundary(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['cmsis_freertos_calls'],p['closed_event_loop_calls'],p['closed_nanopb_facade_calls'],p['closed_ble_central_calls']),(95,1,10,1,1));self.assertEqual((p['direct_cordio_calls'],p['direct_nanopb_calls']),(0,0));self.assertEqual(p['cmsis_freertos_commit'],'d213f261b5be6bb29a7cce8b84071706b72f4d53');self.assertEqual(p['freertos_kernel_commit'],'def7d2df2b0506d3d249334974f51e427c17a41c');self.assertFalse(p['new_version_discriminator']);self.assertIsNone(p['historical_ring_connect_policy_commit'])
 def test_first_party_policy_only(self):
  self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed']);self.assertTrue(all(value for value in self.r['behavior'].values()))
if __name__=='__main__':unittest.main()
