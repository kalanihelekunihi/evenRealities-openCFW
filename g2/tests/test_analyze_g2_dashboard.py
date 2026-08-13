import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_dashboard.py';S=importlib.util.spec_from_file_location('analyze_g2_dashboard',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class DashboardTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(24,21,10040,10856));self.assertEqual((s['direct_bl_entry_sites'],s['indirect_body_calls'],s['strict_interior_ingress']),(35,0,0));self.assertEqual((s['embedded_literal_pool_regions'],s['zero_ingress_recovered_functions'],s['unaligned_stored_interior_pseudo_pointers']),(2,1,6))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','lvgl_calls','iar_dlib_calls','cmsis_freertos_calls','nanopb_calls','first_party_calls')),(370,43,48,13,1,123));self.assertEqual(p['cmsis_freertos_seams'],['osMutexNew','osMutexAcquire','osMutexRelease']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
