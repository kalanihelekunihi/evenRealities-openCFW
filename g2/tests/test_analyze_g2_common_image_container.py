import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_common_image_container.py';S=importlib.util.spec_from_file_location('analyze_g2_common_image_container',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class CommonImageContainerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(3,1554,1834,280));self.assertEqual((s['indirect_body_calls'],s['stored_function_entry_pointers'],s['strict_interior_ingress']),(0,0,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','lvgl_calls','source_owned_heap_calls','source_owned_cache_calls','bounded_abs_calls','first_party_calls')),(70,3,3,1,1,2));self.assertIsNone(p['historical_container_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
