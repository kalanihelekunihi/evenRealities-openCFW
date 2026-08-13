import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_conversate_ui_main_page.py';S=importlib.util.spec_from_file_location('analyze_g2_conversate_ui_main_page',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class ConversateMainPageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(15,11,4132,4492));self.assertEqual((s['stored_function_entry_pointers'],s['indirect_body_calls'],s['strict_interior_ingress'],s['stored_strict_interior_entries']),(21,0,2,1))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','lvgl_calls','iar_dlib_calls','first_party_calls')),(130,98,2,53));self.assertIsNone(p['historical_main_page_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
