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
 def test_production_route(self):
  p=self.r["production"]
  self.assertTrue(p["production_routed"])
  self.assertFalse(p["software_functional_gap"])
  self.assertEqual(p["source_functions"],5)
  self.assertEqual(p["compiled_text_bytes"],{"apple-clang":1102,"linux-clang":1164})
  self.assertEqual(p["alignment_bytes"],{"apple-clang":6,"linux-clang":6})
  self.assertEqual(p["strict_relocations"],6)
  self.assertEqual(p["stock_body_bytes_displaced"],666)
  self.assertEqual(p["retained_diagnostic_pool_bytes"],58)
  self.assertEqual(p["profiles_verified"],["apple-clang","linux-clang"])
  self.assertEqual(p["hardware_validation"],"blocked by unavailable physical evidence")
  self.assertEqual(len(p["hardware_evidence_required"]),2)
  self.assertEqual(p["hardware_operations"],[])
if __name__=="__main__":unittest.main()
