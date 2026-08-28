import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ServiceRingBatteryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("service_ring_battery",ROOT/"tools/analyze_g2_service_ring_battery.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":5,"ghidra_discovered_functions":5,"path_anchored_functions":2,"body_bytes":352,"physical_bytes":396,"outer_pool_bytes":44,"direct_body_calls":19,"internal_direct_body_calls":0,"external_direct_body_calls":19,"indirect_body_calls":0,"direct_bl_entry_sites":9,"stored_entry_pointers":0}
  for key,value in expected.items():self.assertEqual(self.r["surface"][key],value,key)
 def test_providers(self):
  p=self.r["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["iar_dlib_calls"],p["first_party_transport_calls"]),(15,2,2));self.assertEqual(p["easylogger_commit"],"a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24");self.assertFalse(p["new_version_discriminator"])
 def test_production(self):
  p=self.r["production"]
  self.assertTrue(p["production_routed"])
  self.assertEqual((p["source_functions"],p["compiled_text_bytes"],p["alignment_bytes"],p["strict_relocations"],p["stock_replaced_bytes"],p["retained_literal_pool_bytes"]),(5,134,4,2,352,44))
  self.assertFalse(p["software_functional_gap"])
  self.assertEqual(p["hardware_validation"],"deferred by project direction")
 def test_behavior(self):
  b=self.r["behavior"]
  self.assertEqual((b["state_address"],b["service_record_id"],b["update_message_id"],b["request_message_id"],b["message_bytes"]),(0x20074F3A,0x105,5,6,12))
  self.assertTrue(b["charging_normalized"])
if __name__=="__main__":unittest.main()
