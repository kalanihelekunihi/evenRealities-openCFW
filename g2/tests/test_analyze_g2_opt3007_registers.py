import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Opt3007RegistersTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("opt3007_registers",ROOT/"tools/analyze_g2_opt3007_registers.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":1,"ghidra_discovered_functions":1,"path_anchored_functions":1,"body_bytes":340,"physical_bytes":360,"outer_pool_bytes":20,"direct_body_calls":5,"internal_direct_body_calls":0,"external_direct_body_calls":5,"indirect_body_calls":0,"direct_bl_entry_sites":2,"stored_entry_pointers":0}
  for key,value in expected.items():self.assertEqual(self.r["surface"][key],value,key)
 def test_register_map(self):
  m=self.r["register_map"];self.assertEqual((m["descriptor_count"],m["descriptor_bytes"]),(19,57));self.assertEqual(m["descriptors"], [list(x) for x in self.m.DESCRIPTORS]);self.assertEqual(m["datasheet"],"TI SBOS864, August 2017");self.assertFalse(m["public_code_match"])
 def test_provider_and_routing(self):
  self.assertEqual(self.r["provider_boundary"]["easylogger_calls"],5);self.assertFalse(self.r["provider_boundary"]["new_version_discriminator"]);self.assertTrue(self.r["production"]["production_routed"]);self.assertEqual((self.r["production"]["compiled_text_bytes"],self.r["production"]["strict_relocations"]),(224,0));self.assertIn("deferred by project direction",self.r["production"]["hardware_validation"])
if __name__=="__main__":unittest.main()
