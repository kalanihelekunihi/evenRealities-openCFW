import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_service_android_notify.py';S=importlib.util.spec_from_file_location('analyze_g2_service_android_notify',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class AndroidNotifyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(5,2,972,1104,132));self.assertEqual((s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['indirect_body_calls'],s['strict_interior_ingress']),(3,2,0,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','closed_ancc_service_calls','closed_ambiqsuite_ancc_profile_calls','closed_whitelist_service_calls','closed_sync_interface_calls','flagged_json_parser_calls')),(40,7,2,1,1,1,13));self.assertEqual((p['cmsis_freertos_calls'],p['freertos_kernel_calls']),(0,0));self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(len(self.r['identity']['embedded_third_party_definitions']),1);self.assertFalse(self.r['production']['production_routed'])
