import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_terminal_ui.py';S=importlib.util.spec_from_file_location('analyze_g2_terminal_ui',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class TerminalUiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(99,76,13200,14040));self.assertEqual((s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['strict_interior_ingress']),(197,135,0));self.assertEqual((s['indirect_body_calls'],s['open_heap_dispatch_sites'],s['raw_unaligned_interior_bl_collisions']),(1,1,4))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','lvgl_calls','iar_dlib_calls','cmsis_freertos_calls','first_party_calls')),(275,142,9,3,216));self.assertEqual(p['cmsis_freertos_seams'],['osKernelGetTickCount']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
