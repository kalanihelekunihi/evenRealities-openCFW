import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class AtCoreTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("at_core",ROOT/"tools/analyze_g2_at_core.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":5,"ghidra_discovered_functions":4,"additional_recovered_functions":1,"path_anchored_functions":2,"body_bytes":666,"physical_bytes":724,"outer_pool_bytes":58,"direct_body_calls":21,"internal_direct_body_calls":1,"external_direct_body_calls":20,"indirect_body_calls":4,"direct_bl_entry_sites":85,"stored_entry_pointers":0}
  for key,value in expected.items():self.assertEqual(self.r["surface"][key],value,key)
 def test_providers(self):
  p=self.r["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["iar_dlib_calls"],p["first_party_parser_calls"]),(10,6,4));self.assertFalse(p["new_version_discriminator"]);self.assertFalse(self.r["identity"]["public_source_fingerprint_match"]);self.assertEqual(self.r["identity"]["embedded_third_party_definitions"],[])
 def test_not_routed(self):self.assertFalse(self.r["production"]["production_routed"])
if __name__=="__main__":unittest.main()
