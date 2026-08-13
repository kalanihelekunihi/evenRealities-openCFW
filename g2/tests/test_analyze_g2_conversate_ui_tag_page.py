import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ConversateUiTagPageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("conv_tag",ROOT/"tools/analyze_g2_conversate_ui_tag_page.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":11,"body_bytes":2910,"physical_bytes":3056,"outer_pool_bytes":146,"direct_body_calls":204,"internal_direct_body_calls":2,"external_direct_body_calls":202,"direct_bl_entry_sites":3,"stored_entry_pointers":11,"stored_alternate_interior_entries":1,"indirect_body_calls":0}
  for key,value in expected.items():self.assertEqual(self.r["surface"][key],value,key)
 def test_providers(self):
  p=self.r["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["lvgl_calls"],p["cmsis_tick_calls"],p["iar_dlib_calls"],p["first_party_calls"]),(40,113,2,4,43));self.assertEqual(p["cmsis_freertos_commit"],"d213f261b5be6bb29a7cce8b84071706b72f4d53");self.assertFalse(p["new_version_discriminator"]);self.assertEqual(self.r["identity"]["embedded_third_party_definitions"],[])
 def test_not_routed(self):self.assertFalse(self.r["production"]["production_routed"])
if __name__=="__main__":unittest.main()
