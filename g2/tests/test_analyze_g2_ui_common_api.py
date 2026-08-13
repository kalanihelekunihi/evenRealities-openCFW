import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_ui_common_api.py';S=importlib.util.spec_from_file_location('analyze_g2_ui_common_api',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class UiCommonApiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(9,0,892,960,68));self.assertEqual((s['direct_bl_entry_sites'],s['stored_aligned_function_entry_pointers'],s['strict_interior_ingress']),(182,0,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','closed_first_party_calls')),(35,2,4));self.assertEqual(p['cmsis_freertos_seams'],[]);self.assertEqual(p['freertos_kernel_seams'],[]);self.assertIsNone(p['historical_ui_common_api_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
