import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_json_parser.py';S=importlib.util.spec_from_file_location('analyze_g2_json_parser',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class JsonParserTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(21,21,2572,2636,64));self.assertEqual((s['direct_bl_entry_sites'],s['external_direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['strict_interior_ingress'],s['b_w_entry_or_interior_targets']),(68,34,0,0,0));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls']),(47,34,13,6))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual((p['admitted_nanopb_shared_initializer_calls'],p['iar_dlib_calls'],p['unclosed_iar_runtime_calls'],p['hook_dispatch_sites']),(1,7,5,6));self.assertEqual(p['nanopb_commit'],'98bf4db69897b53434f3d0ba72e0a3ab1a902824');self.assertEqual((p['cmsis_freertos_calls'],p['freertos_kernel_calls']),(0,0));self.assertEqual(p['version_interval'],'cJSON v1.7.9 through v1.7.12')
 def test_claims(self):
  i=self.r['identity'];self.assertEqual(i['upstream_family'],'cJSON (DaveGamble/cJSON)');self.assertEqual(i['upstream_version_interval'],'v1.7.9 through v1.7.12');self.assertIsNone(i['retained_path']);self.assertEqual(len(i['embedded_third_party_definitions']),1);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
