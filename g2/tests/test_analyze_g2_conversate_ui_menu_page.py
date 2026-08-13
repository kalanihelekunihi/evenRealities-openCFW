import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ConversateUiMenuPageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("conv_menu",ROOT/"tools/analyze_g2_conversate_ui_menu_page.py"); cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":8,"ghidra_discovered_functions":2,"additional_recovered_functions":6,"path_anchored_functions":1,"body_bytes":1492,"physical_bytes":1592,"outer_pool_bytes":100,"direct_bl_entry_sites":7,"direct_body_calls":102,"internal_direct_body_calls":1,"external_direct_body_calls":101,"stored_entry_pointers":5,"indirect_body_calls":0,"strict_interior_raw_bl_decodes":0}
  for k,v in expected.items(): self.assertEqual(self.r["surface"][k],v,k)
 def test_providers(self):
  p=self.r["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["lvgl_calls"],p["first_party_calls"]),(35,34,32));self.assertEqual(p["lvgl_commit"],"344c7c318047b7348e1be8572a9fd4260c251cfa");self.assertFalse(p["new_version_discriminator"]);self.assertEqual(self.r["identity"]["embedded_third_party_definitions"],[])
 def test_not_routed(self): self.assertFalse(self.r["production"]["production_routed"])
if __name__=="__main__":unittest.main()
