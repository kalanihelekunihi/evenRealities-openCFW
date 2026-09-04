import importlib.util,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class LegalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location("legal",R/"tools/analyze_g2_legal_regulatory.py");cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):self.assertEqual(self.r["surface"],{"linked_functions":1,"body_bytes":234,"physical_bytes":428,"outer_pool_bytes":194,"direct_body_calls":15,"stored_primary_entry_pointers":1,"shared_tail_direct_entries":1,"shared_tail_stored_entries":2,"indirect_body_calls":0})
 def test_providers(self):self.assertEqual((self.r["provider_boundary"]["easylogger_calls"],self.r["provider_boundary"]["lvgl_calls"],self.r["provider_boundary"]["iar_dlib_calls"],self.r["provider_boundary"]["first_party_calls"]),(10,1,2,2));self.assertFalse(self.r["provider_boundary"]["new_version_discriminator"])
 def test_production_route(self):
  p=self.r["production"];self.assertTrue(p["production_routed"]);self.assertFalse(p["software_functional_gap"]);self.assertEqual(p["profiles_verified"],["apple-clang","linux-clang"]);self.assertEqual(p["hardware_validation"],"blocked by unavailable physical evidence");self.assertEqual(p["hardware_operations"],[])
if __name__=="__main__":unittest.main()
