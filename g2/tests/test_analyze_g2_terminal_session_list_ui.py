import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_terminal_session_list_ui.py';S=importlib.util.spec_from_file_location('analyze_g2_terminal_session_list_ui',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class TerminalSessionListUiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(10,8,1966,2168));self.assertEqual((s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['indirect_body_calls'],s['strict_interior_ingress']),(3,25,0,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','lvgl_calls','first_party_calls','cmsis_freertos_calls','freertos_kernel_calls')),(70,5,56,0,0));self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
