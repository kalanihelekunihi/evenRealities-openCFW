import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class HalI2cTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("hal_i2c",ROOT/"tools/analyze_g2_hal_i2c.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":9,"ghidra_discovered_functions":9,"path_anchored_functions":1,"body_bytes":1584,"physical_bytes":1624,"outer_pool_bytes":40,"direct_body_calls":65,"internal_direct_body_calls":15,"external_direct_body_calls":50,"indirect_body_calls":0,"direct_bl_entry_sites":35,"stored_entry_pointers":1}
  for key,value in expected.items():self.assertEqual(self.r["surface"][key],value,key)
 def test_providers(self):
  p=self.r["provider_boundary"];self.assertEqual((p["ambiqsuite_calls"],p["cmsis_freertos_calls"],p["easylogger_calls"],p["nanopb_calls"],p["iar_dlib_calls"],p["first_party_delay_calls"]),(21,15,5,4,3,2));self.assertEqual(p["ambiqsuite_commit"],"5efc0228528a8adce5eae0d226fac85d2551eb3b");self.assertFalse(p["new_version_discriminator"])
 def test_not_routed(self):self.assertFalse(self.r["production"]["production_routed"])
if __name__=="__main__":unittest.main()
