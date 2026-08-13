import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_dashboard_layout.py';S=importlib.util.spec_from_file_location('analyze_g2_dashboard_layout',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class DashboardLayoutTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(11,7,2162,2332));self.assertEqual((s['direct_bl_entry_sites'],s['indirect_body_calls'],s['strict_interior_ingress']),(32,0,0));self.assertEqual((s['stored_function_entry_pointers'],s['unaligned_stored_interior_pseudo_pointers'],s['raw_data_window_interior_bl_decodes']),(0,1,1))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','file_runtime_calls','cmsis_freertos_calls','freertos_kernel_calls')),(75,4,8,0,0));self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
