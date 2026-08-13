import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ExitPromptTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("exit_prompt",ROOT/"tools/analyze_g2_exit_prompt.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":5,"ghidra_discovered_functions":2,"additional_recovered_functions":3,"path_anchored_functions":2,"body_bytes":782,"physical_bytes":900,"outer_pool_bytes":118,"direct_body_calls":56,"internal_direct_body_calls":3,"external_direct_body_calls":53,"direct_bl_entry_sites":17,"stored_entry_pointers":3,"indirect_body_calls":0}
  for key,value in expected.items():self.assertEqual(self.r["surface"][key],value,key)
 def test_providers(self):
  p=self.r["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["lvgl_calls"],p["first_party_calls"]),(35,15,3));self.assertEqual(p["lvgl_commit"],"344c7c318047b7348e1be8572a9fd4260c251cfa");self.assertFalse(p["new_version_discriminator"]);self.assertEqual(self.r["identity"]["embedded_third_party_definitions"],[])
 def test_not_routed(self):self.assertFalse(self.r["production"]["production_routed"])
if __name__=="__main__":unittest.main()
