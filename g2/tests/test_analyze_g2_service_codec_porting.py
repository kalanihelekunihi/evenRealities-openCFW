import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ServiceCodecPortingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("service_codec_porting",ROOT/"tools/analyze_g2_service_codec_porting.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":2,"ghidra_discovered_functions":2,"path_anchored_functions":2,"body_bytes":342,"physical_bytes":414,"outer_pool_bytes":72,"direct_body_calls":24,"internal_direct_body_calls":0,"external_direct_body_calls":24,"indirect_body_calls":0,"direct_bl_entry_sites":7,"stored_entry_pointers":0}
  for key,value in expected.items():self.assertEqual(self.r["surface"][key],value,key)
 def test_providers(self):
  p=self.r["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["ring_buffer_calls"],p["first_party_uart_calls"]),(20,1,3));self.assertEqual(p["ring_buffer_commit_interval"],["cda00e1efb815bad5100757f0d10d117f633ced6","190e30bebcec22d7311fd941179d70b4f439c441"]);self.assertFalse(p["new_version_discriminator"])
 def test_production_routing(self):
  p=self.r["production"];self.assertTrue(p["production_routed"]);self.assertEqual((p["compiled_text_bytes"],p["alignment_bytes"],p["strict_relocations"],p["replaced_stock_body_bytes"],p["retained_official_pool_bytes"]),(126,2,4,342,72));self.assertIn("blocked by unavailable physical evidence",p["hardware_validation"])
if __name__=="__main__":unittest.main()
