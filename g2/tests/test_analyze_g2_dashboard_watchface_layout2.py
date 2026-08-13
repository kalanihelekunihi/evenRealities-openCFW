import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_dashboard_watchface_layout2.py';S=importlib.util.spec_from_file_location('analyze_g2_dashboard_watchface_layout2',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class Layout2Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(19,13,2844,3076));self.assertEqual((s['stored_function_entry_pointers'],s['indirect_body_calls'],s['strict_interior_ingress']),(18,0,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','lvgl_calls','iar_dlib_calls','mpaland_printf_calls','first_party_calls')),(20,104,9,5,43));self.assertIsNone(p['historical_layout2_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
