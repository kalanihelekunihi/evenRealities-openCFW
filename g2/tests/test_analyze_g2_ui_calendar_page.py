import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'tools/analyze_g2_ui_calendar_page.py';S=importlib.util.spec_from_file_location('g2_ui_calendar_page_test',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class CalendarPageAuditTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):self.assertEqual((self.r['surface']['linked_functions'],self.r['surface']['body_bytes'],self.r['surface']['physical_bytes'],self.r['surface']['restored_functions']),(15,9690,10172,3));self.assertEqual(self.r['surface']['stored_function_pointers'],3);self.assertEqual(self.r['surface']['indirect_body_calls'],0)
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual((p['lvgl_calls'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['runtime_calls'],p['first_party_calls']),(533,85,34,12,58));self.assertIsNone(p['historical_calendar_page_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_ownership(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
